# YouTube SEO Research Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a free, anonymous YouTube SEO research pipeline that mines competitor titles, search demand, saturation patterns, and heatmap-derived hook shape into `<video-dir>/seo/research.json`, and wire two skills (`script-writer` and `thumbnail-creator`) to consume it via a documented hook pattern.

**Architecture:** Two layers. (1) A deterministic Python CLI at `tools/youtube-seo/` that fetches data via yt-dlp + YouTube autocomplete and writes the JSON. Mirrors the existing `tools/narration-map/` shape. (2) An LLM-driven skill at `.claude/skills/youtube-seo-research/` that wraps the CLI for natural-language invocation. Two consumer skills (`script-writer` and `thumbnail-creator`) probe for the JSON at their decision points and invoke the skill on-demand if missing.

**Tech Stack:** Python 3.12+, `uv` package manager, `requests` (HTTP), `argparse` (matches narration-map convention — note: spec §2.1 mentioned `click`, but project pattern is argparse so we use it for consistency), `subprocess` to shell out to `yt-dlp` (already installed at `/opt/homebrew/bin/yt-dlp`). No test framework — smoke runs verify correctness, with focused inline doctests/script-style checks for signal computation. Skill files are markdown; no automated testing.

**Spec:** `docs/superpowers/specs/2026-05-09-youtube-seo-research-design.md` — read end-to-end before starting.

**Reference patterns:**
- `tools/narration-map/` — for tool layout, CLI style, README shape, `pyproject.toml` configuration.
- `.claude/skills/script-writer/SKILL.md` — for skill frontmatter, step structure, reference-file conventions.
- `.claude/skills/voiceover-elevenlabs/` — for skill-invokes-skill handoff pattern (commit `219eaae`).

---

## File Structure

**New files (Python tool):**
- `tools/youtube-seo/pyproject.toml` — uv project metadata, deps (`requests`), `[tool.pyright]` for Zed.
- `tools/youtube-seo/README.md` — usage, output schema, examples, troubleshooting.
- `tools/youtube-seo/src/youtube_seo/__init__.py` — public exports.
- `tools/youtube-seo/src/youtube_seo/cli.py` — argparse entrypoint, orchestrates the pipeline.
- `tools/youtube-seo/src/youtube_seo/autocomplete.py` — suggestqueries fetcher + a-z expansion.
- `tools/youtube-seo/src/youtube_seo/search.py` — yt-dlp subprocess wrapper for `ytsearchN:`.
- `tools/youtube-seo/src/youtube_seo/signals.py` — top_nouns, saturation_warnings, demand_phrases, hook_patterns.
- `tools/youtube-seo/src/youtube_seo/output.py` — JSON schema assembly + atomic write.

**New files (skill):**
- `.claude/skills/youtube-seo-research/SKILL.md` — entry point, workflow, triggers.
- `.claude/skills/youtube-seo-research/reference/signal-interpretation.md` — how to read the digest, when to ignore signals.
- `.claude/skills/youtube-seo-research/reference/consumer-integration.md` — hook pattern + consumer field map.

**Modified files (consumer integration):**
- `.claude/skills/script-writer/SKILL.md` — insert Step 2.5 (SEO research checkpoint), update Step 3 to read SEO data when present.
- `.claude/skills/thumbnail-creator/SKILL.md` — Step 2 probes for SEO research, Step 4 prints compressed digest.
- `.claude/skills/thumbnail-creator/reference/youtube-title-pairing.md` — add "Using SEO research" section.
- `CLAUDE.md` — add the per-video SEO research subsection under "Authoring workflow".

---

## Task 1: Scaffold the Python tool

**Files:**
- Create: `tools/youtube-seo/pyproject.toml`
- Create: `tools/youtube-seo/README.md`
- Create: `tools/youtube-seo/src/youtube_seo/__init__.py`
- Create: `tools/youtube-seo/src/youtube_seo/cli.py` (placeholder)

- [ ] **Step 1: Create `tools/youtube-seo/pyproject.toml`**

```toml
[project]
name = "youtube-seo"
version = "0.1.0"
description = "Mine YouTube autocomplete + top-N video metadata into a structured SEO research artifact for one topic."
readme = "README.md"
authors = [
    { name = "Akwasi Konadu Akuoko", email = "akwasikonadueverlasting@gmail.com" }
]
requires-python = ">=3.12"
dependencies = [
    "requests>=2.32",
]

[project.scripts]
seo-research = "youtube_seo.cli:main"

[build-system]
requires = ["uv_build>=0.11.10,<0.12.0"]
build-backend = "uv_build"

[tool.pyright]
venvPath = "."
venv = ".venv"
extraPaths = ["src"]
```

- [ ] **Step 2: Create `tools/youtube-seo/README.md` (initial stub — fleshed out in a later task)**

```markdown
# youtube-seo

Mine YouTube autocomplete + top-N video metadata for a topic into a structured SEO research artifact at `<video-dir>/seo/research.json`. No API key, anonymous, ~25s per run.

Consumed by the `youtube-seo-research` skill (and downstream consumer skills `script-writer` and `thumbnail-creator`).

## Usage

```bash
# From inside a video folder (reads outline.md H1 for the topic):
uv run --project ../../tools/youtube-seo seo-research

# Or with an explicit topic:
uv run --project ../../tools/youtube-seo seo-research --topic "text rendering"
```

(Detailed flag reference, output schema, troubleshooting — added in Task 11.)
```

- [ ] **Step 3: Create `tools/youtube-seo/src/youtube_seo/__init__.py` as empty**

```python
```

(Public exports added incrementally as modules land.)

- [ ] **Step 4: Create `tools/youtube-seo/src/youtube_seo/cli.py` placeholder**

```python
"""CLI entry point for youtube-seo. Placeholder — wired up in Task 8."""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    print("youtube-seo: not yet implemented", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Initialize the uv environment**

Run from `tools/youtube-seo/`:
```bash
cd tools/youtube-seo && uv sync
```

Expected: creates `.venv/`, installs `requests`. Generates `uv.lock`.

- [ ] **Step 6: Verify the script entry point is wired**

Run from `tools/youtube-seo/`:
```bash
uv run seo-research
```

Expected: prints `youtube-seo: not yet implemented` to stderr, exits 1.

- [ ] **Step 7: Commit**

```bash
git add tools/youtube-seo/pyproject.toml tools/youtube-seo/README.md tools/youtube-seo/src tools/youtube-seo/uv.lock
git commit -m "feat(youtube-seo): scaffold tool with uv project + CLI placeholder"
```

---

## Task 2: Autocomplete fetcher

**Files:**
- Create: `tools/youtube-seo/src/youtube_seo/autocomplete.py`

The autocomplete module fetches YouTube search suggestions from `suggestqueries.google.com` and supports a-z expansion. Pure logic + one HTTP function — no global state, easy to inspect.

- [ ] **Step 1: Write `autocomplete.py`**

```python
"""YouTube autocomplete fetcher (suggestqueries.google.com).

Anonymous JSON endpoint, no API key. Returns up to 10 suggestions per call.
The a-z expansion appends each letter to the seed and aggregates results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from string import ascii_lowercase
import time

import requests

SUGGEST_URL = "https://suggestqueries.google.com/complete/search"
DEFAULT_SLEEP_SECS = 0.3
DEFAULT_TIMEOUT_SECS = 10


@dataclass
class AutocompleteResult:
    """Output of an autocomplete pass.

    `seed` — suggestions for the bare topic.
    `expanded` — suggestions per appended letter ('a'..'z').
    `failed` — True when the pass aborted (e.g. HTTP 429); partial data may
    still be present. Consumers handle this by writing `autocomplete: null`.
    """

    seed: list[str] = field(default_factory=list)
    expanded: dict[str, list[str]] = field(default_factory=dict)
    failed: bool = False


def fetch_one(
    query: str,
    *,
    region: str = "us",
    hl: str = "en",
    timeout: int = DEFAULT_TIMEOUT_SECS,
) -> list[str]:
    """Single autocomplete request. Returns suggestion strings.

    Raises requests.HTTPError on non-2xx (caller decides whether to abort).
    """
    params = {
        "client": "firefox",
        "ds": "yt",
        "hl": hl,
        "gl": region,
        "q": query,
    }
    resp = requests.get(SUGGEST_URL, params=params, timeout=timeout)
    resp.raise_for_status()
    payload = resp.json()
    # Shape: ["query", ["suggestion1", "suggestion2", ...], [], {...}]
    if not isinstance(payload, list) or len(payload) < 2:
        return []
    suggestions = payload[1]
    if not isinstance(suggestions, list):
        return []
    return [s for s in suggestions if isinstance(s, str)]


def fetch_seed_and_expanded(
    topic: str,
    *,
    region: str = "us",
    hl: str = "en",
    sleep_secs: float = DEFAULT_SLEEP_SECS,
) -> AutocompleteResult:
    """Run the full autocomplete pass: seed + a-z expansion.

    On HTTP 429 (or other request failure) anywhere in the pass, sets
    `failed=True` and returns what we have so far. Caller decides whether
    to write `autocomplete: null` or include partial data.
    """
    result = AutocompleteResult()
    try:
        result.seed = fetch_one(topic, region=region, hl=hl)
    except requests.RequestException as exc:
        print(f"autocomplete: seed fetch failed: {exc}")
        result.failed = True
        return result

    for letter in ascii_lowercase:
        time.sleep(sleep_secs)
        try:
            result.expanded[letter] = fetch_one(
                f"{topic} {letter}", region=region, hl=hl
            )
        except requests.RequestException as exc:
            print(f"autocomplete: '{topic} {letter}' failed: {exc}")
            result.failed = True
            return result

    return result
```

- [ ] **Step 2: Smoke-test against the live endpoint**

Run from `tools/youtube-seo/`:
```bash
uv run python -c "from youtube_seo.autocomplete import fetch_one; print(fetch_one('text rendering'))"
```

Expected: prints a list of 5–10 suggestion strings (e.g. `['text rendering', 'text rendering gpu', 'text rendering algorithm', ...]`). If empty list, the endpoint is rate-limiting from this IP — note for later but proceed.

- [ ] **Step 3: Smoke-test the full pass (a-z expansion, ~10s)**

Run:
```bash
uv run python -c "from youtube_seo.autocomplete import fetch_seed_and_expanded; r = fetch_seed_and_expanded('text rendering'); print(f'seed={len(r.seed)} expanded_letters={sum(1 for v in r.expanded.values() if v)} failed={r.failed}')"
```

Expected: ~10s wall time; `seed=` 5–10, `expanded_letters=` 10–25 (most letters return nothing for niche topics), `failed=False`.

- [ ] **Step 4: Commit**

```bash
git add tools/youtube-seo/src/youtube_seo/autocomplete.py
git commit -m "feat(youtube-seo): autocomplete fetcher with a-z expansion"
```

---

## Task 3: yt-dlp search wrapper

**Files:**
- Create: `tools/youtube-seo/src/youtube_seo/search.py`

Shells out to the system `yt-dlp` binary and parses the JSON output.

- [ ] **Step 1: Write `search.py`**

```python
"""Top-N video metadata via yt-dlp.

Shells out to the system yt-dlp binary (assumed on PATH). Returns parsed
per-video dicts with the SEO-relevant fields. Description is truncated to
500 chars to keep the output JSON small.
"""

from __future__ import annotations

from typing import Any
import json
import subprocess

DESCRIPTION_MAX_CHARS = 500

# Fields kept from yt-dlp's per-video JSON. Anything not in this list is
# dropped at output time to keep research.json focused.
KEPT_FIELDS = (
    "title",
    "channel",
    "channel_id",
    "view_count",
    "like_count",
    "comment_count",
    "upload_date",
    "tags",
    "categories",
    "chapters",
    "heatmap",
)


class YtDlpSoftBlock(RuntimeError):
    """Raised when yt-dlp returns the 'Sign in to confirm you're not a bot' message."""


def fetch_top_videos(topic: str, n: int = 30) -> list[dict[str, Any]]:
    """Run `yt-dlp --dump-json ytsearchN:<topic>` and return cleaned dicts.

    Raises YtDlpSoftBlock if YouTube serves the bot-check page.
    Raises subprocess.CalledProcessError on other yt-dlp failures.
    """
    cmd = ["yt-dlp", "--dump-json", f"ytsearch{n}:{topic}"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if proc.returncode != 0:
        stderr = proc.stderr.lower()
        if "sign in to confirm" in stderr or "not a bot" in stderr:
            raise YtDlpSoftBlock(
                "yt-dlp soft-blocked. Try `--cookies-from-browser firefox` "
                "manually, or wait and re-run."
            )
        raise subprocess.CalledProcessError(
            proc.returncode, cmd, output=proc.stdout, stderr=proc.stderr
        )

    videos: list[dict[str, Any]] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        videos.append(_clean(raw))
    return videos


def _clean(raw: dict[str, Any]) -> dict[str, Any]:
    """Keep only KEPT_FIELDS, plus `duration_seconds` and `description_excerpt`."""
    out: dict[str, Any] = {field: raw.get(field) for field in KEPT_FIELDS}
    out["duration_seconds"] = raw.get("duration")
    description = raw.get("description") or ""
    out["description_excerpt"] = description[:DESCRIPTION_MAX_CHARS]
    return out
```

- [ ] **Step 2: Smoke-test against YouTube**

Run from `tools/youtube-seo/`:
```bash
uv run python -c "from youtube_seo.search import fetch_top_videos; vids = fetch_top_videos('text rendering', n=5); print(f'got {len(vids)} videos'); print('first title:', vids[0]['title']); print('first heatmap entries:', len(vids[0].get('heatmap') or []))"
```

Expected: ~5–8s wall time; prints `got 5 videos`, a real title, heatmap entry count (often 50–100 for top performers, 0 for less-watched videos).

- [ ] **Step 3: Commit**

```bash
git add tools/youtube-seo/src/youtube_seo/search.py
git commit -m "feat(youtube-seo): yt-dlp search wrapper for top-N video metadata"
```

---

## Task 4: Signals — `top_nouns`

**Files:**
- Create: `tools/youtube-seo/src/youtube_seo/signals.py` (initial — additional signals appended in Tasks 5–7)

Computes the top-frequency nouns across video titles. Pure function — testable inline with a fixture.

- [ ] **Step 1: Write the initial `signals.py` with `top_nouns` only**

```python
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
    "a", "an", "and", "any", "are", "as", "at", "be", "been", "but", "by",
    "can", "did", "do", "does", "for", "from", "has", "have", "how", "i",
    "if", "in", "is", "it", "its", "just", "me", "my", "no", "not", "now",
    "of", "on", "or", "our", "so", "than", "that", "the", "then", "this",
    "to", "up", "us", "vs", "was", "we", "were", "what", "when", "why",
    "will", "with", "you", "your",
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
```

- [ ] **Step 2: Inline-test `compute_top_nouns` with a fixture**

Run from `tools/youtube-seo/`:
```bash
uv run python -c "
from youtube_seo.signals import compute_top_nouns
videos = [
    {'title': 'How text rendering actually works'},
    {'title': 'Text rendering on the GPU'},
    {'title': 'Why text is hard'},
    {'title': 'Text rendering pipeline explained'},
    {'title': 'Modern text rendering with FreeType'},
]
out = compute_top_nouns(videos, top_n=5)
print(out)
"
```

Expected output (order of equal-count nouns may vary):
```
[{'noun': 'text', 'count': 5}, {'noun': 'rendering', 'count': 4}, ...]
```

Stopwords like `how`, `the`, `with`, `on`, `is`, `actually` must NOT appear in the output. If they do, fix `STOPWORDS`.

- [ ] **Step 3: Commit**

```bash
git add tools/youtube-seo/src/youtube_seo/signals.py
git commit -m "feat(youtube-seo): top_nouns signal (frequency + stopword filter)"
```

---

## Task 5: Signals — `saturation_warnings`

**Files:**
- Modify: `tools/youtube-seo/src/youtube_seo/signals.py` (append)

3-to-6-word n-grams over normalized titles, filtered by view_count > 100K and upload_date within 18 months.

- [ ] **Step 1: Append to `signals.py`**

```python
from collections import defaultdict
from datetime import datetime, timedelta, timezone

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
```

- [ ] **Step 2: Inline-test with a synthetic fixture**

Run from `tools/youtube-seo/`:
```bash
uv run python -c "
from datetime import datetime, timezone
from youtube_seo.signals import compute_saturation_warnings
recent = '20251015'  # within 18 months of 2026-05-09
now = datetime(2026, 5, 9, tzinfo=timezone.utc)
videos = [
    {'title': 'How text rendering works', 'view_count': 200_000, 'upload_date': recent},
    {'title': 'How text rendering really works', 'view_count': 500_000, 'upload_date': recent},
    {'title': 'How text rendering finally works', 'view_count': 150_000, 'upload_date': recent},
    {'title': 'Old video', 'view_count': 999_999, 'upload_date': '20200101'},
    {'title': 'Low-view video', 'view_count': 50, 'upload_date': recent},
]
print(compute_saturation_warnings(videos, now=now))
"
```

Expected: prints at least one warning with `pattern` containing `'text rendering'` (the 3-gram in 3 eligible videos), `match_count: 3`, a `sample_title`. The old video and low-view video must be filtered out (not contributing to counts).

- [ ] **Step 3: Commit**

```bash
git add tools/youtube-seo/src/youtube_seo/signals.py
git commit -m "feat(youtube-seo): saturation_warnings signal (n-gram + recency + view filter)"
```

---

## Task 6: Signals — `demand_phrases`

**Files:**
- Modify: `tools/youtube-seo/src/youtube_seo/signals.py` (append)

Autocomplete suggestions appearing in 3+ adjacent letter expansions.

- [ ] **Step 1: Append to `signals.py`**

```python
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
```

- [ ] **Step 2: Inline-test**

Run from `tools/youtube-seo/`:
```bash
uv run python -c "
from youtube_seo.signals import compute_demand_phrases
expanded = {
    'a': ['text rendering algorithm', 'text rendering api'],
    'b': ['text rendering algorithm', 'text rendering basics'],
    'c': ['text rendering algorithm', 'text rendering c++'],
    'd': ['text rendering deep dive'],
    'e': [],
}
print(compute_demand_phrases(expanded))
"
```

Expected: contains `{'phrase': 'text rendering algorithm', 'letter_hits': 3}`. Other phrases with `letter_hits < 3` must be excluded.

- [ ] **Step 3: Commit**

```bash
git add tools/youtube-seo/src/youtube_seo/signals.py
git commit -m "feat(youtube-seo): demand_phrases signal (letter-hit aggregation)"
```

---

## Task 7: Signals — `hook_patterns`

**Files:**
- Modify: `tools/youtube-seo/src/youtube_seo/signals.py` (append)

Heatmap-derived hook-shape data. Returns `None` when fewer than 5 videos have heatmap.

- [ ] **Step 1: Append to `signals.py`**

```python
import statistics

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
```

- [ ] **Step 2: Inline-test the < 5 threshold**

Run from `tools/youtube-seo/`:
```bash
uv run python -c "
from youtube_seo.signals import compute_hook_patterns
print('with 4 videos:', compute_hook_patterns([{'heatmap': [{'start_time':0,'end_time':10,'value':0.9}]}]*4))
print('with 0 videos:', compute_hook_patterns([]))
"
```

Expected: both print `None`.

- [ ] **Step 3: Inline-test with synthetic heatmap fixture**

Run:
```bash
uv run python -c "
from youtube_seo.signals import compute_hook_patterns
hm = [{'start_time': i*5, 'end_time': (i+1)*5, 'value': max(0.1, 0.95 - i*0.1)} for i in range(20)]
videos = [{'heatmap': hm}] * 6
out = compute_hook_patterns(videos)
print(out)
"
```

Expected: prints a dict with `videos_with_heatmap: 6`, non-None medians, and a `note` string referencing the peak time.

- [ ] **Step 4: Commit**

```bash
git add tools/youtube-seo/src/youtube_seo/signals.py
git commit -m "feat(youtube-seo): hook_patterns signal (heatmap-derived medians, <5 videos = null)"
```

---

## Task 8: Output assembly + atomic write

**Files:**
- Create: `tools/youtube-seo/src/youtube_seo/output.py`

Builds the final JSON dict and writes it atomically (write-to-temp + rename).

- [ ] **Step 1: Write `output.py`**

```python
"""Assemble the final research.json payload and write it atomically."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import os
import tempfile

from youtube_seo.autocomplete import AutocompleteResult
from youtube_seo.signals import (
    compute_demand_phrases,
    compute_hook_patterns,
    compute_saturation_warnings,
    compute_top_nouns,
)


def build_payload(
    *,
    topic: str,
    autocomplete: AutocompleteResult,
    videos: list[dict[str, Any]],
    region: str,
    hl: str,
    n: int,
) -> dict[str, Any]:
    """Compose the canonical research.json structure."""
    return {
        "topic": topic,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "params": {"n": n, "region": region, "hl": hl},
        "autocomplete": (
            None
            if autocomplete.failed
            else {"seed": autocomplete.seed, "expanded": autocomplete.expanded}
        ),
        "top_videos": videos,
        "signals": {
            "top_nouns": compute_top_nouns(videos),
            "saturation_warnings": compute_saturation_warnings(videos),
            "demand_phrases": (
                compute_demand_phrases(autocomplete.expanded)
                if not autocomplete.failed
                else []
            ),
            "hook_patterns": compute_hook_patterns(videos),
        },
    }


def write_atomic(payload: dict[str, Any], output_path: Path) -> None:
    """Write JSON to a temp file in the same directory, then rename."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, indent=2) + "\n"
    fd, tmp_name = tempfile.mkstemp(
        dir=output_path.parent,
        prefix=output_path.name + ".",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(serialized)
        os.replace(tmp_name, output_path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
```

- [ ] **Step 2: Smoke-test atomic write**

Run from `tools/youtube-seo/`:
```bash
uv run python -c "
from pathlib import Path
from youtube_seo.output import write_atomic
p = Path('/tmp/seo-test/foo.json')
write_atomic({'hello': 'world'}, p)
print(p.read_text())
"
```

Expected: prints `{"hello": "world"}` (with indent + trailing newline). Verifies the parent dir was created.

- [ ] **Step 3: Commit**

```bash
git add tools/youtube-seo/src/youtube_seo/output.py
git commit -m "feat(youtube-seo): output assembly + atomic JSON write"
```

---

## Task 9: Wire up the CLI

**Files:**
- Modify: `tools/youtube-seo/src/youtube_seo/cli.py` (replace placeholder)

- [ ] **Step 1: Replace `cli.py` with the wired-up version**

```python
"""CLI entry point for youtube-seo.

Reads a topic from --topic or from outline.md H1 in CWD. Runs the
autocomplete pass + yt-dlp top-N pull, computes signals, writes the
research artifact to <output>/research.json (default <cwd>/seo/research.json).

Exits non-zero on yt-dlp soft-block or when output already exists without --force.
"""

from __future__ import annotations

from pathlib import Path
import argparse
import re
import sys

from youtube_seo.autocomplete import fetch_seed_and_expanded
from youtube_seo.output import build_payload, write_atomic
from youtube_seo.search import YtDlpSoftBlock, fetch_top_videos

DEFAULT_N = 30
DEFAULT_OUTPUT_RELATIVE = Path("seo") / "research.json"

H1_TOPIC_RE = re.compile(r"^#\s+(.+?)\s*(?:—|--)\s*9-beat outline\s*$", re.MULTILINE)


def _read_topic_from_outline(outline_path: Path) -> str | None:
    """Extract the topic from a script-writer outline.md H1.

    H1 shape: '# <topic> — 9-beat outline' (em dash) or '# <topic> -- 9-beat outline'.
    Returns None if the file is missing or the H1 doesn't match.
    """
    if not outline_path.is_file():
        return None
    text = outline_path.read_text(encoding="utf-8")
    match = H1_TOPIC_RE.search(text)
    return match.group(1).strip() if match else None


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="seo-research",
        description=(
            "Mine YouTube autocomplete + top-N video metadata for a topic into "
            "a structured SEO research artifact at <output>/research.json."
        ),
    )
    p.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Explicit topic phrase. If omitted, reads outline.md H1 in CWD.",
    )
    p.add_argument(
        "--n",
        type=int,
        default=DEFAULT_N,
        help=f"Number of top videos to fetch via ytsearchN (default: {DEFAULT_N}).",
    )
    p.add_argument(
        "--region",
        type=str,
        default="us",
        help="Autocomplete region (gl param). Default: us.",
    )
    p.add_argument(
        "--hl",
        type=str,
        default="en",
        help="Autocomplete language (hl param). Default: en.",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Output JSON path. Default: <cwd>/seo/research.json. "
            "Parent directory created if missing."
        ),
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing output file. Default: refuse and exit non-zero.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    cwd = Path.cwd()
    output_path = args.output or (cwd / DEFAULT_OUTPUT_RELATIVE)

    if output_path.exists() and not args.force:
        # Show generated_at if we can read it.
        try:
            import json as _json

            generated_at = _json.loads(output_path.read_text()).get("generated_at", "?")
        except Exception:
            generated_at = "?"
        print(
            f"seo-research: {output_path} already exists "
            f"(generated {generated_at}). Use --force to regenerate.",
            file=sys.stderr,
        )
        return 1

    topic = args.topic or _read_topic_from_outline(cwd / "outline.md")
    if not topic:
        print(
            "seo-research: no --topic given and could not extract one from "
            "outline.md (H1 must match '# <topic> — 9-beat outline').",
            file=sys.stderr,
        )
        return 1

    print(f"seo-research: topic = {topic!r}")
    print(f"seo-research: fetching autocomplete (seed + a-z, ~10s)...")
    autocomplete = fetch_seed_and_expanded(topic, region=args.region, hl=args.hl)
    if autocomplete.failed:
        print("seo-research: autocomplete pass failed; continuing with videos only.")

    print(f"seo-research: fetching top {args.n} videos via yt-dlp (~10s)...")
    try:
        videos = fetch_top_videos(topic, n=args.n)
    except YtDlpSoftBlock as exc:
        print(f"seo-research: {exc}", file=sys.stderr)
        return 2

    print(f"seo-research: assembling payload + writing {output_path}")
    payload = build_payload(
        topic=topic,
        autocomplete=autocomplete,
        videos=videos,
        region=args.region,
        hl=args.hl,
        n=args.n,
    )
    write_atomic(payload, output_path)

    nouns = payload["signals"]["top_nouns"]
    print(
        f"seo-research: done. {len(videos)} videos, "
        f"{sum(1 for s in (autocomplete.expanded.values() if not autocomplete.failed else []) if s)} non-empty letter expansions, "
        f"{len(nouns)} top nouns, {len(payload['signals']['saturation_warnings'])} saturation warnings."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Smoke-test against an existing video folder**

The repo has `videos/why-text-is-hard-2026-05-07/` with an outline.md. Run from there:

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/videos/why-text-is-hard-2026-05-07
uv run --project ../../tools/youtube-seo seo-research
```

Expected: ~25s wall time. Prints topic, progress lines, and a summary. Writes `seo/research.json`.

- [ ] **Step 3: Verify the output JSON shape**

Run from the same video folder:
```bash
uv run python -c "
import json
p = open('seo/research.json')
d = json.load(p)
print('keys:', list(d.keys()))
print('signals keys:', list(d['signals'].keys()))
print('top_videos count:', len(d['top_videos']))
print('first top noun:', d['signals']['top_nouns'][0] if d['signals']['top_nouns'] else None)
print('hook_patterns:', d['signals']['hook_patterns'] is not None)
"
```

Expected: keys include `topic`, `generated_at`, `params`, `autocomplete`, `top_videos`, `signals`. Signals has all 4 sub-keys. Top videos count is ~30. First top noun is a real noun from the niche.

- [ ] **Step 4: Verify --force / no-force behavior**

```bash
# Should refuse:
uv run --project ../../tools/youtube-seo seo-research
# Expected: exits 1 with "already exists" message.

# Should succeed:
uv run --project ../../tools/youtube-seo seo-research --force
# Expected: regenerates the file.
```

- [ ] **Step 5: Commit**

```bash
git add tools/youtube-seo/src/youtube_seo/cli.py
git commit -m "feat(youtube-seo): wire CLI — topic resolution, pipeline, atomic write"
```

---

## Task 10: Public exports + end-to-end check

**Files:**
- Modify: `tools/youtube-seo/src/youtube_seo/__init__.py`

- [ ] **Step 1: Update `__init__.py` to expose the public API**

```python
"""youtube-seo: mine YouTube SEO research for one topic into a JSON artifact."""

from youtube_seo.autocomplete import AutocompleteResult, fetch_seed_and_expanded
from youtube_seo.output import build_payload, write_atomic
from youtube_seo.search import YtDlpSoftBlock, fetch_top_videos
from youtube_seo.signals import (
    compute_demand_phrases,
    compute_hook_patterns,
    compute_saturation_warnings,
    compute_top_nouns,
)

__all__ = [
    "AutocompleteResult",
    "YtDlpSoftBlock",
    "build_payload",
    "compute_demand_phrases",
    "compute_hook_patterns",
    "compute_saturation_warnings",
    "compute_top_nouns",
    "fetch_seed_and_expanded",
    "fetch_top_videos",
    "write_atomic",
]
```

- [ ] **Step 2: Verify import surface**

Run from `tools/youtube-seo/`:
```bash
uv run python -c "import youtube_seo; print(sorted(youtube_seo.__all__))"
```

Expected: prints the alphabetized export list.

- [ ] **Step 3: Commit**

```bash
git add tools/youtube-seo/src/youtube_seo/__init__.py
git commit -m "feat(youtube-seo): expose public API via __init__"
```

---

## Task 11: Flesh out the README

**Files:**
- Modify: `tools/youtube-seo/README.md`

- [ ] **Step 1: Replace the README with the full version**

```markdown
# youtube-seo

Mine YouTube autocomplete + top-N video metadata for one topic into a structured SEO research artifact at `<video-dir>/seo/research.json`. No API key, fully anonymous, ~25s per run.

Consumed by the `youtube-seo-research` skill (and downstream consumer skills `script-writer` and `thumbnail-creator`).

## Usage

From inside a video folder (`videos/<slug>-<date>/`) that already has an `outline.md`:

```bash
# Reads topic from outline.md H1; writes seo/research.json.
uv run --project ../../tools/youtube-seo seo-research

# Or pass an explicit topic:
uv run --project ../../tools/youtube-seo seo-research --topic "text rendering"

# Regenerate (overwrites existing seo/research.json):
uv run --project ../../tools/youtube-seo seo-research --force
```

## Flags

| Flag | Default | Purpose |
|---|---|---|
| `--topic <str>` | (read from `outline.md` H1) | Explicit topic phrase. |
| `--n <int>` | `30` | Number of top videos to fetch via `ytsearchN`. |
| `--region <code>` | `us` | Autocomplete `gl` parameter. |
| `--hl <code>` | `en` | Autocomplete `hl` parameter. |
| `--output <path>` | `<cwd>/seo/research.json` | Where to write. Parent dir created if missing. |
| `--force` | off | Overwrite existing output file. |

## Output

Writes `seo/research.json` with this top-level shape:

```json
{
  "topic": "...",
  "generated_at": "2026-05-09T14:32:00+00:00",
  "params": {"n": 30, "region": "us", "hl": "en"},
  "autocomplete": {"seed": [...], "expanded": {"a": [...], "b": [], ...}},
  "top_videos": [/* per-video metadata: title, channel, view_count, like_count, comment_count, upload_date, tags, categories, chapters, heatmap, description_excerpt, duration_seconds */],
  "signals": {
    "top_nouns": [{"noun": "...", "count": N}],
    "saturation_warnings": [{"pattern": "...", "match_count": N, "sample_title": "..."}],
    "demand_phrases": [{"phrase": "...", "letter_hits": N}],
    "hook_patterns": {"median_peak_position_seconds": N, "median_intensity_at_5s": ..., "videos_with_heatmap": N, "note": "..."} 
  }
}
```

`autocomplete: null` if the autocomplete pass failed (HTTP 429). `signals.hook_patterns: null` if fewer than 5 videos returned heatmap data.

## Troubleshooting

- **`seo-research: yt-dlp soft-blocked`** — YouTube served the bot-check page. Wait 30–60 minutes and retry, or pass cookies manually via the system yt-dlp:
  ```bash
  yt-dlp --cookies-from-browser firefox --dump-json "ytsearch30:<topic>"
  ```
  Cookie support is not built into this CLI in v1.
- **`autocomplete pass failed`** — `suggestqueries.google.com` returned 429. The video pull continues; the output JSON has `autocomplete: null` and `signals.demand_phrases: []`. Re-run later with `--force`.
- **Empty top_nouns / no saturation warnings** — niche topic with very few competitor videos. The signal is "this lane is wide open" — useful information.

## How it works

Three passes, all anonymous:

1. **Autocomplete seed:** one GET to `https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&hl=en&gl=us&q=<topic>`.
2. **Autocomplete a-z expansion:** 26 GETs, one per appended letter, with 0.3s sleep between.
3. **Top-N video pull:** one `yt-dlp --dump-json "ytsearchN:<topic>"` subprocess call.

Then signals are computed from the raw data and the JSON is assembled and atomically written.

See `docs/superpowers/specs/2026-05-09-youtube-seo-research-design.md` for the full design rationale.
```

- [ ] **Step 2: Commit**

```bash
git add tools/youtube-seo/README.md
git commit -m "docs(youtube-seo): full README with flags, output schema, troubleshooting"
```

---

## Task 12: Scaffold the youtube-seo-research skill

**Files:**
- Create: `.claude/skills/youtube-seo-research/SKILL.md`

This is a markdown skill — no automated tests. The Skill tool loads it; the LLM follows it.

- [ ] **Step 1: Write `.claude/skills/youtube-seo-research/SKILL.md`**

```markdown
---
name: youtube-seo-research
description: Mine YouTube autocomplete + top-N video metadata for a topic into <video-dir>/seo/research.json, then surface a 5-line digest of searchable nouns, demand phrases, saturation warnings, and hook-shape data. Use when the user wants to research a topic before titling or scripting — phrases like "research SEO for this video", "what are competitors using", "what should I title this", "do keyword research", "research the topic before I write". Also invoked programmatically by other skills (script-writer, thumbnail-creator) when their consumer hooks detect a missing seo/research.json. Backed by the tools/youtube-seo/ Python CLI; this skill handles natural-language invocation, topic resolution, the digest, and follow-ups.
---

# youtube-seo-research

You are the LLM-driven wrapper around `tools/youtube-seo/`. Your job: resolve which video and topic the research is for, run (or re-use) the research artifact at `<video-dir>/seo/research.json`, and surface a single 5-line digest the user (or invoking skill) can act on.

The tool does the data fetching. You do the workflow, the natural-language interpretation, and the digest. Don't reimplement the tool's logic in shell — always shell out.

## Reference files (load on demand)

- `reference/signal-interpretation.md` — how to read each section of the digest, when to ignore signals, the saturated-keyword trap. Load before printing the digest.
- `reference/consumer-integration.md` — the consumer hook pattern + field map per consumer skill. Load when explaining how consumer skills use the JSON, or when a consumer skill is invoking you.

## Workflow

### Step 1 — Resolve the video folder

Resolve in this order:

1. If the user's message contains a path like `videos/<slug>-<date>/` (relative or absolute), use that.
2. If the current working directory matches `**/videos/<slug>-<date>/`, use that.
3. Otherwise, ask: "Which video folder should I research?" — list existing `videos/*` directories.

Convert the result to an absolute path and use it for every subsequent file read/write.

### Step 2 — Resolve the topic

In this order:

1. If the user's message contains an explicit `topic:` or `--topic` phrase, use that verbatim.
2. If `<video-dir>/outline.md` exists and its H1 matches `# <topic> — 9-beat outline`, extract the topic.
3. Otherwise ask: "What topic phrase should I research? (e.g. 'text rendering', 'database B-tree', 'password hashing slow')". Keep it 2–5 words; YouTube autocomplete works best on short phrases.

Print: `Topic: <topic>` so the user can interrupt if it's wrong.

### Step 3 — Probe `<video-dir>/seo/research.json`

- **Missing** → proceed to Step 4 (run the tool).
- **Present** → read the file's `generated_at` field. Tell the user:
  > "Existing research found (generated <date>, topic: '<topic>'). Use it, or regenerate (~25s)?"
  - "use" / no answer → skip to Step 5 (load + digest).
  - "regenerate" / "force" / "refresh" → continue to Step 4 with `--force`.

### Step 4 — Run the tool

Shell out:

```bash
uv run --project <repo-root>/tools/youtube-seo seo-research \
  --topic "<topic>" \
  [--force]
```

Run from inside the video folder so the default output (`<cwd>/seo/research.json`) lands in the right place. Show the command's stdout/stderr to the user as it runs.

If the tool exits non-zero:
- **Soft-block (`yt-dlp soft-blocked`)** → tell the user, suggest waiting 30–60 minutes or running `yt-dlp --cookies-from-browser firefox` manually. Stop. Do not retry automatically.
- **Other errors** → surface the error, stop.

### Step 5 — Load and print the canonical 5-line digest

Read `<video-dir>/seo/research.json`. Load `reference/signal-interpretation.md` to inform what to highlight.

Print this exact format (substitute real values; omit the hook-shape line when `signals.hook_patterns` is null):

```
SEO context — <topic> (n=<N> videos, <L> autocomplete probes)
  Top searchable nouns: <noun1> (<count>), <noun2> (<count>), <noun3> (<count>)
  Demand phrases:       "<phrase1>", "<phrase2>"
  Saturation warning:   <N> videos >100K views use "<pattern>" — differentiate
  Top-performer ages:   median <X> months, freshest <Y> weeks
  Hook shape:           peak at ~<S>s; top performers hold <P5>%/<P15>%/<P30>% at 5/15/30s
```

When a signal is empty (no demand phrases surfaced, no saturation warnings, etc.), substitute `(none surfaced)` instead of dropping the line — empty signals are themselves informative.

For ages: derive from `top_videos[].upload_date` (yt-dlp format `YYYYMMDD`). Compute median and freshest at print time.

### Step 6 — Offer follow-ups

After the digest, ask:

> "Want me to: (a) expand to a related topic and re-research, (b) hand off to script-writer or thumbnail-creator, or (c) explain any signal in detail?"

Handle each:
- **(a) expand** → take the new topic, restart from Step 3 (probe → fetch → digest).
- **(b) handoff** → invoke the named skill via the `Skill` tool. The consumer skill's hook will detect the now-present `seo/research.json` and use it.
- **(c) explain** → load `reference/signal-interpretation.md`, walk through whichever signal the user asked about, with the actual numbers from this run.

If the user is silent or says "thanks / done", stop here.

## Hard rules

- Never block on missing data. If autocomplete failed (`autocomplete: null` in the JSON), the demand-phrases line says `(none surfaced — autocomplete failed)`. Continue.
- Never edit `seo/research.json` by hand. Re-run with `--force` instead.
- Never invent signals not in the JSON. If `top_nouns` is empty, say so — don't fabricate.
- The digest's job is to inform the user/consumer skill, not to make decisions for them. Don't recommend a specific title; surface what the data shows.

## Things this skill does NOT do

- Generate descriptions, tags, or chapters.
- A/B test titles (YouTube native does that).
- Pull related videos (out of scope; would need Invidious).
- Update consumer skills' decision logic — those skills own their own consumption.
```

- [ ] **Step 2: Verify the skill loads**

The skill is auto-discovered from the `.claude/skills/` directory. Verify by listing in a fresh read:
```bash
ls .claude/skills/youtube-seo-research/
```

Expected: `SKILL.md`. (Reference files added in Tasks 13 and 14.)

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/youtube-seo-research/SKILL.md
git commit -m "feat(skill): youtube-seo-research wrapper around tools/youtube-seo"
```

---

## Task 13: Skill reference — `signal-interpretation.md`

**Files:**
- Create: `.claude/skills/youtube-seo-research/reference/signal-interpretation.md`

- [ ] **Step 1: Write the reference**

```markdown
# Signal interpretation

How to read each section of the SEO research digest, and when to ignore it.

## `top_nouns`

The top-frequency content nouns across the top-N video titles, after stopwords are dropped. Tells you what searchable anchor your title needs to carry.

- **Use when:** picking the searchable noun for a paired YouTube title or working title H1. At least one of the top 3 should appear in any title that wants search reach.
- **Ignore when:** the top noun is the literal topic phrase you already used (it's just confirming you got the keyword right). Look at #2 and #3 for the secondary anchor.
- **Don't trust** counts under 3. With a 30-video corpus, a count of 1–2 is noise.

## `demand_phrases`

Autocomplete suggestions that surfaced in 3+ adjacent letter expansions. These are real, recurring queries — what people actually type into YouTube's search bar.

- **Use when:** picking the title's exact phrasing. A demand phrase that fits naturally is gold — it's the literal query that brings viewers.
- **Ignore when:** the list is empty (sparse niche; autocomplete returned little). Empty is informative — it means you're early in the niche, and the searchable-noun strategy from `top_nouns` matters more.

## `saturation_warnings`

3-to-6-word patterns that appear in 3+ recent (last 18 months) high-view (>100K) videos. Tells you which framings the niche has already collapsed onto.

- **Use when:** sanity-checking a draft title. If your title matches a saturation pattern verbatim, you're competing head-on with established incumbents.
- **Differentiate** the pattern, OR commit to the lane only if your thumbnail claim is genuinely sharper than the incumbents'. The script's iceberg-arc reframing is a structural way to differentiate even when the topic is saturated.
- **Ignore when:** the warning's `match_count` is exactly 3 and the niche is small — could be coincidence. Treat 5+ matches as a hard signal.

## `hook_patterns`

Median peak-position and intensity-at-T-seconds across videos that returned heatmap data (the most-replayed segments).

- **Use when:** drafting beat 1 of the script (the open). The peak position tells you the budget for getting viewers hooked before they drop off — usually 8–15s for top performers.
- **Use when:** scoping the open + subversion combined. If `median_intensity_at_15s` is below 0.6, top performers are already losing 40% of viewers by 15s — your open + subversion together must finish before then.
- **Ignore when:** `hook_patterns` is `null` (fewer than 5 videos in the corpus had heatmap data — happens for low-view niches).

## The saturated-keyword trap

The biggest failure mode of any keyword research workflow: the data tells you "demand exists for phrasing X", you adopt phrasing X, and you compete head-on with a 2M-view incumbent that already owns it.

The signal is telling you **demand exists**, not **that exact phrasing will win for you**. Use the research to find the **adjacent under-served phrasing** — long-tail demand phrases with no saturation warning attached — and pair that with a thumbnail or script angle that claims something the incumbents don't.

## When to ignore the digest entirely

- The corpus is empty or near-empty (`top_videos: []` or 1–2 entries). The niche doesn't exist on YouTube yet, or your topic phrasing is too unusual to surface results. Try a related broader phrasing.
- All signals are empty AND the topic is one you know is searched-for. The autocomplete pass likely 429'd — check `autocomplete: null` in the JSON and re-run with `--force` later.
- You have a strong editorial reason to use a phrasing the data discourages. Editorial taste beats SEO when the trade-off is real (e.g., the channel's voice).
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/youtube-seo-research/reference/signal-interpretation.md
git commit -m "docs(youtube-seo-research): signal-interpretation reference"
```

---

## Task 14: Skill reference — `consumer-integration.md`

**Files:**
- Create: `.claude/skills/youtube-seo-research/reference/consumer-integration.md`

- [ ] **Step 1: Write the reference**

```markdown
# Consumer integration

How other skills consume `<video-dir>/seo/research.json` via the shared hook pattern.

## The hook (3 steps)

Any skill that benefits from SEO context follows this hook at its decision point:

1. **Probe** for `<video-dir>/seo/research.json`.
2. **Missing** → invoke the `youtube-seo-research` skill via the `Skill` tool, with one-line user confirmation. If the user declines, proceed without it. **Never block on missing data.**
3. **Present** → load it. Read the fields the consumer skill cares about (see field map below). Optionally surface a consumer-specific compressed digest at the consumer's decision point.

The full canonical 5-line digest is printed once by `youtube-seo-research` when it runs. Consumer-specific digests are compressed reminders printed at consumer decision moments (e.g., thumbnail-creator's title-pairing step) that may happen hours or days after the original research.

## Field map per consumer

| Consumer | Decision point | Fields used |
|---|---|---|
| `script-writer` | Step 2.5 (research checkpoint) + Step 3 (outline) | `signals.top_nouns` (working title), `signals.saturation_warnings` (framing), `signals.hook_patterns` (beat 1 budget), `top_videos[].chapters` (coverage check) |
| `thumbnail-creator` | Step 2 (probe) + Step 4 (paired title) | `signals.top_nouns`, `signals.demand_phrases`, `signals.saturation_warnings`, `top_videos[].upload_date` (recency context) |

## Adding a new consumer

1. Identify the decision point in the consumer skill's flow — the moment a SEO-aware decision is being made.
2. Add the probe + invoke-or-fall-back at that point. Use the same prompt shape: "No SEO research found. Run it now via the youtube-seo-research skill (~25s)? [Y/n/skip]". On Y, invoke `youtube-seo-research` via the `Skill` tool.
3. Document which fields you read in this table.
4. Decide whether to print a consumer-specific compressed digest at your decision point, or rely on the canonical digest the youtube-seo-research skill prints at fetch time. Print one if your decision point is plausibly hours/days after the original research (the user has likely forgotten the digest).

## Hard rules for consumers

- **Never block on missing data.** If the user declines to run research, the consumer skill must still complete its job using its existing logic.
- **Never invent signals.** Only read what's in the JSON. Empty arrays mean empty — don't fabricate signals to fill the digest.
- **Re-run only via the youtube-seo-research skill.** Never edit `seo/research.json` directly. Consumer skills consume; they don't write.
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/youtube-seo-research/reference/consumer-integration.md
git commit -m "docs(youtube-seo-research): consumer-integration reference"
```

---

## Task 15: Wire script-writer (Step 2.5)

**Files:**
- Modify: `.claude/skills/script-writer/SKILL.md`

Insert a new "Step 2.5 — SEO research checkpoint" between the existing Step 2 and Step 3, plus update Step 3 to read the SEO data when present.

- [ ] **Step 1: Insert Step 2.5 after Step 2 in `script-writer/SKILL.md`**

Find the section ending with the `npx hyperframes init` block (end of Step 2), and BEFORE the `### Step 3 — 9-beat outline checkpoint` heading. Add a new step:

Use Edit with this `old_string` (the existing transition between Step 2 and Step 3):

```
Use today's date. The project's `CLAUDE.md` is strict about this folder convention — never author files at the repo root. All subsequent writes go into the new folder.

### Step 3 — 9-beat outline checkpoint
```

And this `new_string`:

```
Use today's date. The project's `CLAUDE.md` is strict about this folder convention — never author files at the repo root. All subsequent writes go into the new folder.

### Step 2.5 — SEO research checkpoint

Before drafting the outline, give the user the option to run SEO research on the topic. The data informs which searchable nouns the working title should anchor on, which framings are saturated by recent incumbents, and how much hook-time top performers have to play with in beat 1.

Probe `<video-dir>/seo/research.json`:

- **Present** → load it. Print one line: `Using existing seo/research.json (generated <date>, topic: '<topic>').` Continue to Step 3.
- **Missing** → ask once: `"Want to run SEO research on '<topic>' before drafting the outline? Will surface searchable nouns, demand phrases, and what incumbents already cover, so the working title and framing can differentiate. (~25s, no API key) [Y/n/skip]"`
  - **Y** → invoke the `youtube-seo-research` skill via the `Skill` tool. It runs the research and prints its 5-line digest. Continue to Step 3 with the JSON loaded.
  - **n / skip** → continue to Step 3 without SEO data. Don't re-prompt later in this session.

Never block on missing or declined research. The outline can be drafted without it; the SEO data only informs choices, never requires them.

### Step 3 — 9-beat outline checkpoint
```

- [ ] **Step 2: Update Step 3 to reference SEO usage**

Find this passage in Step 3:

```
Load `reference/nine-beat-arc.md`. Draft a one-line outline for each of the 9 beats based on the topic + notes. Don't write prose yet — single declarative sentences only, naming what each beat does for *this* topic.
```

Replace with:

```
Load `reference/nine-beat-arc.md`. Draft a one-line outline for each of the 9 beats based on the topic + notes. Don't write prose yet — single declarative sentences only, naming what each beat does for *this* topic.

If `seo/research.json` was loaded in Step 2.5, let it inform the outline:

- **Working title H1** — bias the topic phrasing toward a top searchable noun from `signals.top_nouns`. The H1 becomes the file's identity and what `thumbnail-creator` later reads, so the searchable anchor pays off twice.
- **Framing** — if `signals.saturation_warnings` flags a `"how X works"` pattern that matches your natural framing, lean on the iceberg arc's reframing strength to differentiate (open with the mundane action, not the explainer setup).
- **Beat 1 hook budget** — if `signals.hook_patterns.median_peak_position_seconds` is, say, ~12s, that's the budget for the open + subversion combined before viewers drop off. Tightens the discipline already in `nine-beat-arc.md`.
- **Coverage check** — read `top_videos[].chapters` titles for the top 5–10 videos. If you're about to retread a beat that incumbents already over-cover, flag it during outline review and ask whether to differentiate.

If the SEO file was not loaded, draft the outline from topic + notes alone (current behavior).
```

- [ ] **Step 3: Verify the file edits look right**

Run:
```bash
grep -n "Step 2.5" .claude/skills/script-writer/SKILL.md
grep -n "seo/research.json" .claude/skills/script-writer/SKILL.md
```

Expected: Step 2.5 appears once. `seo/research.json` appears at least 3 times (Step 2.5 probe, Step 2.5 prompt, Step 3 reference).

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/script-writer/SKILL.md
git commit -m "feat(script-writer): integrate seo/research.json at Step 2.5 + Step 3"
```

---

## Task 16: Wire thumbnail-creator (Step 2 probe + Step 4 digest)

**Files:**
- Modify: `.claude/skills/thumbnail-creator/SKILL.md`
- Modify: `.claude/skills/thumbnail-creator/reference/youtube-title-pairing.md`

- [ ] **Step 1: Add the probe to the end of Step 2 in `thumbnail-creator/SKILL.md`**

Find this passage in Step 2:

```
If `script.md` is missing, warn the user but proceed — the rephrase
step works on the title alone; icon and accent picks just have less
context to draw from.
```

Replace with:

```
If `script.md` is missing, warn the user but proceed — the rephrase
step works on the title alone; icon and accent picks just have less
context to draw from.

Then probe `<video-dir>/seo/research.json`:

- **Present** → load it for use at Step 4. Print: `Using SEO research from <date>.`
- **Missing** → ask once per session: `"No SEO research found. Run it now via the youtube-seo-research skill (~25s)? [Y/n/skip]"`. On Y, invoke `youtube-seo-research` via the `Skill` tool and load the result. On n/skip, proceed without it (current behavior) and don't re-prompt during subsequent thumbnail iterations in the same session.

Never block on missing data — the rephrase, icon, and accent picks all work fine without SEO context. The data only informs Step 4 (paired title).
```

- [ ] **Step 2: Add the digest to the start of Step 4**

Find Step 4's opening:

```
### Step 4 — Pair a YouTube title to each rephrase

Load `reference/youtube-title-pairing.md`. For each variant text from
Step 3, write **one** paired YouTube title that the video would ship
with if that variant won.
```

Replace with:

```
### Step 4 — Pair a YouTube title to each rephrase

Load `reference/youtube-title-pairing.md`. For each variant text from
Step 3, write **one** paired YouTube title that the video would ship
with if that variant won.

If `seo/research.json` was loaded in Step 2, before producing the 3 paired titles, print this compressed digest (4 data lines — the hook-shape line is dropped because title pairing is not where hook shape applies):

```
SEO context — <topic> (n=<N> videos)
  Top searchable nouns: <noun1> (<count>), <noun2> (<count>), <noun3> (<count>)
  Demand phrases:       "<phrase1>", "<phrase2>"
  Saturation warning:   <N> videos >100K views use "<pattern>" — differentiate
  Top-performer ages:   median <X> months, freshest <Y> weeks
```

For ages: derive from `top_videos[].upload_date` (yt-dlp format `YYYYMMDD`) at print time. When a signal is empty, substitute `(none surfaced)` instead of dropping the line — empty is informative.

Then produce the 3 paired titles informed by — but not slavishly conforming to — the digest. The "Using SEO research" section in `youtube-title-pairing.md` codifies what to do with each signal.
```

- [ ] **Step 3: Add the "Using SEO research" section to `youtube-title-pairing.md`**

Append at the end of `.claude/skills/thumbnail-creator/reference/youtube-title-pairing.md`:

```markdown

## Using SEO research

When `<video-dir>/seo/research.json` is loaded (probed at Step 2 of thumbnail-creator), the per-variant title-writing routine has more to work with. Apply these rules in addition to the base routine above:

- **Always carry a search anchor.** Include at least one of the top 3 entries from `signals.top_nouns` in the title. That's the literal noun viewers type into YouTube search; without it, you lose search reach regardless of how good the claim is.
- **Avoid verbatim saturation patterns.** If `signals.saturation_warnings` lists `"how X works"` and your draft title is `"How text rendering works"`, you're competing head-on with 5+ recent >100K-view incumbents. Either rephrase (`"What text rendering really does"`, `"Inside the text rendering pipeline"`) or commit to the lane deliberately because your thumbnail claim is genuinely sharper.
- **Prefer demand phrases when natural.** Entries in `signals.demand_phrases` are recurring autocomplete completions — real queries getting typed. If one fits the variant's claim shape without contortion, use it verbatim. Don't force-fit.
- **Vary across variants.** With 3 variants, ideally each carries a different noun from the top-3 list. Don't make all three orbit the same noun — that wastes the A/B surface.
- **Empty signals are informative, not blocking.** If `top_nouns` is empty (sparse niche) or `saturation_warnings` is empty (open lane), draft the paired titles from your own judgment per the base rules. Never skip Step 4 because the SEO data was thin.
```

- [ ] **Step 4: Verify the edits**

Run:
```bash
grep -n "seo/research.json" .claude/skills/thumbnail-creator/SKILL.md
grep -n "Using SEO research" .claude/skills/thumbnail-creator/reference/youtube-title-pairing.md
```

Expected: `seo/research.json` appears at least twice in SKILL.md. The "Using SEO research" header appears once in the reference file.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/thumbnail-creator/SKILL.md .claude/skills/thumbnail-creator/reference/youtube-title-pairing.md
git commit -m "feat(thumbnail-creator): integrate seo/research.json at Step 2 probe + Step 4 digest"
```

---

## Task 17: Update root `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md`

Add the per-video SEO research subsection alongside the existing narration-map block.

- [ ] **Step 1: Find the narration-map block in `CLAUDE.md`**

Grep to locate it:
```bash
grep -n "narration-map" CLAUDE.md | head -5
```

Identify the block ending (after the `uv run --project ../../tools/narration-map ...` example and the trailing description). The new block goes immediately after, still inside the "1. Transcript-as-timing-truth" section since it shares the per-video tool pattern.

- [ ] **Step 2: Add the new subsection**

Find this passage in `CLAUDE.md`:

```
Writes `narration-map.json` next to the transcript. See
`tools/narration-map/README.md` for the full output shape and tunables.
```

Replace with:

```
Writes `narration-map.json` next to the transcript. See
`tools/narration-map/README.md` for the full output shape and tunables.

**YouTube SEO research is a shared per-video artifact.** The
`youtube-seo-research` skill (backed by `tools/youtube-seo/`) generates
`<video-dir>/seo/research.json` from one topic phrase using yt-dlp +
YouTube autocomplete (free, no API key, ~25s). Multiple skills consume
it: `script-writer` reads it at the outline step (Step 2.5),
`thumbnail-creator` reads it at the paired-title step (Step 4). Run it
once per video — both skills will probe for it and offer to invoke the
`youtube-seo-research` skill if it's missing.

```bash
# From inside the video folder, after outline.md exists:
uv run --project ../../tools/youtube-seo seo-research
```

Writes `<video-dir>/seo/research.json`. See the skill's
`reference/signal-interpretation.md` for how to read the digest, and
`reference/consumer-integration.md` for which fields each consumer skill
uses.
```

- [ ] **Step 3: Verify the edit**

Run:
```bash
grep -n "youtube-seo" CLAUDE.md
```

Expected: 3+ matches (skill name, tool path, command example).

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(claude.md): document youtube-seo-research per-video workflow"
```

---

## Task 18: End-to-end smoke test

**Files:**
- (verification only — no edits)

Verify the full pipeline: tool produces correct JSON; consumer skills detect and consume it correctly.

- [ ] **Step 1: Confirm the tool already produced output for the existing video**

```bash
ls /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/videos/why-text-is-hard-2026-05-07/seo/
```

Expected: `research.json` exists from the Task 9 smoke test.

- [ ] **Step 2: Validate the JSON structure**

Run:
```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/videos/why-text-is-hard-2026-05-07
uv run python -c "
import json
d = json.load(open('seo/research.json'))
required_keys = {'topic', 'generated_at', 'params', 'autocomplete', 'top_videos', 'signals'}
assert required_keys <= d.keys(), f'missing: {required_keys - d.keys()}'
required_signals = {'top_nouns', 'saturation_warnings', 'demand_phrases', 'hook_patterns'}
assert required_signals <= d['signals'].keys(), f'missing signals: {required_signals - d[\"signals\"].keys()}'
assert isinstance(d['top_videos'], list) and len(d['top_videos']) > 0
print('JSON shape OK')
print(f'top videos: {len(d[\"top_videos\"])}')
print(f'top nouns: {[n[\"noun\"] for n in d[\"signals\"][\"top_nouns\"][:3]]}')
print(f'hook_patterns present: {d[\"signals\"][\"hook_patterns\"] is not None}')
"
```

Expected: prints `JSON shape OK`, the video count, the top 3 nouns (real words from the typography niche), and whether hook_patterns is non-null.

- [ ] **Step 3: Manually invoke the youtube-seo-research skill (in a fresh Claude Code session)**

This step is not automatable — it requires Claude Code to load and run the skill. Document for the operator:

> In a fresh Claude Code session in the repo root, run:
> ```
> /youtube-seo-research
> ```
> When asked which video, point at `videos/why-text-is-hard-2026-05-07/`. The skill should detect the existing `seo/research.json`, offer to use or regenerate, and on "use" should print the canonical 5-line digest. Verify the digest formatting matches the SKILL.md spec (5 lines including hook shape since heatmap data exists).

- [ ] **Step 4: Manually verify thumbnail-creator integration**

Document for the operator:

> In the same Claude Code session, in `videos/why-text-is-hard-2026-05-07/`, invoke the thumbnail-creator skill on a working title. At Step 2, the probe should detect the existing `seo/research.json` and print `Using SEO research from <date>.`. At Step 4, the compressed 4-line digest should print before the 3 paired titles. The paired titles should each carry one of the top searchable nouns from the digest.

- [ ] **Step 5: Manually verify script-writer integration on a fresh topic**

Document for the operator:

> Start a fresh script-writer flow on a topic with no existing video folder (e.g. "how does a database B-tree work"). At Step 2.5, the skill should ask whether to run SEO research. On Y, it should invoke youtube-seo-research, which writes `seo/research.json` in the new folder. Step 3 should then reference SEO signals when justifying outline choices.

- [ ] **Step 6: Final commit (no code, but a marker for completion)**

If any operator-step revealed a bug, fix it in a follow-up commit. Otherwise no commit is needed for this verification task.

---

## Task 19: Final cleanup checklist

**Files:**
- (verification only — no edits)

- [ ] **Step 1: Verify all expected files exist**

```bash
test -f tools/youtube-seo/pyproject.toml
test -f tools/youtube-seo/README.md
test -f tools/youtube-seo/src/youtube_seo/__init__.py
test -f tools/youtube-seo/src/youtube_seo/cli.py
test -f tools/youtube-seo/src/youtube_seo/autocomplete.py
test -f tools/youtube-seo/src/youtube_seo/search.py
test -f tools/youtube-seo/src/youtube_seo/signals.py
test -f tools/youtube-seo/src/youtube_seo/output.py
test -f .claude/skills/youtube-seo-research/SKILL.md
test -f .claude/skills/youtube-seo-research/reference/signal-interpretation.md
test -f .claude/skills/youtube-seo-research/reference/consumer-integration.md
echo "all files present"
```

Expected: prints `all files present`. Any failure means a file was missed in earlier tasks.

- [ ] **Step 2: Verify clean git status**

```bash
git status
```

Expected: only `tools/topic-pipeline/.gitignore` remains modified (pre-existing). All youtube-seo and skill changes should be committed.

- [ ] **Step 3: Verify commit history**

```bash
git log --oneline -20
```

Expected: ~17–18 commits matching the task structure (one per task that committed code/docs):

- `feat(youtube-seo): scaffold tool with uv project + CLI placeholder`
- `feat(youtube-seo): autocomplete fetcher with a-z expansion`
- `feat(youtube-seo): yt-dlp search wrapper for top-N video metadata`
- `feat(youtube-seo): top_nouns signal (frequency + stopword filter)`
- `feat(youtube-seo): saturation_warnings signal (n-gram + recency + view filter)`
- `feat(youtube-seo): demand_phrases signal (letter-hit aggregation)`
- `feat(youtube-seo): hook_patterns signal (heatmap-derived medians, <5 videos = null)`
- `feat(youtube-seo): output assembly + atomic JSON write`
- `feat(youtube-seo): wire CLI — topic resolution, pipeline, atomic write`
- `feat(youtube-seo): expose public API via __init__`
- `docs(youtube-seo): full README with flags, output schema, troubleshooting`
- `feat(skill): youtube-seo-research wrapper around tools/youtube-seo`
- `docs(youtube-seo-research): signal-interpretation reference`
- `docs(youtube-seo-research): consumer-integration reference`
- `feat(script-writer): integrate seo/research.json at Step 2.5 + Step 3`
- `feat(thumbnail-creator): integrate seo/research.json at Step 2 probe + Step 4 digest`
- `docs(claude.md): document youtube-seo-research per-video workflow`

If any are missing, the corresponding task didn't commit; trace back and commit the missing changes.
