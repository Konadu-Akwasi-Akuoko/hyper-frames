#!/usr/bin/env python3
"""
YouTube cold-search demand sub-signal (Tier D in RUBRIC.md).

Per candidate, fetch the top-N YouTube search results via
`yt-dlp ytsearchN:<query>` and emit:

- demand_score (0-5)   median view_count of top 5 results, mapped via
                       view_count_to_demand() below.
- tier_b_hits          tracked Tier B channels appearing in results,
                       with days_ago (drives the 30-day cooldown rule).
- tier_c_hits          ditto for Tier C.
- untracked_channels   list of unknown channels, fuel for #112 auto-discovery.

Output: data/archive/YYYY-MM-DD/ytsearch.json — keyed by candidate id.
Caches across runs: candidate ids already in the file are skipped unless
--refresh is passed.

Usage:
    python3 cold_search.py --candidates data/archive/2026-05-08/shortlist.json
    python3 cold_search.py --candidates ... --top-k 10 --top-k-for-demand 5
    python3 cold_search.py --candidates ... --refresh --concurrency 6
    python3 cold_search.py --query "how does captcha work"   # one-off probe
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config.json"

# Demand mapping: median view_count of top-K → 0-5 score.
# Calibrated from CALIBRATION-2026-05-08.md cold-search archive.
DEMAND_BANDS = [
    (1_000_000, 5),
    (  100_000, 4),
    (   30_000, 3),
    (   10_000, 2),
    (    3_000, 1),
]


def view_count_to_demand(median_views: float | None) -> int:
    if not median_views:
        return 0
    for threshold, score in DEMAND_BANDS:
        if median_views >= threshold:
            return score
    return 0


# Patterns stripped from candidate titles before passing to ytsearch.
_PREFIX_RE = re.compile(
    r"^(show|ask|tell)\s+(hn|lobsters?)\s*[:\-—]\s*",
    re.IGNORECASE,
)
_SITE_SUFFIX_RE = re.compile(
    r"\s*[\|\-–—]\s*(?:[\w.\-]+\.[a-z]{2,5}|hacker\s*news|lobste\.?rs|reddit)\s*$",
    re.IGNORECASE,
)
_YEAR_PAREN_RE = re.compile(r"\s*\((19|20)\d{2}\)\s*$")
_WHITESPACE_RE = re.compile(r"\s+")


def title_to_query(title: str) -> str:
    """Best-effort transformation from candidate title to a curiosity-shaped
    YouTube search query. Conservative: keeps the title's wording, just
    strips the source-specific noise."""
    q = title or ""
    q = _PREFIX_RE.sub("", q)
    q = _YEAR_PAREN_RE.sub("", q)
    q = _SITE_SUFFIX_RE.sub("", q)
    q = _WHITESPACE_RE.sub(" ", q).strip()
    if len(q) > 100:
        q = q[:100].rsplit(" ", 1)[0]
    return q


def normalize_handle(uploader_id: str | None) -> str | None:
    if not uploader_id:
        return None
    s = uploader_id.strip()
    if s.startswith("@"):
        s = s[1:]
    return s.lower() or None


def load_tier_map(cfg: dict[str, Any]) -> dict[str, str]:
    """Returns {lowercase_handle: 'B' | 'C'}."""
    rc = cfg.get("reference_channels", {})
    out: dict[str, str] = {}
    for c in rc.get("style_reference", []):
        h = (c.get("handle") or "").lower()
        if h:
            out[h] = "B"
    for c in rc.get("watchlist", []):
        h = (c.get("handle") or "").lower()
        if h:
            out[h] = "C"
    return out


def days_between(upload_date_yyyymmdd: str | None, today: datetime) -> int | None:
    if not upload_date_yyyymmdd:
        return None
    try:
        d = datetime.strptime(upload_date_yyyymmdd, "%Y%m%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return (today - d).days


def search_one(query: str, top_k: int, timeout_s: int = 120) -> tuple[list[dict[str, Any]], str | None]:
    """One yt-dlp ytsearch invocation. Returns (videos, error_or_none)."""
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--dump-json",
        "--ignore-errors",
        "--no-warnings",
        f"ytsearch{top_k}:{query}",
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return [], f"timeout after {timeout_s}s"
    except FileNotFoundError:
        return [], "yt-dlp not found on PATH"

    if proc.returncode != 0 and not proc.stdout.strip():
        err = (proc.stderr or "").strip().splitlines()[-1:] or ["unknown error"]
        return [], f"yt-dlp exit {proc.returncode}: {err[0]}"

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
                "channel": d.get("channel") or d.get("uploader"),
                "channel_handle": normalize_handle(d.get("uploader_id")),
                "view_count": d.get("view_count"),
                "upload_date": d.get("upload_date"),
                "duration_s": d.get("duration"),
            }
        )
    return videos, None


def analyze_videos(
    videos: list[dict[str, Any]],
    tier_map: dict[str, str],
    top_k_for_demand: int,
    today: datetime,
) -> dict[str, Any]:
    """Compute demand_score, tier hits, untracked-channel list."""
    # Demand sub-signal: median view_count of the top-K.
    top = videos[:top_k_for_demand]
    views = [v["view_count"] for v in top if v.get("view_count")]
    median_views = statistics.median(views) if views else None
    demand = view_count_to_demand(median_views)

    tier_b: list[dict[str, Any]] = []
    tier_c: list[dict[str, Any]] = []
    untracked: list[dict[str, Any]] = []

    for v in videos:
        h = v.get("channel_handle")
        tier = tier_map.get(h) if h else None
        days_ago = days_between(v.get("upload_date"), today)
        record = {
            "video_id": v.get("id"),
            "title": v.get("title"),
            "handle": h,
            "channel": v.get("channel"),
            "view_count": v.get("view_count"),
            "upload_date": v.get("upload_date"),
            "days_ago": days_ago,
        }
        if tier == "B":
            tier_b.append(record)
        elif tier == "C":
            tier_c.append(record)
        else:
            if h:
                untracked.append(record)

    return {
        "demand_score": demand,
        "median_views_top_k": int(median_views) if median_views else 0,
        "top_k_for_demand": top_k_for_demand,
        "tier_b_hits": tier_b,
        "tier_c_hits": tier_c,
        "untracked_channels": untracked,
    }


def search_and_analyze(
    cid: str,
    title: str,
    top_k: int,
    top_k_for_demand: int,
    tier_map: dict[str, str],
    today: datetime,
) -> dict[str, Any]:
    query = title_to_query(title)
    videos, err = search_one(query, top_k=top_k)
    analysis = analyze_videos(videos, tier_map, top_k_for_demand, today)
    return {
        "id": cid,
        "title": title,
        "query": query,
        "videos": videos,
        "error": err,
        **analysis,
    }


def load_candidates(path: Path) -> list[tuple[str, str]]:
    """Returns [(candidate_id, title)] from a shortlist.json."""
    data = json.loads(path.read_text())
    if isinstance(data, dict) and "candidates" in data:
        return [(c["id"], c["title"]) for c in data["candidates"]]
    if isinstance(data, list):
        return [(c["id"], c["title"]) for c in data]
    raise ValueError(f"unrecognized shape in {path}")


def archive_path_for(cfg: dict[str, Any], date_str: str) -> Path:
    archive_dir = HERE / cfg.get("paths", {}).get("archive_dir", "data/archive")
    return archive_dir / date_str / "ytsearch.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, help="shortlist.json path")
    parser.add_argument("--query", help="run a single ad-hoc query and exit")
    parser.add_argument("--top-k", type=int, default=10, help="top results to fetch (default 10)")
    parser.add_argument("--top-k-for-demand", type=int, default=5,
                        help="how many of the top-K feed the demand median (default 5)")
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument("--refresh", action="store_true",
                        help="re-search candidates already cached in today's ytsearch.json")
    parser.add_argument("--date",
                        help="archive date YYYY-MM-DD (default today UTC)")
    args = parser.parse_args()

    cfg = json.loads(CONFIG_PATH.read_text())
    tier_map = load_tier_map(cfg)
    today = datetime.now(timezone.utc)

    # Single-query probe mode.
    if args.query:
        videos, err = search_one(args.query, top_k=args.top_k)
        if err:
            print(f"error: {err}", file=sys.stderr)
            return 1
        analysis = analyze_videos(videos, tier_map, args.top_k_for_demand, today)
        print(json.dumps({"query": args.query, "videos": videos, **analysis},
                         indent=2, ensure_ascii=False))
        return 0

    if not args.candidates:
        parser.error("--candidates or --query required")

    candidates = load_candidates(args.candidates)
    date_str = args.date or today.strftime("%Y-%m-%d")
    out_path = archive_path_for(cfg, date_str)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    existing: dict[str, Any] = {}
    if out_path.exists():
        existing = json.loads(out_path.read_text()).get("results", {})

    todo: list[tuple[str, str]] = []
    skipped = 0
    for cid, title in candidates:
        if cid in existing and not args.refresh:
            skipped += 1
            continue
        todo.append((cid, title))

    print(
        f"Cold-searching {len(todo)} candidates "
        f"(skipped {skipped} cached, {args.concurrency}-way parallel)...",
        file=sys.stderr,
    )

    started = time.monotonic()
    results: dict[str, Any] = dict(existing)
    failed = 0

    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {
            pool.submit(
                search_and_analyze,
                cid,
                title,
                args.top_k,
                args.top_k_for_demand,
                tier_map,
                today,
            ): (cid, title)
            for cid, title in todo
        }
        done = 0
        for fut in as_completed(futures):
            cid, title = futures[fut]
            try:
                rec = fut.result()
            except Exception as exc:
                rec = {"id": cid, "title": title, "error": f"unexpected: {exc!r}"}
            done += 1
            if rec.get("error"):
                failed += 1
            results[cid] = rec
            elapsed = time.monotonic() - started
            d = rec.get("demand_score", 0)
            n = len(rec.get("videos", []))
            tb = len(rec.get("tier_b_hits", []))
            tc = len(rec.get("tier_c_hits", []))
            err = rec.get("error", "")
            mv = rec.get("median_views_top_k", 0)
            print(
                f"  [{elapsed:6.1f}s] {done:3d}/{len(todo)}  "
                f"d={d}  med={mv:>10,}  n={n:2d}  B={tb} C={tc}  "
                f"{'FAIL ' + err if err else title[:55]}",
                file=sys.stderr,
            )

    elapsed_total = time.monotonic() - started

    payload = {
        "generated_at": today.isoformat(timespec="seconds"),
        "candidate_count": len(candidates),
        "fresh_count": len(todo),
        "cached_count": skipped,
        "failed_count": failed,
        "elapsed_seconds": round(elapsed_total, 1),
        "top_k": args.top_k,
        "top_k_for_demand": args.top_k_for_demand,
        "results": results,
    }
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))

    print(
        f"\nDone in {elapsed_total:.1f}s. "
        f"{len(todo) - failed}/{len(todo)} ok, "
        f"{skipped} cached. → {out_path}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
