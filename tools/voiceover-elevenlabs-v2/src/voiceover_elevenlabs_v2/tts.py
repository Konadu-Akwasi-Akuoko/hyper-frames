"""ElevenLabs Multilingual v2 Text-to-Speech wrapper.

Thin layer over the official `elevenlabs` SDK. Single responsibility:
take a string of text + voice/model/settings, return MP3 bytes. No I/O,
no retries — the calling code (core.py) handles file writes.

Defaults reflect v2 docs guidance for long-form narration:
- stability=0.4 (long-form sweet spot per docs; above 0.7 paradoxically
  produces more monotone delivery)
- similarity_boost=0.75
- style=0.35 (docs recommend 0.3–0.5 for natural expression; cap at 0.5
  by convention — above ~0.6 produces erratic emphasis on long-form)
- use_speaker_boost=True (default per SDK)
- language_code='en' (mitigates v2's tendency to switch accent/language
  on individual proper nouns it thinks belong to another language)
"""
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

# v2 per-request character limit per the official models page (~10 minutes
# of audio). Scripts past this need manual splitting; chunked + stitched
# generation is deferred to a later iteration.
V2_CHAR_LIMIT = 10_000


def synthesize(
    text: str,
    *,
    voice_id: str,
    model_id: str = "eleven_multilingual_v2",
    stability: float = 0.4,
    similarity_boost: float = 0.75,
    style: float = 0.35,
    use_speaker_boost: bool = True,
    language_code: str = "en",
    output_format: str = "mp3_44100_128",
    api_key: str,
) -> bytes:
    """Render text to MP3 bytes via ElevenLabs Multilingual v2.

    Raises:
        ValueError: if `text` exceeds the v2 per-request character limit.
        elevenlabs.core.api_error.ApiError: on API failures (caller decides retry).
    """
    if len(text) > V2_CHAR_LIMIT:
        raise ValueError(
            f"Text is {len(text)} characters; v2 character limit is {V2_CHAR_LIMIT}. "
            f"Split the script into parts and re-run."
        )

    client = ElevenLabs(api_key=api_key)
    audio_iter = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id=model_id,
        language_code=language_code,
        voice_settings=VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
            style=style,
            use_speaker_boost=use_speaker_boost,
        ),
        output_format=output_format,
    )
    return b"".join(audio_iter)
