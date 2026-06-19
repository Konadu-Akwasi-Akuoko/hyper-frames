# tools/thumbnail-inspo

Mechanical backing tools for the `thumbnailInspo/` reference library (repo root).
Deterministic and judgment-free — they harvest and measure; Claude authors the
index prose. Mirrors how `tools/inspo-ingest` backs `motionGraphicsInspo/`.

## `fetch.py` — harvest top thumbnails per channel

Resolves each channel's *Popular* playlist (`UULP` + channel-id suffix, which
YouTube returns view-sorted) — or the `/shorts` tab for shorts channels — takes
the top N entries, and pulls each thumbnail straight from the `i.ytimg.com` CDN
(`maxresdefault` → `sddefault` → `hqdefault` fallback) into
`thumbnailInspo/<slug>/<rank>-<id>.jpg`, with a per-channel `_manifest.json`
(rank, id, title, watch URL, quality).

**Bot-wall discipline:** the only YouTube tab-extractor traffic is ONE flat
metadata dump per channel, run serially with a sleep between channels. The
thumbnail bitmaps come from the CDN, which is not bot-walled. Re-runs are
resumable (present files are skipped).

```bash
python3 tools/thumbnail-inspo/fetch.py [--count 30] [--only slug,slug] [--list channels.txt]
```

Channels live in `channels.txt` (`<handle> <mode> <slug>`, mode ∈ `videos`|`shorts`).
Edit it and re-run to refresh or extend the library.

## `grid.py` — overlay a measuring grid for replication

Stamps a labeled coordinate grid on a reference so its element positions read off
in the same pixel space the thumbnail templates use (1280x720 / 1080x1920):
a numbered 4x4 major grid of cells, fine minor gridlines, and pixel rulers along
the top (x) and left (y) edges.

```bash
python3 tools/thumbnail-inspo/grid.py thumbnailInspo/<channel>/<file>.jpg [--out OUT.png] [--cols 4] [--rows 4] [--minor 80]
```

Writes `<file>.jpg.grid.png` next to the input by default.

## Requirements

`yt-dlp`, `curl`, and ImageMagick (`magick`) on PATH. The grid font is
`/System/Library/Fonts/Monaco.ttf` (single-file mono, magick-safe on this Mac).
