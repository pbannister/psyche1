from pathlib import Path
from typing import Callable, Optional
import json
import os
import threading
import urllib.request
import zipfile

import numpy as np

from .audio_io import AudioIO

try:
    from vosk import Model, KaldiRecognizer
    _vosk_available = True
except ImportError:
    Model = None
    KaldiRecognizer = None
    _vosk_available = False


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

        # Locate the Vosk model
        self.model_path = model_path or os.environ.get("VOSK_MODEL_PATH")
        self._auto_download = False
        if self.model_path is None:
            self.model_path = str(
                Path.home() / ".cache" / "psyche1" / "vosk-model-small-en-us-0.15"
            )
            self._auto_download = True

        self._model = None

        # Streaming state
        self._stream_thread: Optional[threading.Thread] = None
        self._stream_stop_event = threading.Event()
        self._transcription_callback: Optional[Callable[[str], None]] = None

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def transcribe(self, data: np.ndarray) -> str:
        """Transcribe a 16kHz float32 NumPy array and return the text.

        Raises a descriptive ``RuntimeError`` if Vosk or the model cannot
        be loaded.
        """
        if not _vosk_available:
            raise RuntimeError(
                "Vosk is not installed. Install it with: pip install vosk"
            )

        if self._model is None:
            self._ensure_model()
            self._model = Model(self.model_path)

        # Convert float32 audio to 16-bit PCM bytes expected by Vosk
        try:
            pcm_bytes = (
                (data * 32767).clip(-32768, 32767).astype(np.int16).tobytes()
            )
        except Exception as exc:
            raise RuntimeError(f"Failed to convert audio to PCM: {exc}") from exc

        try:
            rec = KaldiRecognizer(self._model, self.audio.sample_rate)
            rec.AcceptWaveform(pcm_bytes)
            result = json.loads(rec.FinalResult())
            return result.get("text", "").strip()
        except Exception as exc:
            raise RuntimeError(f"Vosk transcription failed: {exc}") from exc

    def start_stream(
        self,
        callback: Callable[[str], None],
        chunk_duration: float = 5.0,
    ) -> None:
        """
        Begin capturing audio in a streaming fashion.

        For every *chunk_duration* seconds of recorded audio, the current
        chunk is transcribed and *callback* is invoked with the resulting
        text.
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
    def _ensure_model(self) -> None:
        """Make sure the Vosk model directory exists.

        If the model is a default cache path and the directory is missing,
        download and unzip the small English model automatically.
        Otherwise raise a clear error.
        """
        if os.path.isdir(self.model_path):
            return

        if not self._auto_download:
            raise RuntimeError(
                "Vosk model not found. Set VOSK_MODEL_PATH to a valid "
                "directory containing a Vosk model."
            )

        cache_root = Path.home() / ".cache" / "psyche1"
        cache_root.mkdir(parents=True, exist_ok=True)

        zip_path = cache_root / "vosk-model-small-en-us-0.15.zip"
        url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"

        print("VoiceRecognition: first‑run – downloading Vosk model …")
        try:
            urllib.request.urlretrieve(url, str(zip_path))
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(cache_root)
        except Exception as exc:
            raise RuntimeError(
                "Could not download the Vosk model automatically.\n"
                f"Try downloading it manually from {url}\n"
                "and extracting it to ~/.cache/psyche1/"
            ) from exc
        finally:
            if zip_path.exists():
                zip_path.unlink()

        if not os.path.isdir(self.model_path):
            raise RuntimeError(
                "Vosk model downloaded but the expected directory was not "
                f"created at {self.model_path}. Please check the download."
            )

    def _stream_worker(self, chunk_duration: float) -> None:
        """Background loop that records and transcribes chunks."""
        while not self._stream_stop_event.is_set():
            recorded = self.audio.record(chunk_duration)
            if recorded is None:
                continue

            try:
                text = self.transcribe(recorded)
            except RuntimeError as exc:
                self._stream_stop_event.set()
                if self._transcription_callback:
                    self._transcription_callback(f"[Error] {exc}")
                break

            if self._transcription_callback:
                self._transcription_callback(text)
