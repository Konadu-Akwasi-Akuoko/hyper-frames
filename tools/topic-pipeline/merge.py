#!/usr/bin/env python3
"""Merge a daily shortlist + LLM judgment + cold-search + autocomplete results
into the persistent inbox.json. Composes the v2 6-axis composite per RUBRIC.md.

Inputs (per-day, all optional except shortlist):
  - shortlist.json    (from fetch.py)
  - judgment.json     (from the Claude judgment phase)
  - ytsearch.json     (from cold_search.py)
  - autocomplete.json (from autocomplete.py)

Output:
  - inbox.json (append-only by id; preserves user_status / user_notes)

v2 composite (RUBRIC.md):
    composite = (demand + evergreen + yt_competition
               + audience_reach + curiosity_hook + computing_depth) / 1.2

Where:
  demand            = aggregator_breadth (0-4, fetch.py)
                    + cold_search demand_score (0-5)
                    + autocomplete_score (0-3)
                    + tier_b_hit (0-8, derived from cold-search Tier B view counts)
  yt_competition    = LLM raw score, with 30-day cooldown overlay applied
  audience_reach    = LLM, per angle (0-20)
  curiosity_hook    = LLM, per angle (0-20)
  computing_depth   = LLM, per angle (0-20)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INBOX_VERSION = 2  # bumped: v2 rubric, schema differs from v1

# Tier B hit → demand sub-cap mapping (max 8 per RUBRIC.md).
# Indexed by max view_count of the most-viewed Tier B video appearing in
# cold-search results.
TIER_B_VIEW_BANDS = [
    (1_000_000, 8),
    (  100_000, 5),
    (   10_000, 3),
    (        1, 1),
]


def tier_b_hit_score(tier_b_hits: list[dict]) -> int:
    if not tier_b_hits:
        return 0
    max_views = max((h.get("view_count") or 0) for h in tier_b_hits)
    for threshold, score in TIER_B_VIEW_BANDS:
        if max_views >= threshold:
            return score
    return 0


def load_json(p: Path) -> dict:
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def empty_inbox() -> dict:
    return {"version": INBOX_VERSION, "last_updated": None, "candidates": {}}


def compose_demand(
    aggregator_breadth: int,
    cold_search_rec: dict | None,
    autocomplete_rec: dict | None,
    angle_demand_rec: dict | None = None,
) -> dict[str, Any]:
    """Build the 4-sub-cap demand axis. Returns
    {"demand": 0-20, "demand_sub_caps": {...}}.

    Per RUBRIC.md: aggregator_breadth (0-4) + cold_search (0-5) + autocomplete (0-3)
    + tier_b_hit (0-8) — sums to 0-20.

    `angle_demand_rec` (optional, from angle_demand.py) lifts cold_search,
    autocomplete, and tier_b_hit when an LLM-proposed angle out-probes the
    title. Captures cases where jargon-heavy titles ('WEI repackaged')
    underscore demand vs. how viewers actually search ('how captchas work').
    The lift is per-sub-cap max — never decreases a title-probe score.
    """
    cs = cold_search_rec or {}
    ac = autocomplete_rec or {}
    ad = angle_demand_rec or {}
    title_cold = int(cs.get("demand_score", 0))
    title_auto = int(ac.get("autocomplete_score", 0))
    title_tb = tier_b_hit_score(cs.get("tier_b_hits", []))

    cold_score = max(title_cold, int(ad.get("best_demand_score", 0)))
    auto_score = max(title_auto, int(ad.get("best_autocomplete_score", 0)))
    angle_tb_views = int(ad.get("best_tier_b_views", 0))
    angle_tb = tier_b_hit_score([{"view_count": angle_tb_views}]) if angle_tb_views else 0
    tb_score = max(title_tb, angle_tb)

    breadth = max(0, min(4, int(aggregator_breadth)))
    demand = min(20, breadth + cold_score + auto_score + tb_score)
    return {
        "demand": demand,
        "demand_sub_caps": {
            "aggregator_breadth": breadth,
            "cold_search": cold_score,
            "autocomplete": auto_score,
            "tier_b_hit": tb_score,
        },
        "demand_sub_cap_sources": {
            "cold_search": "angle" if cold_score > title_cold else "title",
            "autocomplete": "angle" if auto_score > title_auto else "title",
            "tier_b_hit": "angle" if tb_score > title_tb else "title",
        },
    }


def apply_cooldown_overlay(yt_raw: int, cold_search_rec: dict | None) -> dict[str, Any]:
    """Per RUBRIC.md, when a tracked channel covered the topic recently:
    - Tier B within 30 days → force yt_competition ≤ 4
    - Tier C within 14 days → −4
    - Tier C within 30 days → −2
    Floors at 0. Returns {yt_competition_final, cooldown_reason}.
    """
    final = max(0, int(yt_raw))
    reason = None
    if not cold_search_rec:
        return {"yt_competition_final": final, "cooldown_reason": None}

    def freshest(hits: list[dict]) -> int | None:
        days: list[int] = [int(d) for h in hits if (d := h.get("days_ago")) is not None]
        return min(days) if days else None

    tb_age = freshest(cold_search_rec.get("tier_b_hits", []))
    tc_age = freshest(cold_search_rec.get("tier_c_hits", []))

    if tb_age is not None and tb_age <= 30:
        if final > 4:
            reason = f"Tier B coverage {tb_age}d ago — capped at 4"
            final = 4
        else:
            reason = f"Tier B coverage {tb_age}d ago (already ≤4)"
    elif tc_age is not None and tc_age <= 14:
        new_final = max(0, final - 4)
        reason = f"Tier C coverage {tc_age}d ago — −4"
        final = new_final
    elif tc_age is not None and tc_age <= 30:
        new_final = max(0, final - 2)
        reason = f"Tier C coverage {tc_age}d ago — −2"
        final = new_final

    return {"yt_competition_final": final, "cooldown_reason": reason}


def compose_v2_angle(angle: dict, demand: int, evergreen: int, yt_final: int) -> dict:
    """Apply the 6-axis composite to a per-angle judgment record."""
    s = angle.get("scores") or {}
    audience = int(s.get("audience_reach") or 0)
    curiosity = int(s.get("curiosity_hook") or 0)
    depth = int(s.get("computing_depth") or 0)
    raw_total = demand + evergreen + yt_final + audience + curiosity + depth
    return {
        **angle,
        "scores": {
            "audience_reach": audience,
            "curiosity_hook": curiosity,
            "computing_depth": depth,
        },
        "raw_total": raw_total,
        "composite": round(raw_total / 1.2),
    }


def merge_candidate(
    existing: dict | None,
    fresh: dict,
    judgment: dict | None,
    cold_search_rec: dict | None,
    autocomplete_rec: dict | None,
    angle_demand_rec: dict | None = None,
) -> dict:
    """Merge fresh shortlist data + signals into the existing inbox record.
    Preserves user_*. Recomputes the v2 composite end-to-end."""
    now = datetime.now(timezone.utc).isoformat()

    base = existing or {
        "id": fresh["id"],
        "title": fresh["title"],
        "url": fresh["url"],
        "canonical_url": fresh.get("canonical_url"),
        "sources": [],
        "per_source": [],
        "tags": [],
        "first_seen_at": now,
        "scores": {},
        "angles": [],
        "best_angle_index": None,
        "best_composite": 0,
        "user_status": None,
        "user_selected_angle_index": None,
        "user_notes": None,
    }

    # Source merge (idempotent)
    base["sources"] = sorted(set(base.get("sources", [])) | set(fresh.get("sources", [])))
    seen_keys = {(p.get("source"), p.get("external_id")) for p in base.get("per_source", [])}
    for ps in fresh.get("per_source", []):
        key = (ps.get("source"), ps.get("external_id"))
        if key not in seen_keys:
            base["per_source"].append(ps)
            seen_keys.add(key)

    base["tags"] = sorted(set(base.get("tags", [])) | set(fresh.get("tags", [])))
    base["last_seen_at"] = now
    base["title"] = fresh.get("title") or base.get("title")
    base["url"] = fresh.get("url") or base.get("url")
    base["canonical_url"] = fresh.get("canonical_url") or base.get("canonical_url")

    # Mechanical inputs from fresh shortlist (v2)
    fresh_scores = fresh.get("scores") or {}
    # aggregator_breadth: prefer the precomputed field from fetch.py v2,
    # else derive it from the source list (handles v1 shortlists).
    raw_breadth = fresh_scores.get("aggregator_breadth")
    if raw_breadth is None:
        aggregator_breadth = min(4, len(fresh.get("sources", [])))
    else:
        aggregator_breadth = int(raw_breadth)
    evergreen = int(fresh_scores.get("evergreen", base.get("scores", {}).get("evergreen", 14)))

    # Compose the demand axis from the four sub-caps. Angle-demand probes
    # (when present) lift cold_search / autocomplete / tier_b_hit if a
    # generated angle scored higher than the title-derived query.
    demand_info = compose_demand(
        aggregator_breadth, cold_search_rec, autocomplete_rec, angle_demand_rec
    )

    # YT competition: LLM raw, then cooldown overlay
    yt_raw = int((judgment or {}).get("yt_competition", 10))
    cooldown = apply_cooldown_overlay(yt_raw, cold_search_rec)

    base["scores"] = {
        "aggregator_breadth": aggregator_breadth,
        "evergreen": evergreen,
        "demand": demand_info["demand"],
        "demand_sub_caps": demand_info["demand_sub_caps"],
        "demand_sub_cap_sources": demand_info.get("demand_sub_cap_sources", {}),
        "yt_competition_raw": yt_raw,
        "yt_competition": cooldown["yt_competition_final"],
        "cooldown_reason": cooldown["cooldown_reason"],
    }

    # Per-angle composition
    if judgment and judgment.get("angles"):
        new_angles = [
            compose_v2_angle(a,
                             demand=base["scores"]["demand"],
                             evergreen=evergreen,
                             yt_final=base["scores"]["yt_competition"])
            for a in judgment["angles"]
        ]
        base["angles"] = new_angles

    # Best angle / composite
    if base.get("angles"):
        composites = [a.get("composite", 0) for a in base["angles"]]
        best_idx = int(max(range(len(composites)), key=lambda i: composites[i]))
        base["best_angle_index"] = best_idx
        base["best_composite"] = composites[best_idx]
        base["pending_judgment"] = False
    else:
        # No angles yet: 3-axis floor (demand + evergreen + yt). Caps at /60,
        # rescaled by /1.2 so it sits on the same 0-100 axis as fully-judged
        # candidates. Marks pending_judgment so the dashboard can disambiguate.
        partial = base["scores"]["demand"] + evergreen + base["scores"]["yt_competition"]
        base["best_composite"] = round(partial / 1.2)
        base["best_angle_index"] = None
        base["pending_judgment"] = True

    # Strip stale v1 fields if present (curriculum_fit, pawel_filter)
    for stale in ("curriculum_fit", "pawel_filter"):
        base["scores"].pop(stale, None)
    for a in base.get("angles", []):
        if "scores" in a:
            for stale in ("curriculum_fit", "pawel_filter"):
                a["scores"].pop(stale, None)

    return base


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(Path(__file__).parent / "config.json"))
    ap.add_argument("--shortlist", required=True, help="Path to shortlist.json")
    ap.add_argument("--judgment", default=None, help="Path to judgment.json (optional)")
    ap.add_argument("--ytsearch", default=None, help="Path to ytsearch.json (optional)")
    ap.add_argument("--autocomplete", default=None, help="Path to autocomplete.json (optional)")
    ap.add_argument("--angle-demand", default=None,
                    help="Path to angle_demand.json (optional, lifts demand sub-caps "
                         "when an angle out-probes the title)")
    args = ap.parse_args()

    cfg_path = Path(args.config).resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    base_dir = cfg_path.parent
    inbox_path = (base_dir / cfg["paths"]["inbox_json"]).resolve()
    inbox_path.parent.mkdir(parents=True, exist_ok=True)

    shortlist = load_json(Path(args.shortlist).resolve())
    judgment = load_json(Path(args.judgment).resolve()) if args.judgment else None
    ytsearch = load_json(Path(args.ytsearch).resolve()) if args.ytsearch else None
    autocomplete = load_json(Path(args.autocomplete).resolve()) if args.autocomplete else None
    angle_demand = load_json(Path(args.angle_demand).resolve()) if args.angle_demand else None

    inbox = load_json(inbox_path) or empty_inbox()
    if "candidates" not in inbox:
        inbox = empty_inbox()
    inbox["version"] = INBOX_VERSION

    judgment_by_id = (judgment or {}).get("candidates", {})
    ytsearch_by_id = (ytsearch or {}).get("results", {})
    autocomplete_by_id = (autocomplete or {}).get("results", {})
    angle_demand_by_id = (angle_demand or {}).get("results", {})

    # Belt-and-suspenders for the "skip already-judged" rule. If a candidate
    # already has angles in inbox.json and judgment.json re-judged it anyway,
    # the LLM phase wasn't filtering its work upstream — flag it here so a
    # bad run is visible in the merge log instead of silently overwriting
    # validated angles with new (and possibly worse) ones.
    rejudged_warnings: list[str] = []
    for cid, j in judgment_by_id.items():
        if not j or not (j.get("angles") or []):
            continue
        existing = inbox.get("candidates", {}).get(cid)
        if existing and (existing.get("angles") or []) and not existing.get("pending_judgment"):
            rejudged_warnings.append(cid)
    if rejudged_warnings:
        print(
            f"[merge]   WARNING: {len(rejudged_warnings)} candidate(s) re-judged "
            f"despite already having angles in inbox; their angles will be replaced. "
            f"Run needs_judgment.py upstream to filter these out.",
            file=sys.stderr,
        )
        for cid in rejudged_warnings[:5]:
            existing = inbox.get("candidates", {}).get(cid) or {}
            title = (existing.get("title") or "")[:70]
            print(f"           - {cid}  {title}", file=sys.stderr)

    added, updated, judged, with_cs, with_ac, with_ad = 0, 0, 0, 0, 0, 0
    angle_lifts = 0
    cooldown_triggered = 0
    for cand in shortlist.get("candidates", []):
        cid = cand["id"]
        was_new = cid not in inbox["candidates"]
        existing = inbox["candidates"].get(cid)
        j = judgment_by_id.get(cid)
        cs = ytsearch_by_id.get(cid)
        ac = autocomplete_by_id.get(cid)
        ad = angle_demand_by_id.get(cid)
        merged = merge_candidate(existing, cand, j, cs, ac, ad)
        inbox["candidates"][cid] = merged
        if was_new:
            added += 1
        else:
            updated += 1
        if j:
            judged += 1
        if cs:
            with_cs += 1
        if ac:
            with_ac += 1
        if ad:
            with_ad += 1
            sources = merged["scores"].get("demand_sub_cap_sources") or {}
            if any(v == "angle" for v in sources.values()):
                angle_lifts += 1
        if merged["scores"].get("cooldown_reason"):
            cooldown_triggered += 1

    inbox["last_updated"] = datetime.now(timezone.utc).isoformat()
    inbox_path.write_text(json.dumps(inbox, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[merge]   added={added} updated={updated} judged={judged}", file=sys.stderr)
    print(f"[merge]   with_cold_search={with_cs} with_autocomplete={with_ac} "
          f"with_angle_demand={with_ad} angle_lifts={angle_lifts} "
          f"cooldown_triggered={cooldown_triggered}", file=sys.stderr)
    print(f"[merge]   inbox total: {len(inbox['candidates'])}", file=sys.stderr)
    print(f"[wrote]   {inbox_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
