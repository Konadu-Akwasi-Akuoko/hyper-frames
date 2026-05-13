---
name: create-srt-and-translate
description: Generate a video's English captions.srt from its Scribe v2 transcript and translate everything into the 13 languages YouTube auto-dubs (Arabic, German, Spanish, French, Hindi, Indonesian, Italian, Japanese, Polish, Portuguese, Russian, Turkish, Vietnamese). Also translates the 3 thumbnail variant titles (overlay text + YouTube title) from every contact-sheet.html under thumbnails/. Use this skill whenever the user says "create the SRT", "translate the captions", "generate captions for this video", "translate the thumbnails", "localize the titles", "make the multilingual subtitles", or anything similar after the voiceover step has run and a transcript.json exists. Also use after a thumbnail round is created when the user wants the titles localized. Triggers on phrases like "translate my video to all languages", "do the localization", "prep this for multi-language upload". Always run from inside or against a `videos/<slug>-<date>/` folder.
---

# create-srt-and-translate

Generate a video's English captions.srt and the full set of YouTube
multi-language subtitle + thumbnail-title localizations from one invocation.

## When to invoke

After:
- The voiceover step (`voiceover-elevenlabs-v2` or v3) has produced
  `transcript.json` at the video folder root.
- (Optional) The thumbnail-creator skill has produced at least one
  `thumbnails/<round>/contact-sheet.html`.

The skill is safe to re-run — it overwrites the same output paths. Each
language file is independent, so partial re-runs are fine.

## What it produces

```
videos/<slug>-<date>/
├── captions.srt                          ← English source SRT
└── multi-lingual/
    ├── srt/
    │   ├── ar.srt   de.srt   es.srt   fr.srt   hi.srt
    │   ├── id.srt   it.srt   ja.srt   pl.srt   pt.srt
    │   └── ru.srt   tr.srt   vi.srt
    └── thumbnail-title/
        ├── ar.txt   de.txt   es.txt   fr.txt   hi.txt
        ├── id.txt   it.txt   ja.txt   pl.txt   pt.txt
        └── ru.txt   tr.txt   vi.txt
```

Each `<lang>.srt` mirrors the English `captions.srt` block-for-block with
identical timestamps. Each `<lang>.txt` contains the translated overlay
text and YouTube title for every thumbnail variant across every round.

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

Verify these exist before starting:

- `<video-folder>/transcript.json` — required
- `<video-folder>/thumbnails/<round>/contact-sheet.html` — optional;
  skip the thumbnail-title step if no contact sheets are found.

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

### Step 4 — Extract thumbnail variant titles

Only if `<video-folder>/thumbnails/` exists. Run:

```bash
python3 .claude/skills/create-srt-and-translate/scripts/extract_titles.py \
  <video-folder> --pretty
```

The script walks every round subdirectory (including any `-vertical`
variants), parses the contact-sheet.html, and prints JSON of the form:

```json
[
  {
    "round": "round-1",
    "path": "thumbnails/round-1/contact-sheet.html",
    "variants": [
      {"letter": "A", "overlay": "THE TEST WASN'T CLICKING THE CHECKBOX",
       "yt_title": "How a CAPTCHA decides you're human before you click"},
      {"letter": "B", "overlay": "…", "yt_title": "…"},
      {"letter": "C", "overlay": "…", "yt_title": "…"}
    ]
  },
  {
    "round": "round-1-vertical",
    "variants": [ … ]
  },
  { "round": "round-2", "variants": [ … ] }
]
```

Capture this JSON in memory — it's the source for the next step.

### Step 5 — Translate the titles into 13 languages

Create `<video-folder>/multi-lingual/thumbnail-title/` if it doesn't exist.
For each of the 13 language codes, write `<lang>.txt` with this layout:

```
# <Language name> thumbnail titles
# Source: <video-folder>/thumbnails/

=== round-1 ===
[A] OVERLAY:  <translated overlay text>
    YT TITLE: <translated YouTube title>
[B] OVERLAY:  <translated overlay text>
    YT TITLE: <translated YouTube title>
[C] OVERLAY:  <translated overlay text>
    YT TITLE: <translated YouTube title>

=== round-1-vertical ===
[A] OVERLAY:  …
    YT TITLE: …
…
```

Sections are in the same order the JSON returned (sorted by round directory
name). Translate every variant of every round — vertical rounds count.

Style guidance for titles is in `references/translation-style.md` —
particularly the sections on **thumbnail overlay text** (visual fit, casing
for non-Latin scripts) and **YouTube title** (lead with keyword, keep
under ~60 chars).

### Step 6 — Report

Summarize for the user:

- The number of SRT blocks per language (should all match captions.srt).
- The number of thumbnail rounds × variants translated per language.
- A reminder of the Studio upload path:
  `Studio → Subtitles → Add language → Upload file → With timing`
  and that the translated thumbnail-title text is plain copy-paste material
  for the Studio "translated titles & descriptions" pane plus for any
  re-rendered localized thumbnail images.

## Things this skill does NOT do (yet)

- **Does not re-render localized thumbnail images.** The `<lang>.txt`
  files contain the translated TEXT; using that text to render the actual
  localized thumbnail PNG/JPG is a separate step that goes through the
  thumbnail-creator pipeline with text overrides. Flag this to the user
  on completion if they want full image localization.
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
- `scripts/extract_titles.py` — contact-sheet.html → variant titles JSON.
- `references/translation-style.md` — terminology, numbers, scripts, register.
- `references/srt-chunking-rules.md` — block-size heuristic parameters.
