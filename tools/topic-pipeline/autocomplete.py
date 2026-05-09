#!/usr/bin/env python3
"""
YouTube autocomplete demand sub-signal (RUBRIC.md demand axis, 0-3 cap).

Per candidate, hit the public Google suggest endpoint and score 0/1/3 based
on how prominently the topic phrase autocompletes for YouTube searchers.

Endpoint:
    https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q=<query>
Returns: [<query>, [<suggestion>...], [], {...}]

Score (matches RUBRIC.md):
    3 = ≥1 suggestion that closely matches the query (Jaccard ≥ 0.5)
    1 = ≥1 suggestion overlaps loosely (Jaccard ≥ 0.25)
    0 = no suggestions, or none with overlap

Output: data/archive/YYYY-MM-DD/autocomplete.json — keyed by candidate id.
Caches: candidate ids already in the file are skipped unless --refresh.

Usage:
    python3 autocomplete.py --candidates data/archive/2026-05-08/shortlist.json
    python3 autocomplete.py --query "how does captcha work"
    python3 autocomplete.py --candidates ... --refresh
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config.json"

ENDPOINT = "https://suggestqueries.google.com/complete/search"

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
    """Same transformation as cold_search.title_to_query — duplicated to keep
    the modules independent. Strips source-specific noise from a candidate
    title so it can be passed as a search query."""
    q = title or ""
    q = _PREFIX_RE.sub("", q)
    q = _YEAR_PAREN_RE.sub("", q)
    q = _SITE_SUFFIX_RE.sub("", q)
    q = _WHITESPACE_RE.sub(" ", q).strip()
    if len(q) > 100:
        q = q[:100].rsplit(" ", 1)[0]
    return q


def load_candidates(path: Path) -> list[tuple[str, str]]:
    data = json.loads(path.read_text())
    if isinstance(data, dict) and "candidates" in data:
        return [(c["id"], c["title"]) for c in data["candidates"]]
    if isinstance(data, list):
        return [(c["id"], c["title"]) for c in data]
    raise ValueError(f"unrecognized shape in {path}")


def query_stem(query: str, max_words: int = 4) -> str:
    """Return the first N words of the query as a prefix stem. YouTube
    autocomplete is prefix-based, so a short stem often surfaces the
    extensions that actually match the topic."""
    parts = query.split()
    return " ".join(parts[:max_words])

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "of", "to", "in", "on", "at", "by", "for", "with", "about", "as",
    "and", "or", "but", "if", "then", "than", "this", "that", "these",
    "those", "it", "its", "just", "do", "does", "doing", "did", "done",
    "i", "you", "he", "she", "we", "they", "me", "us", "them",
    "my", "your", "our", "their",
    "how", "why", "what", "when", "where", "which", "who",
}

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall((text or "").lower()) if t not in STOPWORDS}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def fetch_suggestions(query: str, timeout_s: float = 5.0) -> tuple[list[str], str | None]:
    """Returns (suggestions, error_or_none)."""
    if not query.strip():
        return [], "empty query"
    params = urllib.parse.urlencode({"client": "firefox", "ds": "yt", "q": query})
    url = f"{ENDPOINT}?{params}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 topic-pipeline/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return [], f"http error: {exc!r}"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        return [], f"json decode: {exc}"
    if not isinstance(parsed, list) or len(parsed) < 2:
        return [], "unexpected payload shape"
    suggs = parsed[1] if isinstance(parsed[1], list) else []
    return [s for s in suggs if isinstance(s, str)], None


def score_autocomplete(query: str, suggestions: list[str]) -> tuple[int, float, str | None]:
    """Returns (score 0/1/3, best_jaccard, best_match_string)."""
    if not suggestions:
        return 0, 0.0, None
    q_tokens = tokenize(query)
    best_jacc = 0.0
    best_match: str | None = None
    for s in suggestions:
        j = jaccard(q_tokens, tokenize(s))
        if j > best_jacc:
            best_jacc = j
            best_match = s
    if best_jacc >= 0.5:
        return 3, best_jacc, best_match
    if best_jacc >= 0.25:
        return 1, best_jacc, best_match
    return 0, best_jacc, best_match


def analyze_one(cid: str, title: str) -> dict[str, Any]:
    """Score the candidate against autocomplete using two probes:
    (1) the full cleaned query, and (2) a 4-word prefix stem. Take the
    higher score — YT autocomplete is prefix-driven, so a stem often
    catches topics whose full title carries non-search qualifiers
    (e.g. "actually", "from scratch")."""
    query = title_to_query(title)
    suggs_full, err_full = fetch_suggestions(query)
    score_full, jacc_full, match_full = score_autocomplete(query, suggs_full)

    stem = query_stem(query)
    if stem and stem != query:
        suggs_stem, err_stem = fetch_suggestions(stem)
        score_stem, jacc_stem, match_stem = score_autocomplete(query, suggs_stem)
    else:
        suggs_stem, err_stem = [], None
        score_stem, jacc_stem, match_stem = 0, 0.0, None

    if score_stem > score_full:
        winning = "stem"
        score, best_j, best_match = score_stem, jacc_stem, match_stem
    else:
        winning = "full"
        score, best_j, best_match = score_full, jacc_full, match_full

    return {
        "id": cid,
        "title": title,
        "query": query,
        "stem": stem,
        "suggestions_full": suggs_full,
        "suggestions_stem": suggs_stem,
        "winning_probe": winning,
        "autocomplete_score": score,
        "best_jaccard": round(best_j, 3),
        "best_match": best_match,
        "error": err_full or err_stem,
    }


def archive_path_for(cfg: dict[str, Any], date_str: str) -> Path:
    archive_dir = HERE / cfg.get("paths", {}).get("archive_dir", "data/archive")
    return archive_dir / date_str / "autocomplete.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, help="shortlist.json path")
    parser.add_argument("--query", help="run a single ad-hoc query and exit")
    parser.add_argument("--concurrency", type=int, default=8,
                        help="parallel HTTP requests (default 8)")
    parser.add_argument("--refresh", action="store_true",
                        help="re-fetch candidates already cached")
    parser.add_argument("--date",
                        help="archive date YYYY-MM-DD (default today UTC)")
    parser.add_argument("--throttle-ms", type=int, default=50,
                        help="delay between requests per worker (default 50ms)")
    args = parser.parse_args()

    cfg = json.loads(CONFIG_PATH.read_text())
    today = datetime.now(timezone.utc)

    if args.query:
        suggs, err = fetch_suggestions(args.query)
        score, j, match = score_autocomplete(args.query, suggs)
        print(json.dumps(
            {
                "query": args.query,
                "suggestions": suggs,
                "autocomplete_score": score,
                "best_jaccard": round(j, 3),
                "best_match": match,
                "error": err,
            },
            indent=2, ensure_ascii=False,
        ))
        return 0 if not err else 1

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
        f"Autocomplete-checking {len(todo)} candidates "
        f"(skipped {skipped} cached, {args.concurrency}-way parallel)...",
        file=sys.stderr,
    )

    started = time.monotonic()
    results: dict[str, Any] = dict(existing)
    failed = 0

    def task(cid: str, title: str) -> dict[str, Any]:
        if args.throttle_ms:
            time.sleep(args.throttle_ms / 1000.0)
        return analyze_one(cid, title)

    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {pool.submit(task, cid, title): (cid, title) for cid, title in todo}
        done = 0
        for fut in as_completed(futures):
            cid, title = futures[fut]
            try:
                rec = fut.result()
            except Exception as exc:
                rec = {"id": cid, "title": title, "error": f"unexpected: {exc!r}",
                       "autocomplete_score": 0}
            done += 1
            if rec.get("error"):
                failed += 1
            results[cid] = rec
            elapsed = time.monotonic() - started
            score = rec.get("autocomplete_score", 0)
            j = rec.get("best_jaccard", 0)
            nf = len(rec.get("suggestions_full", []))
            ns = len(rec.get("suggestions_stem", []))
            probe = rec.get("winning_probe", "-")
            err = rec.get("error", "")
            print(
                f"  [{elapsed:5.1f}s] {done:3d}/{len(todo)}  "
                f"ac={score}  j={j:.2f}  full={nf:2d} stem={ns:2d} via={probe}  "
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
