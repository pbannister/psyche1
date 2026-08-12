# Voice recognition

## Overview

Transcribe spoken words from the microphone into text using a fully local,
offline speech‑to‑text engine.
Support both on‑demand recording and continuous streaming mode.
Provide on‑display of the transcribed text.

## Functional requirements

- Use the system microphone as audio input.
- Provide a "Start" / "Stop" button for recording.
- Capture audio at 16k Hz mono, which is the sample rate expected by the
  local speech recognizer.
- Use the `vosk` library for speech‑to‑text conversion.
- Do **not** send audio data over the network.
- Receive the transcribed text and display it in the main window.
- If the `vosk` library or the Vosk model is missing, show a clear error
  message (do not crash).
- All audio I/O operations must run in a background thread so the Qt event
  loop is not blocked.

## API

- Provide a `VoiceRecognition` class in a new file `sources/voice_recognition.py`.
- Constructor accepts an optional `AudioIO` instance and a `model_path`
  parameter.
- `transcribe(data: np.ndarray) -> str`
  - Accept a float32 NumPy array of audio samples (16k Hz, mono).
  - Return a single string containing the best transcription.
  - Raise a descriptive exception on failure.
- `start_stream(callback: Callable[[str], None]) -> None`
  - Begin capturing audio in a continuous streaming fashion.
  - For each chunk of audio, invoke the callback with the transcribed text.
- `stop_stream() -> None`
  - Stop the streaming audio capture and any running transcription task.

## UI integration

- Add a "Voice" group box to the main window.
- Inside it, place a "Record" button that toggles behaviour:
  - On first press the button changes to "Stop" and starts recording.
  - While recording, microphone audio is sent to the local recognizer.
- Below the button, a `QLabel` shows the latest transcription.
- The voice controls operate independently of the video controls.

## Python‑specific requirements

- `vosk>=0.3.45` (offline speech recognition).
- `numpy>=1.24.0` (already required, used for audio data).
- `sounddevice>=0.4.6` (already required; used for audio capture via `AudioIO`).

## Model location

- The application looks for the Vosk model in the following order:
  1. The `model_path` argument passed to the constructor.
  2. The `VOSK_MODEL_PATH` environment variable.
  3. The default cache location `~/.cache/psyche1/vosk-model-small-en-us-0.15`.
- If no model is present, a clear error message is shown.
