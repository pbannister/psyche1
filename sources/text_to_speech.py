"""Local text-to-speech synthesis using Piper.

The :class:`TextToSpeech` class synthesizes speech with the Piper neural
text-to-speech engine and plays it back through the system audio output
using `sounddevice`.

Piper runs fully offline once the voice models are downloaded. The first
time a built-in voice is used, its model files are downloaded to
``~/.cache/psyche1/piper/``. No audio data is sent over the network.

The module remains importable even when `piper` or `sounddevice` is
missing; a descriptive error is raised when speech is attempted.
"""

import io
import json
import logging
import threading
import urllib.request
import wave
from pathlib import Path
from typing import Optional

import numpy as np

try:
    import piper

    _PIPER_AVAILABLE = True
except ImportError:
    piper = None
    _PIPER_AVAILABLE = False

try:
    import sounddevice as sd

    _SD_AVAILABLE = True
except (ImportError, OSError):
    sd = None
    _SD_AVAILABLE = False

logger = logging.getLogger(__name__)

VOICE_CACHE_DIR = Path.home() / ".cache" / "psyche1" / "piper"

# Mapping of built-in voice identifiers to display names and download URLs.
# The URLs point to the HuggingFace repository for Piper voices.
BUILTIN_VOICES = {
    "en_US-lessac-medium": {
        "name": "English (US) - Lessac - Medium",
        "onnx_url": (
            "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
            "en/en_US/lessac/medium/en_US-lessac-medium.onnx?download=true"
        ),
        "json_url": (
            "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
            "en/en_US/lessac/medium/en_US-lessac-medium.onnx.json?download=true"
        ),
    },
    "en_GB-alan-medium": {
        "name": "English (UK) - Alan - Medium",
        "onnx_url": (
            "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
            "en/en_GB/alan/medium/en_GB-alan-medium.onnx?download=true"
        ),
        "json_url": (
            "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
            "en/en_GB/alan/medium/en_GB-alan-medium.onnx.json?download=true"
        ),
    },
    "en_US-amy-medium": {
        "name": "English (US) - Amy - Medium",
        "onnx_url": (
            "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
            "en/en_US/amy/medium/en_US-amy-medium.onnx?download=true"
        ),
        "json_url": (
            "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
            "en/en_US/amy/medium/en_US-amy-medium.onnx.json?download=true"
        ),
    },
    "en_US-ryan-high": {
        "name": "English (US) - Ryan - High",
        "onnx_url": (
            "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
            "en/en_US/ryan/high/en_US-ryan-high.onnx?download=true"
        ),
        "json_url": (
            "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
            "en/en_US/ryan/high/en_US-ryan-high.onnx.json?download=true"
        ),
    },
}


class TextToSpeech:
    """Synthesize speech with Piper and play it through the speakers.

    The voice is chosen by a voice identifier (e.g., ``en_US-lessac-medium``).
    Built-in voices are automatically downloaded on first use. Custom voices
    may be added by placing ``<voice_id>.onnx`` and ``<voice_id>.onnx.json``
    into :data:`VOICE_CACHE_DIR`.
    """

    def __init__(self, voice_id: Optional[str] = None) -> None:
        self.voice_id = voice_id if voice_id else "en_US-lessac-medium"
        self._voice = None
        self._voice_list = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def voices_list_get(self) -> list[dict]:
        """Return all available voices as a list of ``{'id', 'name'}``."""
        if self._voice_list is None:
            voices = {vid: info["name"] for vid, info in BUILTIN_VOICES.items()}

            # Scan user-supplied voices already present in the cache.
            if VOICE_CACHE_DIR.is_dir():
                for onnx_path in VOICE_CACHE_DIR.glob("*.onnx"):
                    vid = onnx_path.stem  # remove the .onnx extension
                    if vid in voices:
                        continue
                    json_path = VOICE_CACHE_DIR / f"{vid}.onnx.json"
                    display_name = vid
                    if json_path.is_file():
                        try:
                            with open(json_path, "r", encoding="utf-8") as f:
                                meta = json.load(f)
                            if isinstance(meta, dict) and meta.get("name"):
                                display_name = meta["name"]
                        except (json.JSONDecodeError, OSError):
                            pass
                    voices[vid] = display_name

            self._voice_list = [
                {"id": vid, "name": name}
                for vid, name in sorted(voices.items())
            ]
        return list(self._voice_list)

    def voice_set(self, voice_id: str) -> None:
        """Set the current voice by identifier.

        Args:
            voice_id: Voice identifier as returned by :meth:`voices_list_get`.

        Raises:
            ValueError: If ``voice_id`` is not found in the available voices.
        """
        voices = self.voices_list_get()
        if not any(v["id"] == voice_id for v in voices):
            raise ValueError(f"Voice '{voice_id}' not found.")
        self.voice_id = voice_id
        # Force the voice to be re-loaded on next speak().
        self._voice = None

    def speech_speak(self, text: str, block: bool = False) -> None:
        """Speak the given text.

        Args:
            text: Plain text to be spoken.
            block: If ``True``, wait until speech finishes before returning.
                If ``False``, start speech in a background thread and return
                immediately.
        """
        self._ensure_available()
        if block:
            self._speak_sync(text, block=True)
        else:
            threading.Thread(
                target=self._speak_sync,
                args=(text, False),
                daemon=True,
            ).start()

    def speech_stop(self) -> None:
        """Stop any currently playing audio."""
        if _SD_AVAILABLE:
            try:
                sd.stop()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _ensure_available(self) -> None:
        if not _PIPER_AVAILABLE:
            raise RuntimeError(
                "Piper is not installed. Install it with: pip install piper-tts"
            )
        if not _SD_AVAILABLE:
            raise RuntimeError(
                "sounddevice (PortAudio) is not available. "
                "Install it with: sudo apt install libportaudio2"
            )

    def _get_voice(self):
        if self._voice is None:
            model_path = self._ensure_voice_files(self.voice_id)
            config_path = VOICE_CACHE_DIR / f"{self.voice_id}.onnx.json"
            self._voice = piper.PiperVoice.load(model_path, config_path=config_path)
        return self._voice

    def _ensure_voice_files(self, voice_id: str) -> Path:
        """Return the path to the ONNX model for ``voice_id``.

        If the voice is a built-in, download it on first use. Otherwise the
        files must already be present in the cache directory.
        """
        VOICE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        model_path = VOICE_CACHE_DIR / f"{voice_id}.onnx"
        json_path = VOICE_CACHE_DIR / f"{voice_id}.onnx.json"

        if voice_id in BUILTIN_VOICES:
            urls = BUILTIN_VOICES[voice_id]
            if not model_path.is_file() or not json_path.is_file():
                print(f"TextToSpeech: first-run – downloading voice {voice_id} …")
                try:
                    urllib.request.urlretrieve(urls["onnx_url"], str(model_path))
                    urllib.request.urlretrieve(urls["json_url"], str(json_path))
                except Exception as exc:
                    # Clean up partial downloads so a later retry can proceed.
                    if model_path.exists():
                        model_path.unlink()
                    if json_path.exists():
                        json_path.unlink()
                    raise RuntimeError(
                        f"Could not download Piper voice '{voice_id}'.\n"
                        f"Check the URLs in {urls} or download the files "
                        f"manually to {VOICE_CACHE_DIR}."
                    ) from exc
        else:
            if not model_path.is_file() or not json_path.is_file():
                raise RuntimeError(
                    f"Voice files for '{voice_id}' are not present.\n"
                    f"Expected to find:\n  {model_path}\n  {json_path}\n"
                    f"Place the two files in {VOICE_CACHE_DIR} or use a "
                    f"built-in voice from {', '.join(BUILTIN_VOICES.keys())}."
                )

        return model_path

    def _speak_sync(self, text: str, block: bool) -> None:
        """Synthesize ``text`` and play it back (optionally blocking)."""
        self._ensure_available()
        voice = self._get_voice()
        sample_rate = getattr(getattr(voice, "config", None), "sample_rate", 22050)

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            voice.synthesize(text, wav_file)

        buffer.seek(0)
        try:
            with wave.open(buffer, "rb") as wav:
                nchannels = wav.getnchannels()
                sampwidth = wav.getsampwidth()
                framerate = wav.getframerate()
                nframes = wav.getnframes()
                raw = wav.readframes(nframes)
        except Exception as exc:
            raise RuntimeError(f"Failed to read Piper output: {exc}") from exc

        if sampwidth == 2:
            dtype = np.int16
        elif sampwidth == 4:
            dtype = np.int32
        else:
            dtype = np.float32

        audio = np.frombuffer(raw, dtype=dtype)
        if nchannels > 1:
            audio = audio.reshape(-1, nchannels)

        # Always block in this thread so the playback finishes before the
        # thread exits.  The thread itself is a background daemon thread,
        # but calling sd.play() with blocking=True keeps it alive until
        # the audio finishes, ensuring that the sound is actually heard.
        sd.play(audio, samplerate=framerate, blocking=True)
