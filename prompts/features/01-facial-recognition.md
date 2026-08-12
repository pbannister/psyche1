# Facial recognition

Detect human faces in a live webcam feed.
Label each detected face with a name when a match is found in the known‑faces directory.
Label each detected face as "Unknown" when no match exists.
Provide a bounding box around each detected face.
Provide a confidence score for recognized faces.
Support both detection only and detection plus recognition modes.
Load known faces from a directory of per‑person subfolders.
Train a recognizer from the images in that directory on startup.
Use OpenCV Haar cascade for detection.
Use OpenCV LBPH recognizer for face recognition.
Expose a `recognize(frame)` method that accepts a BGR frame and returns a list of result dictionaries.
Each result dictionary contains the keys `bbox`, `name`, and `confidence`.
The `bbox` value is a tuple `(x, y, w, h)`.
The `name` value is a string.
The `confidence` value is either a float or `None` when no known faces are loaded.
Fail with a clear error if the Haar cascade cannot be loaded.
Allow the application to start even when no known‑faces directory is provided.
Locate the Haar cascade XML file using a search order.
First search the standard OpenCV data directory (`cv2.data.haarcascades`) for known filenames.
If not found, fall back to a file next to the module (`sources/` directory).
Finally, download the file from the OpenCV repository to the user cache (`~/.cache/psyche1/`).
Cache the downloaded file so later runs do not re‑download.
When opencv‑contrib‑python is missing, the recognizer is disabled.
In that case detection still works, but all recognised faces are labelled "Unknown".
The UI overlays the bounding box and name on the video frame.
The `detect(frame)` method must be available separately and return the list of boxes.
The `recognize()` method calls `detect()` internally.
Known‑faces loading must silently skip images that do not contain faces.
The recogniser is trained only once at startup; no online learning is performed.

## Python-specific requirements

- `opencv-contrib-python>=4.8.0` (provides both Haar cascade and LBPH face recognizer).
- `numpy>=1.24.0` (used for image array representation and training data).
- `requests>=2.28.0` (optional; used only for downloading the cascade file; can be replaced with `urllib.request`).
