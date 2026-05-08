---
name: script-writer
description: Guided generator that turns a topic + research notes into a TTS-ready video script in the project's house style (the 9-beat "iceberg" arc — mundane action revealed as unsuspected depth). Use this skill whenever the user wants to write, draft, plan, or outline a script for a hyper-frames video — phrases like "write a script about X", "I want to make a video on Y", "draft a voiceover about Z", "outline a video on W", or "let's do a video on V" should all trigger it. Also use when the user mentions starting a new video folder under `videos/`, since this skill handles folder scaffolding too. The skill encodes a writing style; it does NOT impersonate any creator.
---

# script-writer

You are guiding the user through writing a single video script in the project's house style. The style is documented in detail in `research/pawel-code-stuff/analysis/script-patterns.md` — the canonical 9-beat arc with TTS-aware sentence rhythm. This skill is the operational version of that analysis: a guided, checkpointed flow that ends in a `script.md` ready for TTS.

Read this whole file before you start. Then load the reference files only when their step calls for them.

## What this skill does and doesn't do

**Does:**
- Interview the user for the topic, notes, and target runtime.
- Create a fresh `videos/<slug>-<YYYY-MM-DD>/` folder, run `npx hyperframes init` inside it, and write artifacts there.
- Draft a 9-beat outline, get approval, then draft the script beat by beat with checkpoints.
- TTS-proof every sentence as it's written, not as a post-pass.
- Extract anchor words for the project's `tools/narration-map/` workflow.
- Append newly discovered TTS failures to `reference/tts-gotchas.md` so the next video benefits.

**Does not:**
- Generate compositions, run `hyperframes preview`, or invoke media commands. After `script.md` lands, the user runs the existing TTS / transcript / animation flow themselves.
- Add CTAs ("smash subscribe"), editorial chrome (scene labels, timecodes, "PART 01 · TITLE" strips), or persona overlays. The project's `CLAUDE.md` forbids those, and the script style doesn't use them.
- Impersonate any creator. The 9-beat arc is a documented writing pattern; this skill encodes the pattern, not the person.

## Reference files (loaded on demand, not all at once)

```
reference/
├── nine-beat-arc.md            beat definitions, target word counts, opener phrases, evidence patterns
├── sentence-rhythm.md          1-in-5 short-declarative rule, "But" pivot, three-part lists, max-22-word rule, personification cues
├── tts-gotchas.md              living list of TTS landmines + rewrite recipes (the only file you append to during a session)
├── example-beats.md            annotated real excerpts organized by beat — read when you need to imitate cadence
└── escalation-cycle-template.md the 4-move loop (naive → flaw → smarter → new flaw) with worked examples
```

Load `nine-beat-arc.md` once at outline time. Load `sentence-rhythm.md` and `tts-gotchas.md` once before any prose drafting starts and keep them in mind for the rest of the session. Load `escalation-cycle-template.md` when you reach beat 6. Load `example-beats.md` whenever you're drafting a beat and want a concrete cadence reference.

## The flow

This is a guided, interactive flow. Do not jump ahead — every step has a checkpoint. The checkpoints exist because the project's writing standard is high (every sentence does work) and structural mistakes early in the arc compound.

### Step 1 — Collect inputs

Prompt the user for, in order:

1. **Topic.** One line. Example: "why is rendering text so complicated", or "how does a database B-tree work".
2. **Research notes.** Accept either:
   - A path to a file, folder, or URL the skill should read. Read it with `Read`/`Bash`/`WebFetch` as appropriate. If it's a folder, list the contents and read what looks relevant.
   - Pasted-in-chat text. Take it as-is.
   - If the user says they have neither, push back gently — the skill needs *some* substrate to mine for incidents, numbers, named concepts, and the rabbit-hole arc. Don't proceed without it.
3. **Target runtime.** Default 5 minutes. Offer 3 / 5 / 7 / 10 as options. The runtime drives word count (~170 words per minute) and the number of escalation cycles in beat 6 (3 cycles for 5min, 4 for 7min, 5–6 for 10min).

### Step 2 — Slug and folder

Propose a kebab-case slug derived from the topic. Keep it short (3–5 words max — Pawel's slugs are like `password-hashing-slow`, not `why-good-password-hashing-is-intentionally-slow`). Confirm with the user.

Once confirmed:

```bash
# from the repo root
mkdir -p videos/<slug>-<YYYY-MM-DD>
cd videos/<slug>-<YYYY-MM-DD>
npx hyperframes init
```

Use today's date. The project's `CLAUDE.md` is strict about this folder convention — never author files at the repo root. All subsequent writes go into the new folder.

### Step 3 — 9-beat outline checkpoint

Load `reference/nine-beat-arc.md`. Draft a one-line outline for each of the 9 beats based on the topic + notes. Don't write prose yet — single declarative sentences only, naming what each beat does for *this* topic.

Format for `outline.md`:

```markdown
# <topic> — 9-beat outline

Runtime target: <N> min · ~<N×170> words

## 1. Familiar-action open
<one sentence: the mundane action this video opens on>

## 2. Subversion
<one sentence: the gap between the apparent simplicity and the actual depth>

## 3. Stakes
<one sentence: the broader system that depends on this thing working>

## 4. Thesis
<one sentence, ideally a three-part list: today we are going to look at why X, how Y, and what Z>

## 5. Foundation
<one sentence: the baseline concept the video will deliberately break>

## 6. Escalation cycles (×<N>)
- Cycle 1: <naive solution> → <flaw> → <smarter solution by name> → <new flaw>
- Cycle 2: <same shape>
- Cycle 3: <same shape>
- (etc. for the runtime)

## 7. Synthesis
<one sentence: the personified summary that pulls the cycles together>

## 8. Reframe
<one sentence: the next time you <opening action>, remember <new mental model>>

## 9. Closer
<one sentence: prescription, philosophical line, or vivid scale>
```

Write `outline.md` to the video folder. Show the outline to the user. Do not proceed to prose until they say it's good. If they redirect — different angle, different cycles, different stakes — revise the outline and re-show.

### Step 4 — Beat-by-beat drafting

This is the longest step. You will draft each beat as prose, show it to the user, wait for `ok` / edit instructions / `redo`, and only then move on. No beat is drafted before the previous one is approved.

Before drafting any prose, load `reference/sentence-rhythm.md` and `reference/tts-gotchas.md`. Those rules apply to every sentence you write from here forward. If you find yourself writing a sentence that violates them, fix it before showing it to the user.

The order:

| Order | Beat | Notes |
|---|---|---|
| 4a | 1. Open | 8–14 word opening sentence, present tense, second person. Often starts with "Every" or "You". |
| 4b | 2. Subversion | Use "But" as a sentence opener. Short, declarative. End with a one-sentence naming the gap. |
| 4c | 3. Stakes | Name the broader system. Use one concrete number or named incident if the notes have one. |
| 4d | 4. Thesis | Use the literal handshake "Today we are going to look at..." Make the thesis a three-part list. |
| 4e | 5. Foundation | Open with "Let's start with..." Define precisely. Name the concept. Establish the naive default. |
| 4f | 6. Escalation cycles | Load `reference/escalation-cycle-template.md`. Draft *one cycle at a time*. Each cycle = naive → flaw → smarter (by name) → new flaw. Each cycle gets its own checkpoint. |
| 4g | 7. Synthesis | Optional anaphora ("every... every... every..."), or personified description of the system "trying to" do its job. |
| 4h | 8. Reframe | "The next time you <opening action>, remember: <new mental model>." Send the viewer back to beat 1 with new eyes. |
| 4i | 9. Closer | Pick one of three archetypes: prescription, philosophical line, or vivid scale. Default to prescription unless the notes suggest otherwise. |

After the user approves each beat, append it to `script.md` under its beat header (kept as a comment so it doesn't read aloud — see the format below).

`script.md` format:

```markdown
<!-- BEAT 1: Open -->
You open a text editor, press the letter E, and it appears instantly.
...

<!-- BEAT 2: Subversion -->
But under the hood, ...
```

### Step 5 — Anchor extraction

Once the script is approved end-to-end, scan it for the named-noun moments — the abstractions, named concepts, and incident names that the script promotes (e.g., "B-tree", "rasterization", "color fringing", "Argon2", "PlayStation 3 break", "UUIDv7"). These are the anchor words the project's `tools/narration-map/` workflow needs.

Write them to `anchors.txt` in the same folder, one phrase per line, grouped by beat with `#` comment headers. Format:

```
# Beat 1 — Open
You open

# Beat 6 — Cycle 1: rasterization
rasterization
staircase effect

# Beat 6 — Cycle 2: anti-aliasing → hinting
hinting
12-point font

# Beat 8 — Reframe
The next time you read
```

This is the file the user will edit further before running `narration-map`. Don't try to be exhaustive — pick the 10–25 phrases that are genuinely the spine of the video.

### Step 6 — TTS-gotcha learning loop

Throughout the session, if the user says something like "the TTS will mangle this" or "we got 'lives' wrong last time" or "kokoro pronounces TLS weirdly", do two things:

1. Rewrite the offending line in the current script.
2. Append the gotcha to `reference/tts-gotchas.md` under the appropriate section (or create a new section if needed). Include the failing token, the failure mode, and the rewrite recipe. This is the only reference file you ever modify; it grows over time and the next video benefits.

## Drafting principles (always in effect once Step 4 starts)

- **170 wpm.** A 5-min script is ~900 words, not "as much as you can say in 5 minutes". Word-count discipline keeps the visual system room to breathe.
- **1 in 5 sentences ≤ 6 words.** After every long explanatory sentence, follow with a 4–6 word declarative that names what was just explained. Read it aloud in your head — that's the cadence test.
- **"But" not "however".** The hard single-syllable "but" is doing rhythmic work.
- **Name everything.** Give each abstraction a noun the viewer can repeat at lunch. Italicize first use in your head: *"this translation process is called rasterization"*.
- **Three-part lists at every scale.** Thesis, evidence sentences, even adjective stacks.
- **Personify systems.** Fonts that *survive* transitions, hashes that *stand at the gate*. Converts a system diagram into a story.
- **Concrete numbers and dated incidents.** "8 pixels tall", "2008 Debian OpenSSL", "PlayStation 3 break". Anchor every claim that could feel hand-wavy.
- **No "however", no "actually" as a hedge, no "kind of" / "sort of", no "I think".** First-person plural ("we") is fine and good.
- **No CTA, no chapter language, no scene labels in the script.** The script reads as one continuous piece of writing, not a slide deck.

## Pushback expected from the project's audience

The research found three recurring criticisms that aren't AI-voice. Bake the mitigations into your drafting:

1. **Pacing too fast on dense moments.** Budget at least 45 seconds of script per technical concept inside an escalation cycle. If a cycle would condense a complex idea into 15 seconds, expand it or split it into two cycles.
2. **Strong general claims without qualifiers.** "X is a vulnerability" gets corrected. "X is a vulnerability *when paired with Y*" doesn't. Add the qualifier proactively when the claim could be expert-pushed-back-on.
3. **No personal context bridge.** At least once per video, connect to something the viewer has done themselves ("you've moved your mouse to generate a key in VeraCrypt — that's why"). The veracrypt-comment moment in beat 1 or 8 is the lever.

## Done condition

You're done when:

- `videos/<slug>-<YYYY-MM-DD>/` exists with `outline.md`, `script.md`, `anchors.txt`.
- The user has approved the full script end-to-end.
- The script reads at the target runtime (count words / 170 to verify).
- Any TTS gotchas surfaced during the session have been appended to `reference/tts-gotchas.md`.

Tell the user the next step is theirs: generate the TTS audio with `npx hyperframes-media tts` (or whichever TTS the project standardizes on), drop it into `audio/`, then run the user's transcript pipeline to produce `transcript.json`, then run `narration-map` with `anchors.txt`. This skill stops at `script.md`.
