# Psyche1

Psyche1 is a Linux desktop application for multimodal capture and presentation.
It combines audio I/O, webcam video, face detection/recognition, voice recognition, speech-to-text, and text-to-speech into a single GUI built with PyQt6.

## Features

- Audio I/O (microphone to speaker loopback; record and playback)
- Video capture from a webcam
- Face detection and recognition (OpenCV Haar cascade + LBPH recognizer)
- Voice recognition using a fully local Vosk model (microphone → text)
- Speech-to-text for already-captured float32 audio arrays
- Text-to-speech using local pyttsx3 engine (no network required)
- Graceful handling of missing optional libraries (Vosk, pyttsx3, PortAudio)
- Automatic download of the Vosk model on first use (if using the default cache path)

## Project structure

