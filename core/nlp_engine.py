"""
core/nlp_engine.py - NeuroDesk NLP Intent Classification Engine
"""

import re
import random
from core.utils import COLORS

INTENT_PATTERNS = [
    ("greet",               [r"\b(hi|hello|hey|howdy|sup|good\s+(morning|evening|afternoon))\b"]),
    ("thanks",              [r"\b(thanks|thank\s+you|thx|ty)\b"]),
    ("help",                [r"\bhelp\b", r"what\s+can\s+you\s+do", r"commands?\b"]),
    ("time",                [r"\bwhat\s+time\b", r"\bcurrent\s+time\b"]),
    ("date",                [r"\bwhat\s+(is\s+)?(today|the\s+date|day)\b"]),
    ("open_youtube",        [r"\b(open|launch|play)\s+youtube\b"]),
    ("open_google",         [r"\b(open|launch|go\s+to)\s+google\b"]),
    ("web_search",          [r"\b(search\s+for|look\s+up|google|find)\b"]),
    ("note",                [r"\b(remember\s+that|note\s+that|don.t\s+forget)\b"]),
    ("add_task",            [r"\b(add|create|new)\s+task\b", r"\bremind\s+me\b", r"\bset\s+(a\s+)?reminder\b"]),
    ("view_tasks",          [r"\b(show|list|view|display)\s+(my\s+)?(tasks?|reminders?|todos?)\b"]),
    ("complete_task",       [r"\b(done|complete|finish|mark)\s+(task|todo|item)\b"]),
    ("study_schedule",      [r"\bstudy\s+schedule\b", r"\btimetable\b", r"\bgenerate\s+schedule\b", r"\bplan\s+my\s+stud"]),
    ("set_name",            [r"\bmy\s+name\s+is\b", r"\bcall\s+me\b"]),
    ("recall_memory",       [r"\bwhat\s+do\s+you\s+remember\b", r"\brecall\b"]),
    ("view_history",        [r"\b(history|chat\s+log|past\s+conversations?)\b"]),
    # Focus — must come BEFORE open_app and goodbye
    ("focus_stop",          [r"\bstop\s+focus\b", r"\bend\s+focus\b", r"\bcancel\s+focus\b",
                              r"\bend\s+(the\s+)?focus\s+session\b"]),
    ("focus_status",        [r"\bfocus\s+status\b", r"\b(time\s+)?(left|remaining)\s*(in\s+focus)?\b",
                              r"\bhow\s+long\s+(left|remaining)\b"]),
    ("focus_summary",       [r"\bfocus\s+summary\b", r"\btoday.s\s+sessions?\b"]),
    ("focus_start",         [r"\bstart\s+focus\b", r"\bfocus\s+(session|mode|for|timer)\b",
                              r"\bpomodoro\b", r"\bstart\s+studying\s+for\b"]),
    ("productivity_score",  [r"\b(my\s+)?(productivity|score|how\s+(productive|did\s+i\s+do))\b",
                              r"\bproductivity\s+report\b"]),
    ("weekly_summary",      [r"\bweekly\s+(summary|report|score)\b", r"\bthis\s+week\b"]),
    # Academic — must come BEFORE open_app
    ("interview_prep",      [r"\binterview\s+(question|prep|practice)\b",
                              r"\bgive\s+me\s+(some\s+)?(interview\s+)?questions?\b",
                              r"\bpractice\s+questions?\b",
                              r"\b(python|dsa|os|general)\s+interview\b"]),
    ("study_tip",           [r"\bstudy\s+tip\b", r"\bhow\s+to\s+study\b", r"\bbetter\s+at\s+studying\b"]),
    ("explain_concept",     [r"\bexplain\s+\w+", r"\bwhat\s+is\s+(a\s+)?\w+",
                              r"\bdifference\s+between\b", r"\bhow\s+does\s+\w+\s+work\b"]),
    # open_app last (broad catch-all)
    ("open_app",            [r"\b(open|launch|start)\s+\w+"]),
    ("mood_check",          [r"\bhow\s+are\s+you\b", r"\bwhat.s\s+up\b"]),
    ("motivate",            [r"\bmotivat", r"\binspir", r"\bencourag", r"\bquote\b"]),
    ("joke",                [r"\b(joke|funny|make\s+me\s+laugh)\b"]),
    ("math",                [r"\b(calculate|compute|math|what\s+is\s+\d)"]),
    ("goodbye",             [r"\b(bye|goodbye|exit|quit|see\s+you|later)\b"]),
]

FALLBACK_RESPONSES = [
    "Interesting! Tell me more — I'm always learning.",
    "Hmm, could you rephrase that?",
    "That's a bit beyond me. Try 'help' to see what I can do!",
    "I didn't quite catch that. Ask me something else?",
]

JOKES = [
    "Why don't scientists trust atoms? Because they make up everything! 😄",
    "Why did the computer go to the doctor? It had a virus! 💻",
    "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
    "What do you call 8 hobbits? A hobbyte! 🧙",
    "Why was the math book sad? It had too many problems! 📚",
]

MOTIVATIONAL_QUOTES = [
    "The secret of getting ahead is getting started. — Mark Twain",
    "It always seems impossible until it's done. — Nelson Mandela",
    "Don't watch the clock; do what it does. Keep going. — Sam Levenson",
    "Success is the sum of small efforts, repeated day in and day out. — Robert Collier",
    "You don't have to be great to start, but you have to start to be great. — Zig Ziglar",
    "The future belongs to those who believe in the beauty of their dreams. — Eleanor Roosevelt",
    "Believe you can and you're halfway there. — Theodore Roosevelt",
]


class NLPEngine:
    def __init__(self):
        self.nlp_lib = None
        self._try_load_spacy()
        self._try_load_nltk()
        print(f"{COLORS['green']}✓ NLP engine ready{COLORS['reset']}")

    def _try_load_spacy(self):
        try:
            import spacy
            self.nlp_lib = spacy.load("en_core_web_sm")
        except Exception:
            pass

    def _try_load_nltk(self):
        if self.nlp_lib:
            return
        try:
            import nltk
            try: nltk.data.find("tokenizers/punkt")
            except LookupError: nltk.download("punkt", quiet=True)
        except Exception:
            pass

    def classify_intent(self, text: str) -> str:
        text_lower = text.lower().strip()
        if not text_lower:
            return "unknown"
        for intent, patterns in INTENT_PATTERNS:
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return intent
        return "unknown"

    def extract_search_query(self, text: str) -> str:
        for p in [r"search\s+for\s+(.+)", r"look\s+up\s+(.+)", r"google\s+(.+)", r"find\s+(.+)"]:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return text

    def tokenize(self, text: str) -> list:
        try:
            from nltk.tokenize import word_tokenize
            return word_tokenize(text.lower())
        except Exception:
            return text.lower().split()

    def generate_response(self, text: str, memory=None) -> str:
        t = text.lower()
        if any(w in t for w in ["joke", "funny"]): return random.choice(JOKES)
        if any(w in t for w in ["motivat", "inspire", "quote"]): return f"💡 {random.choice(MOTIVATIONAL_QUOTES)}"
        if memory:
            name = memory.get("user_name", "")
            suffix = f", {name}" if name else ""
            return random.choice(FALLBACK_RESPONSES).rstrip("!") + suffix + "!"
        return random.choice(FALLBACK_RESPONSES)
