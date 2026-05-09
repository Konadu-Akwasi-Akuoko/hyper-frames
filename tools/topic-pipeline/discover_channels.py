#!/usr/bin/env python3
"""Auto-discover untracked niche channels by overlap analysis on cold-search results.

Walks one or more `ytsearch.json` archives (the per-day cold-search output)
and aggregates `untracked_channels[]` by handle. Channels that surface across
multiple distinct candidate searches — and especially across multiple days —
are the strongest signal that the channel sits inside this project's niche
and is a Tier B / Tier C candidate.

Filters out handles already in `config.json`'s reference_channels so the
report only contains genuinely new candidates.

Usage:
    # Scan every archived day under data/archive/
    python3 discover_channels.py

    # Scan a specific day or set of files
    python3 discover_channels.py --ytsearch data/archive/2026-05-08/ytsearch.json
    python3 discover_channels.py --ytsearch 'data/archive/2026-05-*/ytsearch.json'

    # Tighter relevance filter (default: appears under >=2 candidates)
    python3 discover_channels.py --min-overlap 3 --min-median-views 50000

Output: prints a ranked table to stdout, writes a JSON report alongside.
"""

from __future__ import annotations

import argparse
import glob
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config.json"


def load_known_handles(cfg: dict[str, Any]) -> set[str]:
    rc = cfg.get("reference_channels", {})
    out: set[str] = set()
    for group in ("style_reference", "watchlist"):
        for c in rc.get(group, []):
            h = (c.get("handle") or "").lower()
            if h:
                out.add(h)
    return out


def expand_paths(patterns: list[str], default_root: Path) -> list[Path]:
    if not patterns:
        files = sorted(default_root.glob("*/ytsearch.json"))
        return [p for p in files if p.is_file()]
    out: list[Path] = []
    for pat in patterns:
        matches = [Path(m) for m in glob.glob(pat)] or [Path(pat)]
        for m in matches:
            if m.is_file():
                out.append(m)
    # Dedup, keep order
    seen: set[Path] = set()
    deduped: list[Path] = []
    for p in out:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            deduped.append(p)
    return deduped


def aggregate(
    ytsearch_paths: list[Path],
    known_handles: set[str],
) -> dict[str, dict[str, Any]]:
    """Build per-handle aggregates across all input files.

    Each handle entry tracks:
    - distinct candidate ids it surfaced under (overlap signal)
    - distinct days (cross-day persistence)
    - all view counts seen (for median + max)
    - most recent upload (days_ago) and the corresponding video
    - sample of titles
    - channel display name (last seen)
    """
    by_handle: dict[str, dict[str, Any]] = defaultdict(lambda: {
        "candidate_ids": set(),
        "days_seen": set(),
        "views": [],
        "min_days_ago": None,
        "freshest_video": None,
        "channel": None,
        "sample_titles": [],
    })

    for path in ytsearch_paths:
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[discover] skip {path}: {e}", file=sys.stderr)
            continue
        # Day tag = parent dir name (YYYY-MM-DD) so cross-day uniqueness works.
        day_tag = path.parent.name
        results = doc.get("results", {}) or {}
        for cid, rec in results.items():
            for u in rec.get("untracked_channels", []) or []:
                h = (u.get("handle") or "").lower().strip()
                if not h or h in known_handles:
                    continue
                agg = by_handle[h]
                agg["candidate_ids"].add(cid)
                agg["days_seen"].add(day_tag)
                vc = u.get("view_count")
                if isinstance(vc, int) and vc > 0:
                    agg["views"].append(vc)
                days_ago = u.get("days_ago")
                if days_ago is not None:
                    if agg["min_days_ago"] is None or days_ago < agg["min_days_ago"]:
                        agg["min_days_ago"] = days_ago
                        agg["freshest_video"] = {
                            "video_id": u.get("video_id"),
                            "title": u.get("title"),
                            "view_count": vc,
                            "upload_date": u.get("upload_date"),
                            "days_ago": days_ago,
                        }
                if u.get("channel"):
                    agg["channel"] = u["channel"]
                if u.get("title") and len(agg["sample_titles"]) < 5:
                    agg["sample_titles"].append(u["title"])
    return by_handle


def rank_channels(
    by_handle: dict[str, dict[str, Any]],
    min_overlap: int,
    min_median_views: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for h, agg in by_handle.items():
        overlap = len(agg["candidate_ids"])
        if overlap < min_overlap:
            continue
        views = agg["views"] or [0]
        median_views = int(statistics.median(views))
        if median_views < min_median_views:
            continue
        # Score: overlap dominates, view-strength as tiebreak.
        # log10 of median views keeps the dynamic range sane.
        from math import log10
        view_strength = log10(max(1, median_views))
        days_seen = len(agg["days_seen"])
        score = overlap * 10 + days_seen * 5 + view_strength
        rows.append({
            "handle": h,
            "channel": agg["channel"],
            "overlap": overlap,
            "days_seen": days_seen,
            "median_views": median_views,
            "max_views": int(max(views)),
            "freshest_video": agg["freshest_video"],
            "sample_titles": agg["sample_titles"],
            "score": round(score, 2),
        })
    rows.sort(key=lambda r: (r["score"], r["overlap"], r["max_views"]), reverse=True)
    return rows


def print_table(rows: list[dict[str, Any]], limit: int = 30) -> None:
    if not rows:
        print("No discovery candidates found above thresholds.", file=sys.stderr)
        return
    print(file=sys.stderr)
    header = f"{'handle':<32} {'overlap':>7} {'days':>4} {'medV':>10} {'maxV':>10}  {'channel'}"
    print(header, file=sys.stderr)
    print("-" * len(header), file=sys.stderr)
    for r in rows[:limit]:
        print(
            f"{r['handle']:<32} {r['overlap']:>7} {r['days_seen']:>4} "
            f"{r['median_views']:>10,} {r['max_views']:>10,}  {r['channel'] or ''}",
            file=sys.stderr,
        )
    if len(rows) > limit:
        print(f"... ({len(rows) - limit} more)", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--ytsearch", action="append", default=None,
                    help="Path or glob to a ytsearch.json (repeatable). "
                         "Default: every data/archive/*/ytsearch.json.")
    ap.add_argument("--out", default=None,
                    help="Output JSON path (default: data/discovered_channels.json)")
    ap.add_argument("--min-overlap", type=int, default=2,
                    help="Min distinct candidates a channel must surface under (default: 2)")
    ap.add_argument("--min-median-views", type=int, default=10_000,
                    help="Min median view_count across surfaced videos (default: 10000)")
    ap.add_argument("--limit", type=int, default=30,
                    help="Max rows printed to stderr (default: 30)")
    args = ap.parse_args()

    cfg_path = Path(args.config).resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    base_dir = cfg_path.parent
    archive_root = base_dir / cfg["paths"]["archive_dir"]
    out_path = Path(args.out).resolve() if args.out else (base_dir / "data" / "discovered_channels.json")

    paths = expand_paths(args.ytsearch or [], archive_root)
    if not paths:
        print(f"[discover] no ytsearch.json files found under {archive_root}", file=sys.stderr)
        return 1

    print(f"[discover] scanning {len(paths)} ytsearch archive(s)", file=sys.stderr)
    known = load_known_handles(cfg)
    by_handle = aggregate(paths, known)
    rows = rank_channels(by_handle, args.min_overlap, args.min_median_views)

    print(f"[discover] {len(by_handle)} unknown handles total | {len(rows)} pass filters "
          f"(overlap >= {args.min_overlap}, median views >= {args.min_median_views:,})",
          file=sys.stderr)
    print_table(rows, args.limit)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scanned": [str(p) for p in paths],
        "thresholds": {
            "min_overlap": args.min_overlap,
            "min_median_views": args.min_median_views,
        },
        "candidates": rows,
    }
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[wrote] {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
