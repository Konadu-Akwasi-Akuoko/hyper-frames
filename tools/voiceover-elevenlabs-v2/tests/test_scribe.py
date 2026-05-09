"""Unit tests for the Scribe v2 wrapper."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from voiceover_elevenlabs_v2.scribe import RETRY_BACKOFF_SECS, transcribe


@pytest.fixture
def fake_audio(tmp_path: Path) -> Path:
    p = tmp_path / "voiceover.mp3"
    p.write_bytes(b"\xff\xfb\x90\x00fake")
    return p


def _scribe_response():
    return SimpleNamespace(
        language_code="eng",
        language_probability=0.95,
        text="hi",
        audio_duration_secs=1.0,
        words=[],
    )


def test_transcribe_calls_convert_with_expected_args(fake_audio):
    with patch("voiceover_elevenlabs_v2.scribe.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        mock_client.speech_to_text.convert = MagicMock(return_value=_scribe_response())
        mock_client_class.return_value = mock_client

        transcribe(fake_audio, api_key="sk_test")

        mock_client_class.assert_called_once_with(api_key="sk_test")
        call_kwargs = mock_client.speech_to_text.convert.call_args.kwargs
        assert call_kwargs["model_id"] == "scribe_v2"
        assert call_kwargs["timestamps_granularity"] == "word"
        assert call_kwargs["diarize"] is True
        assert call_kwargs["tag_audio_events"] is True


def test_transcribe_returns_response_object(fake_audio):
    with patch("voiceover_elevenlabs_v2.scribe.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        expected = _scribe_response()
        mock_client.speech_to_text.convert = MagicMock(return_value=expected)
        mock_client_class.return_value = mock_client

        result = transcribe(fake_audio, api_key="sk_test")
        assert result is expected


def test_transcribe_rejects_multichannel_response(fake_audio):
    with patch("voiceover_elevenlabs_v2.scribe.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        # Multichannel responses have a 'transcripts' attribute (list of chunks).
        bad = SimpleNamespace(transcripts=[_scribe_response()])
        mock_client.speech_to_text.convert = MagicMock(return_value=bad)
        mock_client_class.return_value = mock_client

        with pytest.raises(ValueError, match="Multichannel"):
            transcribe(fake_audio, api_key="sk_test")


def test_transcribe_rejects_webhook_response(fake_audio):
    with patch("voiceover_elevenlabs_v2.scribe.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        # Webhook responses have a 'request_id' attribute (snake_case in the Python SDK).
        bad = SimpleNamespace(message="queued", request_id="req_123", transcription_id="tr_456")
        mock_client.speech_to_text.convert = MagicMock(return_value=bad)
        mock_client_class.return_value = mock_client

        with pytest.raises(ValueError, match="Webhook"):
            transcribe(fake_audio, api_key="sk_test")


def test_transcribe_raises_for_missing_file(tmp_path: Path):
    missing = tmp_path / "nope.mp3"
    with pytest.raises(FileNotFoundError):
        transcribe(missing, api_key="sk_test")


def test_retry_backoff_constants_match_reference():
    """The TS reference uses [5_000, 25_000] ms — Python uses seconds."""
    assert RETRY_BACKOFF_SECS == [5, 25]
