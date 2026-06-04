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

Flags: `--dry-run` (don't write), `--report` (print a plan table).

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
| `data-sfx-volume`          | no       | 0.0–1.0 override of the cue's `default_volume`.                             |
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

The cue still supplies the default volume and track index — pinning only
short-circuits the asset picker. Do not add a one-off cue to the global catalog
just to force a file; that's catalog pollution.

## Per-video cue overrides (`sfx-overrides.yml`)

Drop an `sfx-overrides.yml` at the video folder root to customize cue recipes
for one video without touching the shared catalog. Loaded automatically.

```yaml
cues:
  # Override an existing cue's pool or defaults for this video.
  ui-tick:
    filter:
      brightness_in: ["bright"]
    default_volume: 0.7

  # Register a brand-new cue available only inside this video.
  panel-clang-05:
    default_lead_ms: -50
    default_volume: 0.8
    filter:
      path: Mister Horse Free SFX/Clang/Synthetic Clang 05.wav
```

Per-cue semantics: `filter` is replaced wholesale (not deep-merged); other
fields are shallow-replaced. New cues must include a non-empty `filter`.

## Source contract

See `docs/superpowers/specs/2026-05-11-sfx-pipeline-design.md`.
