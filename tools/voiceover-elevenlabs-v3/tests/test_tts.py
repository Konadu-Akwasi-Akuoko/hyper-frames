"""Unit tests for the v3 TTS wrapper."""
from unittest.mock import MagicMock, patch

import pytest

from voiceover_elevenlabs_v3.tts import V3_CHAR_LIMIT, synthesize


def _stub_convert_returns(audio_bytes: bytes):
    """Build a MagicMock whose convert() returns an iterable yielding audio_bytes once."""
    return MagicMock(return_value=iter([audio_bytes]))


def test_synthesize_calls_convert_with_expected_args():
    fake_audio = b"\xff\xfb\x90\x00fake-mp3-bytes"
    with patch("voiceover_elevenlabs_v3.tts.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        mock_client.text_to_speech.convert = _stub_convert_returns(fake_audio)
        mock_client_class.return_value = mock_client

        result = synthesize(
            "Hello world.",
            voice_id="VOICE",
            api_key="sk_test",
        )

        mock_client_class.assert_called_once_with(api_key="sk_test")
        call_kwargs = mock_client.text_to_speech.convert.call_args.kwargs
        assert call_kwargs["voice_id"] == "VOICE"
        assert call_kwargs["text"] == "Hello world."
        assert call_kwargs["model_id"] == "eleven_v3"
        assert call_kwargs["output_format"] == "mp3_44100_128"
        assert result == fake_audio


def test_synthesize_passes_voice_settings():
    with patch("voiceover_elevenlabs_v3.tts.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        mock_client.text_to_speech.convert = _stub_convert_returns(b"x")
        mock_client_class.return_value = mock_client

        synthesize(
            "x",
            voice_id="V",
            stability=0.7,
            similarity_boost=0.8,
            api_key="sk_test",
        )

        call_kwargs = mock_client.text_to_speech.convert.call_args.kwargs
        settings = call_kwargs["voice_settings"]
        assert settings.stability == 0.7
        assert settings.similarity_boost == 0.8


def test_synthesize_rejects_text_over_char_limit():
    long_text = "x" * (V3_CHAR_LIMIT + 1)
    with pytest.raises(ValueError, match="character limit"):
        synthesize(long_text, voice_id="V", api_key="sk_test")


def test_synthesize_concatenates_streamed_chunks():
    """The SDK's convert() returns an iterator of bytes chunks; we join them."""
    with patch("voiceover_elevenlabs_v3.tts.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        mock_client.text_to_speech.convert = MagicMock(return_value=iter([b"abc", b"def", b"ghi"]))
        mock_client_class.return_value = mock_client

        result = synthesize("hi", voice_id="V", api_key="sk_test")
        assert result == b"abcdefghi"
