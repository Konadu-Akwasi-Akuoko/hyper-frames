"""Computed signals from raw SEO research data.

All functions are pure: input is the raw videos list (from search.fetch_top_videos)
or autocomplete result (from autocomplete.fetch_seed_and_expanded), output is
a small JSON-serializable dict. No I/O.
"""

from __future__ import annotations

from collections import Counter
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
