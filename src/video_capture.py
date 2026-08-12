"""
Module for capturing webcam frames using OpenCV in a background thread.
"""

import threading
from typing import Callable, Optional

import cv2


class WebcamCapture:
    """Captures frames from a camera ID asynchronously."""

    def __init__(self, camera_id: int = 0) -> None:
        self.camera_id = camera_id
        self.cap: Optional[cv2.VideoCapture] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def start(self, callback: Callable[[cv2.Mat], None]) -> None:
        """
        Start capturing frames in a daemon thread.

        The provided *callback* will be called with each frame (as a numpy
        array).

        :param callback: function that receives a BGR frame
        """
        if self._thread is not None:
            raise RuntimeError("Capture already running.")

        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera {self.camera_id}")

        def _run() -> None:
            while not self._stop_event.is_set():
                ret, frame = self.cap.read()
                if not ret:
                    break
                callback(frame)
            self.release()

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Signal the capture thread to stop and release the camera."""
        self._stop_event.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join()
        self.release()

    def release(self) -> None:
        """Release the underlying VideoCapture resource."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
