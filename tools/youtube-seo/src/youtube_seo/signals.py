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
import statistics

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


DEMAND_MIN_LETTER_HITS = 3
DEMAND_MAX_PHRASES = 10


def compute_demand_phrases(
    expanded: dict[str, list[str]],
) -> list[dict[str, Any]]:
    """Phrases that appear in 3+ adjacent letter expansions.

    Distinguishes recurring real demand from one-off completions.
    Returned sorted by letter_hits desc, capped at DEMAND_MAX_PHRASES.
    """
    phrase_to_letters: dict[str, set[str]] = defaultdict(set)
    for letter, suggestions in expanded.items():
        for s in suggestions:
            phrase_to_letters[s].add(letter)

    phrases = [
        {"phrase": phrase, "letter_hits": len(letters)}
        for phrase, letters in phrase_to_letters.items()
        if len(letters) >= DEMAND_MIN_LETTER_HITS
    ]
    phrases.sort(key=lambda p: p["letter_hits"], reverse=True)
    return phrases[:DEMAND_MAX_PHRASES]


HOOK_MIN_VIDEOS_WITH_HEATMAP = 5


def _intensity_at(heatmap: list[dict[str, Any]] | None, t: float) -> float | None:
    """Return the heatmap value at timestamp t, or None if heatmap missing or t out of range."""
    if not heatmap:
        return None
    for entry in heatmap:
        start = entry.get("start_time")
        end = entry.get("end_time")
        value = entry.get("value")
        if start is None or end is None or value is None:
            continue
        if start <= t < end:
            return float(value)
    return None


def _peak_position(heatmap: list[dict[str, Any]] | None) -> float | None:
    """Return the start_time of the heatmap entry with the highest value."""
    if not heatmap:
        return None
    best = max(
        (e for e in heatmap if e.get("value") is not None),
        key=lambda e: e["value"],
        default=None,
    )
    return float(best["start_time"]) if best else None


def compute_hook_patterns(
    videos: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Median peak position + intensities at 5/15/30s across videos with heatmaps."""
    with_heatmap = [v for v in videos if v.get("heatmap")]
    if len(with_heatmap) < HOOK_MIN_VIDEOS_WITH_HEATMAP:
        return None

    peaks = [
        p
        for v in with_heatmap
        if (p := _peak_position(v.get("heatmap"))) is not None
    ]
    intensities_5 = [
        i for v in with_heatmap
        if (i := _intensity_at(v.get("heatmap"), 5.0)) is not None
    ]
    intensities_15 = [
        i for v in with_heatmap
        if (i := _intensity_at(v.get("heatmap"), 15.0)) is not None
    ]
    intensities_30 = [
        i for v in with_heatmap
        if (i := _intensity_at(v.get("heatmap"), 30.0)) is not None
    ]

    median_peak = statistics.median(peaks) if peaks else None
    median_5 = statistics.median(intensities_5) if intensities_5 else None
    median_15 = statistics.median(intensities_15) if intensities_15 else None
    median_30 = statistics.median(intensities_30) if intensities_30 else None

    note = (
        f"Top performers' peak hook lives near {median_peak:.0f}s; "
        f"viewer hold at 5/15/30s: "
        f"{(median_5 or 0)*100:.0f}%/{(median_15 or 0)*100:.0f}%/{(median_30 or 0)*100:.0f}%."
        if median_peak is not None
        else "Heatmap available but peak undetermined."
    )

    return {
        "median_peak_position_seconds": median_peak,
        "median_intensity_at_5s": median_5,
        "median_intensity_at_15s": median_15,
        "median_intensity_at_30s": median_30,
        "videos_with_heatmap": len(with_heatmap),
        "note": note,
    }
