# Feature: Audio I/O

## Purpose

Provide asynchronous duplex audio for the application: microphone capture and
speaker playback, with a microphone-to-speaker loopback by default.
Recording and playback are exposed for the other audio features.

## Requirements

- `AUDIO-IO-R001` — Use `sounddevice` for asynchronous duplex audio with microphone input and speaker output.
- `AUDIO-IO-R002` — Provide `AudioIO` in `sources/audio_io.py` with `sample_rate` and `channels` constructor parameters.
- `AUDIO-IO-R003` — `audio_stream_start(input_callback=None, output_callback=None)` begins asynchronous streaming; with no callback it loops the microphone to the speaker.
- `AUDIO-IO-R004` — `audio_stream_stop()` stops and closes the stream.
- `AUDIO-IO-R005` — `audio_record(duration)` records a fixed-duration clip and returns it as a float32 NumPy array.
- `AUDIO-IO-R006` — `audio_play(data)` plays a NumPy audio array asynchronously.
- `AUDIO-IO-R007` — Run the stream in a background thread so the main application is not blocked.
- `AUDIO-IO-R008` — Protect stream state with a `threading.Lock` and refuse a second start while the stream is running.
- `AUDIO-IO-R009` — Use a fixed block size of 1024 frames to reduce input underflow warnings, and print only genuine overflow errors while ignoring benign underflow warnings.
- `AUDIO-IO-R010` — Remain importable when the PortAudio library is missing; raise a `RuntimeError` with installation instructions when an audio method is used.

## Behavior

- Starting the stream with no callbacks loops microphone audio to the speaker.
- A second start while running raises an error rather than opening a second stream.
- Recording returns a float32 array of `int(duration * sample_rate)` frames.

## Dependencies

- None.
