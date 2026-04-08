"""
core/study_scheduler.py - Intelligent Study Schedule Generator
"""

import json
import os
from datetime import datetime, timedelta
from core.utils import COLORS

SCHEDULE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "schedules.json")

# Pomodoro-style block recommendations
DIFFICULTY_BLOCKS = {
    "hard":   {"study": 50, "break": 10},
    "medium": {"study": 45, "break": 10},
    "easy":   {"study": 30, "break": 5},
}

TECHNIQUES = {
    "hard":   "Deep Work — no distractions, full focus",
    "medium": "Active Recall — flashcards & practice problems",
    "easy":   "Spaced Repetition — review & light reading",
}


class StudyScheduler:
    """Generates personalized, optimized study schedules."""

    def interactive_schedule(self) -> str:
        """Guide the user through schedule creation interactively."""
        print(f"\n{COLORS['cyan']}╔══════════════════════════════════════╗{COLORS['reset']}")
        print(f"{COLORS['cyan']}║       📚 STUDY SCHEDULE GENERATOR    ║{COLORS['reset']}")
        print(f"{COLORS['cyan']}╚══════════════════════════════════════╝{COLORS['reset']}")

        # --- Gather subjects ---
        subjects = []
        print("\nEnter your subjects (one per line). Press Enter with no input when done.")
        print("Format: <subject name> [difficulty: easy/medium/hard]")
        print("Example: Mathematics hard   |   History easy\n")

        while True:
            line = input(f"  Subject {len(subjects)+1}: ").strip()
            if not line:
                break
            # Support formats: "Maths hard" or "Maths | hard" or "Maths|hard"
            line = line.replace("|", " ")
            parts = line.split()
            difficulty = "medium"
            if parts and parts[-1].lower() in DIFFICULTY_BLOCKS:
                difficulty = parts[-1].lower()
                name = " ".join(parts[:-1]).strip()
            else:
                name = " ".join(parts).strip()
            if name:
                subjects.append({"name": name, "difficulty": difficulty})

        if not subjects:
            return "No subjects entered. Schedule generation cancelled."

        # --- Gather available hours ---
        print("\nHow many hours do you have available today for studying?")
        while True:
            try:
                hours_input = input("  Available hours (e.g. 4 or 4.5): ").strip()
                total_hours = float(hours_input)
                if 0 < total_hours <= 16:
                    break
                print("  Please enter a value between 0.1 and 16.")
            except ValueError:
                print("  Please enter a valid number.")

        total_minutes = int(total_hours * 60)

        # --- Start time ---
        print("\nWhat time do you want to start? (24h format, e.g. 09:00 or 14:30)")
        while True:
            t_str = input("  Start time [default 09:00]: ").strip() or "09:00"
            try:
                start = datetime.strptime(t_str, "%H:%M")
                start = datetime.now().replace(
                    hour=start.hour, minute=start.minute, second=0, microsecond=0
                )
                break
            except ValueError:
                print("  Invalid format. Use HH:MM.")

        # --- Generate schedule ---
        schedule = self._generate(subjects, total_minutes, start)

        # --- Display ---
        output = self._format_schedule(schedule, subjects, total_hours, start)
        print(output)

        # --- Save ---
        self._save_schedule(schedule, subjects, total_hours)

        return "Your study schedule is ready! I've printed it above and saved it."

    # ------------------------------------------------------------------ #
    #  Generation Algorithm                                                #
    # ------------------------------------------------------------------ #

    def _generate(self, subjects, total_minutes, start):
        """Allocate time slots to subjects based on difficulty weighting."""
        # Weight: hard=3, medium=2, easy=1
        weight_map = {"hard": 3, "medium": 2, "easy": 1}
        weights = [weight_map[s["difficulty"]] for s in subjects]
        total_weight = sum(weights)

        # Distribute time proportionally
        allocations = []
        remaining = total_minutes
        for i, (s, w) in enumerate(zip(subjects, weights)):
            if i == len(subjects) - 1:
                mins = remaining
            else:
                mins = int((w / total_weight) * total_minutes)
                remaining -= mins
            allocations.append({"subject": s, "minutes": max(mins, 20)})

        # Build time blocks (Pomodoro-style)
        schedule_blocks = []
        current_time = start

        for alloc in allocations:
            s = alloc["subject"]
            block_cfg = DIFFICULTY_BLOCKS[s["difficulty"]]
            study_block = block_cfg["study"]
            break_block = block_cfg["break"]
            remaining_mins = alloc["minutes"]

            while remaining_mins > 0:
                actual_study = min(study_block, remaining_mins)
                end_time = current_time + timedelta(minutes=actual_study)
                schedule_blocks.append({
                    "type": "study",
                    "subject": s["name"],
                    "difficulty": s["difficulty"],
                    "start": current_time.strftime("%H:%M"),
                    "end": end_time.strftime("%H:%M"),
                    "duration": actual_study,
                    "technique": TECHNIQUES[s["difficulty"]],
                })
                current_time = end_time
                remaining_mins -= actual_study

                if remaining_mins > 0:
                    break_end = current_time + timedelta(minutes=break_block)
                    schedule_blocks.append({
                        "type": "break",
                        "start": current_time.strftime("%H:%M"),
                        "end": break_end.strftime("%H:%M"),
                        "duration": break_block,
                    })
                    current_time = break_end

        return schedule_blocks

    # ------------------------------------------------------------------ #
    #  Formatting                                                          #
    # ------------------------------------------------------------------ #

    def _format_schedule(self, blocks, subjects, total_hours, start):
        lines = [
            f"\n{COLORS['cyan']}{'═'*58}{COLORS['reset']}",
            f"{COLORS['cyan']}  📅 OPTIMIZED STUDY SCHEDULE — {start.strftime('%A, %b %d')}{COLORS['reset']}",
            f"{COLORS['cyan']}{'═'*58}{COLORS['reset']}",
            f"  Subjects: {', '.join(s['name'] for s in subjects)}",
            f"  Total study time: {total_hours} hours",
            f"{'─'*58}",
        ]

        for b in blocks:
            if b["type"] == "study":
                diff_color = {
                    "hard": COLORS["red"],
                    "medium": COLORS["yellow"],
                    "easy": COLORS["green"],
                }.get(b["difficulty"], "")
                lines.append(
                    f"  {b['start']} – {b['end']}  "
                    f"{diff_color}📚 {b['subject']} ({b['difficulty'].upper()}) "
                    f"— {b['duration']}min{COLORS['reset']}"
                )
                lines.append(f"       💡 Technique: {b['technique']}")
            else:
                lines.append(
                    f"  {b['start']} – {b['end']}  "
                    f"{COLORS['dim']}☕ Break — {b['duration']}min{COLORS['reset']}"
                )

        lines.append(f"{'═'*58}")
        lines.append(f"  ✅ Schedule complete! You've got this! 💪")
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    #  Persistence                                                         #
    # ------------------------------------------------------------------ #

    def _save_schedule(self, blocks, subjects, total_hours):
        os.makedirs(os.path.dirname(SCHEDULE_FILE), exist_ok=True)
        data = {
            "generated": datetime.now().isoformat(),
            "total_hours": total_hours,
            "subjects": subjects,
            "blocks": blocks,
        }
        existing = []
        if os.path.exists(SCHEDULE_FILE):
            try:
                with open(SCHEDULE_FILE) as f:
                    existing = json.load(f)
            except Exception:
                existing = []
        existing.append(data)
        with open(SCHEDULE_FILE, "w") as f:
            json.dump(existing[-10:], f, indent=2)  # keep last 10
