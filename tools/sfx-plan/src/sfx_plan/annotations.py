"""Walk a video folder's HTML files and collect every data-sfx-* annotation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from bs4 import BeautifulSoup

from sfx_plan.errors import MissingTimeReferenceError


@dataclass(frozen=True)
class Annotation:
    """One element's worth of data-sfx-* attributes plus its source location."""

    cue: str
    at_scene_ms: int
    lead_ms: int | None
    volume: float | None
    pan: float
    is_hook: bool
    element_id: str | None
    source: str
    asset: str | None = None


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

    An element is recognized as an annotation when it sets `data-sfx-on-anchor`
    (the cue). It must also set its timing reference `data-sfx-at-scene-ms` — the
    scene-local ms of the element's visual impact frame. SFX in this project are
    triggered only by visual events; there is no spoken-word path.
    """
    for path in _html_files(video_dir):
        if path.name == "sfx.html" and path.parent.name == "compositions":
            continue
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        for tag in soup.find_all(attrs={"data-sfx-on-anchor": True}):
            cue = (tag.get("data-sfx-on-anchor") or "").strip()
            if not cue:
                continue
            line = tag.sourceline or 1
            rel = path.relative_to(video_dir).as_posix()
            source = f"{rel}:{line}"

            at_scene_ms = _parse_int(tag.get("data-sfx-at-scene-ms"))
            if at_scene_ms is None:
                raise MissingTimeReferenceError(source=source)

            asset_raw = tag.get("data-sfx-asset")
            asset = asset_raw.strip() if isinstance(asset_raw, str) and asset_raw.strip() else None

            yield Annotation(
                cue=cue,
                at_scene_ms=at_scene_ms,
                lead_ms=_parse_int(tag.get("data-sfx-lead-ms")),
                volume=_parse_float(tag.get("data-sfx-volume")),
                pan=_parse_float(tag.get("data-sfx-pan")) or 0.0,
                is_hook=(tag.get("data-sfx-hook") == "true"),
                element_id=tag.get("id"),
                source=source,
                asset=asset,
            )
