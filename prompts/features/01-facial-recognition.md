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
