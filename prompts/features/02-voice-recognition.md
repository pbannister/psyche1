# Voice recognition

## Overview

Transcribe spoken words from the microphone into text.  
Support both on-demand recording and continuous streaming mode.  
Provide on-display of the transcribed text.

## Functional requirements

- Use the system microphone as audio input.
- Provide a "Start" / "Stop" button for recording.
- When recording is activated, capture audio through the `AudioIO` class
  (using `record` for a fixed duration, or a streaming callback for live
  capture).
- Send captured audio data to a speech‑to‑text service.
- Use the `google-genai` library (already a dependency) to perform the
  speech‑to‑text conversion.
- Receive the transcribed text and display it in the main window.
- When the speech‑to‑text service is unavailable or returns an error,
  show a clear error message (do not crash).
- All network and audio I/O operations must run in a background thread
  or asynchronous to not block the Qt event loop.

## API

- Provide a `VoiceRecognition` class in a new file `sources/voice_recognition.py`.
- Constructor accepts an optional `AudioIO` instance (defaulting to a new
  one) and any speech‑to‑text configuration (provider credentials, language).
- `transcribe(data: np.ndarray) -> str`
  - Accept a float32 NumPy array of audio samples (channels, sample rate
    as used by `AudioIO`).
  - Return a single string containing the best transcription.
  - Raise a descriptive exception on failure.
- `start_stream(callback: Callable[[str], None]) -> None`
  - Begin capturing audio in a continuous streaming fashion.
  - For each utterance (for example, after a period of silence), invoke the
    callback with the transcribed text.
- `stop_stream() -> None`
  - Stop the streaming audio capture and any running transcription task.

## UI integration

- Add a "Voice" group box to the main window (e.g., below or adjacent to the
  audio group).
- Inside it, place a "Record" button that toggles behaviour:
  - On first press the button changes to "Stop" and starts recording.
  - While recording, microphone audio is sent to the speech‑to‑text service.
- Below the button, a `QLabel` (or read‑only `QTextEdit`) shows the latest
  transcription.
- The voice controls operate independently of the video controls.

## Python-specific requirements

- `google-genai>=0.1.0` (already in `requirements.txt`, provides the
  speech‑to‑text API).
- `numpy>=1.24.0` (already required, used for audio data).
- `sounddevice>=0.4.6` (already required; used for audio capture via `AudioIO`).
