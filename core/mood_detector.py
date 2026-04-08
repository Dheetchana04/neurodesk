"""
core/mood_detector.py - NeuroDesk Enhanced Mood & Emotion Detector
"""
import re
import random

MOOD_SIGNALS = {
    "stressed": [
        "stressed", "stress", "overwhelmed", "too much", "can't cope",
        "anxious", "anxiety", "panic", "deadline", "pressure", "burning out",
        "so much to do", "running out of time", "behind on",
    ],
    "tired": [
        "tired", "exhausted", "sleepy", "fatigue", "worn out", "drained",
        "no energy", "can't focus", "brain fog", "drowsy", "yawning",
        "haven't slept", "up all night", "pulling an all nighter",
    ],
    "sad": [
        "sad", "depressed", "unhappy", "feeling down", "not okay",
        "hopeless", "lonely", "crying", "upset", "miserable", "heartbroken",
        "i give up", "i quit", "what's the point", "nothing matters",
        "i'm hopeless", "im hopeless", "i'll never", "i will never",
        "i'm a failure", "im a failure", "i failed",
    ],
    "angry": [
        "angry", "angryyy", "frustrated", "annoyed", "furious", "mad at",
        "hate this", "so dumb", "ridiculous", "useless", "making me angry",
        "makes me angry", "pissed", "irritated", "rage", "im angry",
        "this is stupid", "i hate",
    ],
    "happy": [
        "happy", "great", "amazing", "awesome", "excited", "fantastic",
        "wonderful", "love this", "so good", "brilliant", "crushing it",
        "nailed it", "feel good", "on fire", "confident",
    ],
    "bored": [
        "bored", "boring", "nothing to do", "not interesting", "dull",
        "tedious", "monotonous", "same thing", "not motivated",
    ],
}

MOOD_RESPONSES = {
    "stressed": [
        "Take a deep breath. 🌬️ You've got this — one step at a time.",
        "Stress is temporary, but your strength is permanent. Let's tackle this together.",
        "Break it into tiny steps. What's the ONE thing you can do right now?",
    ],
    "tired": [
        "Rest is productive too! 😴 Consider a short break — even 10 minutes helps.",
        "You've been working hard. A quick nap or walk can recharge your brain!",
        "Fatigue is your body asking for rest. Be kind to yourself. 🌙",
    ],
    "sad": [
        "I'm sorry you're feeling this way. 💙 It's okay to have tough days.",
        "You're not alone. Even the best students have moments like this.",
        "One bad moment doesn't define your journey. You're still here and that matters. 🤗",
    ],
    "angry": [
        "I hear you — that sounds really frustrating. 😤 Let's work through it.",
        "It's okay to feel angry. Take a moment, then we'll solve it together.",
        "Frustration means you care. Channel that energy into progress! 🔥",
    ],
    "happy": [
        "Love the energy! 🎉 Let's keep that momentum going!",
        "That's the spirit! 🚀 Happy minds are productive minds!",
        "Awesome! Let's make the most of this energy!",
    ],
    "bored": [
        "Boredom is just creativity waiting to happen! 💡 Try something new.",
        "Let's switch it up! Want me to generate a study challenge?",
        "Perfect time to start that task you've been putting off! 😄",
    ],
}


class MoodDetector:
    def detect(self, text: str) -> str:
        text_lower = text.lower()
        scores = {mood: 0 for mood in MOOD_SIGNALS}
        for mood, signals in MOOD_SIGNALS.items():
            for signal in signals:
                if signal in text_lower:
                    scores[mood] += 1
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "neutral"

    def get_response(self, mood: str) -> str:
        if mood == "neutral" or mood not in MOOD_RESPONSES:
            return ""
        return random.choice(MOOD_RESPONSES[mood])
