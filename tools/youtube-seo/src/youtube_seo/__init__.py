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
