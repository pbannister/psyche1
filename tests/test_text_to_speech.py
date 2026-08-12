"""Unit tests for the text-to-speech module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sources.text_to_speech import TextToSpeech


@pytest.fixture
def setup_env(tmp_path):
    cache_dir = tmp_path / "piper"
    cache_dir.mkdir()

    # Create dummy model and config files for a built-in voice
    (cache_dir / "en_US-lessac-medium.onnx").write_bytes(b"dummy")
    (cache_dir / "en_US-lessac-medium.onnx.json").write_text(
        '{"name": "English"}', encoding="utf-8"
    )

    fake_voice = MagicMock()

    def synth(text, wav_file):
        import wave

        with wave.open(wav_file, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(b"\x00\x00" * 1600)  # 0.1 s of silence

    fake_voice.synthesize.side_effect = synth

    fake_piper = MagicMock()
    fake_piper.PiperVoice.load.return_value = fake_voice

    fake_sd = MagicMock()

    patchers = [
        patch("sources.text_to_speech.VOICE_CACHE_DIR", cache_dir),
        patch("sources.text_to_speech.piper", fake_piper),
        patch("sources.text_to_speech._PIPER_AVAILABLE", True),
        patch("sources.text_to_speech.sd", fake_sd),
        patch("sources.text_to_speech._SD_AVAILABLE", True),
    ]
    for p in patchers:
        p.start()

    yield fake_piper, fake_sd, cache_dir

    for p in patchers:
        p.stop()


def test_list_voices_includes_builtin_and_custom(setup_env):
    fake_piper, fake_sd, cache_dir = setup_env

    custom_onnx = cache_dir / "my-custom.onnx"
    custom_onnx.write_bytes(b"dummy")
    (cache_dir / "my-custom.onnx.json").write_text(
        '{"name": "My Custom"}', encoding="utf-8"
    )

    tts = TextToSpeech()
    voices = tts.voices_list_get()
    ids = [v["id"] for v in voices]

    assert "en_US-lessac-medium" in ids
    assert "my-custom" in ids

    my_custom = next(v for v in voices if v["id"] == "my-custom")
    assert my_custom["name"] == "My Custom"


def test_set_voice_valid(setup_env):
    tts = TextToSpeech()
    tts.voice_set("en_US-lessac-medium")
    assert tts.voice_id == "en_US-lessac-medium"


def test_set_voice_invalid_raises(setup_env):
    tts = TextToSpeech()
    with pytest.raises(ValueError, match="not found"):
        tts.voice_set("unknown")


def test_speak_blocking_calls_piper_and_sd(setup_env):
    fake_piper, fake_sd, _ = setup_env

    tts = TextToSpeech()
    tts.speech_speak("hello", block=True)

    fake_piper.PiperVoice.load.assert_called_once()
    fake_sd.play.assert_called_once()

    _, kwargs = fake_sd.play.call_args
    assert kwargs["blocking"] is True
    assert kwargs["samplerate"] == 16000


def test_speak_non_blocking_starts_thread(setup_env):
    fake_piper, fake_sd, _ = setup_env

    tts = TextToSpeech()
    with patch("sources.text_to_speech.threading.Thread") as mock_thread:
        thread_instance = MagicMock()
        mock_thread.return_value = thread_instance

        tts.speech_speak("hello", block=False)

        mock_thread.assert_called_once()
        _, kwargs = mock_thread.call_args
        assert kwargs["daemon"] is True
        assert kwargs["args"] == ("hello", False)
        thread_instance.start.assert_called_once()


def test_stop_calls_sd_stop(setup_env):
    fake_piper, fake_sd, _ = setup_env

    tts = TextToSpeech()
    tts.speech_stop()

    fake_sd.stop.assert_called_once()


def test_missing_piper_raises_on_speak():
    with patch("sources.text_to_speech._PIPER_AVAILABLE", False):
        tts = TextToSpeech()
        with pytest.raises(RuntimeError, match="Piper is not installed"):
            tts.speech_speak("hello")


def test_missing_sd_raises_on_speak():
    with patch("sources.text_to_speech._SD_AVAILABLE", False), patch(
        "sources.text_to_speech._PIPER_AVAILABLE", True
    ):
        tts = TextToSpeech()
        with pytest.raises(RuntimeError, match="sounddevice"):
            tts.speech_speak("hello")
