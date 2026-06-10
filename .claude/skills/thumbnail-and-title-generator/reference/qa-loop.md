# Subagent QA loop — score before ship

Standing rule: **never report a thumbnail without verifying it, and always make
the verification SCORE.** A render that looks fine in your head is not verified.
Self-verify with your own eyes first, then spawn a subagent scorer; ship only
when both agree.

Load this at the review step, after a round's PNGs render and before printing
the contact-sheet URL.

## The two-tier model

- **Sonnet to iterate.** While converging — fixing edges, nudging the pointer,
  rebalancing contrast — spawn a Sonnet scorer per variant. Cheap, fast, and
  harsh enough to catch the artifacts that matter.
- **Opus to verify.** Before final export, re-score with Opus ("so we don't
  make mistakes"). The Opus pass is the gate the final PNGs must clear, not a
  formality.

Spawn one agent per variant, in parallel. Give each the concept, the absolute
file path to the PNG (not the HTML), and the checklist below verbatim — with
item A flagged as priority.

## Self-verification first (do not skip)

Run this before you score, every round. Skipping it once produced "abysmal"
output — faces that were not even rendering, because a hung `remove-background`
download silently produced an empty cutout and nothing in the workflow caught
it until a human looked.

1. **Read the PNG yourself.** Actually look at the rendered file. Confirm the
   face rendered, the text is on-canvas, the accent reads.
2. **Crop-zoom the risky edges** at pixel scale — the cutout's alpha edge is the
   highest-risk region:

   ```bash
   magick thumb.png -crop 420x420+540+20 +repage zoom.png   # then read zoom.png
   ```

   Adjust the crop geometry to whatever edge looks suspect (the bled-right
   cutout edge, a pointer endpoint, a chip/text seam). Read the zoom.
3. **Then** spawn the subagent scorer. Never report "done" on output you have
   not looked at, and never hand a scorer a render you have not pre-checked
   yourself.

## The checklist (PASS / FAIL + one phrase each)

Give the scorer this exact list. It answers PASS or FAIL on each item with one
phrase of justification — not a paragraph.

- **A. Cutout / edge artifacts (PRIORITY).** Any matte fringe, sticker outline,
  colored halo, hard rectangular seam, or hard vertical line on the bled face?
- **B. Face blends naturally** into the base — composited, not pasted on?
- **C. Text legible at BOTH sizes** — readable at full 1280×720 AND imagined at
  ~210 px feed size? (The flanking rows and the `.mono-tell` are the first to
  die when shrunk; judge them, not just the punch row.)
- **D. No collisions / clipping** — no headline word sitting on the pointer, no
  chip overlapping text, nothing clipped at a safe-area edge?
- **E. Annotation lands ON the subject** — the precision pointer / bracket / ring
  endpoint sits on the face or the stat it marks, not in empty base space?
- **F. Color / contrast professional** — accent reads clean against the base, rim
  is soft and accent-matched (present, not a keyline)?

## Ship threshold

**>= 8/10 overall AND zero FAIL on item A.** Item A is non-negotiable: an
edge artifact fails the thumbnail regardless of the aggregate score, because a
sticker outline is the single most "this looks amateur" tell at feed size. A
9/10 with a FAIL on A does not ship — fix the edge and re-score.

Final PNGs only after the **Opus** pass confirms the threshold and your own
crop-zoom agrees.

## When the scorer over-flags

The reviewer is deliberately harsh and will sometimes fail an *inherent property*
of the source as if it were a defect — most commonly naturally blonde or warm
hair fading into the near-black base, flagged as a "halo." Cross-check against
your own crop-zoom before acting:

- If the crop-zoom shows a **colored matte fringe** distinct from the hair, the
  scorer is right — run the despill pass (see `reference/compositing.md`).
- If the crop-zoom shows the **subject's own hair color** honestly fading into
  the base, the scorer is wrong. Tell it so in the re-judge prompt and re-score.
  Do **not** mutilate the cutout chasing the flag — over-eroding the silhouette
  is worse than a faint, honest edge.

For palette or A/B-style "which reads better" questions, run **head-to-head Opus
judges** with the versions labeled neutrally ("Version A / Version B") so the
judge is not biased toward whichever was the original.

## What the QA loop never does

- **Picks a winner.** All three variants ship; the **user** judges and
  **YouTube's A/B feature** does the actual measurement. The scorer rates each
  variant against the checklist — it never says "B is best" or ranks them.
- **Declares done unilaterally.** A passing score means a variant is *ready to
  ship*, not that the round is over. The loop terminates only when the user says
  "ship it" or equivalent.
- **Reports unverified output.** No render reaches the contact sheet without a
  self-look, a crop-zoom of the risky edge, and a passing subagent score behind
  it.

## Reference

Grounded in `learnings/bucket-b-thumbnails.md` §6 (subagent scoring discipline,
the two-tier Sonnet/Opus model, the over-flag cross-check) and §8
(self-verification — Read the PNG, crop-zoom the edges, then score). Read those
sections when the loop behaves unexpectedly.
