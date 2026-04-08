"""
core/command_handler.py - NeuroDesk Master Intent Router
"""

import re
import webbrowser
import subprocess
import platform
import random
from datetime import datetime, timedelta
from core.utils import COLORS

HELP_TEXT = """
╔══════════════════════════════════════════════════╗
║           NEURODESK — COMMAND GUIDE              ║
╠══════════════════════════════════════════════════╣
║ 🌐 WEB & APPS                                   ║
║   open youtube / open google                    ║
║   search for <query>  /  open notepad           ║
║                                                 ║
║ ⏰ TIME & INFO                                   ║
║   what time is it  /  what's the date           ║
║                                                 ║
║ ✅ TASK MANAGER                                  ║
║   add task <text> [at HH:MM]                    ║
║   remind me to <text> at HH:MM                  ║
║   show tasks  /  complete task <n>              ║
║                                                 ║
║ 🎯 FOCUS MODE                                    ║
║   start focus session 25 min                    ║
║   start focus for 1 hour on Physics             ║
║   focus status  /  stop focus                   ║
║   focus summary                                 ║
║                                                 ║
║ 📊 PRODUCTIVITY                                  ║
║   my productivity score                         ║
║   weekly summary                                ║
║                                                 ║
║ 📚 STUDY SCHEDULER                               ║
║   generate study schedule / plan my studies     ║
║                                                 ║
║ 🎓 ACADEMIC ASSISTANT                            ║
║   explain stack vs queue                        ║
║   explain recursion / explain Big O             ║
║   give me Python interview questions            ║
║   give me a study tip                           ║
║                                                 ║
║ 🧠 MEMORY                                        ║
║   my name is <n>  /  call me <n>            ║
║   remember that <fact>                          ║
║   what do you remember                          ║
║                                                 ║
║ 💬 OTHER                                         ║
║   tell me a joke  /  motivate me                ║
║   show history  /  help  /  bye                 ║
╚══════════════════════════════════════════════════╝
"""

SYSTEM_APPS = {
    "notepad":     {"Windows": "notepad",    "Darwin": "open -a TextEdit",    "Linux": "gedit"},
    "calculator":  {"Windows": "calc",       "Darwin": "open -a Calculator",  "Linux": "gnome-calculator"},
    "browser":     {"Windows": "start chrome","Darwin": "open -a Safari",     "Linux": "xdg-open https://google.com"},
    "files":       {"Windows": "explorer",   "Darwin": "open -a Finder",      "Linux": "nautilus"},
    "terminal":    {"Windows": "start cmd",  "Darwin": "open -a Terminal",    "Linux": "gnome-terminal"},
    "vscode":      {"Windows": "code",       "Darwin": "code",                "Linux": "code"},
}


class CommandHandler:
    def __init__(self, assistant, tasks, scheduler, memory,
                 focus_mode=None, scorer=None, academic=None, burnout=None):
        self.assistant  = assistant
        self.tasks      = tasks
        self.scheduler  = scheduler
        self.memory     = memory
        self.focus      = focus_mode
        self.scorer     = scorer
        self.academic   = academic
        self.burnout    = burnout
        self.os_name    = platform.system()

        self._map = {
            "greet":              self._greet,
            "goodbye":            self._goodbye,
            "thanks":             self._thanks,
            "help":               self._help,
            "time":               self._time,
            "date":               self._date,
            "open_youtube":       self._youtube,
            "open_google":        self._google,
            "web_search":         self._search,
            "open_app":           self._open_app,
            "add_task":           self._add_task,
            "view_tasks":         self._view_tasks,
            "complete_task":      self._complete_task,
            "study_schedule":     self._study_schedule,
            "set_name":           self._set_name,
            "note":               self._note,
            "recall_memory":      self._recall,
            "view_history":       self._history,
            "focus_start":        self._focus_start,
            "focus_stop":         self._focus_stop,
            "focus_status":       self._focus_status,
            "focus_summary":      self._focus_summary,
            "productivity_score": self._productivity_score,
            "weekly_summary":     self._weekly_summary,
            "explain_concept":    self._explain,
            "interview_prep":     self._interview,
            "study_tip":          self._study_tip,
            "mood_check":         self._mood_check,
            "motivate":           self._motivate,
            "joke":               self._joke,
            "math":               self._math,
        }

    def handle(self, intent: str, raw_text: str, mood: str = "neutral") -> str:
        handler = self._map.get(intent)
        if handler:
            result = handler(raw_text)
            # Auto-score certain actions
            if self.scorer:
                if intent == "complete_task" and result and "done" in result.lower():
                    self.scorer.record("task_complete", raw_text[:40])
                elif intent == "note":
                    self.scorer.record("note_saved")
                elif intent == "add_task" and "reminder" in result.lower():
                    self.scorer.record("reminder_set")
                elif intent == "study_schedule":
                    self.scorer.record("study_scheduled")
            return result or ""
        return ""

    # ── Greetings / System ─────────────────────────────────────────────
    def _greet(self, text):
        name = self.memory.get("user_name", "friend")
        score_info = ""
        if self.scorer:
            s = self.scorer.get_score()
            if s["score"] > 0:
                score_info = f" You're at {s['score']}% productivity today."
        return random.choice([
            f"Hey {name}! Ready to get things done?{score_info}",
            f"Hello {name}! Let's make today count!{score_info}",
            f"Hi {name}! 🚀 What are we tackling today?{score_info}",
        ])

    def _goodbye(self, text):
        name = self.memory.get("user_name", "")
        report = ""
        if self.scorer:
            s = self.scorer.get_score()
            report = f" Final score: {s['score']}% — {s['label']}"
        self.assistant.running = False
        return f"Goodbye{' ' + name if name else ''}!{report} Keep growing! 💪"

    def _thanks(self, text):
        return random.choice(["You're welcome! 😊", "Happy to help!", "Anytime! That's what I'm here for."])

    def _help(self, text):
        print(HELP_TEXT)
        return "Here's everything NeuroDesk can do! Just ask away."

    # ── Time / Date ────────────────────────────────────────────────────
    def _time(self, text):
        return f"It's currently {datetime.now().strftime('%I:%M %p')}. ⏰"

    def _date(self, text):
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}. 📅"

    # ── Web / Apps ─────────────────────────────────────────────────────
    def _youtube(self, text):
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube! 🎬"

    def _google(self, text):
        webbrowser.open("https://www.google.com")
        return "Opening Google! 🌐"

    def _search(self, text):
        query = re.sub(r"^(search\s+(for)?|look\s+up|google|find)\s+", "", text, flags=re.IGNORECASE).strip()
        if not query:
            return "What would you like me to search for?"
        webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
        return f"Searching Google for: '{query}' 🔍"

    def _open_app(self, text):
        for app_key, cmd_map in SYSTEM_APPS.items():
            if app_key in text.lower():
                cmd = cmd_map.get(self.os_name, "")
                if cmd:
                    try:
                        subprocess.Popen(cmd, shell=True)
                        return f"Opening {app_key.capitalize()}! 🖥️"
                    except Exception as e:
                        return f"Couldn't open {app_key}: {e}"
        m = re.search(r"open\s+(.+?)(?:\s+app)?$", text, re.IGNORECASE)
        if m:
            app = m.group(1).strip()
            try:
                if self.os_name == "Windows":
                    subprocess.Popen(["start", app], shell=True)
                elif self.os_name == "Darwin":
                    subprocess.Popen(["open", "-a", app])
                else:
                    subprocess.Popen([app])
                return f"Trying to open {app}..."
            except Exception:
                return f"I couldn't find '{app}'. Make sure it's installed."
        return ""

    # ── Tasks / Reminders ──────────────────────────────────────────────
    def _add_task(self, text):
        time_match = re.search(r"at\s+(\d{1,2}:\d{2}(?:\s*[ap]m)?)", text, re.IGNORECASE)
        task_text = re.sub(r"^(add\s+task|remind\s+me\s+to|set\s+(a\s+)?reminder\s+(to|for)?)\s+",
                           "", text, flags=re.IGNORECASE)
        task_text = re.sub(r"\s+at\s+\d{1,2}:\d{2}.*$", "", task_text, flags=re.IGNORECASE).strip()
        reminder_time = None
        if time_match:
            t_str = time_match.group(1).strip()
            now = datetime.now()
            for fmt in ("%I:%M %p", "%H:%M"):
                try:
                    parsed = datetime.strptime(t_str.upper(), fmt)
                    reminder_time = now.replace(hour=parsed.hour, minute=parsed.minute, second=0, microsecond=0)
                    if reminder_time < now:
                        reminder_time += timedelta(days=1)
                    break
                except ValueError:
                    continue
        tid = self.tasks.add_task(task_text, reminder_time=reminder_time)
        if reminder_time:
            return f"✅ Task added: '{task_text}' — reminder set for {reminder_time.strftime('%I:%M %p')}. Task #{tid}"
        return f"✅ Task added: '{task_text}'. Task #{tid}"

    def _view_tasks(self, text):
        all_tasks = self.tasks.get_all_tasks()
        if not all_tasks:
            return "No tasks yet! Add one with 'add task <text>'."
        lines = ["\n📋 YOUR TASKS:"]
        for t in all_tasks:
            status = "✅" if t["done"] else "⬜"
            reminder = f" ⏰ {t['reminder_time'][11:16]}" if t.get("reminder_time") else ""
            lines.append(f"  {status} [{t['id']}] {t['text']}{reminder}")
        return "\n".join(lines)

    def _complete_task(self, text):
        nums = re.findall(r"\d+", text)
        if nums:
            tid = int(nums[0])
            if self.tasks.complete_task(tid):
                return f"✅ Task #{tid} marked as done! Great job! 🎉"
            return f"Task #{tid} not found."
        return "Which task number would you like to complete?"

    # ── Study Schedule ─────────────────────────────────────────────────
    def _study_schedule(self, text):
        return self.scheduler.interactive_schedule()

    # ── Memory ─────────────────────────────────────────────────────────
    def _set_name(self, text):
        for p in [r"my name is\s+(\w+)", r"call me\s+(\w+)"]:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                name = m.group(1).capitalize()
                self.memory.set("user_name", name)
                return f"Nice to meet you, {name}! I'll remember that. 😊"
        return "What's your name? Say 'My name is <name>'."

    def _note(self, text):
        note = re.sub(r"^(remember\s+that|note\s+that|don.t\s+forget)\s*", "", text, flags=re.IGNORECASE).strip()
        if not note:
            return "What would you like me to remember?"
        notes = self.memory.get("user_notes", [])
        notes.append(note)
        self.memory.set("user_notes", notes[-20:])
        return f"Got it! I'll remember: '{note}' 🧠"

    def _recall(self, text):
        facts = self.memory.get("user_notes", [])
        name = self.memory.get("user_name", "")
        lines = []
        if name:
            lines.append(f"Your name: {name}")
        if facts:
            lines.append("Things you asked me to remember:")
            for f in facts[-5:]:
                lines.append(f"  • {f}")
        if not lines:
            return "I don't have anything stored yet. Tell me something to remember!"
        return "\n".join(lines)

    def _history(self, text):
        from core.chat_history import ChatHistory
        hist = ChatHistory()
        entries = hist.get_recent(10)
        if not entries:
            return "No chat history yet!"
        lines = ["\n📜 RECENT CHAT HISTORY:"]
        for e in entries:
            label = "You" if e["role"] == "user" else "NeuroDesk"
            lines.append(f"  [{e['timestamp']}] {label}: {e['message'][:80]}")
        return "\n".join(lines)

    # ── Focus Mode ─────────────────────────────────────────────────────
    def _focus_start(self, text):
        if not self.focus:
            return "Focus mode module not available."
        duration = self.focus.parse_duration(text)
        # Extract subject if mentioned
        subject = ""
        m = re.search(r"on\s+(.+?)(?:\s+for|\s*$)", text, re.IGNORECASE)
        if m:
            subj = m.group(1).strip()
            if not re.match(r"^\d", subj):
                subject = subj
        return self.focus.start(duration, subject)

    def _focus_stop(self, text):
        if not self.focus:
            return "Focus mode module not available."
        return self.focus.stop()

    def _focus_status(self, text):
        if not self.focus:
            return "Focus mode module not available."
        return self.focus.status()

    def _focus_summary(self, text):
        if not self.focus:
            return "Focus mode module not available."
        return self.focus.get_today_summary()

    # ── Productivity Score ─────────────────────────────────────────────
    def _productivity_score(self, text):
        if not self.scorer:
            return "Productivity scorer not available."
        return self.scorer.format_score()

    def _weekly_summary(self, text):
        if not self.scorer:
            return "Productivity scorer not available."
        return self.scorer.get_weekly_summary()

    # ── Academic Assistant ─────────────────────────────────────────────
    def _explain(self, text):
        if not self.academic:
            return "Academic assistant not available."
        result = self.academic.explain(text)
        if result:
            return result
        # Fallback: couldn't match a concept
        return (
            "I don't have a built-in explanation for that specific topic yet. "
            "Try: explain stack vs queue, explain recursion, explain Big O, "
            "explain OOP, explain binary search, explain sorting algorithms, "
            "explain git, explain database, or explain Python."
        )

    def _interview(self, text):
        if not self.academic:
            return "Academic assistant not available."
        return self.academic.get_interview_questions(text)

    def _study_tip(self, text):
        if not self.academic:
            return "Academic assistant not available."
        return self.academic.get_study_tip()

    # ── Mood / Fun ─────────────────────────────────────────────────────
    def _mood_check(self, text):
        return random.choice([
            "Running at 100%! Ready to help you crush your goals. 🚀",
            "All systems go! What are we tackling today?",
            "Feeling great! Let's make some progress together. 💪",
        ])

    def _motivate(self, text):
        from core.nlp_engine import MOTIVATIONAL_QUOTES
        return f"💡 {random.choice(MOTIVATIONAL_QUOTES)}"

    def _joke(self, text):
        from core.nlp_engine import JOKES
        return random.choice(JOKES)

    def _math(self, text):
        expr = re.sub(r"[^0-9+\-*/().\s]", "", text).strip()
        if not expr:
            return "Please provide a mathematical expression."
        try:
            result = eval(expr, {"__builtins__": {}})
            return f"🧮 {expr} = {result}"
        except Exception:
            return "I couldn't compute that. Check your expression."
