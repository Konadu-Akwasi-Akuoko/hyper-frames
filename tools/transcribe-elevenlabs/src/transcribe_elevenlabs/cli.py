"""Command-line entry point for transcribe-elevenlabs.

Usage:
    transcribe-elevenlabs audio/raw.mp3
    transcribe-elevenlabs audio/raw.mp3 -o transcript.json
    transcribe-elevenlabs audio/raw.mp3 --dry-run
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv

from transcribe_elevenlabs.scribe import transcribe
from transcribe_elevenlabs.transcript import to_transcript

SCRIBE_USD_PER_HOUR = 0.40


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="transcribe-elevenlabs",
        description="Transcribe an audio file to project transcript.json via ElevenLabs Scribe v2.",
    )
    parser.add_argument("input_path", type=Path, help="Path to the audio file (mp3/wav/flac/m4a).")
    parser.add_argument("-o", "--output", type=Path, default=Path("transcript.json"),
                        help="Where to write transcript.json (default: ./transcript.json).")
    parser.add_argument("--no-reencode", action="store_true",
                        help="Skip the mono-16k-64kbps re-encode pass and upload the file as-is.")
    parser.add_argument("--dry-run", action="store_true",
                        help="ffprobe the input and print duration + cost estimate without calling Scribe.")
    return parser


def _probe_duration_secs(path: Path) -> float:
    """Return audio duration via ffprobe. Raises CalledProcessError on failure."""
    out = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True, capture_output=True, text=True,
    )
    return float(out.stdout.strip())


def _reencode_for_upload(src: Path, dst: Path) -> None:
    """Re-encode to mono 16 kHz 64 kbps MP3 to shrink upload size.

    Scribe accepts the original file too — this is purely an upload-size
    optimization. Mirrors clean-audio/scripts/encode-for-upload.ts.
    """
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(src),
            "-ac", "1",
            "-ar", "16000",
            "-b:a", "64k",
            "-codec:a", "libmp3lame",
            str(dst),
        ],
        check=True,
    )


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.input_path.exists():
        print(f"Input not found: {args.input_path}", file=sys.stderr)
        return 2

    try:
        duration_secs = _probe_duration_secs(args.input_path)
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"ffprobe failed on {args.input_path}: {e}", file=sys.stderr)
        return 2

    minutes = duration_secs / 60
    cost_usd = duration_secs / 3600 * SCRIBE_USD_PER_HOUR
    print(
        f"{args.input_path} · {minutes:.2f} min · ~${cost_usd:.3f} Scribe v2",
        file=sys.stderr,
    )

    if args.dry_run:
        return 0

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print(
            "ELEVENLABS_API_KEY is not set. Add it to .env at the repo root.",
            file=sys.stderr,
        )
        return 2

    upload_path = args.input_path
    tmp_dir: tempfile.TemporaryDirectory[str] | None = None
    if not args.no_reencode:
        tmp_dir = tempfile.TemporaryDirectory(prefix="transcribe-elevenlabs-")
        upload_path = Path(tmp_dir.name) / "upload.mp3"
        try:
            _reencode_for_upload(args.input_path, upload_path)
        except subprocess.CalledProcessError as e:
            print(f"ffmpeg re-encode failed: {e}", file=sys.stderr)
            if tmp_dir:
                tmp_dir.cleanup()
            return 2
        print(
            f"re-encoded → {upload_path.stat().st_size / 1024:.1f} KB",
            file=sys.stderr,
        )

    try:
        response = transcribe(upload_path, api_key=api_key)
        transcript_data = to_transcript(response)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"API error: {e}", file=sys.stderr)
        return 1
    finally:
        if tmp_dir:
            tmp_dir.cleanup()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(transcript_data, indent=2))

    word_count = sum(1 for w in transcript_data["words"] if w["type"] == "word")
    print(f"Transcript → {args.output} ({word_count} words)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
