---
name: script-writer
description: Guided generator that turns a topic + research notes into a TTS-ready video script in the project's house style. Use this skill whenever the user wants to write, draft, plan, or outline a script for a hyper-frames video — phrases like "write a script about X", "I want to make a video on Y", "draft a voiceover about Z", "outline a video on W", or "let's do a video on V" should all trigger it. Also use when the user mentions starting a new video folder under `videos/`, since this skill handles folder scaffolding too. The skill encodes a writing voice, not a structural recipe; it does NOT impersonate any creator.
---

# script-writer

You are guiding the user through writing a single video script in the project's house style. The style is a voice — sentence rhythm, "But" pivots, three-part lists, personification, named concepts, dated incidents as evidence, 170 wpm. It is **not** a structural template. The script's shape emerges from the topic's substrate, not from a pre-decided arc. And the voice **serves** comprehension — it never substitutes for it: a passage that sounds right but leaves its mechanism unclear has failed, however clean the cadence. The skill works in **two passes** — a first pass for voice and retention (Steps 1–4c), then a second **comprehension pass** (Step 4d) that cold-reads the finished script and rewrites anything a first-time viewer couldn't follow.

Read this whole file before you start. Then load the reference files only when their step calls for them.

## What this skill does and doesn't do

**Does:**
- Interview the user for the topic, substrate notes, and target runtime.
- Create or open `videos/<slug>-<YYYY-MM-DD>/` and write artifacts there.
- Distill the user's research into a short notes file of materials (named concepts, dated incidents, concrete numbers, named people and organizations, the emotionally load-bearing moments).
- Draft the body of the script as one continuous prose pass against the voice rules, then carve the hook from the body, then write the landing.
- TTS-proof every sentence as it's written, not as a post-pass.
- Extract anchor words for the project's `tools/narration-map/` workflow.
- Run a second comprehension pass over the assembled script — dispatch a `script-comprehension-auditor` sub-agent (a cold reader standing in for a first-time viewer) that flags every mechanism a newcomer couldn't follow and proposes plain-language rewrites, applied under the user's approval.
- Dispatch a fact-verifier sub-agent after the script is approved end-to-end.
- Append newly discovered TTS failures to `reference/tts-gotchas.md` so the next video benefits.

**Does not:**
- Force the script into a pre-decoded arc, beat list, or escalation cycle count. Structure emerges from substrate.
- Use literal phrase prescriptions ("Today we are going to look at...", "Let's start with...", "But here is where the nightmare begins.", "The next time you...") as required openings. Those are moves available when the prose naturally arrives at them — never mandates.
- Generate compositions, run `hyperframes preview`, or invoke media commands. After `script.md` lands, the user runs the existing TTS / transcript / animation flow.
- Add CTAs ("smash subscribe"), editorial chrome (scene labels, timecodes, "PART 01 · TITLE" strips), or persona overlays. The project's `CLAUDE.md` forbids those, and the voice doesn't use them.
- Impersonate any creator. The voice rules are documented stylistic moves; the skill encodes the moves, not the person.

## Reference files (loaded on demand, not all at once)

```
reference/
├── sentence-rhythm.md            voice moves (1-in-5 short, "But", three-part lists, max-22-word, personification)
├── tts-gotchas.md                living list of TTS landmines + rewrites (the only file you append to during a session)
├── example-passages.md           real excerpts grouped by move type — read for cadence references
├── rhythm-and-retention.md       why the voice moves hold attention — read to reason about retention deliberately
└── personal-context-bridges.md   tactics for finding the Move 10 "you've done this" bridge
```

There is **no** loadable beat arc, escalation-cycle template, or per-beat scaffold. That kind of structural preset was deliberately removed — see `learnings/script-writer-spec-over-restriction.md` for why. If you want the historical analysis of the 9-beat "iceberg" arc that earlier videos drew on, it lives at `research/pawel-code-stuff/analysis/script-patterns.md` as research, not as a skill preset. `rhythm-and-retention.md` is explanation, not a preset — it explains the *why* behind moves the other files already define, and adds no moves of its own.

Load `sentence-rhythm.md` and `tts-gotchas.md` once before any prose drafting starts and keep them in mind for the rest of the session. Load `example-passages.md` whenever you want a concrete cadence reference for a specific move (openings, transitions, synthesis-style sentences, landings). Load `rhythm-and-retention.md` when you want to reason about *why* a move holds attention rather than apply it on feel, and `personal-context-bridges.md` when hunting the Move 10 bridge — both are optional, never required for a draft, and neither changes what gets written.

Two external references live outside this skill. The repo-root **`docs/creator-patterns.md`** — a cross-channel corpus synthesized from 237 transcripts of proven tech-explainer and Shorts creators. Consult it the way you consult `example-passages.md`: as a *menu of references*, never a template to fill. Its **§1 (hook taxonomy)** and **§5 (title formulas)** are the most useful here when shaping the open in Step 4b, and its **§3.8 (measured pacing bands)** for the reset-cadence reasoning in Step 4. Note its CTA section (§4) is about **Shorts**, not this skill — long-form scripts stay CTA-free per the house rules below. §3.8 distils the repo-root **`pacingInspo/`** library (17 per-video scene-change × narration studies) into per-register bands — cuts/min, median-scene, and longest-hold ceilings for the chaptered-explainer / sectioned-talking-head / fast-essay / vertical-Short registers. **Consult §3.8 first** to place the script's register and read its ceiling; drill into `pacingInspo/README.md`'s Quick index + the one matching entry block only when you want a specific video's texture, and **never load a raw `<slug>-pace.json`** (its per-scene transcript text floods context). It grounds Step 4's numbers in measurement instead of feel — evidence, not a target; never pace a script to *match* a reference channel's numbers.

## The flow

This is a guided, interactive flow. The checkpoints exist because the project's writing standard is high and substrate mistakes early in the process compound.

### Step 1 — Collect inputs

Prompt the user for, in order:

1. **Topic.** One line. Example: "why is rendering text so complicated", or "how does a database B-tree work".
2. **Research notes.** Mandatory — the substrate is non-negotiable. Accept either:
   - A path to a file, folder, or URL the skill should read. Read it with `Read`/`Bash`/`WebFetch` as appropriate. If it's a folder, list the contents and read what looks relevant.
   - Pasted-in-chat text. Take it as-is.
   - If the user says they have neither, push back — the skill cannot invent material it doesn't have. Without substrate, every concrete claim becomes a hallucination risk. Don't proceed without it.
3. **Target runtime.** Default 5 minutes. Offer 3 / 5 / 7 / 10 as options. The runtime drives target word count (~170 words per minute). Don't translate runtime into a structural prescription — long videos aren't more cycles, they're more depth on whatever the substrate genuinely contains.

### Step 2 — Slug and folder

Propose a kebab-case slug derived from the topic. Keep it short (3–5 words max — `password-hashing-slow`, not `why-good-password-hashing-is-intentionally-slow`). Confirm with the user.

Once confirmed, run the canonical bootstrap. It's **idempotent** — if the folder already exists (e.g. another skill scaffolded it earlier in the pipeline), skip `mkdir` and `npx hyperframes init` entirely:

```bash
# from the repo root — skip if folder already exists
if [ -d "videos/<slug>-<YYYY-MM-DD>" ]; then
  cd videos/<slug>-<YYYY-MM-DD>
  echo "Folder already exists. Skipping mkdir + hyperframes init."
else
  mkdir -p videos/<slug>-<YYYY-MM-DD>
  cd videos/<slug>-<YYYY-MM-DD>
  npx hyperframes init
fi
```

Use today's date. The project's `CLAUDE.md` is strict about this folder convention — never author files at the repo root. All subsequent writes go into the new folder.

If the folder existed already, do not overwrite any files in it (`substrate-notes.md`, `script.md`, etc.) without asking the user first.

### Step 2.5 — SEO research checkpoint

Before substrate distillation, give the user the option to run SEO research on the topic. The data informs which searchable nouns the working title should anchor on, which framings are saturated by recent incumbents, and how much hook-time top performers have to play with.

Probe `<video-dir>/seo/research.json`:

- **Present** → load it. Print one line: `Using existing seo/research.json (generated <date>, topic: '<topic>').` Continue to Step 3.
- **Missing** → ask once: `"Want to run SEO research on '<topic>' before drafting? Will surface searchable nouns, demand phrases, and what incumbents already cover, so the framing can differentiate. (~25s, no API key) [Y/n/skip]"`
  - **Y** → invoke the `youtube-seo-research` skill via the `Skill` tool. It runs the research and prints its 5-line digest. Continue to Step 3 with the JSON loaded.
  - **n / skip** → continue to Step 3 without SEO data. Don't re-prompt later in this session.

Never block on missing or declined research. The script can be drafted without it; SEO data only informs choices.

### Step 3 — Substrate distillation

Read all the substrate the user provided — every file, URL, pasted block. This is the only invention boundary the skill has. Anything outside substrate is invention; anything inside it is material.

Produce a short notes file `<video-dir>/substrate-notes.md` (≤30 lines). This **replaces** the old `outline.md`. It is not a structure; it is a list of materials.

Format:

```markdown
# <topic> — substrate notes

Runtime target: <N> min · ~<N×170> words

## Named concepts
- <concept> — <one-line gloss from substrate>
- ...

## Real dated incidents
- <year>, <what happened>, <named system / organization / person>
- ...

## Concrete numbers and figures
- <number> <units> — <what it measures, where it came from>
- ...

## Named people and organizations
- <name> — <role / why they matter to this topic>
- ...

## Load-bearing moments
The one or two beats in the substrate that feel emotionally heavy — the moment that, if cut, makes the rest feel weightless. Note them in one line each:
- <moment> — <why it lands>
```

If the SEO research was loaded in Step 2.5, append a 3-line `## SEO context` section: top searchable nouns to bias the working title toward, any saturation warnings, hook-time budget.

Show `substrate-notes.md` to the user. Single approval gate. Invite the user to add things you missed — they may know the substrate has a paper, a person, or an incident you didn't surface. Iterate until they approve.

**Do not draft prose from anything not in `substrate-notes.md`.** If during drafting you find yourself reaching for an incident or number that isn't in the notes, stop. Either it's in the substrate and needs to be added to the notes, or it's invention and needs to be cut.

**Mechanism claims about named real systems need primary evidence.** When the script will assert *how a specific named product behaves* — "Claude Code's cap is a fixed window", "Nginx queues requests", "Stripe caps near 100/s" — that claim is load-bearing: the whole explanation is built on it, and getting it wrong means rewriting the section. Verify it against *primary or authoritative* sources — official docs, the product's own UI/dashboard, the source — not a blog summary or secondhand explainer. Blog posts paraphrase, and they routinely blur exactly the distinction the script hangs on (fixed vs rolling window, queue vs drop). If the user shows you primary evidence (a screenshot of the product's own UI, an official doc), trust it over any secondary summary that contradicts it. Record the verified behaviour in `substrate-notes.md` so the draft rests on it.

### Step 4 — Body draft, single pass

Before drafting, load `reference/sentence-rhythm.md` and `reference/tts-gotchas.md`. Those rules apply to every sentence you write from here forward.

Draft the **body of the script** as one continuous prose pass. Not beat by beat. Not in labeled segments. Continuous prose.

The model has in context:
- The substrate notes.
- `sentence-rhythm.md` (voice moves).
- `tts-gotchas.md` (TTS landmines).
- `reference/example-passages.md` for cadence references when needed.
- `reference/rhythm-and-retention.md` when you want to reason about *why* a move holds attention — optional, explanation only, adds no moves.

The explicit drafting instruction:

> Treat the voice rules in `sentence-rhythm.md` as the bar. Invent worldbuilding — but only from substrate. Use real dated incidents, named systems, personified verbs. **Do not draft to a pre-decided arc. Do not use beat labels. Do not force the topic into "naive → flaw → smarter → new flaw" cycles unless the substrate genuinely has that chain.** Write continuous prose that follows the natural shape of the topic. If the topic has a real chain of broken-then-fixed solutions, the chain emerges in the prose. If the topic is a process walk-through, walk through the process. If the topic is a single counterintuitive fact, deepen the fact. The structure is whatever the substrate naturally wants to become.

Target word count: runtime × 170. A 5-min script is ~900 words of body (the hook and landing add maybe 60–100 more). Don't pad. Don't condense.

**Retention discipline — two measured failure modes, framed as discipline, not arc.** A real video on this channel lost half its viewers by 0:42 and shed most of the rest across one ~2.5-minute subtopic that dragged. Both are failures of moves this skill already has, applied on a cadence:

- *The slow open.* The body must already be paying off the moment Step 4b's cold open hands into it — so draft the first paragraph of the body to land a concrete beat fast, not to clear its throat. (The opening *line* is governed by Step 4b's cold-open rule.)
- *The dragging subtopic.* No single idea should run much past ~45–60 seconds (~130–170 words) without a **reset move** firing — a short declarative (Move 1), a "But / Then / Turns out" pivot (Move 2), a newly *named* concept (Move 6), or a concrete analogy. If the substrate forces a long subtopic (>~90s / ~250 words), it naturally falls into a few sub-beats, each ending on the complication that pulls into the next; let that chain emerge rather than narrating one flat block. This is the existing reset moves on a cadence — **not** a beat template, not a "reset at 25%/50%/75%" checklist. `reference/rhythm-and-retention.md` explains why; `docs/creator-patterns.md` §3 shows twelve channels doing it, and its **§3.8** distils the `pacingInspo/` library into measured per-register bands (a chaptered diagram explainer holds one evolving canvas 100s+ between resets; a fast essay cuts every ~1–3s; a vertical Short cuts sub-1.5s). Read the §3.8 band for the script's register first to see where the hold ceiling actually sits, then drill into the matching `pacingInspo/README.md` entry only when you want a specific video's texture.

**Phrase moves are optional, not required.** Phrases like "Today we are going to look at...", "Let's start with...", "But here is where the nightmare begins.", "The next time you..." are available moves — use them only when the prose naturally arrives at the moment they fit. Forcing them into a script that didn't earn them produces the script-layer chrome the audience can feel.

After the body is drafted, show the **full body** to the user. Single approval gate at the body level. No per-beat checkpoints inside the body. If the user redirects — different shape, different emphasis, missing the load-bearing moment — revise the body and re-show. Iterate until they approve.

Draft for voice and retention here — do **not** also try to bullet-proof every mechanism for a first-time viewer in this pass. That is Step 4d's job, and keeping the two concerns apart is deliberate: it stops the comprehension worry from flattening the voice mid-draft.

### Step 4b — Hook carved from body

Read the approved body. Pick the body's strongest concrete moment — usually a specific dated incident, a counterintuitive fact, or a named system whose existence makes the topic feel urgent. Write a hook (1–3 sentences, opening sentence 8–14 words) that makes that moment feel inevitable when the body reaches it.

These heuristics sharpen *which* moment to pick and *how* to shape the opening — they are selection logic for the decision this step already asks for, not a hook template:

- **Specificity over scale.** A specific, verifiable detail beats a big abstract claim. "This 8-pixel-tall letter" pulls harder than "text rendering is incredibly complex." A number the viewer can picture beats a superlative they can't.
- **Anchor to the viewer's familiar frame.** The strongest hooks start from something the viewer already knows or does, then turn it strange. An everyday object made unfamiliar is sharper than a fact introduced cold.
- **The gap between expectation and reality.** The moment that hooks is usually the one where what's true contradicts what the viewer assumes. Pick the beat with the widest gap between "what you'd think" and "what actually happens."
- **The compression test.** A working hook compresses to 8–12 words and still makes the viewer want the rest. If the strongest moment can't be said that short, it isn't a hook yet — it's a setup. This is the selection logic behind the 8–14 word opening sentence the step already asks for.
- **Withhold the conclusion.** When the body's thesis is a "quiet-dominance" claim — *X secretly runs everything*, *Y is everywhere* — open it as a withheld mystery or paradox, not a flat assertion. "How did a language built in ten days end up running the world?" pulls harder than "JavaScript is everywhere," because the flat version answers the question the hook should make the viewer *ask*. State the dependency, withhold the name; pose the paradox, defer the resolution to the body. (Corpus: `docs/creator-patterns.md` §1.1, §1.9.)
- **Hook and working title restate each other.** The viewer clicked a title; the first line must confirm within ~10 seconds that they're in the right place. Write the opening line and the working title as a pair — one promise phrased two ways.

The hook is carved from the body, not written before it. This is the 2026 YouTube scripting best practice: write the body first, then find the strongest beat inside it and shape an opening that pays it off.

**The opening line is a cold open.** Whatever beat you pick, the *first line of the script is the hook itself* — a claim, a number, a question, or a concrete scene — and its concrete image lands inside the first ~10 seconds (~25–30 spoken words at 170 wpm). Never a frame-setting ramp ("Today we are going to look at…", "In this video…"), never a greeting, never a self-introduction or credentials, never branding. Anything the topic needs to set up comes *after* the hook has earned it, never before tension exists. If your cold open is a concrete scene, the script owes that scene an explicit callback at the close — a loop you open, you close. Across all 237 transcripts in `docs/creator-patterns.md`, not one strong video opens any other way.

Show, approve.

### Step 4c — Landing

Pick a landing archetype based on what the body actually delivered:

- **Prescription** — "If you are X, do Y. If you are A, do B." Best when the body produced an actionable conclusion.
- **Philosophical line** — one aphoristic sentence about the nature of the field. Best when the body produced a counterintuitive insight that wants a frame.
- **Vivid scale** — a sensory close that names the scale of what was just explained. Best when the body's scale itself is the punchline.

Default to prescription if the topic supports it. Use vivid scale otherwise. Use philosophical only when the body's substance earns it.

20–35 words. No CTA. No "smash subscribe". No "let me know in the comments". The project's audience reads CTAs as channel-decay; keep the script pure.

Show, approve. Assemble the final `script.md`:

```markdown
<!-- HOOK -->
<hook prose>

<!-- BODY -->
<body prose>

<!-- LANDING -->
<landing prose>
```

The HTML comments are anchors for downstream tools, not voiceover text. The script reads as one continuous piece of writing from open to close.

**Optional — story spine.** The script is now approved end-to-end: you have the hook (Step 4b carved it from the body's strongest concrete moment), the body, and the landing. If this video is going through the full pipeline (motion, SFX, music), you may offer the user a `story-spine.md`: *"Want me to drop a 3–4 line `story-spine.md` in the folder? It records where the hook beat, the climax, and the landing landed — the motion, SFX, and music skills can read it later so all three point at the same beat. It's optional; nothing downstream requires it."* If the user says yes, load `reference/story-spine.md` and write the file in the strict shape it defines — 3–4 lines, quoted script phrases, descriptive glosses, never a per-scene list. If the user declines or doesn't reply, skip it; the video is not broken without one. Never write it unprompted, and never before the script is approved.

### Step 4d — Comprehension pass (the second pass)

The script is now voice-complete: hook, body, and landing assembled into `script.md`. That was the first pass — it made the script *sound* right and *hold* attention. The second pass makes it *understood*. These are different jobs, and separating them is deliberate: folding "could someone who's never seen this follow it?" into the first draft flattens the voice, so the comprehension work waits until the voice is locked.

Dispatch the `script-comprehension-auditor` sub-agent via the `Agent` tool. It runs in its own context window and reads the script **cold** — as someone who has never seen the topic — which is exactly the perspective the writer (saturated in the substrate, attached to their own clever lines) cannot fake. For every mechanism the script explains, it applies the rubric:

- **Concrete before elegant** — each non-obvious mechanism earns a literal, picturable analogy (a bucket of ten tokens, a bouncer with a clicker, two labeled jars) on first mention; abstract description alone ("the counter ticks down at a steady rate") is not enough.
- **A worked example for anything counterintuitive** — a behaviour that's easy to get backwards gets one case traced with real numbers, not just described.
- **Clever lines cap, they don't carry** — an aphoristic reveal that is the *only* place an idea is taught reads as filler to a viewer who never got the literal version; flag it.
- **The re-explain test** — could you re-explain each mechanism using only what the script gives the viewer? If not, it's missing a picture or an example.

Dispatch:

```
Agent(
  description: "Comprehension-audit the assembled script",
  subagent_type: "script-comprehension-auditor",
  prompt: "Cold-read the assembled script at <absolute-path>/script.md as a first-time viewer. Substrate notes are at <absolute-path>/substrate-notes.md — use them to keep any proposed analogy or worked example faithful to the real mechanism and free of invented facts. Write <absolute-path>/comprehension-pass.md per your format and return the one-paragraph summary."
)
```

The agent writes `comprehension-pass.md` — each opaque passage quoted, where a newcomer stalls, and a proposed plain-language rewrite in the house voice — and returns a summary. **It never edits the script.** Read the summary, then walk the user through the findings:

> *"Comprehension pass: N blocking, M slowing, P polish (see `comprehension-pass.md`). The blocking ones — <named passages> — are spots a first-time viewer would lose the thread. Want me to apply the proposed rewrites (all / select), or leave any?"*

Apply the approved rewrites to `script.md` yourself with `Edit`, preserving voice and TTS-safety, then re-show the touched passages. The blocking findings are the bar: the script isn't done while a mechanism a newcomer can't follow is still in it. The slowing and polish findings are the user's call.

If a `story-spine.md` was written in Step 4c and an applied rewrite changes a phrase it quotes, update the spine to match.

### Step 5 — Anchor extraction

Once the script is approved end-to-end, scan it for the named-noun moments — the abstractions, named concepts, and incident names that the script promotes. These are the anchor words the project's `tools/narration-map/` workflow needs.

Write them to `anchors.txt` in the same folder, one phrase per line, with optional `#` comment headers to group them by where they appear in the script. Format:

```
# Hook
You open

# Body — rasterization
rasterization
staircase effect

# Body — hinting
hinting
12-point font

# Landing
The next time you read
```

Pick the 10–25 phrases that are genuinely the spine of the video. Don't try to be exhaustive — the user will edit this file before running `narration-map`.

### Step 6 — TTS-gotcha learning loop

Throughout the session, if the user says something like "the TTS will mangle this" or "we got 'lives' wrong last time" or "kokoro pronounces TLS weirdly", do two things:

1. Rewrite the offending line in the current script.
2. Append the gotcha to `reference/tts-gotchas.md` under the appropriate section (or create a new section if needed). Include the failing token, the failure mode, and the rewrite recipe. This is the only reference file you ever modify; it grows over time and the next video benefits.

### Step 7 — Fact-verifier dispatch

After the script is approved end-to-end, dispatch the `script-fact-verifier` sub-agent via the `Agent` tool. The agent runs in its own context window, reads the script, extracts every concrete claim, sources via WebSearch, and writes `<video-dir>/fact-check.md`.

Dispatch:

```
Agent(
  description: "Fact-check the approved script",
  subagent_type: "script-fact-verifier",
  prompt: "Fact-check the approved script at <absolute-path>/script.md. Substrate notes the writer used are at <absolute-path>/substrate-notes.md — prefer those as sources when they support the claim, but verify against the open web regardless. Write <absolute-path>/fact-check.md per your usual format and return the one-paragraph summary."
)
```

The agent's summary paragraph comes back as the tool result. Read it, then frame the hand-off prompt to the user:

> *"Script is locked. `script-fact-verifier` found N verified, M partial, P unverified, Q contradicted claims (see `fact-check.md`). The top load-bearing claims to look at: <named claims from the summary>. Want to address those before voiceover, or proceed?"*

Advisory only — never block voiceover hand-off. The user decides whether to revise.

## Done condition

You're done when:

- `videos/<slug>-<YYYY-MM-DD>/` exists with `substrate-notes.md`, `script.md`, `anchors.txt`, `comprehension-pass.md`, and `fact-check.md`.
- The user has approved the body, hook, and landing.
- The script reads at the target runtime (count words / 170 to verify).
- The comprehension pass has run, and every blocking finding is either fixed or explicitly waved off by the user.
- The fact-verifier has run and the user has been told whether to revise before voiceover.
- Any TTS gotchas surfaced during the session have been appended to `reference/tts-gotchas.md`.

`story-spine.md` is **not** in this list. It is an optional artifact offered in Step 4c — its absence is never a gap, and the skill is done whether or not the user accepted the offer.

Once the script is locked and the fact-check report has been surfaced, ask the user: *"Want me to generate the voiceover with ElevenLabs v2 now? (invokes the `voiceover-elevenlabs-v2` skill — long-form stable, our project default. Pass `with v3` if you need the audio-tag path instead.)"* If the user replies affirmatively, hand off to `voiceover-elevenlabs-v2`. If they reply `with v3`, hand off to `voiceover-elevenlabs-v3` instead. Both skills produce `audio/voiceover.mp3` and `transcript.json` in one run. If the user declines both, tell them the next step is theirs (`uv run --project ../../tools/voiceover-elevenlabs-v2 voiceover-elevenlabs-v2 voiceover.txt`), then run `narration-map` with `anchors.txt`. This skill stops at the script + fact-check pair.

## Voice the house style favors

These are the moves the project's voice keeps reaching for. They are not required; they are available. Each one lands when the prose naturally arrives at the moment that asks for it. None of them should appear on cue.

- **170 wpm.** A 5-min script is ~900 words, not "as much as you can say in 5 minutes". Word-count discipline keeps the visual system room to breathe. *When not to use:* never — this is a hard rule of the pipeline.
- **1 in 5 sentences ≤ 6 words.** After a long explanatory sentence, follow with a 4–6 word declarative that names what was just explained. *When not to use:* if every short sentence in your draft feels like padding rather than rhythm work, you've over-applied it — back off.
- **"But" not "however".** The hard single-syllable "but" is doing rhythmic work. *When not to use:* don't open more than one sentence per ~150 words with "But" or the move loses its hinge feel.
- **Name everything.** Give each abstraction a noun the viewer can repeat at lunch. *When not to use:* don't invent names that aren't in the substrate. If the substrate calls it "the staircase effect", use that; don't coin "the jaggies problem" because it sounds better.
- **Three-part lists at every scale.** Thesis sentences, evidence sentences, even adjective stacks. *When not to use:* if the topic genuinely has two cases or four, force-fitting a third is invention. Use two or four.
- **Personify systems.** Fonts that *survive* transitions. Hashes that *stand at the gate*. *When not to use:* on systems where the personification would feel cute rather than load-bearing — a network packet doesn't need a character arc.
- **Analogy as a comprehension reset.** One concrete physical analogy per abstract mechanism on first mention — "a fire hose into a garden hose", "the hash stands at the gate". It doubles as a frame-change that re-grabs attention right where a dry stretch threatens to drag (one of the reset moves in Step 4's pacing band). *When not to use:* don't stack analogies on a concept that's already concrete, and never let the analogy drift from the substrate's actual mechanism.
- **Concrete numbers and dated incidents.** Always from substrate. *When not to use:* if the substrate didn't surface a number or incident for a claim, the claim has to be softened or cut — never invented.
- **Phrase moves as cadence options, not openings.** *"Today we are going to look at..."*, *"Let's start with..."*, *"But here is where the nightmare begins."*, *"The next time you..."* — these landed in the earlier videos because the prose naturally arrived at them. *When not to use:* never as a required opening line. Never as a forced transition. If the prose around them doesn't earn the phrase, the phrase exposes the recipe.
- **First-person plural collegial.** "We obsess over milliseconds." *When not to use:* don't use first-person singular — no "I think", no "in my opinion".
- **No CTA, no scene labels, no chapter language in voiceover.** The script reads as one continuous piece of writing. The audience treats CTAs as channel-decay.

## Pushback expected from the project's audience

The research found three recurring criticisms. Bake the mitigations into your drafting:

1. **Pacing too fast on dense moments.** Budget at least 45 seconds of script per technical concept the viewer hasn't seen before. If a complex idea is condensed into 15 seconds, expand it. The paired ceiling: don't run *longer* than ~45–60 seconds on one idea without a reset move (short declarative, "But" pivot, a newly named concept, an analogy). Floor of 45s per concept, ceiling of ~60s before a reset — together they set the pacing band. The dragging-subtopic failure (a real video lost its back half to a ~2.5-min un-reset block) is a ceiling violation; see Step 4's retention discipline.
2. **Strong general claims without qualifiers.** "X is a vulnerability" gets corrected. "X is a vulnerability *when paired with Y*" doesn't. Add the qualifier proactively when the claim could be expert-pushed-back-on.
3. **No personal context bridge.** At least once per video, connect to something the viewer has done themselves ("you've moved your mouse to generate a key in VeraCrypt — that's why"). One bridge in the hook or the landing is usually enough. When hunting that bridge, `reference/personal-context-bridges.md` has tactics for finding it.
