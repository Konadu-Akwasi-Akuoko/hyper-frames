# Iteration recipes

How to interpret the user's free-form feedback after presenting the
description and decide what to change.

Default behavior: **edit in place** on the same `description.md`.
The description is a single artifact, not a folder of variants — no
round-N pattern, no a/b/c. New runs only happen when the user moves
to a different video folder.

## The interpretation table

| User says | Interpretation | Action |
|---|---|---|
| "Ship it" / "done" / "looks good" / "that works" | Loop terminates | Stop the skill. Confirm the file path and clipboard state once. |
| "Tighter hook" | Hook is too long or too soft | Rewrite the first ~145 chars only. Keep everything else. |
| "Make the hook from a different line" | Hook source choice | Re-read `voiceover.txt` Beat 1 and Beat 2; offer 2 alternative hook lines and let the user pick. |
| "Explainer is too long" | Trim explainer | Cut to a single paragraph (drop the second). Keep top-3 nouns intact. |
| "Explainer doesn't say what the video is about" | Angle missing | Rewrite the second paragraph to name the specific angle (the 3-cycle structure, the named historical moments, whatever the script's spine is). |
| "Add a chapter for X" / "Missing chapter for Beat N" | Re-stamp | Re-run the chapter-stamping recipe for the missing beat opener. Insert in order. |
| "Chapter labels are too literal" | Label rephrase | Rewrite labels as more descriptive / imperative-ish. Keep timestamps unchanged. |
| "Chapter at M:SS is wrong" | Timestamp error | Re-run the filter against the transcript with a different anchor phrase. Never adjust manually. |
| "Add a source for X" | Missing citation | Fire one WebSearch for that claim. Insert the new bullet in the sources list. |
| "Drop the X source" | Trim sources | Remove that bullet. |
| "Wrong URL for X" | Bad citation | Re-fire WebSearch with a different query; replace the URL. |
| "Different hashtags" | Hashtag change | Re-derive from `signals.top_nouns[:6]` and pick 3 different ones; or ask the user which 3. |
| "Less salesy" / "less hype-y" | Tone walk-back | Soften adjectives in hook and explainer. Cut superlatives. |
| "More punchy" / "bolder" | Tone push | Sharpen verbs, cut hedges, lead with the strongest claim. |

## Heuristics for vague feedback

When the user says one word or a short phrase, apply the obvious
interpretation and ship the edit. Don't ask for clarification on
single-word feedback.

| Vague feedback | Action |
|---|---|
| "Tighter" | Trim explainer to one paragraph; cut filler words from hook. |
| "Longer" | Add a second explainer paragraph naming a specific angle from the script (a cycle, a named event, a stat). |
| "Try again" / "no" | Rewrite hook + explainer from scratch. Keep chapters and sources. |
| "Cleaner" | Drop the demand phrase if included; trim sources to 4; tighten labels. |

## When to ask vs. guess

Apply the obvious interpretation by default. Ask one short
clarifying question only when the feedback is structurally
ambiguous:

- "Reword the third chapter" with three chapters at the same beat —
  ask "the cycle-1, cycle-2, or cycle-3 chapter?".
- "Change the second source" when the source list has been reordered
  since the last view — ask the user to name the source by topic.
- "Make it like the last video's description" when there's no
  obvious last video — ask which video folder they mean.

Default: guess and ship the edit. Edits are cheap; the file is one
write away.

## Length thresholds during iteration

If an edit pushes the description over 3500 chars, print the new
length and apply the trim ladder from `SKILL.md` Step 7 before
showing the result:

1. Explainer to single paragraph.
2. Sources to top 5, then top 4.
3. Tighten chapter labels.

If the user explicitly asked for a longer explainer and the result
is now 3700 chars, that's fine — the 3500 number is a target, not a
ceiling. The 5000 cap is the only hard line.

## What the skill never does

- **Picks a hashtag set without grounding.** If SEO data is absent,
  ask the user. Never invent topic nouns to fill the slot.
- **Adjusts a chapter timestamp manually.** Always re-run the
  transcript filter. Manual rounding is the failure mode this skill
  exists to prevent.
- **Cites a URL it didn't WebSearch for.** Every URL in the sources
  section came from a search this session or a verified WebFetch.
- **Declares done on its own.** The loop ends when the user says so.

## What "ship it" means

When the user signals approval, do one final pass:

1. Confirm `<video-dir>/description.md` exists and reflects the
   latest state.
2. Confirm `pbcopy` was called with the final state (re-run the
   `printf '%s' "$(cat …)" | pbcopy` command).
3. Print one line: `description.md ready at <abs-path>; copied to clipboard.`
4. Stop. Do not offer follow-up tasks.
