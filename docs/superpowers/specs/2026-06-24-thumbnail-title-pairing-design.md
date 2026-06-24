# Thumbnail↔title pairing in the inspo library

**Date:** 2026-06-24
**Status:** Approved (brainstorm), pending implementation plan

## Problem

The `thumbnail-and-title-generator` skill was deliberately named as a single
unit because a thumbnail and its title come hand-in-hand — they complement each
other and do different jobs (`title-engine.md`'s claim/ground asymmetry). But the
library currently treats them asymmetrically: every `thumbnailInspo/` reference is
catalogued for its **layout** only. The real YouTube title that ran with each
proven thumbnail is discarded — even though it is already sitting in every
`thumbnailInspo/<channel>/_manifest.json` (the `title` field next to each item).

The skill already replicates a reference's layout **skeleton** and swaps the
**flesh** (our headline, face, colors). It does not yet do the symmetric thing for
titles: learn the **title shape** that paired with that layout and replicate the
shape (not the words). Closing that gap makes the skill consistent with its own
core philosophy and strengthens the title craft by grounding the claim/ground
asymmetry in real, proven pairs — per archetype.

## Goals

1. Capture each reference's real title in the catalog (mechanical join from the
   manifests — zero re-scraping, no bot-wall risk).
2. Classify each title into a two-field vocabulary: a surface formula
   (`title_shape`) and the title-engine pattern it rides (`title_pattern`).
3. Teach the skill to use a chosen reference's title shape as a **strong prior**
   for the paired title it writes — engine + SEO can override.
4. Wire the forward path so future harvests carry the title and the cataloging
   pass classifies the shapes.

## Non-goals

- The per-thumbnail title does **not** become a competing title source. The
  dedicated corpus (`research/thumbnail-title-corpus-*/ANALYSIS.md`) stays the
  engine for what makes titles win/lose (it has winners-vs-losers analysis a
  single attached title cannot). The catalogued title is a worked **pairing
  example** and a shape prior, not raw input to copy.
- No verbatim title reuse, ever. We replicate the title *shape*, swap the words —
  the same rule that governs layout pixels.
- No changes to thumbnail rendering, the Specimen signature, or the harvest CDN
  path.

## Schema — three new fields per catalog entry

```jsonc
{
  "slug": "fireship-c-100-seconds-blue-letter",
  // ... existing fields unchanged ...
  "title": "C in 100 Seconds",          // verbatim from _manifest.json item.title
  "title_shape": "speed-primer",         // surface formula (the concrete tell)
  "title_pattern": "concrete-noun+verb"  // one of the 5 title-engine.md patterns
}
```

- `title` — deterministic join from `_manifest.json`, matched by `file` (or the
  video `id` embedded in `file`). No judgment.
- `title_shape` — surface formula, from the fixed 14-value enum below.
- `title_pattern` — one of the fixed 5 patterns from `title-engine.md`
  (`concrete-noun+verb`, `curiosity-gap→reversal`, `what/why/how`,
  `assumption-flip`, `identity-hook`).

## The `title_shape` vocabulary (fixed enum)

Derived by clustering the ~389 real reference titles. Two shapes carry explicit
corpus caveats and must be surfaced with them.

| `title_shape` | corpus examples | `title_pattern` |
|---|---|---|
| `speed-primer` | "C in 100 Seconds", "Learn JS in 5 MINUTES" | concrete-noun+verb |
| `x-explained` | "OAuth 2 Explained", "WebAssembly Explained" | concrete-noun+verb |
| `every-x-explained` | "Every Database Explained in 5 Minutes!" | concrete-noun+verb — **rigid completeness; wins ONLY on max-searched nouns** |
| `comparison-vs` | "Proxy vs Reverse Proxy", "Session Vs JWT" | concrete-noun+verb |
| `what-is-x` | "What is an API", "What Is REST API?" | what/why/how |
| `open-why-how` | "How Git Works", "Why is Everyone Using Vite?" | what/why/how |
| `listicle-n` | "10 Concepts EVERY Backend Dev…", "Top 5…" | concrete-noun+verb |
| `assumption-flip` | "Vibe coding is dead", "Frameworks don't matter anymore" | assumption-flip |
| `panic-threat` | "Native app dev is in big trouble…", "AI bubble is popping" | curiosity-gap→reversal |
| `curiosity-reversal` | "AI Was Supposed to Replace Devs… Until It Couldn't" | curiosity-gap→reversal |
| `scale-story` | "How Discord Stores TRILLIONS", "How Vercel Makes $200M" | concrete-noun+verb |
| `first-person-feat` | "I tried 10 code editors", "I Gave My Bot $10,000" | curiosity-gap→reversal |
| `identity-advice` | "CS students need to hear this", "think like a GENIUS programmer" | identity-hook |
| `meme-skit` | "If Programming Was An Anime", "if Apple made window blinds…" | identity-hook — **documented corpus floor; flag as weak for our lane** |

The enum is closed: classification is schema-validated so an agent cannot invent a
shape. A title that genuinely fits none maps to the nearest shape and the rationale
notes the imperfect fit.

## Author-time behavior — "suggest, engine decides"

When the skill picks a reference layout for a variant, it also reads that
reference's `title_shape` + `title_pattern`:

- **Default:** draft the paired title in the reference's shape, so the layout and
  the title shape move together as a proven pair.
- **Override:** `title-engine.md` rules and `seo/research.json` can redirect the
  shape — if a different top-3 noun or a saturation warning makes another shape
  win, the engine takes it. The pairing is a prior, not a mandate.
- **Caveat shapes:** `every-x-explained` and `meme-skit` surface with their corpus
  warnings so the skill never blindly inherits a weak shape.

This mirrors layout mimicry: the reference guides, the engine/signature govern.

## Workflow shape

Deterministic work stays out of agents; judgment fans out. ~54 catalog files,
~389 entries total.

- **Phase 0 — title backfill (deterministic):** join `title` verbatim from each
  `_manifest.json` into the matching catalog entries by `file`/`id`. Pure Python.
- **Phase 1 — classify (fan-out, ~one agent per catalog file, ~54 agents):** each
  agent reads its catalog file's entries (`title` + `archetype` + `reads_as` +
  `layout_map`) and returns, per entry, `{slug, title_shape, title_pattern,
  rationale}` against the fixed 14-shape enum (schema-validated).
- **Phase 2 — merge + critic:** write the classified fields back into the catalog
  JSONs; one critic agent samples for obvious misclassifications (e.g. a "vs" title
  not tagged `comparison-vs`, a "… Until It Couldn't" not tagged
  `curiosity-reversal`) and flags them for correction.
- **Phase 3 — regenerate + docs (parallel):** re-run `build_readme.py` to surface
  the new fields; in parallel update `title-engine.md`, `inspiration-mimicry.md`,
  and the catalog-growth path.

## Doc + code changes

- **`tools/thumbnail-inspo/` catalog schema** — document the 3 new fields and the
  14-shape enum reference list next to the cataloging instructions.
- **`fetch.py` / catalog flow** — carry `title` from manifest into catalog
  automatically on future harvests (forward path).
- **`build_readme.py`** — emit `title` + `title_shape` in the **Entries** blocks
  and add a `title_shape` column to the Quick index, labeled "original pair — shape
  to mimic, not copy."
- **`thumbnailInspo/CLAUDE.md`** — add the `title_shape`/`title_pattern`
  classification step to the cataloging contract (forward path).
- **`title-engine.md`** — add archetype→title-shape correlations + the
  "reference shape is a prior, engine decides" rule, with the non-verbatim
  guardrail.
- **`inspiration-mimicry.md`** — extend "copy the skeleton, swap the flesh" to
  titles: replicate the title *shape*, swap the words.

## Success criteria

- All 389 catalog entries carry `title`, `title_shape`, `title_pattern`.
- README Quick index + Entries blocks render the new fields with the
  "shape to mimic, not copy" labeling.
- `title-engine.md` and `inspiration-mimicry.md` describe the prior-not-mandate
  behavior and the non-verbatim guardrail.
- A future `fetch.py` harvest carries `title` into the catalog automatically, and
  `thumbnailInspo/CLAUDE.md` instructs the classification step for new entries.
- Spot-check: pick 5 entries across archetypes; each `title_shape` matches the
  title's actual surface formula and the `title_pattern` is consistent.
