---
name: create-srt-and-translate
description: Generate a video's English captions.srt from its Scribe v2 transcript — and, only when explicitly asked, translate it into the 13 languages YouTube auto-dubs (Arabic, German, Spanish, French, Hindi, Indonesian, Italian, Japanese, Polish, Portuguese, Russian, Turkish, Vietnamese). By DEFAULT this skill produces the English captions and STOPS. Use it for "create the SRT", "generate captions for this video", "make the captions" (English only); generate the 13 translations only on an explicit localization request — "translate the captions", "translate to all languages", "do the localization", "dub it", "make the multilingual subtitles", "prep for multi-language upload". Always run from inside or against a `videos/<slug>-<date>/` folder.
---

# create-srt-and-translate

Generate a video's English captions.srt — and, on explicit request, the full
set of YouTube multi-language subtitle localizations.

**The default is English-only.** The skill produces `captions.srt` and stops.
The 13-language translation is a separate, on-demand phase (progressive
discovery — see Step 2.5 and Step 3). Do not generate the translations unless
the invoking request explicitly asks to translate / localize / dub.

Thumbnail-title localization is intentionally out of scope. Thumbnails ship
in English; if titles ever need to be localized, that's a separate manual
pass through the thumbnail-and-title-generator pipeline.

## When to invoke

After the voiceover step (`voiceover-elevenlabs-v2` or v3) has produced
`transcript.json` at the video folder root.

**Two phases, gated (progressive discovery).** Phase 1 (default) = English
`captions.srt`, then STOP. Phase 2 (on-demand) = the 13-language translation,
run *only* when the user explicitly asks to translate / localize / dub. A plain
"create the SRT" / "make the captions" is Phase 1 only — do not roll into
translations. English alone already unlocks YouTube's own auto-translation and
auto-dub, so it's the right default for most videos.

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

### Step 2.5 — Default stop: English only unless translation was asked for

**This is the default endpoint.** Unless the invoking request explicitly asked
to translate / localize / dub (the trigger list in Step 3), STOP here:

- Skip to Step 4 and report the English `captions.srt` as done.
- Offer the translations as a follow-up, don't perform them: *"English
  `captions.srt` is ready. Want the 13 YouTube auto-dub languages too? Say
  'translate the captions' and I'll run the localization pass."*
- Do **not** create `multi-lingual/srt/` or write any translated file.

Progressive discovery: the 13-language phase below exists, but it is opt-in.
Most videos only need the English SRT; a full hand-translated set is a
deliberate, heavier ask the user makes explicitly.

### Step 3 — Translate the SRT into 13 languages (on-demand only)

**Gate — run this step only on an explicit translation request.** Triggers:
"translate", "translate the captions", "translate to all languages", "do the
localization", "localize", "dub it", "make the multilingual subtitles", "prep
for multi-language upload". If the request was a plain "create the SRT" /
"make the captions", you already stopped at Step 2.5 — do not run this step.

When triggered: first verify `<video-folder>/captions.srt` exists (if not, run
Step 2 once to produce it — do **not** re-run the chunker if it already
exists). Then read `captions.srt` and write one translated file per language
code into `<video-folder>/multi-lingual/srt/`. Each translated file:

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

Summarize for the user. **English-only run (the default):**

- `captions.srt` block count, and that it's ready to upload.
- The Studio upload path: `Studio → Subtitles → Add language → English → Upload file → With timing`.
- The follow-up offer from Step 2.5 (translations available on request).

**After a translation run:**

- The number of SRT blocks per language (should all match captions.srt).
- A reminder of the Studio upload path:
  `Studio → Subtitles → Add language → Upload file → With timing`.

## Things this skill does NOT do

- **Does not translate thumbnail titles.** Thumbnails ship in English. If
  the user wants localized thumbnail text, that is a separate manual pass
  through the thumbnail-and-title-generator pipeline with explicit text overrides.
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
