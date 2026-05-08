# Sentence rhythm rules

These rules are what separates "an engineer narrating slides" from "writing that has rhythm". Apply them while drafting, not as a post-pass — fixing rhythm after the fact tends to flatten the prose.

## Why rhythm matters here

The script will be read by TTS at ~170 wpm and synced to visual beats via word-level transcript anchors. The rhythm of the prose is the rhythm of the video. Get it wrong and the whole video drifts.

Rhythm is also how you keep a 5-minute monologue from feeling like a lecture. The viewer doesn't decide to keep watching at minute 3 because the topic got more interesting; they keep watching because the writing keeps surprising them at the sentence level.

## Rule 1 — The 1-in-5 short-declarative cadence

Roughly **1 in 5 sentences should be six words or fewer.** These short sentences are doing rhythmic work: they sit between longer explanatory sentences and reset attention.

After every long explanatory sentence (12+ words), follow with a 4–6 word declarative that names or recaps what was just explained.

**Real examples (from the corpus):**
- "Drawing a rectangle is easy."
- "Fonts are not pictures."
- "Hashing is a one-way street."
- "When your randomness fails, everything fails."
- "Sub-pixel rendering."
- "Look extremely closely at a white pixel on an LCD monitor."
- "It is not one white square."

Distribution from the studied videos: ~20% of sentences are ≤6 words, ~50% are 7–18 words (workhorses), ~30% are >18 words (full explanations). If your draft is all long sentences, you're missing the short ones.

**Test:** read each beat aloud in your head. If you don't naturally pause between sentences, you don't have enough short ones.

## Rule 2 — "But" pivots, never "however"

Every script uses **"But"** or **"But here is where..."** as a sentence opener 4–8 times. The hard single-syllable "but" is doing rhythmic and tonal work — it's a physical hinge in the prose. "However" is too soft and adds a syllable.

Replace every "however" with "but". Replace every "although" with two sentences joined by "but".

**Examples:**
- "But here is where the nightmare begins."
- "But this hack introduces a new hell."
- "But sequential integers have two major systemic flaws."
- "But text is tiny."

## Rule 3 — Three-part lists at every scale

Three-part lists are pervasive in the house style — used in the thesis, in the synthesis, and at sentence level. Usually escalating in size, severity, or abstraction.

When you can't think of what to write next, a three-part list of concrete examples is almost always the answer.

**Examples:**
- "math, physics, and human biology"
- "an SSH key, a TLS certificate, or encrypt a file"
- "stores, indexes, and retrieves data at the disk level"
- "We obsess over milliseconds. We optimize database queries. We cache responses and we minimize CPU cycles."

## Rule 4 — Max 22 words per sentence (with one exception)

After the first draft, mark every sentence over 22 words and break it. Two short sentences almost always read better than one long one, and TTS handles them with fewer prosody errors.

**The exception:** the synthesis beat (#7) earns a single long sentence with anaphora or a descending list. That's the literary moment of the video. Even there, keep the long sentence to one — don't stack two.

## Rule 5 — Personify systems

Treat inanimate systems as if they have intent. This is the strongest stylistic signature in the house style and converts a static system diagram into a story.

**Patterns:**
- Fonts that *survive* transitions, *distort their own shapes*, *defend* themselves
- A password hash that *stands at the gate*, *drags its feet*, *hoards memory*
- A B-tree that *neatly allocates* a new page
- The kernel that *farms* entropy from physical events
- Attackers who *use*, *guess*, *brute-force*

The verbs do the work. Pick verbs of intent ("survive", "defend", "hoard", "trick", "farm") over verbs of state ("contain", "have", "include").

## Rule 6 — Name everything; introduce on first use

Technical terms are always named on first use, often with an italicized framing.

**Pattern:** introduce concept → name concept → use the name from then on.

**Examples:**
- "this translation process is called rasterization"
- "this is a classic security vulnerability known as an insecure direct object reference"
- "the recently standardized UUID version 7 gives you the best of both worlds"

The first time a noun appears, it should feel like a label being applied. Subsequent uses are the label being deployed.

## Rule 7 — Concrete numbers and dated incidents

Whenever a claim could feel hand-wavy, anchor it to a specific number or a real event.

**Numbers from the corpus:** "8 pixels tall", "12-point font", "1/3 of a pixel", "32-bit seed", "4 billion possible values", "128-bit value", "millions of SHA hashes per second", "45 seconds", "2 billion rows".

**Incidents from the corpus:** "In 2008, a maintainer patching Debian's OpenSSL package..." / "In 2010, a group called Fail Overflow broke the security of the PlayStation 3..."

The dated incidents are the highest-leverage move because they convert "this could be a problem" into "this destroyed something real". If your notes have one, use it.

## Rule 8 — Vocabulary register

- **Hedges per video:** ~2–3 instances of "actually" used emphatically (not as a hedge), ~1 "essentially", zero "however". No "kind of", "sort of", "I think".
- **Voice:** first-person plural collegial. "We obsess over milliseconds. We optimize database queries." Never "I think" or "in my opinion". The voice is "we, the engineers" — inviting the viewer into the in-group.
- **No persona overlay.** Don't introduce yourself. Don't reference the channel. Don't break the fourth wall. The script is essentially anonymous craftsmanship.

## Rule 9 — Add qualifiers to strong claims

The audience pushes back on un-qualified claims. "X is a vulnerability" gets corrected; "X is a vulnerability *when paired with Y*" doesn't.

When you write a strong general claim, immediately add the qualifier. The qualifier costs 6 words and disarms the corrector.

**Bad:** "Guessable IDs are a security vulnerability."
**Good:** "Guessable IDs are a vulnerability *when paired with weak authorization* — which is more common than you'd think."

## Rule 10 — Personal context bridge (at least once per video)

Connect to something the viewer has done themselves. The audience explicitly responds to these moments — "wait so that's why I remember VeraCrypt needing me to move my mouse" got 155 likes on a single comment.

Place the bridge in beat 1 (the opening action itself can be the bridge) or beat 8 (the reframe).

## The iteration recipe

If a draft beat reads stiffly, do these in order:

1. Mark every sentence over 22 words. Break them.
2. After every long explanatory sentence, insert a 4–6 word declarative that names what was just explained.
3. Replace any "however" with "but".
4. Replace any "sort of" / "kind of" / "I think" with nothing.
5. Replace any abstract noun with a concrete one if possible (not "improvements" but "1/3 of a pixel"; not "issues" but "color fringing").
6. Read the result aloud. If you don't naturally pause between sentences, add more short ones.
