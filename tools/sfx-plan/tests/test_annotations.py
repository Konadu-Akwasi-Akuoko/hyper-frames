"""Tests for the HTML annotation scanner."""
from __future__ import annotations

from pathlib import Path

from sfx_plan.annotations import scan_annotations


def test_scan_finds_every_annotation(video_dir: Path) -> None:
    annotations = list(scan_annotations(video_dir))
    assert len(annotations) == 3


def test_scan_extracts_anchor_and_cue_and_source(video_dir: Path) -> None:
    annotations = list(scan_annotations(video_dir))
    nightmare = next(a for a in annotations if a.anchor == "nightmare")
    assert nightmare.cue == "ui-tick"
    assert nightmare.anchor_index == 1
    assert nightmare.source.endswith("index.html:8")
    assert nightmare.element_id == "s1-headline"


def test_scan_reads_optional_overrides(video_dir: Path) -> None:
    p = video_dir / "compositions" / "extra.html"
    p.write_text(
        '<html><body><div id="x"'
        ' data-sfx-anchor="easy" data-sfx-anchor-index="1"'
        ' data-sfx-on-anchor="whoosh" data-sfx-lead-ms="-200"'
        ' data-sfx-volume="0.7" data-sfx-pan="-0.3"></div></body></html>',
        encoding="utf-8",
    )
    annotations = list(scan_annotations(video_dir))
    extra = next(a for a in annotations if a.source.endswith("extra.html:1"))
    assert extra.lead_ms == -200
    assert extra.volume == 0.7
    assert extra.pan == -0.3
