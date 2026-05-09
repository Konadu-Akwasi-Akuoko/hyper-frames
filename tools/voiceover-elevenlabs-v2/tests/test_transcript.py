"""Unit tests for the Scribe v2 → transcript.json mapping."""
from types import SimpleNamespace

import pytest

from voiceover_elevenlabs_v2.transcript import to_transcript


def test_minimal_response_maps_to_project_shape(scribe_response_minimal):
    out = to_transcript(scribe_response_minimal)
    assert out["audio_duration_secs"] == 0.48
    assert out["language_code"] == "eng"
    assert out["language_probability"] == 0.95
    assert out["text"] == "You open"
    assert len(out["words"]) == 3


def test_word_entries_have_full_shape(scribe_response_minimal):
    out = to_transcript(scribe_response_minimal)
    word = out["words"][0]
    assert word["text"] == "You"
    assert word["type"] == "word"
    assert word["start"] == 0.18
    assert word["end"] == 0.26
    assert word["logprob"] == -7.15e-7
    assert word["speaker_id"] == "speaker_0"


def test_spacing_entries_omit_logprob_and_speaker(scribe_response_minimal):
    out = to_transcript(scribe_response_minimal)
    spacing = out["words"][1]
    assert spacing["text"] == " "
    assert spacing["type"] == "spacing"
    assert spacing["start"] == 0.26
    assert spacing["end"] == 0.27
    assert "logprob" not in spacing
    assert "speaker_id" not in spacing


def test_audio_event_entries_treated_like_spacing(scribe_response_with_audio_event):
    out = to_transcript(scribe_response_with_audio_event)
    event = out["words"][1]
    assert event["type"] == "audio_event"
    assert "logprob" not in event
    assert "speaker_id" not in event


def test_missing_audio_duration_raises():
    """Match the TS reference: missing audio_duration_secs is a hard error."""
    bad = SimpleNamespace(
        language_code="eng",
        language_probability=0.9,
        text="x",
        audio_duration_secs=None,
        words=[],
    )
    with pytest.raises(ValueError, match="audio_duration_secs"):
        to_transcript(bad)


def test_undefined_word_timestamps_coerced_to_zero():
    """Match the TS reference: missing per-word start/end → 0.0 (defensive)."""
    response = SimpleNamespace(
        language_code="eng",
        language_probability=0.9,
        text="x",
        audio_duration_secs=1.0,
        words=[
            SimpleNamespace(
                text="x",
                type="word",
                start=None,
                end=None,
                logprob=0.0,
                speaker_id="speaker_0",
            ),
        ],
    )
    out = to_transcript(response)
    assert out["words"][0]["start"] == 0.0
    assert out["words"][0]["end"] == 0.0
