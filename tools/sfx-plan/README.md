# sfx-plan

Scan a HyperFrames video folder for `data-sfx-*` annotations, resolve anchor
words via `narration-map.json`, pick files deterministically from
`sound-effects/sfx-catalog.yml`, and emit `compositions/sfx.html` as a native
HyperFrames audio sub-composition.

## Usage

From inside a video folder (after `video-director` Step H has annotated the HTML):

```bash
uv run --project ../../tools/sfx-plan sfx-plan
```

Flags: `--dry-run` (don't write), `--report` (print a plan table),
`--bake` / `--bake-format` (finalize — see below).

## Two output modes: per-cue (edit) vs. baked (finalize)

By default `sfx-plan` emits **one `<audio preload="none">` per cue** (162 for a
busy video). This is the **editing default**: a `data-sfx-*` tweak rewrites the
HTML attributes sub-second, the preview hot-reloads, and you hear it — the fast
loop a long second-by-second SFX session needs. Its one cost is a
`media_preload_none` lint warning per element (visible only at `npm run check`,
never during `npm run dev`); `preload="none"` is load-bearing, though — without
it the many `<audio>` elements exhaust Chrome's WebMediaPlayer budget and **freeze
preview Play** (scrubbing still works).

`--bake` is the **one-shot finalize**: it mixes every cue (delayed to its
`data-start`, scaled to the fixed **0.4** volume peg, equal-power panned) into a
single `audio/sfx-mix.mp3` (48 kHz stereo, 320 kbps) via ffmpeg, emits **one**
`<audio id="sfx-mix">` at `data-volume="1"` (the per-cue 0.4 peg is already baked
into the mix, so the layer mounts at unity), and writes `compositions/sfx.cues.json`
so per-cue tooling (`sfx-level --batch`) still recovers every cue's timing. The
result is a clean,
lint-silent, single-player artifact for the committed/published video. Requires
ffmpeg (so does `npm run render`). `--bake-format wav` emits PCM instead.

```bash
uv run --project ../../tools/sfx-plan sfx-plan . --bake   # run LAST, when SFX is locked
```

> **Footgun — bake LAST.** A plain `sfx-plan` run **regenerates the per-cue
> layer and reverts the bake** (back to the fast editing default). That's
> intentional: edit in per-cue mode, bake once when the SFX is locked, and don't
> run plain `sfx-plan` again afterward. The orphaned `sfx-mix.mp3` left behind by
> a revert is harmless — the next `--bake` overwrites it. Track the baked mp3 in
> git alongside `voiceover.mp3`.

## Annotation reference (`data-sfx-*`)

Authored on HTML elements inside `index.html` or any `compositions/*.html` (except
the generated `compositions/sfx.html`). `data-sfx-on-anchor` flags an element as
a cue; everything else is either a timing reference, an optional override, or a
breadcrumb.

| Attribute                  | Required | Description                                                                 |
| -------------------------- | -------- | --------------------------------------------------------------------------- |
| `data-sfx-on-anchor`       | yes      | Cue name from `sfx-catalog.yml` or `sfx-overrides.yml` (e.g. `pop`, `whoosh`). Picks the recipe (filter, defaults, track). |
| `data-sfx-anchor`          | (one of) | Spoken word from the narration to align on. Resolved via `narration-map.json`. Use for cues tied to speech. |
| `data-sfx-at-scene-ms`     | (one of) | Scene-local time in milliseconds, relative to the host composition's own `data-start`. Use for cues tied to visual motion. Mutually exclusive with `data-sfx-anchor`. |
| `data-sfx-anchor-index`    | no       | 1-indexed occurrence of the anchor word in the transcript (default `1`).    |
| `data-sfx-asset`           | no       | Path under `sound-effects/` to pin a specific file, bypassing the cue's filter+hash resolver. Must exist in the catalog. |
| `data-sfx-lead-ms`         | no       | Peak-tuning nudge. ±100 ms is normal. ≥200 ms on an anchor-mode cue triggers a warning — use `data-sfx-at-scene-ms` instead. |
| `data-sfx-volume`          | no       | **Ignored.** SFX volume is a fixed 0.4 hard peg (`PEG_VOLUME` in `plan.py`); this attribute no longer changes loudness. |
| `data-sfx-pan`             | no       | −1.0 (left) to 1.0 (right). Defaults to 0.                                  |
| `data-sfx-hook`            | no       | `"true"` marks the single hook moment. Phase A breadcrumb only.             |

Exactly one of `data-sfx-anchor` / `data-sfx-at-scene-ms` must be set. Neither
or both raises at scan time.

### Pinning a specific asset

When a specific named file is non-negotiable (a brand sound, a referenced
moment), pin it on the element:

```html
<div data-sfx-on-anchor="pop"
     data-sfx-asset="Mister Horse Free SFX/Pop/Hollow Pop 06.wav"
     data-sfx-at-scene-ms="7575">…</div>
```

The cue still supplies the track index, and the volume is the fixed 0.4 peg —
pinning only short-circuits the asset picker. Do not add a one-off cue to the
global catalog just to force a file; that's catalog pollution.

## Per-video cue overrides (`sfx-overrides.yml`)

Drop an `sfx-overrides.yml` at the video folder root to customize cue recipes
for one video without touching the shared catalog. Loaded automatically.

```yaml
cues:
  # Override an existing cue's pool for this video.
  ui-tick:
    filter:
      brightness_in: ["bright"]

  # Register a brand-new cue available only inside this video.
  panel-clang-05:
    default_lead_ms: -50
    filter:
      path: Mister Horse Free SFX/Clang/Synthetic Clang 05.wav
```

Per-cue semantics: `filter` is replaced wholesale (not deep-merged); other
fields are shallow-replaced. New cues must include a non-empty `filter`. A
`default_volume` in an override is accepted but **ignored** — SFX volume is the
fixed 0.4 hard peg.

## Source contract

See `docs/superpowers/specs/2026-05-11-sfx-pipeline-design.md`.
