"""Load narration-map.json and resolve anchors to timestamps."""
from __future__ import annotations

import json
import re
from pathlib import Path

from sfx_plan.errors import UnresolvedAnchorError, AnchorIndexOutOfRangeError

_PUNCT_STRIP_RE = re.compile(r"[^\w\s]+", re.UNICODE)


def _normalize(phrase: str) -> str:
    """Lowercase + strip punctuation + collapse whitespace. Matches narration-map's contract."""
    no_punct = _PUNCT_STRIP_RE.sub(" ", phrase.lower())
    return " ".join(no_punct.split())


def load_narration_map(path: Path) -> dict[str, list[dict]]:
    """Return a dict mapping normalized phrase → list of {start, end, ...} matches."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, list[dict]] = {}
    for entry in raw.get("anchors", []):
        phrase = entry.get("phrase", "")
        key = _normalize(phrase)
        if not key:
            continue
        out[key] = list(entry.get("matches", []))
    return out


def resolve_anchor(
    nm: dict[str, list[dict]],
    *,
    anchor: str,
    index: int,
    source: str,
) -> float:
    """Return the start time (seconds) of the `index`-th occurrence of `anchor`.

    `index` is 1-indexed (the user-facing convention from data-sfx-anchor-index).
    """
    key = _normalize(anchor)
    matches = nm.get(key)
    if not matches:
        raise UnresolvedAnchorError(anchor=anchor, source=source)
    if index < 1 or index > len(matches):
        raise AnchorIndexOutOfRangeError(
            anchor=anchor, requested=index, available=len(matches), source=source,
        )
    return float(matches[index - 1]["start"])
