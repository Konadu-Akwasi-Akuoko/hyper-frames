# Iteration 3 — grading (Opus pass)

**Run graded:** session `faf29741` — `video-director` re-authored **sentences 1–5** of
`javascript-the-king` against the **imagery-pushed skill** (iteration-3's tuning deliverable).
Three scene blocks (`01-hn-quote`, `02-loved-vs-runs`, `03-origin-question`), wired with the
overlap/alternating-track convention, lint + inspect green, its own Sonnet visual-QA loop
(passed 13/14).

**Graders:** Opus (this pass, below) + human (the repo owner). Judged against `design.md` and
taste, **not** by similarity to any prior render.

**Bias control:** authored in a separate session that saw the tuned skill + the transcript —
not this grade or the change wording. This session graded but did not author.

**Frames:** `frames/` — a fresh sweep at settled beats and **both seams** (11.4s for 01→02,
21.4s for 02→03), apples-to-apples with the iteration-2 sweep.

---

## Structural layer (deterministic)

- `npx hyperframes lint` → **0 errors, 0 warnings**.
- `npx hyperframes inspect` → **ok: true, 0 issues** at every beat **and both seams** (no
  overflow, no clipped text).
- The session's own Sonnet PNG review passed **13/14**.

Mechanics are not the problem this iteration. Lint, inspect, and seams are all clean — the
failure is entirely on the visual/imagery axis.

---

## Verdict: the imagery push failed — zero images rendered despite the dedicated tuning

Iteration 3 was built to make imagery *show up* (image-sourcer agent + Step D signal-list
default + referent routing + box-on-failure). It did not. All five beats across all three
compositions rendered as type/CSS — **no `<img>`, no Iconify, no Wikimedia, only inline
decorative SVG and a CSS-drawn "Y" square**. The two beats with genuine, gate-passing
referents — the real Hacker News logo and a data-center photo for "runs the world's
infrastructure" — were both declined. The human grader (repo owner) reports he **never saw an
image** and flagged the HN-quote frame as "off — the iteration-2 problem persists." Both are
confirmed below.

### Finding-by-finding (the six from iteration 1, carried through iteration 2)

| # | Finding (iter-1) | Iter-3 result | Evidence |
|---|---|---|---|
| 1 | Generic dark-grid background | **Held (Fixed)** — toned, drifting substrate, no logo; rationed JS-yellow glow felt not pointed at | yellow radial glows on near-black across `frame-04`, `frame-09` |
| 2 | Every scene the same centered card | **Held (Fixed)** — three distinct archetypes, none adjacent alike: quote **card** → split-contrast **pivot** → full-bleed **kinetic type** | `frame-00/01` vs `frame-05/07` vs `frame-12/13` |
| 3 | No real imagery (cutouts, photos, logos) | **STILL OPEN** — and now open *despite a dedicated push*. Zero sourced assets; 2 of 5 beats had gate-passing referents, both declined | no `<img>`/Iconify/Wikimedia anywhere; `frame-01` (HN logo hand-built in CSS), `frame-07` ("infrastructure" as a bare yellow word) |
| 4 | Flat motion | **Held (Fixed)** — idle sine drifts throughout, a genuine reflow pivot in scene 02, word-by-word kinetic build in scene 03 | `frame-05`→`frame-07` reflow; `frame-10`→`frame-13` build |
| 5 | Scene 2→3 seam collision | **Held (Fixed)** — at **21.4s** (iter-1's exact collision frame) the stage is empty substrate, no two text layers share the seam; 01→02 seam (11.4s) equally clean | `frame-09` (zero text) vs iter-1 collision |
| 6a | Scene 02 reorder (payoff = hero, concession recedes) | **Held (Done well)** — danger strike crosses out "loved," divider draws on "but," payoff promoted to bright JS-yellow hero | `frame-06/07` |
| 6b | Scene 01 reaction beat | **STILL OPEN** — scene 01 stays an all-type card; no reaction treatment, and the verbatim human quote is in Inter, not the reserved Excalifont | `frame-00/01/02` |

The two critical rows are **#3 (real imagery)** and **#6b (scene-01 human-voice / reaction)**.
Both were the explicit targets of the iteration-3 tuning, and both are **still not done**. The
push did not move them.

---

## Per-scene

| Scene | Frames | Verdict | Note |
|---|---|---|---|
| 01 — HN quote | `frame-00/01/02/03` | **weak** | Centered comment card — the safe iteration-2 default, unbroken. Ignition choreography is clean and well-anchored (`awful`/`escaped`/`infiltrated` land on the spoken words), but two design-system violations: the verbatim human quote renders in **Inter, not the reserved Excalifont** (design.md names this the canonical Excalifont case), and the YC mark is **hand-built in CSS** (#ff6600 square + bold Inter "Y") instead of the real sourced logo. The human voice is missing — this is exactly why it collapses into the generic system-voice card. |
| 02 — loved vs runs | `frame-04…08` | **good** | The reflow pivot is real and well-earned; palette discipline tight (soft concession, danger strike, JS-yellow rationed to 2026 + "infrastructure"). One flag: "runs the world's **infrastructure**" — the single biggest concrete-image opportunity in the batch — rendered as a bare yellow word with a bloom, not the data-center/server-rack referent photo. The word ignites yellow but shows nothing of what infrastructure *looks like*. |
| 03 — origin question | `frame-09…13` | **strong** | Full-bleed kinetic type with a real three-tier brightness ramp; the "JavaScript" accent ignition (rationed yellow + bloom) lands precisely on the word. No verbatim quote here, so all-Inter is correct — no overfit. The only nit: Q1 settling to muted `#7a8493` sits at the edge of the muted-never-narration rule; a hair brighter would be unambiguously in-spec. |

No overfit anywhere — sentences 4–5 (the abstract pivot question, "How did JavaScript come to
be?") correctly stayed as type, and no gratuitous faces appeared. The failure is purely
*under*-imaging, not over-imaging.

---

## The imagery push failed — why

**Failure class: judgment, not detection, not mechanism.** This is the decisive diagnostic for
iteration 4.

The author *detected* the imagery content. On scene 01 the thinking explicitly named the irony
signal ("The irony of 'awful language' is the signal I'm working with") and the HN source. On
scene 02 the "infrastructure" beat was consciously authored. The signals were *seen*. They were
then **consciously routed away from imagery** to a typographic lighting mechanic: scene 01's
thinking reads "The quote itself is the design — no side imagery needed, just a framed
typographic treatment," and the final report concludes "no asset boxes to catalog — just
typographic elements throughout." Image-sourcer was **never dispatched** (the only three Agent
calls in the session are general-purpose Sonnet visual-QA reviewers). Nothing was attempted and
failed — the box-on-failure path was never even reached. So this is not a wiring bug and not a
detection miss.

The mechanism that defeated the tuning: **Step D has two halves, and the author engaged only
one.** The archetype-variety half (card → split → kinetic, no repeats) was run rigorously and
produced the three good distinct scenes. The imagery-as-default half (the tuned signal list:
named-emotion / irony-punchline / human-reaction / named-who / concrete-recognisable-thing →
declare a box) was **never run as an explicit test**. Because an author can fully satisfy
Step D through archetype variety alone, the imagery-signal check is silently skippable. The
iteration-3 PUSH added more signals and more routing, but a louder default that can be bypassed
without an auditable step gets bypassed.

**The concrete missed candidates:**
- **HN logo (sentence 2, `kind: logo`)** — the real Hacker News / Y Combinator mark is a
  recognisable-on-sight referent that authenticates the source; it passes the 3-part gate. The
  scene **hand-built a weak CSS YC mark** (orange square + Inter "Y") instead of sourcing the
  real Iconify/Wikimedia logo. `frame-01`.
- **"runs the world's infrastructure" (sentence 3, `kind: photo`)** — the textbook
  Wikimedia data-center photo, cited *by name* in `assets-and-media.md` as a worked "yes" case.
  Rendered as the bare yellow word "infrastructure." `frame-07`.
- **Scene-01 human voice / reaction (#6b)** — the disgust beat ("awful," "infiltrated") is a
  borderline reaction candidate the quote-card legitimately covers, but the *real* defect under
  it is the Excalifont type-role miss (below).

**Iteration-4 lever (from this failure class):** because the signal list is being *seen and
overridden*, do **not** add more signals — that treats a detection problem the eval shows we
don't have. Instead, **raise the bar for declining**: force an auditable, per-chunk
imagery-signal decision that must be *quoted back*, exactly like the existing chunk-quoting
requirement. A required one-liner per chunk — *"imagery signals present? → declare a box, or
text-only because \<named candidate explicitly weighed and rejected\>"* — converts the silent
skip into a visible, gradable step. The author would then have to write "HN logo weighed,
rejected because ___" rather than never weighing it at all. The point is to make text-only a
*justified exception against a named candidate*, not a default the archetype-variety pass lets
you reach for free.

---

## The "off" frame (the human's complaint)

The human flagged the fully-revealed HN-quote frame (`frame-02/03`) as off and "the
iteration-2 problem persists." The imagery judge confirms it is off on **two** design-system
counts — and notably, the worst one is **not** the missing image:

1. **Typography (the worst miss).** The quote body is set in **Inter** (`#s01 .body` inherits
   the body `Inter, system-ui, sans-serif`), but design.md names sentence 1 as **the canonical
   Excalifont case** — Excalifont is reserved for verbatim human quotes, and this *is* one.
   Rendering a verbatim Hacker News commenter quote in the generic authority-voice sans
   mis-assigns the type role: the human quote does not *look* human. This is precisely
   iteration 2's "human quote doesn't look human" problem, unfixed.
2. **The fake YC logo.** `#s01 .src .mark` is a CSS-drawn orange square with a bold Inter "Y" —
   an *approximation* of the Y Combinator mark, not the real sourced logo. It looks
   homemade/weak next to the otherwise crisp mono source row.

Layout itself is fine — a framed card is the one legitimate place for a quote, and the ignition
coloring + attribution row are well-handled. The offness is **type-role + fake-logo**, not
composition. The human's instinct is correct on both counts.

---

## Iteration-4 lever

**Single change to test next:** make the imagery decision **auditable per chunk**, not a prose
default. Require the author to emit a one-line, quoted-back imagery verdict for every chunk —
*signals present → declare a box; text-only → name the specific candidate weighed and why it
loses* — mirroring the existing transcript-chunk-quoting discipline that already works. This
targets the *judgment* failure class directly: the signal list is being seen and silently
overridden, so the fix is to make declining cost something (a named, written justification),
not to shout the signals louder.

**Bundle the Excalifont type-role check into the same per-chunk verdict** (verbatim human quote
→ Excalifont, full stop) — it is the same skippable-default failure mode and the same one-line
fix, and it is the human's loudest complaint.

**Overfit guard:** the verdict must permit "text-only, justified" as a first-class outcome, and
the worked example must stay a *beat category* (ironic payoff, named subject) never a scene
index. Success in iteration 4 is **not** "a face/photo on every scene" — sentences 4–5 staying
as clean type is correct and must remain correct. The win condition is narrow: the **two
gate-passing referents land** (real HN logo sourced, data-center photo on "infrastructure") and
the **human quote renders in Excalifont**, while non-subject nouns and abstract pivots stay
text. If faces/logos start appearing on every noun, the push went too hard and the wording
pulls back.

---

## Grade at a glance

| Axis | Grade | Shape |
|---|---|---|
| Mechanics | **A** | lint clean, inspect 0 at every beat + both seams, Sonnet 13/14, both seams resolved. Not the problem. |
| Visual design | **B** | three genuinely distinct archetypes, real reflow + kinetic motion, toned substrate, tight palette discipline. Held all of iteration 2's wins. Docked for the Excalifont type-role miss on the human quote. |
| Imagery | **D** | the push's headline target — zero images rendered; 2 of 5 gate-passing referents declined; HN logo faked in CSS; image-sourcer never dispatched. The dedicated tuning did not move the needle. Judgment failure: signals seen, consciously overridden. |

The skill is the unit under test. The iteration-4 finding generalizes: a louder default that an
author can satisfy through an adjacent pass (archetype variety) gets bypassed — the fix is an
**auditable, justification-on-decline step**, not more signal volume.
