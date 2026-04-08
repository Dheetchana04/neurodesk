"""
core/burnout_detector.py - Burnout & Cognitive Fatigue Detection System
Detects burnout signals from text and recommends recovery actions.
"""

import re
import random
from datetime import datetime, date

BURNOUT_SIGNALS = {
    "high": [
        "i give up", "i quit", "i cant do this", "i can't do this",
        "i'm done", "im done", "forget it", "this is impossible",
        "i hate studying", "i hate this", "i want to cry",
        "i'm going to fail", "im going to fail", "i'm hopeless",
        "everything is pointless", "i can't anymore", "i cant anymore",
        "i'm so burnt out", "im burnt out", "so burnt out", "burnout", "burn out",
    ],
    "medium": [
        "i can't focus", "i cant focus", "cant focus", "cannot focus",
        "i can't concentrate",
        "my brain is fried", "i'm so tired of this", "im tired of this",
        "i've been studying for hours", "been studying for hours",
        "nothing is going in", "not retaining", "keep forgetting",
        "so overwhelmed", "too much to study", "can't keep up",
        "mind is blank", "brain is dead", "mentally drained",
        "i'm exhausted from studying", "study fatigue",
    ],
    "low": [
        "feeling a bit tired", "little tired", "slightly unfocused",
        "losing motivation", "not feeling it today", "distracted",
        "hard to start", "procrastinating", "low energy",
        "not in the mood", "struggling a bit",
    ],
}

BREAK_SUGGESTIONS = {
    "high": [
        "🛑 You need a proper break — at least 30 minutes. Step away from your desk completely.",
        "🌿 Close everything and rest. Your brain literally cannot absorb more right now.",
        "🎵 Put on music, lie down for 20 mins. Studying now would be counterproductive.",
        "🚶 Go for a short walk outside. Fresh air resets your cognitive state better than pushing through.",
    ],
    "medium": [
        "☕ Take a 10-15 minute break. Make tea/coffee, stretch, then come back.",
        "🎮 5-10 mins of something fun — a game, a meme scroll. Then back to it.",
        "💧 Drink water, do 10 jumping jacks. Physical movement boosts focus chemicals.",
        "😮‍💨 Try the 4-7-8 breath: inhale 4s, hold 7s, exhale 8s. Do it 3 times.",
    ],
    "low": [
        "🎯 Switch subjects — try something easier for 20 mins, then return.",
        "📝 Change your method — try writing notes instead of reading.",
        "⏱ Set a 25-minute Pomodoro timer. Short sprints beat marathon sessions.",
        "🎧 Put on lo-fi music and give it 10 more minutes — motivation often returns.",
    ],
}

LIGHT_TASK_SUGGESTIONS = [
    "Review your notes from last week instead of learning new material",
    "Watch a short YouTube explanation (5-10 min) on the topic",
    "Make flashcards — low effort but high retention value",
    "Organize your study folder / notes structure",
    "Do practice MCQs on topics you already know",
    "Read a summary or mind-map instead of a full textbook chapter",
    "Listen to a podcast on the subject while lying down",
]

RECOVERY_MESSAGES = {
    "high": [
        "Hey, burnout is real and it's okay. Even top students hit this wall. Rest IS productive.",
        "Your brain needs rest to consolidate what you've learned. Taking a break is the smart move.",
        "Pushing through burnout leads to zero retention. Rest now, study better later.",
    ],
    "medium": [
        "You've been working hard. A short break will actually make the next session more effective.",
        "Cognitive fatigue is normal. A brief reset will help you absorb more in less time.",
        "Your focus will return after a short break. Don't force it — it backfires.",
    ],
    "low": [
        "Small motivation dips are normal. Try a different approach for 15 minutes.",
        "Sometimes switching subjects or methods is all you need to get back in flow.",
        "You're still in the game! A tiny adjustment can flip the momentum.",
    ],
}


class BurnoutDetector:
    """Detects burnout level from text and suggests recovery strategies."""

    def __init__(self):
        self._session_signals = []  # track signals within a session

    def detect_level(self, text: str) -> str:
        """Returns 'high', 'medium', 'low', or 'none'."""
        text_lower = text.lower()
        # Check from most severe to least
        for level in ("high", "medium", "low"):
            for signal in BURNOUT_SIGNALS[level]:
                if signal in text_lower:
                    self._session_signals.append((datetime.now(), level))
                    return level
        return "none"

    def get_response(self, level: str) -> dict:
        """Returns a full burnout response dict with message, break suggestion, light task."""
        if level == "none":
            return {}
        return {
            "level": level,
            "recovery_message": random.choice(RECOVERY_MESSAGES[level]),
            "break_suggestion": random.choice(BREAK_SUGGESTIONS[level]),
            "light_task": random.choice(LIGHT_TASK_SUGGESTIONS),
            "emoji": {"high": "🔴", "medium": "🟡", "low": "🟢"}[level],
        }

    def format_response(self, level: str) -> str:
        """Returns a formatted string response for CLI/chat output."""
        r = self.get_response(level)
        if not r:
            return ""
        lines = [
            f"{r['emoji']} Burnout level: {level.upper()} detected.",
            f"\n{r['recovery_message']}",
            f"\n{r['break_suggestion']}",
            f"\n💡 Light alternative: {r['light_task']}",
        ]
        return "\n".join(lines)

    def session_burnout_count(self) -> dict:
        """Returns count of burnout signals detected this session."""
        counts = {"high": 0, "medium": 0, "low": 0}
        for _, level in self._session_signals:
            counts[level] += 1
        return counts
