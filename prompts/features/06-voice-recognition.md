# Feature: Voice Recognition

## Purpose

Transcribe microphone speech into text with a fully local, offline engine and
report whether voice is present.
The feature wraps the Speech to Text engine with audio capture, voice-activity
detection, and streaming coordination.

## Requirements

- `VOICE-RECOGNITION-R001` — Capture microphone audio at 16 kHz mono and transcribe it with the local Speech to Text engine.
- `VOICE-RECOGNITION-R002` — Provide `VoiceRecognition` in `sources/voice_recognition.py` with optional `AudioIO`, `model_path`, and `language` constructor parameters.
- `VOICE-RECOGNITION-R003` — `speech_transcribe(data)` accepts a float32 NumPy array and returns the best transcription as a string, raising a descriptive exception on failure.
- `VOICE-RECOGNITION-R004` — `voice_stream_start(callback)` captures audio continuously and invokes `callback(text, has_voice)` for each chunk.
- `VOICE-RECOGNITION-R005` — `voice_stream_stop()` stops streaming capture and any running transcription.
- `VOICE-RECOGNITION-R006` — Decide voice presence from an RMS threshold using a fixed constant such as `VOICE_THRESHOLD = 0.02`.
- `VOICE-RECOGNITION-R007` — Report three distinct outcomes: no voice, voice without a transcription, and voice with a transcription.
- `VOICE-RECOGNITION-R008` — Run all audio I/O in a background thread so the Qt event loop is not blocked.
- `VOICE-RECOGNITION-R009` — Show a clear error instead of crashing when `vosk`, the model, or the audio device is unavailable.
- `VOICE-RECOGNITION-R010` — Resolve the model in the same order as Speech to Text: constructor argument, `VOSK_MODEL_PATH`, then the default cache.
- `VOICE-RECOGNITION-R011` — Send no audio data over the network except the optional one-time model download.
- `VOICE-RECOGNITION-R012` — Log the start and stop of recording, the start and stop of the recognition stream, and any recognized text.

## Behavior

- Pressing Record begins streaming; pressing Stop ends it.
- Each chunk updates the status to one of no voice, unrecognized voice, or recognized voice.
- Recognized text is displayed in the window.

## Dependencies

- `03-speech-to-text.md`
- `07-audio-io.md`
