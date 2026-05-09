"""Computed signals from raw SEO research data.

All functions are pure: input is the raw videos list (from search.fetch_top_videos)
or autocomplete result (from autocomplete.fetch_seed_and_expanded), output is
a small JSON-serializable dict. No I/O.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any
import re

# Lowercase stopwords stripped before noun-frequency counting.
STOPWORDS: frozenset[str] = frozenset({
    "a", "actually", "an", "and", "any", "are", "as", "at", "be", "been",
    "but", "by", "can", "did", "do", "does", "for", "from", "has", "have",
    "how", "i", "if", "in", "is", "it", "its", "just", "me", "my", "no",
    "not", "now", "of", "on", "or", "our", "really", "so", "than", "that",
    "the", "then", "this", "to", "up", "us", "vs", "was", "we", "were",
    "what", "when", "why", "will", "with", "you", "your",
})

# Tokens kept for noun frequency: lowercase letters/digits, len >= 2.
TOKEN_RE = re.compile(r"[a-z0-9]+")

DEFAULT_TOP_NOUNS_N = 10


def _tokenize(text: str) -> list[str]:
    """Lowercase, split into alpha-numeric tokens, drop stopwords + 1-char tokens."""
    return [
        tok
        for tok in TOKEN_RE.findall(text.lower())
        if len(tok) >= 2 and tok not in STOPWORDS
    ]


def compute_top_nouns(
    videos: list[dict[str, Any]], top_n: int = DEFAULT_TOP_NOUNS_N
) -> list[dict[str, Any]]:
    """Return [{noun, count}, ...] sorted by count desc, limited to top_n."""
    counter: Counter[str] = Counter()
    for v in videos:
        title = v.get("title") or ""
        counter.update(_tokenize(title))
    return [{"noun": noun, "count": count} for noun, count in counter.most_common(top_n)]


SATURATION_VIEW_THRESHOLD = 100_000
SATURATION_AGE_MONTHS = 18
SATURATION_NGRAM_MIN = 3
SATURATION_NGRAM_MAX = 6
SATURATION_MIN_MATCHES = 3
SATURATION_MAX_WARNINGS = 5


def _ngrams(tokens: list[str], n_min: int, n_max: int) -> list[tuple[str, ...]]:
    """Sliding-window n-grams of length n_min..n_max."""
    out: list[tuple[str, ...]] = []
    for n in range(n_min, n_max + 1):
        for i in range(len(tokens) - n + 1):
            out.append(tuple(tokens[i : i + n]))
    return out


def _is_recent(upload_date: str | None, now: datetime, max_age_months: int) -> bool:
    """yt-dlp upload_date format: 'YYYYMMDD' string."""
    if not upload_date or len(upload_date) != 8:
        return False
    try:
        dt = datetime.strptime(upload_date, "%Y%m%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return False
    return (now - dt) <= timedelta(days=max_age_months * 30)


def compute_saturation_warnings(
    videos: list[dict[str, Any]],
    *,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    """N-grams (3..6 words) appearing in 3+ recent high-view videos.

    Returns up to SATURATION_MAX_WARNINGS entries, sorted by match count desc.
    """
    now = now or datetime.now(timezone.utc)
    eligible: list[dict[str, Any]] = [
        v
        for v in videos
        if (v.get("view_count") or 0) > SATURATION_VIEW_THRESHOLD
        and _is_recent(v.get("upload_date"), now, SATURATION_AGE_MONTHS)
    ]

    ngram_to_videos: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for v in eligible:
        title = v.get("title") or ""
        tokens = _tokenize(title)
        for ng in _ngrams(tokens, SATURATION_NGRAM_MIN, SATURATION_NGRAM_MAX):
            ngram_to_videos[ng].append(v)

    warnings = [
        {
            "pattern": " ".join(ng),
            "match_count": len(matches),
            "sample_title": matches[0].get("title"),
        }
        for ng, matches in ngram_to_videos.items()
        if len(matches) >= SATURATION_MIN_MATCHES
    ]
    warnings.sort(key=lambda w: w["match_count"], reverse=True)
    return warnings[:SATURATION_MAX_WARNINGS]
