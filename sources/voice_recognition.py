from typing import Callable, Optional
import threading
import time
import os

import numpy as np

from .audio_io import AudioIO

# ---------------------------------------------------------------------------
# google‑genai client  (try to import; None if unavailable)
# ---------------------------------------------------------------------------
try:
    from google import genai as _genai
    from google.genai import types as _types
    _genai_available = True
except ImportError:
    _genai_available = False


class VoiceRecognition:
    """Transcribe microphone audio using the google‑genai speech‑to‑text API.

    Uses :class:`~.audio_io.AudioIO` for audio capture and the ``google‑genai``
    library for transcription.

    The constructor accepts an optional API key either via the ``api_key``
    parameter or the ``GENAI_API_KEY`` environment variable.
    """

    def __init__(
        self,
        audio_io: Optional[AudioIO] = None,
        api_key: Optional[str] = None,
        language: str = "en",
    ) -> None:
        self.audio = audio_io if audio_io is not None else AudioIO()
        self.language = language

        # Google client configuration
        self._client: Optional["_genai.Client"] = None
        self._api_key = api_key or os.environ.get("GENAI_API_KEY")

        if not _genai_available:
            print(
                "VoiceRecognition: google‑genai package not installed. "
                "Install it with: pip install google‑genai"
            )

        # Streaming state
        self._stream_thread: Optional[threading.Thread] = None
        self._stream_stop_event = threading.Event()
        self._transcription_callback: Optional[Callable[[str], None]] = None

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def transcribe(self, data: np.ndarray) -> str:
        """Transcribe a NumPy audio array (float32) and return the text.

        Raises a descriptive ``RuntimeError`` on failure.
        """
        if not _genai_available:
            raise RuntimeError(
                "google‑genai library is not installed. "
                "Speech‑to‑text is unavailable."
            )

        if self._client is None:
            self._client = _genai.Client(api_key=self._api_key)

        # Convert the float32 array to the format expected by the API.
        # google‑genai currently expects raw bytes with a known encoding.
        # We re‑interpret the float32 array as 16‑bit PCM, which is the
        # most common format for speech‑to‑text.
        try:
            # Convert to 16‑bit PCM
            pcm_bytes = (data * 32767).clip(-32768, 32767).astype(np.int16).tobytes()
        except Exception as exc:
            raise RuntimeError(f"Failed to convert audio to PCM: {exc}") from exc

        # Use the `audio.transcribe` method of the `google‑genai` model.
        # The exact method signature may differ between releases, so we
        # wrap it in a broad try‑except.
        try:
            response = self._client.audio.transcribe(
                audio=pcm_bytes,
                sample_rate=44100,
                language=self.language,
            )
            # The response is a single string (or a dict with a 'text' key).
            if isinstance(response, str):
                return response
            if hasattr(response, "text"):
                return response.text
            if isinstance(response, dict) and "text" in response:
                return response["text"]
            # Last resort – return the string representation
            return str(response)
        except Exception as exc:
            raise RuntimeError(
                f"Speech‑to‑text request failed: {exc}"
            ) from exc

    def start_stream(
        self,
        callback: Callable[[str], None],
        chunk_duration: float = 5.0,
    ) -> None:
        """
        Begin capturing audio in a streaming fashion.

        For every *chunk_duration* seconds of recorded audio, the current
        chunk is transcribed and *callback* is invoked with the resulting
        text.  Audio is captured using :meth:`~.AudioIO.record`.

        The capturing runs in a daemon thread so it does not prevent the
        application from shutting down.
        """
        if self._stream_stop_event.is_set():
            raise RuntimeError("A voice stream is already running.")

        self._transcription_callback = callback
        self._stream_stop_event.clear()

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

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _stream_worker(self, chunk_duration: float) -> None:
        """Background loop that records and transcribes chunks."""
        while not self._stream_stop_event.is_set():
            # Record a fixed‑duration chunk.
            recorded = self.audio.record(chunk_duration)
            if recorded is None:
                continue

            try:
                text = self.transcribe(recorded)
            except RuntimeError as exc:
                # If the API has a permanent problem, stop the stream.
                self._stream_stop_event.set()
                if self._transcription_callback:
                    self._transcription_callback(f"[Error] {exc}")
                break

            if self._transcription_callback:
                self._transcription_callback(text)
