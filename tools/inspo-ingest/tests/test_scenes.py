"""Pure unit tests for the scene-boundary detection math — synthetic series only.

Imports only ``inspo_ingest.scenes`` / ``inspo_ingest.frames`` — never ``cv2``,
never a real video. Every assertion pins the module's exact logic against a
hand-built ``SceneCut`` / ``FeatureRow`` series, mirroring the
assert-exact-logic style of ``test_frames.py`` / ``test_motion.py``.
"""
from __future__ import annotations

import pytest

from inspo_ingest.frames import SceneCut
from inspo_ingest.scenes import (
    Boundary,
    FeatureRow,
    SceneWindow,
    build_scenes,
    detect_hard_cuts,
    detect_soft_transitions,
    merge_boundaries,
)

HARD_DEFAULTS = dict(abs_floor=0.12, ratio=6.0, window_s=3.0, min_gap_s=0.30)
SOFT_DEFAULTS = dict(wide_min=0.22, adj_max=0.10, min_plateau_s=0.5, suppress_s=1.0)


def score_series(scores: list[float], *, fps: float = 10.0) -> list[SceneCut]:
    """One SceneCut per score at a fixed sampling grid starting at t=0."""
    return [SceneCut(time_s=round(i / fps, 3), score=s) for i, s in enumerate(scores)]


def row(t_s: float, wide: float, adj: float = 0.05) -> FeatureRow:
    return FeatureRow(t_s=t_s, adj_delta=adj, wide_delta=wide)


# --- detect_hard_cuts ----------------------------------------------------------


def test_hard_cuts_empty_input_yields_no_boundaries():
    assert detect_hard_cuts([], **HARD_DEFAULTS) == []


def test_hard_cuts_spike_over_flat_noise_fires_once_at_the_spike():
    scores = [0.02] * 30
    scores[15] = 0.5
    cuts = detect_hard_cuts(score_series(scores), **HARD_DEFAULTS)
    assert cuts == [Boundary(t_s=1.5, kind="cut", score=0.5)]


def test_hard_cuts_elevated_baseline_does_not_fire_at_fixed_threshold_scores():
    # An animation stretch holds the score series at ~0.35; one frame at 0.6
    # would trip a fixed 0.3 ffmpeg threshold, but the rolling median (~0.35)
    # lifts the adaptive threshold to 6.0 * 0.35 = 2.1, so nothing fires.
    scores = [0.35] * 40
    scores[20] = 0.6
    assert all(s > 0.3 for s in scores)
    assert detect_hard_cuts(score_series(scores), **HARD_DEFAULTS) == []


def test_hard_cuts_quiet_stretch_subtle_cut_fires_below_fixed_threshold():
    # A talking-head stretch sits at 0.01; a subtle cut scores 0.2 — below a
    # fixed 0.3 threshold but above max(abs_floor=0.12, 6.0 * median=0.06).
    scores = [0.01] * 30
    scores[10] = 0.2
    cuts = detect_hard_cuts(score_series(scores), **HARD_DEFAULTS)
    assert cuts == [Boundary(t_s=1.0, kind="cut", score=0.2)]


def test_hard_cuts_abs_floor_blocks_sub_floor_spikes_even_on_silence():
    # 0.1 dwarfs the all-zero median but stays under abs_floor=0.12.
    scores = [0.0] * 20
    scores[10] = 0.1
    assert detect_hard_cuts(score_series(scores), **HARD_DEFAULTS) == []


def test_hard_cuts_rolling_median_excludes_the_frame_itself():
    # A single frame has an empty neighbor window -> median 0.0, so it
    # qualifies on the abs_floor alone. Including itself in the median would
    # raise the threshold to 6.0 * 0.5 = 3.0 and wrongly reject it.
    cuts = detect_hard_cuts([SceneCut(time_s=2.0, score=0.5)], **HARD_DEFAULTS)
    assert cuts == [Boundary(t_s=2.0, kind="cut", score=0.5)]


def test_hard_cuts_rolling_window_is_time_limited():
    # An elevated plateau more than window_s/2 away must not suppress a spike:
    # the spike's window [3.5, 6.5] sees only the quiet floor around it.
    series = [SceneCut(time_s=round(i * 0.1, 3), score=0.8) for i in range(10)]
    series += [
        SceneCut(time_s=round(4.0 + i * 0.1, 3), score=0.02 if i != 10 else 0.5)
        for i in range(21)
    ]
    cuts = detect_hard_cuts(series, abs_floor=0.12, ratio=6.0, window_s=3.0, min_gap_s=0.3)
    assert Boundary(t_s=5.0, kind="cut", score=0.5) in cuts
    assert all(c.t_s >= 4.0 or c.t_s == 0.0 for c in cuts)


def test_hard_cuts_debounce_keeps_the_max_of_a_cluster():
    scores = [0.01] * 40
    scores[10] = 0.4
    scores[12] = 0.9
    scores[14] = 0.5
    cuts = detect_hard_cuts(score_series(scores), **HARD_DEFAULTS)
    assert cuts == [Boundary(t_s=1.2, kind="cut", score=0.9)]


def test_hard_cuts_debounce_tie_keeps_the_earlier_frame():
    scores = [0.01] * 40
    scores[10] = 0.7
    scores[12] = 0.7
    cuts = detect_hard_cuts(score_series(scores), **HARD_DEFAULTS)
    assert cuts == [Boundary(t_s=1.0, kind="cut", score=0.7)]


def test_hard_cuts_beyond_min_gap_stay_separate_and_time_ordered():
    scores = [0.01] * 40
    scores[5] = 0.6
    scores[20] = 0.8
    cuts = detect_hard_cuts(score_series(scores), **HARD_DEFAULTS)
    assert cuts == [
        Boundary(t_s=0.5, kind="cut", score=0.6),
        Boundary(t_s=2.0, kind="cut", score=0.8),
    ]


# --- detect_soft_transitions ----------------------------------------------------


def test_soft_plateau_boundary_lands_on_the_wide_delta_argmax():
    rows = [row(round(i * 0.1, 3), 0.05) for i in range(10)]
    rows += [
        row(1.0, 0.25),
        row(1.1, 0.30),
        row(1.2, 0.40),
        row(1.3, 0.31),
        row(1.4, 0.24),
        row(1.5, 0.23),
    ]
    rows += [row(round(1.6 + i * 0.1, 3), 0.05) for i in range(5)]
    out = detect_soft_transitions(rows, **SOFT_DEFAULTS, hard_cuts=[])
    assert out == [Boundary(t_s=1.2, kind="soft", score=0.40)]


def test_soft_plateau_argmax_tie_breaks_earlier():
    rows = [
        row(1.0, 0.30),
        row(1.1, 0.35),
        row(1.2, 0.35),
        row(1.3, 0.30),
        row(1.4, 0.25),
        row(1.5, 0.25),
    ]
    out = detect_soft_transitions(rows, **SOFT_DEFAULTS, hard_cuts=[])
    assert out == [Boundary(t_s=1.1, kind="soft", score=0.35)]


def test_soft_plateau_shorter_than_min_plateau_is_ignored():
    rows = [row(1.0, 0.30), row(1.1, 0.35), row(1.2, 0.30)]  # span 0.2s < 0.5s
    assert detect_soft_transitions(rows, **SOFT_DEFAULTS, hard_cuts=[]) == []


def test_soft_plateau_broken_by_high_adj_delta():
    # A large adjacent delta mid-run splits it into two sub-min-plateau halves.
    rows = [
        row(1.0, 0.30),
        row(1.1, 0.35),
        row(1.2, 0.40, adj=0.50),
        row(1.3, 0.35),
        row(1.4, 0.30),
    ]
    assert detect_soft_transitions(rows, **SOFT_DEFAULTS, hard_cuts=[]) == []


def test_soft_candidate_within_suppress_of_a_hard_cut_is_dropped():
    rows = [row(round(1.0 + i * 0.1, 3), 0.30) for i in range(8)]
    hard = [Boundary(t_s=1.5, kind="cut", score=0.9)]
    assert detect_soft_transitions(rows, **SOFT_DEFAULTS, hard_cuts=hard) == []


def test_soft_candidate_beyond_suppress_of_a_hard_cut_survives():
    rows = [row(round(5.0 + i * 0.1, 3), 0.30) for i in range(8)]
    hard = [Boundary(t_s=1.5, kind="cut", score=0.9)]
    out = detect_soft_transitions(rows, **SOFT_DEFAULTS, hard_cuts=hard)
    assert out == [Boundary(t_s=5.0, kind="soft", score=0.30)]


def test_soft_empty_rows_yield_no_boundaries():
    assert detect_soft_transitions([], **SOFT_DEFAULTS, hard_cuts=[]) == []


# --- merge_boundaries -----------------------------------------------------------


def test_merge_hard_beats_soft_within_dedupe():
    hard = [Boundary(t_s=10.0, kind="cut", score=0.4)]
    soft = [Boundary(t_s=10.1, kind="soft", score=0.9)]
    out = merge_boundaries(hard, soft, dedupe_s=0.2, duration_s=60.0)
    assert out == [Boundary(t_s=10.0, kind="cut", score=0.4)]


def test_merge_same_kind_higher_score_wins_then_earlier():
    soft_pair = [
        Boundary(t_s=10.0, kind="soft", score=0.3),
        Boundary(t_s=10.1, kind="soft", score=0.5),
    ]
    out = merge_boundaries([], soft_pair, dedupe_s=0.2, duration_s=60.0)
    assert out == [Boundary(t_s=10.1, kind="soft", score=0.5)]

    tied = [
        Boundary(t_s=10.0, kind="soft", score=0.5),
        Boundary(t_s=10.1, kind="soft", score=0.5),
    ]
    out = merge_boundaries([], tied, dedupe_s=0.2, duration_s=60.0)
    assert out == [Boundary(t_s=10.0, kind="soft", score=0.5)]


def test_merge_beyond_dedupe_keeps_both_sorted_by_time():
    hard = [Boundary(t_s=12.0, kind="cut", score=0.4)]
    soft = [Boundary(t_s=10.0, kind="soft", score=0.9)]
    out = merge_boundaries(hard, soft, dedupe_s=0.2, duration_s=60.0)
    assert out == [
        Boundary(t_s=10.0, kind="soft", score=0.9),
        Boundary(t_s=12.0, kind="cut", score=0.4),
    ]


def test_merge_drops_boundaries_at_or_outside_the_video_edges():
    hard = [
        Boundary(t_s=0.0, kind="cut", score=0.9),
        Boundary(t_s=5.0, kind="cut", score=0.9),
        Boundary(t_s=60.0, kind="cut", score=0.9),
    ]
    soft = [Boundary(t_s=-1.0, kind="soft", score=0.9)]
    out = merge_boundaries(hard, soft, dedupe_s=0.2, duration_s=60.0)
    assert out == [Boundary(t_s=5.0, kind="cut", score=0.9)]


def test_merge_chained_cluster_collapses_to_one_winner():
    # Each neighbor is within dedupe_s of the previous; the chain is one cluster.
    soft = [
        Boundary(t_s=10.0, kind="soft", score=0.3),
        Boundary(t_s=10.15, kind="soft", score=0.4),
        Boundary(t_s=10.3, kind="soft", score=0.6),
    ]
    out = merge_boundaries([], soft, dedupe_s=0.2, duration_s=60.0)
    assert out == [Boundary(t_s=10.3, kind="soft", score=0.6)]


# --- build_scenes -----------------------------------------------------------------


def test_build_scenes_tiles_zero_to_duration_exactly_with_1_based_indices():
    boundaries = [
        Boundary(t_s=4.0, kind="cut", score=0.5),
        Boundary(t_s=9.5, kind="soft", score=0.3),
    ]
    scenes = build_scenes(boundaries, duration_s=20.0)
    assert scenes == [
        SceneWindow(index=1, start_s=0.0, end_s=4.0, boundary_kind="start", boundary_score=None),
        SceneWindow(index=2, start_s=4.0, end_s=9.5, boundary_kind="cut", boundary_score=0.5),
        SceneWindow(index=3, start_s=9.5, end_s=20.0, boundary_kind="soft", boundary_score=0.3),
    ]
    assert scenes[0].start_s == 0.0
    assert scenes[-1].end_s == 20.0
    for prev, nxt in zip(scenes, scenes[1:]):
        assert prev.end_s == nxt.start_s


def test_build_scenes_no_boundaries_yields_one_full_scene():
    scenes = build_scenes([], duration_s=12.5)
    assert scenes == [
        SceneWindow(index=1, start_s=0.0, end_s=12.5, boundary_kind="start", boundary_score=None)
    ]


def test_build_scenes_sorts_boundaries_and_ignores_edge_boundaries():
    boundaries = [
        Boundary(t_s=8.0, kind="cut", score=0.7),
        Boundary(t_s=20.0, kind="cut", score=0.9),
        Boundary(t_s=3.0, kind="soft", score=0.3),
        Boundary(t_s=0.0, kind="cut", score=0.9),
    ]
    scenes = build_scenes(boundaries, duration_s=20.0)
    assert [s.start_s for s in scenes] == [0.0, 3.0, 8.0]
    assert [s.index for s in scenes] == [1, 2, 3]
    assert scenes[-1].end_s == 20.0


def test_build_scenes_rejects_non_positive_duration():
    with pytest.raises(ValueError):
        build_scenes([], duration_s=0.0)
