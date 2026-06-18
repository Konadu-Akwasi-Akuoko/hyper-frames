"""derive-streams CLI: one cut master into two frame-identical delivered streams.

Takes the talking-head cut master and emits BOTH delivered streams in one
deterministic run: a muted picture (native resolution, no scale filter) and the
voiceover audio. Both are derived from the SAME source with pinned encoder flags
(see `argv.py`), so they are frame-identical by construction.

This module owns the impure parts — ffprobe stream assertion and the two
subprocess.run calls. The argv math lives in the zero-I/O `argv` module so it can
be unit-tested without touching ffmpeg or the filesystem.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from . import argv as argvmod

TOOL = "derive-streams"


def _probe_streams(master: str) -> tuple[int, int]:
    """Return (video_stream_count, audio_stream_count) for `master` via ffprobe."""
    proc = subprocess.run(
        [
            "ffprobe",
            "-loglevel",
            "error",
            "-show_entries",
            "stream=codec_type",
            "-of",
            "json",
            master,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(proc.stdout or "{}")
    streams = data.get("streams", [])
    video = sum(1 for s in streams if s.get("codec_type") == "video")
    audio = sum(1 for s in streams if s.get("codec_type") == "audio")
    return video, audio


def _probe_duration(path: str) -> float:
    """Return the format duration of `path` in seconds via ffprobe."""
    proc = subprocess.run(
        [
            "ffprobe",
            "-loglevel",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(proc.stdout or "{}")
    return float(data.get("format", {}).get("duration", 0.0))


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Derive both delivered streams from a cut master in one "
        "deterministic, frame-identical run."
    )
    ap.add_argument("master", help="cut master (.mov) — exactly 1 video + 1 audio")
    ap.add_argument(
        "--video-out",
        required=True,
        help="muted picture out (e.g. assets/video/talking-head.mp4)",
    )
    ap.add_argument(
        "--audio-out",
        required=True,
        help="voiceover out (e.g. audio/voiceover.mp3)",
    )
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--preset", default="slow")
    ap.add_argument("--audio-quality", type=int, default=2)
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="print both ffmpeg argv lists and exit without running anything",
    )
    args = ap.parse_args()

    vargv = argvmod.video_argv(
        args.master, args.video_out, args.crf, args.preset
    )
    aargv = argvmod.audio_argv(args.master, args.audio_out, args.audio_quality)

    if args.dry_run:
        print(f"[{TOOL}] video: {' '.join(vargv)}")
        print(f"[{TOOL}] audio: {' '.join(aargv)}")
        return

    video, audio = _probe_streams(args.master)
    if video != 1 or audio != 1:
        sys.exit(
            f"[{TOOL}] master must have exactly 1 video + 1 audio stream; "
            f"found {video} video + {audio} audio in {args.master}"
        )

    Path(args.video_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.audio_out).parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(vargv, check=True)
    subprocess.run(aargv, check=True)

    vdur = _probe_duration(args.video_out)
    adur = _probe_duration(args.audio_out)
    print(
        f"[{TOOL}] derived 2 streams from {args.master}\n"
        f"[{TOOL}]   video {args.video_out} ({vdur:.3f}s, muted)\n"
        f"[{TOOL}]   audio {args.audio_out} ({adur:.3f}s)\n"
        f"[{TOOL}]   durations match within {abs(vdur - adur):.3f}s"
    )


if __name__ == "__main__":
    main()
