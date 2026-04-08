# 🧠 NeuroDesk – AI Student Cognitive Assistant

An intelligent **AI-powered student productivity assistant** that understands mood, detects burnout, tracks productivity, and adapts study plans dynamically. NeuroDesk combines conversational AI, cognitive intelligence, and a real-time dashboard into one unified system.

🌐 **Live Demo:** [https://neurodesk-kd64.onrender.com](https://neurodesk-kd64.onrender.com)

---

# 🚀 Core Idea

NeuroDesk is **not just another chatbot**.

It is a **Cognitive AI Assistant** that:

* Understands student behavior
* Detects burnout & fatigue
* Tracks productivity
* Adapts study plans
* Responds emotionally
* Remembers preferences

Designed specifically for **students preparing for exams, interviews, and daily study planning**.

---

# ✨ Unique Features

## 🧠 Cognitive Study Planner

Not just a timetable generator.

NeuroDesk adapts schedule based on:

* Available time
* Subject difficulty
* User mood
* Cognitive load

If you're tired, hard subjects automatically become lighter.

---

## 🔴 Burnout Detection (Rare Feature)

Detects phrases like:

* "I'm tired"
* "I can't focus"
* "My brain is fried"

Then automatically:

* Suggests break
* Recommends lighter tasks
* Gives motivational response
* Adjusts schedule difficulty

---

## 📊 Productivity Scoring System

Tracks:

* Tasks completed
* Focus sessions
* Notes saved
* Study plans created

Generates:

* Daily productivity %
* Performance label ("On Fire", "Solid Day")
* Weekly analytics
* Persistent progress tracking

---

## 🎯 Focus Mode

Natural language focus sessions:

Examples:

* "Start focus for 25 minutes"
* "Focus on DSA for 30 min"

Features:

* Countdown timer
* Distraction blocking (simulated)
* Motivation prompts
* Session logging
* Dashboard progress bar

---

## 🧠 Smart Memory System

NeuroDesk remembers:

* Your name
* Preferences
* Study habits
* Important notes
* Exams

Examples:

* "My name is Alex"
* "Remember I study at night"
* "Don't forget exam Friday"

All stored in persistent JSON memory.

---

## 🎓 Academic Assistant

Supports:

* DSA explanations
* Interview questions
* CS fundamentals
* Study tips
* Coding concepts
* STAR interview guidance

Examples:

* "Explain recursion"
* "Stack vs Queue"
* "Give Python interview questions"

---

## 😊 Emotional AI Layer (Advanced)

Detects moods:

* stressed
* tired
* happy
* sad
* bored
* angry

Adds empathetic response automatically before answering.

Example:

> "You seem stressed. Let's take this step by step..."

---

## ✅ Task Manager + Reminders

Natural language task system:

Examples:

* "Add task finish assignment"
* "Remind me to study at 6pm"

Features:

* Task list
* Reminder system
* Completion tracking
* Dashboard sync

---

## 💬 Conversational AI Engine

* 30+ intent detection
* Regex-based NLP engine
* Context-aware responses
* Academic fallback
* Mood-aware responses

---

## 📜 Chat History

* Stores last 500 messages
* Timestamped logs
* API access
* Dashboard integration

---

## 🎙️ Voice I/O (Optional)

Voice input:

* SpeechRecognition

Voice output:

* pyttsx3

Fallback:

* Text mode if mic unavailable

---

# 🛠 Tech Stack

| Layer        | Technology        |
| ------------ | ----------------- |
| Language     | Python 3          |
| Backend      | Flask             |
| NLP          | Regex + NLTK      |
| Voice Input  | SpeechRecognition |
| Voice Output | pyttsx3           |
| Storage      | JSON              |
| Frontend     | HTML CSS JS       |
| Dashboard    | Vanilla JS        |
| Deployment   | Render            |
| Charts       | JavaScript        |

---

# 📁 Project Structure

```
neurodesk/
│
├── app.py
├── main.py
├── requirements.txt
│
├── core/
│   ├── assistant.py
│   ├── nlp_engine.py
│   ├── command_handler.py
│   ├── mood_detector.py
│   ├── burnout_detector.py
│   ├── productivity_scorer.py
│   ├── focus_mode.py
│   ├── academic_assistant.py
│   ├── memory.py
│   ├── task_manager.py
│   ├── study_scheduler.py
│   └── chat_history.py
│
├── templates/
│   └── dashboard.html
│
├── data/
└── logs/
```

---

# 🔌 API Endpoints

| Endpoint        | Description   |
| --------------- | ------------- |
| `/`             | Dashboard     |
| `/api/chat`     | AI chatbot    |
| `/api/tasks`    | Tasks         |
| `/api/score`    | Productivity  |
| `/api/focus`    | Focus mode    |
| `/api/schedule` | Study planner |
| `/api/memory`   | Memory        |
| `/api/history`  | Chat history  |
| `/api/burnout`  | Burnout stats |

---

# ⚡ Run Locally

Clone repo

```
git clone https://github.com/Dheetchana04/neurodesk.git
cd neurodesk
```

Create venv

```
python -m venv venv
```

Activate

Windows

```
venv\Scripts\activate
```

Install

```
pip install -r requirements.txt
```

Run

```
python main.py --web
```

Open:

```
http://127.0.0.1:5000
```

---

# 🌐 Deployment

Deployed on Render:

[https://neurodesk-kd64.onrender.com](https://neurodesk-kd64.onrender.com)

---

# 💡 What Makes This Project Special

Unlike normal chatbots, NeuroDesk:

* Detects burnout
* Adapts schedule to mood
* Tracks productivity
* Provides academic help
* Has focus timer
* Remembers preferences
* Responds emotionally

This makes it a **complete AI study companion**.

---

# 👩‍💻 Author

Dheetchana | Final Year CSE

