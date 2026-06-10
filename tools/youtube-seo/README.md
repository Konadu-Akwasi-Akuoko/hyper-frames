# youtube-seo

Mine YouTube autocomplete + top-N video metadata for one topic into a structured SEO research artifact at `<video-dir>/seo/research.json`. No API key, fully anonymous, ~25s per run.

Consumed by the `youtube-seo-research` skill (and downstream consumer skills `script-writer` and `thumbnail-and-title-generator`).

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
