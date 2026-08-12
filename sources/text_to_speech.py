"""Local text-to-speech synthesis using pyttsx3.

The :class:`TextToSpeech` class speaks text through the system audio output.
It uses the local ``pyttsx3`` engine and never sends data over the network.

The module remains importable even when ``pyttsx3`` is missing; a descriptive
error is raised when speech is attempted.
"""

import threading

try:
    import pyttsx3

    _PYTTTSX_AVAILABLE = True
except ImportError:
    pyttsx3 = None
    _PYTTTSX_AVAILABLE = False


class TextToSpeech:
    """Speak text aloud using a local TTS engine.

    The engine is initialised lazily on first use. If ``pyttsx3`` is not
    installed, constructing this class still succeeds but methods that
    need the engine raise a :class:`RuntimeError`.
    """

    def __init__(self, voice_id: str | None = None) -> None:
        self.voice_id = voice_id
        self._engine = None
        self._voice_list = None
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def list_voices(self) -> list[dict]:
        """Return all available voices as a list of ``{'id', 'name'}``."""
        self._load_voice_list()
        return list(self._voice_list)

    def set_voice(self, voice_id: str) -> None:
        """Set the current voice by identifier.

        Args:
            voice_id: Voice identifier as returned by :meth:`list_voices`.

        Raises:
            ValueError: If ``voice_id`` is not found in the available voices.
        """
        voices = self.list_voices()
        if not any(v["id"] == voice_id for v in voices):
            raise ValueError(f"Voice '{voice_id}' not found.")
        self.voice_id = voice_id
        if self._engine is not None:
            self._engine.setProperty("voice", voice_id)

    def speak(self, text: str, block: bool = False) -> None:
        """Speak the given text.

        Args:
            text: Plain text to be spoken.
            block: If ``True``, wait until speech finishes before returning.
                If ``False``, start speech in a background thread and return
                immediately.
        """
        self._ensure_available()
        if block:
            self._speak_sync(text)
        else:
            threading.Thread(
                target=self._speak_sync,
                args=(text,),
                daemon=True,
            ).start()

    def stop(self) -> None:
        """Stop any currently running speech."""
        if self._engine is not None:
            try:
                self._engine.stop()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _ensure_available(self) -> None:
        if not _PYTTTSX_AVAILABLE:
            raise RuntimeError(
                "pyttsx3 is not installed. Install it with: pip install pyttsx3"
            )

    def _get_engine(self):
        if self._engine is None:
            self._ensure_available()
            try:
                self._engine = pyttsx3.init()
            except Exception as exc:
                raise RuntimeError(
                    f"Could not initialise text-to-speech engine: {exc}"
                ) from exc
            if self.voice_id:
                self.set_voice(self.voice_id)
        return self._engine

    def _load_voice_list(self) -> None:
        if self._voice_list is not None:
            return
        self._ensure_available()
        engine = self._get_engine()
        voices = engine.getProperty("voices")
        self._voice_list = [
            {"id": v.id, "name": v.name}
            for v in voices
        ]

    def _speak_sync(self, text: str) -> None:
        engine = self._get_engine()
        engine.say(text)
        try:
            engine.runAndWait()
        except Exception:
            # Ensure any pending speech is stopped before re-raising.
            try:
                engine.stop()
            except Exception:
                pass
            raise
