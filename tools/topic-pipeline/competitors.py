#!/usr/bin/env python3
"""
Pull recent videos from Tier B (style-reference) and Tier C (watchlist)
channels listed in config.json:reference_channels.

Used by the v2 scoring rubric (see RUBRIC.md):
- Demand sub-axis: did a Tier B channel hit on a similar topic?
- 30-day cooldown: did Tier B/C cover this topic in the last 30 days?
- Inspiration mode: which Tier B titles look like our target shape?

Output:
- data/competitors/feed.json — latest snapshot, overwritten each run
- data/archive/YYYY-MM-DD/competitors.json — dated audit copy

Per-video schema:
    {"id", "title", "view_count", "upload_date", "duration_s",
     "channel", "channel_handle", "channel_tier"}

Wall-clock budget: ~5–7 min for 18 channels × 25 videos with 6-way parallelism.

Usage:
    python3 competitors.py
    python3 competitors.py --tier B
    python3 competitors.py --videos-per-channel 10
    python3 competitors.py --concurrency 4 --dry-run
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config.json"


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text())


def channel_url(handle: str) -> str:
    return f"https://www.youtube.com/@{handle}/videos"


def fetch_channel(
    handle: str,
    tier: str,
    note: str,
    videos_per_channel: int,
) -> tuple[str, list[dict[str, Any]], str | None]:
    """Run yt-dlp on one channel. Returns (handle, videos, error_or_none)."""
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--dump-json",
        "--playlist-end",
        str(videos_per_channel),
        "--ignore-errors",
        "--no-warnings",
        channel_url(handle),
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return handle, [], f"timeout after 300s on {handle}"
    except FileNotFoundError:
        return handle, [], "yt-dlp not found on PATH"

    if proc.returncode != 0 and not proc.stdout.strip():
        err = (proc.stderr or "").strip().splitlines()[-1:] or ["unknown error"]
        return handle, [], f"yt-dlp exit {proc.returncode}: {err[0]}"

    videos: list[dict[str, Any]] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        videos.append(
            {
                "id": d.get("id"),
                "title": d.get("title"),
                "view_count": d.get("view_count"),
                "upload_date": d.get("upload_date"),
                "duration_s": d.get("duration"),
                "channel": d.get("channel") or d.get("uploader"),
                "channel_handle": handle,
                "channel_tier": tier,
                "channel_note": note,
            }
        )

    return handle, videos, None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tier",
        choices=["B", "C", "all"],
        default="all",
        help="Which tier to fetch. Default: all.",
    )
    parser.add_argument(
        "--videos-per-channel",
        type=int,
        default=None,
        help="Override config videos_per_channel.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=None,
        help="Override config fetch_concurrency.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List which channels would be fetched without running yt-dlp.",
    )
    args = parser.parse_args()

    cfg = load_config()
    rc = cfg.get("reference_channels", {})
    if not rc:
        print("config.json missing reference_channels section", file=sys.stderr)
        return 2

    videos_per_channel = args.videos_per_channel or rc.get("videos_per_channel", 25)
    concurrency = args.concurrency or rc.get("fetch_concurrency", 6)

    channels: list[tuple[str, str, str]] = []
    if args.tier in ("B", "all"):
        for c in rc.get("style_reference", []):
            channels.append((c["handle"], "B", c.get("note", "")))
    if args.tier in ("C", "all"):
        for c in rc.get("watchlist", []):
            channels.append((c["handle"], "C", c.get("note", "")))

    if not channels:
        print("no channels selected", file=sys.stderr)
        return 2

    print(
        f"Fetching {len(channels)} channels "
        f"({videos_per_channel} videos each, {concurrency}-way parallel)...",
        file=sys.stderr,
    )

    if args.dry_run:
        for handle, tier, note in channels:
            print(f"  [{tier}] @{handle} — {note}")
        return 0

    started = time.monotonic()
    all_videos: list[dict[str, Any]] = []
    per_channel_status: list[dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {
            pool.submit(fetch_channel, h, t, n, videos_per_channel): (h, t)
            for (h, t, n) in channels
        }
        for fut in as_completed(futures):
            handle, tier = futures[fut]
            try:
                h, videos, err = fut.result()
            except Exception as exc:
                err = f"unexpected exception: {exc!r}"
                videos = []
                h = handle
            elapsed = time.monotonic() - started
            count = len(videos)
            status = "ok" if not err else "FAIL"
            print(
                f"  [{elapsed:6.1f}s] [{tier}] @{h:20s} {status:4s} "
                f"({count} videos){' — ' + err if err else ''}",
                file=sys.stderr,
            )
            per_channel_status.append(
                {
                    "handle": h,
                    "tier": tier,
                    "video_count": count,
                    "ok": err is None,
                    "error": err,
                }
            )
            all_videos.extend(videos)

    elapsed_total = time.monotonic() - started

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    feed = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "videos_per_channel_requested": videos_per_channel,
        "elapsed_seconds": round(elapsed_total, 1),
        "per_channel": per_channel_status,
        "videos": all_videos,
    }

    paths = cfg.get("paths", {})
    feed_path = HERE / paths.get("competitors_feed", "data/competitors/feed.json")
    archive_dir = HERE / paths.get("archive_dir", "data/archive") / today
    archive_path = archive_dir / "competitors.json"

    feed_path.parent.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    payload = json.dumps(feed, indent=2, ensure_ascii=False)
    feed_path.write_text(payload)
    archive_path.write_text(payload)

    ok = sum(1 for s in per_channel_status if s["ok"])
    print(
        f"\nDone in {elapsed_total:.1f}s. "
        f"{ok}/{len(per_channel_status)} channels ok, "
        f"{len(all_videos)} videos total.",
        file=sys.stderr,
    )
    print(f"  Latest:  {feed_path}", file=sys.stderr)
    print(f"  Archive: {archive_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
