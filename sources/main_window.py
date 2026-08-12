import cv2
import logging
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from typing import Optional

from .audio_io import AudioIO
from .face_recognition import FaceRecognition
from .text_to_speech import TextToSpeech
from .video_capture import VideoCapture
from .voice_recognition import VoiceRecognition

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main window of the Psyche1 application.

    Provides controls for the audio and video capture devices,
    voice recognition, and text-to-speech synthesis.
    """

    def __init__(self, known_faces_dir: Optional[str] = None) -> None:
        super().__init__()
        self.setWindowTitle("Psyche1")
        self.resize(800, 600)

        self.video_capture = VideoCapture()
        self.audio_io = AudioIO()
        self.face_recognition = FaceRecognition(known_faces_dir=known_faces_dir)

        # ─── Local voice recognition controller ─────────────────────
        try:
            self.voice_recognizer = VoiceRecognition()
        except Exception as exc:
            self.voice_recognizer = None
            print(f"VoiceRecognition disabled: {exc}")

        # ─── Local text-to-speech engine ────────────────────────────
        self.tts = TextToSpeech()

        self._init_ui()

        self._video_timer = QTimer(self)
        self._video_timer.timeout.connect(self._update_frame)

    def _init_ui(self) -> None:
        # Use a tab widget to separate the video and audio pages.
        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # ── Video page ──────────────────────────────────────────────
        video_page = QWidget()
        video_page_layout = QVBoxLayout(video_page)

        video_group = QGroupBox("Video")
        video_layout = QVBoxLayout()

        self.video_label = QLabel("No video")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("background-color: black; color: white;")
        video_layout.addWidget(self.video_label)

        video_buttons = QHBoxLayout()
        self.start_video_button = QPushButton("Start Camera")
        self.start_video_button.clicked.connect(self.video_start)
        self.stop_video_button = QPushButton("Stop Camera")
        self.stop_video_button.clicked.connect(self.video_stop)
        self.stop_video_button.setEnabled(False)

        video_buttons.addWidget(self.start_video_button)
        video_buttons.addWidget(self.stop_video_button)
        video_layout.addLayout(video_buttons)

        video_group.setLayout(video_layout)
        video_page_layout.addWidget(video_group)
        video_page_layout.addStretch()

        # ── Audio page ──────────────────────────────────────────────
        audio_page = QWidget()
        audio_page_layout = QVBoxLayout(audio_page)

        audio_group = QGroupBox("Audio")
        audio_layout = QHBoxLayout()

        self.start_audio_button = QPushButton("Start Audio")
        self.start_audio_button.clicked.connect(self.audio_start)
        self.stop_audio_button = QPushButton("Stop Audio")
        self.stop_audio_button.clicked.connect(self.audio_stop)
        self.stop_audio_button.setEnabled(False)

        audio_layout.addWidget(self.start_audio_button)
        audio_layout.addWidget(self.stop_audio_button)

        audio_group.setLayout(audio_layout)
        audio_page_layout.addWidget(audio_group)

        # ── Voice section (still on the Audio page) ─────────────────
        voice_group = QGroupBox("Voice")
        voice_layout = QVBoxLayout()

        self.record_button = QPushButton("Start Recording")
        self.record_button.clicked.connect(self.voice_recording_toggle)
        voice_layout.addWidget(self.record_button)

        self.voice_status_label = QLabel("Press Record to start")
        self.voice_status_label.setWordWrap(True)
        self.voice_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.voice_status_label.setMinimumHeight(36)
        self.voice_status_label.setStyleSheet(
            """
            background-color: #9e9e9e;
            color: white;
            padding: 8px;
            border: 1px solid #555;
            border-radius: 4px;
            font-size: 14px;
            font-weight: bold;
            """
        )
        voice_layout.addWidget(self.voice_status_label)

        self.transcription_label = QLabel("Press Record to start")
        self.transcription_label.setWordWrap(True)
        self.transcription_label.setStyleSheet(
            "background-color : #444; color: #fff; padding: 8px; font-size: 12px;"
        )
        self.transcription_label.setMinimumHeight(40)
        voice_layout.addWidget(self.transcription_label)

        voice_group.setLayout(voice_layout)
        audio_page_layout.addWidget(voice_group)

        # ── Speech (Text-to-Speech) section (Audio page) ────────────
        speech_group = QGroupBox("Speech")
        speech_layout = QVBoxLayout()

        self.voice_combo = QComboBox()
        self.voice_combo.currentIndexChanged.connect(self.voice_selection_changed)
        speech_layout.addWidget(self.voice_combo)

        self.tts_text_edit = QLineEdit()
        self.tts_text_edit.setPlaceholderText("Type text to speak…")
        speech_layout.addWidget(self.tts_text_edit)

        speech_buttons = QHBoxLayout()
        self.speak_button = QPushButton("Speak")
        self.speak_button.clicked.connect(self.speech_speak_clicked)
        self.stop_speech_button = QPushButton("Stop")
        self.stop_speech_button.clicked.connect(self.speech_stop_clicked)
        speech_buttons.addWidget(self.speak_button)
        speech_buttons.addWidget(self.stop_speech_button)
        speech_layout.addLayout(speech_buttons)

        speech_group.setLayout(speech_layout)
        audio_page_layout.addWidget(speech_group)
        audio_page_layout.addStretch()

        tabs.addTab(video_page, "Video")
        tabs.addTab(audio_page, "Audio")

        self.voice_combo_populate()

    # ── Video controls ──────────────────────────────────────────────
    def video_start(self) -> None:
        """Start the webcam capture and begin showing frames."""
        if not self.video_capture.cap.isOpened():
            self.video_capture = VideoCapture()

        if not self.video_capture.cap.isOpened():
            QMessageBox.critical(self, "Camera Error", "Could not open the camera.")
            return

        self.video_capture.video_capture_start()
        self._video_timer.start(33)  # ~30 fps
        self.start_video_button.setEnabled(False)
        self.stop_video_button.setEnabled(True)
        logger.info("Face recognition started")

    def video_stop(self) -> None:
        """Stop the webcam capture and clear the displayed frame."""
        self._video_timer.stop()
        self.video_capture.video_capture_release()
        self.video_label.clear()
        self.video_label.setText("No video")
        self.start_video_button.setEnabled(True)
        self.stop_video_button.setEnabled(False)
        logger.info("Face recognition stopped")

    def _update_frame(self) -> None:
        """Fetch the latest video frame, run face detection/recognition, and display it."""
        frame = self.video_capture.video_frame_get()
        if frame is None:
            return

        face_results = self.face_recognition.face_recognize(frame)
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
                if name != "Unknown":
                    logger.info("Face recognized: %s", name)

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

    def audio_start(self) -> None:
        """Start the microphone‑to‑speaker audio loopback."""
        try:
            self.audio_io.audio_stream_start()
        except Exception as exc:
            QMessageBox.critical(self, "Audio Error", str(exc))
            return

        self.start_audio_button.setEnabled(False)
        self.stop_audio_button.setEnabled(True)

    def audio_stop(self) -> None:
        """Stop the audio loopback stream."""
        self.audio_io.audio_stream_stop()
        self.start_audio_button.setEnabled(True)
        self.stop_audio_button.setEnabled(False)

    # ── Voice controls ──────────────────────────────────────────────
    def voice_recording_toggle(self) -> None:
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
                self.voice_recognizer.voice_stream_start(self._on_transcription)
            except Exception as exc:
                QMessageBox.critical(self, "Voice Recognition", str(exc))
                return

            self.voice_status_label.setText("Listening…")
            self.voice_status_label.setStyleSheet(
                """
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border: 1px solid #555;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                """
            )
            self.transcription_label.setText("Listening…")
            self.transcription_label.setStyleSheet(
                "background-color : #444; color: #fff; padding: 8px; font-size: 12px;"
            )
            self.record_button.setText("Stop Recording")
            logger.info("Voice recognition started")
            logger.info("Recording started")
        else:
            self.voice_recognizer.voice_stream_stop()
            self.voice_status_label.setText("Idle")
            self.voice_status_label.setStyleSheet(
                """
                background-color: #9e9e9e;
                color: white;
                padding: 8px;
                border: 1px solid #555;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                """
            )
            self.transcription_label.setText("Idle")
            self.transcription_label.setStyleSheet(
                "background-color : #444; color: #fff; padding: 8px; font-size: 12px;"
            )
            self.record_button.setText("Start Recording")
            logger.info("Voice recognition stopped")
            logger.info("Recording stopped")

    def _on_transcription(self, text: str, has_voice: bool) -> None:
        """Called by the voice recognition thread with each transcribed chunk.

        The call originates from a background thread, so we schedule the
        UI update on the main thread using QTimer.singleShot.
        """
        QTimer.singleShot(0, lambda: self._set_transcription(text, has_voice))

    def _set_transcription(self, text: str, has_voice: bool) -> None:
        """Update the transcription and status labels.

        This method runs on the main (GUI) thread.
        """
        if text.startswith("[Error]"):
            self.voice_status_label.setText("Error")
            self.voice_status_label.setStyleSheet(
                """
                background-color: #F44336;
                color: white;
                padding: 8px;
                border: 1px solid #555;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                """
            )
            self.transcription_label.setText(text)
            self.transcription_label.setStyleSheet(
                "background-color : #F44336; color: white; padding: 8px; font-size: 12px;"
            )
        elif not has_voice:
            self.voice_status_label.setText("No voice")
            self.voice_status_label.setStyleSheet(
                """
                background-color: #616161;
                color: white;
                padding: 8px;
                border: 1px solid #555;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                """
            )
            self.transcription_label.setText("No voice")
            self.transcription_label.setStyleSheet(
                "background-color : #616161; color: white; padding: 8px; font-size: 12px;"
            )
        elif text.strip():
            self.voice_status_label.setText("Recognized voice")
            self.voice_status_label.setStyleSheet(
                """
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border: 1px solid #555;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                """
            )
            self.transcription_label.setText(text)
            self.transcription_label.setStyleSheet(
                "background-color : #4CAF50; color: white; padding: 8px; font-size: 12px;"
            )
            logger.info("Voice name: %s", text)
        else:
            self.voice_status_label.setText("Unrecognized voice")
            self.voice_status_label.setStyleSheet(
                """
                background-color: #FF9800;
                color: white;
                padding: 8px;
                border: 1px solid #555;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                """
            )
            self.transcription_label.setText("Unrecognized voice")
            self.transcription_label.setStyleSheet(
                "background-color : #FF9800; color: white; padding: 8px; font-size: 12px;"
            )

    # ── Speech controls ─────────────────────────────────────────────
    def voice_combo_populate(self) -> None:
        """Populate the voice combo box from the local TTS engine.

        If the TTS engine is unavailable, disable the controls and show
        a descriptive message in the combo box.
        """
        try:
            voices = self.tts.voices_list_get()
        except RuntimeError as exc:
            self.voice_combo.addItem(f"TTS unavailable: {exc}")
            self.voice_combo.setEnabled(False)
            self.speak_button.setEnabled(False)
            self.stop_speech_button.setEnabled(False)
            self.tts_text_edit.setEnabled(False)
            return

        if not voices:
            self.voice_combo.addItem("No voices found")
            self.voice_combo.setEnabled(False)
            self.speak_button.setEnabled(False)
            self.stop_speech_button.setEnabled(False)
            self.tts_text_edit.setEnabled(False)
            return

        for voice in voices:
            self.voice_combo.addItem(voice["name"], voice["id"])

        if self.tts.voice_id:
            idx = self.voice_combo.findData(self.tts.voice_id)
            if idx >= 0:
                self.voice_combo.setCurrentIndex(idx)

    def voice_selection_changed(self) -> None:
        """Handle a change in the selected TTS voice."""
        voice_id = self.voice_combo.currentData()
        if not voice_id:
            return
        try:
            self.tts.voice_set(voice_id)
        except Exception as exc:
            QMessageBox.critical(self, "Voice Selection", str(exc))

    def speech_speak_clicked(self) -> None:
        """Speak the text currently entered in the text field."""
        text = self.tts_text_edit.text().strip()
        if not text:
            return
        try:
            self.tts.speech_speak(text)
        except Exception as exc:
            QMessageBox.critical(self, "Text to Speech", str(exc))

    def speech_stop_clicked(self) -> None:
        """Stop any currently running speech."""
        try:
            self.tts.speech_stop()
        except Exception:
            pass

    def closeEvent(self, event) -> None:
        """Clean up resources when the window is closed."""
        self._video_timer.stop()
        self.video_capture.video_capture_release()
        self.audio_io.audio_stream_stop()

        if self.voice_recognizer is not None:
            self.voice_recognizer.voice_stream_stop()

        if hasattr(self, "tts"):
            self.tts.speech_stop()

        event.accept()
