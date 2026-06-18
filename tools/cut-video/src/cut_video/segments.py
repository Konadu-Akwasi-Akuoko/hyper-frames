"""Pure keep-window math + ffmpeg filtergraph synthesis. No I/O, no subprocess.

All functions here are deterministic — no randomness, no wall-clock, no global
state — so cut-video produces a byte-identical filtergraph (and therefore an
identical encode under pinned encoder flags) for identical input. This is a hard
requirement for the render-safe pipeline. Every boundary float is rounded to 6
decimals before it is baked into the graph text so the generated
filter_complex_script is byte-stable across runs and machines.
"""

from __future__ import annotations

from typing import NamedTuple

ROUND = 6


class Keep(NamedTuple):
    """A kept (retained) window in source time, seconds."""

    start: float
    end: float

    @property
    def duration(self) -> float:
        return self.end - self.start


class WholeDurationRemovedError(ValueError):
    """Raised when the cuts cover the entire source — nothing is kept."""


def _r(value: float) -> float:
    """Round to the graph's fixed precision (6 decimals)."""
    return round(float(value), ROUND)


def coalesce_cuts(
    cuts: list[tuple[float, float]],
) -> list[tuple[float, float]]:
    """Sort removed spans by start and merge overlapping/touching ones.

    Adjacent spans (where one ends exactly where the next begins) are merged so
    no zero-length keep can ever be emitted between them. Zero/negative-length
    removed spans are dropped. Returns disjoint, sorted [start, end] spans.
    """
    spans = sorted(
        ((float(s), float(e)) for s, e in cuts if e > s),
        key=lambda se: se[0],
    )
    merged: list[tuple[float, float]] = []
    for start, end in spans:
        if merged and start <= merged[-1][1]:
            prev_s, prev_e = merged[-1]
            merged[-1] = (prev_s, max(prev_e, end))
        else:
            merged.append((start, end))
    return merged


def keep_windows(
    cuts: list[tuple[float, float]],
    duration: float,
    fps: float,
    epsilon_frames: float = 1.0,
    snap: bool = False,
) -> list[Keep]:
    """Complement the removed spans into the kept windows over [0, duration].

    1. Coalesce removed spans (sort + merge touching/overlapping).
    2. Walk a cursor from 0: emit keep [cursor, cut.start] then cursor = cut.end.
    3. Final keep [last_cut.end, duration].
    4. Optionally snap each boundary to the nearest integer frame time.
    5. Drop any keep whose duration <= epsilon (epsilon_frames frames at `fps`).

    Raises WholeDurationRemovedError if no keep survives (whole source removed).
    """
    if duration <= 0:
        raise WholeDurationRemovedError(
            f"source duration must be positive, got {duration}"
        )
    if fps <= 0:
        raise ValueError(f"fps must be positive, got {fps}")

    merged = coalesce_cuts(cuts)

    raw: list[tuple[float, float]] = []
    cursor = 0.0
    for cut_start, cut_end in merged:
        clipped_start = max(cut_start, 0.0)
        clipped_end = min(cut_end, duration)
        if clipped_end <= cursor:
            continue
        if clipped_start > cursor:
            raw.append((cursor, clipped_start))
        cursor = max(cursor, clipped_end)
    if cursor < duration:
        raw.append((cursor, duration))

    epsilon = epsilon_frames / fps

    keeps: list[Keep] = []
    for start, end in raw:
        if snap:
            start = round(start * fps) / fps
            end = round(end * fps) / fps
        start = max(start, 0.0)
        end = min(end, duration)
        if end - start > epsilon:
            keeps.append(Keep(_r(start), _r(end)))

    if not keeps:
        raise WholeDurationRemovedError(
            "every keep-window was removed or sub-epsilon — the cuts cover the "
            "entire source; nothing would remain to encode"
        )
    return keeps


def _fmt(value: float) -> str:
    """Format a rounded boundary float for the graph (stable, no sci-notation)."""
    return f"{_r(value):.6f}"


def filter_complex_script(keeps: list[Keep], *, audio: bool, video: bool) -> str:
    """Build the deterministic ffmpeg filter_complex_script for the keep list.

    For each keep i, emits per-stream trim chains in absolute source time, then
    a single concat. With both streams:

        [0:v]trim=start=Si:end=Ei,setpts=PTS-STARTPTS[vi]
        [0:a]atrim=start=Si:end=Ei,asetpts=PTS-STARTPTS[ai]
        ...
        [v0][a0][v1][a1]...concat=n=N:v=1:a=1[v][a]

    Audio-only emits just the atrim/aconcat half ([a]); video-only just [v].
    Boundary floats are rounded to 6 decimals so the output is byte-identical
    across runs. Raises ValueError if keeps is empty or no stream is selected.
    """
    if not keeps:
        raise ValueError("cannot build a filtergraph with no keep-windows")
    if not (audio or video):
        raise ValueError("at least one of audio/video must be selected")

    lines: list[str] = []
    concat_labels: list[str] = []
    for i, keep in enumerate(keeps):
        si, ei = _fmt(keep.start), _fmt(keep.end)
        if video:
            lines.append(
                f"[0:v]trim=start={si}:end={ei},setpts=PTS-STARTPTS[v{i}]"
            )
        if audio:
            lines.append(
                f"[0:a]atrim=start={si}:end={ei},asetpts=PTS-STARTPTS[a{i}]"
            )
        if video:
            concat_labels.append(f"[v{i}]")
        if audio:
            concat_labels.append(f"[a{i}]")

    n = len(keeps)
    v_flag = 1 if video else 0
    a_flag = 1 if audio else 0
    out_labels = (("[v]" if video else "") + ("[a]" if audio else ""))
    lines.append(
        f"{''.join(concat_labels)}concat=n={n}:v={v_flag}:a={a_flag}{out_labels}"
    )
    return ";\n".join(lines) + "\n"


def summarize(
    keeps: list[Keep], duration: float
) -> tuple[float, float, int]:
    """Return (kept_duration, removed_duration, segment_count) for reporting."""
    kept = sum(k.duration for k in keeps)
    return _r(kept), _r(duration - kept), len(keeps)
