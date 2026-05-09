"""Command-line entry point.

Usage:
    voiceover-elevenlabs voiceover.txt
    voiceover-elevenlabs voiceover.txt --dry-run
    voiceover-elevenlabs voiceover.txt --no-transcript -o audio/v.mp3
"""
import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from voiceover_elevenlabs_v3.core import generate

# v3 cost per 1k characters in credits. Used only for the dry-run estimate.
V3_CREDITS_PER_1K_CHARS = 30
# Scribe v2 cost in USD per hour of audio. Used only for the dry-run estimate.
SCRIBE_USD_PER_HOUR = 0.40
# Words per minute (project house style — 170 wpm per CLAUDE.md).
WORDS_PER_MINUTE = 170


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="voiceover-elevenlabs",
        description="Generate v3 voiceover + Scribe v2 transcript from an annotated script.",
    )
    parser.add_argument("input_path", type=Path, help="Path to the annotated script (e.g. voiceover.txt).")
    parser.add_argument("-o", "--output-audio", type=Path, default=Path("audio/voiceover.mp3"))
    parser.add_argument("--output-transcript", type=Path, default=Path("transcript.json"))
    parser.add_argument("--voice-id", default="UgBBYS2sOqTuMpoF3BR0")
    parser.add_argument("--model", default="eleven_v3")
    parser.add_argument("--stability", type=float, default=0.5)
    parser.add_argument("--similarity-boost", type=float, default=0.75)
    parser.add_argument("--no-transcript", dest="generate_transcript", action="store_false")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print char count + cost estimate without calling any API.")
    return parser


def _estimate_cost(text: str) -> str:
    chars = len(text)
    words = len(text.split())
    minutes = words / WORDS_PER_MINUTE
    credits = chars * V3_CREDITS_PER_1K_CHARS / 1000
    scribe_usd = minutes * SCRIBE_USD_PER_HOUR / 60
    return (
        f"{chars} characters · ~{words} words · ~{minutes:.1f} min audio\n"
        f"v3 TTS: ~{credits:.0f} credits\n"
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
