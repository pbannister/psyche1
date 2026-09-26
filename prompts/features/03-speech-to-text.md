# Feature: Speech to Text

## Purpose

Transcribe a pre-recorded audio buffer into text with a fully local, offline
speech recognition engine.

The feature does not capture microphone audio: it accepts a 16 kHz mono
float32 NumPy array and returns the recognized text.
Audio capture and voice-activity detection belong to the Voice Recognition
feature (`06-voice-recognition.md`).

## Requirements

- `SPEECH-TO-TEXT-R001` — Accept a 16 kHz mono float32 NumPy array and return the recognized text as a single UTF-8 string.
- `SPEECH-TO-TEXT-R002` — Convert the float32 samples to 16-bit PCM bytes before passing them to the Vosk recognizer.
- `SPEECH-TO-TEXT-R003` — Use the `vosk` library as the recognition engine and keep the loaded model in memory for all subsequent calls.
- `SPEECH-TO-TEXT-R004` — Resolve the model in this order: the `model_path` constructor argument, the `VOSK_MODEL_PATH` environment variable, then `~/.cache/psyche1/vosk-model-small-en-us-0.15`.
- `SPEECH-TO-TEXT-R005` — When the default cache location is used and the directory is absent, download and extract the small English model automatically on first use.
- `SPEECH-TO-TEXT-R006` — Raise a `RuntimeError` with a descriptive message when Vosk is not installed, the model cannot be loaded, or the model cannot be downloaded.
- `SPEECH-TO-TEXT-R007` — Remain importable when `vosk` is missing; the error is raised only when transcription is attempted.
- `SPEECH-TO-TEXT-R008` — Send no audio data over the network; only the optional one-time model download may use the network.
- `SPEECH-TO-TEXT-R009` — Provide a `SpeechToText` class in `sources/speech_to_text.py` with a `speech_transcribe(data)` method and a `model_get()` method that loads the model on first access.
- `SPEECH-TO-TEXT-R010` — Accept optional `model_path` and `language` constructor parameters.

## Behavior

- A call to `speech_transcribe` returns the best transcription for the supplied buffer.
- Repeated calls reuse the loaded model and do not reload it.
- A missing engine or model produces a `RuntimeError` whose message names the missing piece.

## Dependencies

- None.
