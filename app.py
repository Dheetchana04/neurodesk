"""
app.py - NeuroDesk Flask Application
All endpoints: chat, tasks, schedule, score, focus, memory, history, burnout
"""

from flask import Flask, render_template, request, jsonify
import json, os
from datetime import datetime

from core.memory import MemorySystem
from core.task_manager import TaskManager
from core.chat_history import ChatHistory
from core.nlp_engine import NLPEngine
from core.command_handler import CommandHandler
from core.study_scheduler import StudyScheduler
from core.mood_detector import MoodDetector
from core.burnout_detector import BurnoutDetector
from core.productivity_scorer import ProductivityScorer
from core.focus_mode import FocusMode
from core.academic_assistant import AcademicAssistant


def create_app():
    app = Flask(__name__)

    memory   = MemorySystem()
    tasks    = TaskManager()
    history  = ChatHistory()
    nlp      = NLPEngine()
    mood_det = MoodDetector()
    burnout  = BurnoutDetector()
    scorer   = ProductivityScorer()
    focus    = FocusMode(productivity_scorer=scorer)
    academic = AcademicAssistant()
    scheduler= StudyScheduler()

    class _Shim:
        running = True

    commands = CommandHandler(
        assistant=_Shim(), tasks=tasks, scheduler=scheduler, memory=memory,
        focus_mode=focus, scorer=scorer, academic=academic, burnout=burnout,
    )

    # ── Routes ────────────────────────────────────────────────────────

    @app.route("/")
    def index():
        return render_template("dashboard.html")

    # ── Chat ──────────────────────────────────────────────────────────
    @app.route("/api/chat", methods=["POST"])
    def chat():
        data = request.get_json() or {}
        msg = data.get("message", "").strip()
        if not msg:
            return jsonify({"error": "Empty message"}), 400

        history.log("user", msg)

        # 1. Burnout — highest priority
        burnout_level = burnout.detect_level(msg)
        if burnout_level != "none":
            response = burnout.format_response(burnout_level)
            scorer.record("burnout_recovered")
            history.log("assistant", response)
            return jsonify({
                "response": response,
                "intent": "burnout_detected",
                "mood": "stressed",
                "burnout_level": burnout_level,
            })

        # 2. Normal pipeline
        detected_mood = mood_det.detect(msg)
        intent = nlp.classify_intent(msg)

        # Study schedule opens modal in web UI
        if intent == "study_schedule":
            response = "📚 Opening the Study Schedule builder!"
            history.log("assistant", response)
            return jsonify({
                "response": response, "intent": intent,
                "mood": detected_mood, "action": "open_study_modal",
            })

        response = commands.handle(intent, msg, mood=detected_mood)
        if not response:
            if academic.is_academic_query(msg):
                response = academic.explain(msg) or nlp.generate_response(msg, memory)
            else:
                response = nlp.generate_response(msg, memory)

        if detected_mood and detected_mood != "neutral":
            preamble = mood_det.get_response(detected_mood)
            if preamble:
                response = f"{preamble}\n\n{response}"

        history.log("assistant", response)
        return jsonify({"response": response, "intent": intent, "mood": detected_mood})

    # ── Tasks ─────────────────────────────────────────────────────────
    @app.route("/api/tasks")
    def get_tasks():
        return jsonify(tasks.get_all_tasks())

    @app.route("/api/tasks/<int:tid>/complete", methods=["POST"])
    def complete_task(tid):
        ok = tasks.complete_task(tid)
        if ok:
            scorer.record("task_complete", f"task #{tid}")
        return jsonify({"success": ok})

    @app.route("/api/tasks/<int:tid>", methods=["DELETE"])
    def delete_task(tid):
        return jsonify({"success": tasks.delete_task(tid)})

    # ── Study Schedule ────────────────────────────────────────────────
    @app.route("/api/schedule", methods=["POST"])
    def generate_schedule():
        data = request.get_json() or {}
        subjects   = data.get("subjects", [])
        total_hours= float(data.get("hours", 2))
        start_str  = data.get("start_time", "09:00")
        mood_hint  = data.get("mood", "neutral")

        if not subjects:
            return jsonify({"error": "No subjects provided"}), 400

        try:
            parsed = datetime.strptime(start_str, "%H:%M")
            start  = datetime.now().replace(hour=parsed.hour, minute=parsed.minute, second=0, microsecond=0)
        except ValueError:
            return jsonify({"error": "Invalid start time. Use HH:MM"}), 400

        # Mood-aware adjustment: reduce hard blocks if stressed/tired
        adjusted = []
        for s in subjects:
            diff = s.get("difficulty", "medium")
            if mood_hint in ("stressed", "tired") and diff == "hard":
                diff = "medium"
            adjusted.append({**s, "difficulty": diff})

        blocks = scheduler._generate(adjusted, int(total_hours * 60), start)
        scheduler._save_schedule(blocks, adjusted, total_hours)
        scorer.record("study_scheduled")

        return jsonify({
            "blocks": blocks, "subjects": adjusted,
            "total_hours": total_hours,
            "date": datetime.now().strftime("%A, %B %d, %Y"),
            "mood_adjusted": mood_hint in ("stressed", "tired"),
        })

    # ── Productivity Score ────────────────────────────────────────────
    @app.route("/api/score")
    def get_score():
        return jsonify(scorer.get_score())

    @app.route("/api/score/weekly")
    def get_weekly():
        from datetime import date, timedelta
        result = []
        today = date.today()
        for i in range(6, -1, -1):
            d = str(today - timedelta(days=i))
            result.append(scorer.get_score(d))
        return jsonify(result)

    # ── Focus Mode ────────────────────────────────────────────────────
    @app.route("/api/focus")
    def get_focus():
        active = focus.is_active()
        data = {"is_active": active}
        if active and focus._active_session:
            rem = focus._active_session.get("remaining_seconds", 0)
            data.update({
                "remaining_seconds": rem,
                "remaining_display": f"{rem // 60}m {rem % 60}s",
                "subject": focus._active_session.get("subject", ""),
                "duration_minutes": focus._active_session.get("duration_minutes", 0),
            })
        return jsonify(data)

    @app.route("/api/focus/start", methods=["POST"])
    def start_focus():
        data = request.get_json() or {}
        duration = int(data.get("duration", 25))
        subject  = data.get("subject", "")
        result   = focus.start(duration, subject)
        return jsonify({"message": result, "is_active": focus.is_active()})

    @app.route("/api/focus/stop", methods=["POST"])
    def stop_focus():
        result = focus.stop()
        return jsonify({"message": result, "is_active": focus.is_active()})

    # ── Memory / History ──────────────────────────────────────────────
    @app.route("/api/memory")
    def get_memory():
        return jsonify(memory.all())

    @app.route("/api/history")
    def get_history():
        n = request.args.get("n", 50, type=int)
        return jsonify(history.get_recent(n))

    # ── Burnout History ───────────────────────────────────────────────
    @app.route("/api/burnout")
    def get_burnout():
        counts = burnout.session_burnout_count()
        return jsonify({
            "session_counts": counts,
            "total": sum(counts.values()),
            "risk_level": (
                "high"   if counts["high"] >= 2 else
                "medium" if counts["medium"] >= 3 or counts["high"] >= 1 else
                "low"    if counts["low"] >= 2 else
                "none"
            ),
        })

    return app
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)