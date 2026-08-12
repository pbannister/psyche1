# Voice recognition

## Overview

Transcribe spoken words from the microphone into text using a fully local,
offline speech‑to‑text engine.
Support both on‑demand recording and continuous streaming mode.
Provide on‑display of the transcribed text and a clear status indicator
that distinguishes silence, unrecognised speech, and recognised speech.

## Functional requirements

- Use the system microphone as audio input.
- Provide a "Start" / "Stop" button for recording.
- Capture audio at 16k Hz mono, which is the sample rate expected by the
  local speech recognizer.
- Use the `vosk` library for speech‑to‑text conversion.
- Do **not** send audio data over the network, except for the optional
  first‑run download of the model.
- Receive the transcribed text and display it in the main window.
- Detect whether a chunk of audio contains audible speech.
  - Use an RMS threshold to decide if voice is present.
  - Use a fixed threshold constant (e.g., `VOICE_THRESHOLD = 0.02`).
- When no voice is present, show a "No voice" status.
- When voice is present but the model returns no text, show
  "Unrecognized voice".
- When voice is present and the model returns text, show "Recognized voice"
  and display the transcribed text.
- If the `vosk` library or the Vosk model is missing, show a clear error
  message (do not crash).
- All audio I/O operations must run in a background thread so the Qt event
  loop is not blocked.
- Log the start and stop of recording, the start and stop of the voice
  recognition stream, and any recognised voice text.

## API

- Provide a `VoiceRecognition` class in a new file `sources/voice_recognition.py`.
- Constructor accepts an optional `AudioIO` instance, an optional
  `model_path` parameter, and an optional `language` parameter.
- `speech_transcribe(data: np.ndarray) -> str`
  - Accept a float32 NumPy array of audio samples (16k Hz, mono).
  - Return a single string containing the best transcription.
  - Raise a descriptive exception on failure.
- `voice_stream_start(callback: Callable[[str, bool], None]) -> None`
  - Begin capturing audio in a continuous streaming fashion.
  - For each chunk of audio, invoke the callback with the transcribed text
    and a boolean indicating whether any voice was present.
- `voice_stream_stop() -> None`
  - Stop the streaming audio capture and any running transcription task.

## UI integration

- Add a "Voice" group box to the main window.
- Inside it, place a "Record" button that toggles behaviour:
  - On first press the button changes to "Stop" and starts recording.
  - While recording, microphone audio is sent to the local recognizer.
- Below the button, a status label shows one of the following states:
  - "Idle" (grey)
  - "Listening…" (blue)
  - "No voice" (grey‑dark)
  - "Unrecognized voice" (orange)
  - "Recognized voice" (green)
  - "Error" (red)
- Below the status label, a transcription `QLabel` shows the latest
  recognised text or the appropriate status text when no text is available.
- The voice controls operate independently of the video controls.

## Python‑specific requirements

- `vosk>=0.3.45` (offline speech recognition).
- `numpy>=1.24.0` (already required, used for audio data).
- `sounddevice>=0.4.6` (already required; used for audio capture via
  `AudioIO`).

## Model location

- The application looks for the Vosk model in the following order:
  1. The `model_path` argument passed to the constructor.
  2. The `VOSK_MODEL_PATH` environment variable.
  3. The default cache location `~/.cache/psyche1/vosk-model-small-en-us-0.15`.
- If no model is present and the default cache location is used, the
  application attempts to download and unzip a small English Vosk model
  automatically on first run.
- If the model cannot be found or downloaded, a clear error message is
  displayed.
