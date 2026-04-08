"""
core/utils.py - Shared Utilities
"""

import sys
import time

# ANSI color codes (auto-disabled on Windows if no ANSI support)
COLORS = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "dim":    "\033[2m",
    "cyan":   "\033[96m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "red":    "\033[91m",
    "blue":   "\033[94m",
    "magenta":"\033[95m",
}

# Disable colors on Windows if not supported
if sys.platform == "win32":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        COLORS = {k: "" for k in COLORS}


def typing_print(text: str, delay: float = 0.012):
    """Print text with a typewriter animation effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()  # newline at end
