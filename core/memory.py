"""
core/memory.py - Persistent Memory System
"""

import json
import os
from datetime import datetime
from core.utils import COLORS

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "memory.json")


class MemorySystem:
    """Persistent key-value store for user preferences and notes."""

    def __init__(self):
        self._store: dict = {}
        self._load()
        print(f"{COLORS['green']}✓ Memory system loaded{COLORS['reset']}")

    def get(self, key: str, default=None):
        return self._store.get(key, default)

    def set(self, key: str, value):
        self._store[key] = value
        self._store["_last_updated"] = datetime.now().isoformat()
        self._save()

    def delete(self, key: str):
        self._store.pop(key, None)
        self._save()

    def all(self) -> dict:
        return {k: v for k, v in self._store.items() if not k.startswith("_")}

    # ------------------------------------------------------------------ #
    #  Persistence                                                         #
    # ------------------------------------------------------------------ #

    def _load(self):
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    self._store = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._store = {}
        else:
            self._store = {}

    def _save(self):
        try:
            os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self._store, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"{COLORS['yellow']}⚠ Memory save failed: {e}{COLORS['reset']}")
