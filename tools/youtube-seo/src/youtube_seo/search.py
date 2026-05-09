"""Top-N video metadata via yt-dlp.

Shells out to the system yt-dlp binary (assumed on PATH). Returns parsed
per-video dicts with the SEO-relevant fields. Description is truncated to
500 chars to keep the output JSON small.
"""

from __future__ import annotations

from typing import Any
import json
import subprocess

DESCRIPTION_MAX_CHARS = 500

# Fields kept from yt-dlp's per-video JSON. Anything not in this list is
# dropped at output time to keep research.json focused.
KEPT_FIELDS = (
    "title",
    "channel",
    "channel_id",
    "view_count",
    "like_count",
    "comment_count",
    "upload_date",
    "tags",
    "categories",
    "chapters",
    "heatmap",
)


class YtDlpSoftBlock(RuntimeError):
    """Raised when yt-dlp returns the 'Sign in to confirm you're not a bot' message."""


def fetch_top_videos(topic: str, n: int = 30) -> list[dict[str, Any]]:
    """Run `yt-dlp --dump-json ytsearchN:<topic>` and return cleaned dicts.

    Raises YtDlpSoftBlock if YouTube serves the bot-check page.
    Raises subprocess.CalledProcessError on other yt-dlp failures.
    """
    cmd = ["yt-dlp", "--dump-json", f"ytsearch{n}:{topic}"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if proc.returncode != 0:
        stderr = proc.stderr.lower()
        if "sign in to confirm" in stderr or "not a bot" in stderr:
            raise YtDlpSoftBlock(
                "yt-dlp soft-blocked. Try `--cookies-from-browser firefox` "
                "manually, or wait and re-run."
            )
        raise subprocess.CalledProcessError(
            proc.returncode, cmd, output=proc.stdout, stderr=proc.stderr
        )

    videos: list[dict[str, Any]] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        videos.append(_clean(raw))
    return videos


def _clean(raw: dict[str, Any]) -> dict[str, Any]:
    """Keep only KEPT_FIELDS, plus `duration_seconds` and `description_excerpt`."""
    out: dict[str, Any] = {field: raw.get(field) for field in KEPT_FIELDS}
    out["duration_seconds"] = raw.get("duration")
    description = raw.get("description") or ""
    out["description_excerpt"] = description[:DESCRIPTION_MAX_CHARS]
    return out
