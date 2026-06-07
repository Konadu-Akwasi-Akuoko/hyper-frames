"""Pure helpers: section parsing, scene-score parsing, ranking, even-spacing fallback.

Nothing here touches the network, the filesystem, or a subprocess. Every function
is deterministic so the pipeline's decision logic is unit-testable without binaries.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_SECTION_RE = re.compile(
    r"^\s*(?P<sh>\d+):(?P<sm>[0-5]?\d)(?::(?P<ss>[0-5]?\d))?"
    r"\s*-\s*"
    r"(?P<eh>\d+):(?P<em>[0-5]?\d)(?::(?P<es>[0-5]?\d))?\s*$"
)

# `select` filter writes 0-1 floats as `lavfi.scene_score=0.445904`.
# `scdet` filter writes 0-100 floats as `lavfi.scd.score=42.817`.
_SCORE_RE = re.compile(
    r"lavfi\.(?:scene_score|scd\.score)\s*[:=]\s*(?P<score>[\d.]+)"
)
_FRAME_RE = re.compile(
    r"frame:\d+\s+pts:[\d.]+\s+pts_time:(?P<pts_time>[\d.]+)"
)
# scdet stderr log line: "lavfi.scd.score: 42.817, lavfi.scd.time: 3.337"
_STDERR_TIME_RE = re.compile(
    r"lavfi\.scd\.score\s*[:=]\s*(?P<score>[\d.]+)\s*,"
    r"\s*lavfi\.scd\.time\s*[:=]\s*(?P<time>[\d.]+)"
)


@dataclass(frozen=True)
class SceneCut:
    """A single scored frame candidate: its time within the clip and its scene score."""

    time_s: float
    score: float


def parse_section(section: str) -> tuple[float, float]:
    """Parse a ``MM:SS-MM:SS`` (or ``HH:MM:SS-HH:MM:SS``) window into ``(start_s, end_s)``.

    Both endpoints accept either ``M:SS`` or ``H:MM:SS`` form. Raises ``ValueError``
    on malformed input or when the end is not strictly after the start.
    """
    m = _SECTION_RE.match(section)
    if not m:
        raise ValueError(
            f'malformed --section {section!r}; expected "MM:SS-MM:SS" '
            f'(e.g. "1:12-1:18") or "HH:MM:SS-HH:MM:SS"'
        )

    start = _to_seconds(m.group("sh"), m.group("sm"), m.group("ss"))
    end = _to_seconds(m.group("eh"), m.group("em"), m.group("es"))
    if end <= start:
        raise ValueError(
            f"--section end ({end:g}s) must be strictly after start ({start:g}s)"
        )
    return start, end


def _to_seconds(a: str, b: str, c: str | None) -> float:
    if c is None:
        # a:b == MM:SS
        return float(a) * 60.0 + float(b)
    # a:b:c == HH:MM:SS
    return float(a) * 3600.0 + float(b) * 60.0 + float(c)


def parse_scene_scores(text: str) -> list[SceneCut]:
    """Parse ffmpeg scene-detection output into ``[SceneCut(time_s, score), ...]``.

    Handles both shapes verified from the research:

    * the ``metadata=print`` file, where interleaved ``frame:N ... pts_time:T`` header
      lines are paired with the following ``lavfi.scene_score=`` / ``lavfi.scd.score=``
      line, and
    * the ``scdet`` stderr log lines of the form
      ``lavfi.scd.score: 42.817, lavfi.scd.time: 3.337``.

    Returns cuts in source order. A frame header with no following score line (or a
    score line with no preceding header) is skipped.
    """
    cuts: list[SceneCut] = []
    pending_time: float | None = None

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        stderr_match = _STDERR_TIME_RE.search(line)
        if stderr_match:
            cuts.append(
                SceneCut(
                    time_s=float(stderr_match.group("time")),
                    score=float(stderr_match.group("score")),
                )
            )
            pending_time = None
            continue

        frame_match = _FRAME_RE.search(line)
        if frame_match:
            pending_time = float(frame_match.group("pts_time"))
            continue

        score_match = _SCORE_RE.search(line)
        if score_match and pending_time is not None:
            cuts.append(SceneCut(time_s=pending_time, score=float(score_match.group("score"))))
            pending_time = None

    return cuts


def rank_cuts(
    cuts: list[SceneCut],
    *,
    clip_duration_s: float,
    max_frames: int,
    min_frames: int,
) -> list[SceneCut]:
    """Pick the frames to extract, deterministically.

    Keeps the top ``max_frames`` cuts by score (ties broken by earlier time), then
    re-sorts the survivors by time. If fewer than ``min_frames`` candidates survive,
    falls back to ``min_frames`` evenly-spaced timestamps spanning the clip
    ``[0, clip_duration_s]`` (scene scores discarded, ``score`` set to ``0.0``).

    All ``time_s`` values are clip-relative (matching ffmpeg's ``pts_time`` on a
    section-downloaded clip that starts at ~0), so callers must not re-add the
    window start.
    """
    if max_frames < 1:
        raise ValueError("max_frames must be >= 1")
    if min_frames < 1:
        raise ValueError("min_frames must be >= 1")

    if len(cuts) < min_frames:
        return _even_spacing(clip_duration_s=clip_duration_s, count=min_frames)

    ranked = sorted(cuts, key=lambda c: (-c.score, c.time_s))[:max_frames]
    return sorted(ranked, key=lambda c: c.time_s)


def hero_cut(cuts: list[SceneCut]) -> SceneCut:
    """Return the single highest-score cut (ties broken by earlier time)."""
    if not cuts:
        raise ValueError("no cuts to choose a hero from")
    return min(cuts, key=lambda c: (-c.score, c.time_s))


def _even_spacing(*, clip_duration_s: float, count: int) -> list[SceneCut]:
    if count == 1:
        return [SceneCut(time_s=clip_duration_s / 2.0, score=0.0)]
    # Inset from both edges so frames don't land on the clip's first/last frame
    # (a keyframe leader or a hard cut at the boundary makes those frames unstable).
    step = clip_duration_s / (count + 1)
    return [SceneCut(time_s=step * (i + 1), score=0.0) for i in range(count)]
