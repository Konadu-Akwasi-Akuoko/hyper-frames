"""Shared test fixtures.

The `scribe_response_minimal` fixture mimics the Python SDK's Scribe v2
response shape using a plain SimpleNamespace. We don't import the SDK's
response class because pinning to its internal types makes tests fragile
across SDK versions; the wrapper code only reads the snake_case attribute
names listed here (which match `SpeechToTextChunkResponseModel`).
"""
from types import SimpleNamespace

import pytest


def _word(text: str, type_: str, start: float, end: float, logprob: float = 0.0, speaker_id: str | None = "speaker_0"):
    """Build a SimpleNamespace mimicking one entry in Scribe's words array."""
    base = {
        "text": text,
        "type": type_,
        "start": start,
        "end": end,
        "logprob": logprob,
    }
    if speaker_id is not None:
        base["speaker_id"] = speaker_id
    return SimpleNamespace(**base)


@pytest.fixture
def scribe_response_minimal():
    """A minimal valid Scribe v2 response: 'You open' (2 words + 1 spacing)."""
    return SimpleNamespace(
        language_code="eng",
        language_probability=0.95,
        text="You open",
        audio_duration_secs=0.48,
        words=[
            _word("You", "word", 0.18, 0.26, logprob=-7.15e-7),
            _word(" ", "spacing", 0.26, 0.27, speaker_id=None),
            _word("open", "word", 0.27, 0.48, logprob=-2.03e-6),
        ],
    )


@pytest.fixture
def scribe_response_with_audio_event():
    """Includes an audio_event word type — the third 'type' Scribe emits."""
    return SimpleNamespace(
        language_code="eng",
        language_probability=0.92,
        text="You open",
        audio_duration_secs=0.6,
        words=[
            _word("You", "word", 0.18, 0.26, logprob=0.0),
            _word("[breath]", "audio_event", 0.26, 0.4, speaker_id=None),
            _word("open", "word", 0.4, 0.6, logprob=0.0),
        ],
    )
