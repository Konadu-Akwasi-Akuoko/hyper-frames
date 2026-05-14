# Sentence-rhythm moves

These are the voice moves that separate "an engineer narrating slides" from "writing that has rhythm". Apply them while drafting, not as a post-pass — fixing rhythm after the fact tends to flatten the prose.

These are *moves*, not rules. A move lands when the prose naturally arrives at the moment for it. None of them is required on cue. Treat them as the palette this voice keeps reaching for.

## Why rhythm matters here

The script will be read by TTS at ~170 wpm and synced to visual beats via word-level transcript anchors. The rhythm of the prose is the rhythm of the video. Get it wrong and the whole video drifts.

Rhythm is also how a long monologue stays watchable. The viewer doesn't decide to keep watching at minute 3 because the topic got more interesting; they keep watching because the writing keeps surprising them at the sentence level.

## Move 1 — The 1-in-5 short-declarative cadence

Roughly **1 in 5 sentences is six words or fewer.** These short sentences do rhythmic work: they sit between longer explanatory sentences and reset attention.

After a long explanatory sentence (12+ words), follow with a 4–6 word declarative that names or recaps what was just explained.

**Real examples (from the corpus):**
- "Drawing a rectangle is easy."
- "Fonts are not pictures."
- "Hashing is a one-way street."
- "When your randomness fails, everything fails."
- "Sub-pixel rendering."
- "Look extremely closely at a white pixel on an LCD monitor."
- "It is not one white square."

Distribution from the studied videos: ~20% of sentences are ≤6 words, ~50% are 7–18 words (workhorses), ~30% are >18 words (full explanations). If your draft is all long sentences, you're missing the short ones.

**Test:** read each paragraph aloud in your head. If you don't naturally pause between sentences, you don't have enough short ones.

**When this move doesn't land:** padding the prose with short sentences that don't actually name anything makes the rhythm feel performative. The short sentences need to *do something* — recap, name, hinge — not just appear.

## Move 2 — "But" pivots, never "however"

The hard single-syllable "but" is doing rhythmic and tonal work — it's a physical hinge in the prose. "However" is too soft and adds a syllable.

Replace every "however" with "but". Replace every "although" with two sentences joined by "but".

**Examples:**
- "But here is where the nightmare begins."
- "But this hack introduces a new hell."
- "But sequential integers have two major systemic flaws."
- "But text is tiny."

**When this move doesn't land:** if every other sentence opens with "But", the hinge feel disappears. Earlier scripts used the move 4–8 times across the whole video, not 4–8 times per paragraph.

## Move 3 — Three-part lists at every scale

Three-part lists are pervasive in the house style — used in thesis sentences, in synthesis sentences, and at adjective-level. Usually escalating in size, severity, or abstraction.

When you can't think of what to write next, a three-part list of concrete examples is almost always a good answer.

**Examples:**
- "math, physics, and human biology"
- "an SSH key, a TLS certificate, or encrypt a file"
- "stores, indexes, and retrieves data at the disk level"
- "We obsess over milliseconds. We optimize database queries. We cache responses and we minimize CPU cycles."

**When this move doesn't land:** if the topic genuinely has two cases or four, forcing a third (or dropping a fourth) is invention dressed as rhythm. Use the count the substrate supports.

## Move 4 — Max 22 words per sentence (with one exception)

After the first draft, mark every sentence over 22 words and break it. Two short sentences almost always read better than one long one, and TTS handles them with fewer prosody errors.

**The exception:** one long sentence per script, at the moment where the prose pulls its threads together — anaphora ("every... every... every...") or a descending three-part list. That's the literary moment of the video. Keep it to one — don't stack two.

## Move 5 — Personify systems

Treat inanimate systems as if they have intent. This is the strongest stylistic signature in the house style and converts a static system diagram into a story.

**Patterns:**
- Fonts that *survive* transitions, *distort their own shapes*, *defend* themselves
- A password hash that *stands at the gate*, *drags its feet*, *hoards memory*
- A B-tree that *neatly allocates* a new page
- The kernel that *farms* entropy from physical events
- Attackers who *use*, *guess*, *brute-force*

The verbs do the work. Pick verbs of intent ("survive", "defend", "hoard", "trick", "farm") over verbs of state ("contain", "have", "include").

**When this move doesn't land:** on systems where personification would feel cute rather than load-bearing. A network packet doesn't need a character arc; a DNS lookup doesn't have an interior life. Use the move where the system's behavior actually feels like agency — caches that "lie", schedulers that "starve" processes, garbage collectors that "stop the world".

## Move 6 — Name everything; introduce on first use

Technical terms are always named on first use, often with an italicized framing.

**Pattern:** introduce concept → name concept → use the name from then on.

**Examples:**
- "this translation process is called rasterization"
- "this is a classic security vulnerability known as an insecure direct object reference"
- "the recently standardized UUID version 7 gives you the best of both worlds"

The first time a noun appears, it should feel like a label being applied. Subsequent uses are the label being deployed.

**When this move doesn't land:** inventing names that aren't in the substrate. If the substrate calls something "the staircase effect", use that — don't coin "the jaggies problem" because it sounds better.

## Move 7 — Concrete numbers and dated incidents

Whenever a claim could feel hand-wavy, anchor it to a specific number or a real event.

**Numbers from the corpus:** "8 pixels tall", "12-point font", "1/3 of a pixel", "32-bit seed", "4 billion possible values", "128-bit value", "millions of SHA hashes per second", "45 seconds", "2 billion rows".

**Incidents from the corpus:** "In 2008, a maintainer patching Debian's OpenSSL package..." / "In 2010, a group called Fail Overflow broke the security of the PlayStation 3..."

Dated incidents are the highest-leverage move because they convert "this could be a problem" into "this destroyed something real".

**When this move doesn't land:** if the substrate didn't surface a number or an incident for the claim, do not invent one. Soften the claim, or cut it. Inventing concrete-sounding evidence is exactly the failure mode the fact-verifier sub-agent exists to catch.

## Move 8 — Vocabulary register

- **Hedges:** ~2–3 instances of "actually" used emphatically (not as a hedge), ~1 "essentially", zero "however". No "kind of", "sort of", "I think".
- **Voice:** first-person plural collegial. "We obsess over milliseconds. We optimize database queries." Never "I think" or "in my opinion". The voice is "we, the engineers" — inviting the viewer into the in-group.
- **No persona overlay.** Don't introduce yourself. Don't reference the channel. Don't break the fourth wall.

## Move 9 — Add qualifiers to strong claims

The audience pushes back on un-qualified claims. "X is a vulnerability" gets corrected; "X is a vulnerability *when paired with Y*" doesn't.

When you write a strong general claim, immediately add the qualifier. The qualifier costs 6 words and disarms the corrector.

**Bad:** "Guessable IDs are a security vulnerability."
**Good:** "Guessable IDs are a vulnerability *when paired with weak authorization* — which is more common than you'd think."

## Move 10 — Personal context bridge (at least once per video)

Connect to something the viewer has done themselves. The audience explicitly responds to these moments — one comment about VeraCrypt's mouse-movement key generation got 155 likes.

Place the bridge in the hook (the opening action itself can be the bridge) or in the landing (the reframe). One bridge per video is usually enough.

## The iteration recipe

If a draft reads stiffly, do these in order:

1. Mark every sentence over 22 words. Break them.
2. After every long explanatory sentence, insert a 4–6 word declarative that names what was just explained.
3. Replace any "however" with "but".
4. Replace any "sort of" / "kind of" / "I think" with nothing.
5. Replace any abstract noun with a concrete one if possible (not "improvements" but "1/3 of a pixel"; not "issues" but "color fringing").
6. Read the result aloud. If you don't naturally pause between sentences, add more short ones — but only where they name something.
