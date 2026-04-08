"""
core/academic_assistant.py - Academic Knowledge & Interview Prep Assistant
Handles CS concepts, definitions, interview questions, and study tips.
"""

import re
import random

# ── CS Concepts Knowledge Base ──────────────────────────────────────────
CS_CONCEPTS = {
    "stack vs queue": {
        "title": "Stack vs Queue",
        "explanation": (
            "📚 STACK vs QUEUE\n\n"
            "STACK (LIFO — Last In, First Out)\n"
            "  Think of a stack of plates. You add/remove from the TOP only.\n"
            "  Operations: push() → add to top | pop() → remove from top\n"
            "  Use cases: undo/redo, function call stack, browser back button\n"
            "  Example: [1, 2, 3] → pop() → [1, 2], returns 3\n\n"
            "QUEUE (FIFO — First In, First Out)\n"
            "  Think of a queue at a ticket counter. First come, first served.\n"
            "  Operations: enqueue() → add to rear | dequeue() → remove from front\n"
            "  Use cases: printer jobs, CPU scheduling, BFS traversal\n"
            "  Example: [1, 2, 3] → dequeue() → [2, 3], returns 1\n\n"
            "KEY DIFFERENCE: Stack removes newest. Queue removes oldest."
        ),
    },
    "big o notation": {
        "title": "Big O Notation",
        "explanation": (
            "📊 BIG O NOTATION — Measuring Algorithm Efficiency\n\n"
            "O(1)      — Constant  : Array index access. Always same speed.\n"
            "O(log n)  — Log       : Binary search. Halves problem each step.\n"
            "O(n)      — Linear    : Loop through array. Grows with input.\n"
            "O(n log n)— Linearithmic: Merge sort, Heap sort.\n"
            "O(n²)     — Quadratic : Nested loops. Bubble sort.\n"
            "O(2ⁿ)     — Exponential: Fibonacci recursion (naive).\n"
            "O(n!)     — Factorial : Traveling salesman brute force.\n\n"
            "RULE: Always aim for O(1) or O(log n) where possible."
        ),
    },
    "linked list": {
        "title": "Linked List",
        "explanation": (
            "🔗 LINKED LIST\n\n"
            "A sequence of nodes where each node contains DATA + a POINTER to the next node.\n\n"
            "Types:\n"
            "  Singly: A → B → C → None\n"
            "  Doubly: None ← A ⇄ B ⇄ C → None\n"
            "  Circular: A → B → C → A\n\n"
            "VS Arrays:\n"
            "  ✅ Dynamic size   ✅ O(1) insert/delete at head\n"
            "  ❌ No random access  ❌ More memory (stores pointers)\n\n"
            "Common operations: traverse O(n), insert O(1), search O(n)"
        ),
    },
    "binary search": {
        "title": "Binary Search",
        "explanation": (
            "🔍 BINARY SEARCH\n\n"
            "Works ONLY on SORTED arrays. Divide and conquer approach.\n\n"
            "Algorithm:\n"
            "  1. Set low=0, high=len-1\n"
            "  2. Find mid = (low+high)//2\n"
            "  3. If arr[mid] == target → found!\n"
            "  4. If arr[mid] < target → search right (low = mid+1)\n"
            "  5. If arr[mid] > target → search left (high = mid-1)\n"
            "  6. Repeat until found or low > high\n\n"
            "Time: O(log n) | Space: O(1) iterative, O(log n) recursive\n"
            "Example: Find 7 in [1,3,5,7,9] → check 5 → check 7 → found!"
        ),
    },
    "recursion": {
        "title": "Recursion",
        "explanation": (
            "🔄 RECURSION\n\n"
            "A function that calls itself with a smaller version of the problem.\n\n"
            "Two mandatory parts:\n"
            "  1. BASE CASE  — stops the recursion (prevents infinite loop)\n"
            "  2. RECURSIVE CASE — function calls itself with simpler input\n\n"
            "Example — Factorial:\n"
            "  factorial(5) = 5 × factorial(4)\n"
            "              = 5 × 4 × factorial(3)\n"
            "              = 5 × 4 × 3 × 2 × 1 = 120\n\n"
            "Common uses: tree traversal, divide & conquer, backtracking\n"
            "Watch out for: stack overflow (too deep), missing base case"
        ),
    },
    "oop": {
        "title": "Object-Oriented Programming",
        "explanation": (
            "🏗 OOP — 4 PILLARS\n\n"
            "1. ENCAPSULATION\n"
            "   Bundling data + methods. Hide internals, expose interface.\n"
            "   Example: BankAccount has balance (private) + deposit() (public)\n\n"
            "2. ABSTRACTION\n"
            "   Show only what's necessary, hide complexity.\n"
            "   Example: drive() works without knowing the engine internals.\n\n"
            "3. INHERITANCE\n"
            "   Child class inherits parent's properties and methods.\n"
            "   Example: Dog extends Animal — gets eat(), sleep() for free.\n\n"
            "4. POLYMORPHISM\n"
            "   Same method name, different behavior per class.\n"
            "   Example: Animal.speak() → Dog says 'Woof', Cat says 'Meow'"
        ),
    },
    "sorting algorithms": {
        "title": "Sorting Algorithms",
        "explanation": (
            "📊 SORTING ALGORITHMS CHEAT SHEET\n\n"
            "Bubble Sort    O(n²)     — Simple, slow. For teaching only.\n"
            "Selection Sort O(n²)     — Finds min each pass. Slow.\n"
            "Insertion Sort O(n²)     — Good for small/nearly sorted data.\n"
            "Merge Sort     O(n log n)— Stable, reliable. Needs extra space.\n"
            "Quick Sort     O(n log n)— Fast in practice. Worst case O(n²).\n"
            "Heap Sort      O(n log n)— In-place but not stable.\n"
            "Counting Sort  O(n+k)    — Fastest for integers in small range.\n\n"
            "Golden rule: Use Merge Sort for linked lists, Quick Sort for arrays."
        ),
    },
    "git": {
        "title": "Git Essentials",
        "explanation": (
            "🔧 GIT ESSENTIAL COMMANDS\n\n"
            "git init           — Initialize new repo\n"
            "git clone <url>    — Copy remote repo\n"
            "git add .          — Stage all changes\n"
            "git commit -m 'msg'— Save staged changes\n"
            "git push           — Upload to remote\n"
            "git pull           — Download + merge remote changes\n"
            "git branch <name>  — Create new branch\n"
            "git checkout <name>— Switch branch\n"
            "git merge <branch> — Merge branch into current\n"
            "git log --oneline  — View commit history\n"
            "git status         — See what's changed\n"
            "git diff           — See exact changes\n\n"
            "Flow: edit → git add → git commit → git push"
        ),
    },
    "database": {
        "title": "Database Basics",
        "explanation": (
            "🗄 DATABASE BASICS\n\n"
            "SQL (Relational):\n"
            "  Data in tables with rows and columns.\n"
            "  ACID properties: Atomic, Consistent, Isolated, Durable\n"
            "  Examples: MySQL, PostgreSQL, SQLite\n\n"
            "NoSQL (Non-relational):\n"
            "  Document: MongoDB (JSON-like documents)\n"
            "  Key-Value: Redis (fast caching)\n"
            "  Graph: Neo4j (relationships)\n\n"
            "Key SQL:\n"
            "  SELECT * FROM users WHERE age > 18;\n"
            "  INSERT INTO users (name) VALUES ('Alice');\n"
            "  UPDATE users SET age=20 WHERE id=1;\n"
            "  DELETE FROM users WHERE id=1;\n\n"
            "Joins: INNER (match both), LEFT (all left + matches)"
        ),
    },
    "python": {
        "title": "Python Key Concepts",
        "explanation": (
            "🐍 PYTHON KEY CONCEPTS\n\n"
            "Data structures: list [], tuple (), dict {}, set {}\n"
            "List comp: [x*2 for x in range(10) if x%2==0]\n"
            "Lambda: f = lambda x: x**2  →  f(3) = 9\n"
            "Decorators: @property, @staticmethod, @classmethod\n"
            "Generators: yield instead of return (memory efficient)\n"
            "Context manager: with open('file') as f:\n"
            "*args: variable positional args  **kwargs: variable keyword args\n"
            "GIL: Global Interpreter Lock — Python threads aren't truly parallel\n"
            "PEP8: Python style guide — snake_case, 4 spaces indent\n\n"
            "Common libs: os, sys, re, json, datetime, collections, itertools"
        ),
    },
}

# ── Interview Questions Bank ─────────────────────────────────────────────
INTERVIEW_QUESTIONS = {
    "python": [
        "What is the difference between a list and a tuple in Python?",
        "Explain Python's GIL (Global Interpreter Lock).",
        "What are Python decorators? Give an example.",
        "What is the difference between deep copy and shallow copy?",
        "How does Python manage memory? Explain garbage collection.",
        "What are *args and **kwargs? When do you use them?",
        "Explain list comprehensions vs generator expressions.",
        "What is the difference between 'is' and '==' in Python?",
        "What are Python's built-in data types?",
        "Explain the difference between @staticmethod and @classmethod.",
    ],
    "dsa": [
        "What is the time complexity of searching in a hash map?",
        "Explain the difference between DFS and BFS.",
        "When would you use a stack vs a queue?",
        "What is dynamic programming? Give a classic example.",
        "Explain the two-pointer technique with an example.",
        "What is a balanced binary search tree? Why does balance matter?",
        "How would you detect a cycle in a linked list?",
        "Explain merge sort. Why is it preferred over quick sort sometimes?",
        "What is memoization and how does it relate to recursion?",
        "How do you find the longest common subsequence?",
    ],
    "general": [
        "What is the difference between an interpreted and compiled language?",
        "Explain REST API principles.",
        "What is the difference between SQL and NoSQL databases?",
        "Explain SOLID principles in OOP.",
        "What is the difference between synchronous and asynchronous programming?",
        "Explain how HTTP works at a high level.",
        "What is caching? Give a real-world example.",
        "What is the difference between a process and a thread?",
        "Explain version control and why it matters.",
        "What is Big O notation? Why does it matter in interviews?",
    ],
    "os": [
        "What is a deadlock? How do you prevent it?",
        "Explain the difference between paging and segmentation.",
        "What is a semaphore vs a mutex?",
        "How does virtual memory work?",
        "What is a context switch?",
        "Explain the producer-consumer problem.",
        "What is thrashing in an OS?",
        "Difference between process scheduling algorithms: FCFS, SJF, Round Robin?",
    ],
}

STUDY_TIPS = [
    "📝 Use active recall: close your notes and try to write everything from memory.",
    "🔁 Space your revision: review after 1 day, 3 days, 7 days, then 21 days.",
    "🗣 Teach it: explain the concept out loud as if teaching a 10-year-old.",
    "🖊 Write code by hand: builds deeper understanding than typing.",
    "🧩 Break complex topics into tiny sub-problems. Solve each independently.",
    "📊 Use diagrams: flowcharts and mind-maps stick better than bullet points.",
    "⏱ Use Pomodoro: 25 min focus, 5 min break. Repeat 4 times, then long break.",
    "🔗 Link new knowledge to what you already know — build mental frameworks.",
    "🧪 Practice problems > reading theory. Do at least 3 problems per concept.",
    "😴 Sleep is non-negotiable: memory consolidation happens during sleep.",
]


class AcademicAssistant:
    """Handles academic questions, CS concepts, and interview prep."""

    def __init__(self):
        self._concept_keys = list(CS_CONCEPTS.keys())

    def explain(self, text: str) -> str:
        """Try to find and explain a CS concept from the text."""
        text_lower = text.lower()
        # Direct key match
        for key in self._concept_keys:
            if key in text_lower:
                return CS_CONCEPTS[key]["explanation"]
        # Partial keyword match
        keyword_map = {
            "stack": "stack vs queue", "queue": "stack vs queue",
            "big o": "big o notation", "complexity": "big o notation",
            "link": "linked list", "node": "linked list",
            "binary": "binary search", "search": "binary search",
            "recur": "recursion", "factorial": "recursion",
            "class": "oop", "object": "oop", "inherit": "oop",
            "sort": "sorting algorithms", "bubble": "sorting algorithms",
            "merge": "sorting algorithms", "quick sort": "sorting algorithms",
            "git": "git", "commit": "git", "branch": "git",
            "sql": "database", "nosql": "database", "database": "database",
            "python": "python", "django": "python", "flask": "python",
        }
        for keyword, concept_key in keyword_map.items():
            if keyword in text_lower:
                return CS_CONCEPTS[concept_key]["explanation"]
        return ""

    def get_interview_questions(self, text: str, count: int = 5) -> str:
        """Return interview questions matching the topic."""
        text_lower = text.lower()
        category = "general"
        if any(w in text_lower for w in ["python", "django", "flask"]):
            category = "python"
        elif any(w in text_lower for w in ["dsa", "data structure", "algorithm", "leetcode"]):
            category = "dsa"
        elif any(w in text_lower for w in ["os", "operating system", "process", "thread"]):
            category = "os"

        questions = random.sample(
            INTERVIEW_QUESTIONS[category],
            min(count, len(INTERVIEW_QUESTIONS[category]))
        )
        lines = [f"\n🎯 {category.upper()} INTERVIEW QUESTIONS:"]
        for i, q in enumerate(questions, 1):
            lines.append(f"  {i}. {q}")
        lines.append("\n💡 Tip: Answer using STAR method (Situation, Task, Action, Result) for behavioral questions.")
        return "\n".join(lines)

    def get_study_tip(self) -> str:
        """Return a random study tip."""
        return f"💡 STUDY TIP:\n  {random.choice(STUDY_TIPS)}"

    def is_academic_query(self, text: str) -> bool:
        """Detect if the input is an academic/CS question."""
        academic_signals = [
            "explain", "what is", "how does", "difference between",
            "define", "interview question", "give me question",
            "study tip", "how to study", "cs concept",
            "algorithm", "data structure", "sorting", "searching",
        ]
        text_lower = text.lower()
        return any(s in text_lower for s in academic_signals)
