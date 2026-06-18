"""Filtergraph synthesis must be byte-identical to a golden fixture."""

from __future__ import annotations

from pathlib import Path

import pytest

from cut_video.segments import Keep, filter_complex_script

FIXTURES = Path(__file__).parent / "fixtures"

# A fixed keep list with a non-terminating boundary (25/3) to exercise rounding.
KEEPS = [Keep(0.0, 2.5), Keep(5.25, round(25 / 3, 6))]


def test_video_filtergraph_matches_golden() -> None:
    graph = filter_complex_script(KEEPS, audio=True, video=True)
    golden = (FIXTURES / "golden_video.filtergraph").read_text()
    assert graph == golden


def test_audio_filtergraph_matches_golden() -> None:
    graph = filter_complex_script(KEEPS, audio=True, video=False)
    golden = (FIXTURES / "golden_audio.filtergraph").read_text()
    assert graph == golden


def test_filtergraph_is_byte_stable_across_calls() -> None:
    a = filter_complex_script(KEEPS, audio=True, video=True)
    b = filter_complex_script(KEEPS, audio=True, video=True)
    assert a == b
    assert a.encode("utf-8") == b.encode("utf-8")


def test_empty_keeps_raises() -> None:
    with pytest.raises(ValueError):
        filter_complex_script([], audio=True, video=True)


def test_no_stream_selected_raises() -> None:
    with pytest.raises(ValueError):
        filter_complex_script(KEEPS, audio=False, video=False)
