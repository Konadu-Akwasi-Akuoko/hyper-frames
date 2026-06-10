# pacingInspo — how to read and how to add

## What this is

Per-video pacing studies (scene-change timeline × narration alignment) for
authoring our own videos. Sibling of `motionGraphicsInspo/` with a different
unit: motionGraphicsInspo catalogs single *beats* (one motion, one strip);
pacingInspo catalogs whole *videos* (cut cadence, hold lengths, how cuts ride
the narration). Do not merge the two — their index contracts differ.

## Reading rules

- Start with the `## Quick index` table in `README.md` — it is the cheap,
  few-hundred-token surface. Drill into one entry block, then (only if needed)
  the per-video `<slug>-pacing.md` report for the scene-by-scene table.
- NEVER load a `<slug>-pace.json` manifest whole into context — it carries
  per-scene transcript text. Filter it with `python3 -c` / `jq` slices.
- Contact-sheet tiles are row-major, 10 per row, in scene order, no labels;
  scene N = tile N of the sheet sequence.
- The `Stats:` line in each entry is a mechanical copy of the manifest's
  `aggregates` under exact field names — never re-derive or rename. The
  `Pacing:` and `Use when:` lines are human/Claude judgment.
- Numbers are approximate by construction: ASR word onsets (±0.1–0.2s), no
  diarization (embedded-clip speech counts toward wps), heuristic
  soft-transition detection. Treat them as comparative signals, not gospel.

## Adding an entry

Note: the default entry path is `motion-inspo-add`'s **combined ingest** (a
bare whole-video URL feeds BOTH libraries from one download — pace runs first,
then `scan --from-proxy` reuses its proxy). The steps below are the
pacing-side mechanics either way.

1. Run the tool (it emits candidates into `scratch/pacing/<slug>/`, never here):
   `uv run --project tools/inspo-ingest inspo-ingest pace "<url>" --slug <slug>`
2. QA the contact sheet before trusting the numbers: adjacent near-identical
   tiles = over-detection (raise `--soft-wide-min`, or `--hard-floor` toward
   0.12); an implausibly long scene = under-detection (lower them). Re-runs
   reuse the cached proxy and are fast.
3. Promote exactly three artifact kinds: `<slug>-pace.json`,
   `<slug>-pacing.md`, `<slug>-scenes-sheet-*.png`. Proxy, thumbs dir, json3,
   and info.json stay in scratch (throwaway).
4. Add BOTH a Quick-index row and an Entries block (one slug, linked anchor),
   author the `Pacing:` note (2–4 sentences) from the report + sheet — real
   numbers, never imagination — and a `Use when:` line tying it to our
   authoring decisions.
5. `git diff --stat` — only `pacingInspo/` (and nothing else) should change.

## Consumers

All three consumers are now wired — the library grew to **17 register-diverse
entries on 2026-06-10**, clearing the "~10+ entries, ≥3 registers" threshold the
wiring waited on (`TODO.md` items 1 & 2):

- **`docs/creator-patterns.md` §3.8** is the cross-video distillation: four
  per-register bands (chaptered explainer / brisk sectioned talking-head / fast
  essay-listicle / vertical Short) computed mechanically from every entry's
  `aggregates`, plus two findings that hold across all 17 (cuts ride the breath,
  not the pause — `pct_cuts_in_pause`≈0 everywhere; a faster register is *less*
  sentence-aligned, not faster-spoken). This is the cheap first stop.
- **`script-writer`** (Step 4 retention-discipline + external-references note)
  reads §3.8 first to place the script's register and its hold ceiling, drilling
  into the one matching entry block here only for a specific video's texture —
  evidence, never a target to match.
- **`video-director`** (Step B, first chunk of a *new video* only) reads the
  Quick index + the one register-matched entry directly, letting `median scene`
  + `longest_hold_s` calibrate how many sentences a chunk can carry before it
  drags — once per video, never per chunk.

When you add entries the §3.8 bands go stale: recompute them from the full set
of `*-pace.json` `aggregates` (the grouped-by-register dump method is in
`TODO.md` item 2), don't hand-patch. Activation history + the exact procedure
remain in the repo-root `TODO.md`.
