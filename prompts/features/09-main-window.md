# Feature: Main Window

## Purpose

Provide the PyQt6 desktop shell that presents video and audio controls in a
tabbed window and coordinates the capture, recognition, and speech features.
Running the application launches this window.

## Requirements

- `MAIN-WINDOW-R001` — Provide a `MainWindow` in `sources/main_window.py` built with PyQt6, titled `Psyche1` and sized about 800 by 600 pixels.
- `MAIN-WINDOW-R002` — Separate the interface into a Video tab and an Audio tab.
- `MAIN-WINDOW-R003` — The Video tab shows the live webcam feed with Start Camera and Stop Camera buttons.
- `MAIN-WINDOW-R004` — The Audio tab holds the audio loopback buttons, the voice recognition controls, and the text-to-speech controls.
- `MAIN-WINDOW-R005` — Overlay face bounding boxes and recognized names on the displayed frame.
- `MAIN-WINDOW-R006` — Show voice status as one of idle, listening, no voice, unrecognized voice, recognized voice, or error, and display the latest transcription.
- `MAIN-WINDOW-R007` — Provide a voice combo box, a text field, and Speak and Stop buttons for text-to-speech.
- `MAIN-WINDOW-R008` — Disable the speech controls and show the reason when the text-to-speech engine is unavailable.
- `MAIN-WINDOW-R009` — Schedule background-thread callbacks onto the GUI thread with `QTimer.singleShot`.
- `MAIN-WINDOW-R010` — Release the camera, stop the audio stream, stop voice streaming, and stop speech when the window closes.
- `MAIN-WINDOW-R011` — Provide an entry point in `sources/main.py` so `python -m sources.main` launches the application, accepting an optional `--known-faces-dir` argument.
- `MAIN-WINDOW-R012` — Show a critical message box, rather than crashing, when the camera or audio device cannot be opened.

## Behavior

- Launching the module opens the window on the Video tab.
- Closing the window releases all audio and video resources.
- When the camera cannot be opened, a critical dialog appears and the application stays running.

## Dependencies

- `04-text-to-speech.md`
- `05-facial-recognition.md`
- `06-voice-recognition.md`
- `07-audio-io.md`
- `08-video-capture.md`
