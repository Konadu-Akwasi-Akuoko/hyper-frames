# Iteration 1 — grading & response

**Run graded:** session `22a836d9` — `video-director` invoked greenfield on the
**first 3 sentences** of `javascript-the-king`. It authored a substrate + three scene
blocks (`01-the-comment`, `02-never-loved`, `03-how`), wired with the 0.5s-overlap /
alternating-track-index convention, lint + inspect green, ran its Sonnet visual-QA loop.

**Graders:** human (repo owner) + Opus (this session). Per the SPEC, this is layer (c),
the ground-truth bar — judged against `design.md` and the human's taste, **not** by
similarity to the `js-king-pre-director` backup.

**Frames:** `frames/` — a fresh snapshot sweep of the three (unchanged) blocks at settled
beats, plus `seam-21.4s-collision.png` capturing the scene 2→3 seam. (The graded blocks
are unchanged on disk; the sweep is the canonical render of what was graded.)

---

## Verdict: structurally strong, visually a flat slideshow

The mechanics are good and were **not** the problem:

- State detection, greenfield resume, real word-timing anchors (no round numbers),
  lint/inspect clean, honest self-correcting QA loop (it caught and regenerated the
  scene-02 graph-paper mesh on its own). It also laid a substrate proactively and
  respected the grading-bar rule (peeked at the backup only for host mechanics).

The **visual design** is the weak axis, and it is systematic, not per-scene. Six findings.

### Per-scene

| Scene | Frame | Verdict | Note |
|---|---|---|---|
| 01 — the comment | `frame-01-at-6.5s` | ok-but-samey | Quote card reads; emphasis lands. But it's a centered muted card — the default look. Wants a reaction-image cutout (a surprised face) per the brief. |
| 02 — never loved | `frame-04..05` | flag | "infrastructure" payoff is fine, but the **cyan mesh reads as graph-paper, not infrastructure** ("does this look like infrastructure? No"). Should be a **real server image**, and the payoff line ("…runs the world's infrastructure") should move **up** as the hero; the concession line recedes. |
| 03 — how | `frame-07-at-23.3s` | ok | The pivot question works in isolation. |
| **seam 2→3** | `seam-21.4s-collision.png` | **fail** | Scene 02's full layout is still up while scene 03's "So…" fades in over it — **two legible text layers colliding**. The dual-opacity crossfade is the bug. |

### The six themed findings (the human grade)

1. **Background is generic.** A flat dark grid that says nothing. Wants a subtle
   JavaScript *tone* — a rationed yellow tint/glow that can drift and fade — **no logo**.
2. **Every scene looks the same** (centered muted text). Each scene's look should come
   from *what its sentence says*. North star: "you do you, use the sentence to denote how
   each scene looks."
3. **No real imagery.** The video needs real images/video: full-height side cutouts,
   emotion-matched to the beat, background-removed, with grain/duotone/halftone/vintage
   VFX — supplied by the user via labeled "boxes" the author fills.
4. **Motion is flat.** Reference creator (`youtube.com/watch?v=SoQ19gHEM2A`,
   studied in `../reference-study/`): cutouts slide in from the edges, **layout reflow**
   (a new element pushes existing ones rather than stacking on them), and **constant
   subtle motion** (3D tilt / 2D shake on text, cards, images).
5. **The scene 2→3 transition is broken** — the seam collision above.
6. **Concrete fixes** for the existing scenes (scene 02 reorder + real server image;
   scene 01 add a surprised-celebrity reaction to the card).

---

## Response — what changed in the skill (this iteration's deliverable)

Scope was **skill/reference + tooling only** (locked with the user); the scenes are
**not** re-authored here. The user re-authors them in a fresh session, and that becomes
**iteration 2**'s gradable batch. Every finding above maps to a generalizing change:

| Finding | Change | Where |
|---|---|---|
| 1 background tone | "background = rationed subject tone, drifting, **no logo**" rule | NEW `reference/visual-language.md` §1; pointers in `composition-structure.md` |
| 2 sameness | anti-sameness north star + **archetype menu**; "never repeat the neighbour's archetype" | `visual-language.md` §2; `SKILL.md` Step D |
| 3 imagery | **labeled asset-box** mechanism + collected **shopping list** + `assets/` convention + treatment spec | NEW `reference/assets-and-media.md`; `SKILL.md` Steps D/E/G |
| 4 motion | edge slide-ins, **layout reflow**, constant low-amplitude tilt/drift | `visual-language.md` §3; `SKILL.md` Step E; `composition-structure.md` |
| 5 seam | transition must **cover/occlude, not cross-dissolve text**; snapshot the seam | `composition-structure.md` wiring rules; `SKILL.md` Step F; `verify-and-preview.md` |
| 3/treatment | **`tools/image-prep`** — rembg BG-removal + grain/duotone/halftone/vintage presets reading `design.md` tokens | NEW `tools/image-prep/` |
| QA coverage | rubric gains seam-collision, per-scene distinctness, imagery-fit, liveliness; snapshot at `prev_end − 0.25` | `verify-and-preview.md`; `SKILL.md` Step G |

Reference study of the named creator (patterns extracted, not copied):
`../reference-study/patterns.md`.

### What iteration 2 tests

Re-author the same first sentences (or more) with the updated skill, then re-grade
(human + Opus) on a fresh snapshot sweep + the seam frame. Success = scenes look
distinct, the background carries subject tone, imagery boxes appear where beats want
them, motion reads alive, and the seam no longer mushes two text layers. Watch for
**overfitting** to these three sentences — the new guidance must read video-agnostic.
