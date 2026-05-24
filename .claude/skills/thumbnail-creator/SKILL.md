---
name: thumbnail-creator
description: >-
  Guided generator that turns a hyper-frames video's working title into three
  production-ready YouTube thumbnail variants (1280x720) or Shorts/TikTok cover
  variants (1080x1920) in the channel's locked visual style, with an iterative
  review loop. Use this skill whenever the user wants to create, draft,
  generate, design, or A/B test thumbnails for a hyper-frames video — phrases
  like "make a thumbnail for this video", "I need thumbnails", "generate
  thumbnail variants", "design a thumbnail", or any request that names a
  `videos/<slug>-<date>/` folder and asks for a thumbnail. Vertical/Shorts/TikTok
  mode activates when the invoking message contains any of: vertical, portrait,
  tiktok, shorts, reels, 9:16, 1080x1920. Also triggers when the user runs the
  skill from inside a video folder after the script is drafted.
---

# thumbnail-creator

You are guiding the user through creating three YouTube thumbnail variants
for a single hyper-frames video. Output: three HTML variants and a
contact-sheet review page per round, then three PNGs ready for YouTube's
native A/B test feature once the user approves.

The visual signature is **locked** (font, background, accent color, text
color, icon style — all in `templates/styles.css` and documented in
`reference/visual-signature.md`). You do not redesign it per video. You
only choose: thumbnail text, accent placement, and icon.

## Pre-flight check

Before doing anything, verify the visual signature is locked: check that
`templates/styles.css` contains real CSS (not placeholder content) and
that `reference/visual-signature.md` exists. If either is missing or
empty, refuse to run with this message:

> "Visual signature not yet locked. Run the visual-signature design
> exercise first — see `reference/visual-signature.md` for the rebrand
> process."

If both are present, continue.

## Workflow

### Step 1 — Resolve the target video folder and orientation mode

Resolve the **target folder** in this order:

1. If the user's message contains a path like `videos/<slug>-<date>/`
   (relative or absolute), use that.
2. If the current working directory matches `**/videos/<slug>-<date>/`,
   use that.
3. Otherwise, ask: "Which video folder should I work in?" — list existing
   `videos/*` directories, **plus an option to create a new folder** (the
   user supplies a slug; date is today).

Convert the result to an absolute path. Use that absolute path for every
subsequent file read and write — do not depend on CWD after this step.

**Bootstrap the folder if it doesn't exist.** The skill can be invoked
before later pipeline stages have run (e.g. designing thumbnails up
front). If the resolved folder doesn't exist on disk, scaffold it now
using the project's canonical bootstrap from `CLAUDE.md`. The block is
**idempotent** — when invoked against an existing folder, it skips
`mkdir` and `npx hyperframes init` entirely:

```bash
# from the repo root — skip if folder already exists
if [ -d "videos/<slug>-<YYYY-MM-DD>" ]; then
  cd videos/<slug>-<YYYY-MM-DD>
  echo "Folder already exists. Skipping mkdir + hyperframes init."
else
  mkdir -p videos/<slug>-<YYYY-MM-DD>
  cd videos/<slug>-<YYYY-MM-DD>
  npx hyperframes init
fi
```

Use today's date when constructing a new folder name. After this, Step 2
will read `outline.md` and `script.md` — if those don't exist yet (the
folder was just bootstrapped), the skill will halt at Step 2 with a
clear "run script-writer first" message rather than fabricating a
working title.

Resolve the **orientation mode** in this order (case-insensitive):

1. If the invoking message contains any of `vertical`, `portrait`,
   `tiktok`, `shorts`, `reels`, `9:16`, `1080x1920` → **vertical mode**.
2. Otherwise → **horizontal mode** (default).

Print a one-line confirmation:
- Horizontal: `Mode: horizontal (1280×720) — YouTube thumbnail.`
- Vertical: `Mode: vertical (1080×1920) — Shorts/TikTok cover.`

If mode is vertical, **load `reference/vertical-mode.md` now** and
apply its overrides to every subsequent step it names (Steps 3, 5, 7,
10). Anything that doc doesn't override carries over from this file
verbatim.

Round folders are mode-tagged. When computing the next round number in
Step 7:
- Horizontal mode: scan `<video-dir>/thumbnails/round-(\d+)/` entries
  (un-suffixed). The vertical rounds are excluded.
- Vertical mode: scan `<video-dir>/thumbnails/round-(\d+)-vertical/`
  entries. The horizontal rounds are excluded.

Modes have independent counters; a single video can have
`round-3/` (horizontal) and `round-1-vertical/` simultaneously.

### Step 2 — Read the title and topic context

From the resolved `<video-dir>`:

- Read `<video-dir>/outline.md`. The H1 is the working title (format:
  `# <topic> — 9-beat outline`). Extract the topic.
- Read `<video-dir>/script.md` for prose body context. Mine candidate
  nouns for icon picking and accent words.

If `outline.md` is missing or its H1 isn't a usable working title, ask
the user for the title and a 2-line topic summary before continuing.

If `script.md` is missing, warn the user but proceed — the rephrase
step works on the title alone; icon and accent picks just have less
context to draw from.

Then probe `<video-dir>/seo/research.json`:

- **Present** → load it for use at Step 4. Print: `Using SEO research from <date>.`
- **Missing** → ask once per session: `"No SEO research found. Run it now via the youtube-seo-research skill (~25s)? [Y/n/skip]"`. On Y, invoke `youtube-seo-research` via the `Skill` tool and load the result. On n/skip, proceed without it (current behavior) and don't re-prompt during subsequent thumbnail iterations in the same session.

Never block on missing data — the rephrase, icon, and accent picks all work fine without SEO context. The data only informs Step 4 (paired title).

### Step 3 — Generate three thumbnail-text rephrases

Load `reference/text-rephrase-recipes.md`. Apply the recipes to produce
three variant texts that:

- Are 7–11 ALL CAPS words each.
- Break into exactly 3 rows.
- Read as bolder, more declarative claims than the working title.
- Fit cleanly in JetBrains Mono ExtraBold within the available text
  column (~780 px wide).

The three variants must differ on **direction** (direct upgrade /
sweeping reframe / punchy declarative), not just word choice — otherwise
the user can't make a real choice between them.

#### Computing the per-variant font size

JetBrains Mono is monospace, so the longest row determines the maximum
font size. The text column is 780 px wide (1280 − 80 left padding − 420
right padding for the 320 px icon). The formula:

```
longest_row_chars   = max character count across the 3 rows
                      (count letters, digits, and spaces; not the
                      <span> markup)
ROW_FONT_SIZE_PX    = floor(780 / (longest_row_chars * 0.6))
                      capped at 140
```

Examples (verified against rendered mockups):
- 13 chars → 100 px
- 14 chars →  92 px
- 15 chars →  86 px
- 16 chars →  81 px (visibly small — consider rephrasing shorter)
- 17 chars →  76 px (rejects, below the 80 px floor)

If the computed size falls below 80 px, reject the rephrase and either
produce a shorter wording or ask the user to choose a shorter title.
The renderer must NOT silently shrink — preview-vs-output drift is the
worst failure mode.

### Step 4 — Pair a YouTube title to each rephrase

Load `reference/youtube-title-pairing.md`. For each variant text from
Step 3, write **one** paired YouTube title that the video would ship
with if that variant won.

If `seo/research.json` was loaded in Step 2, before producing the 3 paired titles, print this compressed digest (4 data lines — the hook-shape line is dropped because title pairing is not where hook shape applies):

```
SEO context — <topic> (n=<N> videos)
  Top searchable nouns: <noun1> (<count>), <noun2> (<count>), <noun3> (<count>)
  Demand phrases:       "<phrase1>", "<phrase2>"
  Saturation warning:   <N> videos >100K views use "<pattern>" — differentiate
  Top-performer ages:   median <X> months, freshest <Y> weeks
```

For ages: derive from `top_videos[].upload_date` (yt-dlp format `YYYYMMDD`) at print time. When a signal is empty, substitute `(none surfaced)` instead of dropping the line — empty is informative.

Then produce the 3 paired titles informed by — but not slavishly conforming to — the digest. The "Using SEO research" section in `youtube-title-pairing.md` codifies what to do with each signal.

The thumbnail and the YouTube title do **different jobs**: the
thumbnail wins the click in the feed, the title wins search and the
algorithm. They should differ — never let the title be a
sentence-cased copy of the thumbnail text.

Quick rules (full version in the reference file):

- **Sentence case**, not ALL CAPS. ALL CAPS is the thumbnail's locked
  signature.
- Carry the **searchable topic noun** verbatim (e.g., "text",
  "rendering", "font" for a typography video). This is what earns the
  YouTube search.
- Length: 40–70 chars target. Hard cap 100.
- The thumbnail makes the bigger CLAIM; the title is the grounded,
  answerable version of that claim.

Per `research/pawel-code-stuff/analysis/thumbnail-patterns.md` §7,
this asymmetry is the point — let the surfaces play different roles.

### Step 5 — Pick accent words per variant

Load `reference/red-word-recipes.md`. For each variant, pick the accent
word(s):

- Tier 1 (always accent): the topic noun.
- Tier 2 (often accent): the verb/adjective creating tension with the
  noun.
- Tier 3 (never accent): connectors.
- Cap: 2 accent regions per variant.

### Step 6 — Pick the icon

Load `reference/icon-picking.md`. Pick **one** icon for the topic (same
icon across all 3 variants in this round). Resolution order:

1. **Lucide.** Read
   `<repo-root>/tools/thumbnail-render/icons/lucide.json`. Look up by
   Lucide name (e.g. `Lock`, `Database`). Each entry is
   `{body, viewBox}` — capture both. Lucide is canonically 24×24, so
   `viewBox` is always `"0 0 24 24"`.
2. **Iconify line-icon fallback.** If no Lucide entry fits, pick an
   Iconify name in `<set>:<icon>` form from the line-icon search order
   below (e.g. `ph:cursor-click`, `tabler:typography`). Resolve via:

   ```bash
   node <repo-root>/tools/thumbnail-render/bin/icon.mjs <name>
   ```

   The CLI prints JSON `{"body": "...", "viewBox": "..."}` to stdout,
   fetches from `api.iconify.design` on first use, caches to
   `tools/thumbnail-render/icons/iconify-cache.json`. Parse the JSON
   and capture both fields.
3. **Brand exception.** When the topic noun *is* a specific brand
   (Jenkins, Docker, React, Postgres, Kubernetes — the brand appears
   in the working title or is the explicit subject), brand-icon sets
   become eligible. Preference order:
   `simple-icons` (monochrome silhouette) → `logos` (multi-color) →
   `devicon`. Take the first that's recognizable at thumbnail size;
   only escalate to multi-color when the brand collapses without its
   colors (Google, Slack). Resolve via the same `icon.mjs` CLI.
4. **Stop.** If none of the above fit, ask the user for an alternate
   icon name. Hand-coded SVG is no longer a documented option — the
   visual signature requires real icons from a curated set.

Iconify line-icon search order (default path, step 2):
`lucide` → `ph` → `tabler` → `mynaui` → `heroicons` (outline) →
`lineicons`. Filled, multi-color, and pictographic sets
(`fluent-color`, `noto`, `twemoji`, `flat-color-icons`, etc.) are
reserved for the brand exception in step 3 — never use them for
generic topic nouns.

#### Choosing the `ICON_CLASS` token value

Color and stroke handling is class-driven, not body-mutating. Body
strings stay verbatim from the cache; pick the right class for the
icon family:

| Source | `ICON_CLASS` value | Effect |
|---|---|---|
| Lucide / line-icon Iconify (`ph`, `tabler`, etc.) | `""` (empty) | Default line-icon styling: cream stroke, no fill |
| `simple-icons:*` (monochrome brand silhouette) | `"brand-silhouette"` | Filled cream silhouette, no stroke |
| `simple-icons:*` with full-icon accent tint | `"brand-silhouette accent"` | Filled amber silhouette |
| `logos:*` / `devicon:*` (multi-color brand) | `"brand-color"` | Path fills win, no stroke |

For line icons, apply the accent to one detail by inlining
`stroke="#FFB627"` on exactly one element of the body string (or
`fill="#FFB627"` for a filled detail). See `reference/icon-picking.md`
for which element to accent on common Lucide icons.

For brand-silhouette icons, never inline accent — use the `accent`
class modifier above (tints the whole logo amber). For `brand-color`,
never tint at all — keep original brand colors. See
`reference/icon-picking.md` "Brand exception" for the full rules.

### Step 7 — Compute the next round number and write the HTML

Round number `N`:
- List entries in `<video-dir>/thumbnails/`.
- Filter for names matching `round-(\d+)`.
- `N = max(captured numbers) + 1`, or `1` if none exist.
- This handles user-deleted rounds correctly — pick `max + 1`, NOT
  `count + 1`.

Create `<video-dir>/thumbnails/round-N/`. Read the templates from
`templates/variant.html` and `templates/contact-sheet.html`. Substitute
tokens (see those files' leading comments for the token list).

**Substitution must be global.** Use a regex with the `g` flag in JS
(`html.replace(/\{\{TOKEN\}\}/g, value)`), `re.sub(...)` in Python, or
equivalent — never naive single-occurrence string replace. Token names
appear in both the leading documentation comment AND the actual
markup; first-occurrence replace will eat the comment occurrence and
leave real tags unsubstituted.

Token reference (for `variant.html`):
- `STYLES_HREF` — absolute file:// URL to
  `<repo-root>/.claude/skills/thumbnail-creator/templates/styles.css`
  (never relative — round folders are deep enough that relative paths
  are fragile)
- `TITLE_PLAIN` — plain text title
- `ROW_FONT_SIZE_PX` — autosized integer per variant
- `TITLE_ROW_1`, `TITLE_ROW_2`, `TITLE_ROW_3` — row HTML with accent
  spans
- `TITLE_ROW_4`, `TITLE_ROW_5` — extra rows for vertical Variant B
  (stacked staccato, 4-5 rows). Default to `""` for horizontal mode
  and for vertical Variants A/C; empty rows are hidden by the
  `.thumbnail-row:empty` CSS rule.
- `ICON_VIEWBOX` — from the cache entry / CLI JSON; e.g.
  `"0 0 24 24"`, `"0 0 256 417"`
- `ICON_CLASS` — per the table in step 6 (`""`, `"brand-silhouette"`,
  `"brand-silhouette accent"`, or `"brand-color"`)
- `ICON_SVG_BODY` — the `body` field from the cache entry / CLI JSON
- `THUMBNAIL_CLASS` — `""` for horizontal (default); `"vertical"` for
  vertical mode. Determines the `.thumbnail` wrapper class which
  drives layout via class-scoped CSS in `templates/styles.css`. See
  `reference/vertical-mode.md` for the full vertical layout spec.
- `ROW_3_CLASS` — `""` for horizontal and for Variants A/B in vertical
  mode. `"kicker"` for Variant C in vertical mode only. Scales row 3
  to 0.6em via the `.thumbnail.vertical .thumbnail-row.kicker` CSS
  rule. The kicker's computed pixel size (0.6 × dominant font size)
  must clear the 90 px floor; if it doesn't, rephrase shorter.

Write:
- `<video-dir>/thumbnails/round-N/a.html`
- `<video-dir>/thumbnails/round-N/b.html`
- `<video-dir>/thumbnails/round-N/c.html`
- `<video-dir>/thumbnails/round-N/contact-sheet.html`

#### The `{{VARIANTS_HTML}}` block shape

`templates/contact-sheet.html` has a single `{{VARIANTS_HTML}}` slot.
In horizontal mode, build it by concatenating three copies of this block
(one per variant). In vertical mode, use the alternative block defined
in `reference/vertical-mode.md` §7 instead — same `{{VARIANTS_HTML}}`
slot, different per-variant block shape (three preview wraps: full,
Shorts feed, TikTok profile-grid 1:1 crop).

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
    <div>
      <div class="row-label">Full size (40% of 1280×720)</div>
      <div class="full-wrap">
        {{THUMBNAIL_DIV}}
      </div>
    </div>
    <div>
      <div class="row-label">YouTube feed grid (~210px)</div>
      <div class="grid-wrap">
        {{THUMBNAIL_DIV}}
      </div>
    </div>
  </div>
  <div class="variant-links">
    <a href="{{LETTER_LOWER}}.html">view full</a> ·
    <a href="{{LETTER_LOWER}}.html?grid">view with grid</a>
  </div>
</div>
```

Tokens introduced for this block:
- `{{LETTER_LOWER}}` — `a` | `b` | `c` for variants A | B | C.
- `{{YOUTUBE_TITLE}}` — the paired YouTube title from Step 4
  (sentence case, contains the searchable topic noun).

`{{THUMBNAIL_DIV}}` is the same `.thumbnail` markup used in
`variant.html`, inlined twice (once in `full-wrap`, once in `grid-wrap`).
The wraps CSS-scale the inner `.thumbnail` to 40% and ~16.4% of its
1280×720 source, so the same markup reads at both sizes.

### Step 8 — Print the contact-sheet URL

Tell the user:

> "Round N is ready. Open `file://<absolute-path-to-contact-sheet.html>`
> in your browser. The page shows each variant at full 1280×720 plus a
> small grid-size simulation (~210×118 px) so you can judge legibility
> at the YouTube feed size. Each variant header lists the **paired
> YouTube title** I'd ship that variant with — the title and thumbnail
> do different jobs, so they're written differently. Each variant has
> 'view full · view with grid' links — `?grid` overlays a 4×3 numbered
> grid plus YouTube safe-area markers for layout review. Tell me what
> you want to change (text, accent placement, icon, or paired title)."

### Step 9 — Iterate

Receive the user's feedback. Interpret per
`reference/iteration-recipes.md`. Generate the next round (Step 7 again
with the new content). Loop.

The default is always a new round folder. Edit-in-place only when the
user explicitly says so.

### Step 10 — Final export

When the user signals approval ("ship it", "export", "done", "approved"),
run the renderer to produce the final PNGs. Use absolute paths for both
the renderer binary and the round directory:

Horizontal mode:

```bash
node <repo-root>/tools/thumbnail-render/bin/render.mjs \
  <video-dir>/thumbnails/round-N \
  --variants \
  --out-dir <video-dir>
```

Vertical mode:

```bash
node <repo-root>/tools/thumbnail-render/bin/render.mjs \
  <video-dir>/thumbnails/round-N-vertical \
  --variants \
  --orientation vertical \
  --out-dir <video-dir>
```

This writes (horizontal):
- `<video-dir>/thumbnail-a.png`
- `<video-dir>/thumbnail-b.png`
- `<video-dir>/thumbnail-c.png`

Or (vertical):
- `<video-dir>/thumbnail-vertical-a.png`
- `<video-dir>/thumbnail-vertical-b.png`
- `<video-dir>/thumbnail-vertical-c.png`

Print the three absolute paths so the user can drag them into YouTube's
A/B test upload UI.

## Hard rules (always in effect)

- Exactly 7–11 words per variant.
- Exactly 3 rows of text per variant.
- ALL CAPS, always.
- Maximum 2 accent regions per variant.
- No question marks, ellipses, colons, parentheses, emoji, arrows, drop
  shadows, or gradients.
- The icon names the topic statically. Never the insight, never a
  before/after, never a comparison.
- The visual signature constants do not change per video.
- Never pick a winner from the three variants. The user judges; YouTube's
  A/B mechanism measures.
- Termination: the loop ends when the user says "ship it" or equivalent.
  Never declare "this is good enough" on your own.

## Reference files (load on demand)

- `reference/visual-signature.md` — the locked constants and why each was
  chosen. Load when the user asks why something looks the way it does, or
  when discussing rebranding.
- `reference/text-rephrase-recipes.md` — the rephrase patterns. Load at
  Step 3.
- `reference/youtube-title-pairing.md` — paired YouTube title rules
  (title vs. thumbnail division of labor, length, search keywords).
  Load at Step 4.
- `reference/red-word-recipes.md` — accent placement rules. Load at
  Step 5.
- `reference/icon-picking.md` — Lucide lookup + Iconify fallback. Load
  at Step 6.
- `reference/iteration-recipes.md` — feedback interpretation. Load at
  Step 9 (every iteration).
- `reference/vertical-mode.md` — overrides applied when the user
  invokes vertical mode (Shorts/TikTok cover). Load at Step 1 if mode
  is vertical; not loaded otherwise.
- `reference/text-rephrase-vertical.md` — vertical-mode rephrase
  rhythms (Variants A/B/C correspond to wide-recap / stacked-staccato
  / headline+kicker). Load at Step 3 in vertical mode; the horizontal
  `text-rephrase-recipes.md` is not loaded in vertical mode.

## Things this skill does NOT do

- Generate the script. That's the `script-writer` skill (this runs after).
- Pick a winner. The user picks; YouTube measures.
- Upload to YouTube. The user does the upload.
- Render thumbnails for non-hyper-frames content. This skill assumes a
  `videos/<slug>-<date>/` folder structure.
