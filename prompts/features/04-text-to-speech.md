# Feature: Text to Speech

## Purpose

Provide local text-to-speech synthesis with the Piper neural engine.
The module accepts plain text, synthesizes audio with a local voice model, and
plays it through the system audio output.
No text or audio leaves the machine after installation.

## Requirements

- `TEXT-TO-SPEECH-R001` — Accept a text string and speak it through the system audio output.
- `TEXT-TO-SPEECH-R002` — Use Piper as the local neural text-to-speech engine and send no text or audio data over the network.
- `TEXT-TO-SPEECH-R003` — Provide `TextToSpeech` in `sources/text_to_speech.py` with an optional `voice_id` constructor parameter and a `voice_id` attribute reflecting the current voice.
- `TEXT-TO-SPEECH-R004` — `voices_list_get()` returns the available voices as a list of dictionaries with `id` and `name` keys.
- `TEXT-TO-SPEECH-R005` — `voice_set(voice_id)` selects a voice and raises `ValueError` when the identifier is unknown.
- `TEXT-TO-SPEECH-R006` — `speech_speak(text, block=False)` speaks the text; when `block` is true it waits for completion, otherwise it returns immediately.
- `TEXT-TO-SPEECH-R007` — `speech_stop()` stops any speech currently in progress.
- `TEXT-TO-SPEECH-R008` — Run synthesis and playback in a background thread so the Qt event loop is not blocked.
- `TEXT-TO-SPEECH-R009` — Store downloaded voice models in `~/.cache/psyche1/piper/` and download built-in voices automatically on first use.
- `TEXT-TO-SPEECH-R010` — Discover custom voices from `<voice_id>.onnx` and `<voice_id>.onnx.json` pairs in the cache directory, using the file name without the `.onnx` extension as the identifier.
- `TEXT-TO-SPEECH-R011` — Remain importable when `piper` or `sounddevice` is missing; raise a descriptive `RuntimeError` when speech is attempted.
- `TEXT-TO-SPEECH-R012` — Expose the built-in identifiers `en_US-lessac-medium`, `en_GB-alan-medium`, `en_US-amy-medium`, and `en_US-ryan-high`.

## Behavior

- Listing voices returns built-in and custom voices; the built-in set is available before any speech is attempted.
- Speaking with `block=False` returns while audio continues in the background; `speech_stop()` ends it.
- A missing engine disables speech and reports the reason.

## Dependencies

- None.
