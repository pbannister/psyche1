# Text to speech

## Overview

Provide text-to-speech synthesis for the Psyche1 application using the Piper neural text-to-speech engine.
The module accepts a plain text string, synthesizes audio using a local voice model, and plays it through the system audio output.
No audio data is sent over the network after installation.

## Functional requirements

- Accept a text string and speak it aloud through the system audio output.
- Use Piper as the local TTS engine, which produces significantly higher-quality speech than classic formant synthesizers.
- Do not send text or audio data over the network.
- Allow the user to choose a voice from the available voices.
- Provide a way to list all available voices with their identifiers and display names.
- Provide a way to set the current voice by identifier.
- Provide a way to stop speech that is currently being spoken.
- If the Piper engine or the underlying PortAudio library is missing, the module must still be importable and raise a descriptive error when speech is attempted.
- All speech operations must run in a background thread so the Qt event loop is not blocked.

## Voices

- Built-in voices are downloaded automatically on first use.
- Voice models are stored in `~/.cache/psyche1/piper/`.
- Built-in identifiers:

  | Voice ID               | Description                  |
  |------------------------|------------------------------|
  | `en_US-lessac-medium`  | English (US) – Lessac – Medium |
  | `en_GB-alan-medium`    | English (UK) – Alan – Medium   |
  | `en_US-amy-medium`     | English (US) – Amy – Medium    |
  | `en_US-ryan-high`      | English (US) – Ryan – High     |

- Users can add custom voices by placing two files in the cache directory:
  - `<voice_id>.onnx`
  - `<voice_id>.onnx.json`

The identifier is the file name without the `.onnx` extension.

## API

- Provide a class `TextToSpeech` in a new file `sources/text_to_speech.py`.
- Constructor accepts an optional `voice_id` parameter.
- `list_voices() -> list[dict]`
  - Return a list of dictionaries with keys `id` and `name`.
- `set_voice(voice_id: str) -> None`
  - Set the current voice to the given identifier.
  - Raise a `ValueError` if the identifier is not found.
- `speak(text: str, block: bool = False) -> None`
  - Speak the given text.
  - If `block` is `True`, wait until speech finishes before returning.
  - If `block` is `False`, start speech in a background thread and return immediately.
- `stop() -> None`
  - Stop any currently running speech.
- The class may expose a `voice_id` attribute that reflects the current voice.

## UI integration

- Add a "Speech" group box to the main window.
- Inside it, place:
  - A `QComboBox` listing available voices.
  - A `QLineEdit` for entering text.
  - A "Speak" button that triggers `speak(text)`.
  - A "Stop" button that triggers `stop()`.
- Populate the voice combo box when the window is created.
- If the TTS engine is unavailable, disable the controls and show a clear error message.

## Python-specific requirements

- `piper-tts>=1.2.0` (local neural text-to-speech engine).
- `sounddevice>=0.4.6` (audio output; already a project dependency).
- The module must be importable even when `piper` or `sounddevice` is missing; imports provide a descriptive error when speech is attempted.
- Use `threading` for background speech synthesis and playback.
