---
name: script-writer
description: Guided generator that turns a topic + research notes into a TTS-ready video script in the project's house style. Use this skill whenever the user wants to write, draft, plan, or outline a script for a hyper-frames video — phrases like "write a script about X", "I want to make a video on Y", "draft a voiceover about Z", "outline a video on W", or "let's do a video on V" should all trigger it. Also use when the user mentions starting a new video folder under `videos/`, since this skill handles folder scaffolding too. The skill encodes a writing voice, not a structural recipe; it does NOT impersonate any creator.
---

# script-writer

You are guiding the user through writing a single video script in the project's house style. The style is a voice — sentence rhythm, "But" pivots, three-part lists, personification, named concepts, dated incidents as evidence, 170 wpm. It is **not** a structural template. The script's shape emerges from the topic's substrate, not from a pre-decided arc.

Read this whole file before you start. Then load the reference files only when their step calls for them.

## What this skill does and doesn't do

**Does:**
- Interview the user for the topic, substrate notes, and target runtime.
- Create or open `videos/<slug>-<YYYY-MM-DD>/` and write artifacts there.
- Distill the user's research into a short notes file of materials (named concepts, dated incidents, concrete numbers, named people and organizations, the emotionally load-bearing moments).
- Draft the body of the script as one continuous prose pass against the voice rules, then carve the hook from the body, then write the landing.
- TTS-proof every sentence as it's written, not as a post-pass.
- Extract anchor words for the project's `tools/narration-map/` workflow.
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
├── sentence-rhythm.md      voice moves (1-in-5 short, "But", three-part lists, max-22-word, personification)
├── tts-gotchas.md          living list of TTS landmines + rewrites (the only file you append to during a session)
└── example-passages.md     real excerpts grouped by move type — read for cadence references
```

There is **no** loadable beat arc, escalation-cycle template, or per-beat scaffold. That kind of structural preset was deliberately removed — see `learnings/script-writer-spec-over-restriction.md` for why. If you want the historical analysis of the 9-beat "iceberg" arc that earlier videos drew on, it lives at `research/pawel-code-stuff/analysis/script-patterns.md` as research, not as a skill preset.

Load `sentence-rhythm.md` and `tts-gotchas.md` once before any prose drafting starts and keep them in mind for the rest of the session. Load `example-passages.md` whenever you want a concrete cadence reference for a specific move (openings, transitions, synthesis-style sentences, landings).

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

### Step 4 — Body draft, single pass

Before drafting, load `reference/sentence-rhythm.md` and `reference/tts-gotchas.md`. Those rules apply to every sentence you write from here forward.

Draft the **body of the script** as one continuous prose pass. Not beat by beat. Not in labeled segments. Continuous prose.

The model has in context:
- The substrate notes.
- `sentence-rhythm.md` (voice moves).
- `tts-gotchas.md` (TTS landmines).
- `reference/example-passages.md` for cadence references when needed.

The explicit drafting instruction:

> Treat the voice rules in `sentence-rhythm.md` as the bar. Invent worldbuilding — but only from substrate. Use real dated incidents, named systems, personified verbs. **Do not draft to a pre-decided arc. Do not use beat labels. Do not force the topic into "naive → flaw → smarter → new flaw" cycles unless the substrate genuinely has that chain.** Write continuous prose that follows the natural shape of the topic. If the topic has a real chain of broken-then-fixed solutions, the chain emerges in the prose. If the topic is a process walk-through, walk through the process. If the topic is a single counterintuitive fact, deepen the fact. The structure is whatever the substrate naturally wants to become.

Target word count: runtime × 170. A 5-min script is ~900 words of body (the hook and landing add maybe 60–100 more). Don't pad. Don't condense.

**Phrase moves are optional, not required.** Phrases like "Today we are going to look at...", "Let's start with...", "But here is where the nightmare begins.", "The next time you..." are available moves — use them only when the prose naturally arrives at the moment they fit. Forcing them into a script that didn't earn them produces the script-layer chrome the audience can feel.

After the body is drafted, show the **full body** to the user. Single approval gate at the body level. No per-beat checkpoints inside the body. If the user redirects — different shape, different emphasis, missing the load-bearing moment — revise the body and re-show. Iterate until they approve.

### Step 4b — Hook carved from body

Read the approved body. Pick the body's strongest concrete moment — usually a specific dated incident, a counterintuitive fact, or a named system whose existence makes the topic feel urgent. Write a hook (1–3 sentences, opening sentence 8–14 words) that makes that moment feel inevitable when the body reaches it.

The hook is carved from the body, not written before it. This is the 2026 YouTube scripting best practice: write the body first, then find the strongest beat inside it and shape an opening that pays it off.

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

- `videos/<slug>-<YYYY-MM-DD>/` exists with `substrate-notes.md`, `script.md`, `anchors.txt`, and `fact-check.md`.
- The user has approved the body, hook, and landing.
- The script reads at the target runtime (count words / 170 to verify).
- The fact-verifier has run and the user has been told whether to revise before voiceover.
- Any TTS gotchas surfaced during the session have been appended to `reference/tts-gotchas.md`.

Once the script is locked and the fact-check report has been surfaced, ask the user: *"Want me to generate the voiceover with ElevenLabs v2 now? (invokes the `voiceover-elevenlabs-v2` skill — long-form stable, our project default. Pass `with v3` if you need the audio-tag path instead.)"* If the user replies affirmatively, hand off to `voiceover-elevenlabs-v2`. If they reply `with v3`, hand off to `voiceover-elevenlabs-v3` instead. Both skills produce `audio/voiceover.mp3` and `transcript.json` in one run. If the user declines both, tell them the next step is theirs (`uv run --project ../../tools/voiceover-elevenlabs-v2 voiceover-elevenlabs-v2 voiceover.txt`), then run `narration-map` with `anchors.txt`. This skill stops at the script + fact-check pair.

## Voice the house style favors

These are the moves the project's voice keeps reaching for. They are not required; they are available. Each one lands when the prose naturally arrives at the moment that asks for it. None of them should appear on cue.

- **170 wpm.** A 5-min script is ~900 words, not "as much as you can say in 5 minutes". Word-count discipline keeps the visual system room to breathe. *When not to use:* never — this is a hard rule of the pipeline.
- **1 in 5 sentences ≤ 6 words.** After a long explanatory sentence, follow with a 4–6 word declarative that names what was just explained. *When not to use:* if every short sentence in your draft feels like padding rather than rhythm work, you've over-applied it — back off.
- **"But" not "however".** The hard single-syllable "but" is doing rhythmic work. *When not to use:* don't open more than one sentence per ~150 words with "But" or the move loses its hinge feel.
- **Name everything.** Give each abstraction a noun the viewer can repeat at lunch. *When not to use:* don't invent names that aren't in the substrate. If the substrate calls it "the staircase effect", use that; don't coin "the jaggies problem" because it sounds better.
- **Three-part lists at every scale.** Thesis sentences, evidence sentences, even adjective stacks. *When not to use:* if the topic genuinely has two cases or four, force-fitting a third is invention. Use two or four.
- **Personify systems.** Fonts that *survive* transitions. Hashes that *stand at the gate*. *When not to use:* on systems where the personification would feel cute rather than load-bearing — a network packet doesn't need a character arc.
- **Concrete numbers and dated incidents.** Always from substrate. *When not to use:* if the substrate didn't surface a number or incident for a claim, the claim has to be softened or cut — never invented.
- **Phrase moves as cadence options, not openings.** *"Today we are going to look at..."*, *"Let's start with..."*, *"But here is where the nightmare begins."*, *"The next time you..."* — these landed in the earlier videos because the prose naturally arrived at them. *When not to use:* never as a required opening line. Never as a forced transition. If the prose around them doesn't earn the phrase, the phrase exposes the recipe.
- **First-person plural collegial.** "We obsess over milliseconds." *When not to use:* don't use first-person singular — no "I think", no "in my opinion".
- **No CTA, no scene labels, no chapter language in voiceover.** The script reads as one continuous piece of writing. The audience treats CTAs as channel-decay.

## Pushback expected from the project's audience

The research found three recurring criticisms. Bake the mitigations into your drafting:

1. **Pacing too fast on dense moments.** Budget at least 45 seconds of script per technical concept the viewer hasn't seen before. If a complex idea is condensed into 15 seconds, expand it.
2. **Strong general claims without qualifiers.** "X is a vulnerability" gets corrected. "X is a vulnerability *when paired with Y*" doesn't. Add the qualifier proactively when the claim could be expert-pushed-back-on.
3. **No personal context bridge.** At least once per video, connect to something the viewer has done themselves ("you've moved your mouse to generate a key in VeraCrypt — that's why"). One bridge in the hook or the landing is usually enough.
