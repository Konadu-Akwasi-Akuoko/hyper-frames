"""Command-line entry point for voiceover-elevenlabs-v2.

Usage:
    voiceover-elevenlabs-v2 voiceover.txt
    voiceover-elevenlabs-v2 voiceover.txt --dry-run
    voiceover-elevenlabs-v2 voiceover.txt --no-transcript -o audio/v.mp3
"""
import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from voiceover_elevenlabs_v2.core import generate
from voiceover_elevenlabs_v2.tts import V2_CHAR_LIMIT

# v2 cost per 1k characters in credits. Approximate — verify against actual
# billing on the first real run and adjust if needed.
V2_CREDITS_PER_1K_CHARS = 15
# Scribe v2 cost in USD per hour of audio.
SCRIBE_USD_PER_HOUR = 0.40
# Words per minute (project house style — 170 wpm per CLAUDE.md).
WORDS_PER_MINUTE = 170


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="voiceover-elevenlabs-v2",
        description="Generate Multilingual v2 voiceover + Scribe v2 transcript from an annotated script.",
    )
    parser.add_argument("input_path", type=Path, help="Path to the annotated script (e.g. voiceover.txt).")
    parser.add_argument("-o", "--output-audio", type=Path, default=Path("audio/voiceover.mp3"))
    parser.add_argument("--output-transcript", type=Path, default=Path("transcript.json"))
    parser.add_argument("--voice-id", default="JBFqnCBsd6RMkjVDRZzb")
    parser.add_argument("--model", default="eleven_multilingual_v2")
    parser.add_argument("--stability", type=float, default=0.4)
    parser.add_argument("--similarity-boost", type=float, default=0.75)
    parser.add_argument("--style", type=float, default=0.35)
    parser.add_argument("--use-speaker-boost", dest="use_speaker_boost", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--language-code", default="en")
    parser.add_argument("--no-transcript", dest="generate_transcript", action="store_false")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print char count + cost estimate without calling any API.")
    return parser


def _estimate_cost(text: str) -> str:
    chars = len(text)
    words = len(text.split())
    minutes = words / WORDS_PER_MINUTE
    credits = chars * V2_CREDITS_PER_1K_CHARS / 1000
    scribe_usd = minutes * SCRIBE_USD_PER_HOUR / 60
    return (
        f"{chars} characters · ~{words} words · ~{minutes:.1f} min audio\n"
        f"v2 TTS: ~{credits:.0f} credits (≈ half v3's rate)\n"
        f"Scribe v2: ~${scribe_usd:.2f}"
    )


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.input_path.exists():
        print(f"Input not found: {args.input_path}", file=sys.stderr)
        return 2

    text = args.input_path.read_text()

    if args.dry_run:
        print(_estimate_cost(text))
        return 0

    if len(text) > V2_CHAR_LIMIT:
        print(
            f"Input is {len(text)} chars; v2's per-request limit is 10,000.\n"
            f"Split voiceover.txt into parts and run again. Chunked + stitched\n"
            f"mode is not yet implemented (see design doc §2 'Out of scope').",
            file=sys.stderr,
        )
        return 2

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print(
            "ELEVENLABS_API_KEY is not set. Add it to .env at the repo root.",
            file=sys.stderr,
        )
        return 2

    print(_estimate_cost(text))
    print(f"Generating audio → {args.output_audio}", file=sys.stderr)

    try:
        generate(
            text_path=args.input_path,
            audio_path=args.output_audio,
            transcript_path=args.output_transcript,
            voice_id=args.voice_id,
            api_key=api_key,
            model_id=args.model,
            stability=args.stability,
            similarity_boost=args.similarity_boost,
            style=args.style,
            use_speaker_boost=args.use_speaker_boost,
            language_code=args.language_code,
            generate_transcript=args.generate_transcript,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"API error: {e}", file=sys.stderr)
        return 1

    print(f"Audio    → {args.output_audio}")
    if args.generate_transcript:
        print(f"Transcript → {args.output_transcript}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
