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
from .voice_recognition import VoiceRecognition


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

        # ─── New: local voice recognition controller ────────────────────
        try:
            # Do not pass the 48 kHz audio_io; VoiceRecognition creates its
            # own 16 kHz stream for Vosk.
            self.voice_recognizer = VoiceRecognition()
        except Exception as exc:
            self.voice_recognizer = None
            print(f"VoiceRecognition disabled: {exc}")

        self._init_ui()

        self._video_timer = QTimer(self)
        self._video_timer.timeout.connect(self._update_frame)

    def _init_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # ── Video section ───────────────────────────────────────────────
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

        # ── Audio section ───────────────────────────────────────────────
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

        # ── Voice section ───────────────────────────────────────────────
        voice_group = QGroupBox("Voice")
        voice_layout = QVBoxLayout()

        self.record_button = QPushButton("Start Recording")
        self.record_button.clicked.connect(self.toggle_voice_recording)
        voice_layout.addWidget(self.record_button)

        self.voice_status_label = QLabel("Idle")
        self.voice_status_label.setWordWrap(True)
        self.voice_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.voice_status_label.setAutoFillBackground(True)
        self.voice_status_label.setMinimumHeight(28)
        self.voice_status_label.setStyleSheet(
            """
            background-color: #9e9e9e;
            color: white;
            padding: 4px;
            border: 1px solid #555;
            border-radius: 4px;
            font-weight: bold;
            """
        )
        voice_layout.addWidget(self.voice_status_label)

        self.transcription_label = QLabel("")
        self.transcription_label.setWordWrap(True)
        self.transcription_label.setStyleSheet(
            "background-color : #222; color: #fff; padding: 5px;"
        )
        self.transcription_label.setMinimumHeight(40)
        voice_layout.addWidget(self.transcription_label)

        voice_group.setLayout(voice_layout)
        layout.addWidget(voice_group)

    # ── Video controls ──────────────────────────────────────────────────
    def start_video(self) -> None:
        """Start the webcam capture and begin showing frames."""
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
        """Start the microphone‑to‑speaker audio loopback."""
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

    # ── Voice controls ──────────────────────────────────────────────────
    def toggle_voice_recording(self) -> None:
        if self.voice_recognizer is None:
            QMessageBox.critical(
                self,
                "Voice Recognition",
                "Voice recognition is not available (Vosk missing or no model "
                "configured).\nInstall Vosk and place a model in "
                "~/.cache/psyche1/ or set VOSK_MODEL_PATH.",
            )
            return

        if self.record_button.text() == "Start Recording":
            try:
                self.voice_recognizer.start_stream(self._on_transcription)
            except Exception as exc:
                QMessageBox.critical(self, "Voice Recognition", str(exc))
                return

            self.voice_status_label.setText("Listening…")
            self.voice_status_label.setStyleSheet(
                """
                background-color: #2196F3;
                color: white;
                padding: 4px;
                border: 1px solid #555;
                border-radius: 4px;
                font-weight: bold;
                """
            )
            self.record_button.setText("Stop Recording")
        else:
            self.voice_recognizer.stop_stream()
            self.voice_status_label.setText("Idle")
            self.voice_status_label.setStyleSheet(
                """
                background-color: #9e9e9e;
                color: white;
                padding: 4px;
                border: 1px solid #555;
                border-radius: 4px;
                font-weight: bold;
                """
            )
            self.record_button.setText("Start Recording")

    def _on_transcription(self, text: str, has_voice: bool) -> None:
        """Called by the voice recognition thread with each transcribed chunk.

        The call originates from a background thread, so we schedule the
        UI update on the main thread using QTimer.singleShot.
        """
        QTimer.singleShot(0, lambda: self._set_transcription(text, has_voice))

    def _set_transcription(self, text: str, has_voice: bool) -> None:
        """Update the transcription label and the voice status indicator.

        This method runs on the main (GUI) thread.
        """
        self.transcription_label.setText(text if text else "")

        if text.startswith("[Error]"):
            self.voice_status_label.setText("Error")
            self.voice_status_label.setStyleSheet(
                """
                background-color: #F44336;
                color: white;
                padding: 4px;
                border: 1px solid #555;
                border-radius: 4px;
                font-weight: bold;
                """
            )
        elif not has_voice:
            self.voice_status_label.setText("No voice")
            self.voice_status_label.setStyleSheet(
                """
                background-color: #616161;
                color: white;
                padding: 4px;
                border: 1px solid #555;
                border-radius: 4px;
                font-weight: bold;
                """
            )
        elif text.strip():
            self.voice_status_label.setText("Recognized voice")
            self.voice_status_label.setStyleSheet(
                """
                background-color: #4CAF50;
                color: white;
                padding: 4px;
                border: 1px solid #555;
                border-radius: 4px;
                font-weight: bold;
                """
            )
        else:
            self.voice_status_label.setText("Unrecognized voice")
            self.voice_status_label.setStyleSheet(
                """
                background-color: #FF9800;
                color: white;
                padding: 4px;
                border: 1px solid #555;
                border-radius: 4px;
                font-weight: bold;
                """
            )

    def closeEvent(self, event) -> None:
        """Clean up resources when the window is closed."""
        self._video_timer.stop()
        self.video_capture.release()
        self.audio_io.stop()

        if self.voice_recognizer is not None:
            self.voice_recognizer.stop_stream()

        event.accept()
