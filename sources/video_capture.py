from typing import Optional
import threading
import time

import cv2
import numpy as np


class VideoCapture:
    """Webcam capture using OpenCV with a background thread.

    Frames are read continuously without blocking the main thread.
    Use :meth:`get_frame` to retrive the latest frame.
    """

    def __init__(self, camera_index: int = 0, width: int | None = None, height: int | None = None):
        self.cap = cv2.VideoCapture(camera_index)
        if width is not None and height is not None:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self.lock = threading.Lock()
        self.frame = None
        self.running = False
        self.thread = None

    def start(self) -> None:
        """Start the background capture thread."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self) -> None:
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            with self.lock:
                self.frame = frame
            time.sleep(0.03)  # roughly 30 FPS

    def get_frame(self) -> Optional[np.ndarray]:
        """Return the latest captured frame as a BGR numpy array.

        Returns ``None`` if no frame has been captured yet.
        """
        with self.lock:
            if self.frame is None:
                return None
            return self.frame.copy()

    def release(self) -> None:
        """Stop the capture thread and release the camera."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        self.cap.release()
