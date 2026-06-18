"""Pure argv builders: turn (master, outputs, encoder knobs) into ffmpeg argv.

Zero I/O — no subprocess, no filesystem, no RNG, no clocks, no global state.
Given identical inputs these functions return byte-identical argv lists, a hard
requirement for the render-safe pipeline: the two delivered streams are derived
from the SAME source with pinned encoder flags so they are frame-identical by
construction. Floats (CRF/quality knobs) are rounded to 6 decimals before being
baked into the args so equivalent inputs never drift in their string form.

The flags are FIXED by talking-head.md and honored verbatim:
  - Video: muted picture, native resolution (NO scale filter), -an mandatory.
  - Audio: voiceover only, libmp3lame.
"""

from __future__ import annotations


def _num(value: float | int) -> str:
    """Render an encoder knob deterministically.

    Ints stay bare (`18`); floats round to 6 decimals and drop trailing zeros so
    `18.0` and `18` produce identical argv strings.
    """
    if isinstance(value, int):
        return str(value)
    rounded = round(float(value), 6)
    if rounded == int(rounded):
        return str(int(rounded))
    return f"{rounded:.6f}".rstrip("0").rstrip(".")


def video_argv(
    master: str,
    video_out: str,
    crf: int | float = 18,
    preset: str = "slow",
) -> list[str]:
    """Build the muted-picture (video-only) ffmpeg invocation.

    -an mute is mandatory; there is NO scale filter — the picture is delivered at
    its native resolution.
    """
    return [
        "ffmpeg",
        "-nostdin",
        "-loglevel",
        "error",
        "-y",
        "-i",
        master,
        "-an",
        "-c:v",
        "libx264",
        "-crf",
        _num(crf),
        "-preset",
        preset,
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        video_out,
    ]


def audio_argv(
    master: str,
    audio_out: str,
    audio_quality: int | float = 2,
) -> list[str]:
    """Build the voiceover (audio-only) ffmpeg invocation."""
    return [
        "ffmpeg",
        "-nostdin",
        "-loglevel",
        "error",
        "-y",
        "-i",
        master,
        "-vn",
        "-c:a",
        "libmp3lame",
        "-q:a",
        _num(audio_quality),
        audio_out,
    ]
