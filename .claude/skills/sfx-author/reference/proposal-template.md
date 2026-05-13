# Proposal template

The exact format your cue plan must take before any HTML edit. This template
is fully fleshed; trim only the optional sections marked below.

```
SFX CUE PLAN — <video-folder-slug>
Runtime <mm:ss> · <N> scenes detected
Read design.md as: <one-line characterization, e.g. "editorial / restrained">
(informs cue character choice; no mechanical keyword-to-caps mapping)

Scene <K> (<mm:ss>–<mm:ss>) "<scene gist>"
  ✗ skip   <element-ref-or-shorthand>                         (<reason, 6–10 words>)
  ✓ <mm:ss.ms>  mode=<anchor("word"#N) | at-scene-ms(N)>  cue=<name>  asset=<basename>  on <element-ref>   (<reason>)
  ✓ ...

Scene <K+1> ...

TOTAL: <count> cues  (<cue type breakdown, e.g. "3 whoosh · 7 ui-tick · 1 boom · 1 riser · 1 hook-tag">)
DENSITY: 1 cue / <X.Xs> avg
NEW ANCHORS NEEDED: <comma-separated list — write "none" if empty>
NOTES:                                                                     [OPTIONAL]
  • <anything the user should know, e.g. hook moment, design.md tone read>
  • <anything you considered but skipped at the scene level>

Approve to write annotations into HTML?  [yes / refine / abort]
```

## Field rules

- **`mode=`** is mandatory on every `✓` line. It shows whether the cue is
  speech-anchored (`anchor("word"#N)`) or visual-anchored
  (`at-scene-ms(N)`). This is the editorial intent — picking the wrong mode
  is the SFX-before-visual bug pattern Rule 6 forbids, so the proposal
  surfaces it for review. Example lines:
    ```
    ✓ 00:07.42  mode=at-scene-ms(7420)  cue=pop  asset=Hollow Pop 06.wav  on .target #1   (signup-forms card landing — 50% into 400ms fade)
    ✓ 00:02.79  mode=anchor("and"#1)    cue=card-tap  asset=Mouse Click 04.wav  on #s1-cb       (checkbox click follows the spoken "and")
    ```
- **`asset=`** is **mandatory** on every `✓` line — it's the file the
  cue resolves to via `data-sfx-asset`. Show just the basename; full
  paths belong in the HTML. See SKILL.md "Asset selection" for how to
  pick from a cue's pool. The resolver in `tools/sfx-plan` is a safety
  net for un-pinned cues, not the intended path.
- **`<element-ref>`** uses `#id` when the element has one, else a short
  CSS-y descriptor (`.scene > .headline:nth-of-type(2)` is fine, but
  `the second headline in scene 2` is also fine — prioritize legibility).
- **`<reason>`** is a *short* causal phrase. The bar is: a reader who skipped
  the playbook should still understand why. Examples:
  - "punctuates landing word"
  - "scene-2 boundary, first emphatic word"
  - "swarm reveal — would crowd next anchor"
  - "ambient drift, not punctuation"
  - "honors 2s cooldown after prior tick"
- **`<mm:ss.ms>`** uses up to two decimals (e.g. `01:34.62`). It's a *display*
  number — the actual scheduled `data-start` is computed by `tools/sfx-plan`
  from the anchor word's narration-map entry.
- **`NEW ANCHORS NEEDED`** lists every anchor you'll use that doesn't yet
  appear in `narration-map.json`. Empty? Write "none." Non-empty? Your first
  write action is to extend `anchors.txt` and re-run `tools/narration-map`.

## How density is computed

Density = number of cues ÷ total video runtime in seconds, expressed as
`1 cue / X.Xs`. Target ≥ 3s. Below 3s is allowed but should be defended in
NOTES.

## When to add NOTES

NOTES is for legibility, not boilerplate. Include a NOTES bullet when:

- You marked a hook moment (and why that moment).
- You read design.md as something specific that informed restraint (e.g.
  "editorial / restrained → halved my tick budget per scene").
- You skipped a high-volume candidate type (e.g. "skipped scoring the 12
  Bézier markers — would crowd the upcoming tick").
- You're flagging an alignment risk (e.g. "the riser ends at 03:12 but the
  visual reveal is at 03:13; expect 1-frame slip").

Skip NOTES entirely when there's nothing surprising to surface.

## Approval response handling

- `yes`, `approve`, `go` → proceed to write phase.
- `refine`, plus natural-language instructions → adjust plan, re-print, loop.
- `abort`, `cancel`, `stop` → exit without writing anything.
- Anything else → treat as a refine and ask for clarification rather than
  guessing.
