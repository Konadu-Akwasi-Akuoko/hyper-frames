"""Assemble the final research.json payload and write it atomically."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import os
import tempfile

from youtube_seo.autocomplete import AutocompleteResult
from youtube_seo.signals import (
    compute_demand_phrases,
    compute_hook_patterns,
    compute_saturation_warnings,
    compute_top_nouns,
)


def build_payload(
    *,
    topic: str,
    autocomplete: AutocompleteResult,
    videos: list[dict[str, Any]],
    region: str,
    hl: str,
    n: int,
) -> dict[str, Any]:
    """Compose the canonical research.json structure."""
    return {
        "topic": topic,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "params": {"n": n, "region": region, "hl": hl},
        "autocomplete": (
            None
            if autocomplete.failed
            else {"seed": autocomplete.seed, "expanded": autocomplete.expanded}
        ),
        "top_videos": videos,
        "signals": {
            "top_nouns": compute_top_nouns(videos),
            "saturation_warnings": compute_saturation_warnings(videos),
            "demand_phrases": (
                compute_demand_phrases(autocomplete.expanded)
                if not autocomplete.failed
                else []
            ),
            "hook_patterns": compute_hook_patterns(videos),
        },
    }


def write_atomic(payload: dict[str, Any], output_path: Path) -> None:
    """Write JSON to a temp file in the same directory, then rename."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, indent=2) + "\n"
    fd, tmp_name = tempfile.mkstemp(
        dir=output_path.parent,
        prefix=output_path.name + ".",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(serialized)
        os.replace(tmp_name, output_path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
