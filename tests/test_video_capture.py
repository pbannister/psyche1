import cv2
import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from sources.video_capture import VideoCapture


@pytest.fixture
def video_capture():
    with patch("sources.video_capture.cv2.VideoCapture") as mock_vc:
        mock_cap = MagicMock()
        mock_vc.return_value = mock_cap
        vc = VideoCapture()
        yield vc, mock_cap, mock_vc


def test_constructor_uses_default_camera(video_capture):
    vc, mock_cap, mock_vc = video_capture
    mock_vc.assert_called_once_with(0)
    assert vc.cap is mock_cap
    assert vc.running is False
    assert vc.frame is None


def test_constructor_sets_width_and_height_when_provided():
    with patch("sources.video_capture.cv2.VideoCapture") as mock_vc:
        mock_cap = MagicMock()
        mock_vc.return_value = mock_cap
        vc = VideoCapture(width=1280, height=720)
        mock_cap.set.assert_any_call(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        mock_cap.set.assert_any_call(cv2.CAP_PROP_FRAME_HEIGHT, 720)


def test_constructor_does_not_set_resolution_when_not_given(video_capture):
    vc, mock_cap, _ = video_capture
    mock_cap.set.assert_not_called()


def test_start_starts_daemon_thread(video_capture):
    vc, _, _ = video_capture
    with patch("sources.video_capture.threading.Thread") as mock_thread:
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        vc.start()
        assert vc.running is True
        mock_thread.assert_called_once()
        _, kwargs = mock_thread.call_args
        assert kwargs["daemon"] is True
        assert kwargs["target"] == vc._update
        mock_thread_instance.start.assert_called_once()


def test_start_does_nothing_if_already_running(video_capture):
    vc, _, _ = video_capture
    vc.running = True
    vc.thread = MagicMock()
    with patch("sources.video_capture.threading.Thread") as mock_thread:
        vc.start()
        mock_thread.assert_not_called()


def test_get_frame_returns_none_when_no_frame(video_capture):
    vc, _, _ = video_capture
    assert vc.get_frame() is None


def test_get_frame_returns_copy_of_latest_frame(video_capture):
    vc, _, _ = video_capture
    frame = np.array([[1, 2], [3, 4]], dtype=np.uint8)
    with vc.lock:
        vc.frame = frame
    result = vc.get_frame()
    np.testing.assert_array_equal(result, frame)
    assert result is not frame


def test_release_without_thread_releases_camera(video_capture):
    vc, mock_cap, _ = video_capture
    vc.release()
    assert vc.running is False
    mock_cap.release.assert_called_once_with()


def test_release_with_thread_stops_and_releases(video_capture):
    vc, mock_cap, _ = video_capture
    vc.running = True
    vc.thread = MagicMock()
    vc.release()
    assert vc.running is False
    vc.thread.join.assert_called_once_with(timeout=1.0)
    mock_cap.release.assert_called_once_with()
