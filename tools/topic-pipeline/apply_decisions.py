#!/usr/bin/env python3
"""Apply decisions exported from the dashboard back into inbox.json.

Replaces the inline Python that previously lived in step 8 of
SCHEDULED_TASK_PROMPT.md and adds support for the dashboard's new
"Inspire from this" YouTube flow (which queues candidates derived from
Tier B/C videos).

Decisions schema (written by render.py's Export button):
{
    "exported_at": ISO8601,
    "candidates": {
        "<cid>": {
            "status": "go|pass|later|shipped",
            "selected_angle_index": int,
            "video_folder": "videos/<slug>-<date>",  // present iff shipped
            ...
        }
    },
    "create_candidates": [
        {"from_youtube": {video_id, title, channel, channel_handle,
                          channel_tier, view_count, upload_date, ...}}
    ]
}

Behavior:
- For each entry under `candidates`: update `user_status`,
  `user_selected_angle_index`, `user_notes` on the matching inbox entry.
  Unknown ids are skipped with a warning.
- For each entry under `create_candidates`: build a synthetic
  inbox candidate with sources=["youtube"]. Skips ids already present in
  the inbox so re-applying the same decisions file is idempotent.
- After applying, the next merge.py / pipeline run scores the new
  candidates the same way as aggregator-derived ones.

Usage:
    python3 apply_decisions.py
    python3 apply_decisions.py --decisions data/decisions.json --keep
    python3 apply_decisions.py --dry-run

By default, decisions.json is renamed with the run timestamp after a
successful apply so it isn't double-processed. --keep disables the rename.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config.json"

_TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "ref", "ref_src", "fbclid", "gclid", "mc_cid", "mc_eid", "igshid",
}


def canonicalize_url(url: str) -> str:
    """Mirrors fetch.py's canonicalization so YouTube-derived ids hash
    consistently with the rest of the inbox."""
    try:
        p = urllib.parse.urlparse(url)
    except Exception:
        return url
    netloc = p.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    qs = urllib.parse.parse_qsl(p.query, keep_blank_values=False)
    qs = [(k, v) for k, v in qs if k.lower() not in _TRACKING_PARAMS]
    qs.sort()
    query = urllib.parse.urlencode(qs)
    path = p.path.rstrip("/") or "/"
    return urllib.parse.urlunparse((p.scheme.lower() or "https", netloc, path, "", query, ""))


def url_hash(url: str) -> str:
    return hashlib.sha1(canonicalize_url(url).encode("utf-8")).hexdigest()[:16]


def youtube_url_for(video_id: str) -> str:
    return f"https://youtube.com/watch?v={urllib.parse.quote(video_id, safe='')}"


def evergreen_default_for_youtube(_: dict[str, Any]) -> int:
    """Tier B/C videos that the user manually flagged as inspiration are
    almost always evergreen-shaped (the curiosity hooks the user is
    imitating). 14 matches the default that fetch.py assigns for
    aggregator candidates without ephemeral keywords."""
    return 14


def build_youtube_candidate(yt: dict[str, Any], queued_at: str) -> dict[str, Any]:
    video_id = yt["video_id"]
    url = youtube_url_for(video_id)
    cid = url_hash(url)
    sources = ["youtube"]
    per_source_entry = {
        "source": "youtube",
        "subreddit": None,
        "external_id": video_id,
        "points": yt.get("view_count"),
        "comments": None,
        "created_at": queued_at,
        "comments_url": url,
        "tags": [yt["channel_tier"]] if yt.get("channel_tier") else [],
        # Snapshot of the inspiration source so the candidate stays
        # informative even if feed.json drops the video later.
        "channel": yt.get("channel"),
        "channel_handle": yt.get("channel_handle"),
        "channel_tier": yt.get("channel_tier"),
        "channel_note": yt.get("channel_note"),
        "view_count": yt.get("view_count"),
        "upload_date": yt.get("upload_date"),
        "duration_s": yt.get("duration_s"),
    }
    evergreen = evergreen_default_for_youtube(yt)
    yt_competition = 10
    demand = 1  # aggregator_breadth = 1; rest of the sub-caps fill in on next pipeline run
    # Same 3-axis floor formula merge.py uses for unjudged candidates,
    # so the dashboard ranks the new entry sensibly until it's judged.
    fallback_composite = round((demand + evergreen + yt_competition) / 1.2)
    candidate = {
        "id": cid,
        "title": yt["title"],
        "url": url,
        "canonical_url": canonicalize_url(url),
        "sources": sources,
        "per_source": [per_source_entry],
        "tags": [],
        "first_seen_at": queued_at,
        "scores": {
            "aggregator_breadth": 1,
            "evergreen": evergreen,
            "demand": demand,
            "demand_sub_caps": {
                "aggregator_breadth": 1,
                "cold_search": 0,
                "autocomplete": 0,
                "tier_b_hit": 0,
            },
            "yt_competition_raw": yt_competition,
            "yt_competition": yt_competition,
            "cooldown_reason": None,
        },
        "angles": [],
        "best_angle_index": None,
        "best_composite": fallback_composite,
        "pending_judgment": True,
    }
    return candidate


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--decisions", default=None,
                    help="Path to decisions.json (default: from config)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print summary without writing inbox.json")
    ap.add_argument("--keep", action="store_true",
                    help="Don't rename decisions.json after applying")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    base_dir = Path(args.config).resolve().parent

    decisions_path = (
        Path(args.decisions).resolve() if args.decisions
        else (base_dir / cfg["paths"]["decisions_json"]).resolve()
    )
    inbox_path = (base_dir / cfg["paths"]["inbox_json"]).resolve()

    if not decisions_path.exists():
        print(f"[apply_decisions] no decisions at {decisions_path}; nothing to apply.",
              file=sys.stderr)
        return 0

    decisions = json.loads(decisions_path.read_text(encoding="utf-8"))
    inbox = json.loads(inbox_path.read_text(encoding="utf-8"))
    candidates = inbox.setdefault("candidates", {})

    # Status updates
    status_block = decisions.get("candidates", {})
    # Backwards-compat: flat {cid: {status: ...}} form (the v0 schema, where
    # the entire decisions dict was the candidate map).
    first_value = next(iter(status_block.values()), {})
    if status_block and not (isinstance(first_value, dict) and "status" in first_value):
        status_block = decisions
    updated_status = 0
    skipped_status = 0
    for cid, dec in status_block.items():
        if not isinstance(dec, dict):
            continue
        c = candidates.get(cid)
        if not c:
            skipped_status += 1
            continue
        if "status" in dec:
            c["user_status"] = dec["status"]
        if "selected_angle_index" in dec:
            c["user_selected_angle_index"] = dec["selected_angle_index"]
        if "notes" in dec:
            c["user_notes"] = dec["notes"]
        if "video_folder" in dec and dec["video_folder"]:
            c["video_folder"] = dec["video_folder"]
        updated_status += 1

    # YouTube-derived candidate creation
    creates = decisions.get("create_candidates", []) or []
    queued_at = decisions.get("exported_at") or datetime.now(timezone.utc).isoformat(timespec="seconds")
    created_new = 0
    skipped_existing = 0
    for entry in creates:
        if not isinstance(entry, dict):
            continue
        yt = entry.get("from_youtube")
        if not yt or not yt.get("video_id") or not yt.get("title"):
            continue
        candidate = build_youtube_candidate(yt, yt.get("queued_at") or queued_at)
        if candidate["id"] in candidates:
            skipped_existing += 1
            continue
        candidates[candidate["id"]] = candidate
        created_new += 1

    inbox["last_updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    print(
        f"[apply_decisions] status updates: {updated_status} (skipped {skipped_status} unknown) "
        f"| YouTube candidates created: {created_new} (skipped {skipped_existing} already in inbox)",
        file=sys.stderr,
    )

    if args.dry_run:
        print("[apply_decisions] --dry-run: not writing inbox.", file=sys.stderr)
        return 0

    inbox_path.write_text(json.dumps(inbox, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[apply_decisions] wrote {inbox_path}", file=sys.stderr)

    if not args.keep:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
        archived = decisions_path.with_name(f"decisions-applied-{ts}.json")
        decisions_path.rename(archived)
        print(f"[apply_decisions] archived decisions -> {archived}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
