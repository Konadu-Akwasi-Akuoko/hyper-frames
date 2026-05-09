"""High-level orchestrator: text file → audio + transcript on disk.

Orchestrates the two API calls (Multilingual v2 TTS, then Scribe v2 on the
rendered audio) and the schema mapping. Intentionally simple — no retry
logic beyond what the wrappers do; no parallelism (Scribe needs the audio).
"""
import json
from pathlib import Path

from voiceover_elevenlabs_v2.scribe import transcribe
from voiceover_elevenlabs_v2.transcript import to_transcript
from voiceover_elevenlabs_v2.tts import synthesize


def generate(
    *,
    text_path: Path,
    audio_path: Path,
    transcript_path: Path,
    voice_id: str,
    api_key: str,
    model_id: str = "eleven_multilingual_v2",
    stability: float = 0.4,
    similarity_boost: float = 0.75,
    style: float = 0.35,
    use_speaker_boost: bool = True,
    language_code: str = "en",
    output_format: str = "mp3_44100_128",
    generate_transcript: bool = True,
) -> None:
    """Read text, render audio via v2, transcribe via Scribe v2, write both files.

    Overwrites existing files at `audio_path` and `transcript_path` without
    prompting. Creates parent directories as needed.
    """
    text = text_path.read_text()

    audio_bytes = synthesize(
        text,
        voice_id=voice_id,
        model_id=model_id,
        stability=stability,
        similarity_boost=similarity_boost,
        style=style,
        use_speaker_boost=use_speaker_boost,
        language_code=language_code,
        output_format=output_format,
        api_key=api_key,
    )
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    audio_path.write_bytes(audio_bytes)

    if not generate_transcript:
        return

    response = transcribe(audio_path, api_key=api_key)
    transcript_data = to_transcript(response)
    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    transcript_path.write_text(json.dumps(transcript_data, indent=2))
