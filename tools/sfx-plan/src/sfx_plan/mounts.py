"""Read index.html and map each mounted composition to its data-start offset.

Annotations carry `source = "<posix-rel-path>:<line>"`, e.g.
`compositions/scene-01-open.html:265`. The mount map uses the same posix
relative path shape as the dict key so the join is direct.
"""
from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup


def _posix(value: str) -> str:
    return value.replace("\\", "/").strip()


def load_mount_offsets(index_html_path: Path) -> dict[str, float]:
    """Return {posix-relative composition src: data-start seconds} for every mount.

    Elements without `data-composition-src` are skipped. Mounts without
    `data-start` default to 0.0. A non-numeric `data-start` raises ValueError
    so a malformed index surfaces loudly.
    """
    if not index_html_path.exists():
        return {}
    soup = BeautifulSoup(index_html_path.read_text(encoding="utf-8"), "html.parser")
    offsets: dict[str, float] = {}
    for tag in soup.find_all(attrs={"data-composition-src": True}):
        src = tag.get("data-composition-src")
        if not src:
            continue
        raw = tag.get("data-start", "0")
        try:
            offset = float(raw)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"index.html mount {src!r} has non-numeric data-start={raw!r}"
            ) from exc
        offsets[_posix(src)] = offset
    return offsets
