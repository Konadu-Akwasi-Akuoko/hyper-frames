"""Tests for the pure parsing/ranking helpers — no network, no binaries."""
from __future__ import annotations

import pytest

from inspo_ingest.frames import (
    SceneCut,
    hero_cut,
    parse_scene_scores,
    parse_section,
    rank_cuts,
)


# --- section parsing ---------------------------------------------------------

def test_parse_section_mmss() -> None:
    assert parse_section("1:12-1:18") == (72.0, 78.0)


def test_parse_section_short_window() -> None:
    assert parse_section("0:05-0:12") == (5.0, 12.0)


def test_parse_section_hhmmss() -> None:
    assert parse_section("00:01:12-00:01:18") == (72.0, 78.0)


def test_parse_section_whitespace_tolerant() -> None:
    assert parse_section(" 1:00 - 1:30 ") == (60.0, 90.0)


@pytest.mark.parametrize(
    "bad",
    [
        "1:12",            # no end
        "1:12-",           # empty end
        "112-118",         # no colons
        "1:99-2:00",       # seconds out of range
        "1:18-1:12",       # end before start
        "1:12-1:12",       # zero-length
        "",                # empty
        "abc-def",         # garbage
    ],
)
def test_parse_section_rejects_malformed(bad: str) -> None:
    with pytest.raises(ValueError):
        parse_section(bad)


# --- scene-score parsing -----------------------------------------------------

# Verified metadata=print shape (select filter, lavfi.scene_score 0-1).
_METADATA_SELECT = """\
frame:0 pts:0 pts_time:0.000000
lavfi.scene_score=0.000000
frame:1 pts:512 pts_time:0.033367
lavfi.scene_score=0.052710
frame:101 pts:51712 pts_time:3.337000
lavfi.scene_score=0.445904
frame:166 pts:84992 pts_time:5.506000
lavfi.scene_score=0.183130
"""

# Verified scdet metadata shape (lavfi.scd.score 0-100, plus lavfi.scd.time on cuts).
_METADATA_SCDET = """\
frame:0 pts:0 pts_time:0.000000
lavfi.scd.mafd=0.000
lavfi.scd.score=0.000
frame:1 pts:512 pts_time:0.033367
lavfi.scd.mafd=3.142
lavfi.scd.score=5.271
frame:101 pts:51712 pts_time:3.337000
lavfi.scd.mafd=28.119
lavfi.scd.score=42.817
lavfi.scd.time=3.337000
"""

# Verified scdet stderr log lines.
_STDERR_SCDET = """\
lavfi.scd.score: 42.817, lavfi.scd.time: 3.337
lavfi.scd.score: 18.313, lavfi.scd.time: 5.506
"""


def test_parse_scene_scores_select_metadata() -> None:
    cuts = parse_scene_scores(_METADATA_SELECT)
    assert cuts == [
        SceneCut(0.0, 0.0),
        SceneCut(0.033367, 0.05271),
        SceneCut(3.337, 0.445904),
        SceneCut(5.506, 0.18313),
    ]


def test_parse_scene_scores_scdet_metadata() -> None:
    cuts = parse_scene_scores(_METADATA_SCDET)
    assert cuts == [
        SceneCut(0.0, 0.0),
        SceneCut(0.033367, 5.271),
        SceneCut(3.337, 42.817),
    ]


def test_parse_scene_scores_scdet_stderr() -> None:
    cuts = parse_scene_scores(_STDERR_SCDET)
    assert cuts == [
        SceneCut(3.337, 42.817),
        SceneCut(5.506, 18.313),
    ]


def test_parse_scene_scores_empty() -> None:
    assert parse_scene_scores("") == []


# --- ranking -----------------------------------------------------------------

def test_rank_top_n_then_time_sorted() -> None:
    cuts = [
        SceneCut(1.0, 0.10),
        SceneCut(2.0, 0.90),
        SceneCut(3.0, 0.50),
        SceneCut(4.0, 0.80),
        SceneCut(5.0, 0.20),
    ]
    # Top 3 by score: 0.90(t2), 0.80(t4), 0.50(t3) -> re-sorted by time.
    ranked = rank_cuts(cuts, clip_duration_s=6.0, max_frames=3, min_frames=2)
    assert ranked == [
        SceneCut(2.0, 0.90),
        SceneCut(3.0, 0.50),
        SceneCut(4.0, 0.80),
    ]


def test_rank_tie_broken_by_earlier_time() -> None:
    cuts = [
        SceneCut(5.0, 0.50),
        SceneCut(1.0, 0.50),
        SceneCut(3.0, 0.50),
    ]
    ranked = rank_cuts(cuts, clip_duration_s=6.0, max_frames=2, min_frames=1)
    # Top 2 are the two earliest (tie -> earlier time wins), then time-sorted.
    assert ranked == [SceneCut(1.0, 0.50), SceneCut(3.0, 0.50)]


def test_rank_fewer_than_min_falls_back_to_even_spacing() -> None:
    cuts = [SceneCut(2.0, 0.9)]  # only 1 candidate, min is 3
    ranked = rank_cuts(cuts, clip_duration_s=6.0, max_frames=6, min_frames=3)
    assert len(ranked) == 3
    times = [c.time_s for c in ranked]
    # Evenly spaced across [0, 6] with edge inset: 1.5, 3.0, 4.5
    assert times == pytest.approx([1.5, 3.0, 4.5])
    assert all(c.score == 0.0 for c in ranked)


def test_rank_exactly_min_keeps_real_cuts() -> None:
    cuts = [SceneCut(1.0, 0.3), SceneCut(2.0, 0.9), SceneCut(3.0, 0.6)]
    ranked = rank_cuts(cuts, clip_duration_s=6.0, max_frames=6, min_frames=3)
    assert ranked == cuts  # already time-sorted, all kept


def test_rank_single_min_frame_even_spacing_is_midpoint() -> None:
    ranked = rank_cuts([], clip_duration_s=6.0, max_frames=4, min_frames=1)
    assert ranked == [SceneCut(3.0, 0.0)]


# --- hero --------------------------------------------------------------------

def test_hero_cut_picks_highest_score() -> None:
    cuts = [SceneCut(1.0, 0.3), SceneCut(2.0, 0.9), SceneCut(3.0, 0.6)]
    assert hero_cut(cuts) == SceneCut(2.0, 0.9)


def test_hero_cut_tie_breaks_to_earlier_time() -> None:
    cuts = [SceneCut(3.0, 0.9), SceneCut(1.0, 0.9)]
    assert hero_cut(cuts) == SceneCut(1.0, 0.9)


def test_hero_cut_empty_raises() -> None:
    with pytest.raises(ValueError):
        hero_cut([])
