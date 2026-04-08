"""
core/chat_history.py - Conversation History Logger
"""

import json
import os
from datetime import datetime
from typing import List, Dict

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "..", "logs", "chat_history.json")


class ChatHistory:
    """Logs and retrieves conversation history."""

    def __init__(self):
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        self._history: List[Dict] = self._load()

    def log(self, role: str, message: str):
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "role": role,
            "message": message,
        }
        self._history.append(entry)
        self._save()

    def get_recent(self, n: int = 20) -> List[Dict]:
        return self._history[-n:]

    def get_all(self) -> List[Dict]:
        return list(self._history)

    def clear(self):
        self._history = []
        self._save()

    def _load(self) -> List[Dict]:
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _save(self):
        try:
            # Keep last 500 entries to avoid bloat
            trimmed = self._history[-500:]
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(trimmed, f, indent=2, ensure_ascii=False)
        except IOError:
            pass
