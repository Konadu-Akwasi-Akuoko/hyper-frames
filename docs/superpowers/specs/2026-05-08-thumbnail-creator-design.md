# thumbnail-creator skill — design

**Date:** 2026-05-08
**Status:** spec, ready for implementation plan
**Companion skill:** `script-writer` (this runs after the script is drafted)

## 1. Purpose

Generate three production-ready YouTube thumbnail variants for a hyper-frames
video, in the channel's locked visual style, with a tight iteration loop until
the user approves all three. On approval, render all three to PNG so the user
can upload the full set to YouTube's native A/B test feature (which rotates up
to 3 thumbnails per video and picks the best-performing one).

The thumbnails follow the structural rules surfaced in the
`research/pawel-code-stuff/` analysis — fixed visual template, three rows of
ALL-CAPS text, two-color rule, accent reserved for the curiosity noun, one icon
that names the topic statically. The visual signature itself (font, colors,
icon style) is intentionally distinct from Pawel's so our thumbnails don't
lose to his in any feed where they appear together.

## 2. Scope

**In scope:**
- Reading video context from `script.md` inside `videos/<slug>-<date>/`.
- Generating three text rephrases of the video's title that are punchier than
  the title itself, per the research's rephrase pattern.
- Selecting accent words for each variant per the research's red-word rules.
- Picking a Lucide icon for the topic (with a hand-coded SVG fallback).
- Rendering three HTML variants plus a contact-sheet review page into a
  numbered round folder.
- Conversational iteration loop: free-form feedback → next round.
- Final export: invoking the renderer to write three PNGs at the video folder
  root, ready for YouTube upload.

**Out of scope:**
- Designing the channel's visual signature (one-time exercise, already complete
  — see §4 of this spec).
- Picking a winner from the three variants (the user judges; YouTube's A/B
  test mechanism does the actual measurement).
- Uploading thumbnails to YouTube.
- Generating thumbnails for content other than hyper-frames videos (the skill
  reads `script.md`; standalone use would need a different entry point).

## 3. Inputs and outputs

### Trigger conditions

The skill activates whenever the user asks for a thumbnail for a hyper-frames
video — phrases like "make a thumbnail for this video", "I need thumbnails",
"generate thumbnail variants for `videos/<slug>-<date>/`", or starts a
thumbnail-related task that references a video folder. The user does **not**
have to be inside the video folder; they can invoke the skill from anywhere
(typically the repo root) and pass the target folder as part of the request.

### Resolving the target video folder

The skill resolves a target video folder before doing anything else, in this
priority order:

1. **Explicit path in the user's message.** If the user's message contains a
   path like `videos/<slug>-<date>/` (relative or absolute), use that.
2. **CWD match.** If the current working directory itself matches
   `**/videos/<slug>-<date>/`, use that.
3. **Ask.** If neither resolves to a real directory, ask the user which video
   folder to work in. List existing `videos/*` folders to make the choice
   concrete.

The resolved path is converted to an absolute path and used for every
subsequent file read and write. The skill does not depend on CWD after this
step; the renderer is invoked with absolute paths too.

### Inputs (read by the skill at invocation)

Once the target folder `<video-dir>` is resolved:

- `<video-dir>/outline.md` — the H1 is the working topic/title
  ("# <topic> — 9-beat outline" per the script-writer's format). Primary
  source for the title fed into the rephrase step.
- `<video-dir>/script.md` — the prose body (per-beat sections delimited by
  `<!-- BEAT N: ... -->` comments). Used to mine candidate nouns for icon
  picking and accent-word selection.
- If `outline.md` is missing or its H1 isn't a usable working title, the
  skill asks the user for the title and a 2-line topic summary before
  continuing. If `script.md` is missing, the skill warns but proceeds (the
  rephrase step still works on the title alone; icon/accent picks just have
  less context to draw from).

The thumbnail text is a *rephrase* of the working title (per the research's
rephrase pattern), so it does not need to match the final YouTube title
verbatim — those are different artifacts and are explicitly allowed to
diverge.

### Outputs (written by the skill per round)

```
videos/<slug>-<date>/
└── thumbnails/
    └── round-N/
        ├── a.html
        ├── b.html
        ├── c.html
        └── contact-sheet.html
```

Round number `N` is computed as `max(existing round-* dirs) + 1`. Rounds are
never overwritten — feedback like "go back to round 2's variant A" must remain
satisfiable.

### Final outputs (written on approval)

```
videos/<slug>-<date>/
├── thumbnail-a.png    # 1280×720, ready for YouTube A/B upload
├── thumbnail-b.png
└── thumbnail-c.png
```

PNGs are produced by `tools/thumbnail-render/` from the most recent round's
HTML files.

## 4. Visual signature — locked

These constants are baked into `templates/styles.css` and documented in
`reference/visual-signature.md`. They do not vary per video. Changing them is a
rebrand decision, not a per-video parameter.

| Constant | Value | Reasoning |
|---|---|---|
| Font | `JetBrains Mono`, weight 800 (ExtraBold) | Code-feeling without copying Pawel's bitmap font; monospace evokes terminals; ExtraBold survives at thumbnail grid size. |
| Background | `#1A1410` (espresso brown) | Differentiates from Pawel's pure black and the cool-blue dark thumbnails common on tech YouTube. Warm dark reads as "scholarly" rather than "techbro." |
| Accent color | `#FFB627` (amber) | High contrast against espresso; warm complement; not red (which is Pawel's). Reserved for the curiosity noun(s) per §7 below. |
| Text color | `#F5E6D3` (warm off-white) | Off-white instead of pure white reads as paper/print, reinforces the "scholarly" register. |
| Icon style | Lucide line icons, stroke-width 8 in a 24×24 viewBox, accent-color fill on exactly one detail | Real SVG (not styled text). Accent on one detail only — the lock body, not the shackle; the second "A", not both. |

The visual signature was chosen via a one-time design pass on 2026-05-08
during the brainstorming session that produced this spec. Rationale and
alternatives considered are in the `reference/visual-signature.md` file (to be
written during implementation).

## 5. Architecture

Two artifacts, separated along a clean line:

### `tools/thumbnail-render/` — mechanics (brand-agnostic)

A small Node project that knows nothing about our channel's brand. It owns:
- HTML → PNG rendering via Playwright headless Chrome at exact 1280×720,
  device pixel ratio 1, with explicit `document.fonts.ready` await before
  screenshot (otherwise web-font fallback shows in the PNG).
- An optional dev preview server with auto-refresh, for long iteration
  sessions.
- A version-pinned cache of Lucide SVG bodies in `icons/lucide.json`, refreshed
  via `pnpm run sync-icons`.

If we later swap render engines (Playwright → Puppeteer → satori) or change
brand, this tool barely changes — the skill is what holds the opinions.

### `.claude/skills/thumbnail-creator/` — judgment (channel-specific)

The skill owns:
- The locked visual signature CSS.
- The HTML templates (one variant, one contact sheet).
- The recipes for generating thumbnail text, picking accent words, picking
  icons, and interpreting iteration feedback.
- The orchestration loop in `SKILL.md`.

### Why split

The narration-map tool already follows this pattern (`tools/narration-map/` is
a separate uv project; the skill that uses it is judgment-only). Splitting
keeps the skill focused on per-video decisions and lets the renderer evolve
independently.

## 6. File layout

### Skill

```
.claude/skills/thumbnail-creator/
├── SKILL.md                          # orchestration entry point (~250 lines)
├── templates/
│   ├── variant.html                  # single-variant template
│   ├── contact-sheet.html            # 3-up review page with grid-size simulation
│   └── styles.css                    # the LOCKED visual signature
└── reference/
    ├── visual-signature.md           # constants + reasoning + rebrand process
    ├── text-rephrase-recipes.md      # title → punchier thumbnail text
    ├── red-word-recipes.md           # accent-word selection rules
    ├── icon-picking.md               # Lucide lookup + hand-coded SVG fallback
    └── iteration-recipes.md          # feedback interpretation patterns
```

### Tool

```
tools/thumbnail-render/
├── package.json
├── README.md
├── bin/
│   ├── render.mjs                    # CLI: HTML → PNG
│   └── serve.mjs                     # CLI: dev server with auto-refresh
├── src/
│   ├── render.mjs                    # core Playwright logic
│   └── server.mjs                    # core dev-server logic
└── icons/
    └── lucide.json                   # version-pinned cache of SVG bodies
```

### Per-video output

Already specified in §3.

## 7. Skill workflow (per invocation)

1. **Resolve the target video folder.** Use the path from the user's message
   if provided, otherwise the CWD if it matches `**/videos/<slug>-<date>/`,
   otherwise ask. Convert to an absolute path; all subsequent reads and
   writes use that absolute path. Read `<video-dir>/outline.md` for the
   working title (its H1) and `<video-dir>/script.md` for the prose body.
   If `outline.md` is missing or its H1 isn't a usable working title, ask
   the user for the title plus a 2-line topic summary before continuing. If
   `script.md` is missing, warn and continue with title-only context.

2. **Identify the title source.** The working title (from `outline.md`'s H1)
   is the *input* to the thumbnail-text generation step — not the thumbnail
   text itself. Per the research, the thumbnail text is a punchier rephrase
   of the title, not a copy of it. The thumbnail text and the final YouTube
   title are allowed to diverge.

3. **Generate three thumbnail-text rephrases** per `reference/text-rephrase-recipes.md`.
   Each variant must:
   - Be 7–11 ALL CAPS words.
   - Break into exactly 3 rows.
   - Read as a punchier, more declarative claim than the video title.
   - Fit cleanly in JetBrains Mono ExtraBold at decent size — words like
     "RENDERING" set a width budget per row.

4. **Pick accent words per variant** per `reference/red-word-recipes.md`:
   - Tier 1 (always accent): the topic noun the viewer doesn't know yet.
   - Tier 2 (often accent): the verb/adjective that creates tension with that
     noun.
   - Tier 3 (never accent): connectors (IS, VS, IN, BE, EXPLAINED, MUST).
   - Cap: two accent regions per variant. Three would dilute the signal.

5. **Pick the Lucide icon** per `reference/icon-picking.md`. One icon, shared
   across all three variants. The icon names the topic statically — no
   diagrams, no comparisons, no arrows. Apply the accent color to exactly one
   detail of the icon.

6. **Render the HTML.** Compute the next round number. Fill `templates/variant.html`
   three times and `templates/contact-sheet.html` once. Write to
   `videos/<slug>-<date>/thumbnails/round-N/`.

7. **Print the contact-sheet URL.** Tell the user to open
   `file:///.../thumbnails/round-N/contact-sheet.html`. The contact sheet shows
   each variant at full 1280×720 plus a small grid-size simulation
   (~210×118 px) so legibility at the actual feed size is visible.

8. **Iterate.** Receive free-form feedback. Interpret per
   `reference/iteration-recipes.md`. Generate the next round. Loop.

9. **Final export.** When the user signals approval ("ship it", "export",
   "done"), invoke the renderer with absolute paths so it works regardless
   of CWD:

   ```bash
   node <repo-root>/tools/thumbnail-render/bin/render.mjs \
     <video-dir>/thumbnails/round-N \
     --variants \
     --out-dir <video-dir>
   ```

   Writes `thumbnail-a.png`, `thumbnail-b.png`, `thumbnail-c.png` into the
   target video folder. Print the upload-ready absolute paths.

## 8. Tool CLI surface

```bash
# Render one HTML file to a PNG at exact 1280×720
node tools/thumbnail-render/bin/render.mjs <html-path> --out <png-path>

# Render all three variants from a round folder in one call
node tools/thumbnail-render/bin/render.mjs <round-dir> --variants --out-dir <video-folder>
# expects a.html, b.html, c.html in <round-dir>;
# writes thumbnail-{a,b,c}.png to <out-dir>

# (Optional) dev server with auto-refresh for long iteration sessions
node tools/thumbnail-render/bin/serve.mjs <round-dir> --port 4567
```

The renderer must wait for `document.fonts.ready` before screenshotting.
Without this, web-font requests resolve after the screenshot fires and the PNG
shows fallback fonts. This is a real footgun and goes in the tool's README.

## 9. Reference files (skill-side)

### `reference/visual-signature.md`

Documents the locked constants (font, background, accent color, text color,
icon style) with the *why* for each — what was deliberately chosen *not* to do
(Pawel's bitmap font, pure black, coral red, white-line-with-red-dot icons)
and which research insight drove the alternative. Includes the rebrand
process: changing these constants is a rebrand exercise that re-runs the
visual-signature design pass; do not change them per video.

### `reference/text-rephrase-recipes.md`

Patterns for turning a video title into bolder thumbnail text:

- Softer → harder: "is intentionally" → "must"; "can be" → "is".
- Question → declarative: "Why is X complicated?" → "X IS INSANELY DIFFICULT".
- Narrow → sweeping: "generates secure keys" → "secures the internet".
- Adjective upgrade: "complicated" → "insanely difficult"; "fast" → "brutal".
- Width constraint: must fit in JetBrains Mono ExtraBold across 3 rows of
  ~13–14 monospace characters each at the target font size; the rephrase step
  treats this as a hard constraint.
- Anti-patterns: no question marks, no ellipses, no colons, no parentheses,
  no adverbs other than for emphasis.
- Annotated examples drawn from the research (3–4 title→thumbnail rewrite
  pairs).

### `reference/red-word-recipes.md`

The accent-color rules from research §5: tier system, two-region cap, three
sub-patterns (topic-only, contrast-pair, tension-pair), examples table. Plus a
practical "if in doubt, mark only the topic noun" fallback.

### `reference/icon-picking.md`

- Lucide first. Look up by topic noun, not insight.
- Lookup table of common technical topics → Lucide icon names (database,
  password → lock, file format → file-text, terminal, network, randomness →
  dice-5, etc.).
- Accent-color application rule: exactly one detail of the icon, never the
  whole icon.
- Fallback: if no Lucide icon fits, write a tiny hand-coded SVG. Keep it
  simple, geometric, in the same line-icon style. Example: the "Aa" glyph for
  text-rendering videos when no Lucide letter pair exists.
- Reuse is fine. If two videos share a topic family, they can share an icon —
  the research showed Pawel reuses database+lightning across videos.

### `reference/iteration-recipes.md`

Free-form feedback → action mapping. Examples:

| User says | Skill does |
|---|---|
| "B is good but bolder text" | Keep B's wording; regenerate A and C with bolder rephrases. New round. |
| "All three feel safe" | Regenerate all 3 with rephrase recipes pushed harder. |
| "A's words but B's icon" | New round with mixed pick. |
| "Round 2's A was best" | Re-emit round 2's A as the new round's anchor; regenerate B and C against it. |
| "Try with PASSWORD as accent instead of HASHING" | New round, edit accent map only. |
| "Done, ship it" | Run final export. |

Plus heuristics: when "punchier" is asked, push verb strength + claim size +
adjective intensity. When "safer" is asked, fall back to formula pattern
("TOPIC EXPLAINED IN N MINUTES"). Default to a new round; only edit-in-place
when the user explicitly says so. Ask one short clarifying question only when
the feedback is structurally ambiguous.

## 10. Hard rules and invariants

These rules are always in effect, embedded in `SKILL.md`:

- Exactly 7–11 words per variant.
- Exactly 3 rows of text per variant.
- ALL CAPS, always.
- Maximum 2 accent regions per variant.
- No question marks, ellipses, colons, parentheses, emoji, arrows, drop
  shadows, or gradients on the thumbnail.
- The icon names the topic statically. Never the insight, never a
  before/after, never a comparison.
- The visual signature constants do not change per video.
- The skill never picks a winner from the three variants. The user judges;
  YouTube's A/B mechanism measures.
- Termination: the loop ends when the user says "ship it" / equivalent. The
  skill never declares "this is good enough" on its own.

## 11. Pre-flight check

The first invocation needs the visual signature already locked. If
`templates/styles.css` is empty or `reference/visual-signature.md` does not
exist, the skill must refuse to run with a clear message: "Visual signature
not yet locked. Run the visual-signature design exercise first." This avoids
producing thumbnails with default browser fonts on a placeholder background.

For the implementation following this spec, the visual signature is **already
locked** (the values in §4) and gets baked into `templates/styles.css` as part
of the implementation plan.

## 12. Known footguns

- **Web font loading in headless Chrome.** Must `await document.fonts.ready`
  before screenshotting, or the PNG falls back to default fonts. Goes in the
  tool's README.
- **Lucide icon drift.** Pin the Lucide version in `package.json`; commit
  `icons/lucide.json` so upstream icon changes don't silently change our
  thumbnails.
- **JetBrains Mono is wide.** Long words like "RENDERING" or "INSANELY" set
  a per-row width budget. The text-rephrase step must treat width-fit as a
  hard constraint, not an afterthought; the renderer should not silently
  shrink text to fit (that produces dishonest preview-vs-output drift). If
  no rephrase fits, the skill asks the user for a shorter wording rather
  than guessing.
- **Round-folder collisions.** Round number is derived from existing
  `round-*` directories. If the user manually deletes round 2 mid-session,
  the next round is `round-3` (not `round-2`); the skill should detect gaps
  and pick `max + 1`, not `count + 1`.

## 13. Out-of-scope future work

- A "winner picker" pass that asks the user to rank the three after upload
  and records the winner for future videos to learn from. Useful once we have
  10+ videos shipped.
- Shorts-format (9:16) thumbnails. The current template is 16:9 only.
- Multi-channel branding (e.g., a second locked signature for a sub-channel).
  Would require parameterizing the visual signature, which we explicitly
  rejected during brainstorming.
- Auto-uploading the three PNGs to YouTube via the YouTube API.

## 14. Implementation order (for the writing-plans skill that follows)

1. Build `tools/thumbnail-render/` first — it has no dependencies on the skill
   and can be tested with a hand-written HTML file.
2. Write `templates/styles.css` with the locked B signature constants.
3. Write `templates/variant.html` and `templates/contact-sheet.html`.
4. Write the five reference files.
5. Write `SKILL.md` with the orchestration loop + frontmatter.
6. End-to-end test: invoke the skill from inside
   `videos/why-text-is-hard-2026-05-07/` (the existing video folder) and
   confirm the produced thumbnails are usable.
