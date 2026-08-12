"""Unit tests for the text-to-speech module."""

from unittest.mock import MagicMock, patch

import pytest

from sources.text_to_speech import TextToSpeech


@pytest.fixture
def fake_engine():
    engine = MagicMock()
    engine.getProperty.side_effect = (
        lambda name: [MagicMock(id="en-us", name="English")]
        if name == "voices"
        else None
    )
    return engine


@pytest.fixture
def patched_pyttsx3(fake_engine):
    with patch("sources.text_to_speech.pyttsx3") as mock_pyttsx3:
        mock_pyttsx3.init.return_value = fake_engine
        yield mock_pyttsx3


def test_constructor_sets_voice_id():
    tts = TextToSpeech(voice_id="test-voice")
    assert tts.voice_id == "test-voice"


def test_list_voices_returns_dicts(patched_pyttsx3, fake_engine):
    tts = TextToSpeech()
    voices = tts.list_voices()
    assert isinstance(voices, list)
    assert len(voices) == 1
    assert voices[0]["id"] == "en-us"
    assert voices[0]["name"] == "English"
    fake_engine.getProperty.assert_called_with("voices")
    assert fake_engine.getProperty.call_count == 1


def test_list_voices_cached(patched_pyttsx3, fake_engine):
    tts = TextToSpeech()
    tts.list_voices()
    tts.list_voices()
    assert fake_engine.getProperty.call_count == 1


def test_set_voice_sets_attribute(patched_pyttsx3, fake_engine):
    tts = TextToSpeech()
    tts.set_voice("en-us")
    assert tts.voice_id == "en-us"
    fake_engine.setProperty.assert_called_with("voice", "en-us")


def test_set_voice_raises_for_unknown(patched_pyttsx3):
    tts = TextToSpeech()
    with pytest.raises(ValueError, match="not found"):
        tts.set_voice("unknown")


def test_speak_blocking(patched_pyttsx3, fake_engine):
    tts = TextToSpeech()
    tts.speak("hello", block=True)
    fake_engine.say.assert_called_once_with("hello")
    fake_engine.runAndWait.assert_called_once()


def test_speak_non_blocking_starts_thread(patched_pyttsx3, fake_engine):
    tts = TextToSpeech()
    with patch("sources.text_to_speech.threading.Thread") as mock_thread:
        thread_instance = MagicMock()
        mock_thread.return_value = thread_instance
        tts.speak("hello", block=False)
        mock_thread.assert_called_once()
        _, kwargs = mock_thread.call_args
        assert kwargs["daemon"] is True
        thread_instance.start.assert_called_once()


def test_stop_calls_engine_stop(patched_pyttsx3, fake_engine):
    tts = TextToSpeech()
    tts.speak("hello", block=True)  # force engine creation
    tts.stop()
    fake_engine.stop.assert_called_once()


def test_missing_pyttsx3_raises_on_list_voices():
    with patch("sources.text_to_speech._PYTTTSX_AVAILABLE", False), \
         patch("sources.text_to_speech.pyttsx3", None):
        tts = TextToSpeech()
        with pytest.raises(RuntimeError, match="pyttsx3 is not installed"):
            tts.list_voices()


def test_missing_pyttsx3_raises_on_speak():
    with patch("sources.text_to_speech._PYTTTSX_AVAILABLE", False), \
         patch("sources.text_to_speech.pyttsx3", None):
        tts = TextToSpeech()
        with pytest.raises(RuntimeError, match="pyttsx3 is not installed"):
            tts.speak("hello")
