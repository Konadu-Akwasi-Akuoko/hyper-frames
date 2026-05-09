"""End-to-end tests for the core orchestrator (with mocked SDK)."""
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from voiceover_elevenlabs_v3.core import generate


@pytest.fixture
def temp_video_dir(tmp_path: Path) -> Path:
    (tmp_path / "audio").mkdir()
    return tmp_path


def _scribe_response():
    return SimpleNamespace(
        language_code="eng",
        language_probability=0.95,
        text="Hello world",
        audio_duration_secs=1.5,
        words=[
            SimpleNamespace(text="Hello", type="word", start=0.0, end=0.5, logprob=0.0, speaker_id="speaker_0"),
            SimpleNamespace(text=" ", type="spacing", start=0.5, end=0.6),
            SimpleNamespace(text="world", type="word", start=0.6, end=1.5, logprob=0.0, speaker_id="speaker_0"),
        ],
    )


def test_generate_writes_audio_and_transcript(temp_video_dir: Path):
    text_path = temp_video_dir / "voiceover.txt"
    text_path.write_text("Hello world.")
    audio_path = temp_video_dir / "audio" / "voiceover.mp3"
    transcript_path = temp_video_dir / "transcript.json"

    with (
        patch("voiceover_elevenlabs_v3.core.synthesize") as mock_synth,
        patch("voiceover_elevenlabs_v3.core.transcribe") as mock_transcribe,
    ):
        mock_synth.return_value = b"\xff\xfb\x90\x00fake-mp3"
        mock_transcribe.return_value = _scribe_response()

        generate(
            text_path=text_path,
            audio_path=audio_path,
            transcript_path=transcript_path,
            voice_id="VOICE",
            api_key="sk_test",
        )

        assert audio_path.read_bytes() == b"\xff\xfb\x90\x00fake-mp3"
        transcript = json.loads(transcript_path.read_text())
        assert transcript["audio_duration_secs"] == 1.5
        assert transcript["language_code"] == "eng"
        assert len(transcript["words"]) == 3


def test_generate_skips_transcript_when_disabled(temp_video_dir: Path):
    text_path = temp_video_dir / "voiceover.txt"
    text_path.write_text("hi")
    audio_path = temp_video_dir / "audio" / "voiceover.mp3"
    transcript_path = temp_video_dir / "transcript.json"

    with (
        patch("voiceover_elevenlabs_v3.core.synthesize") as mock_synth,
        patch("voiceover_elevenlabs_v3.core.transcribe") as mock_transcribe,
    ):
        mock_synth.return_value = b"audio"

        generate(
            text_path=text_path,
            audio_path=audio_path,
            transcript_path=transcript_path,
            voice_id="V",
            api_key="sk",
            generate_transcript=False,
        )

        assert audio_path.exists()
        assert not transcript_path.exists()
        mock_transcribe.assert_not_called()


def test_generate_creates_audio_parent_dir(tmp_path: Path):
    text_path = tmp_path / "voiceover.txt"
    text_path.write_text("hi")
    audio_path = tmp_path / "fresh-dir" / "voiceover.mp3"
    transcript_path = tmp_path / "transcript.json"

    with (
        patch("voiceover_elevenlabs_v3.core.synthesize") as mock_synth,
        patch("voiceover_elevenlabs_v3.core.transcribe") as mock_transcribe,
    ):
        mock_synth.return_value = b"a"
        mock_transcribe.return_value = _scribe_response()

        generate(
            text_path=text_path,
            audio_path=audio_path,
            transcript_path=transcript_path,
            voice_id="V",
            api_key="sk",
        )

        assert audio_path.exists()


def test_generate_overwrites_existing_files(temp_video_dir: Path):
    text_path = temp_video_dir / "voiceover.txt"
    text_path.write_text("hi")
    audio_path = temp_video_dir / "audio" / "voiceover.mp3"
    transcript_path = temp_video_dir / "transcript.json"
    audio_path.write_bytes(b"old-audio")
    transcript_path.write_text("{}")

    with (
        patch("voiceover_elevenlabs_v3.core.synthesize") as mock_synth,
        patch("voiceover_elevenlabs_v3.core.transcribe") as mock_transcribe,
    ):
        mock_synth.return_value = b"new-audio"
        mock_transcribe.return_value = _scribe_response()

        generate(
            text_path=text_path,
            audio_path=audio_path,
            transcript_path=transcript_path,
            voice_id="V",
            api_key="sk",
        )

        assert audio_path.read_bytes() == b"new-audio"
        assert json.loads(transcript_path.read_text())["language_code"] == "eng"
