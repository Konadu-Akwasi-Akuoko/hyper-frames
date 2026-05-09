#!/usr/bin/env python3
"""Fetch trending tech content from HN, Reddit, Lobste.rs, daily.dev.

Dedupes by canonical URL, computes the v2 mechanical sub-caps
(aggregator_breadth 0-4, evergreen 0-20), and writes the day's outputs
under data/archive/YYYY-MM-DD/:
  - shortlist.json  top candidates by mechanical pre-rank
  - raw.json        full pre-filter set
  - run_meta.json   per-source counts and error strings

The LLM judgment phase (yt_competition, audience_reach, curiosity_hook,
computing_depth, angle generation) runs separately as a Claude task per
SCHEDULED_TASK_PROMPT.md; the remaining demand sub-caps (cold_search,
autocomplete, tier_b_hit) come from cold_search.py / autocomplete.py /
angle_demand.py and are composed in merge.py.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

USER_AGENT = "topic-pipeline/0.1 (https://github.com/hyper-frames; research script)"
TIMEOUT = 15


# ──────────────────────────────────────────────────────────────────────────
# HTTP helpers
# ──────────────────────────────────────────────────────────────────────────

def http_get(url: str, headers: dict[str, str] | None = None) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read()


def http_json(url: str, headers: dict[str, str] | None = None) -> Any:
    return json.loads(http_get(url, headers))


def http_post_json(url: str, body: dict[str, Any], headers: dict[str, str] | None = None) -> Any:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
            **(headers or {}),
        },
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read())


# ──────────────────────────────────────────────────────────────────────────
# URL canonicalization (so cross-source dedup works)
# ──────────────────────────────────────────────────────────────────────────

_TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "utm_id", "utm_name", "ref", "ref_src", "ref_url", "source",
    "fbclid", "gclid", "mc_cid", "mc_eid", "_gl", "igshid",
    "feature", "spm",
}


def canonicalize_url(url: str) -> str:
    try:
        p = urllib.parse.urlparse(url.strip())
    except Exception:
        return url
    # Drop fragment
    netloc = p.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    # Filter tracking params, sort the rest
    qs = urllib.parse.parse_qsl(p.query, keep_blank_values=False)
    qs = [(k, v) for k, v in qs if k.lower() not in _TRACKING_PARAMS]
    qs.sort()
    query = urllib.parse.urlencode(qs)
    path = p.path.rstrip("/") or "/"
    return urllib.parse.urlunparse((p.scheme.lower() or "https", netloc, path, "", query, ""))


def url_hash(url: str) -> str:
    return hashlib.sha1(canonicalize_url(url).encode("utf-8")).hexdigest()[:16]


# ──────────────────────────────────────────────────────────────────────────
# Source: Hacker News (Algolia API, public, no auth)
# ──────────────────────────────────────────────────────────────────────────

def fetch_hn(min_points: int, lookback_hours: int, max_items: int) -> list[dict]:
    cutoff = int((datetime.now(timezone.utc) - timedelta(hours=lookback_hours)).timestamp())
    url = (
        "https://hn.algolia.com/api/v1/search_by_date"
        "?tags=story"
        f"&numericFilters=points>={min_points},created_at_i>{cutoff}"
        f"&hitsPerPage={max_items}"
    )
    data = http_json(url)
    out: list[dict] = []
    for hit in data.get("hits", []):
        if not hit.get("url"):
            continue  # Ask HN / Show HN with no link
        out.append({
            "source": "hn",
            "title": hit.get("title") or "",
            "url": hit["url"],
            "external_id": hit.get("objectID"),
            "points": hit.get("points") or 0,
            "comments": hit.get("num_comments") or 0,
            "created_at": hit.get("created_at"),
            "comments_url": f"https://news.ycombinator.com/item?id={hit['objectID']}",
            "tags": [],
        })
    return out


# ──────────────────────────────────────────────────────────────────────────
# Source: Reddit JSON (public, no auth, ~10 req/min unauthenticated)
# ──────────────────────────────────────────────────────────────────────────

def fetch_reddit(subreddits: list[str], window: str, limit: int, min_score: int) -> list[dict]:
    out: list[dict] = []
    for sub in subreddits:
        try:
            url = f"https://www.reddit.com/r/{sub}/top.json?t={window}&limit={limit}"
            data = http_json(url)
        except Exception as e:
            print(f"[reddit] {sub}: {e}", file=sys.stderr)
            continue
        for child in data.get("data", {}).get("children", []):
            d = child.get("data") or {}
            if d.get("is_self") or d.get("stickied"):
                continue
            external_url = d.get("url_overridden_by_dest") or d.get("url")
            if not external_url or "reddit.com" in (external_url or ""):
                continue
            score = d.get("score") or 0
            if score < min_score:
                continue
            out.append({
                "source": "reddit",
                "subreddit": sub,
                "title": d.get("title") or "",
                "url": external_url,
                "external_id": d.get("id"),
                "points": score,
                "comments": d.get("num_comments") or 0,
                "created_at": datetime.fromtimestamp(d.get("created_utc") or 0, timezone.utc).isoformat(),
                "comments_url": f"https://www.reddit.com{d.get('permalink', '')}",
                "tags": [d.get("link_flair_text")] if d.get("link_flair_text") else [],
            })
        time.sleep(2.5)  # respect Reddit's 10-req-per-minute unauth limit
    return out


# ──────────────────────────────────────────────────────────────────────────
# Source: Lobste.rs RSS
# ──────────────────────────────────────────────────────────────────────────

def fetch_lobsters(rss_url: str, max_items: int) -> list[dict]:
    raw = http_get(rss_url).decode("utf-8", errors="replace")
    out: list[dict] = []
    items = re.findall(r"<item>(.*?)</item>", raw, flags=re.DOTALL)
    for block in items[:max_items]:
        def grab(tag: str) -> str:
            m = re.search(rf"<{tag}>(.*?)</{tag}>", block, flags=re.DOTALL)
            return html.unescape((m.group(1) if m else "").strip())
        title = grab("title")
        link = grab("link")
        pub = grab("pubDate")
        comments = grab("comments")
        # categories may repeat
        cats = re.findall(r"<category>(.*?)</category>", block)
        if not link or "lobste.rs" in link:
            continue
        out.append({
            "source": "lobsters",
            "title": title,
            "url": link,
            "external_id": grab("guid"),
            "points": 0,  # lobsters RSS doesn't expose score; treat as a baseline signal
            "comments": 0,
            "created_at": pub,
            "comments_url": comments,
            "tags": cats,
        })
    return out


# ──────────────────────────────────────────────────────────────────────────
# Source: daily.dev (anonymous GraphQL, no auth)
# ──────────────────────────────────────────────────────────────────────────

DAILYDEV_QUERY = """
query AnonFeed($first: Int!, $ranking: Ranking) {
  anonymousFeed(first: $first, ranking: $ranking) {
    edges {
      node {
        id
        title
        permalink
        commentsPermalink
        numUpvotes
        numComments
        createdAt
        source { name }
        tags
      }
    }
  }
}
""".strip()


def resolve_dailydev_permalink(short_url: str, timeout_s: float = 4.0) -> str:
    """Follow the daily.dev redirect (api.daily.dev/r/<id>) to the underlying
    article URL. Returns the original URL on failure so the pipeline never
    breaks because of a single redirect timeout.

    Resolving these matters for cross-source dedup: the same article on HN
    and daily.dev should merge into one candidate, but daily.dev's shortener
    URL never matches HN's direct article URL until it's been resolved.
    """
    if not short_url or "api.daily.dev/r/" not in short_url:
        return short_url
    req = urllib.request.Request(
        short_url,
        headers={"User-Agent": "Mozilla/5.0"},
        method="HEAD",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            final = resp.geturl()
        if final and final != short_url:
            return final
    except Exception:
        pass
    # HEAD sometimes 405s; retry GET and read 0 bytes.
    try:
        req = urllib.request.Request(
            short_url,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return resp.geturl() or short_url
    except Exception:
        return short_url


def fetch_dailydev(ranking: str, max_items: int, min_upvotes: int) -> list[dict]:
    body = {
        "query": DAILYDEV_QUERY,
        "variables": {"first": max_items, "ranking": ranking},
    }
    try:
        data = http_post_json("https://api.daily.dev/graphql", body)
    except Exception as e:
        print(f"[dailydev] {e}", file=sys.stderr)
        return []
    if data.get("errors"):
        print(f"[dailydev] errors: {data['errors']}", file=sys.stderr)
        return []
    nodes: list[dict] = []
    for edge in data.get("data", {}).get("anonymousFeed", {}).get("edges", []):
        n = edge.get("node") or {}
        upvotes = n.get("numUpvotes") or 0
        if upvotes < min_upvotes:
            continue
        nodes.append(n)

    # Resolve permalinks in parallel so cross-source dedup (HN/Reddit/Lobste.rs)
    # works against the canonical article URL, not the daily.dev shortener.
    short_urls = [n.get("permalink") or "" for n in nodes]
    resolved_urls: list[str] = list(short_urls)
    if short_urls:
        with ThreadPoolExecutor(max_workers=8) as pool:
            for i, url in enumerate(
                pool.map(resolve_dailydev_permalink, short_urls)
            ):
                resolved_urls[i] = url

    out: list[dict] = []
    for n, url in zip(nodes, resolved_urls):
        final_url = url or n.get("commentsPermalink") or ""
        out.append({
            "source": "dailydev",
            "title": n.get("title") or "",
            "url": final_url,
            "external_id": n.get("id"),
            "points": n.get("numUpvotes") or 0,
            "comments": n.get("numComments") or 0,
            "created_at": n.get("createdAt"),
            "comments_url": n.get("commentsPermalink"),
            "tags": n.get("tags") or [],
        })
    return out


# ──────────────────────────────────────────────────────────────────────────
# Filtering
# ──────────────────────────────────────────────────────────────────────────

def make_drop_filter(filter_cfg: dict) -> tuple:
    url_pats = [re.compile(p) for p in filter_cfg.get("drop_url_patterns", [])]
    title_pats = [re.compile(p) for p in filter_cfg.get("drop_title_patterns", [])]
    return url_pats, title_pats


def should_drop(item: dict, url_pats: list[re.Pattern], title_pats: list[re.Pattern]) -> str | None:
    url = item.get("url") or ""
    title = item.get("title") or ""
    for p in url_pats:
        if p.search(url):
            return f"url~{p.pattern}"
    for p in title_pats:
        if p.search(title):
            return f"title~{p.pattern}"
    return None


# ──────────────────────────────────────────────────────────────────────────
# Dedup + cross-source merge
# ──────────────────────────────────────────────────────────────────────────

def merge_by_url(items: list[dict]) -> list[dict]:
    """Group by canonical URL; merge cross-source signals into one record."""
    groups: dict[str, list[dict]] = {}
    for it in items:
        h = url_hash(it["url"])
        groups.setdefault(h, []).append(it)
    merged: list[dict] = []
    for h, group in groups.items():
        primary = max(group, key=lambda x: x.get("points") or 0)
        sources = sorted({g["source"] for g in group})
        merged.append({
            "id": h,
            "title": primary.get("title"),
            "url": primary.get("url"),
            "canonical_url": canonicalize_url(primary.get("url") or ""),
            "sources": sources,
            "per_source": [
                {
                    "source": g["source"],
                    "subreddit": g.get("subreddit"),
                    "external_id": g.get("external_id"),
                    "points": g.get("points") or 0,
                    "comments": g.get("comments") or 0,
                    "created_at": g.get("created_at"),
                    "comments_url": g.get("comments_url"),
                    "tags": g.get("tags") or [],
                }
                for g in group
            ],
            "tags": sorted({t for g in group for t in (g.get("tags") or []) if t}),
            "discovered_at": datetime.now(timezone.utc).isoformat(),
        })
    return merged


# ──────────────────────────────────────────────────────────────────────────
# Mechanical scoring
# ──────────────────────────────────────────────────────────────────────────

def score_aggregator_breadth(rec: dict) -> int:
    """v2 demand sub-cap: number of distinct sources, capped at 4.

    Replaces v1's engagement-weighted formula. Per RUBRIC.md the
    aggregator-vote signal is breadth-not-depth — HN/Reddit/Lobsters/daily.dev
    voters are good at *discovery* but weak at *YouTube demand prediction*,
    so vote magnitudes are intentionally ignored. The full v2 demand axis is
    composed downstream in merge.py from this + cold-search + autocomplete +
    Tier B reference-channel hits."""
    return min(4, len(rec.get("sources", [])))


_EVERGREEN_HINT_DEFAULT = re.compile(
    r"\b(internals?|deep[-\s]dive|how .* works?|why .* is|explained|anatomy of|"
    r"tour of|guide to|from scratch|under the hood)\b",
    re.I,
)


def score_evergreen(rec: dict, cfg: dict) -> int:
    title = rec.get("title", "")
    url = rec.get("url", "")
    blob = f"{title} {url}"
    base = 14  # neutral
    ephemeral = re.compile(
        r"\b(" + "|".join(cfg.get("ephemeral_keywords", [])) + r")\b",
        re.I,
    )
    evergreen_kw = cfg.get("evergreen_keywords") or []
    if evergreen_kw:
        evergreen_pat = re.compile(r"(" + "|".join(evergreen_kw) + r")", re.I)
    else:
        evergreen_pat = _EVERGREEN_HINT_DEFAULT
    if ephemeral.search(blob):
        base -= 8
    if evergreen_pat.search(blob):
        base += 4
    # Penalise URL paths that smell of release notes / changelogs
    if re.search(r"/(releases?|changelog|release-notes|whats-new)/", url, re.I):
        base -= 6
    return max(0, min(20, base))


def load_pending_youtube_from_inbox(inbox_path: Path, existing_ids: set[str]) -> list[dict]:
    """Pull pending_judgment YouTube candidates from inbox into the daily
    shortlist so they ride along through cold-search → autocomplete → judgment
    → merge instead of sitting unjudged forever.

    These candidates were created by `apply_decisions.py` from the dashboard's
    "Inspire from this" YouTube flow; they have sources=["youtube"] and the
    3-axis floor composite. Reshaped into fetch.py's record shape so merge.py
    treats them identically to aggregator candidates.
    """
    if not inbox_path.exists():
        return []
    try:
        inbox = json.loads(inbox_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    out: list[dict] = []
    for cid, c in (inbox.get("candidates") or {}).items():
        if cid in existing_ids:
            continue
        if not c.get("pending_judgment"):
            continue
        if list(c.get("sources") or []) != ["youtube"]:
            continue
        scores = c.get("scores") or {}
        breadth = int(scores.get("aggregator_breadth", 1))
        evergreen = int(scores.get("evergreen", 14))
        out.append({
            "id": cid,
            "title": c.get("title") or "",
            "url": c.get("url") or "",
            "canonical_url": c.get("canonical_url"),
            "sources": list(c.get("sources") or []),
            "per_source": list(c.get("per_source") or []),
            "tags": list(c.get("tags") or []),
            "discovered_at": c.get("first_seen_at"),
            "scores": {
                "aggregator_breadth": breadth,
                "evergreen": evergreen,
            },
            "mechanical_subtotal": breadth + evergreen,
        })
    return out


# ──────────────────────────────────────────────────────────────────────────
# Driver
# ──────────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(Path(__file__).parent / "config.json"))
    ap.add_argument("--out-dir", default=None, help="Override archive root (default: data/archive)")
    ap.add_argument("--dry-run", action="store_true", help="Don't write files; print summary.")
    args = ap.parse_args()

    cfg_path = Path(args.config).resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    base_dir = cfg_path.parent
    archive_root = Path(args.out_dir) if args.out_dir else (base_dir / cfg["paths"]["archive_dir"])
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    day_dir = archive_root / today
    day_dir.mkdir(parents=True, exist_ok=True)

    # Fetch — track per-source counts + errors so the scheduled-task summary
    # can surface silent degradations (e.g. Reddit 429-throttling) instead of
    # hiding them behind a low candidate count.
    raw: list[dict] = []
    source_meta: dict[str, dict[str, Any]] = {}
    src_cfg = cfg["sources"]

    def run_source(name: str, enabled: bool, fn) -> None:
        if not enabled:
            source_meta[name] = {"enabled": False, "count": 0, "error": None}
            return
        try:
            items = fn()
            source_meta[name] = {"enabled": True, "count": len(items), "error": None}
            print(f"[{name}]{' ' * max(1, 10 - len(name))}{len(items)}", file=sys.stderr)
            raw.extend(items)
        except Exception as e:
            source_meta[name] = {"enabled": True, "count": 0, "error": str(e)}
            print(f"[{name}] FAILED: {e}", file=sys.stderr)

    run_source("hn", src_cfg["hn"]["enabled"],
               lambda: fetch_hn(src_cfg["hn"]["min_points"],
                                src_cfg["hn"]["lookback_hours"],
                                src_cfg["hn"]["max_items"]))
    run_source("reddit", src_cfg["reddit"]["enabled"],
               lambda: fetch_reddit(src_cfg["reddit"]["subreddits"],
                                    src_cfg["reddit"]["window"],
                                    src_cfg["reddit"]["limit_per_sub"],
                                    src_cfg["reddit"]["min_score"]))
    run_source("lobsters", src_cfg["lobsters"]["enabled"],
               lambda: fetch_lobsters(src_cfg["lobsters"]["rss_url"],
                                      src_cfg["lobsters"]["max_items"]))
    run_source("dailydev", src_cfg["dailydev"]["enabled"],
               lambda: fetch_dailydev(src_cfg["dailydev"]["ranking"],
                                      src_cfg["dailydev"]["max_items"],
                                      src_cfg["dailydev"]["min_upvotes"]))

    # Filter
    url_pats, title_pats = make_drop_filter(cfg["filter"])
    kept: list[dict] = []
    drops: dict[str, int] = {}
    for it in raw:
        reason = should_drop(it, url_pats, title_pats)
        if reason:
            drops[reason] = drops.get(reason, 0) + 1
            continue
        kept.append(it)
    print(f"[filter]   kept {len(kept)} / {len(raw)} (dropped {sum(drops.values())})", file=sys.stderr)

    # Dedup + merge
    merged = merge_by_url(kept)
    print(f"[merge]    {len(merged)} unique candidates after cross-source dedup", file=sys.stderr)

    # Mechanical scoring (v2 — see RUBRIC.md)
    eg_cfg = cfg["mechanical_scoring"]["evergreen"]
    for rec in merged:
        rec["scores"] = {
            "aggregator_breadth": score_aggregator_breadth(rec),  # 0-4 demand sub-cap
            "evergreen": score_evergreen(rec, eg_cfg),            # 0-20
            # Remaining axes are filled downstream:
            #   demand (full)        composed in merge.py from breadth + cold-search + autocomplete + Tier B hits
            #   yt_competition       LLM phase, with cooldown overlay in merge.py
            #   audience_reach       LLM phase, per angle
            #   curiosity_hook       LLM phase, per angle
            #   computing_depth      LLM phase, per angle
        }
        rec["mechanical_subtotal"] = rec["scores"]["aggregator_breadth"] + rec["scores"]["evergreen"]

    # Pending YouTube candidates created via the dashboard's "Inspire from
    # this" flow ride along in the daily shortlist so they pick up
    # cold-search / autocomplete / judgment signals.
    inbox_path = (base_dir / cfg["paths"]["inbox_json"]).resolve()
    existing_ids = {r["id"] for r in merged}
    pending_yt = load_pending_youtube_from_inbox(inbox_path, existing_ids)
    if pending_yt:
        print(f"[inbox]    + {len(pending_yt)} pending YouTube candidates", file=sys.stderr)
        merged.extend(pending_yt)

    # Shortlist
    sl_cfg = cfg["shortlist"]
    merged.sort(key=lambda r: r["mechanical_subtotal"], reverse=True)
    shortlist = [r for r in merged if r["mechanical_subtotal"] >= sl_cfg["min_mechanical_score"]][: sl_cfg["size"]]

    # Output — dated subfolder under data/archive/
    shortlist_path = day_dir / "shortlist.json"
    full_path = day_dir / "raw.json"

    payload_shortlist = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(shortlist),
        "candidates": shortlist,
    }
    payload_full = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(merged),
        "drops": drops,
        "candidates": merged,
    }

    run_meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": source_meta,
        "totals": {
            "raw": len(raw),
            "after_filter": len(kept),
            "dropped": sum(drops.values()),
            "merged": len(merged) - len(pending_yt),
            "pending_youtube": len(pending_yt),
            "shortlist": len(shortlist),
        },
        "drops": drops,
    }

    if args.dry_run:
        print(f"[dry-run]  shortlist would have {len(shortlist)} items, top 5:", file=sys.stderr)
        for r in shortlist[:5]:
            print(f"  {r['mechanical_subtotal']:>3}  {r['title'][:80]}  ({','.join(r['sources'])})", file=sys.stderr)
        return 0

    run_meta_path = day_dir / "run_meta.json"
    shortlist_path.write_text(json.dumps(payload_shortlist, indent=2, ensure_ascii=False), encoding="utf-8")
    full_path.write_text(json.dumps(payload_full, indent=2, ensure_ascii=False), encoding="utf-8")
    run_meta_path.write_text(json.dumps(run_meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[wrote]    {shortlist_path}", file=sys.stderr)
    print(f"[wrote]    {full_path}", file=sys.stderr)
    print(f"[wrote]    {run_meta_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
