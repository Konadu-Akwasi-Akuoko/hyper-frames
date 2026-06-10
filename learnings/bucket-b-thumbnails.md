# Bucket-B (face/still) thumbnails — playbook + session handoff

End-to-end method for building high-CTR "Bucket-B" YouTube thumbnails (a large
emotional face/character bled to one side, bold 2-tone punch text, a hand-drawn
accent + arrow, a brand chip) — distilled from the session that rebuilt the
thumbnails for `videos/javascript-the-king-programming-languages-2026-05-15/`.

This was the **session handoff** from the navy/coral Bucket-B prototype. **It is
now historical** — see the status note below.

> **STATUS — 2026-06-10: DONE + SUPERSEDED.** The "Next phase" (§15) is complete.
> A corpus study (11 channels, 319 thumbnails) ran, and the resulting signature —
> **"Specimen"** (green-near-black base + an accent *palette* + a 2-tone headline
> + a monospace stat tell + a *precision* inline-SVG pointer) — is now **baked
> into the `thumbnail-and-title-generator` skill**, which IS the channel's live
> thumbnail + title generator. The navy/coral system this doc describes was the
> prototype that led there.
> **Canonical now:** `.claude/skills/thumbnail-and-title-generator/` (esp.
> `reference/specimen-signature.md`) + `research/thumbnail-title-corpus-2026-06-09/ANALYSIS.md`.
> Still valid here: the compositing recipes (§4 defringe/despill, §5 rim-light,
> §10 source rules) — also lifted into the skill's `reference/compositing.md`.

---

## 0. Why this exists (the problem we were solving)

- The JS-king video had **2,200 impressions, 1.2% CTR**. Reach was fine; the
  **click-rate was the bottleneck**. (Impressions/CTR are Studio-UI-only — not
  in the public Analytics API; read them via the Studio Reach tab in Chrome.)
- The competitor `@awesome-coding` wins with **Bucket-B** thumbnails: 14 of
  their top 15 by views are face/pop-culture-still + 2-tone punch text. That is
  the proven high-CTR format we replicated.
- The project's `thumbnail-and-title-generator` skill **was** a different, locked
  text-only style ("Terminal Scholar": JetBrains Mono + Lucide icon, no faces).
  As of 2026-06-10 it has been **rebranded to the face-forward "Specimen"
  signature** — so the skill now IS this Bucket-B-family pipeline (faces, 2-tone
  headline, accent palette, precision pointer). The "separate custom HTML/CSS
  pipeline" this doc built for the JS-king video was the prototype; new videos go
  through the skill.

---

## 1. The proven pipeline

```
1. User supplies the source image (and credits it)   ← see §10
2. Cut out the subject:  npx hyperframes remove-background <in> -o cutout.png
3. DEFRINGE / DESPILL the cutout (CRITICAL — §4)
4. Compose in HTML/CSS (Bucket-B structure — §3)
5. Render to PNG via Playwright (§2)
6. LOOK at it yourself; crop-zoom the edges (§8)
7. Score with a subagent (Sonnet to iterate, Opus to verify — §6)
8. Fix the top issues, re-render, re-score. Loop until the subagent says SHIP
   (>=8/10) AND your own eyes agree.
```

Work in **round folders** so good versions are never destroyed:
`thumbnails/bucket-b/round-N/` (or named variants like `scholar/`, `final/`).

---

## 2. The render tool

`tools/thumbnail-render/bin/render.mjs` — Playwright, full-viewport 1280×720
screenshot, waits for `document.fonts.ready`, allows `file://` + network.

**Single-file mode (what we used):**
```bash
node tools/thumbnail-render/bin/render.mjs <path/to.html> --out <path/to.png>
```
Batch/variants mode also exists (`--variants --out-dir`) — that's the
`thumbnail-and-title-generator` path, not Bucket-B.

Fonts in play: **Inter** (Google Fonts `@import`, the "system" voice) and
**Excalifont** (local `woff2` `@font-face`, the hand-drawn "human annotation"
voice — used for the accent words and arrows). Excalifont is single-weight; you
cannot bold it — fake weight with `-webkit-text-stroke` + `text-shadow`.

---

## 3. Bucket-B composition structure

A shared `_shared.css` holds the system; each concept is its own `.html` with a
small `<style>` block of per-file overrides (face size/bleed, font sizes, arrow
position). Architecture:

- `:root` design tokens (see §12).
- `.thumb` — 1280×720, radial bg (soft top-left light → base → deep).
- `.grid` — faint 48px graph-paper grid, radial-masked so it fades at the edges.
  This is the "graph paper / blueprint" texture. Tint it to match the bg
  (cool grid on navy; warm cream grid on espresso).
- `.vignette` — radial darkening at the corners.
- `.face-wrap` (absolute, bled to the right edge) → contains `.face-glow` +
  `.face` (the cutout `<img>`).
- `.face` — `object-fit: contain`, plus the **rim-light filter** (§5).
- `.copy` (text column, left) → `.line` rows; `.hand` = Excalifont accent word;
  `.coral` = accent color; `.js-chip` = the JS brand badge.
- `.annot` — hand-drawn annotation text + an inline `<svg>` arrow.

**Layout rule that matters:** text sits **far-left**, face sits **far-right** —
they do not overlap, so you do **not** need any fade/scrim panel between them
(see the face-fade gotcha in §7).

---

## 4. Cutout prep — DEFRINGE / DESPILL (the biggest technical win)

`remove-background` (u2net_human_seg) leaves a **semi-transparent matte fringe**
on edges that carries the *original* background's color. On a dark thumbnail bg
this reads as a glowing **sticker outline** — the #1 "this looks amateur" tell.
A strict subagent QA fails on it every time and is right to. **CSS rim-light
glow does NOT fix it** (and an over-strong glow *adds* a fake keyline). Fix the
PNG itself with ImageMagick.

**Defringe — erode the alpha to cut the fringe off:**
```bash
magick in.png \( +clone -alpha extract -morphology Erode Disk:1.5 -blur 0x0.6 \) \
  -alpha off -compose CopyOpacity -composite out.png
```

**Despill — when a *colored* halo persists (blonde hair / red cloth shot on a
light background is the hardest case): erode harder AND darken+desaturate the
edge ring so residual warm pixels sink into the dark bg:**
```bash
magick in.png \( +clone -alpha extract -morphology Erode Disk:2.5 -blur 0x0.7 \) \
  -alpha off -compose CopyOpacity -composite t1.png
magick t1.png -alpha extract a.png
magick a.png -morphology Erode Disk:6 inner.png
magick a.png inner.png -compose Minus -composite ring.png      # ~6px edge ring
magick t1.png -modulate 32,22 dark.png                          # brightness 32%, sat 22%
magick t1.png dark.png ring.png -composite -alpha set a.png -compose CopyOpacity -composite out.png
```
(For a milder warm halo, `-modulate 52,35` over a `Disk:4` ring is enough.)

This pass took the Home Alone thumbnail from a QA 5/10 (halo) to 9/10. The
Gigachad cutout was clean enough that a single defringe (Disk:1.5) passed.

---

## 5. Rim-light ("highlight") tuning

The **rim-light highlight is desirable** (the user explicitly loved it) — it
separates the subject from the bg. But:

- **Too strong = sticker outline.** A tight, uniform, bright keyline tracing the
  whole silhouette reads as a cheap cutout. Avoid `drop-shadow(0 0 1px white)`
  style hard keylines.
- **Right = a soft, diffuse glow that fades.** What worked:
  ```css
  filter: saturate(0.84) contrast(1.14) brightness(1.05)
          drop-shadow(0 0 10px rgba(150,190,255,0.26))   /* soft cool halo */
          drop-shadow(-18px 12px 30px rgba(0,0,0,0.55)); /* dark cast shadow = depth */
  ```
- **Match the rim color to the background.** Cool blue rim on navy; warm amber
  rim on espresso. A blue glow behind a warm/blonde subject *rings* badly —
  `display:none` the `.face-glow` disc for warm-haired subjects and let the
  rim drop-shadow + dark cast shadow do separation.

---

## 6. The subagent QA loop (scoring discipline)

The user's standing instruction: **always verify with a subagent and make it
score.** Use **Sonnet** while iterating, **Opus** for the final verification
("so we don't make mistakes").

- Spawn one agent per thumbnail (parallel). Give it the concept, the file path,
  and a **strict checklist** with the highest-risk item as **item A**.
- The checklist that converged (answer PASS/FAIL + one phrase each):
  - **A. Cutout/edge artifacts** — any matte fringe, sticker outline, halo,
    hard rectangular seam, or **hard vertical line**? (priority)
  - **B.** Face blends naturally into bg (not pasted)?
  - **C.** All text legible at full size **and imagined ~210px feed size**?
  - **D.** No collisions/clipping — **no word sitting on an arrow**, no
    text/chip overlap?
  - **E.** Arrow aims correctly and **lands on the subject** (not empty space)?
  - **F.** Rim-light present + natural? Color/contrast professional?
- **Ship threshold = 8/10 AND zero FAIL on item A.** Final files only after Opus
  confirms.
- The Sonnet reviewer is **harsh and will sometimes over-flag** an inherent
  property (e.g. naturally blonde hair fading into dark = "halo"). Cross-check
  against your own crop-zoom; when it's the hair color itself, tell the reviewer
  so in the prompt and re-judge. Don't mutilate the cutout chasing a reviewer.

For palette/A-B questions, run **head-to-head Opus judges** (label versions
neutrally "Version A / Version B" so the judge isn't biased toward an original).

---

## 7. Gotchas (each cost real iterations this session)

- **The "hard vertical line top-to-bottom" = a fade/scrim panel, NOT the
  cutout.** We had a `.face-fade` navy-gradient div (`linear-gradient(90deg,
  navy 0%, transparent 42%)`) meant to darken behind text. Its **left box edge
  was a hard navy line** in the middle of the canvas. Since text and face don't
  overlap in this layout, **delete the fade panel entirely.** The transparent
  cutout's own alpha edge + rim does the separation. (User: "remove that
  blending in of the image with the background. I don't think it's needed." —
  correct.)
- **`object-fit: cover` in a fixed `overflow:hidden` box re-introduces a
  rectangle.** It zooms into the opaque center of a cutout and crops away the
  transparent border, so the subject reads as a filled rectangular photo with a
  hard edge. Display cutouts with `object-fit: contain` (height-based, bled to
  edge), not cover-in-a-box, unless you deliberately want a framed crop.
- **Arrows misplaced / words over arrows.** Arrows must visibly **land on the
  face** (cheek/chin/eyes), not stop in empty bg. Reposition the inline `<svg>`
  by its container `left/top` and lengthen the path so the head reaches the
  subject. Never let a headline word cross the arrow stroke. When an annotation
  *can't* avoid crossing text (e.g. an arrow to a number sitting under a
  headline), **drop the annotation** — a redundant flourish isn't worth a
  collision.
- **Arrow stroke colors are hardcoded in the SVG** (`stroke="#ff5c52"`), not the
  CSS var. A palette swap must `sed` the SVG hex too, not just the `:root` vars.
- **`shuf` isn't on macOS** — use `sort -R`. **yt-dlp** flat-playlist works for
  listing; full per-video extraction hits the bot-wall ("Sign in to confirm
  you're not a bot") — grab thumbnails directly from the CDN:
  `https://i.ytimg.com/vi/<VIDEO_ID>/maxresdefault.jpg`.

---

## 8. Self-verification discipline (don't skip this)

Early in the session I showed results **without** running the subagent and the
output was "abysmal" (faces not even rendering, because a piped
`remove-background` run hung on the 168MB model download and produced nothing).
The lesson the user drove home:

1. After every render, **Read the PNG yourself** — actually look at it.
2. **Crop-zoom the risky regions** to inspect edges/seams at pixel scale:
   ```bash
   magick thumb.png -crop 420x420+540+20 +repage zoom.png   # then Read zoom.png
   ```
3. Use the **grid-debug overlay** to place items precisely in x/y (the user
   stressed "use the grid to position items really well"). `_shared.css` carries
   a `.thumb.dbg` overlay: 320×240 cells + a 60px dashed safe-area border.
4. **Then** run the subagent score. Never report "done" on unverified output.

---

## 9. Palette test result (settled this session)

We A/B-tested the live **navy/coral** palette against the `thumbnail-and-title-generator`
**"Terminal Scholar"** palette (espresso `#1A1410` / warm off-white `#F5E6D3` /
amber `#FFB627`). Three head-to-head Opus judges, all three concepts:

- **Navy/coral won all three, "clear" margin.** Reasons (consistent):
  - **Cool-vs-warm beats warm-on-warm** for scroll-stopping at feed size. Navy
    ground lets coral + warm faces "detonate"; espresso-on-espresso is tasteful
    but quiet — and CTR is the whole point.
  - **Amber accent melts into the JS-yellow chip** (both yellow). worst scored
    amber/chip separation **3/10**. Coral vs yellow = two distinct hot colors.
- Espresso/amber won **premium feel** and **face integration** (warm-on-warm hid
  the weak tendays rectangle better). Keep it for non-CTR-critical surfaces
  (banner, calm evergreen). Files kept in `thumbnails/bucket-b/scholar/`.

**Decision: navy/coral for live thumbnails.**

---

## 10. Source-image requirements (what's usable vs not)

A composite can only be as good as the source. The "Confused Math Lady"
(`tendays`) concept stayed at Opus 4/10 because the source was unfixable:
**555×312 low-res TV screengrab, with a watermark, an un-keyable gray studio
background (u2net only stripped one side), and a weary — not disbelief —
expression.** No compositing fixes wrong-emotion + un-keyable + low-res.

**A usable Bucket-B source is:** high-res (ideally ≥1000px on the bled
dimension), a **clear, legible emotion** that matches the concept's beat, and a
**clean/simple background** so it cuts cleanly (or already a transparent PNG).

**Division of labor (standing rule):** the **user supplies and credits** the
source image; **I composite** it (cut out, defringe, bleed, rim, text). I do
**not** go source third-party copyrighted imagery myself.

---

## 11. Title pairing

Thumbnail and YouTube title do **different jobs** — never make the title a
sentence-cased copy of the thumbnail. Thumbnail makes the bold CLAIM; the title
is the grounded, searchable version carrying the topic noun ("JavaScript").
Sentence case, 40–70 chars. The three we wrote:

- escape → *Why you can't escape JavaScript anymore*
- worst → *JavaScript is the worst language — and it still won*
- tendays → *JavaScript was built in 10 days. Now it runs the world.*

---

## 12. Design tokens (navy/coral Bucket-B, the live system)

```css
--navy:      #121a2e;   /* bg base */
--navy-deep: #0b1020;   /* bg deep / corners */
--white:     #f4f6fb;   /* headline text */
--coral:     #ff5c52;   /* accent: hand words + arrows */
--js:        #f7df1e;   /* JS brand chip (logo) */
--ink:       #0b0d12;   /* dark glyph on the JS chip */
```
(Grid lines `rgba(150,180,240,0.11)`; rim glow `rgba(150,190,255,0.26)`.)

---

## 13. Current state of the JS-king thumbnails

In `videos/javascript-the-king-programming-languages-2026-05-15/thumbnails/bucket-b/`:

- `final/escape.png` — Home Alone, "YOU CAN'T / escape / JAVASCRIPT [JS]",
  "it's everywhere" + arrow. **Opus 9/10, SHIP.**
- `final/worst.png` — Gigachad, "THE WORST / LANGUAGE / won [JS]", arrow lands
  on his cheek. **Opus 9/10, SHIP.**
- `final/tendays-DRAFT.png` — Math Lady. **Opus 4/10, needs a replacement
  source image** (see §10).
- `scholar/` — the espresso/amber palette test (lost the A/B, kept for warm
  surfaces).
- Source cutouts: `thumbnails/cutouts/` + defringed copies in
  `thumbnails/cutouts/defringed/`.

**Not yet done:** pushing escape + worst into YouTube's native A/B test (always
preview the change + unit cost and get explicit yes before any
`video_set_thumbnail` write).

---

## 14. Existing thumbnail-research infrastructure (don't rebuild)

- `research/pawel-code-stuff/` — full study of one coding channel (17
  thumbnails + `analysis/thumbnail-patterns.md`, comments, scripts). This study
  → the "Terminal Scholar" signature in
  `.claude/skills/thumbnail-and-title-generator/reference/visual-signature.md`.
- `scratch/thumbnail-compare/awesome-coding/` — downloaded awesome-coding
  thumbnails incl. a `top/` folder with **view-count-labeled** files
  (e.g. `08_157k_<id>.jpg`). This study → the Bucket-B style.
- `.claude/skills/thumbnail-and-title-generator/reference/visual-signature.md` is the
  **format** to copy for a locked-signature spec.
- `tools/thumbnail-render/` — the renderer (+ `icons/lucide.json`, Iconify
  cache for the `thumbnail-and-title-generator` path).

---

## 15. NEXT PHASE — DONE (2026-06-10)

Completed. The three scope decisions were answered (corpus = 11 user-named
channels incl. awesome-coding / Fireship / Cleo Abram + emerging peers;
differentiation = **find-the-gap-then-own-it**; execution = **multi-agent
workflows**). Gather → Learn → Synthesize ran:

1. **Gather** — 11 channels, top-by-views, **319 thumbnails** →
   `research/thumbnail-title-corpus-2026-06-09/` (cookie-authed yt-dlp at scale;
   see the updated `motion-inspo-batch-youtube-botwall` memory).
2. **Learn** — 11 parallel vision-analysts + an adversarial gap-validator →
   `research/thumbnail-title-corpus-2026-06-09/ANALYSIS.md` (saturated
   conventions vs the validated white space + the title engine).
3. **Synthesize** — designed + judge-validated the **"Specimen"** signature (beat
   the old navy/coral baseline **8.5 vs 6** across 3 Opus judges) and **baked it
   into `thumbnail-and-title-generator`**: a new `specimen-signature.md` spec,
   `styles.css`, face + 2-tone + mono + precision-pointer templates, an accent
   palette (teal default; red available but sparingly), a corpus-derived
   `title-engine.md`, the inline-SVG `annotation-kit.md` + numbered coord-grid,
   and `compositing.md` + `qa-loop.md`.

Key deltas from this prototype, all corpus-driven: **teal/palette accent, not
coral** (coral collides with awesome-coding + Pawel); **precision pointer, not
hand-scribble arrow** (the lane's single most-overused device); **green-near-black,
not navy**; **a monospace stat tell** as the ownable type signal nobody else holds.

---

## 16. Related memories / docs

- Memory: `thumbnail-bucket-b-user-supplies-images.md` (the §10 division of
  labor).
- Memory: `thumbnail-cutout-defringe-despill.md` (the §4 recipes).
- Memory: `imagemagick-montage-font-fail-use-append.md` (tile via `+append`,
  `montage` aborts on missing font on this Mac).
- `.claude/skills/thumbnail-and-title-generator/` — **now the live "Specimen"
  (Bucket-B-family) signature** (was the old text-only Terminal Scholar style).
  Canonical for new videos; this doc is the prototype it grew from.
- `research/thumbnail-title-corpus-2026-06-09/ANALYSIS.md` — the corpus study
  (gap map + title engine) that drove the Specimen design.
