---
name: design-catalog-add
description: Extract a CSS or motion effect from a video composition into the shared design-catalog/ at the repo root, generalize it for reuse, and regenerate the viewer index. Use when the user says "add this to the design catalog", "catalog this effect", "save this snippet for reuse", "extract this into the catalog", "make this reusable", or points at a snippet and asks for it to be cataloged. Also use when finishing a composition and wanting to harvest standout effects before moving on.
---

# design-catalog-add

Guided workflow to add a reusable effect to `design-catalog/` at the repo
root. The skill encodes the contract — you (Claude) walk the user through
each step, propose, wait for confirmation, then write.

## Hard rules

- **Never modify the source video.** Extraction is a copy. The source files
  under `videos/<slug>/` stay untouched.
- **Never write outside `design-catalog/<slug>/`.** Only the new entry folder
  and the regenerated `design-catalog/catalog.json` may be touched (the
  generator writes the latter — you don't hand-edit it).
- **Read the actual source lines before proposing anything.** The line ranges
  the user gives you are starting points; verify by reading.
- **Wait for confirmation at every checkpoint.** Don't chain steps.

## Workflow

### Step 1 — Locate source

Ask the user (or read from context) for:

- The source file path, e.g. `videos/<slug>/compositions/scene-XX.html`.
- The CSS line range (the rule block that defines the effect).
- The motion/JS line range (a single GSAP `.to(...)` call, a tween, an
  Anime.js block, etc.) — optional; static effects skip this.

Read those exact lines with the `Read` tool and quote them back to the user
so they can confirm you have the right snippet. If the user said "the
border beam in scene 7", grep first, narrow it down, then confirm.

### Step 2 — Propose meta

Draft `meta.json` and show it to the user before writing. Fields:

- **slug**: kebab-case, derived from the effect's name. Must match the
  destination folder name. Existing slugs are in `design-catalog/*/`; pick a
  fresh one.
- **name**: human-readable, sentence case (e.g. `"Rotating border beam"`).
- **description**: one sentence. Lead with what it looks like, end with the
  technique (e.g. `"Conic-gradient comet sweeping along the border of a
  rounded card. Built with the mask-composite hollow-border trick."`).
- **tags**: pull from the controlled vocabulary below; suggest 2–4. Add a
  new tag only when none of the existing ones fit.
- **type**: `"animated"` if there's motion, else `"static"`.
- **dependencies**: `["gsap"]`, `["anime"]`, `[]`, etc. Reflect what
  `motion.js` actually imports/calls.
- **files**: always `{ preview, snippet }`; add `motion` for animated.
- **source**: `{ video, file, css_lines, motion_lines? }` pointing back at
  the original — this is how future you finds the context.
- **created_at**: today's date in `YYYY-MM-DD`.

#### Tag vocabulary (controlled — extend sparingly)

Visual character: `border`, `glow`, `gradient`, `shimmer`, `grain`, `glitch`,
`blur`, `shadow`, `outline`.

Motion character: `slam-in`, `sweep`, `pulse`, `parallax`, `morph`,
`reveal`, `transition`.

Component role: `card-decoration`, `text`, `chart`, `button`, `badge`,
`overlay`, `divider`, `cursor`, `hud`.

Atmosphere: `ambient`, `accent`, `loading`.

Show the proposed `meta.json` as JSON, ask: *"Confirm or adjust before I
write?"* — wait.

### Step 3 — Generalize

This is the work. Take the raw extracted code and decouple it from the source:

1. **Selectors**. Strip ancestor scoping like
   `[data-composition-id="scene-XX"] #s7-c .bars` down to a single
   class selector: `.<slug>` (e.g. `.border-beam`). The host element only
   needs that class plus whatever positioning the effect requires
   (usually `position: relative`).
2. **IDs → classes**. Replace `#some-id` with the same scoping class.
3. **Magic numbers → CSS custom properties**. Lift colors, sizes, durations,
   angles, and arc stops to `--<slug>-*` variables defined on the host class
   so the consumer can theme without forking. Keep the defaults you saw in
   the source as the variable defaults.
4. **Animated property**. The CSS custom property the motion kit tweens
   (e.g. `--beam-angle`) gets defined on the host with a starting value.
5. **Motion kit shape**. Export a single function the consumer calls from
   their composition's inline script:
   ```js
   export function <verbName><EffectName>(tl, target, opts = {}) { ... }
   ```
   Default the timing options the user can override (`at`, `duration`,
   `repeat`, `ease`). Don't bake video-specific timestamps in.

Show the user a side-by-side diff between the original snippet and the
generalized one. Ask: *"Approve, or want changes?"* — wait.

### Step 4 — Write the entry

Create the folder `design-catalog/<slug>/` and write all four files:

#### `meta.json`

The JSON you confirmed in Step 2.

#### `snippet.html`

Markup + a single `<style>` block. No `<html>`, `<head>`, `<body>`. No
`<script>`. Top comment briefly states what the consumer needs (e.g.
`"any element with class='border-beam' gets the comet sweep"`). All
custom properties documented inline.

#### `motion.js` (animated only)

ES module exporting the single function from Step 3. Top comment shows
example usage:

```js
//   import { spinBorderBeam } from "./design-catalog/border-beam/motion.js";
//   spinBorderBeam(tl, "#my-card", { at: 4.2, duration: 9, repeat: 1 });
```

#### `preview.html`

Self-contained HTML doc. Use this scaffold and fill in the marked sections:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title><Name> preview</title>
    <style>
      html, body {
        margin: 0; padding: 0; height: 100%;
        background: #0a0d12; color: #e6e9ef;
        font-family: "Inter", system-ui, sans-serif;
      }
      body { display: grid; place-items: center; padding: 24px; box-sizing: border-box; }

      /* --- snippet styles (kept in sync with snippet.html) --- */
      <PASTE the <style> contents from snippet.html here>
    </style>
  </head>
  <body>
    <div class="<slug>" id="demo">
      <!-- minimal demo content -->
    </div>

    <!-- Animated entries: load any deps then drive the motion on a loop -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
    <script type="module">
      import { <verbName><EffectName> } from "./motion.js";
      const tl = gsap.timeline({ repeat: -1 });
      <verbName><EffectName>(tl, "#demo", { at: 0, duration: 9, repeat: 0 });
    </script>
  </body>
</html>
```

Use `border-beam/preview.html` as the canonical reference for the scaffold
shape. Static-type entries omit the `<script>` blocks.

> **White-substrate viability.** With white now the composition **default**, an
> effect extracted from a dark scene may not survive the switch — additive
> **glow/bloom** mechanics that read on dark go invisible on white. This is
> advisory, NOT a default flip: the dark preview scaffold above can stay
> (effects are showcased in isolation, decoupled from any video's substrate).
> But when cataloging a newly-harvested effect, **check it for white-substrate
> viability** — ideally preview it on both backdrops — and if it only works on
> one, carry a `designed-for: dark` / `designed-for: light` tag so consumers
> know before they wire it onto a white canvas.

### Step 5 — Regenerate the index

Run:

```bash
uv run --project tools/design-catalog design-catalog
```

If validation fails, the tool prints a per-file error — fix and re-run. Do
not declare done until exit code is 0 and the new entry appears in
`design-catalog/catalog.json`.

### Step 6 — Hand off to verify

Tell the user:

> Open `design-catalog/index.html` via `python3 -m http.server 8000` from the
> repo root (or refresh if it's already open). The new card should appear in
> the grid; click it to confirm the preview animates and both copy buttons
> work.

Wait for their confirmation before claiming the task is done. If they tell
you to skip verification explicitly, fine — otherwise wait.

## Anti-patterns

- ❌ Inlining the snippet's CSS with the original `[data-composition-id]`
  ancestor selector. The whole point is to decouple from the source video.
- ❌ Hardcoding the source video's color palette without lifting to custom
  properties. The next consumer will want to retheme.
- ❌ Skipping `motion.js` because "the snippet works without it" — when the
  source has motion, the kit is required. (Otherwise mark `type: "static"`.)
- ❌ Writing a `motion.js` that depends on globals from the source video
  (`window.__timelines["scene-07"]`, scene-specific timestamps). The kit
  takes the timeline + target as arguments.
- ❌ Forgetting to run the generator. The viewer reads `catalog.json` —
  if you don't regenerate, the new card never appears.
- ❌ Modifying anything in `videos/`. Read-only.
