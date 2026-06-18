"""Thin ffmpeg/ffprobe subprocess wrapper. Owns process I/O; no cut math here.

Encoder flags are pinned (no RNG, no wall-clock) so the encode is reproducible
for the render-safe pipeline. The cut boundaries themselves come from
`segments.py`, already rounded to 6 decimals, and are written to a
filter_complex_script file so the graph text — and therefore the libx264 input
— is byte-identical across runs.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass


class StreamError(RuntimeError):
    """Raised when the source's stream set doesn't match the requested mode."""


@dataclass(frozen=True)
class Probe:
    """ffprobe result: stream counts, duration, and detected frame rate."""

    n_video: int
    n_audio: int
    duration: float
    fps: float


def _run(argv: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(argv, capture_output=True, check=True)


def _parse_fps(rate: str) -> float:
    """Parse an ffprobe r_frame_rate like '30000/1001' into a float."""
    rate = (rate or "").strip()
    if not rate or rate == "0/0":
        return 0.0
    if "/" in rate:
        num, den = rate.split("/", 1)
        den_f = float(den)
        return float(num) / den_f if den_f else 0.0
    return float(rate)


def probe(path: str) -> Probe:
    """Probe `path` for video/audio stream counts, duration, and fps."""
    proc = _run(
        [
            "ffprobe", "-loglevel", "error",
            "-print_format", "json",
            "-show_streams", "-show_format",
            path,
        ]
    )
    data = json.loads(proc.stdout)
    streams = data.get("streams", [])
    video = [s for s in streams if s.get("codec_type") == "video"]
    audio = [s for s in streams if s.get("codec_type") == "audio"]

    fps = 0.0
    if video:
        fps = _parse_fps(
            video[0].get("avg_frame_rate") or video[0].get("r_frame_rate") or ""
        )
        if fps <= 0:
            fps = _parse_fps(video[0].get("r_frame_rate") or "")

    duration = 0.0
    fmt_dur = data.get("format", {}).get("duration")
    if fmt_dur is not None:
        duration = float(fmt_dur)
    if duration <= 0:
        for s in streams:
            if s.get("duration"):
                duration = max(duration, float(s["duration"]))

    return Probe(
        n_video=len(video),
        n_audio=len(audio),
        duration=duration,
        fps=fps,
    )


def assert_streams(p: Probe, mode: str) -> None:
    """Fail loud unless the stream set matches the requested mode."""
    if mode == "video":
        if p.n_video != 1 or p.n_audio != 1:
            raise StreamError(
                "video mode requires exactly 1 video + 1 audio stream, found "
                f"{p.n_video} video / {p.n_audio} audio"
            )
    elif mode == "audio":
        if p.n_audio != 1:
            raise StreamError(
                f"audio mode requires exactly 1 audio stream, found {p.n_audio}"
            )
    else:
        raise ValueError(f"unknown mode: {mode!r}")


def infer_mode(p: Probe) -> str:
    """Infer the cut mode from the stream set: video present -> video."""
    return "video" if p.n_video >= 1 else "audio"


def build_argv(
    src: str,
    graph_path: str,
    out: str,
    mode: str,
    crf: int,
    preset: str,
) -> list[str]:
    """Assemble the pinned ffmpeg argv for a cut master (video or audio mode)."""
    base = ["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", src,
            "-filter_complex_script", graph_path]
    if mode == "video":
        return base + [
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-crf", str(crf), "-preset", preset,
            "-pix_fmt", "yuv420p",
            "-c:a", "pcm_s16le",
            "-movflags", "+faststart",
            out,
        ]
    return base + [
        "-map", "[a]",
        "-c:a", "libmp3lame", "-q:a", "2",
        out,
    ]


def run_cut(argv: list[str]) -> None:
    """Invoke ffmpeg for the cut. Raises CalledProcessError on failure."""
    _run(argv)


def extract_audio_argv(
    src: str,
    out: str,
    bitrate: str,
    mono: bool,
    ar: int | None,
) -> list[str]:
    """Assemble the ffmpeg argv to extract the audio track to an mp3."""
    argv = ["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", src,
            "-vn", "-c:a", "libmp3lame", "-b:a", bitrate]
    if mono:
        argv += ["-ac", "1"]
    if ar is not None:
        argv += ["-ar", str(ar)]
    argv.append(out)
    return argv


def run_extract_audio(argv: list[str]) -> None:
    """Invoke ffmpeg to extract audio. Raises CalledProcessError on failure."""
    _run(argv)
