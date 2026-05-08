# Research: PawelCodeStuff

Cross-cutting research on the [PawelCodeStuff YouTube channel](https://www.youtube.com/@pawel_code_stuff/videos)
to inform script-writing and production patterns for hyper-frames videos.

## Channel snapshot (as of 2026-05-07)

- 8 videos, all uploaded between 2026-04-09 and 2026-05-01
- 12,200 subscribers, ~244K cumulative views
- Breakout video "Why is rendering text so complicated?" — 125K views, 10.3% like rate
- Format: short technical deep-dives, 3–10 min, voiceover + visuals

## Layout

```
research/pawel-code-stuff/
├── README.md                          (this file)
├── scripts/
│   ├── parse_transcripts.py           json3 → clean + timed transcript converter
│   └── extract_comments.py            info.json comments → per-video JSON + aggregate CSV
├── transcripts/
│   ├── raw/                           yt-dlp .en.json3 (and read-only .en-orig duplicates)
│   ├── clean/                         plain text, sentence-wrapped
│   └── timed/                         [mm:ss.mmm] prefixed lines
├── thumbnails/
│   ├── 01-load-balancing.jpg .. 08-text-rendering.jpg   1280x720 thumbnails
│   └── contact-sheet.html             sortable visual mosaic of all 8 thumbnails
├── comments/
│   ├── raw/                           yt-dlp .info.json files with embedded comments
│   ├── clean/                         per-video .comments.json + _all-comments.csv + _summary.csv
│   └── top-comments-swipe.md          best comments organized by theme (swipe file)
└── analysis/
    ├── script-patterns.md             script pattern analysis across top 5 videos
    ├── thumbnail-patterns.md          thumbnail visual + text-strategy analysis (all 8)
    ├── comment-insights.md            audience do's and don'ts from 622 mined comments
    ├── distribution-channels.md       cross-platform mention search + Day-1 launch playbook
    └── topic-selection.md             reverse-engineered topic pipeline + 30-topic backlog
```

## How transcripts were pulled

```bash
yt-dlp --skip-download --write-auto-subs \
       --sub-langs "en.*,en" --sub-format json3 \
       --output "<slug>.%(ext)s" \
       "https://www.youtube.com/watch?v=<id>"
```

YouTube auto-captions only — none of the 5 videos publish manual subs.

## Videos studied (top 5 by engagement)

| # | Slug | Video ID | Title |
|---|---|---|---|
| 1 | `01-why-text-rendering` | 4soZ33MvlW4 | Why is rendering text so complicated? |
| 2 | `02-autoincrement-vs-uuid` | JbdvmQ_HgJo | Auto-Increment vs UUID Explained in 5 Minutes |
| 3 | `03-mouse-secure-keys` | DB0dEPDCm24 | Why Moving Your Mouse Generates Secure Keys |
| 4 | `04-password-hashing-slow` | lLDZ9O8E62Y | Why Good Password Hashing is Intentionally Slow |
| 5 | `05-three-databases` | rZbJLJIESZg | 3 Databases Built for Specific Problems |

## Re-running

```bash
# from research/pawel-code-stuff/
python3 scripts/parse_transcripts.py .
```
