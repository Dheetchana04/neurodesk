"""
core/voice.py - Speech Recognition & Text-to-Speech Engine
"""

import sys
from core.utils import COLORS


class VoiceEngine:
    """Handles both speech-to-text (STT) and text-to-speech (TTS)."""

    def __init__(self, enabled=True):
        self.tts_engine = None
        self.recognizer = None
        self.microphone = None
        self.enabled = enabled
        self.stt_available = False

        self._init_tts()
        self._init_stt()

    # ------------------------------------------------------------------ #
    #  Initialization                                                      #
    # ------------------------------------------------------------------ #

    def _init_tts(self):
        if not self.enabled:
            return
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty("rate", 165)
            self.tts_engine.setProperty("volume", 0.9)
            # Prefer a female voice if available
            voices = self.tts_engine.getProperty("voices")
            for v in voices:
                if "female" in v.name.lower() or "zira" in v.name.lower():
                    self.tts_engine.setProperty("voice", v.id)
                    break
            print(f"{COLORS['green']}✓ TTS engine ready{COLORS['reset']}")
        except ImportError:
            print(f"{COLORS['yellow']}⚠ pyttsx3 not found – voice output disabled{COLORS['reset']}")
            self.enabled = False
        except Exception as e:
            print(f"{COLORS['yellow']}⚠ TTS init failed: {e}{COLORS['reset']}")
            self.enabled = False

    def _init_stt(self):
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            self.microphone = sr.Microphone()
            self.stt_available = True
            print(f"{COLORS['green']}✓ STT engine ready{COLORS['reset']}")
        except ImportError:
            print(f"{COLORS['yellow']}⚠ SpeechRecognition not found – using text input{COLORS['reset']}")
        except Exception as e:
            print(f"{COLORS['yellow']}⚠ Microphone unavailable: {e}{COLORS['reset']}")

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def speak(self, text: str):
        """Convert text to speech."""
        if not self.enabled or not self.tts_engine:
            return
        try:
            # Strip emojis for cleaner TTS
            clean = self._strip_emojis(text)
            self.tts_engine.say(clean)
            self.tts_engine.runAndWait()
        except RuntimeError:
            # runAndWait called while engine is busy – safe to ignore
            pass
        except Exception as e:
            print(f"{COLORS['dim']}[TTS error: {e}]{COLORS['reset']}")

    def listen(self, timeout=5, phrase_limit=10) -> str:
        """Listen from microphone and return transcribed text."""
        if not self.stt_available:
            return ""

        import speech_recognition as sr
        print(f"{COLORS['dim']}🎤 Listening...{COLORS['reset']}", end="\r")

        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_limit
                )
            text = self.recognizer.recognize_google(audio)
            return text.strip()

        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            print(f"{COLORS['dim']}Could not understand audio.{COLORS['reset']}")
            return ""
        except sr.RequestError as e:
            print(f"{COLORS['yellow']}⚠ Google STT unavailable: {e}{COLORS['reset']}")
            self.stt_available = False
            return ""
        except Exception as e:
            print(f"{COLORS['dim']}[STT error: {e}]{COLORS['reset']}")
            return ""

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _strip_emojis(text: str) -> str:
        """Remove emoji characters for cleaner TTS output."""
        import re
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002700-\U000027BF"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE,
        )
        return emoji_pattern.sub("", text).strip()
