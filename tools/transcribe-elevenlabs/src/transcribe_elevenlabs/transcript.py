"""Schema mapping: ElevenLabs Scribe v2 SDK response → project transcript.json.

The Python SDK already returns snake_case fields (matching the project's
transcript.json shape). This module's job is the dict conversion and
defensive coercion of missing per-word timestamps.
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
    """Map the SDK's Scribe v2 response into the project's transcript.json shape.

    - Missing audio_duration_secs → ValueError (cut-decider needs it for bounds).
    - Missing per-word start/end → coerced to 0.0. Scribe always emits both
      for word/spacing/audio_event types in practice; the defensive default
      keeps the file parseable rather than crashing here.
    """
    duration = getattr(response, "audio_duration_secs", None)
    if duration is None:
        raise ValueError(
            "Scribe response is missing audio_duration_secs — cannot validate cuts against duration."
        )

    words: list[TranscriptWord] = []
    for w in response.words:  # type: ignore[attr-defined]
        if w.type == "word":
            entry: TranscriptWord = {
                "text": w.text,
                "type": "word",
                "start": w.start if w.start is not None else 0.0,
                "end": w.end if w.end is not None else 0.0,
                "logprob": w.logprob,
            }
            speaker = getattr(w, "speaker_id", None)
            if speaker is not None:
                entry["speaker_id"] = speaker
            words.append(entry)
        else:
            words.append({
                "text": w.text,
                "type": w.type,
                "start": w.start if w.start is not None else 0.0,
                "end": w.end if w.end is not None else 0.0,
            })

    return {
        "audio_duration_secs": duration,
        "language_code": response.language_code,  # type: ignore[attr-defined]
        "language_probability": response.language_probability,  # type: ignore[attr-defined]
        "text": response.text,  # type: ignore[attr-defined]
        "words": words,
    }
