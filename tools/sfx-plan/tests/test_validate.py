"""Tests for the validation pass."""
from __future__ import annotations

import pytest

from sfx_plan.plan import Cue
from sfx_plan.validate import validate_plan, DensityViolationError


def _cue(
    start: float,
    dur: float = 0.4,
    cue: str = "ui-tick",
    track: int = 20,
    *,
    lead_ms: int = 0,
    at_scene_ms: int | None = None,
    anchor: str | None = "a",
) -> Cue:
    return Cue(
        data_start=start, duration_s=dur, volume=0.8, pan=0.0,
        track_index=track, src="x.wav", cue=cue,
        anchor=anchor, anchor_index=1, source="x:1", clamped=False,
        at_scene_ms=at_scene_ms, lead_ms=lead_ms,
    )


def test_no_warnings_for_well_spaced_cues() -> None:
    warnings = validate_plan([_cue(0.0), _cue(5.0), _cue(10.0)], total_duration_s=60.0)
    assert warnings == []


def test_overlap_on_same_track_emits_warning() -> None:
    warnings = validate_plan([_cue(1.0, 1.0, track=20), _cue(1.5, 0.4, track=20)], total_duration_s=60.0)
    assert any("overlap" in w.lower() for w in warnings)


def test_overlap_on_different_tracks_does_not_warn() -> None:
    warnings = validate_plan([_cue(1.0, 1.0, track=20), _cue(1.5, 0.4, track=21)], total_duration_s=60.0)
    assert not any("overlap" in w.lower() for w in warnings)


def test_density_warning_above_three_per_window() -> None:
    cues = [_cue(t) for t in [0.0, 0.4, 0.8, 1.2]]
    warnings = validate_plan(cues, total_duration_s=60.0)
    assert any("density" in w.lower() for w in warnings)


def test_density_above_hard_cap_raises() -> None:
    cues = [_cue(t * 0.2) for t in range(20)]
    with pytest.raises(DensityViolationError):
        validate_plan(cues, total_duration_s=60.0)


def test_large_lead_warning_for_anchor_cue() -> None:
    warnings = validate_plan([_cue(1.0, lead_ms=-220)], total_duration_s=60.0)
    assert any("large lead_ms" in w for w in warnings)


def test_small_lead_does_not_warn() -> None:
    warnings = validate_plan([_cue(1.0, lead_ms=-50)], total_duration_s=60.0)
    assert not any("large lead_ms" in w for w in warnings)


def test_at_scene_ms_cues_are_exempt_from_large_lead_warning() -> None:
    warnings = validate_plan(
        [_cue(1.0, lead_ms=-500, at_scene_ms=1000, anchor=None)],
        total_duration_s=60.0,
    )
    assert not any("large lead_ms" in w for w in warnings)
