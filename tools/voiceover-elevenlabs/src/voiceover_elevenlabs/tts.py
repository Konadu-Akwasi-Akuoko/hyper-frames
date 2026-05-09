"""ElevenLabs v3 Text-to-Speech wrapper.

Thin layer over the official `elevenlabs` SDK. Single responsibility:
take a string of text + voice/model/settings, return MP3 bytes. No I/O,
no retries — the calling code (core.py) handles file writes.
"""
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

# v3 per-request character limit. Working assumption — ElevenLabs docs don't
# state a number for v3 specifically. 10k is comfortably under any plausible
# limit for the scripts this project sends (5-min ≈ 5k, 7-min ≈ 7k).
V3_CHAR_LIMIT = 10_000


def synthesize(
    text: str,
    *,
    voice_id: str,
    model_id: str = "eleven_v3",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    output_format: str = "mp3_44100_128",
    api_key: str,
) -> bytes:
    """Render text to MP3 bytes via ElevenLabs v3.

    Raises:
        ValueError: if `text` exceeds the v3 per-request character limit.
        elevenlabs.core.api_error.ApiError: on API failures (caller decides retry).
    """
    if len(text) > V3_CHAR_LIMIT:
        raise ValueError(
            f"Text is {len(text)} characters; v3 character limit is {V3_CHAR_LIMIT}. "
            f"Split the script into parts and re-run."
        )

    client = ElevenLabs(api_key=api_key)
    audio_iter = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id=model_id,
        voice_settings=VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
        ),
        output_format=output_format,
    )
    return b"".join(audio_iter)
