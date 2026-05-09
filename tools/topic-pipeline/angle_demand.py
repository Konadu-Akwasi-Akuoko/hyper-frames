#!/usr/bin/env python3
"""Angle-aware demand probing.

Title-derived demand under-scores jargon-heavy candidates (e.g. "WEI
repackaged" probes "wei repackaged" — nobody types that into YouTube; viewers
actually search "captcha"). After judgment, each candidate has 1–3 LLM-proposed
angles whose titles are search-shaped. Re-probe demand against those, then
take the per-candidate max as the demand-axis input.

Inputs:
- judgment.json (per-candidate angles[])

For each candidate × angle, runs:
- cold_search.search_one + analyze_videos (gives demand_score + tier_b_hits)
- autocomplete.analyze_one (gives autocomplete_score)

Writes data/archive/YYYY-MM-DD/angle_demand.json:
{
  "generated_at": iso,
  "results": {
    "<cid>": {
      "best_demand_score": int,           # 0-5, max across angles
      "best_autocomplete_score": int,     # 0-3, max across angles
      "best_tier_b_views": int,           # max view_count of any tier-B hit
                                          # found across the angle probes
                                          # (feeds tier_b_hit sub-cap in merge)
      "winning_demand_angle": str,        # angle title that produced best demand
      "winning_autocomplete_angle": str,
      "per_angle": [
        {"title", "query", "demand_score", "median_views_top_k",
         "tier_b_hits": [...], "autocomplete_score", "best_match"},
        ...
      ]
    }
  }
}

merge.py reads this and uses:
    cold_search_score = max(title_probe, angle_probe.best_demand_score)
    autocomplete_score = max(title_probe, angle_probe.best_autocomplete_score)
    tier_b_views_for_subcap = max(title_probe_tier_b_views, angle_probe.best_tier_b_views)

Usage:
    python3 angle_demand.py                        # latest archive
    python3 angle_demand.py --date 2026-05-08
    python3 angle_demand.py --top-n 20             # only top-N by mechanical score
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config.json"

# Sibling scripts, not a package. Make them importable when invoked directly.
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import autocomplete as ac_mod  # type: ignore[import-not-found]  # noqa: E402
import cold_search as cs_mod  # type: ignore[import-not-found]  # noqa: E402


def latest_archive_dir(archive_root: Path) -> Path | None:
    days = sorted(p for p in archive_root.iterdir() if p.is_dir())
    return days[-1] if days else None


def load_shortlist_order(shortlist_path: Path) -> list[str]:
    """Return candidate ids in mechanical-rank order (highest first)."""
    if not shortlist_path.exists():
        return []
    doc = json.loads(shortlist_path.read_text(encoding="utf-8"))
    cands = doc.get("candidates", []) if isinstance(doc, dict) else doc
    return [c["id"] for c in cands]


def probe_angle(cid: str, angle_title: str, top_k: int, top_k_for_demand: int,
                tier_map: dict[str, str], today: datetime) -> dict[str, Any]:
    """Run cold_search + autocomplete on a single angle title."""
    query = cs_mod.title_to_query(angle_title)
    videos, err = cs_mod.search_one(query, top_k=top_k)
    if err or not videos:
        cs_analysis = {
            "demand_score": 0,
            "median_views_top_k": 0,
            "tier_b_hits": [],
            "tier_c_hits": [],
            "untracked_channels": [],
            "error": err,
        }
    else:
        cs_analysis = cs_mod.analyze_videos(videos, tier_map, top_k_for_demand, today)

    ac_rec = ac_mod.analyze_one(cid, angle_title)
    return {
        "title": angle_title,
        "query": query,
        "demand_score": int(cs_analysis.get("demand_score") or 0),
        "median_views_top_k": int(cs_analysis.get("median_views_top_k") or 0),
        "tier_b_hits": cs_analysis.get("tier_b_hits") or [],
        "tier_c_hits": cs_analysis.get("tier_c_hits") or [],
        "autocomplete_score": int(ac_rec.get("autocomplete_score") or 0),
        "best_match": ac_rec.get("best_match"),
        "error": cs_analysis.get("error"),
    }


def aggregate_per_candidate(per_angle: list[dict[str, Any]]) -> dict[str, Any]:
    if not per_angle:
        return {
            "best_demand_score": 0,
            "best_autocomplete_score": 0,
            "best_tier_b_views": 0,
            "winning_demand_angle": None,
            "winning_autocomplete_angle": None,
            "per_angle": [],
        }
    best_d = max(per_angle, key=lambda a: a["demand_score"])
    best_a = max(per_angle, key=lambda a: a["autocomplete_score"])
    tb_views = 0
    for a in per_angle:
        for h in a.get("tier_b_hits") or []:
            v = h.get("view_count") or 0
            if v > tb_views:
                tb_views = v
    return {
        "best_demand_score": best_d["demand_score"],
        "best_autocomplete_score": best_a["autocomplete_score"],
        "best_tier_b_views": tb_views,
        "winning_demand_angle": best_d["title"],
        "winning_autocomplete_angle": best_a["title"],
        "per_angle": per_angle,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--date", default=None,
                    help="YYYY-MM-DD archive day (default: latest)")
    ap.add_argument("--top-n", type=int, default=0,
                    help="Only probe the top-N candidates by shortlist rank "
                         "(default: 0 = all)")
    ap.add_argument("--top-k", type=int, default=10,
                    help="ytsearch top-K per probe (default: 10)")
    ap.add_argument("--top-k-for-demand", type=int, default=5)
    ap.add_argument("--concurrency", type=int, default=4,
                    help="Parallel candidate workers (default: 4)")
    ap.add_argument("--refresh", action="store_true",
                    help="Re-probe even if angle_demand.json already has the cid")
    args = ap.parse_args()

    cfg_path = Path(args.config).resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    base_dir = cfg_path.parent
    archive_root = base_dir / cfg["paths"]["archive_dir"]

    if args.date:
        day_dir = archive_root / args.date
    else:
        day_dir = latest_archive_dir(archive_root) or archive_root / datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not day_dir.exists():
        print(f"[angle_demand] no archive at {day_dir}", file=sys.stderr)
        return 1

    judgment_path = day_dir / "judgment.json"
    shortlist_path = day_dir / "shortlist.json"
    out_path = day_dir / "angle_demand.json"

    if not judgment_path.exists():
        print(f"[angle_demand] missing {judgment_path}; run judgment first.", file=sys.stderr)
        return 1

    judgment = json.loads(judgment_path.read_text(encoding="utf-8"))
    judgment_cands = (judgment.get("candidates") or judgment) if isinstance(judgment, dict) else {}

    rank_order = load_shortlist_order(shortlist_path)
    rank_index = {cid: i for i, cid in enumerate(rank_order)}

    cids_with_angles: list[str] = [
        cid for cid, j in judgment_cands.items()
        if isinstance(j, dict) and (j.get("angles") or [])
    ]
    if args.top_n > 0:
        cids_with_angles.sort(key=lambda cid: rank_index.get(cid, 9999))
        cids_with_angles = cids_with_angles[: args.top_n]

    if not cids_with_angles:
        print("[angle_demand] no candidates with angles to probe", file=sys.stderr)
        return 0

    existing: dict[str, Any] = {}
    if out_path.exists() and not args.refresh:
        try:
            existing = (json.loads(out_path.read_text(encoding="utf-8")).get("results") or {})
        except Exception:
            existing = {}

    todo = [cid for cid in cids_with_angles if cid not in existing]
    print(
        f"[angle_demand] {len(cids_with_angles)} candidates with angles | "
        f"{len(todo)} to probe ({len(cids_with_angles) - len(todo)} cached)",
        file=sys.stderr,
    )

    tier_map = cs_mod.load_tier_map(cfg)
    today = datetime.now(timezone.utc)
    results: dict[str, Any] = dict(existing)

    def probe_candidate(cid: str) -> tuple[str, dict[str, Any]]:
        angles = judgment_cands[cid].get("angles") or []
        per_angle = []
        for a in angles:
            title = (a.get("title") or "").strip()
            if not title:
                continue
            try:
                rec = probe_angle(cid, title, args.top_k, args.top_k_for_demand, tier_map, today)
            except Exception as exc:
                rec = {"title": title, "error": f"probe failed: {exc!r}",
                       "demand_score": 0, "autocomplete_score": 0,
                       "tier_b_hits": [], "tier_c_hits": []}
            per_angle.append(rec)
        return cid, aggregate_per_candidate(per_angle)

    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {pool.submit(probe_candidate, cid): cid for cid in todo}
        for fut in as_completed(futures):
            cid, agg = fut.result()
            results[cid] = agg
            print(
                f"  {cid}: best_demand={agg['best_demand_score']} "
                f"best_ac={agg['best_autocomplete_score']} "
                f"tb_views={agg['best_tier_b_views']:,}",
                file=sys.stderr,
            )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "candidate_count": len(results),
        "results": results,
    }
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[wrote] {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
