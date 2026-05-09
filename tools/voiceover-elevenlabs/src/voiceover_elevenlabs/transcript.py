"""Schema mapping: ElevenLabs Scribe v2 SDK response → project transcript.json.

The Python SDK already returns snake_case fields (matching the project's
transcript.json shape). This module's job is the dict conversion, defensive
coercion of missing per-word timestamps, and stripping fields the project
schema doesn't carry (`channel_index`, `additional_formats`, `transcription_id`,
`entities`, per-word `characters`).
"""
from typing import Literal, TypedDict


class TranscriptWord(TypedDict, total=False):
    text: str
    type: Literal["word", "spacing", "audio_event"]
    start: float
    end: float
    logprob: float
    speaker_id: str


class Transcript(TypedDict):
    audio_duration_secs: float
    language_code: str
    language_probability: float
    text: str
    words: list[TranscriptWord]


def to_transcript(response: object) -> Transcript:
    """Map the SDK's Scribe v2 response into the project's snake_case shape.

    Implemented in Task 4.
    """
    raise NotImplementedError
