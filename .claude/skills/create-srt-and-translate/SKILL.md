---
name: create-srt-and-translate
description: Generate a video's English captions.srt from its Scribe v2 transcript and translate it into the 13 languages YouTube auto-dubs (Arabic, German, Spanish, French, Hindi, Indonesian, Italian, Japanese, Polish, Portuguese, Russian, Turkish, Vietnamese). Use this skill whenever the user says "create the SRT", "translate the captions", "generate captions for this video", "make the multilingual subtitles", or anything similar after the voiceover step has run and a transcript.json exists. Triggers on phrases like "translate my video to all languages", "do the localization", "prep this for multi-language upload". Always run from inside or against a `videos/<slug>-<date>/` folder.
---

# create-srt-and-translate

Generate a video's English captions.srt and the full set of YouTube
multi-language subtitle localizations from one invocation.

Thumbnail-title localization is intentionally out of scope. Thumbnails ship
in English; if titles ever need to be localized, that's a separate manual
pass through the thumbnail-creator pipeline.

## When to invoke

After the voiceover step (`voiceover-elevenlabs-v2` or v3) has produced
`transcript.json` at the video folder root.

The skill is safe to re-run — it overwrites the same output paths. Each
language file is independent, so partial re-runs are fine.

## What it produces

```
videos/<slug>-<date>/
├── captions.srt                          ← English source SRT
└── multi-lingual/
    └── srt/
        ├── ar.srt   de.srt   es.srt   fr.srt   hi.srt
        ├── id.srt   it.srt   ja.srt   pl.srt   pt.srt
        └── ru.srt   tr.srt   vi.srt
```

Each `<lang>.srt` mirrors the English `captions.srt` block-for-block with
identical timestamps.

## Target languages

These are the 13 YouTube auto-dub languages worth pairing subtitles with as
of 2026. The first eight (en, es, pt, fr, de, it, hi, id) get YouTube's
Expressive Speech dubbing; all 13 get standard auto-dub.

| Code | Language | Script | Notes |
|---|---|---|---|
| `ar` | Arabic (MSA) | Arabic, RTL | Use Arabic comma `،` and question mark `؟` |
| `de` | German | Latin | Long compounds OK; preserves "Sie" register |
| `es` | Spanish | Latin | Neutral / Latin American register |
| `fr` | French | Latin | "vous" register; `« … »` quotes |
| `hi` | Hindi | Devanagari | Indian numbering (lakh/crore/arab) for large numbers |
| `id` | Indonesian | Latin | Bahasa Indonesia |
| `it` | Italian | Latin | |
| `ja` | Japanese | Hiragana/Katakana/Kanji | `「 」` quotes |
| `pl` | Polish | Latin (diacritics) | |
| `pt` | Portuguese | Latin | Brazilian Portuguese register |
| `ru` | Russian | Cyrillic | `« … »` quotes |
| `tr` | Turkish | Latin (diacritics) | |
| `vi` | Vietnamese | Latin (tone marks) | |

Translation style — read `references/translation-style.md` before you
write any translation. It documents which technical terms stay in Latin
script (CAPTCHA, GPT-4, TaskRabbit, etc.), how to handle numbers, ALL-CAPS
anchors, RTL, and per-language quotation conventions.

## Workflow

### Step 1 — Resolve the video folder

Default to the current working directory if it is a `videos/<slug>-<date>/`
folder (looks for `transcript.json` and either `hyperframes.json` or
`package.json` at the root). Otherwise the user must pass the path
explicitly (e.g. "create the SRTs for `videos/why-text-is-hard-2026-05-07/`").

Verify `<video-folder>/transcript.json` exists before starting.

`voiceover.txt` is **not** required by the script. If present, it can be
referenced for cleaner casing/spelling on a manual pass, but the chunker
uses `transcript.json` text directly.

### Step 2 — Generate the English captions.srt

Run the bundled chunker:

```bash
python3 .claude/skills/create-srt-and-translate/scripts/transcript_to_srt.py \
  <video-folder>/transcript.json
```

It writes `<video-folder>/captions.srt`. The chunker groups words into
SRT blocks using sentence-break preferences and ~84 char / 7 s caps. See
`references/srt-chunking-rules.md` if you ever need to tune.

If captions.srt already exists, the script overwrites it. That's
intentional — re-runs should be idempotent.

### Step 3 — Translate the SRT into 13 languages

Read `captions.srt`, then write one translated file per language code into
`<video-folder>/multi-lingual/srt/`. Each translated file:

- **Preserves block numbers and timestamps verbatim.** Only the text changes.
- **Preserves the line-wrap structure when reasonable.** Translations may
  shift line breaks slightly (German often longer than English, Indonesian
  often shorter); that's fine. The viewer doesn't see line breaks differently
  from the original.
- **Follows `references/translation-style.md`** for technical-term
  handling, numbers, ALL-CAPS, RTL, quotation marks, and register.

Translate each language as a single `Write` of the full SRT — do not
attempt to split the translation across multiple write operations. The
file must be a complete, valid SRT before YouTube will accept the upload.

After writing all 13 SRT files, verify they all have the same number of
blocks as `captions.srt`:

```bash
for f in <video-folder>/multi-lingual/srt/*.srt; do
  echo -n "$f: "
  grep -c '^[0-9]\+$' "$f"
done
```

Every file should report the same count.

### Step 4 — Report

Summarize for the user:

- The number of SRT blocks per language (should all match captions.srt).
- A reminder of the Studio upload path:
  `Studio → Subtitles → Add language → Upload file → With timing`.

## Things this skill does NOT do

- **Does not translate thumbnail titles.** Thumbnails ship in English. If
  the user wants localized thumbnail text, that is a separate manual pass
  through the thumbnail-creator pipeline with explicit text overrides.
- **Does not align voiceover.txt against transcript.json.** Captions
  use Scribe v2's transcribed text verbatim. If the script's exact
  casing/spelling matters (e.g. brand names that Scribe misheard), a
  manual pass on captions.srt before translating is the cleanest fix.
- **Does not handle dialect splits within a language code.** `es.srt` is
  a single neutral Spanish; if you need Castilian vs. Latin American
  separately, that's a manual fork. Same applies to `pt` (Brazilian
  default), `ar` (MSA default), and `zh` (not in the set).
- **Does not auto-upload to YouTube.** Output is on disk; the user runs
  the uploads through Studio.

## Files referenced

- `scripts/transcript_to_srt.py` — Scribe v2 → SRT chunker.
- `references/translation-style.md` — terminology, numbers, scripts, register.
- `references/srt-chunking-rules.md` — block-size heuristic parameters.
