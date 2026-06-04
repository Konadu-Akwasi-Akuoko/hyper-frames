"""Tests for the HTML annotation scanner (visual-only timing)."""
from __future__ import annotations

from pathlib import Path

import pytest

from sfx_plan.annotations import scan_annotations
from sfx_plan.errors import MissingTimeReferenceError


def test_scan_finds_every_annotation(video_dir: Path) -> None:
    annotations = list(scan_annotations(video_dir))
    assert len(annotations) == 3


def test_scan_extracts_cue_at_scene_ms_and_source(video_dir: Path) -> None:
    annotations = list(scan_annotations(video_dir))
    headline = next(a for a in annotations if a.element_id == "s1-headline")
    assert headline.cue == "ui-tick"
    assert headline.at_scene_ms == 8400
    assert headline.source.endswith("index.html:8")


def test_scan_reads_optional_attributes(video_dir: Path) -> None:
    p = video_dir / "compositions" / "extra.html"
    p.write_text(
        '<html><body><div id="x"'
        ' data-sfx-on-anchor="whoosh" data-sfx-at-scene-ms="3000" data-sfx-lead-ms="-80"'
        ' data-sfx-volume="0.7" data-sfx-pan="-0.3"></div></body></html>',
        encoding="utf-8",
    )
    annotations = list(scan_annotations(video_dir))
    extra = next(a for a in annotations if a.element_id == "x")
    assert extra.lead_ms == -80
    assert extra.volume == 0.7
    assert extra.pan == -0.3


def test_scan_parses_data_sfx_asset(video_dir: Path) -> None:
    p = video_dir / "compositions" / "pinned.html"
    p.write_text(
        '<html><body><div id="p"'
        ' data-sfx-on-anchor="pop" data-sfx-at-scene-ms="500"'
        ' data-sfx-asset="Mister Horse Free SFX/Pop/Hollow Pop 06.wav"></div></body></html>',
        encoding="utf-8",
    )
    annotations = list(scan_annotations(video_dir))
    pinned = next(a for a in annotations if a.element_id == "p")
    assert pinned.asset == "Mister Horse Free SFX/Pop/Hollow Pop 06.wav"


def test_scan_parses_data_sfx_at_scene_ms(video_dir: Path) -> None:
    p = video_dir / "compositions" / "visual.html"
    p.write_text(
        '<html><body><div id="v"'
        ' data-sfx-on-anchor="pop" data-sfx-at-scene-ms="7420"></div></body></html>',
        encoding="utf-8",
    )
    annotations = list(scan_annotations(video_dir))
    visual = next(a for a in annotations if a.element_id == "v")
    assert visual.at_scene_ms == 7420


def test_scan_raises_when_no_timing_reference(video_dir: Path) -> None:
    p = video_dir / "compositions" / "neither.html"
    p.write_text(
        '<html><body><div id="n" data-sfx-on-anchor="pop"></div></body></html>',
        encoding="utf-8",
    )
    with pytest.raises(MissingTimeReferenceError):
        list(scan_annotations(video_dir))
