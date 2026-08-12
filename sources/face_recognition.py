from pathlib import Path
from typing import Dict, List, Optional, Tuple
import os
import urllib.request

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
        # ---- Locate the Haar cascade XML file --------------------------------
        if cascade_path is None:
            # 1. Try the standard OpenCV data directory (cv2.data.haarcascades)
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

            # 2. Fall back to a file placed next to this module
            if cascade_path is None:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                local = os.path.join(script_dir, "haarcascade_frontalface_default.xml")
                if os.path.isfile(local):
                    try:
                        test = cv2.CascadeClassifier(local)
                        if not test.empty():
                            cascade_path = local
                    except Exception:
                        pass

            # 3. Last resort – download the file from OpenCV's repository
            if cascade_path is None:
                cascade_path = self._download_cascade()

        # ––––––––––––– Load the cascade –––––––––––––––––––––––––––––––––––
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
            raise RuntimeError(
                f"Could not load Haar cascade from {cascade_path}.\n"
                "Ensure one of the following files exists:\n"
                f"  – a file named ``haarcascade_frontalface_default.xml`` "
                f"in the ``sources/`` directory;\n"
                f"  – the ``cv2.data.haarcascades`` directory "
                f"(looked in {base_dir!r});\n"
                f"  – the file downloaded by the application to your cache.\n"
                "You can manually download the classifier from:\n"
                "  https://raw.githubusercontent.com/opencv/opencv/master/data/"
                "haarcascades/haarcascade_frontalface_default.xml"
            )

        # ─────────────── Set up recognizer (contrib‑only) ──────────────────
        try:
            self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        except AttributeError:
            self.recognizer = None

        self.known_faces_dir = known_faces_dir
        self.ready = False
        self.labels: Dict[int, str] = {}

        if known_faces_dir is not None:
            self.known_faces_load(known_faces_dir)

    # -----------------------------------------------------------------
    # Helper that downloads the cascade XML from the OpenCV repository
    # into the user's cache directory (~/.cache/psyche1/) and returns
    # the local path.
    # -----------------------------------------------------------------
    @staticmethod
    def _download_cascade() -> str:
        """Download the cascade file from GitHub if not already cached."""
        cache_root = Path.home() / ".cache" / "psyche1"
        cache_root.mkdir(parents=True, exist_ok=True)

        dest_path = cache_root / "haarcascade_frontalface_default.xml"
        if not dest_path.is_file():
            url = (
                "https://raw.githubusercontent.com/opencv/opencv/master/data"
                "/haarcascades/haarcascade_frontalface_default.xml"
            )
            print("FaceRecognition: first‑run – downloading cascade classifier…")
            try:
                urllib.request.urlretrieve(url, str(dest_path))
            except Exception as exc:
                raise RuntimeError(
                    "Could not obtain the Haar cascade file automatically.\n"
                    f"Try manually downloading the file from:\n  {url}\n"
                    f"and placing it in the sources/ directory."
                ) from exc
        return str(dest_path)

    # -----------------------------------------------------------------

    def known_faces_load(self, directory: str) -> None:
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

    def face_detect(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Return bounding boxes of all detected faces as (x, y, w, h)."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60),
        )
        return [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in faces]

    def face_recognize(self, frame: np.ndarray) -> List[dict]:
        """Detect faces and return info for each face.

        Each dictionary contains ``bbox``, ``name`` and ``confidence``.
        Confidence is ``None`` when no known faces have been loaded.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        results = []

        for x, y, w, h in self.face_detect(frame):
            roi = gray[y: y + h, x: x + w]
            name = "Unknown"
            confidence = None

            if self.ready:
                label, confidence = self.recognizer.predict(roi)
                name = self.labels.get(label, "Unknown")

            results.append({
                "bbox": (x, y, w, h),
                "name": name,
                "confidence": float(confidence) if confidence is not None else None,
            })

        return results
