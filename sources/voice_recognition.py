from pathlib import Path  # noqa: F401  (kept for compatibility)
from typing import Callable, Optional
import logging
import threading

import numpy as np

from .audio_io import AudioIO
from .speech_to_text import SpeechToText

# RMS above this threshold is considered “voice present”.
VOICE_THRESHOLD = 0.02

logger = logging.getLogger(__name__)


class VoiceRecognition:
    """Transcribe microphone audio using a local Vosk model.

    Audio is captured through :class:`~.audio_io.AudioIO` and processed
    entirely offline. No network call is performed except the optional
    first‑run download of the model.
    """

    def __init__(
        self,
        audio_io: Optional[AudioIO] = None,
        model_path: Optional[str] = None,
        language: str = "en",
    ) -> None:
        # Vosk requires 16kHz mono audio. If the caller provides an AudioIO
        # instance that already uses 16kHz, reuse it; otherwise create our own.
        if audio_io is not None and audio_io.sample_rate == 16000:
            self.audio = audio_io
        else:
            self.audio = AudioIO(sample_rate=16000, channels=1)

        self.language = language
        self.stt = SpeechToText(model_path=model_path, language=language)

        # Streaming state
        self._stream_thread: Optional[threading.Thread] = None
        self._stream_stop_event = threading.Event()
        self._transcription_callback: Optional[Callable[[str, bool], None]] = None

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def transcribe(self, data: np.ndarray) -> str:
        """Transcribe a 16 kHz float32 NumPy array and return the text.

        Raises a descriptive ``RuntimeError`` if Vosk or the model cannot
        be loaded.
        """
        return self.stt.transcribe(data)

    def start_stream(
        self,
        callback: Callable[[str, bool], None],
        chunk_duration: float = 5.0,
    ) -> None:
        """
        Begin capturing audio in a streaming fashion.

        For every *chunk_duration* seconds of recorded audio, the current
        chunk is transcribed and *callback* is invoked with the resulting
        text and a boolean indicating whether any voice was present.
        """
        if self._stream_stop_event.is_set():
            raise RuntimeError("A voice stream is already running.")

        self._transcription_callback = callback
        self._stream_stop_event.clear()

        logger.info("Voice recognition stream started")

        self._stream_thread = threading.Thread(
            target=self._stream_worker,
            args=(chunk_duration,),
            daemon=True,
        )
        self._stream_thread.start()

    def stop_stream(self) -> None:
        """Stop the streaming transcription and wait for the thread to finish."""
        self._stream_stop_event.set()
        if self._stream_thread is not None:
            self._stream_thread.join(timeout=1.0)
        self._stream_thread = None

        logger.info("Voice recognition stream stopped")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _stream_worker(self, chunk_duration: float) -> None:
        """Background loop that records and transcribes chunks."""
        while not self._stream_stop_event.is_set():
            recorded = self.audio.record(chunk_duration)
            if recorded is None:
                continue

            # Determine if the chunk contains audible sound
            rms = float(np.sqrt(np.mean(np.square(recorded))))
            has_voice = rms > VOICE_THRESHOLD

            if not has_voice:
                # No voice heard — inform the UI without transcribing silence.
                if self._transcription_callback:
                    self._transcription_callback("", False)
                continue

            try:
                text = self.transcribe(recorded)
            except RuntimeError as exc:
                self._stream_stop_event.set()
                if self._transcription_callback:
                    self._transcription_callback(f"[Error] {exc}", True)
                break

            if text.strip():
                logger.info("Voice recognized: %s", text)

            if self._transcription_callback:
                self._transcription_callback(text, True)
