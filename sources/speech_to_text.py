"""Offline speech-to-text transcription using Vosk.

The :class:`SpeechToText` class accepts a 16 kHz mono float32 NumPy array
and returns the recognised text. It does not access the microphone itself;
audio capture is handled by the :class:`~.voice_recognition.VoiceRecognition`
module.

Vosk is imported lazily so that the rest of the application can start even
when the library is missing. Attempting to transcribe without Vosk raises a
clear ``RuntimeError``.
"""

import json
import logging
import os
import urllib.request
import zipfile
from pathlib import Path

import numpy as np

try:
    from vosk import Model, KaldiRecognizer

    _VOSK_AVAILABLE = True
except (ImportError, OSError):  # allow startup when vosk is not installed
    Model = None
    KaldiRecognizer = None
    _VOSK_AVAILABLE = False

logger = logging.getLogger(__name__)


class SpeechToText:
    """Transcribe a 16 kHz float32 mono audio array into text.

    The model is loaded on first use and kept in memory for later calls.
    The model location is looked up in the following order:

    1. The ``model_path`` argument passed to the constructor.
    2. The ``VOSK_MODEL_PATH`` environment variable.
    3. The default cache ``~/.cache/psyche1/vosk-model-small-en-us-0.15``.

    If the default location is used and the directory is missing, the small
    English model is automatically downloaded and extracted on first usage.
    """

    def __init__(self, model_path: str | None = None, language: str = "en") -> None:
        self.language = language
        self.model_path = model_path or os.environ.get("VOSK_MODEL_PATH")
        self._auto_download = False

        if self.model_path is None:
            self.model_path = str(
                Path.home() / ".cache" / "psyche1" / "vosk-model-small-en-us-0.15"
            )
            self._auto_download = True

        self._model = None

    @property
    def model(self) -> "Model":
        """Return the loaded Vosk model, loading it on first access."""
        if self._model is None:
            self._ensure_model()
            if not _VOSK_AVAILABLE:
                raise RuntimeError(
                    "Vosk is not installed. Install it with: pip install vosk"
                )
            try:
                self._model = Model(self.model_path)
            except Exception as exc:
                raise RuntimeError(
                    f"Failed to load Vosk model from {self.model_path}: {exc}"
                ) from exc
        return self._model

    def _ensure_model(self) -> None:
        """Make sure the model directory exists.

        If the model is the default cache path and the directory is missing,
        download and unzip the small English model automatically.
        Otherwise raise a descriptive error.
        """
        if os.path.isdir(self.model_path):
            return

        if not self._auto_download:
            raise RuntimeError(
                "Vosk model not found. Set VOSK_MODEL_PATH to a valid directory "
                "containing a Vosk model."
            )

        cache_root = Path.home() / ".cache" / "psyche1"
        cache_root.mkdir(parents=True, exist_ok=True)

        zip_path = cache_root / "vosk-model-small-en-us-0.15.zip"
        url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"

        print("SpeechToText: first-run – downloading Vosk model …")
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
                "Vosk model downloaded but the expected directory was not created "
                f"at {self.model_path}. Please check the download."
            )

    def transcribe(self, data: np.ndarray) -> str:
        """Transcribe a 16 kHz mono float32 array and return the recognised text.

        Args:
            data: Float32 audio samples at 16 kHz, shape ``(N,)``.

        Returns:
            The best transcription as a UTF‑8 string.

        Raises:
            RuntimeError: If Vosk is missing, the model cannot be loaded, or
                the audio cannot be converted/processed.
        """
        if not _VOSK_AVAILABLE:
            raise RuntimeError(
                "Vosk is not installed. Install it with: pip install vosk"
            )

        try:
            pcm_bytes = (data * 32767).clip(-32768, 32767).astype(np.int16).tobytes()
        except Exception as exc:
            raise RuntimeError(f"Failed to convert audio to PCM: {exc}") from exc

        try:
            rec = KaldiRecognizer(self.model, 16000)
            rec.AcceptWaveform(pcm_bytes)
            result = json.loads(rec.FinalResult())
            return result.get("text", "").strip()
        except Exception as exc:
            raise RuntimeError(f"Vosk transcription failed: {exc}") from exc
