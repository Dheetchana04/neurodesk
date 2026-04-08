"""
core/productivity_scorer.py - Daily Productivity Tracking & Scoring System
Tracks tasks completed, focus sessions, and gives a productivity score.
"""

import json
import os
from datetime import datetime, date
from typing import List, Dict

SCORES_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "productivity.json")

# Points awarded per action
POINTS = {
    "task_complete":    20,
    "focus_session":    30,
    "study_scheduled":  10,
    "reminder_set":      5,
    "note_saved":        5,
    "burnout_recovered": 15,  # bonus for continuing after burnout
}

# Score thresholds
SCORE_LABELS = [
    (90, "🔥 On Fire! Absolutely crushing it today!"),
    (75, "⚡ Highly Productive! Great momentum!"),
    (60, "✅ Solid Day! You got meaningful work done."),
    (40, "📈 Decent Progress. Every step counts!"),
    (20, "🌱 Getting Started. Tomorrow is a new chance!"),
    (0,  "😴 Rest Day. Recharge and come back stronger!"),
]

MAX_DAILY_POINTS = 200  # cap to normalize score to 0–100%


class ProductivityScorer:
    """Tracks and scores daily productivity."""

    def __init__(self):
        self._data: Dict = {}
        self._load()

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def record(self, action: str, note: str = "") -> int:
        """Record a productive action and return points awarded."""
        points = POINTS.get(action, 0)
        if points == 0:
            return 0

        today = str(date.today())
        if today not in self._data:
            self._data[today] = {"events": [], "total_points": 0}

        self._data[today]["events"].append({
            "time": datetime.now().strftime("%H:%M"),
            "action": action,
            "note": note,
            "points": points,
        })
        self._data[today]["total_points"] = min(
            self._data[today]["total_points"] + points,
            MAX_DAILY_POINTS
        )
        self._save()
        return points

    def get_score(self, for_date: str = None) -> dict:
        """Get productivity score for today (or a specific date)."""
        target = for_date or str(date.today())
        day_data = self._data.get(target, {"events": [], "total_points": 0})
        total_pts = day_data["total_points"]
        score_pct = min(int((total_pts / MAX_DAILY_POINTS) * 100), 100)

        label = SCORE_LABELS[-1][1]
        for threshold, lbl in SCORE_LABELS:
            if score_pct >= threshold:
                label = lbl
                break

        tasks_done = sum(1 for e in day_data["events"] if e["action"] == "task_complete")
        focus_sessions = sum(1 for e in day_data["events"] if e["action"] == "focus_session")

        return {
            "date": target,
            "score": score_pct,
            "total_points": total_pts,
            "label": label,
            "tasks_completed": tasks_done,
            "focus_sessions": focus_sessions,
            "events": day_data["events"],
        }

    def format_score(self, for_date: str = None) -> str:
        """Return a formatted productivity report string."""
        s = self.get_score(for_date)
        bar_filled = int(s["score"] / 5)
        bar = "█" * bar_filled + "░" * (20 - bar_filled)
        lines = [
            f"\n📊 PRODUCTIVITY REPORT — {s['date']}",
            f"   [{bar}] {s['score']}%",
            f"   {s['label']}",
            f"   Tasks completed : {s['tasks_completed']}",
            f"   Focus sessions  : {s['focus_sessions']}",
            f"   Total points    : {s['total_points']} / {MAX_DAILY_POINTS}",
        ]
        if s["events"]:
            lines.append("\n   Recent activity:")
            for e in s["events"][-5:]:
                lines.append(f"   {e['time']} +{e['points']}pts — {e['action'].replace('_',' ')}"
                             + (f" ({e['note']})" if e["note"] else ""))
        return "\n".join(lines)

    def get_weekly_summary(self) -> str:
        """Return a 7-day summary string."""
        from datetime import timedelta
        lines = ["\n📅 WEEKLY PRODUCTIVITY SUMMARY"]
        today = date.today()
        for i in range(6, -1, -1):
            d = str(today - timedelta(days=i))
            s = self.get_score(d)
            bar = "█" * int(s["score"] / 10) + "░" * (10 - int(s["score"] / 10))
            label = "Today" if i == 0 else f"{i}d ago"
            lines.append(f"   {d} [{bar}] {s['score']:3d}%  ({label})")
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    #  Persistence                                                         #
    # ------------------------------------------------------------------ #

    def _load(self):
        os.makedirs(os.path.dirname(SCORES_FILE), exist_ok=True)
        if os.path.exists(SCORES_FILE):
            try:
                with open(SCORES_FILE, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}

    def _save(self):
        try:
            with open(SCORES_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except IOError:
            pass
