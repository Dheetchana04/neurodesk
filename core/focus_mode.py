"""
core/focus_mode.py - Focus Session Timer & Distraction Blocker Simulator
"""

import json
import os
import re
import random
import threading
import time
from datetime import datetime, date
from typing import Optional

FOCUS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "focus_sessions.json")

MOTIVATIONAL_NUDGES = [
    "💪 Stay locked in — you're building something great right now.",
    "🔥 Every minute of focus now = results you'll see later.",
    "🎯 Distractions are temporary. Your goals are permanent. Stay focused.",
    "⚡ You chose this session. Honor that choice. Keep going.",
    "🧠 Your brain is in deep work mode. Don't break the flow!",
    "📈 Progress, not perfection. Every focused minute counts.",
    "🏆 Champions are made in moments like this — stay with it.",
    "🌊 Stay in the flow. You're doing better than you think.",
]

BLOCKED_SITES = [
    "instagram.com", "twitter.com", "x.com", "facebook.com",
    "youtube.com", "tiktok.com", "reddit.com", "snapchat.com",
    "netflix.com", "twitch.tv",
]

COMPLETED_MESSAGES = [
    "🎉 Focus session complete! You just built real momentum.",
    "✅ Session done! You should be proud — that was serious work.",
    "🏆 Nailed it! Another focus session in the books.",
    "⚡ DONE! That's the kind of effort that compounds over time.",
]


class FocusMode:
    """Manages focus sessions with timers and motivational nudges."""

    def __init__(self, productivity_scorer=None, speak_fn=None):
        self._scorer = productivity_scorer
        self._speak = speak_fn  # optional TTS callback
        self._active_session: Optional[dict] = None
        self._timer_thread: Optional[threading.Thread] = None
        self._sessions: list = []
        self._load()

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def parse_duration(self, text: str) -> int:
        """Extract duration in minutes from text like 'focus for 30 mins'."""
        patterns = [
            (r"(\d+)\s*hour",   lambda m: int(m.group(1)) * 60),
            (r"(\d+)\s*hr",     lambda m: int(m.group(1)) * 60),
            (r"(\d+)\s*min",    lambda m: int(m.group(1))),
            (r"for\s+(\d+)",    lambda m: int(m.group(1))),
            (r"(\d+)\s*m\b",    lambda m: int(m.group(1))),
        ]
        for pattern, extractor in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                return max(1, min(extractor(m), 180))  # clamp 1–180 min
        return 25  # default Pomodoro

    def start(self, duration_minutes: int, subject: str = "") -> str:
        """Start a focus session."""
        if self._active_session:
            remaining = self._active_session.get("remaining_seconds", 0)
            mins = remaining // 60
            secs = remaining % 60
            return f"⏱ Focus session already running! {mins}m {secs}s remaining. Type 'stop focus' to end it."

        self._active_session = {
            "start_time": datetime.now().isoformat(),
            "duration_minutes": duration_minutes,
            "subject": subject,
            "remaining_seconds": duration_minutes * 60,
            "nudges_sent": 0,
        }

        self._timer_thread = threading.Thread(
            target=self._run_timer, daemon=True
        )
        self._timer_thread.start()

        blocked = ", ".join(BLOCKED_SITES[:5]) + "…"
        subject_line = f" on {subject}" if subject else ""
        return (
            f"🎯 FOCUS MODE ON — {duration_minutes} minute session{subject_line} started!\n"
            f"🚫 Simulating blocks on: {blocked}\n"
            f"💡 Type 'status' to check remaining time, 'stop focus' to end early."
        )

    def stop(self) -> str:
        """Stop the current focus session early."""
        if not self._active_session:
            return "No active focus session right now. Start one with 'start focus session 25 min'."
        elapsed = self._active_session["duration_minutes"] * 60 - self._active_session.get("remaining_seconds", 0)
        self._end_session(completed=False, elapsed_seconds=elapsed)
        return f"⏹ Focus session ended early after {elapsed // 60}m {elapsed % 60}s. Progress still counts!"

    def status(self) -> str:
        """Get current focus session status."""
        if not self._active_session:
            return "No active focus session. Start one with 'start focus session 25 min'."
        rem = self._active_session.get("remaining_seconds", 0)
        mins, secs = rem // 60, rem % 60
        elapsed_secs = self._active_session["duration_minutes"] * 60 - rem
        elapsed_mins = elapsed_secs // 60
        subject = self._active_session.get("subject", "")
        subj_line = f" — studying {subject}" if subject else ""
        return (
            f"⏱ FOCUS SESSION ACTIVE{subj_line}\n"
            f"   Elapsed  : {elapsed_mins}m {elapsed_secs % 60}s\n"
            f"   Remaining: {mins}m {secs}s\n"
            f"   {random.choice(MOTIVATIONAL_NUDGES)}"
        )

    def get_today_summary(self) -> str:
        """Return a summary of today's focus sessions."""
        today = str(date.today())
        today_sessions = [s for s in self._sessions if s.get("date") == today]
        if not today_sessions:
            return "No focus sessions today. Start one with 'start focus session 25 min'!"
        total_mins = sum(s.get("duration_minutes", 0) for s in today_sessions if s.get("completed"))
        completed = sum(1 for s in today_sessions if s.get("completed"))
        lines = [
            f"\n🎯 TODAY'S FOCUS SESSIONS",
            f"   Completed sessions : {completed}",
            f"   Total focused time : {total_mins} minutes",
        ]
        for s in today_sessions[-3:]:
            status = "✅" if s.get("completed") else "⏹"
            subj = f" — {s['subject']}" if s.get("subject") else ""
            lines.append(f"   {status} {s.get('start_time','')[:5]} | {s.get('duration_minutes',0)}min{subj}")
        return "\n".join(lines)

    def is_active(self) -> bool:
        return self._active_session is not None

    # ------------------------------------------------------------------ #
    #  Timer Thread                                                        #
    # ------------------------------------------------------------------ #

    def _run_timer(self):
        """Background timer that counts down and fires nudges."""
        session = self._active_session
        total_secs = session["duration_minutes"] * 60
        nudge_interval = max(300, total_secs // 4)  # nudge every ~25% of session

        for remaining in range(total_secs, 0, -1):
            if self._active_session is None:
                return
            self._active_session["remaining_seconds"] = remaining

            # Send motivational nudge
            elapsed = total_secs - remaining
            if elapsed > 0 and elapsed % nudge_interval == 0:
                nudge = random.choice(MOTIVATIONAL_NUDGES)
                print(f"\n\n  {nudge}\n")
                if self._speak:
                    self._speak(nudge)
                self._active_session["nudges_sent"] = self._active_session.get("nudges_sent", 0) + 1

            time.sleep(1)

        # Session completed naturally
        if self._active_session:
            self._end_session(completed=True, elapsed_seconds=total_secs)
            msg = random.choice(COMPLETED_MESSAGES)
            print(f"\n\n  {msg}\n")
            if self._speak:
                self._speak(msg)

    def _end_session(self, completed: bool, elapsed_seconds: int):
        """Finalize and save the session."""
        if not self._active_session:
            return
        session_record = {
            **self._active_session,
            "date": str(date.today()),
            "completed": completed,
            "actual_duration_minutes": elapsed_seconds // 60,
            "start_time": self._active_session.get("start_time", "")[:16].replace("T", " "),
        }
        self._sessions.append(session_record)
        self._save()

        if self._scorer and completed:
            self._scorer.record("focus_session",
                                f"{session_record['actual_duration_minutes']}min"
                                + (f" on {session_record['subject']}" if session_record.get("subject") else ""))
        self._active_session = None

    # ------------------------------------------------------------------ #
    #  Persistence                                                         #
    # ------------------------------------------------------------------ #

    def _load(self):
        os.makedirs(os.path.dirname(FOCUS_FILE), exist_ok=True)
        if os.path.exists(FOCUS_FILE):
            try:
                with open(FOCUS_FILE, "r", encoding="utf-8") as f:
                    self._sessions = json.load(f)
            except Exception:
                self._sessions = []

    def _save(self):
        try:
            with open(FOCUS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._sessions[-100:], f, indent=2)
        except IOError:
            pass
