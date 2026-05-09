#!/usr/bin/env python3
"""Emit the subset of shortlist candidate ids that still need LLM judgment.

The "skip already-judged" rule used to live only in SCHEDULED_TASK_PROMPT.md,
which meant a forgetful run could re-judge every candidate. This helper is the
code-enforced version: it diffs `shortlist.json` against `inbox.json` and
prints the ids whose `angles` array is missing or empty (i.e. genuinely
unjudged).

The scheduled task can pipe this into its WebFetch loop so judgment only ever
runs on candidates that need it.

Output formats:
    --format ids   (default) one candidate id per line, suitable for `xargs`
                   or shell loops
    --format json  array-of-objects with id, title, url, sources — handy when
                   driving the judgment loop directly from the JSON output
    --format table human-readable preview on stderr only

Examples:
    python3 needs_judgment.py --shortlist data/archive/2026-05-08/shortlist.json
    python3 needs_judgment.py --shortlist ... --format json > pending.json
    python3 needs_judgment.py --shortlist ... --format table  # preview only
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config.json"


def already_judged(rec: dict[str, Any] | None) -> bool:
    """A candidate is already-judged iff inbox carries a non-empty angles
    array. `pending_judgment=True` (e.g. dashboard-queued YouTube candidates)
    explicitly counts as not-yet-judged even if the record exists."""
    if not rec:
        return False
    if rec.get("pending_judgment"):
        return False
    angles = rec.get("angles") or []
    return len(angles) > 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--shortlist", required=True,
                    help="Path to data/archive/YYYY-MM-DD/shortlist.json")
    ap.add_argument("--inbox", default=None,
                    help="Path to inbox.json (default: from config)")
    ap.add_argument("--format", choices=("ids", "json", "table"), default="ids")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    base_dir = Path(args.config).resolve().parent
    inbox_path = (
        Path(args.inbox).resolve() if args.inbox
        else (base_dir / cfg["paths"]["inbox_json"]).resolve()
    )
    shortlist_path = Path(args.shortlist).resolve()

    if not shortlist_path.exists():
        print(f"[needs-judgment] no shortlist at {shortlist_path}", file=sys.stderr)
        return 1

    shortlist = json.loads(shortlist_path.read_text(encoding="utf-8"))
    inbox = (json.loads(inbox_path.read_text(encoding="utf-8"))
             if inbox_path.exists() else {})
    inbox_cands = inbox.get("candidates") or {}

    pending: list[dict[str, Any]] = []
    skipped = 0
    for cand in shortlist.get("candidates", []):
        cid = cand["id"]
        existing = inbox_cands.get(cid)
        if already_judged(existing):
            skipped += 1
            continue
        pending.append({
            "id": cid,
            "title": cand.get("title") or "",
            "url": cand.get("url") or "",
            "sources": list(cand.get("sources") or []),
            "mechanical_subtotal": cand.get("mechanical_subtotal", 0),
        })

    print(f"[needs-judgment] shortlist={len(shortlist.get('candidates', []))} "
          f"pending={len(pending)} skipped={skipped} (already-judged)",
          file=sys.stderr)

    if args.format == "ids":
        for p in pending:
            print(p["id"])
    elif args.format == "json":
        json.dump(pending, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:  # table
        for p in pending:
            print(f"  {p['mechanical_subtotal']:>3}  {p['id']}  "
                  f"{p['title'][:80]}  ({','.join(p['sources'])})",
                  file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
