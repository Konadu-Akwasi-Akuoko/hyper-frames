"""Text-aggregator fetchers — HN (Algolia), Reddit, Lobsters (RSS), daily.dev
(GraphQL). Ported from tools/topic-pipeline/fetch.py, minus the scoring rubric.
Each `parse_*` is pure (testable on fixtures); each `fetch_*` does the HTTP and
returns normalized raw rows: {source, external_id, title, url, payload}."""

from __future__ import annotations

import html
import json
import re
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any

UA = "studio-discover/0.1 (+https://github.com/hyper-frames; research script)"

DEFAULT_SUBREDDITS = [
    "programming",
    "compsci",
    "webdev",
    "databases",
    "cpp",
    "rust",
    "golang",
]


def _http_json(url: str, timeout: int = 20) -> Any:
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _http_get(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _http_post_json(url: str, body: dict[str, Any], timeout: int = 20) -> Any:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"User-Agent": UA, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


# ---------------- Hacker News (Algolia) ----------------

def parse_hn(data: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for hit in data.get("hits", []):
        if not hit.get("url"):
            continue
        oid = hit.get("objectID")
        out.append(
            {
                "source": "hn",
                "external_id": oid,
                "title": hit.get("title") or "",
                "url": hit["url"],
                "payload": {
                    "points": hit.get("points") or 0,
                    "comments": hit.get("num_comments") or 0,
                    "created_at": hit.get("created_at"),
                    "comments_url": f"https://news.ycombinator.com/item?id={oid}",
                },
            }
        )
    return out


def fetch_hn(
    min_points: int = 25, lookback_hours: int = 48, max_items: int = 80
) -> list[dict[str, Any]]:
    cutoff = int(
        (datetime.now(timezone.utc) - timedelta(hours=lookback_hours)).timestamp()
    )
    url = (
        "https://hn.algolia.com/api/v1/search_by_date"
        "?tags=story"
        f"&numericFilters=points>={min_points},created_at_i>{cutoff}"
        f"&hitsPerPage={max_items}"
    )
    return parse_hn(_http_json(url))


# ---------------- Reddit ----------------

def parse_reddit(data: dict[str, Any], sub: str, min_score: int = 40) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for child in data.get("data", {}).get("children", []):
        d = child.get("data") or {}
        if d.get("is_self") or d.get("stickied"):
            continue
        external_url = d.get("url_overridden_by_dest") or d.get("url")
        if not external_url or "reddit.com" in external_url:
            continue
        score = d.get("score") or 0
        if score < min_score:
            continue
        out.append(
            {
                "source": f"reddit:r/{sub}",
                "external_id": d.get("id"),
                "title": d.get("title") or "",
                "url": external_url,
                "payload": {
                    "subreddit": sub,
                    "points": score,
                    "comments": d.get("num_comments") or 0,
                    "comments_url": f"https://www.reddit.com{d.get('permalink', '')}",
                    "flair": d.get("link_flair_text"),
                },
            }
        )
    return out


def fetch_reddit(
    subreddits: list[str] | None = None,
    window: str = "day",
    limit: int = 15,
    min_score: int = 40,
    sleep: float = 2.5,
) -> list[dict[str, Any]]:
    subs = subreddits or DEFAULT_SUBREDDITS
    out: list[dict[str, Any]] = []
    for i, sub in enumerate(subs):
        try:
            data = _http_json(
                f"https://www.reddit.com/r/{sub}/top.json?t={window}&limit={limit}"
            )
            out.extend(parse_reddit(data, sub, min_score))
        except Exception as e:  # one dead sub never fails the source
            print(f"[reddit] {sub}: {e}")
        if i < len(subs) - 1:
            time.sleep(sleep)  # respect the unauth rate limit
    return out


# ---------------- Lobsters (RSS) ----------------

def parse_lobsters(xml_text: str, max_items: int = 25) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    items = re.findall(r"<item>(.*?)</item>", xml_text, flags=re.DOTALL)
    for block in items[:max_items]:

        def grab(tag: str) -> str:
            m = re.search(rf"<{tag}>(.*?)</{tag}>", block, flags=re.DOTALL)
            return html.unescape((m.group(1) if m else "").strip())

        link = grab("link")
        if not link or "lobste.rs" in link:
            continue
        cats = re.findall(r"<category>(.*?)</category>", block)
        out.append(
            {
                "source": "lobsters",
                "external_id": grab("guid") or link,
                "title": grab("title"),
                "url": link,
                "payload": {
                    "created_at": grab("pubDate"),
                    "comments_url": grab("comments"),
                    "tags": cats,
                },
            }
        )
    return out


def fetch_lobsters(
    rss_url: str = "https://lobste.rs/rss", max_items: int = 25
) -> list[dict[str, Any]]:
    xml_text = _http_get(rss_url).decode("utf-8", errors="replace")
    return parse_lobsters(xml_text, max_items)


# ---------------- daily.dev (GraphQL) ----------------

DAILYDEV_QUERY = """
query AnonFeed($first: Int!, $ranking: Ranking) {
  anonymousFeed(first: $first, ranking: $ranking) {
    edges { node {
      id title permalink commentsPermalink numUpvotes numComments createdAt
      source { name } tags
    } }
  }
}
""".strip()


def parse_dailydev(data: dict[str, Any], min_upvotes: int = 10) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    edges = data.get("data", {}).get("anonymousFeed", {}).get("edges", [])
    for edge in edges:
        n = edge.get("node") or {}
        upvotes = n.get("numUpvotes") or 0
        if upvotes < min_upvotes:
            continue
        out.append(
            {
                "source": "dailydev",
                "external_id": n.get("id"),
                "title": n.get("title") or "",
                "url": n.get("permalink") or n.get("commentsPermalink") or "",
                "payload": {
                    "points": upvotes,
                    "comments": n.get("numComments") or 0,
                    "created_at": n.get("createdAt"),
                    "comments_url": n.get("commentsPermalink"),
                    "feed_source": (n.get("source") or {}).get("name"),
                    "tags": n.get("tags") or [],
                },
            }
        )
    return out


def fetch_dailydev(
    ranking: str = "POPULARITY", max_items: int = 40, min_upvotes: int = 10
) -> list[dict[str, Any]]:
    body = {
        "query": DAILYDEV_QUERY,
        "variables": {"first": max_items, "ranking": ranking},
    }
    data = _http_post_json("https://api.daily.dev/graphql", body)
    if data.get("errors"):
        raise RuntimeError(f"daily.dev errors: {data['errors']}")
    return parse_dailydev(data, min_upvotes)
