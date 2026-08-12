# Psyche1 Project Requirements

This document captures the project requirements gathered so far.

## Overview

Psyche1 is a Linux desktop application for multimodal capture and presentation. 
It focuses on:

- Audio capture from the microphone
* Playback to the speakers
- Video capture from a webcam
- A main window that provides:
   * controls to start and stop audio capture
   * controls to start and stop video capture
   * displays the live webcam feed.

## Functional Requirements

1. **Audio I/O**
   - Use `sounddevice` for asynchronous duplex audio (input and output).
   - Provide a default loopback mode (microphone → speaker).
   - Use a threaded stream so the main application is not blocked.
   - Expose at least the following operations:
     - `start()` — begin asynchronous duplex streaming.
     - `stop()` — stop and close the audio stream.
     - `record(duration)` — record a fixed‑duration clip and return it as a NumPy array.
     - `play(data)` — play a NumPy audio array asynchronously.

2. **Video Capture**
   - Use OpenCV (`cv2.VideoCapture`) to read frames from a webcam.
   - Run capture in a background thread to avoid blocking the UI.
   - Protect the current frame with a lock.
   - Expose at least the following operations:
     - `start()` — begin the background capture thread.
     - `get_frame()` — return a copy of the latest BGR frame (or `None` before any frame is available).
     - `release()` — stop the thread and release the camera.

3. **Graphical User Interface**
   - Provide a main window built with PyQt6.
   - The window should contain:
     - A video panel that displays the live webcam feed.
     - Buttons to start and stop the camera.
     - Buttons to start and stop the audio loopback.
   - When the window is closed, release all audio and video resources.

4. **Application Entry Point**
   - Running `python -m sources.main` must launch the desktop application.

## Technical Constraints

- Language runtime: Python 3.10 or later.
- Use type hints for all public functions and methods.
- Dependencies must be declared in `requirements.txt` with compatible version ranges.
- Use `threading` for all I/O‑bound background work.
- Shared state must be protected with `threading.Lock` or equivalent.
- Follow the project conventions described in `prompts/common/conventions.md`.
- Use the development workflow described in `prompts/common/workflow.md`.

## Project Structure

