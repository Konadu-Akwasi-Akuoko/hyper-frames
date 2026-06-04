"""Tests for the validation pass — informational only, never fatal."""
from __future__ import annotations

from sfx_plan.plan import Cue
from sfx_plan.validate import validate_plan


def _cue(
    start: float,
    dur: float = 0.4,
    cue: str = "ui-tick",
    track: int = 20,
    *,
    at_scene_ms: int = 1000,
    clamped: bool = False,
    preroll_s: float = 0.0,
) -> Cue:
    return Cue(
        data_start=start, duration_s=dur, volume=0.8, pan=0.0,
        track_index=track, src="x.wav", cue=cue, source="x:1",
        clamped=clamped, at_scene_ms=at_scene_ms, lead_ms=0, preroll_s=preroll_s,
    )


def test_no_notes_for_well_spaced_cues() -> None:
    notes = validate_plan([_cue(0.0), _cue(5.0), _cue(10.0)], total_duration_s=60.0)
    assert notes == []


def test_dense_cues_never_raise_and_never_drop() -> None:
    # 20 cues in 4s used to trip the density hard cap. Now: no raise, no notes.
    cues = [_cue(t * 0.2) for t in range(20)]
    notes = validate_plan(cues, total_duration_s=60.0)
    assert all("density" not in n.lower() for n in notes)


def test_overlap_on_same_track_is_an_info_note() -> None:
    notes = validate_plan([_cue(1.0, 1.0, track=20), _cue(1.5, 0.4, track=20)], total_duration_s=60.0)
    assert any("overlap" in n.lower() and "layer" in n.lower() for n in notes)


def test_overlap_on_different_tracks_does_not_note() -> None:
    notes = validate_plan([_cue(1.0, 1.0, track=20), _cue(1.5, 0.4, track=21)], total_duration_s=60.0)
    assert not any("overlap" in n.lower() for n in notes)


def test_preroll_note_for_peak_aligned_cue() -> None:
    notes = validate_plan([_cue(1.0, cue="whoosh", preroll_s=0.35)], total_duration_s=60.0)
    assert any("before its impact frame" in n for n in notes)


def test_onset_aligned_cue_has_no_preroll_note() -> None:
    notes = validate_plan([_cue(1.0, cue="pop", preroll_s=-0.012)], total_duration_s=60.0)
    assert not any("before its impact frame" in n for n in notes)


def test_clamped_cue_emits_note() -> None:
    notes = validate_plan([_cue(0.0, clamped=True)], total_duration_s=60.0)
    assert any("clamped" in n.lower() for n in notes)
