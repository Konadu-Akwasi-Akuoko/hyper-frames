# Script-writer: spec-over-restriction kills invention

**Date learned:** 2026-05-13
**Sibling learning:** `learnings/composition-spec-over-restriction.md` — the composition pipeline hit the same failure mode and got the same fix. This document is the script-layer parallel.
**Videos involved:**
- `videos/why-text-is-hard-2026-05-07/` — maiden video; voice rules clearly present, structure emerged from substrate (the topic genuinely had a chain of broken-then-fixed solutions).
- `videos/how-does-captchas-work-2026-05-10/` — CAPTCHA video; script survived because the topic also fit the iceberg arc, but every concrete claim landed unsourced and the prose carried visible "script-layer chrome" (literal "Today we are going to look at..." handshakes, beat labels in the file, escalation cycles labeled as such).

## The failure mode

The `script-writer` skill before this rewrite was structured like the heavy composition pipeline. It pre-decoded the script into:

- A **9-beat arc** (Familiar-action open / Subversion / Stakes / Thesis / Foundation / Escalation cycles ×N / Synthesis / Reframe / Closer) mandated for every topic.
- **Literal phrase prescriptions** — "Today we are going to look at..." described as a "verbal handshake" that must appear. "Let's start with...", "But here is where the nightmare begins.", "The next time you..." similarly mandated.
- **Outline-first, beat-by-beat drafting** with approval gates inside the body (4a → 4b → ... → 4i).
- **No fact-grounding step.** Every concrete claim (Jonathan Wilkins's 2009 18%, Chad Houck's DEF CON figure, ETH Zurich YOLO study, GPT-4 TaskRabbit incident, 819M hours / $6B) was unsourced.
- **Hook drafted first**, before the body. 2026 YouTube scripting best practice writes the body first.

The CAPTCHA script survived because the topic happens to have a real evolutionary chain (image grids → text-distortion → reCAPTCHA → reCAPTCHA v2 → invisible reCAPTCHA → adversarial breaks). The arc fit. But the script still showed every spec-over-restriction symptom: visible recipe, prescribed phrases the prose didn't fully earn, invented concrete numbers, and no way to tell verified facts from plausible-sounding invention.

The next topic without an iceberg shape — "what is a memory barrier", "what happens between when you press a key and a character appears on screen", any process walk-through — would have been force-fit into nine labeled boxes, with the model filling whichever boxes the substrate couldn't justify.

## Why heavier scaffolds make worse scripts

The composition learning called this out at the spec layer: *every meaningful decision gets pre-made in the spec layer, before the implementer sees the script. By the time the scene-builder reads "you click I'm not a robot," the spec has decoded that into [stuff].* Same dynamic here, one layer up. Every meaningful writing decision was pre-made in the beat scaffold, before the drafter saw the substrate. By the time the drafter reached beat 4, the prose was being filled into a slot ("Today we are going to look at...") instead of being written from the substrate.

A pre-decoded scaffold removes the model's room to invent against the topic. When the topic doesn't naturally fit the scaffold, the model fills the boxes with plausible-but-unverifiable invention — because *something* has to go in the box, and the box demands a specific shape.

External research confirms the diagnosis: rigid output formats force-fit invented content into prescribed slots. Hook-first ordering inverts the right sequence (body first, then carve the hook from the strongest beat). Overcomplicated guardrails hurt more than help with each model upgrade.

## The demote-vs-delete lemma

The composition fix already established this, but it's worth naming explicitly because it's the **non-obvious move that actually worked**:

> Demoting a scaffold from "required" to "optional" doesn't fix the problem. The model reaches for whatever is in the skill's reference tree because a checklist is always cheaper to comply with than to invent against. The fix is *deletion*, not *demotion*.

For compositions: `expanded-prompt.md` was deleted, the 141-line `design.md` was replaced with a 43-line one, all 11 pre-scaffolded `compositions/*.html` stubs were deleted. The next session produced miles better results.

For scripts: `nine-beat-arc.md` was deleted from the skill, `escalation-cycle-template.md` was deleted from the skill, `outline.md` was removed as a required artifact, `example-beats.md` was rewritten as `example-passages.md` with beat labels stripped. The historical analysis of the arc survives at `research/pawel-code-stuff/analysis/script-patterns.md` because that's research, not a loadable preset. The skill stops loading it.

This is the lemma: **if you leave a structural preset in the skill's reference tree, the model picks it every time, because compliance is cheaper than invention. To restore invention, remove the preset entirely.** Applies to any preset, not just the 9-beat one. The rewritten skill ships with zero structural presets.

## Rules going forward

### 1. Voice rules stay; structure presets go

The voice layer — sentence rhythm, "But" pivot, three-part lists, max-22-word, personification, naming things, dated incidents, 170 wpm, no CTA — survived across every studied video because those are *voice*, not *structure*. They're the palette. Keep them.

The structure layer — 9 beats, escalation cycles, hook-first, beat-by-beat checkpoints, literal phrase mandates — has to leave. Structure is whatever the substrate genuinely wants to become.

### 2. Substrate distillation replaces outline

The skill now produces `substrate-notes.md` instead of `outline.md`. The difference:

| outline.md (old) | substrate-notes.md (new) |
|---|---|
| Pre-decided 9-beat structure | List of materials |
| Each beat = one sentence prescribing what fills it | Each section = a category of evidence the substrate actually contains |
| Tells the drafter what to write | Tells the drafter what's available to write *with* |

If the substrate doesn't surface a dated incident, the notes file doesn't have a "dated incidents" entry, and the prose doesn't get to invent one. If the substrate surfaces three named systems, the prose has three named systems. The notes are a constraint on invention, not a recipe for it.

### 3. Body-first, single-pass drafting

Draft the body as one continuous prose pass. Single approval gate at the body level. Hook is carved from the body afterward. Landing is picked from three archetypes after the body delivers something specific.

No per-beat checkpoints inside the body. By the time the drafter writes the prose, the only commitments are: (a) the voice rules, (b) the substrate, (c) the target word count. Everything else emerges.

### 4. Phrase moves are optional, not prescribed

"Today we are going to look at...", "Let's start with...", "But here is where the nightmare begins.", "The next time you..." are available moves. They land when the prose naturally arrives at the moment for them. They do not appear on cue.

If the skill mandates them, the model recites them on cue, and the audience hears the recipe. Earlier scripts used these phrases because the writers' prose happened to land at the moment that asked for them — not because a checklist said to.

### 5. Fact-verifier sub-agent after the script is locked

Concrete claims (dated incidents, percentages, named people, organizations, papers, products) are the highest-leverage move in the voice — and the highest-risk site for invention. The skill now dispatches a project-scoped sub-agent (`.claude/agents/script-fact-verifier.md`) after the script is approved end-to-end. The agent extracts every claim, sources via WebSearch, scores ✅/⚠️/❌/🚫, and writes `<video-dir>/fact-check.md`.

Advisory only — never blocks voiceover hand-off. The user decides whether to revise. The point is *visibility*, not enforcement. A script with three unverified claims can still proceed if the user accepts it.

### 6. The CAPTCHA script stays as the cautionary example

`videos/how-does-captchas-work-2026-05-10/script.md` is the artifact that exposed the failure. It still reads fine — the topic fit the arc — but every concrete claim is unsourced, the literal phrase prescriptions are visible in the prose, and the beat structure shows through. Compare it against the next script generated by the rewritten skill on a non-iceberg topic: the prose should follow the substrate's natural shape, not nine labeled boxes.

## Quick failure smell-tests

If any of these are true mid-pipeline, you are heading back toward the failure mode:

- The skill is loading a beat scaffold, escalation-cycle template, or arc preset.
- The draft has labels like "Beat 1", "Cycle 2", "Synthesis" embedded in the prose or in comments.
- The skill is prescribing a literal opening phrase as required.
- The hook is being drafted before the body.
- Concrete claims (numbers, dated incidents) are landing in the prose without verification, and there is no fact-check step after approval.
- The drafter is being asked to approve the structure before the substrate is distilled.

Reset to substrate-notes + voice rules + body-first drafting + fact-verifier-after. The rewrite (2026-05-13) is the canonical baseline.
