#!/usr/bin/env python3
"""
Inspiration module — Tier B titles as a mood board, plus rough starter
angles, written before the LLM judgment phase.

For each candidate in shortlist.json, this script emits:

1. **mood_board** (3-5 entries) — the closest Tier B titles by Jaccard
   similarity. Pure retrieval; no generation. Used by the judgment phase
   prompt as a title-shape reference, not a content reference.

2. **starter_angles** (0-3 entries) — rough draft titles produced by
   instantiating the curiosity-hook patterns from RUBRIC.md against the
   candidate's topic seed. Each carries a `[<pattern>]` prefix so the
   judgment phase doesn't anchor to the rough wording. Skipped for
   candidates classified as news / opinion (no reframes invented).

Output: data/archive/YYYY-MM-DD/inspiration.json — keyed by candidate id.

Usage:
    python3 inspiration.py --candidates data/archive/2026-05-08/shortlist.json
    python3 inspiration.py --candidates ... --top-k 3 --max-starters 2
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config.json"

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "of", "to", "in", "on", "at", "by", "for", "with", "about", "as",
    "and", "or", "but", "if", "then", "than", "this", "that", "these",
    "those", "it", "its", "just", "do", "does", "doing", "did", "done",
    "i", "you", "he", "she", "we", "they", "me", "us", "them",
    "my", "your", "our", "their",
    "how", "why", "what", "when", "where", "which", "who",
    "from", "into", "out", "up", "down", "over", "under",
    "not", "no", "yes", "use", "using", "make", "made", "go", "going",
    "now", "still", "also", "more", "most", "very", "much",
}

_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9\-+]*")
_PREFIX_RE = re.compile(
    r"^(show|ask|tell)\s+(hn|lobsters?)\s*[:\-—]\s*", re.IGNORECASE,
)
_YEAR_PAREN_RE = re.compile(r"\s*\((19|20)\d{2}\)\s*$")
_WHITESPACE_RE = re.compile(r"\s+")


def tokenize(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall((text or "").lower()) if t not in STOPWORDS and len(t) > 1}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def clean_title(title: str) -> str:
    t = title or ""
    t = _PREFIX_RE.sub("", t)
    t = _YEAR_PAREN_RE.sub("", t)
    t = _WHITESPACE_RE.sub(" ", t).strip()
    return t


def extract_topic_seed(title: str) -> str:
    """Return a short topic-anchor phrase from the cleaned title.

    Heuristic: drop stop words and very short tokens; take the first 1-3
    surviving content tokens, restoring the original case from the title.
    Crude on purpose — the LLM in the judgment phase rewrites the title
    anyway; the seed only needs to be evocative."""
    cleaned = clean_title(title)
    tokens = cleaned.split()
    keep: list[str] = []
    for tok in tokens:
        low = re.sub(r"[^a-z0-9\-]+", "", tok.lower())
        if not low or low in STOPWORDS or low in TOPIC_SEED_VERB_STOPLIST or len(low) < 2:
            continue
        keep.append(tok.strip(",.;:!?\"'()"))
        if len(keep) >= 3:
            break
    if not keep:
        return cleaned[:40]
    return " ".join(keep)


# ---- shape classification --------------------------------------------------

NEWS_HOSTS = (
    "reuters.com", "apnews.com", "theverge.com", "tomshardware.com",
    "bloomberg.com", "ft.com", "wsj.com", "nytimes.com", "cnbc.com",
    "elciudadano.com", "techcrunch.com",
    # Lifestyle / non-tech publishers that occasionally hit the aggregators
    "tastecooking.com", "bonappetit.com", "vogue.com", "newyorker.com",
    "theatlantic.com", "vulture.com",
)

# Verbs and weak modifiers that bleed into the topic seed when their
# inflected form survives stopword filtering. Only applied during seed
# extraction, not during similarity scoring.
TOPIC_SEED_VERB_STOPLIST = {
    "killing", "running", "building", "serving", "writing", "reading",
    "making", "using", "trying", "working", "coming", "going", "doing",
    "shaping", "looking", "talking", "saying", "starting", "ending",
    "winning", "losing", "playing", "moving", "growing", "showing",
    "shipped", "shipping", "released", "releasing", "announcing",
    "live", "like", "love", "hate", "feel", "think", "know",
    "get", "got", "let", "lets", "need", "want", "wants",
    "become", "becomes", "can", "could", "would", "should",
    "fucking",  # for the "Just Fucking Use Go" archetype
}
OPINION_PATTERNS = (
    r"\bjust\s+(use|fucking\s+use)\b", r"\bis\s+dead\b", r"\bis\s+broken\b",
    r"\byou\s+(should|shouldn'?t|don'?t)\b", r"\bagainst\b", r"\bin\s+defense\s+of\b",
    r"\bopinion\b", r"\bmaybe\s+you\s+shouldn",
)
EXPLOIT_PATTERNS = (
    r"\bcve-\d", r"\bexploit\b", r"\bvulnerab", r"\brce\b", r"\blpe\b",
    r"\bprivilege\s+escalation\b", r"\buse-after-free\b", r"\b0day\b",
    r"\bbreach\b", r"\bleak\b", r"\bmalware\b", r"\bbackdoor\b",
)
PROJECT_PATTERNS = (
    r"\bbuilding\b", r"\bi\s+built\b", r"\bmy\s+own\b", r"\bfrom\s+scratch\b",
    r"\bin\s+raw\b", r"\bin\s+\d+\s+(lines|days|hours)\b", r"\bself-hosting\b",
    r"\brunning\b", r"\bserving\b",
)
PRIMER_PATTERNS = (
    r"^(how|why|what)\s", r"\bexplained\b", r"\bdemystif", r"\bprimer\b",
    r"\bintroduction\s+to\b", r"\bunderstanding\b",
)


def classify_shape(title: str, url: str) -> str:
    """Return one of: news, opinion, exploit, project, primer, tool."""
    t = (title or "").lower()
    u = (url or "").lower()
    if any(host in u for host in NEWS_HOSTS):
        return "news"
    for pat in OPINION_PATTERNS:
        if re.search(pat, t):
            return "opinion"
    for pat in EXPLOIT_PATTERNS:
        if re.search(pat, t):
            return "exploit"
    for pat in PROJECT_PATTERNS:
        if re.search(pat, t):
            return "project"
    for pat in PRIMER_PATTERNS:
        if re.search(pat, t):
            return "primer"
    return "tool"


# Patterns recommended per candidate shape. News + opinion get no starters.
SHAPE_PATTERNS: dict[str, list[str]] = {
    "news": [],
    "opinion": ["counterintuitive-twist", "hidden-mechanism"],
    "exploit": ["hidden-mechanism", "mystery", "counterintuitive-twist"],
    "project": ["personal-stake", "hidden-mechanism", "counterintuitive-twist"],
    "primer": ["hidden-mechanism", "personal-stake", "counterintuitive-twist"],
    "tool": ["hidden-mechanism", "counterintuitive-twist", "personal-stake"],
}


PATTERN_TEMPLATES: dict[str, list[str]] = {
    "hidden-mechanism": [
        "Why {topic} actually works the way it does",
        "What's hiding inside {topic}",
        "The thing inside every {topic} you've never seen",
    ],
    "counterintuitive-twist": [
        "Why {topic} is weirder than you think",
        "Why {topic} is harder than it looks",
        "{topic} is not what you think it is",
    ],
    "personal-stake": [
        "How easy is it to build your own {topic}?",
        "Why can't I just {topic}?",
        "Could you actually understand {topic} in 10 minutes?",
    ],
    "hyper-claim": [
        "The most unusual {topic} ever built",
        "Maybe the smallest {topic} that still works",
    ],
    "mystery": [
        "The {topic} bug that nobody can fully explain",
        "Why {topic} keeps surprising the engineers who built it",
    ],
}


def make_starter_angles(
    topic: str,
    patterns: list[str],
    inspirations: list[dict[str, Any]],
    max_starters: int,
) -> list[dict[str, Any]]:
    if not patterns or max_starters <= 0:
        return []
    starters: list[dict[str, Any]] = []
    for i, pattern in enumerate(patterns[:max_starters]):
        templates = PATTERN_TEMPLATES.get(pattern) or []
        if not templates:
            continue
        title = templates[0].format(topic=topic)
        inspired_by = [insp["title"] for insp in inspirations[: max(1, i + 1)]]
        starters.append(
            {
                "title": f"[{pattern}] {title}",
                "lens": f"{pattern.replace('-', ' ')} on {topic}",
                "source_pattern": pattern,
                "topic_seed": topic,
                "inspired_by": inspired_by,
            }
        )
    return starters


def load_candidates(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text())
    if isinstance(data, dict) and "candidates" in data:
        return data["candidates"]
    if isinstance(data, list):
        return data
    raise ValueError(f"unrecognized shape in {path}")


def load_tier_b_videos(feed_path: Path) -> list[dict[str, Any]]:
    feed = json.loads(feed_path.read_text())
    videos = feed.get("videos", feed) if isinstance(feed, dict) else feed
    return [v for v in videos if v.get("channel_tier") == "B"]


def archive_path_for(cfg: dict[str, Any], date_str: str) -> Path:
    archive_dir = HERE / cfg.get("paths", {}).get("archive_dir", "data/archive")
    return archive_dir / date_str / "inspiration.json"


def feed_path_from_cfg(cfg: dict[str, Any]) -> Path:
    p = cfg.get("paths", {}).get("competitors_feed", "data/competitors/feed.json")
    return HERE / p


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, required=True,
                        help="path to shortlist.json")
    parser.add_argument("--feed", type=Path,
                        help="path to competitors feed.json (defaults to config)")
    parser.add_argument("--date", help="archive date YYYY-MM-DD (default today UTC)")
    parser.add_argument("--top-k", type=int, default=5,
                        help="mood-board size (default 5)")
    parser.add_argument("--max-starters", type=int, default=3,
                        help="max starter angles per candidate (default 3)")
    parser.add_argument("--min-similarity", type=float, default=0.06,
                        help="floor for mood-board entries (default 0.06)")
    args = parser.parse_args()

    cfg = json.loads(CONFIG_PATH.read_text())
    today = datetime.now(timezone.utc)

    feed_path = args.feed or feed_path_from_cfg(cfg)
    if not feed_path.exists():
        print(f"FAIL: feed not found at {feed_path}. Run competitors.py first.",
              file=sys.stderr)
        return 1

    candidates = load_candidates(args.candidates)
    tier_b = load_tier_b_videos(feed_path)
    print(
        f"Inspiring {len(candidates)} candidates from {len(tier_b)} Tier B titles...",
        file=sys.stderr,
    )

    tier_b_tokens: list[tuple[set[str], dict[str, Any]]] = [
        (tokenize(v["title"]), v) for v in tier_b
    ]

    results: dict[str, Any] = {}
    shape_counts: dict[str, int] = {}
    for c in candidates:
        cid = c["id"]
        title = c.get("title", "")
        url = c.get("url", "")
        cand_tokens = tokenize(title)

        scored: list[tuple[float, dict[str, Any]]] = []
        for tb_tokens, video in tier_b_tokens:
            sim = jaccard(cand_tokens, tb_tokens)
            if sim >= args.min_similarity:
                scored.append((sim, video))
        scored.sort(key=lambda x: x[0], reverse=True)

        mood_board: list[dict[str, Any]] = []
        for sim, video in scored[: args.top_k]:
            mood_board.append(
                {
                    "title": video["title"],
                    "channel": video.get("channel"),
                    "channel_handle": video.get("channel_handle"),
                    "view_count": video.get("view_count"),
                    "upload_date": video.get("upload_date"),
                    "similarity": round(sim, 3),
                }
            )

        shape = classify_shape(title, url)
        shape_counts[shape] = shape_counts.get(shape, 0) + 1
        topic_seed = extract_topic_seed(title)
        patterns = SHAPE_PATTERNS.get(shape, [])
        starters = make_starter_angles(topic_seed, patterns, mood_board, args.max_starters)

        results[cid] = {
            "id": cid,
            "title": title,
            "candidate_shape": shape,
            "topic_seed": topic_seed,
            "mood_board": mood_board,
            "starter_angles": starters,
        }

    out_path = archive_path_for(cfg, args.date or today.strftime("%Y-%m-%d"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": today.isoformat(timespec="seconds"),
        "candidate_count": len(candidates),
        "tier_b_pool": len(tier_b),
        "shape_counts": shape_counts,
        "results": results,
    }
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))

    no_mood = sum(1 for r in results.values() if not r["mood_board"])
    no_starter = sum(1 for r in results.values() if not r["starter_angles"])
    print(
        f"Done. {len(results)} candidates inspired. "
        f"shape distribution: {shape_counts}. "
        f"empty mood_board: {no_mood}, no starters: {no_starter}. "
        f"→ {out_path}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
