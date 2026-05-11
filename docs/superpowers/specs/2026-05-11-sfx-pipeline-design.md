# Sound Design Pipeline — Phase A (SFX Placement)

**Status:** Design approved 2026-05-11
**Scope:** SFX placement layer only. Music bed, ambience, and mastering chain are explicit non-goals (deferred to Phase B/C).
**Drivers:** Make HyperFrames videos sound "big-budget production grade" by adding a curated, anchor-aligned SFX layer authored by a Claude skill, resolved by a deterministic tool, and rendered as a native HyperFrames sub-composition.

## Background

The pipeline today produces voiceover-only videos: VO is generated via ElevenLabs (v2 or v3), word-level timing lands in `transcript.json`, structural timing lands in `narration-map.json`, and compositions render against that timing. There is no music layer, no SFX layer, no mastering pass.

Research on big-budget YouTube video essays (Veritasium, Kurzgesagt, Vox, Wendover, Mark Rober, Mustard) established that the perceived quality gap between amateur and pro YouTube is dominated by sound design layers, not VO quality. The single biggest "feels expensive" multiplier is constant ambient bed + curated SFX on visual reveals + light music ducked under VO.

Phase A targets the SFX layer specifically — the highest ratio of impact-per-effort because:
- The repo already owns ~1178 sound effects across 4 libraries in `sound-effects/`.
- The repo already produces word-level timing (`transcript.json`) and structural timing (`narration-map.json`).
- HyperFrames already supports multi-track audio natively via `<audio data-start data-duration data-volume data-track-index>`.

The missing pieces are an editorial layer (what to score and when) and a mechanical layer (resolve named cues to files at exact timestamps).

## Goals

1. Per-video SFX layer that scores meaningful visual and narrative moments.
2. Author the SFX layer **after** the composition is visually done — SFX follows animation timing, not the other way around.
3. Editorial decisions (which moments deserve a hit, which cue character fits) made by a Claude skill that reads the script, narration map, design notes, and composition HTML.
4. Mechanical resolution (anchor → timestamp, cue name → file, peak alignment) done deterministically by a Python CLI.
5. Native HyperFrames playback — `npx hyperframes preview` and `render` must play SFX without a separate post-render step.
6. Reproducible: same inputs always produce the same `sfx.html`.

## Non-goals (deferred to later phases)

- Music bed selection and per-scene track swaps (Phase B).
- Constant ambient drone bed under the full video (Phase B).
- Sidechain ducking of music under VO (Phase B).
- Pre-impact silence at hook moments (Phase C — Phase A only leaves a `data-sfx-hook="true"` breadcrumb).
- Master loudness normalization to −14 LUFS / −1 dBTP (Phase C, post-render ffmpeg).
- VO mastering chain — HPF, de-ess, compression, small-room reverb send (Phase C).
- Stereo width and reverb sends on SFX (Phase C, if needed).

## Architecture

Phase A is three subsystems with distinct lifecycles:

```
A1.  tools/sfx-catalog/         (Python CLI)
     Repo-level. Runs rarely — only when sound-effects/ changes.
     Output: sound-effects/sfx-catalog.yml  (committed to git)

A2.  .claude/skills/sfx-author/ (Claude skill)
     Per-video. The editorial brain — decides WHICH elements deserve
     SFX and which cue character. Reads HTML + narration-map + transcript
     + design.md + catalog. Writes data-sfx-* annotations into HTML.

A3.  tools/sfx-plan/            (Python CLI)
     Per-video. Deterministic resolver. Reads annotated HTML +
     narration-map + catalog. Picks files. Emits compositions/sfx.html.
```

### Data flow

```
ONCE per library state:
  sound-effects/  ──▶ A1 sfx-catalog ──▶ sfx-catalog.yml  (committed)

PER VIDEO, after composition is done and visually approved in preview:
  user invokes A2 sfx-author skill
       │
       ├──▶ reads HTML, narration-map, transcript, design.md, catalog
       ├──▶ proposes a cue plan: "13 cues — 3 whooshes, 7 ticks, 1 boom, 1 riser, 1 hook-tag"
       ├──▶ HUMAN REVIEW GATE: user approves / refines / aborts
       ├──▶ writes data-sfx-* attributes into HTML (Edit tool, surgical)
       ├──▶ runs A3 sfx-plan → generates compositions/sfx.html
       └──▶ launches npx hyperframes preview, surfaces studio URL

  user audits in preview, asks skill to refine specific cues, repeat.
```

### Ownership zones

- **Repo-level** (shared across all videos): `sound-effects/` library, `sound-effects/sfx-catalog.yml`.
- **Per-video** (lives in `videos/<slug>-<date>/`): annotated `index.html` + `compositions/*.html`, generated `compositions/sfx.html`, optional `sfx-overrides.yml` for tonal overrides.

## Component 1: `tools/sfx-catalog/`

Builds a rich per-asset metadata index from `sound-effects/`. Runs as a `uv`-managed Python CLI.

### Output: `sound-effects/sfx-catalog.yml`

Two top-level sections.

**`assets:`** — one entry per audio file in the library, keyed by repo-relative path under `sound-effects/`:

```yaml
version: 1
generated_at: 2026-05-11T10:30:00Z
library_sha: <sha256 of folder tree>
assets:
  "Mister Horse Free SFX/Click/click-bright-01.wav":
    library: "Mister Horse"
    category: "Click"
    duration_s: 0.412
    sample_rate: 48000
    channels: 2
    format: wav
    bit_depth: 24
    sha256: "ab12..."
    peak_dbfs: -1.2
    peak_time_s: 0.083
    integrated_lufs: -14.6
    rms_dbfs: -18.4
    onset_time_s: 0.041
    attack_time_s: 0.042
    tail_time_s: 0.288
    spectral_centroid_hz: 4820
    brightness: bright
    low_energy_pct: 8
    mid_energy_pct: 34
    high_energy_pct: 58
    tags: [click, ui, bright, short, snappy]
    auto_role: accent
```

Metadata groups:

- **Identification & shape**: `path`, `library`, `category`, `duration_s`, `sample_rate`, `channels`, `format`, `bit_depth`, `sha256`.
- **Loudness & timing** (the "informed picking" data): `peak_dbfs`, `peak_time_s`, `integrated_lufs`, `rms_dbfs`, `onset_time_s`, `attack_time_s`, `tail_time_s`.
- **Spectral character** (for tonal matching): `spectral_centroid_hz`, `brightness` (enum: `dark` <1kHz, `warm` 1–3kHz, `bright` 3–6kHz, `airy` >6kHz), `low_energy_pct`, `mid_energy_pct`, `high_energy_pct`.
- **Authoring hints** (auto-derived from above): `tags`, `auto_role` (enum: `transition`, `accent`, `impact`, `riser`, `ambience`, `foley`).

`peak_time_s` is the single most important field — Component 3 uses it for peak-aligned timing.

**`cues:`** — named cue recipes that map logical names (`ui-tick`, `whoosh`, `boom`, `riser`, `pop`) to filter expressions over `assets:`:

```yaml
cues:
  ui-tick:
    filter:
      auto_role: accent
      duration_s_max: 0.5
      brightness_in: [bright, airy]
    default_lead_ms: -50
    default_volume: 0.8

  whoosh:
    filter:
      auto_role: transition
      duration_s_min: 0.4
      duration_s_max: 1.5
      attack_time_s_min: 0.1
    default_lead_ms: -150
    default_volume: 0.9

  boom:
    filter:
      auto_role: impact
      low_energy_pct_min: 50
      peak_time_s_max: 0.2
    default_lead_ms: 0
    default_volume: 1.0

  riser:
    filter:
      auto_role: riser
      duration_s_min: 1.5
    default_lead_ms: null  # = -(asset.duration_s)
    default_volume: 0.85

  pop:
    filter:
      auto_role: accent
      duration_s_max: 0.3
      brightness_in: [warm, bright]
    default_lead_ms: -50
    default_volume: 0.8
```

### Build behavior

- Incremental: skips files whose `sha256` matches the previous run.
- Initial build of the current ~1178-file library: estimated 5–10 minutes.
- Subsequent runs (no library change): near-instant (only YAML re-serialization).
- Catalog file is committed to git so every clone is immediately usable.

### Dependencies (Python, `uv`-managed)

- `soundfile` — IO, sample rate, channels, bit depth.
- `numpy` — peak, RMS, onset detection.
- `pyloudnorm` — integrated LUFS measurement.
- `librosa` — spectral centroid, band energy.
- `PyYAML` — output serialization.

### CLI

```bash
# From repo root:
uv run --project tools/sfx-catalog sfx-catalog

# Flags:
#   --force      ignore sha256 cache; rebuild every asset
#   --dry-run    measure but don't write YAML
#   --report     print catalog stats (asset counts per role/brightness/library)
```

## Component 2: `.claude/skills/sfx-author/`

The editorial brain. Reads inputs, reasons about the video, proposes a cue plan, writes annotations on approval, runs Component 3, launches preview.

### Inputs

- `index.html` and every `compositions/*.html` in the video folder
- `transcript.json` (word-level timing + spoken text)
- `narration-map.json` (anchors, pauses, scene boundaries, emphatic words)
- `design.md` (tone signals)
- `sound-effects/sfx-catalog.yml` (available cues + asset metadata)
- (optional) `sfx-overrides.yml` in the video folder (per-video cue recipe overrides)

### The annotation contract — `data-sfx-*` attributes

The complete attribute surface the skill writes (and Component 3 reads):

| Attribute | Required | Meaning |
|---|---|---|
| `data-sfx-anchor` | yes | Anchor word or phrase from the transcript (must resolve via narration-map) |
| `data-sfx-on-anchor` | yes | Named cue from `sfx-catalog.yml` |
| `data-sfx-anchor-index` | no, default `1` | Which occurrence if the anchor appears multiple times (1-indexed) |
| `data-sfx-lead-ms` | no, default per cue | Negative = land earlier than anchor (sound leads picture) |
| `data-sfx-volume` | no, default per cue | Per-cue gain override (0..1) |
| `data-sfx-pan` | no, default `0` | Stereo pan (−1..1) |
| `data-sfx-hook` | no | `"true"` marks the one editorial hook moment per video (Phase C uses this; Phase A only places the breadcrumb) |

### The playbook (principles, not rules)

The skill operates from a deliberately light scaffold: principles + technical floors + a cue character library + worked examples. It does **not** consult a rigid trigger-to-cue mapping table. This is the lesson encoded in `learnings/composition-spec-over-restriction.md` applied to sound design.

**Placement principles** (the skill's editorial north star):

Score moments that *earn* a hit — the spoken payoff, the visual punchline, the threshold cross between scenes, the reveal of the line that the line is about. Skip texture (typewriter chatter, decorative drift, ambient pulses) — they belong to atmosphere, not punctuation. Lead sound ahead of picture. Match cue character to what the moment is *doing*, not to what CSS class the element wears. When in doubt, score less — silence is a tool, and an unused cue is cheaper than a wrong one. Read the script first; only then look at the HTML.

**Technical floors** (mix-craft physics, not aesthetic choices):

- **Peak alignment**: a cue's peak (catalog `peak_time_s`) lands on the anchor's `start`, not the cue's start.
- **Default lead**: −50ms for ticks, −150ms for whooshes, 0 for booms, −(duration) for risers. Override per element via `data-sfx-lead-ms`.
- **Cooldown** (prevents ear fatigue): ≥ 2s between same-cue ticks; ≥ 4s between whooshes; ≥ 30s between booms.
- **Density ceiling** (protects VO intelligibility): ≤ 1 cue per 3s rolling average. At > 1 cue / 1.5s, the tool hard-fails.

**Cue character library** (intent, not mapping):

| Cue | Character | Best when the moment is… |
|---|---|---|
| `whoosh` | spatial motion | crossing a threshold, entering/exiting a frame, scene transitions |
| `ui-tick` | discrete arrival | a thing snapping into place, a label landing, a small reveal |
| `pop` | playful arrival | softer than tick, for lighter or rhythmic reveals |
| `boom` | weight / finality | scale, gravitas, the line that lands |
| `riser` | build-to-payoff | tension into a reveal, the climb before the hit |
| (no cue) | negative space | the punchline is *the silence*; or the texture is texture |

**Worked examples** (the skill learns taste by demonstration, not by flowchart):

> **Scene 1 "mathematical NIGHTMARE" reveal** (from `videos/why-text-is-hard-2026-05-07/`). Scored `ui-tick` on the word "NIGHTMARE." The element is `#s1-nightmare` and the line is "a mathematical nightmare." The visual punctuation lines up with the word's emphasis. Did *not* score the typewriter on `#s1-typed` — the keystrokes are texture under the line, and ticking each character would crowd the line that's actually the moment.

> **Scene 2→3 boundary at "control point"**. Scored `whoosh` keyed to "control" — the first emphatic word of scene 3 — with lead −150ms so the whoosh peaks on the syllable. Did *not* place a whoosh on every Bézier control-point marker that appears during the scene; they're a swarm reveal, not threshold crosses, and clicking each one would turn the scene into a UI bleep festival.

### The proposal format (review checkpoint)

Before writing any annotation, the skill prints a plan and waits for explicit approval:

```
SFX CUE PLAN — how-does-captchas-work-2026-05-10
Runtime 4:12 · 4 scenes detected
Read design.md as: editorial / restrained (informs cue character choice;
no mechanical keyword-to-caps mapping — see Playbook)

Scene 1 (00:00–01:08) "Hook"
  ✗ skip   typewriter on #s1-typed             (texture, not punctuation)
  ✓ 00:08.4  anchor="nightmare"    ui-tick   on #s1-nightmare
  ✓ 01:04.7  anchor="easy"         whoosh    on scene-2 boundary

Scene 2 (01:08–02:10) "Easy vs hard"
  ✓ 01:10.2  anchor="easy"         ui-tick   on #s2-easy-tag
  ✓ 01:11.8  anchor="hard"         ui-tick   on #s2-hard-tag
  ✗ skip   12 control-point markers           (swarm reveal, would crowd "Bézier")
  ✓ 01:34.6  anchor="Bézier"       ui-tick   on #s2-glyph reveal
  ✓ 02:08.3  anchor="control"      whoosh    on scene-3 boundary

[…]

TOTAL: 13 cues  (3 whoosh · 7 ui-tick · 1 boom · 1 riser · 1 hook-tag)
DENSITY: 1 cue / 19.4s avg
NOTES:
  • Hook moment marked at 03:41 ("never seen") — Phase C silence treatment

Approve to write annotations into HTML?  [yes / refine / abort]
```

On `refine`: the user can request edits in natural language ("drop the boom in scene 3", "the hook is 02:48 not 03:41", "score the Bézier control points after all — make them quieter"). The skill adjusts and re-prints the plan. Loop until `yes`.

On `yes`: the skill writes `data-sfx-*` attributes into the named elements using the Edit tool (surgical changes, one element at a time), runs Component 3, and launches `npx hyperframes preview`.

On `abort`: nothing is written; skill exits cleanly.

### The refine loop after preview

After audit, the user can ask the skill to adjust specific cues:

- "The whoosh into scene 3 lands late" → skill adjusts `data-sfx-lead-ms` on that element.
- "Scene 2 feels too busy" → skill drops the lowest-priority tick in scene 2.

Each refine re-runs Component 3 and reloads preview.

### The skill's checklist (TodoWrite tasks on invoke)

1. Load all inputs; verify catalog version matches.
2. Walk HTML, identify candidate elements (by class/id/role + animation evidence).
3. Apply placement principles to each candidate; pick cue character from the library.
4. Apply technical floors (cooldown, density ceiling).
5. Produce review report.
6. **Wait for user approval** (HARD GATE).
7. Write `data-sfx-*` attributes into HTML.
8. Run Component 3 (`tools/sfx-plan`).
9. Launch `npx hyperframes preview`, surface studio URL.
10. Wait for audit feedback; loop to step 7 on refines.

## Component 3: `tools/sfx-plan/`

Deterministic placement. No editorial decisions. Resolves annotations to a timed audio layer.

### Inputs

- All HTML files in the video folder (scanned for `data-sfx-*` attributes)
- `narration-map.json` (anchor → timestamp lookup)
- `sound-effects/sfx-catalog.yml` (cue definitions + asset metadata)
- (optional) `sfx-overrides.yml` in the video folder (override `cues:` recipes for this video)

### Algorithm

1. **Scan HTML.** Walk all composition files, collect every element with `data-sfx-anchor` + `data-sfx-on-anchor`. Capture: anchor text, anchor index, cue name, lead-ms override, volume override, pan override, source file + line.
2. **Resolve anchor → timestamp.** Look up the anchor text in `narration-map.json`'s `anchors`. Use `anchor_index` (1-indexed) to pick the occurrence. The matched anchor's `start` becomes `t_anchor`.
3. **Resolve cue → file.** Look up the cue name in `sfx-catalog.yml`'s `cues:` section. Apply the filter against `assets:`. From the filtered candidates, pick one deterministically: `index = hash(anchor_text + str(anchor_index) + cue_name) % len(candidates)`. Same inputs always produce the same file.
4. **Compute scheduled `data-start`.** Goal: cue's peak lands on `t_anchor + lead_ms`. So:
   ```
   data-start = t_anchor + (lead_ms / 1000) − asset.peak_time_s
   ```
   If `data-start < 0`, clamp to 0 and emit a warning.
5. **Emit `compositions/sfx.html`.** One `<audio>` tag per resolved cue, sorted by `data-start`. Each tag carries `data-start`, `data-duration` (= `asset.duration_s`), `data-volume`, `data-track-index` (one track per cue type so HF can stack), `src` (repo-relative path). A comment above each tag pins the source location.

### Generated `compositions/sfx.html` shape

```html
<!--
  GENERATED by tools/sfx-plan — do not edit by hand.
  Source: sfx-plan v1, run at 2026-05-11T14:22:09Z
  Cues: 13   Duration: 4:12   Catalog: sfx-catalog.yml@<sha>
-->
<html data-composition-id="sfx-layer" data-start="0" data-duration="252">
<body>
  <!-- from index.html:127  anchor="nightmare" idx=1  cue=ui-tick  lead=-50ms -->
  <audio data-start="8.358" data-duration="0.412" data-volume="0.8"
         data-track-index="20"
         src="../../../sound-effects/Mister Horse Free SFX/Click/click-bright-04.wav"></audio>

  <!-- from index.html:154  anchor="easy" idx=1  cue=whoosh  lead=-150ms -->
  <audio data-start="64.572" data-duration="0.821" data-volume="0.9"
         data-track-index="21"
         src="../../../sound-effects/Whooshes/whoosh-mid-02.wav"></audio>
</body>
</html>
```

### One-time `index.html` wiring

The skill adds this once on first invocation; idempotent thereafter:

```html
<!-- sfx-layer: generated by tools/sfx-plan, do not edit -->
<div data-composition-src="compositions/sfx.html"
     data-composition-id="sfx-layer"></div>
```

### CLI

```bash
# From inside the video folder:
uv run --project ../../tools/sfx-plan sfx-plan

# Flags:
#   --dry-run    report cues, don't write sfx.html
#   --report     print a human-readable plan table
#   --watch      re-run on HTML changes (for the iteration loop)
```

### Determinism contract

Given the same annotated HTML + same `narration-map.json` + same `sfx-catalog.yml`, `tools/sfx-plan` produces byte-identical `sfx.html`. The seed for asset picking is `hash(anchor_text + str(anchor_index) + cue_name)`, not a random source. Re-runs in CI, fresh clones, and human re-renders all produce the same result.

### Boundaries (what `tools/sfx-plan` does NOT decide)

- *Which* elements deserve cues (skill)
- *Which* cue type is right (skill)
- *Which* anchor word to pick (skill)
- *How much* density is too much (skill)

The tool only resolves what the skill wrote.

## Pipeline integration

### Per-video lifecycle (updated)

```
1.  Slug + date → create videos/<slug>-<YYYY-MM-DD>/
2.  npx hyperframes init
3.  Drop voiceover.mp3 in audio/ and transcript.json at folder root
4.  Run tools/narration-map (anchors + pauses + scene boundaries)
5.  YouTube SEO research (optional, parallel)
6.  Author compositions; iterate via lint → inspect → preview
7.  ─── composition is done; visuals approved in preview ───
8.  [NEW] Invoke .claude/skills/sfx-author/
       • proposes plan → user approves
       • writes data-sfx-* into HTML
       • runs tools/sfx-plan → compositions/sfx.html
       • mounts sfx-layer in index.html (first run only)
       • launches hyperframes preview, surfaces URL
9.  [NEW] Audit by ear; refine specific cues; loop step 8 as needed
10. npx hyperframes render
```

### Repo-level setup (once)

```
0a. Build the catalog initially:
    uv run --project tools/sfx-catalog sfx-catalog
    → writes sound-effects/sfx-catalog.yml
    → commit to git

0b. Re-run when sound-effects/ grows or shrinks:
    Same command; incremental (sha256-keyed); commit the updated YAML.
```

### Interaction with existing HyperFrames commands

- `npx hyperframes lint` — `compositions/sfx.html` is a regular composition block; lint applies normally. If lint flags it, that's a tool bug, not authoring.
- `npx hyperframes inspect` — the sfx-layer surfaces as a sub-composition with its own timeline samples; overlap warnings between SFX and other layers appear here.
- `npx hyperframes preview` — plays VO + SFX as native HF audio tracks. The iteration loop.
- `npx hyperframes render` — produces the final video with SFX baked into the audio track. No separate render step.

### Re-running concerns

- **VO re-recorded** → `transcript.json` regenerates → `narration-map.json` re-runs → anchor timestamps shift → re-run `tools/sfx-plan` (skill triggers automatically). Annotations themselves don't need to change unless anchor words got cut from the script.
- **Animation retimed** → if the SFX still wants to land on the same spoken word, no change needed (anchor-driven). If the SFX wanted to land on the visual moment and the visual moved relative to the word, the author tweaks `data-sfx-lead-ms` on that element (or re-invokes the skill for that scene).
- **Catalog refreshed (new SFX added)** → `tools/sfx-plan` re-runs and may pick different files for newly-added annotations. Existing picks remain stable unless the previously-chosen file was removed.

### Commit boundaries

- `feat(sfx): add sound-effects catalog v1` — initial 0a commit, includes `sfx-catalog.yml`
- `feat(sfx): add sfx-author skill + sfx-plan tool` — A2/A3 landing
- Per-video: `feat(<slug>): sound design pass` — annotated HTML + generated `compositions/sfx.html`
- Catalog refreshes: `chore(sfx): rebuild catalog for <new pack>`

### Project CLAUDE.md update

A new section titled **Sound design** lands between "Transcript-as-timing-truth" and "Lint / inspect / preview before declaring done", covering:

- Sound design is the last authoring pass, not the first.
- Invoke the `sfx-author` skill once visuals are approved in preview.
- Catalog lives at `sound-effects/sfx-catalog.yml`; rebuild only when the library changes.
- Treat the skill's plan as a proposal — refine before approval, not after the fact.

## Error handling & validation

### Failure modes `tools/sfx-plan` must surface (not swallow)

| Failure | Behavior |
|---|---|
| `data-sfx-anchor` not found in narration-map | Hard fail. `unresolved anchor "Bézier" at index.html:127 — not present in narration-map. Did the script change?` Exit non-zero. |
| `data-sfx-anchor-index="3"` but anchor only occurs twice | Hard fail. `anchor "easy" requested index 3, only 2 occurrences in narration-map.` |
| `data-sfx-on-anchor="unknown"` references unknown cue | Hard fail. List known cues from `sfx-catalog.yml` in the error. |
| Cue's filter matches zero assets in catalog | Hard fail. `cue "boom" filter matched 0 assets — relax the recipe or add files.` |
| Previously-picked file deleted from library | Warn + reseed. `previously picked "bass-impact-04.wav" no longer in library — repicked "bass-impact-07.wav".` |
| Two cues overlap (same track, intersecting windows) | Warn. Doesn't block render — HF handles overlap. |
| Scheduled start < 0 after lead/peak alignment | Clamp to 0, warn. |
| `sound-effects/sfx-catalog.yml` missing | Hard fail with remediation command. |
| Catalog version mismatch (newer file than tool) | Hard fail. Forces upgrade rather than silent mis-parse. |

### Validation `tools/sfx-plan` always runs before emitting

1. Every annotation resolves to a real timestamp.
2. Every cue name resolves to at least one candidate asset.
3. Every picked file exists on disk.
4. No `data-start` < 0 after lead/peak alignment.
5. Per-track overlap check (warn only).
6. Total cue density ≤ technical ceiling (warn at > 1 cue / 3s rolling avg, hard fail at > 1 cue / 1.5s).

### Skill-level guards

- Skill re-reads `narration-map.json` after the plan is approved to confirm anchors still resolve.
- If any anchor in the plan doesn't resolve at write time, the skill aborts the write and re-proposes against the updated narration-map.

### Generated-file safety

`compositions/sfx.html` opens with a "GENERATED — do not edit" header. The skill never edits this file by hand; only `tools/sfx-plan` writes it. If a human edits it, the next tool run overwrites silently.

## Testing

### `tools/sfx-catalog`

- Unit: peak detection on a synthetic WAV with a known impulse at t=0.083s returns `peak_time_s = 0.083`.
- Unit: LUFS computation against an EBU R128 reference tone returns the expected integrated value (±0.1 LU).
- Unit: spectral centroid for a 1kHz sine ≈ 1000Hz; for a 4kHz sine ≈ 4000Hz.
- Integration: pointing the builder at a fixture folder with 3 files produces a YAML with all 3 assets and stable metadata across runs.
- Determinism: re-running over unchanged files is a no-op (sha256 short-circuit).

### `tools/sfx-plan`

- Unit: anchor resolution given a fixture `narration-map.json` (right occurrence picked from `anchor_index`).
- Unit: peak-aligned `data-start` math (anchor at 10.0s, lead −150ms, peak_time 0.08s → data-start = 9.77s).
- Unit: deterministic file picking — same `(anchor, index, cue)` always picks same file given same catalog.
- Unit: catalog mutation — adding new files leaves existing picks stable; deleting the picked file triggers reseed warning.
- Integration: fixture video folder (annotated HTML + narration-map + small catalog) produces a known-good `sfx.html`. Snapshot test.
- Failure surface: each row in the Failure modes table has a regression test asserting the exact error message.

### `.claude/skills/sfx-author/`

Skills can't be unit-tested, but the canonical video gets a fixture: an annotated copy of `videos/why-text-is-hard-2026-05-07/` with hand-curated `data-sfx-*` attributes matching the spirit of the worked examples in Component 2. This serves two purposes:

1. Smoke test for `tools/sfx-plan` — re-runs against the fixture must produce the same `sfx.html`.
2. Training data for the skill — when invoked, it reads this as a "this is what good annotation looks like" reference.

### Manual acceptance

Apply the full Phase A flow to `videos/how-does-captchas-work-2026-05-10/` (the current in-progress video).

**Verdict criterion**: does the captchas video feel *materially* more produced after the SFX pass? If yes, Phase A is validated. If no, re-examine the skill's playbook.
