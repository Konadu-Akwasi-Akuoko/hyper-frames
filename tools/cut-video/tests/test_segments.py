"""Pure keep-window math tests — no ffmpeg, no I/O."""

from __future__ import annotations

import pytest

from cut_video.segments import (
    Keep,
    WholeDurationRemovedError,
    coalesce_cuts,
    keep_windows,
    summarize,
)

FPS = 30.0
DUR = 10.0


def test_complement_over_known_duration() -> None:
    keeps = keep_windows([(3.0, 5.0)], duration=DUR, fps=FPS)
    assert keeps == [Keep(0.0, 3.0), Keep(5.0, 10.0)]


def test_multiple_cuts_complement() -> None:
    keeps = keep_windows([(2.0, 3.0), (6.0, 7.0)], duration=DUR, fps=FPS)
    assert keeps == [Keep(0.0, 2.0), Keep(3.0, 6.0), Keep(7.0, 10.0)]


def test_overlapping_cuts_coalesce_no_zero_length_keep() -> None:
    keeps = keep_windows([(2.0, 5.0), (4.0, 7.0)], duration=DUR, fps=FPS)
    assert keeps == [Keep(0.0, 2.0), Keep(7.0, 10.0)]
    assert all(k.duration > 0 for k in keeps)


def test_adjacent_cuts_coalesce_no_zero_length_keep() -> None:
    # Two removed spans that touch at t=5 must not leave a zero-length keep.
    keeps = keep_windows([(2.0, 5.0), (5.0, 7.0)], duration=DUR, fps=FPS)
    assert keeps == [Keep(0.0, 2.0), Keep(7.0, 10.0)]
    assert all(k.duration > 0 for k in keeps)


def test_cut_at_t0_no_leading_keep() -> None:
    keeps = keep_windows([(0.0, 4.0)], duration=DUR, fps=FPS)
    assert keeps == [Keep(4.0, 10.0)]


def test_cut_touching_eof_no_trailing_keep() -> None:
    keeps = keep_windows([(6.0, 10.0)], duration=DUR, fps=FPS)
    assert keeps == [Keep(0.0, 6.0)]


def test_sub_epsilon_keep_dropped() -> None:
    # The middle keep [5.0, 5.01] is ~0.3 frames at 30fps -> below 1-frame epsilon.
    keeps = keep_windows(
        [(2.0, 5.0), (5.01, 7.0)], duration=DUR, fps=FPS, epsilon_frames=1.0
    )
    assert Keep(5.0, 5.01) not in keeps
    assert keeps == [Keep(0.0, 2.0), Keep(7.0, 10.0)]


def test_sub_epsilon_keep_kept_when_epsilon_small() -> None:
    keeps = keep_windows(
        [(2.0, 5.0), (5.01, 7.0)], duration=DUR, fps=FPS, epsilon_frames=0.1
    )
    assert Keep(5.0, 5.01) in keeps


def test_whole_duration_removed_raises_loud() -> None:
    with pytest.raises(WholeDurationRemovedError):
        keep_windows([(0.0, 10.0)], duration=DUR, fps=FPS)


def test_overlapping_cuts_covering_whole_raises() -> None:
    with pytest.raises(WholeDurationRemovedError):
        keep_windows([(0.0, 6.0), (5.0, 10.0)], duration=DUR, fps=FPS)


def test_unsorted_cuts_are_sorted() -> None:
    unsorted = keep_windows([(6.0, 7.0), (2.0, 3.0)], duration=DUR, fps=FPS)
    expected = keep_windows([(2.0, 3.0), (6.0, 7.0)], duration=DUR, fps=FPS)
    assert unsorted == expected
    assert unsorted == [Keep(0.0, 2.0), Keep(3.0, 6.0), Keep(7.0, 10.0)]


def test_coalesce_drops_zero_length_removed_span() -> None:
    assert coalesce_cuts([(3.0, 3.0), (5.0, 6.0)]) == [(5.0, 6.0)]


def test_coalesce_sorts_and_merges() -> None:
    assert coalesce_cuts([(6.0, 7.0), (1.0, 2.0), (1.5, 3.0)]) == [
        (1.0, 3.0),
        (6.0, 7.0),
    ]


def test_no_cuts_keeps_whole_source() -> None:
    assert keep_windows([], duration=DUR, fps=FPS) == [Keep(0.0, 10.0)]


def test_frame_snap_deterministic() -> None:
    cuts = [(3.017, 4.991)]
    first = keep_windows(cuts, duration=DUR, fps=FPS, snap=True)
    second = keep_windows(cuts, duration=DUR, fps=FPS, snap=True)
    assert first == second
    # cut.start 3.017 -> nearest 30fps frame round(90.51)/30 = 91/30;
    # cut.end 4.991 -> round(149.73)/30 = 150/30 = 5.0
    assert first == [
        Keep(0.0, round(91 / 30, 6)),
        Keep(5.0, 10.0),
    ]


def test_frame_snap_boundaries_land_on_frame_grid() -> None:
    keeps = keep_windows([(3.017, 4.991)], duration=DUR, fps=FPS, snap=True)
    # Snapped boundaries land on the frame grid up to the deterministic
    # 6-decimal rounding floor (rounding wins over exact-frame fidelity).
    tol = FPS * 0.5e-6 + 1e-9
    for k in keeps:
        assert abs(k.start * FPS - round(k.start * FPS)) < tol
        assert abs(k.end * FPS - round(k.end * FPS)) < tol


def test_boundaries_rounded_to_six_decimals() -> None:
    keeps = keep_windows([(1.0 / 3.0, 2.0 / 3.0)], duration=DUR, fps=FPS)
    for k in keeps:
        assert k.start == round(k.start, 6)
        assert k.end == round(k.end, 6)


def test_summarize() -> None:
    keeps = keep_windows([(3.0, 5.0)], duration=DUR, fps=FPS)
    kept, removed, count = summarize(keeps, DUR)
    assert kept == 8.0
    assert removed == 2.0
    assert count == 2
