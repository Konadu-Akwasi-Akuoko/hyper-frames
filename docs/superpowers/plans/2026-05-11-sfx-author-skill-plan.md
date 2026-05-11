# .claude/skills/sfx-author Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `sfx-author` Claude skill — the editorial brain that reads a finished composition + transcript + narration-map + design.md + sfx-catalog, proposes a sound-design cue plan, awaits human approval, then writes `data-sfx-*` annotations into the HTML and runs `tools/sfx-plan`.

**Architecture:** A markdown skill at `.claude/skills/sfx-author/SKILL.md` with supporting reference docs under `reference/`. The skill is a *contract* between the user and Claude, not executable code — its quality lives in how clearly it expresses (a) what to read, (b) the placement principles, (c) the technical floors that must not be violated, (d) the cue character library, (e) the worked examples that teach taste, and (f) the proposal-then-confirm flow.

**Tech Stack:** Markdown + YAML frontmatter. No new code. Depends on Plan 1 (the catalog) and Plan 2 (the placement tool) being landed first.

**Source spec:** `docs/superpowers/specs/2026-05-11-sfx-pipeline-design.md` (Component 2).

**Anti-pattern guard:** The skill's playbook is deliberately principles + floors + vocabulary + examples — *not* a trigger-to-cue mapping table. This honors `learnings/composition-spec-over-restriction.md`: heavy pre-decoding of editorial decisions kills the creative leap. The plan below MUST resist the temptation to add rigid `class="x" → cue="y"` rules during execution.

## File structure

```
.claude/skills/sfx-author/
├── SKILL.md                       # the skill itself (Tasks 2–5)
└── reference/
    ├── cue-vocabulary.md          # one page per cue: when it earns a hit (Task 6)
    ├── worked-examples.md         # canonical-video reasoning walkthroughs (Task 7)
    ├── anchor-discipline.md       # how to choose + register an anchor word (Task 8)
    └── proposal-template.md       # exact format for the review checkpoint (Task 9)
```

Plus:
- `CLAUDE.md` at the repo root gets a new "Sound design" section (Task 10).
- A manual acceptance pass against `videos/how-does-captchas-work-2026-05-10/` (Task 11).

---

### Task 1: Scaffold the skill directory and frontmatter

**Files:**
- Create: `.claude/skills/sfx-author/SKILL.md` (frontmatter only at this step)
- Create: `.claude/skills/sfx-author/reference/` (empty dir)

- [ ] **Step 1: Create directories**

```bash
mkdir -p .claude/skills/sfx-author/reference
```

- [ ] **Step 2: Write the frontmatter + a one-line placeholder body**

Write `.claude/skills/sfx-author/SKILL.md`:

```markdown
---
name: sfx-author
description: Editorial sound-design pass for a finished HyperFrames video. Reads index.html + compositions/*.html + transcript.json + narration-map.json + design.md + sound-effects/sfx-catalog.yml. Proposes a SFX cue plan, awaits human approval, then writes data-sfx-* annotations and runs tools/sfx-plan to emit compositions/sfx.html as a native HyperFrames audio sub-composition. Use when the user says "add sound design", "score this video", "add sfx", "do the sound pass", or asks for cues/whooshes/ticks on a finished composition. Only runs after the composition is visually approved in preview.
---

# sfx-author

(body fills in over Tasks 2–5)
```

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/sfx-author/
git commit -m "chore(sfx-author): scaffold skill directory and frontmatter"
```

---

### Task 2: SKILL.md — Overview + inputs + what it does/doesn't

**Files:**
- Modify: `.claude/skills/sfx-author/SKILL.md`

- [ ] **Step 1: Replace the placeholder body with overview + inputs + scope**

Open `.claude/skills/sfx-author/SKILL.md` and replace everything *after* the frontmatter block with:

```markdown
# sfx-author

You are running the sound-design pass on a HyperFrames video whose visuals are
already finished. Your job is to decide *which moments earn a hit*, propose a
cue plan, get explicit human approval, then write `data-sfx-*` attributes into
the composition HTML and run `tools/sfx-plan` to materialize a native audio
sub-composition at `compositions/sfx.html`.

This is the **last** authoring pass before render. If the composition is not
visually settled in `npx hyperframes preview`, stop and ask the user to confirm
visuals are locked before continuing.

## Inputs you always read

From the video folder (`videos/<slug>-<YYYY-MM-DD>/`):

- `index.html` and every file under `compositions/*.html` — the visuals you are
  scoring. Skip `compositions/sfx.html` (that's your own output).
- `transcript.json` — word-level timing, the source of all spoken text.
- `narration-map.json` — pre-computed anchors, pause windows, scene-boundary
  candidates, emphatic words. This is your fastest path to timing.
- `anchors.txt` — the human-curated anchor list that produced `narration-map.json`.
  You may need to extend it (see `reference/anchor-discipline.md`).
- `design.md` — tone signals. Read it; do not pattern-match keywords. Use it as
  context for cue character choice, never as a mechanical filter.

From the repo:

- `sound-effects/sfx-catalog.yml` — available cues + per-asset metadata. The cue
  recipes (`ui-tick`, `whoosh`, `boom`, `riser`, `pop`) define what's pickable.

Optional, per-video:

- `sfx-overrides.yml` at the video folder root — override cue recipes for this
  video specifically (e.g. swap `ui-tick`'s candidate pool to sharper variants).
  Absence means "use repo defaults."

## What this skill does

- Reads all inputs above.
- Walks the visuals and the narration *together*. Identifies moments that earn
  a sound. Decides cue character per moment based on what the moment is *doing*.
- Produces a cue plan in the exact format shown in
  `reference/proposal-template.md`.
- **Hard-gates** on user approval before writing anything.
- On approval, makes surgical Edit calls to add `data-sfx-*` attributes to the
  named elements. Does not rewrite or reformat surrounding HTML.
- Registers any new anchor words in `anchors.txt` and re-runs `tools/narration-map`
  so the new anchors are resolvable (see `reference/anchor-discipline.md`).
- Runs `tools/sfx-plan` from the video folder. Reports the cue count, warning
  count, and the path written.
- Idempotently mounts the sfx-layer in `index.html` (only on first run).
- Launches `npx hyperframes preview` and surfaces the studio URL.

## What this skill does NOT do

- It does not author or modify animations. SFX follows visuals; visuals are not
  retimed for SFX.
- It does not pick assets directly. Asset filenames are picked by
  `tools/sfx-plan`'s deterministic resolver — you decide *anchors* and *cues*,
  never file paths.
- It does not edit `compositions/sfx.html`. That file is generated. If the user
  has hand-edited it, mention that next run will overwrite their changes.
- It does not run if visuals are unfinished. If `compositions/` contains stubs
  with `[ TO BE BUILT ]` or `PLACEHOLDER`, stop and surface the gap.
- It does not bypass the proposal-then-confirm gate. Auto-apply is forbidden.

## Hard rules (non-negotiable)

1. Propose the full plan before any HTML edit. The user must approve with the
   literal word `yes`, `approve`, or `go`. Any other response is a refine or an
   abort, not implicit approval.
2. Anchors in `data-sfx-anchor` must already exist in `narration-map.json` at
   write time. If you need a new one, add it to `anchors.txt` and re-run
   `tools/narration-map` *before* writing the attributes.
3. Respect the technical floors in the Playbook section. They are mix-craft
   physics, not aesthetics; violating them produces an actually worse mix.
4. Never edit `compositions/sfx.html` by hand. Always run `tools/sfx-plan`.
5. If `sfx-catalog.yml` is missing, stop and direct the user to run
   `uv run --project tools/sfx-catalog sfx-catalog`. Do not proceed without it.
```

- [ ] **Step 2: Verify the skill is syntactically valid**

```bash
head -5 .claude/skills/sfx-author/SKILL.md
```

Expected: opens with `---`, `name:`, `description:`, `---`. No parse errors.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/sfx-author/SKILL.md
git commit -m "feat(sfx-author): SKILL.md overview, inputs, scope, hard rules"
```

---

### Task 3: SKILL.md — Playbook (principles, floors, cue library)

**Files:**
- Modify: `.claude/skills/sfx-author/SKILL.md`

This is the **load-bearing** section. It encodes the lesson from
`learnings/composition-spec-over-restriction.md`: principles + floors + cue
character library + worked examples — *not* a trigger-to-cue mapping table.

- [ ] **Step 1: Append the playbook**

Append to `.claude/skills/sfx-author/SKILL.md`:

```markdown
## Playbook

You operate from principles, technical floors, a cue character vocabulary, and
worked examples. You **do not** consult a rigid CSS-class-to-cue mapping table.
That kind of pre-decoding is what failed in
`learnings/composition-spec-over-restriction.md` — it strips the editorial leap
that distinguishes a real-looking moment from a generic one.

### Placement principles

- Score moments that *earn* a hit — the spoken payoff, the visual punchline,
  the threshold cross between scenes, the reveal of the line that the line is
  about.
- Skip texture (typewriter chatter, decorative drift, ambient pulses) — they
  belong to atmosphere, not punctuation.
- Lead sound ahead of picture. The ear is faster than the eye; a cue that lands
  exactly on the frame feels late.
- Match cue character to what the moment is *doing*, not to what CSS class the
  element wears.
- When in doubt, score less. Silence is a tool, and an unused cue is cheaper
  than a wrong one.
- Read the script (`transcript.json`) first; only then look at the HTML.

### Technical floors (mix-craft physics, not aesthetic preferences)

These are not negotiable. Violating them produces an actually worse mix.

- **Peak alignment.** A cue's *peak* (catalog `peak_time_s`) lands on the
  anchor's `start`, not the cue's start. `tools/sfx-plan` does this math for
  you — your job is to pick the anchor correctly.
- **Default leads.** `-50ms` for `ui-tick`, `-150ms` for `whoosh`, `0ms` for
  `boom`, `-(duration)` for `riser`. Override via `data-sfx-lead-ms` only when
  you have a specific reason — keep a note in the proposal saying why.
- **Same-cue cooldowns.** `ui-tick` ≥ 2s apart; `whoosh` ≥ 4s apart;
  `boom` ≥ 30s apart. Two ticks 1.2s apart smear; the ear hears one event
  smeared over both, not two.
- **Density ceiling.** ≤ 1 cue per 3s rolling average across the whole video.
  Above ~1 per 1.5s, the tool will hard-fail — and rightly so, because the
  ducking math thrashes and VO intelligibility collapses.

### Cue character library

Pick by **intent**, not by element type. Five cues plus the option of silence.

| Cue       | Character           | Best when the moment is…                                              |
|-----------|---------------------|------------------------------------------------------------------------|
| `whoosh`  | spatial motion      | crossing a threshold, entering/exiting a frame, scene transitions      |
| `ui-tick` | discrete arrival    | a thing snapping into place, a label landing, a small reveal           |
| `pop`     | playful arrival     | softer than tick — lighter or rhythmic reveals                         |
| `boom`    | weight / finality   | scale, gravitas, the line that lands                                   |
| `riser`   | build-to-payoff     | tension into a reveal, the climb before the hit                        |
| *(none)*  | negative space      | the punchline is *the silence*; or the texture is texture              |

Available cues are defined in `sfx-catalog.yml`'s `cues:` section. If you need
a cue that isn't there, *stop and surface the gap* — don't author against an
imaginary cue. Adding new cues is catalog work, outside this skill's scope.

### Hook moment

Each video has at most **one** "hook moment" — the largest emotional or
informational beat. Mark it on its element with `data-sfx-hook="true"`. In
Phase A this is a breadcrumb only (no audio change). Phase C will use it to
mute music/ambience for ~500ms before the moment (pre-impact silence). Choose
the hook carefully; if you can't identify a single clear hook, omit the tag.
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/sfx-author/SKILL.md
git commit -m "feat(sfx-author): playbook — principles, floors, cue character library, hook"
```

---

### Task 4: SKILL.md — Proposal format + refine loop

**Files:**
- Modify: `.claude/skills/sfx-author/SKILL.md`

- [ ] **Step 1: Append the proposal-and-refine sections**

Append to `.claude/skills/sfx-author/SKILL.md`:

```markdown
## The proposal you produce before any edit

Before touching HTML, print a plan in the exact format below. The full template
with annotations lives at `reference/proposal-template.md`; this is the
inline version.

```
SFX CUE PLAN — <slug>
Runtime <mm:ss> · <N> scenes detected
Read design.md as: <one-line characterization>
(informs cue character choice; no mechanical keyword-to-caps mapping)

Scene 1 (00:00–<scene end>) "<scene title or first-line gist>"
  ✗ skip   <element ref>                            (<reason in 6–10 words>)
  ✓ <mm:ss.ms>  anchor="<word>" [idx=<N>]  <cue>  on <element ref>   (<one-line reason>)
  ...

Scene 2 ...

TOTAL: <count> cues  (breakdown by type)
DENSITY: 1 cue / <X.Xs> avg
NEW ANCHORS NEEDED: <list — empty if none>
NOTES:
  • <anything the user should know — e.g. hook moment, design.md tone read>

Approve to write annotations into HTML?  [yes / refine / abort]
```

Rules for the proposal:

- Every line shows either `✓` (will write) or `✗ skip` (considered, deliberately
  not scoring). Skips are as important as wrote-ins — they make your editorial
  reasoning legible.
- Reason fields stay short. The full thinking belongs in your own head; the
  proposal is a contract surface.
- `NEW ANCHORS NEEDED` lists any `data-sfx-anchor` values you intend to use that
  don't yet appear in `narration-map.json`. If the list is non-empty, your first
  write action is to extend `anchors.txt` and re-run `tools/narration-map` —
  before any HTML edit.

## Refine loop

The user can respond with `refine` plus natural-language instructions. Treat
each refine as a transformation on the current plan:

- "drop the boom in scene 3" → remove that line, re-print plan.
- "the hook is 02:48 not 03:41" → move the `data-sfx-hook` tag to the element
  spoken at 02:48, re-print plan.
- "score the Bézier markers after all — make them quieter" → add `ui-tick` cues
  with `data-sfx-volume="0.5"` on those elements, re-print plan.
- "the whoosh into scene 3 lands late" → after the plan is written, this is a
  post-preview refine: add `data-sfx-lead-ms="-200"` to that element and re-run
  `tools/sfx-plan`.

Loop until the user types `yes`/`approve`/`go`. Then write.

## After approval

1. If `NEW ANCHORS NEEDED` is non-empty: append each anchor on its own line to
   `anchors.txt` (preserve existing entries; add a `# sfx` comment block if
   useful for legibility). Then run:

   ```bash
   uv run --project ../../tools/narration-map narration-map \
       transcript.json --anchors anchors.txt
   ```

   from the video folder. Verify the new anchors appear in the regenerated
   `narration-map.json` before continuing.

2. Use the `Edit` tool to add `data-sfx-*` attributes to each scored element.
   One element per Edit call. Never reformat surrounding HTML.

3. From the video folder, run:

   ```bash
   uv run --project ../../tools/sfx-plan sfx-plan --report
   ```

   Report the cue count, warning count, and the studio URL.

4. Run `npx hyperframes preview`. Surface the URL the user should open. Stop
   and wait for their audit feedback.

5. On feedback, loop back into the refine flow.

## Failure modes you must handle gracefully

- **`sfx-catalog.yml` missing** → instruct the user to build it
  (`uv run --project tools/sfx-catalog sfx-catalog`) and stop.
- **Anchor not resolvable after extending `anchors.txt`** → the anchor text
  isn't a literal substring of the transcript. Surface the candidate words from
  `transcript.json` that are nearby in time and ask the user to choose a real
  anchor word.
- **`tools/sfx-plan` raises `DensityViolationError`** → the plan was too dense
  even though you tried to honor the ceiling. Drop the lowest-priority cues in
  the densest window and re-run.
- **Composition has placeholder stubs** (`[ TO BE BUILT ]` etc.) → stop. SFX is
  the last pass; visuals must be done first.
- **User asks for a cue not in `sfx-catalog.yml`'s `cues:` section** → don't
  invent. Tell the user the available cues; suggest a similar one; offer to
  open a catalog-revision task.

## Skill's checklist when invoked

When this skill is invoked, use `TaskCreate` to add these items and execute
them in order:

1. Verify visuals are settled (no placeholders; preview is clean).
2. Load all inputs; verify `sfx-catalog.yml` version matches.
3. Walk HTML + transcript + narration-map. Identify candidate moments.
4. Apply placement principles. Pick cue character from the library.
5. Apply technical floors (cooldowns, density ceiling).
6. Produce the proposal in the exact format above.
7. **WAIT for user approval. Hard gate.**
8. If new anchors needed: extend `anchors.txt`, re-run `tools/narration-map`.
9. Write `data-sfx-*` attributes via `Edit` (one element at a time).
10. Run `tools/sfx-plan --report`.
11. Run `npx hyperframes preview` and surface the URL.
12. Wait for audit feedback; loop step 9 onward on refines.
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/sfx-author/SKILL.md
git commit -m "feat(sfx-author): proposal format, refine loop, post-approval flow, checklist"
```

---

### Task 5: SKILL.md — Final wiring, references, and trigger phrases

**Files:**
- Modify: `.claude/skills/sfx-author/SKILL.md`

- [ ] **Step 1: Append a closing section pointing at the reference docs**

Append to `.claude/skills/sfx-author/SKILL.md`:

```markdown
## Reference documents

Read these before producing your first proposal in a fresh session — they
encode the taste this skill is built on:

- `reference/cue-vocabulary.md` — per-cue: when it earns a hit, when it doesn't.
- `reference/worked-examples.md` — concrete annotated walkthroughs from
  `videos/why-text-is-hard-2026-05-07/`. The "this is what good looks like"
  reference.
- `reference/anchor-discipline.md` — how to pick an anchor word, when to extend
  `anchors.txt`, edge cases (homonyms, repeated words, anchors that don't appear
  in the transcript).
- `reference/proposal-template.md` — the exact proposal output format with
  annotations.

## When to invoke this skill

Trigger on any of:

- "add sound design", "score the video", "add SFX", "do the sound pass"
- "add whooshes / ticks / cues to this composition"
- The user signals visuals are done and asks "what's next?" right after a
  `hyperframes preview` cycle. Confirm visuals are locked before starting.

**Do not invoke** if:

- Composition is unfinished (placeholder stubs, only Scene 1 built, etc.).
- The user is asking about music or mastering — those are Phase B/C, out of
  scope for this skill. Surface that politely.
- `sound-effects/sfx-catalog.yml` is missing — point at the catalog tool first.
```

- [ ] **Step 2: Sanity-check the full SKILL.md**

```bash
wc -l .claude/skills/sfx-author/SKILL.md
```

Expected: roughly 200–280 lines. If it's under 150, sections were probably
truncated; if over 350, sections probably overgrew — trim back to the spec's
shape.

```bash
grep -c '^##' .claude/skills/sfx-author/SKILL.md
```

Expected: at least 10 `##` headings (Overview, Inputs, What does, What does NOT,
Hard rules, Playbook, Proposal, Refine loop, After approval, Failure modes,
Checklist, References, When to invoke).

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/sfx-author/SKILL.md
git commit -m "feat(sfx-author): closing section — references + trigger phrases"
```

---

### Task 6: `reference/cue-vocabulary.md`

**Files:**
- Create: `.claude/skills/sfx-author/reference/cue-vocabulary.md`

One short page per cue. Each page answers: what character does this have, what
earns it, what doesn't, common failure modes.

- [ ] **Step 1: Write the reference**

Write `.claude/skills/sfx-author/reference/cue-vocabulary.md`:

```markdown
# Cue vocabulary — when each cue earns a hit

This page is intent-by-intent. Use it to pick a cue *after* you've identified
a moment that deserves one — never to scan for elements that "should have" one.

---

## `ui-tick` — discrete arrival

**Character:** sharp, bright, ≤ 0.5s, fast attack. The sound of a *thing
landing*.

**Earns a tick:**
- A headline or label that fades in from opacity 0 on a spoken word.
- A diagram element that snaps into final position (a connector arrow lands,
  a vertex appears, a label resolves).
- A list item revealed in step with the line that names it.

**Doesn't earn a tick:**
- A typewriter that runs per-character (the line is the moment, not each glyph).
- An element that drifts in continuously (drift is texture; tick is event).
- An element whose entrance is masked by a louder cue (e.g. mid-whoosh).

**Failure modes:**
- Too many ticks in a row → density collapse. Honor the 2s cooldown ruthlessly.
- Tick on every reveal in a high-density scene → use one tick on the *headline*
  reveal and let the other reveals ride.

---

## `whoosh` — spatial motion / threshold cross

**Character:** 0.4–1.5s, swelling attack ≥ 0.1s, peaks toward the middle.
The sound of *something passing through*.

**Earns a whoosh:**
- Scene-boundary cuts at narration-map's scene-boundary candidates (pauses
  >600ms after `.!?`).
- A large element traversing the frame.
- A camera-like move (zoom out, push in) implemented in the composition.

**Doesn't earn a whoosh:**
- Small element entrances — use `ui-tick` or `pop` instead.
- Opening scene (the start of a video already has the user's full attention; a
  whoosh out of silence feels jarring).
- Scenes that end on a *deliberate* silence (the whoosh would steal the beat).

**Failure modes:**
- Whoosh on every scene boundary → wears thin by scene 4. Reserve for boundaries
  with a real visual cross; let some boundaries fall silent.

---

## `pop` — playful arrival

**Character:** ≤ 0.3s, warm-to-bright spectrum, soft attack. Lighter than tick,
less authoritative.

**Earns a pop:**
- Rhythmic reveals where ticks would feel too sharp (icons appearing on a beat).
- Playful or whimsical moments — explainer/essay videos with a lighter tone.
- Reveals inside an already-scored scene where adding another tick would crowd.

**Doesn't earn a pop:**
- Serious or technical moments — feels too cute. Use tick.
- Anything that needs presence — a pop won't carry weight; use tick or boom.

---

## `boom` — weight / finality

**Character:** sub-bass-dominated, peak near the start (≤ 0.2s), 0.3–2s tail.
The sound of *something landing with weight*.

**Earns a boom:**
- The line that the whole video is about, when it lands.
- A reveal of a huge number or scale (the dollar amount, the year, the body count).
- The *final* word of a key sentence, when paired with a major visual reveal.

**Doesn't earn a boom:**
- More than once per 30s. Booms wear out instantly when overused.
- The wrong word. A boom on "is" or "a" is comedic; a boom on the noun lands.
- On a beat that's already heavy from music or ambience (Phase B/C concern —
  in Phase A there's no music, so this is less of a worry).

**Failure modes:**
- Mistaking a number for a "boom moment." Not every number is a hit. "The page
  is 800 pixels wide" doesn't need a boom; "two billion lines of code" might.

---

## `riser` — build-to-payoff

**Character:** ≥ 1.5s, slow attack, ends on the payoff. The sound of *tension
climbing toward release*.

**Earns a riser:**
- A 1.5–3s build before a major reveal.
- A scene's final tension-into-revelation movement.

**Doesn't earn a riser:**
- More than once per scene. Two risers per scene cheapens both.
- Adjacent scenes both ending in risers. The pattern reads as filler.

**Failure modes:**
- Riser ending in silence (no payoff cue) → feels unfinished. Pair with the
  reveal's own cue (often a `boom` or `whoosh`).

---

## Silence — the unused cue

The absence of sound is itself a tool. Use it when:

- The line is so emphatic that any sound would dilute it.
- The moment immediately precedes a big payoff (deliberate negative space).
- The texture is the texture (typewriter, ambient drift, background motion).

If you're tempted to add a cue but can't say *what the moment is doing*, leave
it silent.
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/sfx-author/reference/cue-vocabulary.md
git commit -m "docs(sfx-author): cue vocabulary reference"
```

---

### Task 7: `reference/worked-examples.md`

**Files:**
- Create: `.claude/skills/sfx-author/reference/worked-examples.md`

This is the skill's "this is what good looks like" reference, pulled from the
canonical maiden video.

- [ ] **Step 1: Write the worked examples**

Write `.claude/skills/sfx-author/reference/worked-examples.md`:

```markdown
# Worked examples — `videos/why-text-is-hard-2026-05-07/`

These examples teach the editorial reasoning by demonstration. Each shows: the
moment, the cue, the anchor, and *why* — including why nearby elements were
*not* scored.

---

## Example 1 — "mathematical NIGHTMARE" (Scene 1)

**Context.** The hook scene. A typewriter types `~/draft.txt`, then the line
"A MATHEMATICAL NIGHTMARE." resolves with NIGHTMARE in amber.

**Annotation.**

```html
<div id="s1-nightmare"
     class="nightmare-stack"
     data-sfx-anchor="nightmare"
     data-sfx-on-anchor="ui-tick">
  <div class="eyebrow ns-eyebrow">UNDER THE HOOD</div>
  <div class="ns-line">A <span class="ns-amber">MATHEMATICAL</span></div>
  <div class="ns-line ns-amber">NIGHTMARE.</div>
  <div class="ns-foot">/// translating one keystroke into pixels</div>
</div>
```

**Reasoning.** "NIGHTMARE" is where the line lands. The element entrance peaks
emotionally there. A `ui-tick` at `-50ms` lead lands the click on the syllable.

**What was *not* scored:**

- `#s1-typed` (typewriter) — texture. Per-character clicks would crowd the
  word that's actually the moment.
- `.eyebrow.ns-eyebrow` ("UNDER THE HOOD") — scene metadata, ambient. No tick.
- `.ns-foot` (the slash-comment footer) — atmosphere, not punctuation.

---

## Example 2 — Scene 2→3 boundary at "control point"

**Context.** Scene 2 closes on the Bézier glyph with control-point markers
appearing. Scene 3 begins describing control points in detail. The first
spoken word of scene 3 is "control."

**Annotation.**

```html
<div id="s3" class="scene"
     data-sfx-anchor="control"
     data-sfx-on-anchor="whoosh">
  ...
</div>
```

**Reasoning.** A scene-boundary `whoosh` keyed to the first emphatic word of
the next scene. Lead `-150ms` (the default) so the whoosh peaks on "con-".

**What was *not* scored:**

- Each individual control-point marker in scene 2 — they're a swarm reveal,
  not threshold crosses. Clicking each one would turn the scene into a UI
  bleep festival and crowd the upcoming "Bézier" tick.
- The exact transition frame between scenes — the *anchor* is the spoken word,
  not a visual cut. `tools/sfx-plan` handles peak alignment from there.

---

## Example 3 — "Bézier" tick (Scene 2 mid)

**Context.** Mid-scene 2, the glyph "A" is broken down into Bézier curves;
control points pop on. The narration says "Bézier" as the first marker appears.

**Annotation.**

```html
<svg id="s2-overlay" class="glyph-overlay"
     data-sfx-anchor="Bézier"
     data-sfx-on-anchor="ui-tick">
  ...
</svg>
```

**Reasoning.** "Bézier" is the conceptual landing word — it's the term the
viewer is supposed to register. A single `ui-tick` punctuates the conceptual
reveal. The 12 control-point markers that follow are scored *only* by the
silence-after-the-tick (they ride the visual rhythm, no audio).

**What was *not* scored:**

- The 12 control-point markers individually. Bezier's tick is the punctuation;
  the markers are texture.

---

## Anti-example — what NOT to do

If a video has a list of three competing definitions appearing in sequence, the
tempting move is one `ui-tick` per item:

```
✗ tick on item 1
✗ tick on item 2
✗ tick on item 3
```

Don't. Honor the 2s cooldown — if the three items appear within ~3s, you get
one tick on the *list heading* and let the three items ride on visual rhythm.
Three ticks in 3s smear into perceptual mud.

---

## How to use these examples

When you're producing a proposal for a new video, **reference these examples
explicitly in your reasoning lines**. For example:

> ✓ 00:08.4 anchor="nightmare" ui-tick on #s1-nightmare (Example 1 pattern —
>          punctuates the landing word; skips the typewriter texture)

That referent makes your editorial logic legible to the user and links back to
the canonical bar.
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/sfx-author/reference/worked-examples.md
git commit -m "docs(sfx-author): worked examples from canonical why-text-is-hard"
```

---

### Task 8: `reference/anchor-discipline.md`

**Files:**
- Create: `.claude/skills/sfx-author/reference/anchor-discipline.md`

How to pick anchor words, when to extend `anchors.txt`, and edge cases.

- [ ] **Step 1: Write the reference**

Write `.claude/skills/sfx-author/reference/anchor-discipline.md`:

```markdown
# Anchor discipline

A `data-sfx-anchor` value must resolve via `narration-map.json` at write time.
The narration map is regenerated by `tools/narration-map` from `anchors.txt`.
So the chain is:

```
anchors.txt → tools/narration-map → narration-map.json → tools/sfx-plan
```

If you want to use an anchor word that's not yet in `narration-map.json`, you
add it to `anchors.txt` and re-run `tools/narration-map` first.

## Picking a good anchor

- **Prefer the conceptually-loaded word**, not a function word.
  - "the **nightmare** is in the math" → anchor "nightmare", not "the".
- **Prefer words spoken with emphasis.** `narration-map.json`'s `emphatic_words`
  list ranks words by spoken duration — these are often where the voice lingers
  on a key term.
- **Prefer single words over phrases** unless the phrase is the actual moment.
  - "Bézier control point" appearing as a phrase reveal → anchor the phrase.
  - One word in a sentence carrying meaning → anchor that word alone.
- **Match the visual peak**, not the visual start. A label that fades in 200ms
  is *resolved* at the end of the fade, not the start. The anchor word should
  fall in or just after that window.

## When to extend `anchors.txt`

You'll need new anchors whenever:

- You want to score a word that wasn't an `anchors.txt` entry to begin with
  (common — `anchors.txt` is usually authored for animation timing, not SFX).
- A word appears multiple times and you need `data-sfx-anchor-index` to pick
  the right occurrence. The narration-map already reports all occurrences as
  long as the *phrase* is in `anchors.txt`.

To extend:

1. Add each new anchor on its own line in `anchors.txt`. Group with a comment:

   ```
   # sfx anchors
   nightmare
   Bézier
   control
   ```

2. Re-run from the video folder:

   ```bash
   uv run --project ../../tools/narration-map narration-map \
       transcript.json --anchors anchors.txt
   ```

3. Verify with:

   ```bash
   python3 -c "import json; nm = json.load(open('narration-map.json')); print(sorted(a['phrase'] for a in nm['anchors']))"
   ```

   Confirm your new entries appear.

## Edge cases

### Homonyms / words that appear many times

Use `data-sfx-anchor-index`. The narration-map's `matches` array is in spoken
order; `index=1` is first occurrence, `index=2` is second, etc.

```html
<div data-sfx-anchor="hard" data-sfx-anchor-index="2" data-sfx-on-anchor="ui-tick"></div>
```

If you don't know how many times the word appears, check the narration-map:

```bash
python3 -c "import json; nm = json.load(open('narration-map.json'));
   [print(a['phrase'], len(a['matches'])) for a in nm['anchors'] if 'hard' in a['phrase'].lower()]"
```

### A word you want isn't actually spoken

Two paths:

- Pick a nearby word that *is* spoken. The peak alignment math will land the
  cue close enough.
- If the moment is in pure silence (a logo, a pre-VO opener), this skill can't
  score it. `data-sfx-anchor` requires a spoken word. Surface the gap and
  suggest the user revisit in Phase C when absolute-time cues are added.

### Phrase anchors that span pause windows

If you write `data-sfx-anchor="under the hood"` and `narration-map` shows that
phrase spans a 0.3s pause, the anchor still resolves (the matched_text covers
the full span). The cue lands on `start` (the first word). Generally prefer a
single word for tighter timing.

### Anchor word is also a sentence boundary

A word that's also `.!?` punctuated may have its `start` slightly *before* the
punctuation. That's correct — `start` is the word's onset. If you want the cue
to land *after* the sentence ends, use a positive lead-ms (rare; usually
negative lead).

## Anti-patterns

- **Sharing an anchor between multiple elements** with the same `cue` and
  `anchor_index`. The picker is deterministic, so both would resolve to the
  same file and overlap. Use different indices, different cues, or different
  anchors.
- **Treating `narration-map.json` as fully editable.** It's generated. Edit
  `anchors.txt` and re-run, don't hand-edit the JSON.
- **Adding anchors for words you'll only score with one cue, when an existing
  anchor a few words earlier would land tighter.** Don't bloat `anchors.txt`
  unnecessarily — it's a working file the author also reads.
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/sfx-author/reference/anchor-discipline.md
git commit -m "docs(sfx-author): anchor discipline reference"
```

---

### Task 9: `reference/proposal-template.md`

**Files:**
- Create: `.claude/skills/sfx-author/reference/proposal-template.md`

The full proposal-format reference, with annotation comments. The skill links to
this from the inline summary in `SKILL.md`.

- [ ] **Step 1: Write the template**

Write `.claude/skills/sfx-author/reference/proposal-template.md`:

```markdown
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
  ✓ <mm:ss.ms>  anchor="<word>"[ idx=<N>]  <cue-name>  on <element-ref>   (<reason>)
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
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/sfx-author/reference/proposal-template.md
git commit -m "docs(sfx-author): proposal template reference"
```

---

### Task 10: Update repo `CLAUDE.md` with a Sound design section

**Files:**
- Modify: `CLAUDE.md` (project root)

Per the spec, a new section lands between "Transcript-as-timing-truth" and
"Lint / inspect / preview before declaring done."

- [ ] **Step 1: Locate the insertion point**

```bash
grep -n "Lint / inspect / preview" CLAUDE.md
```

Expected: one match. The new section goes immediately above this line.

- [ ] **Step 2: Insert the new section**

Insert the following before the matched line:

```markdown
### Sound design — the last authoring pass

Sound design follows visuals, never drives them. Run it only after the
composition is settled in `npx hyperframes preview`.

The pipeline ships with:

- A shared SFX library at `sound-effects/` (~1416 assets across 4 sub-libraries).
- A repo-level metadata catalog at `sound-effects/sfx-catalog.yml` (committed;
  rebuild only when the library changes via `uv run --project tools/sfx-catalog sfx-catalog`).
- A Claude skill at `.claude/skills/sfx-author/` that proposes a cue plan,
  awaits human approval, and writes `data-sfx-*` annotations into the HTML.
- A deterministic placement tool at `tools/sfx-plan/` that resolves
  annotations into a native HyperFrames audio sub-composition at
  `compositions/sfx.html`.

Invoke the skill when visuals are done and you want SFX:

> "add sound design to this video" / "score this composition" / "do the sfx pass"

The skill always proposes its full plan before writing anything. Treat the
proposal as the contract — refine before approval, not after the fact.

**Phase A scope, by design.** This pipeline handles SFX placement only. Music
beds, ambient drone, sidechain ducking, and master loudness normalization to
−14 LUFS / −1 dBTP are Phase B/C — explicit non-goals for now.
```

- [ ] **Step 3: Verify the file still reads cleanly**

```bash
grep -A 2 "Sound design — the last" CLAUDE.md
grep -B 2 "Lint / inspect / preview" CLAUDE.md
```

Expected: the new section appears, immediately followed by the Lint section.

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(claude): add sound-design workflow section to project CLAUDE.md"
```

---

### Task 11: Manual acceptance — apply the full pipeline to the captchas video

**Files:**
- Modify: `videos/how-does-captchas-work-2026-05-10/index.html` (annotations from the skill)
- Modify: `videos/how-does-captchas-work-2026-05-10/anchors.txt` (any new entries the skill needs)
- Modify: `videos/how-does-captchas-work-2026-05-10/narration-map.json` (regenerated)
- Create: `videos/how-does-captchas-work-2026-05-10/compositions/sfx.html` (generated)

This is the manual acceptance pass for the entire Phase A. Per the spec:

> Verdict criterion: does the captchas video feel materially more produced
> after the SFX pass?

- [ ] **Step 1: Confirm visuals are settled**

The current captchas video is in active scaffold per
`learnings/composition-spec-over-restriction.md`. If composition work is still
in progress, **stop** — Plan 3 cannot validate against an unfinished video.
Confirm with:

```bash
grep -l "TO BE BUILT\|PLACEHOLDER" videos/how-does-captchas-work-2026-05-10/ -r
```

Expected: empty output. If anything matches, return to composition work first.

- [ ] **Step 2: Verify dependencies are landed**

```bash
test -f sound-effects/sfx-catalog.yml && echo "catalog OK"
uv run --project tools/sfx-plan sfx-plan --help && echo "tool OK"
test -f .claude/skills/sfx-author/SKILL.md && echo "skill OK"
```

All three should print "OK".

- [ ] **Step 3: Invoke the skill in a fresh conversation**

Open a new Claude Code session in the repo. Say:

> "I'm in `videos/how-does-captchas-work-2026-05-10/` and the composition is
> visually done. Add sound design to this video."

The skill should:

1. Load all inputs.
2. Print a SFX CUE PLAN in the proposal template format.
3. Wait for approval.

- [ ] **Step 4: Review and approve the plan**

Read the plan critically:

- Density ≥ 1 cue / 3s avg? ✓
- Any cue type exceeded its per-scene cap? ✗
- Any cue's `<reason>` field opaque or generic? Ask for refine.
- Does any `✗ skip` line surprise you (something you wanted scored)? Ask for refine.

Loop refines until satisfied, then approve.

- [ ] **Step 5: Audit in preview**

After the skill writes annotations and runs `tools/sfx-plan`, open the studio
URL. For each cue in the plan:

- Scrub to the cue's time.
- Confirm the cue is audible and lands on the right beat.
- Confirm the cue's character matches the moment (no boom where a tick would
  have done, no tick where the moment wanted silence).

Refines you might issue:

- "the boom in scene 3 feels late" → `data-sfx-lead-ms="-80"` on that element.
- "scene 2 is too busy" → drop one of the ticks.
- "swap the whoosh into scene 4 for a riser" → cue character change.

- [ ] **Step 6: Verdict**

Two questions, answer honestly:

1. **Does the captchas video feel materially more produced after the SFX pass
   than before?** (Compare against a saved copy of the no-SFX render.)
2. **Did the skill's plan need more than 3 refines to land?** If yes, the
   playbook needs tuning — file a follow-up to revise principles or worked
   examples.

If question 1 is "yes" and question 2 is "no," Phase A is validated.

- [ ] **Step 7: Commit the captchas SFX pass**

```bash
git add videos/how-does-captchas-work-2026-05-10/index.html \
        videos/how-does-captchas-work-2026-05-10/compositions/ \
        videos/how-does-captchas-work-2026-05-10/anchors.txt \
        videos/how-does-captchas-work-2026-05-10/narration-map.json
git commit -m "feat(captchas): sound design pass — first end-to-end SFX video"
```

If the verdict was "needs work," do *not* commit; file a follow-up plan to
revise the skill's playbook and re-run.

---

## Self-review against the spec

Spec coverage check (Component 2 — the skill):

- ✅ Inputs the skill always reads — SKILL.md Task 2
- ✅ `data-sfx-*` attribute contract — referenced in SKILL.md Task 4, anchored
  in the Plan 2 implementation
- ✅ Placement principles (not rules) — SKILL.md Task 3
- ✅ Technical floors (mix-craft physics) — SKILL.md Task 3
- ✅ Cue character library — SKILL.md Task 3 + `reference/cue-vocabulary.md`
  (Task 6)
- ✅ Worked examples — `reference/worked-examples.md` (Task 7)
- ✅ Proposal-then-confirm review checkpoint — SKILL.md Task 4 +
  `reference/proposal-template.md` (Task 9)
- ✅ Refine loop — SKILL.md Task 4
- ✅ Anchor extension flow (`anchors.txt` → re-run narration-map) —
  `reference/anchor-discipline.md` (Task 8) + SKILL.md "After approval"
- ✅ Skill's checklist (10 steps) — SKILL.md Task 4
- ✅ Project CLAUDE.md update — Task 10
- ✅ Manual acceptance against captchas — Task 11

Placeholder scan: no `TBD`, `TODO`, or "fill in details" left.

Type consistency: the `data-sfx-*` attribute set named in SKILL.md (Task 2,
Task 4) matches Plan 2's `Annotation` dataclass fields (anchor, anchor_index,
cue, lead_ms, volume, pan, is_hook). The cue names (`ui-tick`, `whoosh`,
`boom`, `riser`, `pop`) are consistent across SKILL.md, `cue-vocabulary.md`,
and Plan 1's `cues.py`.

**Anti-pattern guard reaffirmed:** the playbook in Task 3 is principles + floors
+ vocabulary + examples — not a class-to-cue mapping table. If implementation
adds one, push back and remove it.

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-11-sfx-author-skill-plan.md`. Two execution options:

**1. Subagent-Driven (recommended)** — fresh subagent per task, review between tasks.

**2. Inline Execution** — batch execution with checkpoints in this session.

This is Plan 3 of 3. Recommended execution order:

1. `docs/superpowers/plans/2026-05-11-sfx-catalog-plan.md` (catalog must exist before anything reads it).
2. `docs/superpowers/plans/2026-05-11-sfx-plan-tool-plan.md` (the tool the skill will invoke).
3. `docs/superpowers/plans/2026-05-11-sfx-author-skill-plan.md` (this plan).
