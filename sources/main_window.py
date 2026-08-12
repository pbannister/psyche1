import cv2
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from typing import Optional

from .audio_io import AudioIO
from .face_recognition import FaceRecognition
from .video_capture import VideoCapture


class MainWindow(QMainWindow):
    """Main window of the Psyche1 application.

    Provides controls for the audio and video capture devices and
    displays the live webcam feed.
    """

    def __init__(self, known_faces_dir: Optional[str] = None) -> None:
        super().__init__()
        self.setWindowTitle("Psyche1")
        self.resize(800, 600)

        self.video_capture = VideoCapture()
        self.audio_io = AudioIO()
        self.face_recognition = FaceRecognition(known_faces_dir=known_faces_dir)

        self._init_ui()

        self._video_timer = QTimer(self)
        self._video_timer.timeout.connect(self._update_frame)

    def _init_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Video section
        video_group = QGroupBox("Video")
        video_layout = QVBoxLayout()

        self.video_label = QLabel("No video")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("background-color: black; color: white;")
        video_layout.addWidget(self.video_label)

        video_buttons = QHBoxLayout()
        self.start_video_button = QPushButton("Start Camera")
        self.start_video_button.clicked.connect(self.start_video)
        self.stop_video_button = QPushButton("Stop Camera")
        self.stop_video_button.clicked.connect(self.stop_video)
        self.stop_video_button.setEnabled(False)

        video_buttons.addWidget(self.start_video_button)
        video_buttons.addWidget(self.stop_video_button)
        video_layout.addLayout(video_buttons)

        video_group.setLayout(video_layout)
        layout.addWidget(video_group)

        # Audio section
        audio_group = QGroupBox("Audio")
        audio_layout = QHBoxLayout()

        self.start_audio_button = QPushButton("Start Audio")
        self.start_audio_button.clicked.connect(self.start_audio)
        self.stop_audio_button = QPushButton("Stop Audio")
        self.stop_audio_button.clicked.connect(self.stop_audio)
        self.stop_audio_button.setEnabled(False)

        audio_layout.addWidget(self.start_audio_button)
        audio_layout.addWidget(self.stop_audio_button)

        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)

    def start_video(self) -> None:
        """Start the webcam capture and begin showing frames."""
        # If the camera was previously stopped, recreate the capture object
        if not self.video_capture.cap.isOpened():
            self.video_capture = VideoCapture()

        if not self.video_capture.cap.isOpened():
            QMessageBox.critical(self, "Camera Error", "Could not open the camera.")
            return

        self.video_capture.start()
        self._video_timer.start(33)  # ~30 fps
        self.start_video_button.setEnabled(False)
        self.stop_video_button.setEnabled(True)

    def stop_video(self) -> None:
        """Stop the webcam capture and clear the displayed frame."""
        self._video_timer.stop()
        self.video_capture.release()
        self.video_label.clear()
        self.video_label.setText("No video")
        self.start_video_button.setEnabled(True)
        self.stop_video_button.setEnabled(False)

    def _update_frame(self) -> None:
        """Fetch the latest video frame, run face detection/recognition, and display it."""
        frame = self.video_capture.get_frame()
        if frame is None:
            return

        # Run face detection / recognition on the BGR frame
        face_results = self.face_recognition.recognize(frame)
        for result in face_results:
            x, y, w, h = result["bbox"]
            name = result["name"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if name:
                cv2.putText(
                    frame,
                    name,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(
            rgb_image.tobytes(),
            w,
            h,
            bytes_per_line,
            QImage.Format.Format_RGB888,
        )
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))

    def start_audio(self) -> None:
        """Start the microphone-to-speaker audio loopback."""
        try:
            self.audio_io.start()
        except Exception as exc:
            QMessageBox.critical(self, "Audio Error", str(exc))
            return

        self.start_audio_button.setEnabled(False)
        self.stop_audio_button.setEnabled(True)

    def stop_audio(self) -> None:
        """Stop the audio loopback stream."""
        self.audio_io.stop()
        self.start_audio_button.setEnabled(True)
        self.stop_audio_button.setEnabled(False)

    def closeEvent(self, event) -> None:
        """Clean up resources when the window is closed."""
        self._video_timer.stop()
        self.video_capture.release()
        self.audio_io.stop()
        event.accept()
