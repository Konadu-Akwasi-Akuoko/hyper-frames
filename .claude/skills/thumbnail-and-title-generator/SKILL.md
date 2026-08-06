---
name: thumbnail-and-title-generator
description: >-
  Guided generator that turns a hyper-frames video's working title into three
  production-ready YouTube thumbnails (1280x720) or Shorts/TikTok covers
  (1080x1920). Each variant REPLICATES the layout of a real, high-performing
  thumbnail picked from the `thumbnailInspo/` reference library (composition
  from the reference; the channel's "Specimen" style vocabulary — Inter 900
  2-tone headline + JetBrains Mono stat tell + precision pointer + accent
  palette — for the voice), PAIRED with a corpus-derived YouTube title, in an
  iterative render-and-score review loop. Use whenever the user wants to create, draft,
  generate, design, or A/B test thumbnails AND/OR titles for a hyper-frames
  video — phrases like "make a thumbnail", "I need thumbnails", "generate
  thumbnail variants", "design a cover", "write the title", "title this video",
  or any request that names a `videos/<slug>-<date>/` folder and asks for a
  thumbnail or title. Vertical/Shorts/TikTok mode activates when the invoking
  message contains any of: vertical, portrait, tiktok, shorts, reels, 9:16,
  1080x1920. Also triggers when run from inside a video folder after the script
  is drafted.
---

# thumbnail-and-title-generator

You guide the user through creating three YouTube thumbnails — each paired with
a YouTube title — for a single hyper-frames video. Output per round: three HTML
variants + a contact-sheet review page + three rendered PNGs, scored by a
subagent; on approval, three PNGs ready for YouTube's native A/B test.

**You never design a thumbnail from a blank canvas.** Every variant *replicates
the layout of a proven thumbnail* picked from the `thumbnailInspo/` reference
library (top thumbnails harvested from creators who win this niche's click), then
rebuilds that same composition with OUR content. Read
`reference/inspiration-mimicry.md` — it is the spine of this skill — and the
library contract in `thumbnailInspo/CLAUDE.md`.

Two halves, kept distinct:

- **Composition comes from the chosen reference** — archetype, where each element
  sits, the device that stops the scroll, the size hierarchy. Read off a measuring
  grid (`tools/thumbnail-inspo/grid.py`) so positions are exact.
- **Style vocabulary comes from the locked "Specimen" signature**
  (`reference/specimen-signature.md` + `templates/styles.css`) — the Inter 900
  2-tone headline, the JetBrains Mono stat tell, the precision annotation kit, the
  face compositing, and the accent **palette** (the one per-video hue variable).

We copy the *arrangement* (a public, uncopyrightable pattern) and swap ALL the
content — our headline, accent hue, face still, icons, stat. We never reproduce a
reference's face, artwork, screenshot, or text.

## Pre-flight check

Verify the signature is locked: `templates/styles.css` contains real CSS and
`reference/specimen-signature.md` exists. If either is missing/empty, refuse:

> "Visual signature not yet locked. See `reference/specimen-signature.md` for
> the rebrand process before generating thumbnails."

Verify the reference library exists: `thumbnailInspo/README.md` has a populated
`## Quick index` table. If it's missing or empty, refuse and point at the
harvester:

> "Thumbnail reference library empty. Run `python3 tools/thumbnail-inspo/fetch.py`
> then catalog it (see `thumbnailInspo/CLAUDE.md`) before generating thumbnails —
> this skill replicates a reference, it does not design from scratch."

## Division of labor (hard rule)

The **user supplies and credits the face image**; **you composite** it (cut
out, defringe, bleed, rim-light, place). You do **not** source third-party
copyrighted imagery yourself. If no usable face is provided, ask for one (see
`reference/compositing.md` for what "usable" means) — do not fabricate or
scrape one.

## Workflow

### Step 1 — Resolve the target folder + orientation mode

Resolve the **folder**: (1) a `videos/<slug>-<date>/` path in the message; else
(2) the CWD if it matches `**/videos/<slug>-<date>/`; else (3) ask, listing
`videos/*` plus a "create new" option (user supplies slug; date = today).
Convert to an absolute path and use it for every subsequent read/write.

Bootstrap the folder if it doesn't exist (idempotent — skip `mkdir` +
`npx hyperframes init` when it already exists), per `CLAUDE.md`.

Resolve the **orientation mode** (case-insensitive): the message contains any
of `vertical`, `portrait`, `tiktok`, `shorts`, `reels`, `9:16`, `1080x1920`
→ **vertical**; else **horizontal** (default). Print one line:
- Horizontal: `Mode: horizontal (1280×720) — YouTube thumbnail.`
- Vertical: `Mode: vertical (1080×1920) — Shorts/TikTok cover.`

If vertical, **load `reference/vertical-mode.md` now** and apply its overrides.

Round folders are mode-tagged with **independent counters**: horizontal scans
`round-(\d+)/`, vertical scans `round-(\d+)-vertical/`. Next round = `max + 1`
(NOT count + 1 — handles user-deleted rounds).

### Step 2 — Read the title + topic context

From `<video-dir>`: read `outline.md` (H1 = working title) and `script.md`
(prose body — mine candidate nouns, emotional beats, a citable stat for the
mono tell). If `outline.md` is missing/unusable, ask for the title + a 2-line
summary. If `script.md` is missing, warn but proceed.

Then probe `<video-dir>/seo/research.json`: **present** → load it for Step 5
(`Using SEO research from <date>.`); **missing** → ask once: run the
`youtube-seo-research` skill now (~25s)? On yes, invoke it and load the result;
on no/skip, proceed without and don't re-prompt this session. Never block on it.

### Step 3 — Pick + grid the reference layouts (drives Steps 4–8)

**Load `reference/inspiration-mimicry.md` now** — it is the spine of the build.
Then open `thumbnailInspo/README.md` and scan the `## Quick index` table only.

Pick **three references**, one per variant, deliberately spread across different
archetypes/devices so the round is a real choice (e.g. a face-reaction, a
giant-number stat, a comparison-vs) — matched to the video's beats via each row's
`archetype` / `device` / `mimic-for`. (If the user asked for variations on a
single idea, pick ONE reference and vary headline/accent/face across a/b/c.) In
vertical mode, prefer references that survive a 9:16 crop. Print the picks, and
**`open` each picked reference image so the user can see it** (`open
thumbnailInspo/<channel>/<file>`) — then print the per-direction source list of
`<label> · <youtube-source-url>` (no `file://`, no local path; the image is
already on screen):

`A ← thumbnailInspo/<channel>/<file> (<slug>): <archetype>/<device> — why it fits.`

Then **grid each picked reference** and read its element positions in the same
1280×720 space the templates use:

```bash
python3 tools/thumbnail-inspo/grid.py thumbnailInspo/<channel>/<file>.jpg \
  --out <video-dir>/thumbnails/round-N/ref/<letter>.grid.png
```

`Read` each gridded PNG and record, per variant: the face/object zone (cells +
x,y + fill), the headline zone (cells + baseline y + which word pops), and the
device/stat/badge position. Cross-check against that entry's `Layout map:` line.
These positions drive the headline sizing (Step 4), accent (Step 6), face side
(Step 7), and the composition (Step 8). Picking + gridding a reference is
**mandatory** for every variant — never design a layout from scratch.

### Step 4 — Write the 2-tone headlines (shaped to each reference's text zone)

Load `reference/headline-recipes.md`. Produce three headline texts that differ
on **direction** (direct upgrade / sweeping reframe / punchy declarative). Each
is the Specimen 2-tone shape: white flanking row(s) + ONE accent **punch** row
+ a monospace `// tell` (carry a concrete stat/number when one exists). ALL
CAPS for the headline rows. **Size + shape each headline to fit its variant's
reference text zone** (the cells/width you read in Step 3) — a centered big-text
reference wants a short punchy line; a text-left-face-right reference wants the
multi-row stack in the left column. If a line won't fit its zone, rewrite shorter
— never overflow. Sizing: flanking base on `.thumbnail-text`, `.punch` = 1.7em,
mono tell = 0.42em.

### Step 5 — Pair a YouTube title to each headline

Load `reference/title-engine.md`. Write **one** paired YouTube title per
variant — the searchable, grounded version of the thumbnail's bigger claim
(one concrete searchable noun + an emotional beat; 38–46 chars; sentence case;
curiosity resolving to a named enemy/reversal, or an open What/Why/How). If
`seo/research.json` is loaded, print the compressed digest first (top nouns,
demand phrases, saturation warning) and let it inform — not dictate — the
titles. The thumbnail and title do different jobs; never make the title a
sentence-cased copy of the headline.

### Step 6 — Pick the accent word + accent hue

Load `reference/accent-recipes.md`. Per variant: (a) which word is the **punch/
accent** (Tier 1 topic noun always; Tier 2 tension verb/adjective; ≤2 accent
regions); (b) which **hue** from the palette (`acc-teal` default; choose by
topic/emotion). Use `acc-red` only for emotionally-red beats — it is the
niche's most-saturated accent; lean cooler/unclaimed hues for contrast. If the
reference's device is a danger/worst beat in red, `acc-red` is the right call;
otherwise keep the reference's *role* (one hot accent) in our cooler palette.

### Step 7 — Source-prep the face (+ optional brand chip)

Only if the chosen reference has a face. **Faceless references** (logo-grid,
object-hero, code-screenshot, diagram, big-text) take **no** face — do not force
one in; build their hero element instead (Step 8).

When the reference has a face, the user supplies the still. Cut it out and
**defringe/despill** per
`reference/compositing.md` (`npx hyperframes remove-background`, then the
ImageMagick erode/despill recipes). Save the cleaned cutout under
`<video-dir>/thumbnails/cutouts/`. Same face across a round's three variants
unless the concepts call for different emotions. CSS glow does **not** fix a
matte fringe — fix the PNG.

Optional brand chip: load `reference/brand-chip.md` only if the topic IS a
nameable brand (JS, React, Docker…). Most thumbnails need none.

### Step 8 — Compose by replication + write the variant HTML + contact sheet

Create `<video-dir>/thumbnails/round-N/` (or `round-N-vertical/`). Each variant
**rebuilds its Step-3 reference's composition** with our content, in the Specimen
style vocabulary. Per `reference/inspiration-mimicry.md`: land OUR elements at the
positions you read off the reference grid — face/object on the reference's side
(override the CSS default via inline `style`), headline in its zone, the
scroll-stopping device reproduced with a signature primitive (annotation kit,
`.chip`, mono `.stat`, or a bespoke absolutely-positioned hero block) at the
reference's coordinates. Faceless references get no face. Copy the arrangement;
never the reference's face/artwork/screenshot/text.

`templates/variant.html` is the scaffold — read `variant.html` +
`templates/contact-sheet.html` and substitute tokens **globally** (regex `/g` in
JS, `re.sub` in Python — token names appear in both the doc comment and the
markup). For layouts that differ from the default Specimen silhouette, add inline
`style` position overrides to the `.thumbnail-text` / `.face-wrap` / `.anno` /
`.chip` elements (and bespoke hero `div`s) so the composition matches the
reference — the token slots cover the common face-right case; the overrides cover
the rest.

`variant.html` tokens: `STYLES_HREF` (absolute file:// to `templates/styles.css`),
`TITLE_PLAIN`, `THUMBNAIL_CLASS` (`""`|`vertical`), `ACCENT_CLASS` (`acc-*`),
`WARM_CLASS` (`""`|`warm`), `FACE_IMAGE_URL` (absolute file:// to the defringed
cutout), `ROW_FONT_SIZE_PX` (flanking base), `TITLE_ROW_1..5` + `ROW_1..3_CLASS`
(the punch row gets `punch accent`; vertical Variant C kicker gets `kicker`),
`MONO_TELL`, `CHIP_HTML` (`""` or a positioned `.chip`), `ANNOTATION_SVG`
(`""` or a positioned `.anno` inline-SVG from `reference/annotation-kit.md`).

**Place every element against BOTH grids**: read the target (x, y) off the
reference's `ref/<letter>.grid.png` (Step 3), then append `?grid` to our variant
URL to see the 20px/100px graph + numbered x/y axes + title-safe border and set
the element's `left/top` (+ any annotation endpoint) to the matching coordinate.
Our position should mirror the reference's. Use the precision pointer / bracket /
ring from the kit — **never a hand-drawn scribble arrow**, never the `leader-line`
library.

Write `a.html`, `b.html`, `c.html`, `contact-sheet.html` into the round folder.
In vertical mode use the per-variant block from `reference/vertical-mode.md`;
the horizontal `{{VARIANTS_HTML}}` block is three copies of:

```html
<div class="variant">
  <div class="variant-header">
    <span class="variant-letter">{{LETTER_UPPER}}</span>
    <span class="variant-text">{{TITLE_PLAIN}}</span>
  </div>
  <div class="variant-yt-title">
    <span class="variant-yt-label">YouTube title</span>
    <span class="variant-yt-text">{{YOUTUBE_TITLE}}</span>
  </div>
  <div class="row">
    <div><div class="row-label">Full size (40% of 1280×720)</div>
      <div class="full-wrap">{{THUMBNAIL_DIV}}</div></div>
    <div><div class="row-label">YouTube feed grid (~210px)</div>
      <div class="grid-wrap">{{THUMBNAIL_DIV}}</div></div>
  </div>
  <div class="variant-links">
    <a href="{{LETTER_LOWER}}.html">view full</a> ·
    <a href="{{LETTER_LOWER}}.html?grid">view with grid</a>
  </div>
</div>
```

Do NOT rename `variant-letter` / `variant-text` / `variant-yt-text` — `create-srt`
`extract_titles.py` parses them. `{{THUMBNAIL_DIV}}` = the variant's `.thumbnail`
markup (the `<div class="thumbnail …">…</div>` block **without** the trailing
`<script>`), inlined in both wraps; `{{TITLE_PLAIN}}` = the headline text,
`{{YOUTUBE_TITLE}}` = the paired title.

### Step 9 — Render the round + self-verify + score

Render each variant to `round-N/out/{a,b,c}.png` (single-file mode):

```bash
node <repo-root>/tools/thumbnail-render/bin/render.mjs \
  <video-dir>/thumbnails/round-N/<letter>.html \
  --out <video-dir>/thumbnails/round-N/out/<letter>.png
```

Then load `reference/qa-loop.md` and run it: **Read each PNG yourself**,
**crop-zoom the risky edges** (`magick … -crop … +repage`), then spawn a
subagent to **score** each (Sonnet to iterate, Opus to verify). Add a
**resemblance check**: put each rendered PNG next to its reference's
`ref/<letter>.grid.png` and confirm the *composition* matches (element positions,
size hierarchy, device, reading path) — content is all ours, layout is the
reference's. If it doesn't read as the same layout family, re-place. Fix the top
issues (cutout fringe is priority), re-render, re-score. Do not present until
each variant is **≥8/10 AND zero FAIL on cutout edges AND the composition matches
its reference** AND your own eyes agree. Never report unverified output.

### Step 10 — Present + iterate

Tell the user the round is ready and **`open` the contact sheet for them**
(`open <video-dir>/thumbnails/round-N/contact-sheet.html`) — each card shows the
paired YouTube title; append `?grid` to a variant URL to overlay the numbered
coord grid. Also `open` the three rendered PNGs. `open` is how the user actually
sees them — `file://` and markdown links won't open in their terminal; print
paths only as a written record. Interpret feedback per
`reference/iteration-recipes.md` and generate the next round (default: a new
round folder). Loop.

Never pick a winner among the three, and never declare "good enough" — the user
judges and YouTube's A/B mechanism measures. The loop ends only when the user
says "ship it" / "export" / "approved".

### Step 11 — Final export

On approval, render the chosen round to the video folder:

```bash
# horizontal
node <repo-root>/tools/thumbnail-render/bin/render.mjs \
  <video-dir>/thumbnails/round-N --variants --out-dir <video-dir>
# vertical
node <repo-root>/tools/thumbnail-render/bin/render.mjs \
  <video-dir>/thumbnails/round-N-vertical --variants --orientation vertical --out-dir <video-dir>
```

Writes `thumbnail-{a,b,c}.png` (or `thumbnail-vertical-{a,b,c}.png`). Print the
three absolute paths + the three paired titles so the user can load them into
YouTube's A/B upload. Record the face image credit where the video tracks
sources (description/credits).

## Hard rules (always in effect)

- **Every variant replicates a `thumbnailInspo/` reference — never design from
  scratch.** Pick the reference (Step 3), grid it, read positions, rebuild the
  composition with our content. Copy the *arrangement*; swap ALL content. Never
  reproduce a reference's face, artwork, screenshot, or text. Spread the three
  variants across different archetypes.
- **The user supplies + credits the face; you composite.** Never source
  third-party imagery yourself. Always defringe/despill the cutout. Faceless
  references take no face.
- **2-tone headline:** white flanking + ONE accent punch row + a mono `// tell`.
  ALL CAPS headline. ≤2 accent regions.
- **Accent = one palette hue per video** (`acc-*`). Red is available but is the
  saturated niche hue — use it sparingly.
- **Annotation = the inline-SVG kit, precision grammar.** No hand-drawn
  scribble arrows. No `leader-line`. Place by reading the numbered coord grid.
- **Render + LOOK + crop-zoom + subagent-score every round** before presenting;
  ship ≥8/10 with zero cutout-edge FAILs.
- **Never pick a winner; never declare done unilaterally.** User judges,
  YouTube A/B measures. The loop ends on the user's "ship it".
- **No editorial chrome** beyond the signature (the coord grid is design-only,
  never in the final PNG).
- **To show the user any local image, `open` it.** When you reference a file for
  the user to *view* — candidate references, gridded refs, rendered PNGs, the
  contact sheet — run `open <path>` (macOS) so it launches in Preview/browser.
  `file://` URLs and relative markdown links do **not** open in the user's Claude
  Code terminal. Alongside the `open`, print a written record as a per-direction
  list of `<label> · <youtube-source-url>` (the source URL from the reference's
  `## Entries` block / channel `_manifest.json`) — **never** a `file://` or local
  path in that list; the file is already on screen, the list is for the source.
- **Preserve the consumer contract:** `a/b/c.html`, `contact-sheet.html`, the
  `variant-letter`/`variant-text`/`variant-yt-text` spans, `<span
  class="thumbnail-row">` rows + `<title>`, and the output PNG names — other
  skills (`create-srt-and-translate`, the renderer, `shorts-creator`) depend on
  them.

## Reference files (load on demand)

- `reference/inspiration-mimicry.md` — **the spine: pick a `thumbnailInspo/` reference, grid it, replicate the layout with our content.** Load at Step 3.
- `reference/specimen-signature.md` — the locked style vocabulary (type/color/annotation/face) + accent palette + why. Load at pre-flight / rebrand discussion.
- `reference/headline-recipes.md` — the 2-tone headline patterns. Load at Step 4.
- `reference/title-engine.md` — corpus-derived paired-title formulas. Load at Step 5.
- `reference/accent-recipes.md` — accent word + hue selection. Load at Step 6.
- `reference/compositing.md` — cutout / defringe / despill / rim-light + source-image requirements. Load at Step 7.
- `reference/brand-chip.md` — the optional per-topic brand chip. Load at Step 7 only if the topic is a brand.
- `reference/annotation-kit.md` — the inline-SVG primitives + coord-grid placement. Load at Step 8.
- `reference/qa-loop.md` — the subagent QA checklist + ship threshold. Load at Step 9.
- `reference/iteration-recipes.md` — feedback interpretation. Load at Step 10.
- `reference/vertical-mode.md` — portrait (1080×1920) overrides. Load at Step 1 if mode is vertical.

## Things this skill does NOT do

- Generate the script (that's `script-writer`) or the voiceover/transcript.
- Source the face image (the user supplies + credits it).
- Pick a winner among variants (the user picks; YouTube measures).
- Upload to YouTube (the user does the upload + A/B setup).
- Render thumbnails for non-hyper-frames content (assumes the `videos/<slug>-<date>/` layout).
