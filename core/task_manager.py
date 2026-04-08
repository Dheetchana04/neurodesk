"""
core/task_manager.py - Task & Reminder Manager
"""

import json
import os
from datetime import datetime
from typing import List, Optional, Dict
from core.utils import COLORS

TASKS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "tasks.json")


class TaskManager:
    """Manages tasks and timed reminders, persisted to JSON."""

    def __init__(self):
        self._tasks: List[Dict] = []
        self._next_id = 1
        self._load()
        print(f"{COLORS['green']}✓ Task manager loaded ({len(self._tasks)} tasks){COLORS['reset']}")

    # ------------------------------------------------------------------ #
    #  CRUD                                                                #
    # ------------------------------------------------------------------ #

    def add_task(self, text: str, reminder_time: Optional[datetime] = None) -> int:
        task = {
            "id": self._next_id,
            "text": text,
            "done": False,
            "created": datetime.now().isoformat(),
            "reminder_time": reminder_time.isoformat() if reminder_time else None,
            "reminder_fired": False,
        }
        self._tasks.append(task)
        self._next_id += 1
        self._save()
        return task["id"]

    def complete_task(self, task_id: int) -> bool:
        for t in self._tasks:
            if t["id"] == task_id:
                t["done"] = True
                self._save()
                return True
        return False

    def delete_task(self, task_id: int) -> bool:
        before = len(self._tasks)
        self._tasks = [t for t in self._tasks if t["id"] != task_id]
        if len(self._tasks) < before:
            self._save()
            return True
        return False

    def get_all_tasks(self) -> List[Dict]:
        return sorted(self._tasks, key=lambda t: t["id"])

    def get_pending_tasks(self) -> List[Dict]:
        return [t for t in self._tasks if not t["done"]]

    # ------------------------------------------------------------------ #
    #  Reminders                                                           #
    # ------------------------------------------------------------------ #

    def get_due_reminders(self) -> List[Dict]:
        """Return tasks whose reminder time has passed and not yet fired."""
        now = datetime.now()
        due = []
        for t in self._tasks:
            if t.get("reminder_time") and not t.get("reminder_fired"):
                try:
                    rt = datetime.fromisoformat(t["reminder_time"])
                    if rt <= now:
                        due.append(t)
                except ValueError:
                    pass
        return due

    def mark_reminder_fired(self, task_id: int):
        for t in self._tasks:
            if t["id"] == task_id:
                t["reminder_fired"] = True
                self._save()
                return

    # ------------------------------------------------------------------ #
    #  Persistence                                                         #
    # ------------------------------------------------------------------ #

    def _load(self):
        os.makedirs(os.path.dirname(TASKS_FILE), exist_ok=True)
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._tasks = data.get("tasks", [])
                    self._next_id = data.get("next_id", 1)
            except (json.JSONDecodeError, IOError):
                self._tasks = []
        else:
            self._tasks = []

    def _save(self):
        try:
            with open(TASKS_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    {"tasks": self._tasks, "next_id": self._next_id},
                    f, indent=2
                )
        except IOError as e:
            print(f"{COLORS['yellow']}⚠ Task save failed: {e}{COLORS['reset']}")
