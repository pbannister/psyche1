from pathlib import Path
from typing import Dict, List, Optional, Tuple
import os

import cv2
import numpy as np


class FaceRecognition:
    """Detect faces in a video frame and optionally recognize known people.

    Detection uses OpenCV's Haar cascade. Recognition (when a directory of
    known face images is supplied) uses OpenCV's LBPH recognizer.

    Known-face directory layout::

        known_faces/
            Alice/
                alice_1.jpg
                alice_2.png
            Bob/
                bob_1.jpg

    If no directory is given, the engine still performs detection but every
    detected face will be labeled "Unknown".
    """

    def __init__(
        self,
        known_faces_dir: Optional[str] = None,
        cascade_path: Optional[str] = None,
    ) -> None:
        # Search for a usable Haar cascade file in the standard OpenCV data
        # directory.  Several file names exist across OpenCV releases; try
        # the most common ones.
        if cascade_path is None:
            base_dir = cv2.data.haarcascades
            candidates = (
                "haarcascade_frontalface_default.xml",
                "haarcascade_frontalface_alt.xml",
                "haarcascade_frontalface_alt2.xml",
            )
            for name in candidates:
                full = os.path.join(base_dir, name)
                try:
                    test = cv2.CascadeClassifier(full)
                    if not test.empty():
                        cascade_path = full
                        break
                except Exception:
                    continue
            if cascade_path is None:
                raise RuntimeError(
                    "Could not find a Haar cascade classifier.  "
                    f"Searched in {base_dir} with candidates "
                    f"{', '.join(candidates)}"
                )

        # Try the usual attribute first, fall back to the low‑level
        # extension module that some builds expose as cv2.cv2.
        try:
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
        except AttributeError:
            try:
                self.face_cascade = cv2.cv2.CascadeClassifier(cascade_path)
            except AttributeError:
                raise RuntimeError(
                    "OpenCV does not provide CascadeClassifier. "
                    "Please install opencv-python or opencv-contrib-python."
                )

        if self.face_cascade.empty():
            raise RuntimeError(f"Could not load Haar cascade from {cascade_path}")

        # LBPHFaceRecognizer comes from opencv-contrib; gracefully
        # degrade to detection-only mode if it is missing.
        try:
            self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        except AttributeError:
            self.recognizer = None

        self.known_faces_dir = known_faces_dir
        self.ready = False
        self.labels: Dict[int, str] = {}

        if known_faces_dir is not None:
            self.load_known_faces(known_faces_dir)

    def load_known_faces(self, directory: str) -> None:
        """Train the recognizer from a directory of person-named subfolders."""
        if self.recognizer is None:
            print(
                "Warning: face recognizer is not available "
                "(opencv-contrib-python is missing). Recognition will be disabled."
            )
            self.ready = False
            return

        dir_path = Path(directory)
        if not dir_path.is_dir():
            raise FileNotFoundError(f"Faces directory not found: {directory}")

        faces = []
        labels = []
        label_ids: Dict[str, int] = {}
        next_id = 0

        for person_dir in sorted(dir_path.iterdir()):
            if not person_dir.is_dir():
                continue
            person_name = person_dir.name
            if person_name not in label_ids:
                label_ids[person_name] = next_id
                next_id += 1

            image_paths = sorted(person_dir.glob("*.jpg")) + sorted(
                person_dir.glob("*.png")
            )
            for image_path in image_paths:
                img = cv2.imread(str(image_path))
                if img is None:
                    continue
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces.append(gray)
                labels.append(label_ids[person_name])

        if not faces:
            self.ready = False
            return

        self.labels = {v: k for k, v in label_ids.items()}
        self.recognizer.train(faces, np.array(labels))
        self.ready = True

    def detect(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Return bounding boxes of all detected faces as (x, y, w, h)."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60),
        )
        return [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in faces]

    def recognize(self, frame: np.ndarray) -> List[dict]:
        """Detect faces and return info for each face.

        Each dictionary contains ``bbox``, ``name`` and ``confidence``.
        Confidence is ``None`` when no known faces have been loaded.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        results = []

        for x, y, w, h in self.detect(frame):
            roi = gray[y : y + h, x : x + w]
            name = "Unknown"
            confidence = None

            if self.ready:
                label, confidence = self.recognizer.predict(roi)
                name = self.labels.get(label, "Unknown")

            results.append(
                {
                    "bbox": (x, y, w, h),
                    "name": name,
                    "confidence": float(confidence) if confidence is not None else None,
                }
            )

        return results
