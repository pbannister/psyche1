import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from sources.audio_io import AudioIO


@pytest.fixture(autouse=True)
def fake_sd():
    fake = MagicMock()
    fake.Stream.return_value = MagicMock()
    fake.rec.return_value = np.zeros((1, 1), dtype=np.float32)
    fake.play.return_value = None
    with patch("sources.audio_io.sd", fake):
        yield fake


def _get_callback(fake_sd, audio):
    audio.audio_stream_start()
    args, kwargs = fake_sd.Stream.call_args
    return kwargs["callback"]


def test_start_creates_stream_with_desired_parameters(fake_sd):
    audio = AudioIO(sample_rate=16000, channels=2)
    audio.audio_stream_start()
    args, kwargs = fake_sd.Stream.call_args
    assert kwargs["samplerate"] == 16000
    assert kwargs["channels"] == 2
    assert kwargs["dtype"] == "float32"
    assert kwargs["blocksize"] == 1024
    assert callable(kwargs["callback"])
    assert audio._is_running


def test_start_twice_raises(fake_sd):
    audio = AudioIO()
    audio.audio_stream_start()
    with pytest.raises(RuntimeError, match="already running"):
        audio.audio_stream_start()


def test_stop_when_running(fake_sd):
    audio = AudioIO()
    audio.audio_stream_start()
    stream = fake_sd.Stream.return_value
    audio.audio_stream_stop()
    stream.stop.assert_called_once_with()
    stream.close.assert_called_once_with()
    assert audio.stream is None
    assert not audio._is_running


def test_stop_when_not_running_does_nothing(fake_sd):
    audio = AudioIO()
    audio.audio_stream_stop()
    fake_sd.Stream.assert_not_called()


def test_record_uses_sd_rec_and_returns_array(fake_sd):
    audio = AudioIO(sample_rate=8000, channels=1)
    expected = np.zeros((4000, 1), dtype=np.float32)
    fake_sd.rec.return_value = expected
    result = audio.audio_record(0.5)
    args, kwargs = fake_sd.rec.call_args
    assert args[0] == 4000
    assert kwargs["samplerate"] == 8000
    assert kwargs["channels"] == 1
    assert kwargs["dtype"] == "float32"
    assert result.shape == (4000, 1)


def test_play_calls_sd_play(fake_sd):
    audio = AudioIO(sample_rate=8000, channels=1)
    data = np.zeros((100, 1), dtype=np.float32)
    audio.audio_play(data)
    fake_sd.play.assert_called_once_with(data, samplerate=8000, blocking=False)


def test_default_loopback_copies_input_to_output(fake_sd):
    audio = AudioIO()
    callback = _get_callback(fake_sd, audio)
    indata = np.array([[1.0], [2.0], [3.0], [4.0]], dtype=np.float32)
    outdata = np.zeros_like(indata)
    callback(indata, outdata, 4, None, None)
    np.testing.assert_allclose(outdata, indata)


def test_callback_ignores_underflow(fake_sd, capsys):
    audio = AudioIO()
    callback = _get_callback(fake_sd, audio)

    class Status:
        input_underflow = True
        output_underflow = True
        input_overflow = False
        output_overflow = False

        def __str__(self):
            return "underflow"

    outdata = np.zeros((4, 1), dtype=np.float32)
    callback(np.ones((4, 1), dtype=np.float32), outdata, 4, None, Status())
    captured = capsys.readouterr()
    assert captured.out == ""


def test_callback_reports_overflow(fake_sd, capsys):
    audio = AudioIO()
    callback = _get_callback(fake_sd, audio)

    class Status:
        input_underflow = False
        output_underflow = False
        input_overflow = True
        output_overflow = False

        def __str__(self):
            return "overflow"

    outdata = np.zeros((4, 1), dtype=np.float32)
    callback(np.ones((4, 1), dtype=np.float32), outdata, 4, None, Status())
    captured = capsys.readouterr()
    assert "Audio error: overflow" in captured.out


def test_start_with_input_callback(fake_sd):
    audio = AudioIO()
    audio.audio_stream_start(input_callback=lambda indata: indata * 2)
    callback = fake_sd.Stream.call_args.kwargs["callback"]
    indata = np.ones((4, 1), dtype=np.float32)
    outdata = np.zeros((4, 1), dtype=np.float32)
    callback(indata, outdata, 4, None, None)
    np.testing.assert_allclose(outdata, 2)


def test_start_with_output_callback(fake_sd):
    audio = AudioIO()
    audio.audio_stream_start(output_callback=lambda frames: np.full((frames, 1), 5.0, dtype=np.float32))
    callback = fake_sd.Stream.call_args.kwargs["callback"]
    outdata = np.zeros((4, 1), dtype=np.float32)
    callback(np.zeros((4, 1), dtype=np.float32), outdata, 4, None, None)
    np.testing.assert_allclose(outdata, 5.0)


def test_missing_portaudio_raises_on_start():
    with patch("sources.audio_io.sd", None), \
         patch("sources.audio_io._SD_IMPORT_ERROR", OSError("PortAudio library missing")):
        audio = AudioIO()
        with pytest.raises(RuntimeError, match="PortAudio library not found"):
            audio.audio_stream_start()


def test_missing_portaudio_raises_on_record():
    with patch("sources.audio_io.sd", None), \
         patch("sources.audio_io._SD_IMPORT_ERROR", OSError("PortAudio library missing")):
        audio = AudioIO()
        with pytest.raises(RuntimeError, match="PortAudio library not found"):
            audio.audio_record(1.0)


def test_missing_portaudio_raises_on_play():
    with patch("sources.audio_io.sd", None), \
         patch("sources.audio_io._SD_IMPORT_ERROR", OSError("PortAudio library missing")):
        audio = AudioIO()
        with pytest.raises(RuntimeError, match="PortAudio library not found"):
            audio.audio_play(np.zeros((4, 1), dtype=np.float32))
