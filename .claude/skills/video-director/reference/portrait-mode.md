# Portrait mode — authoring vertical 1080×1920 compositions

The canvas is **whatever the root `#root` host declares**, not a constant. The
default is landscape **1920×1080**; this file is the delta for **portrait
1080×1920** (Shorts / Reels / TikTok). The director detects orientation in
Step A by reading the root host's `data-width`/`data-height` (it already reads
those there) — it does **not** decide orientation. The `shorts-creator` skill
scaffolds the portrait root; the director honors it. Everything in `SKILL.md`
and the other references still applies; this file states only what *changes*
for portrait.

Portrait support is first-class in HyperFrames, not a hack: shipping registry
blocks (`tiktok-follow`, `instagram-follow`, `spotify-card`) are native
1080×1920, the `vignelli` init example is portrait, and the render reads
`data-width`/`data-height` off the root either way.

## The dimensions flip — three coordinated places

Portrait dims live in the same three coordinated spots as landscape, all
flipped:

1. **Root host** `#root`: `data-width="1080" data-height="1920"`.
2. **CSS**: `html, body { width: 1080px; height: 1920px; }` and
   `.scene { width: 1080px; height: 1920px; }`.
3. **Viewport meta**: `<meta name="viewport" content="width=1080, height=1920" />`.

And every **per-scene host** wired in Step F carries `data-width="1080"
data-height="1920"` to match the root — never the landscape literals. The
scene-local composition docs use the same flipped CSS.

Scaffold (the `shorts-creator` skill owns this, not the director): `npx
hyperframes init <short> --example vignelli` gives a 1080×1920 portrait start,
or `--example blank` then set the root dims. The director just authors against
whatever root it finds.

## Safe areas — the phone UI eats the edges

Vertical video plays full-bleed on a phone with native UI overlapping the
frame. Keep every essential element (payoff words, key graphics) inside a safe
band; decorative bleed into the danger zones is fine:

- **Top ~220px** — the clock/status bar, the "Shorts" label, and the channel
  chip can sit here. No text or payoff content; decorative bleed OK.
- **Bottom ~320px** — the video title, the like/comment/share rail, and the
  channel avatar + **Subscribe** button overlay the bottom. Keep payoff content
  out; in particular the CTA beat's on-screen "Subscribe" cue sits in the
  **upper-middle**, pointing *down* toward the real button — never in the bottom
  where it collides with the native one.
- **Right ~120px gutter** — the action rail (like/comment/share). Keep key
  elements off the far right.
- Net **title-safe** zone: roughly the central **1080×1380** band. Compose
  heroes there.

## Layout reflow — landscape archetypes rotate vertical

The archetype *families* (typographic / structural / figural / numeric,
`visual-language.md` §2) all hold; their *layout* rotates 90°:

- **Split / contrast** (landscape = side-by-side L|R) → **stacked top/bottom**.
  The contrast reads down the frame, not across.
- **Side-cutout figural** (landscape = full-height figure on one side) → the
  cutout dominates more of the tall frame; text overlays the top or bottom third
  rather than sitting beside it.
- **Stat hero / numeric** → the big number owns the vertical center; the
  supporting label goes above or below, never flanking.
- **Code reveal / diagram** → narrower column; wrap or scale code down, prefer
  fewer columns. A wide landscape diagram usually has to become a **vertical
  flow** (top→bottom arrows instead of left→right).
- **Kinetic type** → portrait's strongest archetype; large type stacked
  line-by-line fills the tall frame. Reach for it often.

Type runs larger relative to width: body rarely below ~36px, hero words
120–220px. A phone screen is small and the legibility tolerance is tighter than
landscape — the visual-QA reviewer should grade legibility harder here.

## Pacing — change the frame more often

Shorts retention is even more frame-hungry than long-form. Change the on-screen
frame every **1–2 sentences** (the WS4 hook spec, set by `shorts-creator`). The
idle drift and per-element entrances still apply — just at a faster cut cadence,
and the seam discipline matters more because cuts come quicker.

## The CTA beat — the one portrait-specific scene

The final scene is the Cleo-shape subscribe CTA (the `shorts-creator` skill
authors its *script* shape — solve the headline, open a bigger loop, end on
"…subscribe"). The director's authoring notes for that beat:

- Check the registry first: `npx hyperframes catalog --type block` →
  **`tiktok-follow`**, **`instagram-follow`**, **`spotify-card`** are native
  1080×1920. Prefer adapting one (via the `hyperframes-registry` skill) over
  hand-rolling a subscribe button.
- The on-screen "Subscribe" cue sits **upper-middle**, gesturing *down* toward
  where YouTube's real Subscribe button lives — never replace or overlap the
  native button.
- The "Subscribe" word lands on the VO's "subscribe" — pull the word timing
  from the clip transcript like any other anchor (Step C).
- Defer branding (channel name / logo) to this final beat only, matching the
  script's deferred-branding rule.

## What does NOT change

Everything else: the incremental loop, transcript-as-timing-truth, the entrance
invariant, the 0.5s seam overlap, the `scene-design-decider` dispatch, the
visual-QA loop, the SFX pass (Step H), the final reconcile + bake. Portrait is a
**layout delta**, not a different pipeline.
