"""Unit tests for the v2 TTS wrapper."""
from unittest.mock import MagicMock, patch

import pytest

from voiceover_elevenlabs_v2.tts import V2_CHAR_LIMIT, synthesize


def _stub_convert_returns(audio_bytes: bytes):
    """Build a MagicMock whose convert() returns an iterable yielding audio_bytes once."""
    return MagicMock(return_value=iter([audio_bytes]))


def test_synthesize_calls_convert_with_v2_defaults():
    fake_audio = b"\xff\xfb\x90\x00fake-mp3-bytes"
    with patch("voiceover_elevenlabs_v2.tts.ElevenLabs") as mock_client_class:
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
        assert call_kwargs["model_id"] == "eleven_multilingual_v2"
        assert call_kwargs["output_format"] == "mp3_44100_128"
        assert call_kwargs["language_code"] == "en"
        assert result == fake_audio


def test_synthesize_passes_full_voice_settings():
    """v2 carries stability + similarity_boost + style + use_speaker_boost."""
    with patch("voiceover_elevenlabs_v2.tts.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        mock_client.text_to_speech.convert = _stub_convert_returns(b"x")
        mock_client_class.return_value = mock_client

        synthesize(
            "x",
            voice_id="V",
            stability=0.4,
            similarity_boost=0.75,
            style=0.35,
            use_speaker_boost=True,
            api_key="sk_test",
        )

        call_kwargs = mock_client.text_to_speech.convert.call_args.kwargs
        settings = call_kwargs["voice_settings"]
        assert settings.stability == 0.4
        assert settings.similarity_boost == 0.75
        assert settings.style == 0.35
        assert settings.use_speaker_boost is True


def test_synthesize_rejects_text_over_10k():
    long_text = "x" * (V2_CHAR_LIMIT + 1)
    with pytest.raises(ValueError, match="character limit"):
        synthesize(long_text, voice_id="V", api_key="sk_test")


def test_synthesize_concatenates_streamed_chunks():
    """The SDK's convert() returns an iterator of bytes chunks; we join them."""
    with patch("voiceover_elevenlabs_v2.tts.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        mock_client.text_to_speech.convert = MagicMock(return_value=iter([b"abc", b"def", b"ghi"]))
        mock_client_class.return_value = mock_client

        result = synthesize("hi", voice_id="V", api_key="sk_test")
        assert result == b"abcdefghi"


def test_synthesize_accepts_custom_language_code():
    """When the caller overrides language_code, that value is forwarded."""
    with patch("voiceover_elevenlabs_v2.tts.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        mock_client.text_to_speech.convert = _stub_convert_returns(b"x")
        mock_client_class.return_value = mock_client

        synthesize("x", voice_id="V", language_code="es", api_key="sk_test")

        call_kwargs = mock_client.text_to_speech.convert.call_args.kwargs
        assert call_kwargs["language_code"] == "es"
