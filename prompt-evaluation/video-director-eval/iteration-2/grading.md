# Iteration 2 — grading (Opus pass)

**Run graded:** session `77e948c1` — `video-director` re-authored the **first 3 sentences**
of `javascript-the-king` greenfield, against the **overhauled skill** (iteration-1's
deliverable). Fresh substrate + three scene blocks (`01-hn-quote`, `02-loved-vs-runs`,
`03-how-did-that-happen`), wired with the 0.5s-overlap / alternating-track-index
convention, lint + inspect green, its own Sonnet visual-QA loop.

**Graders:** Opus (this pass, below) + human (the repo owner, pending). Judged against
`design.md` and taste, **not** by similarity to the iteration-1 render.

**Bias control:** authored in a separate, clean session that saw only the skill + the
transcript — not the iteration-1 grade or the change wording. This session graded but did
not author.

**Frames:** `frames/` — a fresh sweep at settled beats **and the 21.4s seam** (the exact
timestamp where iteration 1 collided), for an apples-to-apples comparison.

---

## Structural layer (deterministic)

- `npx hyperframes lint` → **0 errors, 0 warnings** (5 files).
- `npx hyperframes inspect --at 5.0,10.8,16.3,20.4,21.45,23.8 --json` → **ok: true, 0
  issues** (no overflow, no clipped text) at every beat.

Mechanics remain clean — never the problem. This iteration tested the **visual** axis.

---

## Verdict: the flat slideshow is gone — 5 of 6 findings landed; imagery is the holdout

The iteration-1 grade was "structurally strong, visually a flat slideshow." That is no
longer true. Three scenes, three genuinely different archetypes, a toned and moving
background, and a seam that no longer mushes two text layers. The one finding that did
**not** carry through is real imagery — consciously declined, not forgotten.

### Finding-by-finding (the six from iteration 1)

| # | Finding (iter-1) | Iter-2 result | Evidence |
|---|---|---|---|
| 1 | Generic dark-grid background | **Fixed** — rationed JS-yellow glow, drifting, **no logo**. Felt, not pointed at. | warm glow top-left in every frame; `substrate.html` 0.10/0.06-opacity glows + slow yoyo drift |
| 2 | Every scene the same centered card | **Fixed** — three distinct archetypes, no two adjacent alike: quote/source **card** → split-contrast **pivot** → full-bleed **kinetic type** | `frame-00/01` vs `frame-04` vs `frame-07` |
| 3 | No real imagery (cutouts, reaction shots) | **Not exercised** — director declared all three beats "text-driven," emitted no shopping list. The asset-box mechanism was *considered and declined*, not ignored. | no `<img>`/`data-asset` in any composition; session report: "No asset boxes were used … no shopping list to fill" |
| 4 | Flat motion | **Addressed** — idle 3D tilt on the card, glow drift on substrate, and a real **reflow** in scene 02 (concession recedes left + dims as reality slides in from the right). Deterministic yoyo idles throughout. | `frame-03` (mid-reflow) → `frame-04` (settled); `s01` rotateX/Y idle |
| 5 | Scene 2→3 seam collision | **Fixed** — scrim cover/occlude. At **21.4s** (iter-1's exact collision frame) only scene 02 is legible; scene 03's text has not entered. Seam 01→02 (11.4s) equally clean. | `frame-05` (one text layer, dimming) vs iter-1 `seam-21.4s-collision.png` (two) |
| 6a | Scene 02 reorder (payoff = hero, concession recedes) | **Done well** — "it runs the **world's infrastructure**" is the bright right-hand hero with a JS-yellow underline; "never the most loved" is struck and dimmed to the left. | `frame-04` |
| 6b | Scene 01 surprised-celebrity reaction cutout | **Not done** — folded into finding #3; scene 01 stays a (well-elevated) card. | `frame-01` |

### Per-scene

| Scene | Frame | Verdict | Note |
|---|---|---|---|
| 01 — HN quote | `frame-00/01` | good, but the safest | Ghost quote mark, `▲ Hacker News commenter` source, `2014` stamp, danger-red verb ignition on *escaped*/*infiltrated* with underline. Strong — but it is the closest of the three to the old "centered card" default, and the missing reaction cutout (6b) is exactly what would have broken it out. |
| 02 — loved vs runs | `frame-03/04` | **strongest** | Split-contrast with a genuine pivot reflow. The reorder reads perfectly: concession struck + receded, payoff promoted to bright hero with accent underline. This is the scene that proves the anti-sameness guidance works. |
| 03 — how | `frame-06/07` | good | Full-bleed kinetic type, word-by-word reveal, "happen?" slams to 232px. Distinct archetype, clean, no overflow. |
| seam 2→3 | `frame-05` | **pass** | The iteration-1 failure is gone. |

---

## The one open question for the human grader: imagery

This is the single judgment call worth your verdict. The director **considered** real
imagery and chose not to use it, reasoning that a quote, a reframe, and a pivot-question
are text-centric beats. That is defensible — and it avoided pasting a face where one
didn't belong. But it diverges from two explicit iteration-1 asks:

- **#3** wanted real cutouts to appear (the asset-box → shopping-list flow exercised).
- **#6b** specifically wanted a *surprised-celebrity reaction* on the scene-01 card.

So the skill's imagery guidance is currently **"available but not pulled"** — fully
discretionary, and the director declined. The eval signal: if we want imagery to actually
show up on a hook beat, the skill may need to *push* (e.g. "an opening hook actively wants
a face/character beat — declare a reaction box unless the beat truly resists it") rather
than leaving it purely optional. The risk to weigh against that: over-prescribing faces
onto beats that are genuinely better as type. **This is the iteration-3 lever, pending the
human's call on whether scene 01 needed the reaction shot.**

### What iteration 3 would test (if imagery is the verdict)

Tighten the imagery guidance from optional to *actively-considered-on-hook-beats*, re-author,
and grade whether a reaction cutout appears on scene 01 (or another beat) **without** the
type-first scenes regressing into pasted-rectangle stock. Watch for overfitting — the push
must read video-agnostic, not "always put a face in scene 1."
