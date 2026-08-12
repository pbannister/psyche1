# Speech to text

## Overview

Transcribe spoken words from a raw audio array into text using a fully local,
offline speech‑to‑text engine.
This module does **not** capture microphone audio itself –
it accepts a pre‑recorded audio buffer and returns the recognised text.
Audio capture and voice‑activity detection are handled by the
voice‑recognition module (see ``02-voice-recognition.md``).

The engine relies on the ``vosk`` library.
It supports both on‑demand transcription of a single audio chunk and
re‑use of the loaded language model across multiple calls.

## Functional requirements

- Accept a 16 kHz mono float32 NumPy array.
- Convert the float32 array to 16‑bit PCM bytes before passing it to Vosk.
- Return the recognised text as a single UTF‑8 string.
- Raise a descriptive exception if Vosk is not installed.
- Raise a descriptive exception if the Vosk model cannot be loaded.
- The model is loaded once and kept in memory for all subsequent calls.
- The model location follows the same search order as for voice recognition:
  1. The ``model_path`` argument passed to the constructor.
  2. The ``VOSK_MODEL_PATH`` environment variable.
  3. The default cache ``~/.cache/psyche1/vosk-model-small-en-us-0.15``.
- If the default cache location is used and the directory does not exist,
  the module downloads and extracts the small English model automatically on
  first use.
- If the model cannot be found or downloaded, a clear error is raised.
- The module may not send any audio data over the network (only an optional
  one‑time model download occurs).

## API

- Provide a class ``SpeechToText`` in a new file ``sources/speech_to_text.py``.
- Constructor accepts an optional ``model_path`` parameter and an optional
  ``language`` parameter.
- ``speech_transcribe(data: np.ndarray) -> str``
  - Accept a 16 kHz mono float32 NumPy array.
  - Return the best transcription string.
  - Raise a ``RuntimeError`` with a descriptive message on failure.
- The class may also expose a ``model_get()`` method that returns the
  loaded Vosk model, loading it on first access.

## Integration

- The ``SpeechToText`` class is the core transcription engine used by
  ``VoiceRecognition``.
- ``VoiceRecognition`` wraps ``SpeechToText`` with audio capture,
  voice‑activity detection, and streaming coordination.
- Other modules ``future modules`` that only need transcribe an
  already‑captured audio chunk may depend directly on ``SpeechToText``.

## Python-specific requirements

- ``vosk>=0.3.45`` (speech‑to‑text engine).
- ``numpy>=1.24.0`` (already required, used for audio data conversion).
- ``requests>=2.28.0`` ``urqlib.request`` (used only for model download).
- The module must be importable even when ``vosk`` is missing;
  imports provide a descriptive error when transcription is attempted.
