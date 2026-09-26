# Feature: Facial Recognition

## Purpose

Detect human faces in a live webcam frame and label each one with a known name
or `Unknown`.
The feature provides bounding boxes and confidence scores for the UI overlay
and supports detection-only and detection-plus-recognition modes.

## Requirements

- `FACIAL-RECOGNITION-R001` — Detect faces with an OpenCV Haar cascade and recognize them with the OpenCV LBPH recognizer.
- `FACIAL-RECOGNITION-R002` — Provide `face_detect(frame)` returning the list of face boxes and `face_recognize(frame)` returning a list of result dictionaries.
- `FACIAL-RECOGNITION-R003` — Each result dictionary contains `bbox` as an `(x, y, w, h)` tuple, `name` as a string, and `confidence` as a float or `None` when no known faces are loaded.
- `FACIAL-RECOGNITION-R004` — `face_recognize()` calls `face_detect()` internally.
- `FACIAL-RECOGNITION-R005` — Load known faces from a directory of per-person subfolders and train the recognizer from those images at startup.
- `FACIAL-RECOGNITION-R006` — Train the recognizer only once at startup and perform no online learning.
- `FACIAL-RECOGNITION-R007` — Silently skip known-face images that contain no detectable face.
- `FACIAL-RECOGNITION-R008` — Allow the application to start with no known-faces directory; in that mode every detection is labelled `Unknown`.
- `FACIAL-RECOGNITION-R009` — Locate the Haar cascade in this order: the OpenCV data directory, a file next to the module, then a download to `~/.cache/psyche1/`.
- `FACIAL-RECOGNITION-R010` — Cache a downloaded cascade so later runs do not download it again.
- `FACIAL-RECOGNITION-R011` — Raise a clear error when the Haar cascade cannot be loaded, and disable recognition while keeping detection when the LBPH recognizer is unavailable.
- `FACIAL-RECOGNITION-R012` — Provide `FaceRecognition` in `sources/face_recognition.py` with an optional `known_faces_dir` constructor parameter.
- `FACIAL-RECOGNITION-R013` — The UI overlays each bounding box and name on the displayed frame.
- `FACIAL-RECOGNITION-R014` — Log the start and stop of recognition and the name of each recognized face.

## Behavior

- Starting the camera overlays a green box per detected face.
- A face matching a known person is labelled with that name; an unmatched or unknown face is labelled `Unknown`.
- With no known-faces directory the feature still detects and boxes faces.

## Dependencies

- `08-video-capture.md`
