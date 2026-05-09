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
