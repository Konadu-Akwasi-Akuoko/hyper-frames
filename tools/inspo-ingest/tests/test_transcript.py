"""Tests for the pure transcript math — no network, no binaries, no cv2."""
from __future__ import annotations

from dataclasses import dataclass

import pytest

from inspo_ingest.transcript import (
    LAST_WORD_TAIL_S,
    SceneNarration,
    Word,
    aggregates,
    align_scenes,
    filter_non_speech,
    is_sentence_end,
    parse_json3,
    punctuated_fraction,
)


@dataclass(frozen=True)
class _Win:
    """Duck-typed scene window: align_scenes/aggregates never import scenes.py."""

    start_s: float
    end_s: float
    boundary_kind: str = "cut"


# --- json3 fixtures (literal strings modeled on real auto-caption tracks) -----

# Verified json3 shape: wireMagic header, a window-definition event with no
# segs, a multi-seg event whose FIRST seg legitimately lacks tOffsetMs plus a
# whitespace-only seg, an aAppend re-emit event, a bracketed [Music] seg, and
# punctuated word tokens.
_JSON3_PUNCTUATED = (
    '{"wireMagic":"pb3","pens":[{}],"wsWinStyles":[{},{"mhModeHint":2,'
    '"juJustifCode":0,"sdScrollDir":3}],"wpWinPositions":[{},{"apPoint":6,'
    '"ahHorPos":20,"avVerPos":100,"rcRows":2,"ccCols":40}],"events":['
    '{"tStartMs":0,"dDurationMs":540000,"id":1,"wpWinPosId":1,"wsWinStyleId":1},'
    '{"tStartMs":120,"dDurationMs":4000,"wWinId":1,"segs":[{"utf8":"Hello"},'
    '{"utf8":"  ","tOffsetMs":300},{"utf8":" world.","tOffsetMs":600}]},'
    '{"tStartMs":4120,"dDurationMs":120,"wWinId":1,"aAppend":1,"segs":[{"utf8":"\\n"}]},'
    '{"tStartMs":4240,"dDurationMs":3000,"wWinId":1,"segs":[{"utf8":"[Music]"}]},'
    '{"tStartMs":7240,"dDurationMs":2000,"wWinId":1,"segs":[{"utf8":"Next"},'
    '{"utf8":" up,","tOffsetMs":400},{"utf8":" pacing","tOffsetMs":900}]}'
    "]}"
)

# Same structure, no punctuation anywhere (the unpunctuated-track degradation).
_JSON3_UNPUNCTUATED = (
    '{"wireMagic":"pb3","events":['
    '{"tStartMs":0,"dDurationMs":540000,"id":1},'
    '{"tStartMs":100,"dDurationMs":2000,"segs":[{"utf8":"hello"},'
    '{"utf8":" world","tOffsetMs":600}]},'
    '{"tStartMs":4000,"dDurationMs":2000,"segs":[{"utf8":"next"},'
    '{"utf8":" up","tOffsetMs":400},{"utf8":" pacing","tOffsetMs":900}]}'
    "]}"
)


# --- parse_json3 ---------------------------------------------------------------

def test_parse_json3_onsets_are_tstart_plus_toffset() -> None:
    words = parse_json3(_JSON3_PUNCTUATED)
    assert [w.text for w in words] == ["Hello", "world.", "[Music]", "Next", "up,", "pacing"]
    assert [w.start_s for w in words] == pytest.approx(
        [0.12, 0.72, 4.24, 7.24, 7.64, 8.14]
    )


def test_parse_json3_first_seg_without_toffset_defaults_to_tstart() -> None:
    words = parse_json3(_JSON3_PUNCTUATED)
    assert words[0].start_s == pytest.approx(0.12)  # tStartMs=120, no tOffsetMs
    assert words[3].start_s == pytest.approx(7.24)  # tStartMs=7240, no tOffsetMs


def test_parse_json3_skips_window_def_aappend_and_whitespace_segs() -> None:
    words = parse_json3(_JSON3_PUNCTUATED)
    texts = [w.text for w in words]
    assert len(words) == 6
    assert "\n" not in texts  # aAppend re-emit skipped
    assert all(w.text.strip() for w in words)  # whitespace-only seg skipped
    assert not any(w.start_s == 0.0 for w in words)  # window-def event has no segs


def test_parse_json3_word_end_is_next_onset() -> None:
    words = parse_json3(_JSON3_PUNCTUATED)
    for prev, nxt in zip(words[:-1], words[1:]):
        assert prev.end_s == pytest.approx(nxt.start_s)


def test_parse_json3_last_word_gets_tail() -> None:
    words = parse_json3(_JSON3_PUNCTUATED)
    assert words[-1].end_s == pytest.approx(8.14 + LAST_WORD_TAIL_S)


def test_parse_json3_empty_events_yields_no_words() -> None:
    assert parse_json3('{"wireMagic":"pb3","events":[]}') == []


@pytest.mark.parametrize(
    "bad",
    [
        "WEBVTT\n\n00:00.000 --> 00:01.000\nhello",  # vtt, not JSON
        '{"wireMagic":"pb3"}',                       # no events
        '{"events":"nope"}',                         # events not a list
        '{"wireMagic":"pb2","events":[]}',           # wrong magic
        "[1, 2, 3]",                                 # JSON but not a dict
    ],
)
def test_parse_json3_rejects_non_json3(bad: str) -> None:
    with pytest.raises(ValueError):
        parse_json3(bad)


# --- filter_non_speech ---------------------------------------------------------

def test_filter_non_speech_drops_bracket_tokens_keeps_baked_ends() -> None:
    words = filter_non_speech(parse_json3(_JSON3_PUNCTUATED))
    assert [w.text for w in words] == ["Hello", "world.", "Next", "up,", "pacing"]
    # world.'s end stays at [Music]'s onset, exposing the music stretch as a gap.
    assert words[1].end_s == pytest.approx(4.24)
    assert words[2].start_s == pytest.approx(7.24)


@pytest.mark.parametrize(
    "token", ["[Music]", "[Applause]", "[♪ upbeat music ♪]", "[Laughter]"]
)
def test_filter_non_speech_token_shapes(token: str) -> None:
    assert filter_non_speech([Word(token, 0.0, 1.0)]) == []


def test_filter_non_speech_keeps_speech() -> None:
    speech = [Word("hello", 0.0, 0.5), Word("[sic]world", 0.5, 1.0)]
    assert filter_non_speech(speech) == speech


# --- is_sentence_end / punctuated_fraction --------------------------------------

@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Done.", True),
        ("really?", True),
        ("wow!", True),
        ('end."', True),
        ("done!)", True),
        ("etc...", True),
        ("up,", False),
        ("word", False),
        ("mid.dle", False),
    ],
)
def test_is_sentence_end(text: str, expected: bool) -> None:
    assert is_sentence_end(Word(text, 0.0, 0.5)) is expected


def test_punctuated_fraction() -> None:
    words = filter_non_speech(parse_json3(_JSON3_PUNCTUATED))
    # "world." and "up," carry trailing punctuation out of 5 words.
    assert punctuated_fraction(words) == pytest.approx(0.4)


def test_punctuated_fraction_empty_and_unpunctuated() -> None:
    assert punctuated_fraction([]) == 0.0
    assert punctuated_fraction(parse_json3(_JSON3_UNPUNCTUATED)) == 0.0


# --- align_scenes ----------------------------------------------------------------

# Hand-built words: a sentence end at 1.0, a 1.0s gap, then a word straddling
# the boundary at 3.0, and silence after 4.1.
_WORDS = [
    Word("One", 0.0, 0.4),
    Word("two.", 0.4, 1.0),
    Word("Three", 2.0, 2.5),
    Word("four", 2.5, 3.6),
    Word("five.", 3.6, 4.1),
]

_WINDOWS = [
    _Win(0.0, 2.0, "start"),
    _Win(2.0, 3.0, "cut"),
    _Win(3.0, 5.0, "soft"),
    _Win(5.0, 12.0, "cut"),
]


def _aligned() -> list[SceneNarration]:
    narrations = align_scenes(_WINDOWS, _WORDS)
    assert all(nar is not None for nar in narrations)
    return [nar for nar in narrations if nar is not None]


def test_align_word_count_wps_and_text() -> None:
    n1, n2, n3, n4 = _aligned()
    assert (n1.word_count, n2.word_count, n3.word_count, n4.word_count) == (2, 2, 1, 0)
    assert n1.words_per_s == pytest.approx(1.0)
    assert n2.words_per_s == pytest.approx(2.0)
    assert n3.words_per_s == pytest.approx(0.5)
    assert n4.words_per_s == 0.0
    assert n1.text == "One two."
    assert n2.text == "Three four"
    assert n3.text == "five."
    assert n4.text == ""


def test_align_coverage_clips_spans_to_window() -> None:
    n1, n2, n3, n4 = _aligned()
    assert n1.coverage == pytest.approx(0.5)   # 1.0s of speech over 2.0s
    assert n2.coverage == pytest.approx(1.0)   # straddler's clipped span counts
    assert n3.coverage == pytest.approx(0.55)  # four clipped to 0.6 + five. 0.5
    assert n4.coverage == 0.0


def test_align_coverage_capped_at_one() -> None:
    overlapping = [Word("a", 0.0, 3.0), Word("b", 1.0, 2.0)]
    narrations = align_scenes([_Win(1.0, 2.0)], overlapping)
    assert narrations[0] is not None
    assert narrations[0].coverage == 1.0


def test_align_cut_in_pause_fires_on_boundary_gap() -> None:
    _, n2, _, _ = _aligned()
    assert n2.pause_before_cut_s == pytest.approx(1.0)  # two. ends 1.0, Three at 2.0
    assert n2.cut_in_pause is True


def test_align_straddling_word_zeroes_pause() -> None:
    _, _, n3, _ = _aligned()
    assert n3.pause_before_cut_s == 0.0  # four spans 2.5-3.6 across b=3.0
    assert n3.cut_in_pause is False


def test_align_first_scene_boundary_at_speech_onset() -> None:
    n1 = _aligned()[0]
    assert n1.pause_before_cut_s == 0.0  # One starts exactly at 0.0
    assert n1.cut_in_pause is False


def test_align_trailing_silence_gap_clips_to_last_window_end() -> None:
    n4 = _aligned()[3]
    # No speech after five. (ends 4.1); gap runs to the last window end (12.0).
    assert n4.pause_before_cut_s == pytest.approx(7.9)
    assert n4.cut_in_pause is True


def test_align_leading_and_trailing_silence() -> None:
    n1, n2, n3, n4 = _aligned()
    assert n1.first_word_offset_s == pytest.approx(0.0)
    assert n1.trailing_silence_s == pytest.approx(1.0)
    assert n2.trailing_silence_s == 0.0  # four's end (3.6) overshoots e=3.0, clipped
    assert n3.first_word_offset_s == pytest.approx(0.6)
    assert n3.leading_silence_s == pytest.approx(0.6)
    assert n3.trailing_silence_s == pytest.approx(0.9)
    assert n4.first_word_offset_s is None
    assert n4.leading_silence_s == pytest.approx(7.0)
    assert n4.trailing_silence_s == pytest.approx(7.0)


def test_align_sentence_aligned_true_false() -> None:
    n1, n2, n3, n4 = _aligned()
    assert n1.sentence_aligned is False  # no word ends in [-1.0, 0.0]
    assert n2.sentence_aligned is True   # "two." ends at 1.0, within lookback of 2.0
    assert n3.sentence_aligned is False  # "Three" ends at 2.5, not sentence-ending
    assert n4.sentence_aligned is True   # "five." ends at 4.1, within lookback of 5.0


def test_align_sentence_aligned_none_when_unpunctuated() -> None:
    unpunctuated = [Word(w.text.rstrip(".,!?"), w.start_s, w.end_s) for w in _WORDS]
    narrations = align_scenes(_WINDOWS, unpunctuated)
    assert all(nar is not None and nar.sentence_aligned is None for nar in narrations)


def test_align_empty_words_yields_all_none() -> None:
    assert align_scenes(_WINDOWS, []) == [None, None, None, None]


def test_align_empty_windows_yields_empty() -> None:
    assert align_scenes([], _WORDS) == []


# --- aggregates ------------------------------------------------------------------

def test_aggregates_full() -> None:
    agg = aggregates(_WINDOWS, _aligned(), duration_s=12.0)
    assert agg["scene_count"] == 4
    assert agg["cuts_per_minute"] == pytest.approx(10.0)  # 2 hard cuts in 12s
    assert agg["soft_transition_count"] == 1
    durs = agg["scene_duration_s"]
    assert isinstance(durs, dict)
    assert durs["median"] == pytest.approx(2.0)
    assert durs["p25"] == pytest.approx(1.75)
    assert durs["p75"] == pytest.approx(3.25)
    assert durs["min"] == pytest.approx(1.0)
    assert durs["max"] == pytest.approx(7.0)
    assert agg["longest_hold_s"] == pytest.approx(7.0)
    assert agg["words_per_s_mean"] == pytest.approx(0.875)
    assert agg["pct_cuts_in_pause"] == pytest.approx(2.0 / 3.0)
    assert agg["pct_sentence_aligned"] == pytest.approx(2.0 / 3.0)


def test_aggregates_nullable_without_narration() -> None:
    agg = aggregates(_WINDOWS, [None, None, None, None], duration_s=12.0)
    assert agg["words_per_s_mean"] is None
    assert agg["pct_cuts_in_pause"] is None
    assert agg["pct_sentence_aligned"] is None
    assert agg["scene_count"] == 4
    assert agg["cuts_per_minute"] == pytest.approx(10.0)


def test_aggregates_pct_sentence_aligned_none_when_unpunctuated() -> None:
    unpunctuated = [Word(w.text.rstrip(".,!?"), w.start_s, w.end_s) for w in _WORDS]
    narrations = align_scenes(_WINDOWS, unpunctuated)
    agg = aggregates(_WINDOWS, narrations, duration_s=12.0)
    assert agg["pct_sentence_aligned"] is None
    assert agg["pct_cuts_in_pause"] == pytest.approx(2.0 / 3.0)
    assert agg["words_per_s_mean"] == pytest.approx(0.875)


def test_aggregates_single_scene_duration_stats_collapse() -> None:
    windows = [_Win(0.0, 6.0, "start")]
    agg = aggregates(windows, [None], duration_s=6.0)
    durs = agg["scene_duration_s"]
    assert isinstance(durs, dict)
    assert durs == {"median": 6.0, "p25": 6.0, "p75": 6.0, "min": 6.0, "max": 6.0}
    assert agg["cuts_per_minute"] == 0.0
    assert agg["longest_hold_s"] == 6.0
