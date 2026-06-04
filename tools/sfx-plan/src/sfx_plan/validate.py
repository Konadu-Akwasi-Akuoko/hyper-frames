"""Validation pass: per-cue, informational, never fatal.

Cross-cue suppression has been removed by design. Each cue is independent and
element-bound: a cue is placed solely because its own visual event warrants a
sound, and is never dropped, delayed, or merged because of any neighbouring cue.
There is no density cap. Concurrent cues simply layer in playback (and build_plan
lane-packs them onto distinct track-indices). Everything here only ever returns
notes — nothing raises.
"""
from __future__ import annotations

from sfx_plan.plan import Cue


def _overlap_notes(cues: list[Cue]) -> list[str]:
    """Quiet note when two cues share a track-index and overlap in time.

    build_plan lane-packs cues so this should not fire; kept as a safety. Overlap
    is NOT an error — concurrent SFX layer fine — so this only ever returns notes.
    """
    notes: list[str] = []
    by_track: dict[int, list[Cue]] = {}
    for c in cues:
        by_track.setdefault(c.track_index, []).append(c)
    for track, lane in by_track.items():
        lane.sort(key=lambda c: c.data_start)
        for prev, curr in zip(lane, lane[1:]):
            if curr.data_start < prev.data_start + prev.duration_s:
                notes.append(
                    f"note: cues share track {track} and overlap at "
                    f"{curr.data_start:.2f}s ({prev.cue} → {curr.cue}); they layer fine."
                )
    return notes


def _preroll_notes(cues: list[Cue]) -> list[str]:
    """Per-cue hint: a cue audible before its own visual impact frame.

    Only peak-aligned cues (whoosh, riser) carry pre-roll — their swell leads in,
    which is correct for *motion*. If such a cue is punctuating a thing *appearing*,
    that pre-roll reads as sound-before-visual; the fix is an onset-aligned cue
    (pop / tick / ding). This is a cue-vs-its-own-visual check, never a cross-cue
    rule, and never drops anything.
    """
    notes: list[str] = []
    for c in cues:
        if c.preroll_s > 0.05:
            notes.append(
                f"note: {c.cue} at {c.source} is audible {c.preroll_s * 1000:.0f}ms "
                f"before its impact frame (peak-aligned). Fine for motion; if this is "
                f"a thing appearing, use an onset-aligned cue (pop/tick/ding)."
            )
    return notes


def validate_plan(cues: list[Cue], *, total_duration_s: float) -> list[str]:
    """Return a list of informational notes. Never raises — cues are never dropped."""
    notes = _overlap_notes(cues)
    notes.extend(_preroll_notes(cues))
    for c in cues:
        if c.clamped:
            notes.append(
                f"note: cue at {c.source} clamped to 0s (computed start was negative)."
            )
    return notes
