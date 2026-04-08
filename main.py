"""
NeuroDesk – AI Student Cognitive Assistant
Run: python main.py              → CLI mode
     python main.py --web        → Flask dashboard
     python main.py --text-only  → No microphone
     python main.py --no-voice   → No TTS
"""
import sys, argparse

def main():
    p = argparse.ArgumentParser(description="NeuroDesk AI Assistant")
    p.add_argument("--web",       action="store_true", help="Launch Flask dashboard")
    p.add_argument("--no-voice",  action="store_true", help="Disable voice output")
    p.add_argument("--text-only", action="store_true", help="Text input only")
    args = p.parse_args()

    if args.web:
        from app import create_app
        app = create_app()
        print("\n🧠 NeuroDesk Dashboard → http://127.0.0.1:5000\n")
        app.run(debug=False, use_reloader=False)
    else:
        from core.assistant import Assistant
        bot = Assistant(
            voice_enabled=not args.no_voice,
            voice_input=not args.text_only
        )
        bot.run()

if __name__ == "__main__":
    main()
