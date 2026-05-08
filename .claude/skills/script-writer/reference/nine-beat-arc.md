# The 9-beat arc

Every script in the house style follows the same nine beats, with minor reordering for topic-specific reasons. Times are approximate and apply to a 5–6 min video; longer runtimes extend beat 6 (escalation cycles) but keep the rest of the arc intact.

## Why this arc works

The viewer signs up for a rabbit hole at beat 4 (the thesis). Beats 5–6 deliver the rabbit hole. Beats 7–8 close the loop by sending the viewer back to the everyday action from beat 1 with a new mental model. The arc is essentially: *here's something you do every day → here's why it's secretly a hard problem → here's the chain of clever-and-broken solutions engineers came up with → here's how to think about it now*.

The arc is invariant. The thing that changes with runtime is how many escalation cycles you can fit in beat 6.

## The table

| Beat | Function | Length (5min) | Length (10min) |
|---|---|---|---|
| 1. Familiar-action open | Place viewer inside a relatable everyday moment | 5–15s | 5–15s |
| 2. Subversion | "It feels simple. But under the hood…" | 10–25s | 10–25s |
| 3. Stakes amplification | Name what's at risk or what scale this operates at | 10–30s | 10–30s |
| 4. Thesis | "Today we are going to look at why/what/how…" | 5–15s | 5–15s |
| 5. Foundation | "Let's start with…" — establish baseline so the rabbit hole has a floor | 30–60s | 30–60s |
| 6. Escalation cycle | Solution → flaw → better solution → worse flaw, ×3 (5min) or ×5–6 (10min) | 60–70% of runtime | 60–70% of runtime |
| 7. Synthesis | Pull threads together, often with a personified summary | 15–30s | 15–30s |
| 8. Reframe / payoff | Change the viewer's mental model of the opening action | 10–20s | 10–20s |
| 9. Closer | Prescription, philosophical line, or "next time you do X…" | 5–15s | 5–15s |

Total target word count: runtime in minutes × 170. So 5 min ≈ 850–900 words, 7 min ≈ 1190 words, 10 min ≈ 1700 words.

## Beat-by-beat

### Beat 1 — Familiar-action open

**Function:** drop the viewer inside a concrete everyday moment they've experienced. No metaphor, no setup. Present tense, second person (or first-person plural).

**Constraints:**
- 8–14 words in the opening sentence.
- Concrete verb. "You open a text editor, press the letter E, and it appears instantly."
- Often starts with "Every" or "You". Three of the studied videos literally start with "Every".

**Opener phrases that work:**
- "Every time you <do mundane thing>..."
- "You open <thing>, press <key>, and..."
- "In software engineering, we spend our entire careers..."

### Beat 2 — Subversion

**Function:** name the gap between apparent simplicity and actual complexity.

**Constraints:**
- Often opens with "But" as the first word of a sentence. This is the single most repeated structural move in the house style.
- Short, declarative.
- End with a one-sentence summary that names the gap in vivid language ("a mathematical nightmare", "a catastrophic security failure").

**Phrases that work:**
- "But under the hood, ..."
- "But <the thing actually being done>, when you look at it carefully, is <vivid framing>."
- "But there is exactly one place in your stack where <opposite of common sense>."

### Beat 3 — Stakes amplification

**Function:** name the broader system, scale, or property that depends on this thing working.

**Constraints:**
- Use a concrete number or a named incident if the notes have one. "The entire security of the internet rests on..." beats "this matters a lot".
- One sentence is usually enough. Two if the stakes need a number to land.

### Beat 4 — Thesis

**Function:** the verbal handshake that promises the structure of the video.

**Constraints:**
- Use the literal phrase "Today we are going to look at..." or a near-variant. It appears in 4 of 5 studied videos.
- Make the thesis a three-part list: "why X, how Y, and what Z". This pre-promises the body's structure.

**Examples (real, from the corpus):**
- "Today we're going to look at why making text readable is a fight against math, physics, and human biology."
- "Today we are going to look at what actually happens under the hood when you choose one over the other and why the UUID versus integer debate is missing a crucial third option."

### Beat 5 — Foundation

**Function:** establish the baseline concept that the video will deliberately break.

**Constraints:**
- Open with "Let's start with..." or a similarly low-stakes definitional sentence.
- Define precisely. Use an analogy if useful. Name the concept.
- Establish the naive / default approach to the problem.
- Don't assume prior knowledge. Even if the audience would mostly know — define hashing-vs-encryption, B-trees, PRNGs, columnar storage every time. The reason: this gives a clean platform from which to deliberately break the viewer's mental model in beat 6.

### Beat 6 — Escalation cycle

**Function:** the engine of the whole video. Each cycle is a four-move loop that the viewer rides through. See `escalation-cycle-template.md` for the full template and worked examples.

**Constraints:**
- 60–70% of total runtime.
- 3 cycles for 5min, 4 cycles for 7min, 5–6 cycles for 10min.
- Each cycle = naive → flaw → smarter solution by name → new flaw.
- Each cycle should: name a real-world incident if you can, use one concrete number, end with a one-sentence personified summary.
- Signature transition phrases between cycles: *"But here is where the nightmare begins"*, *"But this hack introduces a new hell"*, *"And that is where the problem begins"*. Give yourself permission to escalate by literally announcing it.

### Beat 7 — Synthesis

**Function:** pull the cycles together, often with personification or anaphora. This is where the writing voice becomes visibly literary.

**Constraints:**
- One long sentence, or two short ones.
- Either anaphora ("every... every... every...") or personified description of the system "trying to" do its job.
- Read it aloud — it should have rhythm, not just information.

**Real example (mouse-keys video):**
> "Every SSH key you've ever generated, every HTTPS session your browser has negotiated, every encrypted message you've sent, somewhere in the lineage of the random numbers behind it, there is a bit that came from a tremor in somebody's hand, the jitter of a hard drive head, or the thermal noise of a few transistors."

### Beat 8 — Reframe

**Function:** send the viewer back to the opening action with new eyes.

**Constraints:**
- Use the structure "The next time you <opening action>, remember: <new mental model>."
- The reframe should make the viewer feel they understand something they didn't before — this is the "aha" moment the audience explicitly responds to in comments.

**Real example (text-rendering):**
> "The next time you read a simple article online, remember what is happening. Your computer is interpreting raw math, dynamically compiling bytecode to distort perfect curves, and exploiting the physical properties of microscopic colored lights to trick your optical system."

### Beat 9 — Closer

**Function:** land the video. Three observed archetypes, used roughly evenly:

- **Prescription**: "If you are X, do Y. If you are A, do B." — used for actionable topics (UUID, three databases).
- **Philosophical line**: an aphoristic statement about the nature of the field. ("Cryptography doesn't work without that link to the physical world.")
- **All-happening-invisibly / vivid scale**: a sensory close that names the scale of what was just explained. ("All happening thousands of times a second, completely invisibly.")

**Constraints:**
- 20–35 words.
- No CTA. No "smash subscribe". No "let me know in the comments". The audience explicitly fears the channel "going Fireship" — keep it pure.
- Default to prescription unless the topic genuinely doesn't have an actionable recommendation, in which case use vivid scale.

## What to imitate vs. what to leave alone

**Imitate:**
- The 9-beat arc (it works at 3 minutes and at 10).
- "Today we are going to look at..." thesis.
- "Let's start with..." foundation opener.
- Three-part lists at every scale.
- Real dated incidents as evidence.
- Personification of inanimate systems.
- The 1-in-5 short-declarative rhythm.
- 170 wpm pace.

**Leave alone:**
- Pawel's title formula. "Why X is Y" / "X explained in N minutes" is now him; copying invites direct comparison and his SEO will eat ours.
- His exact subject matter (text rendering, hashing, randomness — he's been there). Pick adjacent rabbit holes.
- His bare-minimum visual style. With HyperFrames the visual ceiling is ours to set; under-using it would forfeit the project's edge.
