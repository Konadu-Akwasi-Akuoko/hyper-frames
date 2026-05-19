"""ElevenLabs Scribe v2 wrapper.

Thin layer over the official `elevenlabs` SDK. Mirrors the defensive choices
in tools/voiceover-elevenlabs-v2/scribe.py:
- Reject multichannel responses (we only support single-channel narration).
- Reject webhook responses (we need the transcript inline).
"""
from pathlib import Path

from elevenlabs.client import ElevenLabs


def transcribe(audio_path: Path, *, api_key: str) -> object:
    """Transcribe an audio file with Scribe v2 at word granularity.

    Returns the raw SDK response (already snake_case in the Python SDK).
    Use `transcript.to_transcript` to convert to the project's dict shape.

    Raises:
        FileNotFoundError: if `audio_path` doesn't exist.
        ValueError: if the response is multichannel or webhook-mode (unsupported).
        elevenlabs.core.api_error.ApiError: on API failures.
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"Input audio not found: {audio_path}")

    client = ElevenLabs(api_key=api_key)
    with audio_path.open("rb") as f:
        response = client.speech_to_text.convert(
            model_id="scribe_v2",
            file=f,
            timestamps_granularity="word",
            diarize=True,
            tag_audio_events=True,
        )

    if hasattr(response, "transcripts"):
        raise ValueError(
            "Multichannel transcripts are not supported. Provide single-channel audio."
        )
    if hasattr(response, "request_id"):
        raise ValueError(
            "Webhook mode is not supported — the tool needs the transcript inline."
        )

    return response
