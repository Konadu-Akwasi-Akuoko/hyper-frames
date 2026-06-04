# Story spine — the optional cross-layer note

A finished video has four craft layers — script, motion, SFX, music — and each skill,
left alone, picks its own "most important moment" independently. The result is a video
with no single climax: the motion peaks in one place, the SFX `boom` lands in another,
the music swells in a third.

The **story spine** is a tiny, optional per-video note that fixes this. It names — in
three or four lines — where the script's hook, climax, and landing actually landed, so
the downstream skills can all point at the same beats. It is written *after* the script
is approved, it records what the script already did, and it is never required.

## What it is — and is not

The story spine is **descriptive**. It records where the strongest beat landed in the
already-approved body. It is **not generative** — it does not tell any skill what to
build.

It is **not** a storyboard, a beat sheet, a scene list, or a spec. The pipeline deleted
those for a reason — see `learnings/script-writer-spec-over-restriction.md` and
`learnings/composition-spec-over-restriction.md`. If the story spine ever starts
dictating scene count, beat order, transition types, or "open a loop here," it has
become the thing those learnings warned against, and it must be deleted.

## The shape — strict

A one-line header, then **three or four bullet lines. Never more.** This is a hard
ceiling, not a guideline.

Each line names one beat that **already exists in the approved script**:

- the **hook** beat,
- the **climax / payoff** beat — the moment the hook was carved to set up,
- optionally one **mid-video re-hook** — a turn or fresh stake, only if the script
  genuinely has one,
- the **landing**, if it differs from the climax.

Each line is: a short label, a **quoted phrase from the script** (so every layer can
anchor to the same words), an optional rough transcript timestamp, and a 3–6 word
descriptive gloss of *why that beat carries weight*.

### Example — the whole file

```markdown
# why-text-is-hard — story spine

- HOOK · "It is not one white square." — the everyday object turns strange
- RE-HOOK · ~2:10 "But text is tiny." — stakes narrow to a single glyph
- CLIMAX · ~3:40 "...called rasterization" — the named mechanism withheld until here
- LANDING · "The next time you read" — hands the concept back to the viewer
```

That is the entire file. Four lines. No depth layers, no motion verbs, no per-scene
anything. It records what the script *already did*; it tells no skill what to build. If
your story spine needs a second screen, it is wrong.

## When script-writer writes it

The story spine is written **after the full script is approved end-to-end** — at the end
of Step 4c, once the hook, body, and landing are all locked. By that point script-writer
has already identified the body's strongest concrete moment (Step 4b's hook payoff) and
written the landing (Step 4c); the spine just records where the hook, climax, and
landing landed. Nothing new is decided — every decision already happened.

It is **offered, not assumed**. If the user declines, skip it — the video is not broken
without one. It is never written before the body is approved (that would be pre-decoding
the script — the exact failure mode the pipeline removed).

## How the downstream skills use it

Each of `hyperframes`, `video-director` (its SFX pass, Step H), and `audio-bed-music`
reads the story spine — *if it exists* — as **orientation, not instruction**:

- `hyperframes` — where the rhythm pattern's energy should peak and resolve.
- `video-director` Step H — confirms the `data-sfx-hook` beat and any climax `boom`
  agree with the other layers.
- `audio-bed-music` — where a layer crossfade or a bed-pullback might coincide with a
  narrative turn.

In every case the skill still makes its own decisions from the script, transcript, and
visuals. The spine confirms; it does not dictate. A video without a spine is handled by
every downstream skill exactly as before.

## Not part of the done condition

The story spine is **not** a required artifact. It is not in script-writer's done
condition. No downstream skill treats a missing `story-spine.md` as a gap, an error, or
a TODO. Most videos will not have one, and that is fine.

## Failure smell-tests — delete it if any of these are true

The story spine is safe only while it stays a tiny descriptive note. Stop and delete it
if:

- it has grown past 4 lines, or gained a line per scene;
- it names scene count, beat order, transition types, or "open a loop here";
- a downstream skill treats a missing spine as a gap or a missing input;
- script-writer writes it before the body is approved, or writes it unprompted;
- any skill's done-condition or required-input list starts referencing it.

If you catch any of these, the spine has become `expanded-prompt.md` 2.0 — the per-beat
scaffold the pipeline already learned to delete. Reset to: three or four lines,
descriptive of the substrate, optional, written after approval.
