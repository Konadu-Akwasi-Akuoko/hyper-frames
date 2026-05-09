#!/usr/bin/env python3
"""Aging / graveyard prune for inbox.json.

Candidates accumulate in `data/inbox.json` daily. Without periodic pruning
the dashboard grows unbounded and old, never-reviewed entries crowd out fresh
ones. This tool moves stale candidates from `inbox.json` to `graveyard.json`
based on age × current status:

    unreviewed (no user_status) + age >= 30 days → graveyard
    user_status == "later"      + age >= 60 days → graveyard
    user_status == "pass"       + age >= 90 days → graveyard

`go` and `shipped` are never pruned — those are explicit "keep" signals.

The graveyard file preserves the full record + adds `graveyarded_at` and
`graveyard_reason` so nothing is lost; rerunning is idempotent because moved
candidates no longer appear in inbox.

Usage:
    python3 prune.py                          # apply defaults
    python3 prune.py --dry-run                # show what would move
    python3 prune.py --age-unreviewed 21      # tighter cutoff
    python3 prune.py --age-pass 0             # archive every pass immediately
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config.json"


def parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def candidate_age_days(c: dict[str, Any], now: datetime) -> int | None:
    """Use the most-recent activity timestamp available — first_seen_at if
    that's all we have, last_seen_at if the candidate was re-surfaced. The
    later timestamp better reflects "still in rotation" vs. truly stale."""
    last = parse_iso(c.get("last_seen_at")) or parse_iso(c.get("first_seen_at"))
    if last is None:
        return None
    return (now - last).days


def prune_reason(c: dict[str, Any], age_days: int,
                 unreviewed_max: int, later_max: int, pass_max: int) -> str | None:
    status = (c.get("user_status") or "").strip().lower()
    if status in ("go", "shipped"):
        return None
    if not status and age_days >= unreviewed_max:
        return f"unreviewed for {age_days} days (>= {unreviewed_max})"
    if status == "later" and age_days >= later_max:
        return f"deferred for {age_days} days (>= {later_max})"
    if status == "pass" and age_days >= pass_max:
        return f"passed {age_days} days ago (>= {pass_max})"
    return None


def load_existing_graveyard(graveyard_path: Path) -> dict[str, Any]:
    if not graveyard_path.exists():
        return {"version": 1, "last_updated": None, "candidates": {}}
    try:
        doc = json.loads(graveyard_path.read_text(encoding="utf-8"))
        if "candidates" not in doc:
            doc["candidates"] = {}
        return doc
    except Exception:
        return {"version": 1, "last_updated": None, "candidates": {}}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--age-unreviewed", type=int, default=30,
                    help="Days before unreviewed candidates graveyard (default: 30)")
    ap.add_argument("--age-later", type=int, default=60,
                    help="Days before 'later' candidates graveyard (default: 60)")
    ap.add_argument("--age-pass", type=int, default=90,
                    help="Days before 'pass' candidates graveyard (default: 90)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print what would move without writing files")
    args = ap.parse_args()

    cfg_path = Path(args.config).resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    base_dir = cfg_path.parent
    inbox_path = (base_dir / cfg["paths"]["inbox_json"]).resolve()
    graveyard_path = inbox_path.with_name("graveyard.json")

    if not inbox_path.exists():
        print(f"[prune] no inbox at {inbox_path}", file=sys.stderr)
        return 1

    inbox = json.loads(inbox_path.read_text(encoding="utf-8"))
    cands = dict(inbox.get("candidates") or {})
    now = datetime.now(timezone.utc)
    moved: list[tuple[str, str]] = []  # (cid, reason)
    unaged = 0
    for cid, c in list(cands.items()):
        age = candidate_age_days(c, now)
        if age is None:
            unaged += 1
            continue
        reason = prune_reason(c, age, args.age_unreviewed, args.age_later, args.age_pass)
        if reason:
            moved.append((cid, reason))

    print(f"[prune] inbox={len(cands)} unaged={unaged} eligible={len(moved)}", file=sys.stderr)
    by_status: dict[str, int] = {}
    for cid, reason in moved:
        s = (cands[cid].get("user_status") or "unreviewed")
        by_status[s] = by_status.get(s, 0) + 1
    if by_status:
        print(f"[prune] by status: {by_status}", file=sys.stderr)
    for cid, reason in moved[:10]:
        title = (cands[cid].get("title") or "").replace("\n", " ")[:70]
        print(f"  - {title}  [{reason}]", file=sys.stderr)
    if len(moved) > 10:
        print(f"  ... ({len(moved) - 10} more)", file=sys.stderr)

    if args.dry_run:
        print("[prune] --dry-run: no files written", file=sys.stderr)
        return 0
    if not moved:
        print("[prune] nothing to move", file=sys.stderr)
        return 0

    graveyard = load_existing_graveyard(graveyard_path)
    g_cands = graveyard.setdefault("candidates", {})
    moved_at = now.isoformat(timespec="seconds")
    for cid, reason in moved:
        rec = cands.pop(cid)
        rec["graveyarded_at"] = moved_at
        rec["graveyard_reason"] = reason
        g_cands[cid] = rec

    graveyard["last_updated"] = moved_at
    inbox["candidates"] = cands
    inbox["last_updated"] = moved_at

    inbox_path.write_text(json.dumps(inbox, indent=2, ensure_ascii=False), encoding="utf-8")
    graveyard_path.write_text(json.dumps(graveyard, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[prune] moved {len(moved)} -> {graveyard_path}", file=sys.stderr)
    print(f"[prune] inbox now has {len(cands)} candidates", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
