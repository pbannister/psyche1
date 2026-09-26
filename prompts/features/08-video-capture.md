# Feature: Video Capture

## Purpose

Capture frames from a webcam in the background and make the latest frame
available without blocking the UI.

## Requirements

- `VIDEO-CAPTURE-R001` — Use OpenCV `cv2.VideoCapture` to read frames from a webcam.
- `VIDEO-CAPTURE-R002` — Provide `VideoCapture` in `sources/video_capture.py` with an optional `camera_index` and optional `width` and `height` constructor parameters.
- `VIDEO-CAPTURE-R003` — `video_capture_start()` begins the background capture thread and is idempotent while already running.
- `VIDEO-CAPTURE-R004` — `video_frame_get()` returns a copy of the latest BGR frame, or `None` before any frame is available.
- `VIDEO-CAPTURE-R005` — `video_capture_release()` stops the thread and releases the camera.
- `VIDEO-CAPTURE-R006` — Run capture in a daemon background thread and protect the current frame with a lock.
- `VIDEO-CAPTURE-R007` — Throttle capture to roughly 30 frames per second.
- `VIDEO-CAPTURE-R008` — Continue waiting for a frame when a read fails instead of terminating the thread.

## Behavior

- After a start, `video_frame_get` returns frames within one capture interval.
- Before a start, or before the first frame, `video_frame_get` returns `None`.
- Release stops the thread within the join timeout and frees the camera.

## Dependencies

- None.
