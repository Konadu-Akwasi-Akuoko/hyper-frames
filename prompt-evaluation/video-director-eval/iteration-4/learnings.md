# Iteration 4 — the lever validated (auditable per-chunk verdict)

Re-author of the js-king first 5 sentences against the iteration-3 hardening, run by the
user in a fresh session (`/video-director` — agent + skill both reloaded there). Session:
`cf5af7a3-62a4-4d1b-b9a7-e4532d32f3a7`. Reviewed read-only; no Opus `/workflows` grade run
(the human called it on sight — "this looks good, let's end here").

## Result — pass on the hardening lever

The iteration-3 imagery push **failed: zero images, failure class JUDGMENT** (author saw the
signals, silently chose type; `image-sourcer` never dispatched). Iteration 4 reverses both of
that grade's defects **and** avoids the overfit failure mode the plan warned about.

| Defect (iter 3, graded D) | Iteration 4 |
|---|---|
| Verbatim HN quote rendered in **Inter** (system font) | **Excalifont** — `compositions/01-quote.html:45,51`, local `@font-face` |
| HN/YC mark **hand-built in CSS**, no image | Real SVG **sourced via `image-sourcer`** → static `assets/icons/hacker-news-logo.svg`, no runtime CDN |
| `image-sourcer` **never dispatched** | Dispatched, returned high-confidence, asset wired into the box |

## The mechanism that moved it: verdicts on the record before authoring

The author emitted all three per-chunk verdicts **before** building anything, in the exact
Step D format — the silent skip from iteration 3 became a visible, gradable decision:

- **Scene 01 (HN quote)** → `box: class=logo referent="Hacker News"`. Quote line in Excalifont
  (the reserved human voice — the canonical case), attribution in muted JetBrains Mono.
- **Scene 02 (loved / runs the world)** → `text-only`, **candidate named**: a `class=logo`
  "JavaScript" mark, rejected because `design.md` reserves the `accent` token to mark JS itself
  (the yellow word already carries identity) *and* to ration against Scene 01's adjacent logo.
- **Scene 03 (the pivot questions)** → `text-only`, **candidate named**: a `?` glyph, rejected
  because these are the narrator's own questions with no recognisable referent and an icon would
  merely restate punctuation already on screen (gate clause 3).

This is the lever working as designed: **don't shout signals — raise the cost of declining.**
Two of three scenes still resolved to text, but each as a *named, principled* rejection rather
than a silent "the quote is the design." Declining stayed first-class; the judgment failure
class is gone.

## No overfit — the inverse failure didn't fire

The plan's explicit watch item was the swing-back: a logo/face stamped on every noun. It didn't
happen. Only the one beat where the referent **is** the subject and is recognisable on sight (the
HN source mark) got an image; the abstract pivot and the JS-identity beat stayed type, with the
`accent` token deliberately rationed so the JS mark and the HN mark don't double up on adjacent
scenes. The 3-part gate held under the new pressure.

## Honest scope caveat — what iteration 4 did *not* exercise

The iter-3 prediction named **two** gate-passing referents to watch: the HN logo *and* "a real
photo on the concrete-subject beat." Sentences 1–5 contain **no concrete-place/object beat**, so
only the logo path was actually tested. The Wikimedia-photo routing and the `class=photo` verdict
remain **unproven in practice** — validated only in the multi-shot bank, not in a real author run.
First real photo beat (later in the script, or a future video) is still the test for that path.
Likewise `class=reaction` (Pinterest cutout) is untested end-to-end here.

So: the **logo half** of referent imagery + the **type-role** fix are validated on real output;
the **photo / reaction** halves are still bank-only. One sourced referent is a pass on the lever,
not a full proof of the routing matrix.

## What carried the win (kept, don't touch)

- The **auditable per-chunk verdict** in Step D (the structural fix — converted a skippable check
  into a quoted-back, gradable step, mirroring Step B's chunk quote-back that already worked).
- **`reference/decision-examples.md`** — the multi-shot bank; the named-rejection discipline in
  Scenes 02/03 reads straight off the `text-only` examples there.
- The **Type-role fidelity** rubric bullet in `verify-and-preview.md` (closed the Excalifont gap).
- Unchanged working halves: signal list, 3-part gate, archetype variety, `image-sourcer.md`.

## Still open (deferred, post-eval, user-approved before any edit)

1. **`<template>` vs full-doc sub-comp** wording — plugin skill says `<template>`, project says
   full HTML docs. Parked in memory (`deferred-reconcile-subcomp-template-conflict`). The eval is
   now closed, so this is safe to reconcile when the user wants.
2. **The video-folder `CLAUDE.md` / `design.md` soft-contributor finding** (read-only analysis,
   prior turn): neither *forbids* imagery, but `CLAUDE.md`'s Project Structure omits `assets/` and
   `design.md` is 100% typographic with no imagery vocabulary — an ambient "type-only" frame. Not
   the graded root cause (that was judgment, now fixed), but giving `design.md` a short **Imagery**
   section and aligning `CLAUDE.md` with `AGENTS.md` would reinforce the skill fix. Candidate
   follow-up, nothing changed yet.
3. **Photo / reaction routing** still needs a real author run to validate (see scope caveat).
