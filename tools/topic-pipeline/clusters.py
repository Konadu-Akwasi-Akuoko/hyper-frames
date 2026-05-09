#!/usr/bin/env python3
"""Cluster candidates by topic similarity.

Reads `data/inbox.json`, tokenizes each candidate's title + tags + per-angle
lenses, computes pairwise Jaccard similarity, and groups candidates with
similarity >= threshold into clusters via union-find.

Surfaces redundant candidates (same article from N sources, near-duplicate
posts on the same news beat) so the user can pick the best framing per
topic instead of judging the same idea three times.

Output: `data/clusters.json`:
{
  "generated_at": iso,
  "threshold": float,
  "clusters": [
    {
      "id": int,
      "size": int,
      "members": [{id, title, sources, best_composite, status}, ...],
      "shared_tokens": [str, ...]   // top-K most-frequent tokens in cluster
    }, ...
  ],
  "singletons": int
}

Singletons (no near-neighbors) are counted but not emitted to keep the file
focused on actionable groups.

Usage:
    python3 clusters.py
    python3 clusters.py --threshold 0.35 --min-size 2
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config.json"

# Sibling scripts, not a package. Reuse tokenize() / jaccard() / STOPWORDS.
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import inspiration as insp  # type: ignore[import-not-found]  # noqa: E402


def candidate_blob(c: dict[str, Any]) -> str:
    """Build the text blob a candidate should be tokenized over.
    Title + tags + each angle's title + lens — captures both the source
    framing and the LLM-proposed reframings."""
    parts: list[str] = [c.get("title") or ""]
    parts.extend(c.get("tags") or [])
    for a in c.get("angles") or []:
        parts.append(a.get("title") or "")
        parts.append(a.get("lens") or "")
    return " ".join(p for p in parts if p)


class UnionFind:
    def __init__(self, ids: list[str]) -> None:
        self.parent: dict[str, str] = {i: i for i in ids}

    def find(self, x: str) -> str:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb

    def groups(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for i in self.parent:
            r = self.find(i)
            out.setdefault(r, []).append(i)
        return out


def shared_tokens(token_sets: list[set[str]], top_k: int = 6) -> list[str]:
    counter: Counter[str] = Counter()
    for ts in token_sets:
        counter.update(ts)
    return [t for t, _ in counter.most_common(top_k)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--threshold", type=float, default=0.25,
                    help="Min pairwise Jaccard to put two candidates in same "
                         "cluster. 0.25 is empirically clean (no false "
                         "positives on a 60-candidate inbox); 0.15 starts "
                         "merging unrelated candidates that share a single "
                         "stopword-adjacent token. (default: 0.25)")
    ap.add_argument("--min-size", type=int, default=2,
                    help="Minimum cluster size to emit (default: 2)")
    ap.add_argument("--out", default=None,
                    help="Output path (default: data/clusters.json)")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    base_dir = Path(args.config).resolve().parent
    inbox_path = (base_dir / cfg["paths"]["inbox_json"]).resolve()
    out_path = Path(args.out).resolve() if args.out else (base_dir / "data" / "clusters.json")

    if not inbox_path.exists():
        print(f"[clusters] no inbox at {inbox_path}", file=sys.stderr)
        return 1

    inbox = json.loads(inbox_path.read_text(encoding="utf-8"))
    cands = list((inbox.get("candidates") or {}).values())

    # Skip candidates the user has already passed/shipped — they're not
    # actionable for clustering decisions.
    cands = [c for c in cands if (c.get("user_status") or "") not in ("pass", "shipped")]
    if not cands:
        print("[clusters] no actionable candidates to cluster", file=sys.stderr)
        return 0

    ids = [c["id"] for c in cands]
    by_id = {c["id"]: c for c in cands}
    tokens_by_id: dict[str, set[str]] = {
        c["id"]: insp.tokenize(candidate_blob(c)) for c in cands
    }

    uf = UnionFind(ids)
    pair_sims: list[tuple[str, str, float]] = []
    n = len(ids)
    comparisons = 0
    for i in range(n):
        ai = ids[i]
        ta = tokens_by_id[ai]
        if not ta:
            continue
        for j in range(i + 1, n):
            bj = ids[j]
            tb = tokens_by_id[bj]
            if not tb:
                continue
            comparisons += 1
            sim = insp.jaccard(ta, tb)
            if sim >= args.threshold:
                uf.union(ai, bj)
                pair_sims.append((ai, bj, sim))

    groups = uf.groups()
    clusters_out: list[dict[str, Any]] = []
    cluster_id = 0
    for members in groups.values():
        if len(members) < args.min_size:
            continue
        cluster_id += 1
        member_records = []
        for mid in members:
            c = by_id[mid]
            member_records.append({
                "id": mid,
                "title": c.get("title"),
                "sources": list(c.get("sources") or []),
                "best_composite": c.get("best_composite") or 0,
                "status": c.get("user_status") or None,
                "pending_judgment": bool(c.get("pending_judgment")),
            })
        member_records.sort(key=lambda r: r["best_composite"], reverse=True)
        clusters_out.append({
            "id": cluster_id,
            "size": len(members),
            "members": member_records,
            "shared_tokens": shared_tokens([tokens_by_id[m] for m in members]),
        })

    clusters_out.sort(key=lambda c: c["size"], reverse=True)
    singletons = sum(1 for members in groups.values() if len(members) == 1)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "threshold": args.threshold,
        "min_size": args.min_size,
        "comparisons": comparisons,
        "clusters": clusters_out,
        "singletons": singletons,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[clusters] {len(cands)} candidates -> {len(clusters_out)} clusters "
          f"({singletons} singletons, {comparisons} comparisons)", file=sys.stderr)
    if clusters_out:
        print(file=sys.stderr)
        for c in clusters_out[:10]:
            top = c["members"][0]
            print(f"  cluster #{c['id']} ({c['size']} members, "
                  f"shared: {', '.join(c['shared_tokens'][:4])})", file=sys.stderr)
            print(f"    top: [{top['best_composite']}] {top['title'][:70]}", file=sys.stderr)
            for m in c["members"][1:]:
                print(f"         [{m['best_composite']}] {m['title'][:70]}", file=sys.stderr)
    print(f"[wrote] {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
