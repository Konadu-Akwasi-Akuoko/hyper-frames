"""Validation pass: overlap detection + density checks."""
from __future__ import annotations

from sfx_plan.errors import SfxPlanError
from sfx_plan.plan import Cue


DENSITY_WARN_PER_SEC = 1.0 / 3.0
DENSITY_HARD_PER_SEC = 1.0 / 1.5
DENSITY_WINDOW_S = 6.0


class DensityViolationError(SfxPlanError):
    def __init__(self, *, density: float, window_s: float, hard_cap: float) -> None:
        super().__init__(
            f"cue density {density:.2f}/s in a {window_s}s window exceeds the hard cap "
            f"of {hard_cap:.2f}/s. Drop cues — the mix will smear VO intelligibility."
        )
        self.density = density


def _overlap_warnings(cues: list[Cue]) -> list[str]:
    warnings: list[str] = []
    by_track: dict[int, list[Cue]] = {}
    for c in cues:
        by_track.setdefault(c.track_index, []).append(c)
    for track, lane in by_track.items():
        lane.sort(key=lambda c: c.data_start)
        for prev, curr in zip(lane, lane[1:]):
            if curr.data_start < prev.data_start + prev.duration_s:
                warnings.append(
                    f"overlap on track {track}: cue at {prev.data_start:.2f}s "
                    f"({prev.cue}, {prev.duration_s:.2f}s) intersects cue at "
                    f"{curr.data_start:.2f}s ({curr.cue})."
                )
    return warnings


def _density_check(cues: list[Cue]) -> list[str]:
    """Rolling-window density. Warn at WARN cap; raise at HARD cap."""
    warnings: list[str] = []
    if not cues:
        return warnings
    ordered = sorted(cues, key=lambda c: c.data_start)
    warned = False
    for i, anchor in enumerate(ordered):
        window_end = anchor.data_start + DENSITY_WINDOW_S
        count = sum(1 for c in ordered[i:] if c.data_start < window_end)
        density = count / DENSITY_WINDOW_S
        if density > DENSITY_HARD_PER_SEC:
            raise DensityViolationError(
                density=density, window_s=DENSITY_WINDOW_S, hard_cap=DENSITY_HARD_PER_SEC,
            )
        if density > DENSITY_WARN_PER_SEC and not warned:
            warnings.append(
                f"density {density:.2f}/s in window starting {anchor.data_start:.2f}s "
                f"({count} cues in {DENSITY_WINDOW_S}s). Consider trimming."
            )
            warned = True
    return warnings


def validate_plan(cues: list[Cue], *, total_duration_s: float) -> list[str]:
    """Run all validations; return a list of warning strings. May raise on hard caps."""
    warnings = _overlap_warnings(cues)
    warnings.extend(_density_check(cues))
    for c in cues:
        if c.clamped:
            warnings.append(
                f"cue at {c.source} clamped to 0s (computed start was negative)."
            )
    return warnings
