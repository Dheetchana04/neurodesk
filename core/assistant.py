"""
core/assistant.py - NeuroDesk AI Student Cognitive Assistant Orchestrator
"""

import time
import threading
from datetime import datetime

from core.voice import VoiceEngine
from core.nlp_engine import NLPEngine
from core.command_handler import CommandHandler
from core.memory import MemorySystem
from core.task_manager import TaskManager
from core.study_scheduler import StudyScheduler
from core.mood_detector import MoodDetector
from core.burnout_detector import BurnoutDetector
from core.productivity_scorer import ProductivityScorer
from core.focus_mode import FocusMode
from core.academic_assistant import AcademicAssistant
from core.chat_history import ChatHistory
from core.utils import typing_print, COLORS


class Assistant:
    NAME = "NeuroDesk"

    def __init__(self, voice_enabled=True, voice_input=True):
        print(f"\n{COLORS['cyan']}Initializing {self.NAME}...{COLORS['reset']}")

        self.voice    = VoiceEngine(enabled=voice_enabled)
        self.nlp      = NLPEngine()
        self.memory   = MemorySystem()
        self.tasks    = TaskManager()
        self.scheduler= StudyScheduler()
        self.mood     = MoodDetector()
        self.burnout  = BurnoutDetector()
        self.scorer   = ProductivityScorer()
        self.academic = AcademicAssistant()
        self.history  = ChatHistory()
        self.focus    = FocusMode(productivity_scorer=self.scorer,
                                  speak_fn=self.voice.speak if voice_enabled else None)

        self.commands = CommandHandler(
            assistant=self,
            tasks=self.tasks,
            scheduler=self.scheduler,
            memory=self.memory,
            focus_mode=self.focus,
            scorer=self.scorer,
            academic=self.academic,
            burnout=self.burnout,
        )

        self.voice_input_enabled = voice_input
        self.running = False
        self._reminder_thread = threading.Thread(target=self._reminder_loop, daemon=True)

        print(f"{COLORS['green']}✓ {self.NAME} ready!{COLORS['reset']}\n")

    # ── Main Loop ───────────────────────────────────────────────────────
    def run(self):
        self.running = True
        self._reminder_thread.start()
        self._respond(self._build_greeting())

        while self.running:
            try:
                user_input = self._get_input()
                if not user_input:
                    continue
                self._process(user_input)
            except KeyboardInterrupt:
                self._respond("Goodbye! Keep growing! 👋")
                self.running = False
            except Exception as e:
                self._respond(f"Something went wrong: {e}. Let's continue!")

    # ── I/O ─────────────────────────────────────────────────────────────
    def _get_input(self) -> str:
        print(f"\n{COLORS['yellow']}[You]{COLORS['reset']} ", end="", flush=True)
        if self.voice_input_enabled:
            text = self.voice.listen()
            if text:
                print(text)
                return text
            print(f"{COLORS['dim']}(type your message){COLORS['reset']}")
        return input().strip()

    def _respond(self, text: str):
        print(f"\n{COLORS['cyan']}[{self.NAME}]{COLORS['reset']} ", end="")
        typing_print(text)
        self.voice.speak(text)
        self.history.log("assistant", text)

    # ── Pipeline ────────────────────────────────────────────────────────
    def _process(self, user_input: str):
        self.history.log("user", user_input)

        # 1. Burnout check — highest priority
        burnout_level = self.burnout.detect_level(user_input)
        if burnout_level != "none":
            response = self.burnout.format_response(burnout_level)
            if self.scorer:
                self.scorer.record("burnout_recovered")
            self._respond(response)
            return

        # 2. Mood detection
        detected_mood = self.mood.detect(user_input)

        # 3. Intent classification
        intent = self.nlp.classify_intent(user_input)

        # 4. Command execution
        response = self.commands.handle(intent, user_input, mood=detected_mood)

        # 5. Fallback to NLP
        if not response:
            # Try academic assistant as secondary fallback
            if self.academic.is_academic_query(user_input):
                result = self.academic.explain(user_input)
                if result:
                    response = result
            if not response:
                response = self.nlp.generate_response(user_input, self.memory)

        # 6. Mood preamble
        if detected_mood and detected_mood != "neutral":
            preamble = self.mood.get_response(detected_mood)
            if preamble:
                response = f"{preamble}\n\n{response}"

        self._respond(response)

    # ── Reminder Thread ─────────────────────────────────────────────────
    def _reminder_loop(self):
        while self.running:
            for reminder in self.tasks.get_due_reminders():
                msg = f"⏰ REMINDER: {reminder['text']}"
                print(f"\n\n{COLORS['red']}{msg}{COLORS['reset']}\n")
                self.voice.speak(msg)
                self.tasks.mark_reminder_fired(reminder["id"])
            time.sleep(30)

    # ── Greeting ────────────────────────────────────────────────────────
    def _build_greeting(self) -> str:
        hour = datetime.now().hour
        period = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
        name = self.memory.get("user_name", "there")
        visits = self.memory.get("visit_count", 0) + 1
        self.memory.set("visit_count", visits)
        score = self.scorer.get_score()

        if visits == 1:
            return (
                f"{period}! I'm {self.NAME}, your AI Student Cognitive Assistant. "
                "I help with studying, focus, burnout detection, and academic questions. "
                "What's your name?"
            )
        score_line = f" You're at {score['score']}% productivity today." if score["score"] > 0 else ""
        return (
            f"{period}, {name}! Welcome back — visit #{visits}.{score_line} "
            "Type 'help' for all commands."
        )
