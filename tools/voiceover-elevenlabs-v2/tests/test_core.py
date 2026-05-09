"""Unit tests for the v2 core orchestrator."""
import json
from unittest.mock import patch

from voiceover_elevenlabs_v2.core import generate


def test_generate_writes_audio_and_transcript(tmp_path, scribe_response_minimal):
    text_path = tmp_path / "voiceover.txt"
    text_path.write_text("You open a text editor.")
    audio_path = tmp_path / "audio" / "voiceover.mp3"
    transcript_path = tmp_path / "transcript.json"

    with patch("voiceover_elevenlabs_v2.core.synthesize", return_value=b"FAKE_MP3") as mock_tts, \
         patch("voiceover_elevenlabs_v2.core.transcribe", return_value=scribe_response_minimal) as mock_scribe:
        generate(
            text_path=text_path,
            audio_path=audio_path,
            transcript_path=transcript_path,
            voice_id="V",
            api_key="sk_test",
        )

    # Audio: written, parent dir created
    assert audio_path.exists()
    assert audio_path.read_bytes() == b"FAKE_MP3"

    # Transcript: written as JSON matching project schema
    transcript = json.loads(transcript_path.read_text())
    assert transcript["audio_duration_secs"] == 0.48
    assert transcript["text"] == "You open"
    assert len(transcript["words"]) == 3

    # synthesize received the text and v2 defaults via kwargs
    tts_kwargs = mock_tts.call_args.kwargs
    assert tts_kwargs["voice_id"] == "V"
    assert tts_kwargs["api_key"] == "sk_test"
    assert tts_kwargs["model_id"] == "eleven_multilingual_v2"
    assert tts_kwargs["language_code"] == "en"
    assert tts_kwargs["stability"] == 0.4
    assert tts_kwargs["similarity_boost"] == 0.75
    assert tts_kwargs["style"] == 0.35
    assert tts_kwargs["use_speaker_boost"] is True

    # Scribe was called on the rendered audio
    mock_scribe.assert_called_once()
    assert mock_scribe.call_args.args[0] == audio_path


def test_generate_skips_transcript_when_disabled(tmp_path):
    text_path = tmp_path / "voiceover.txt"
    text_path.write_text("hi")
    audio_path = tmp_path / "audio.mp3"
    transcript_path = tmp_path / "transcript.json"

    with patch("voiceover_elevenlabs_v2.core.synthesize", return_value=b"X") as _, \
         patch("voiceover_elevenlabs_v2.core.transcribe") as mock_scribe:
        generate(
            text_path=text_path,
            audio_path=audio_path,
            transcript_path=transcript_path,
            voice_id="V",
            api_key="sk_test",
            generate_transcript=False,
        )

    assert audio_path.exists()
    assert not transcript_path.exists()
    mock_scribe.assert_not_called()


def test_generate_forwards_custom_voice_settings(tmp_path, scribe_response_minimal):
    text_path = tmp_path / "voiceover.txt"
    text_path.write_text("x")
    audio_path = tmp_path / "audio.mp3"
    transcript_path = tmp_path / "t.json"

    with patch("voiceover_elevenlabs_v2.core.synthesize", return_value=b"X") as mock_tts, \
         patch("voiceover_elevenlabs_v2.core.transcribe", return_value=scribe_response_minimal):
        generate(
            text_path=text_path,
            audio_path=audio_path,
            transcript_path=transcript_path,
            voice_id="V",
            api_key="sk_test",
            stability=0.5,
            similarity_boost=0.8,
            style=0.5,
            use_speaker_boost=False,
            language_code="es",
        )

    tts_kwargs = mock_tts.call_args.kwargs
    assert tts_kwargs["stability"] == 0.5
    assert tts_kwargs["similarity_boost"] == 0.8
    assert tts_kwargs["style"] == 0.5
    assert tts_kwargs["use_speaker_boost"] is False
    assert tts_kwargs["language_code"] == "es"
