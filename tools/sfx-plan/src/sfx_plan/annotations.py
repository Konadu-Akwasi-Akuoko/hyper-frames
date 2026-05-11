"""Walk a video folder's HTML files and collect every data-sfx-* annotation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class Annotation:
    """One element's worth of data-sfx-* attributes plus its source location."""

    anchor: str
    anchor_index: int
    cue: str
    lead_ms: int | None
    volume: float | None
    pan: float
    is_hook: bool
    element_id: str | None
    source: str


def _parse_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _parse_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _html_files(root: Path) -> Iterator[Path]:
    yield from sorted(root.rglob("*.html"))


def scan_annotations(video_dir: Path) -> Iterator[Annotation]:
    """Yield every data-sfx-* annotation found under `video_dir`.

    `compositions/sfx.html` is skipped (it's the output of this tool — scanning
    it would create a loop).
    """
    for path in _html_files(video_dir):
        if path.name == "sfx.html" and path.parent.name == "compositions":
            continue
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        for tag in soup.find_all(attrs={"data-sfx-anchor": True}):
            anchor = tag.get("data-sfx-anchor", "").strip()
            cue = tag.get("data-sfx-on-anchor", "").strip()
            if not anchor or not cue:
                continue
            line = tag.sourceline or 1
            rel = path.relative_to(video_dir).as_posix()
            yield Annotation(
                anchor=anchor,
                anchor_index=_parse_int(tag.get("data-sfx-anchor-index")) or 1,
                cue=cue,
                lead_ms=_parse_int(tag.get("data-sfx-lead-ms")),
                volume=_parse_float(tag.get("data-sfx-volume")),
                pan=_parse_float(tag.get("data-sfx-pan")) or 0.0,
                is_hook=(tag.get("data-sfx-hook") == "true"),
                element_id=tag.get("id"),
                source=f"{rel}:{line}",
            )
