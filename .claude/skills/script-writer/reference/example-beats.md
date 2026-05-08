# Example beats — annotated excerpts

Real passages from the studied corpus, organized by beat. Use these as cadence references when drafting. Do not copy the topic-specific words — copy the structural moves.

All quotes are verbatim from the clean transcripts in `research/pawel-code-stuff/transcripts/clean/`.

---

## Beat 1 — Familiar-action open

**Text rendering (5:19, 125K views):**
> "You open a text editor, press the letter E, and it appears instantly. It feels like the simplest, most fundamental thing a computer can do."

*Notes:* 14 words, present tense, second person, three concrete verbs. Followed immediately by a one-sentence emotional reading ("It feels like...") that sets up the subversion.

**UUID (5:18):**
> "Every time you create a database table, you have to answer one fundamental question. How do you identify a record?"

*Notes:* opens with "Every time you", which is a project signature. Ends on a question that the rest of the video will answer.

**Mouse keys (9:41):**
> "Every time you generate an SSH key, create a TLS certificate, or encrypt a file, something strange has to happen."

*Notes:* three-part list inside the opening sentence. "Something strange has to happen" is the subversion teased into the open.

**Password hashing (5:55):**
> "In software engineering, we spend our entire careers trying to make code run faster. We obsess over milliseconds."

*Notes:* first-person plural collegial. Sets up a universal expectation that the video will then break.

---

## Beat 2 — Subversion

**Text rendering:**
> "But under the hood, translating that keystroke into the shape you see on your monitor is a mathematical nightmare. Drawing a rectangle is easy. You tell the GPU to fill a block of pixels with a color. But drawing text is arguably one of the most complex, computationally expensive tasks your operating system handles."

*Notes:* sentence-initial "But". Followed by a 4-word declarative ("Drawing a rectangle is easy.") which is rule-1 cadence in action. Then the comparison sets up the depth.

**UUID:**
> "But swapping a sequential integer for a UUID isn't just a simple format change in your application code. It completely alters how your database stores, indexes, and retrieves data at the disk level."

*Notes:* "But" opener. Three-part list ("stores, indexes, and retrieves") at sentence level.

**Password hashing:**
> "But there is exactly one place in your stack where optimizing for speed is a catastrophic security failure."

*Notes:* one sentence is enough when the subversion is sharp. The phrase "catastrophic security failure" does the emotional work.

---

## Beat 3 — Stakes amplification

**Mouse keys:**
> "The entire security of the internet rests on a problem that shouldn't even be solvable on a deterministic machine."

**Text rendering:**
> "But text is arguably one of the most complex, computationally expensive tasks your operating system handles."

*Notes:* often the stakes beat is one big claim. It earns its space because the rest of the video is about to back it up.

---

## Beat 4 — Thesis

**Text rendering:**
> "Today we're going to look at why making text readable is a fight against math, physics, and human biology."

*Notes:* literal "Today we're going to look at...". Three-part list ("math, physics, and human biology") that pre-promises the body's structure.

**UUID:**
> "Today we are going to look at what actually happens under the hood when you choose one over the other and why the UUID versus integer debate is missing a crucial third option."

*Notes:* longer thesis because the topic has a genuine third option to reveal. Note the tease ("a crucial third option") that creates a curiosity gap held until late in the video.

**Password hashing:**
> "Today we are going to look at what actually happens when you hash a password, why algorithms designed for speed are a liability, and how modern systems defend against hardware designed to crack them."

*Notes:* three-part list with escalating stakes ("what happens" → "why X" → "how to defend").

---

## Beat 5 — Foundation

**UUID:**
> "Let's start with auto incrementing integers. To understand their performance, we need to look at how relational databases manage indexes. Under the hood, your primary key is stored in a B-tree data structure. B-trees store data in sorted order across memory pages on your disk."

*Notes:* "Let's start with..." opener. Defines B-tree by structure and behavior. Names the concept. Sets up the platform that beat 6 will break.

**Mouse keys:**
> "Let's start with what computers can do on their own. Every modern operating system ships with a pseudo-random number generator, a PRNG."

*Notes:* defines the PRNG by introducing both the spelled-out name and the abbreviation in one sentence.

---

## Beat 6 — Escalation cycle

See `escalation-cycle-template.md` for the full template. One real cycle here for cadence reference:

**Text rendering, cycle 2 (anti-aliasing → hinting):**
> "If you're rendering a massive 3D model in a video game, anti-aliasing works brilliantly, but text is tiny. A lowercase E in a standard 12-point font might only be 8 pixels tall. If you blindly apply mathematical anti-aliasing to something that small, it doesn't look smooth. It turns into a smudgy, blurry mess. The critical stems of the letters fall right between the pixels, washing out the contrast and making it illegible.
>
> To solve this, typographers and software engineers created hinting. Hinting is quite literally a programming language embedded inside the font file itself. For every single character at various specific sizes, there are manually written or algorithmically generated instructions. These instructions tell the rendering engine, if this letter is being drawn at exactly 12 pixels tall, deliberately distort the mathematical curve so that the left vertical stem aligns perfectly with the physical pixel grid.
>
> Let's repeat that one more time. Fonts contain executable bytecode that distorts their own shapes just to survive the transition to a low-resolution screen."

*Notes:* full four-move cycle in ~140 words. "But text is tiny" is the rule-1 short declarative. Concrete numbers ("12-point font", "8 pixels tall") anchor the abstract claim. Closing sentence is personification ("fonts that survive the transition") — that's the cycle's mic-drop summary.

---

## Beat 7 — Synthesis

**Mouse keys:**
> "Every SSH key you've ever generated, every HTTPS session your browser has negotiated, every encrypted message you've sent, somewhere in the lineage of the random numbers behind it, there is a bit that came from a tremor in somebody's hand, the jitter of a hard drive head, or the thermal noise of a few transistors."

*Notes:* anaphora ("every... every... every...") followed by a descending three-part list of physical sources ("a tremor... the jitter... the thermal noise..."). This is the literary moment of the video. One long sentence; the rest of the video earned this exception to rule 4.

**Password hashing:**
> "The password hash is the one piece of code standing at the gate, intentionally dragging its feet, burning cycles, and hoarding memory, ensuring that no one gets through quickly."

*Notes:* personification stack ("standing at the gate", "dragging its feet", "burning cycles", "hoarding memory") — five verbs, all of intent. Converts the technical idea into a character.

**Text rendering:**
> "Fonts contain executable bytecode that distorts their own shapes just to survive the transition to a low-resolution screen."

*Notes:* one-sentence synthesis can also work. The sentence is doing the heavy lifting because every word is loaded.

---

## Beat 8 — Reframe

**Text rendering:**
> "The next time you read a simple article online, remember what is happening. Your computer is interpreting raw math, dynamically compiling bytecode to distort perfect curves, and exploiting the physical properties of microscopic colored lights to trick your optical system."

*Notes:* literal "The next time you..." opener. Three-part list at the end recapping the body's three main moves. Sends the viewer back to beat 1 with new eyes.

---

## Beat 9 — Closer

**Prescription (UUID):**
> "To summarize, if you are building a simple single-node application where IDs are strictly internal and never exposed to the client, auto incrementing integers are still the most efficient choice. But if you are building a distributed system or if your identifiers will ever be exposed in URLs or APIs, do not default to random UUIDv4. Adopt a time-ordered identifier like UUIDv7. You will save your database from a massive amount of unnecessary work."

*Notes:* if/else prescription is the actionable closer. "Do not default to X. Adopt Y." is direct.

**Vivid scale (text rendering):**
> "All happening thousands of times a second, completely invisibly."

*Notes:* 8 words. The rest of the video earned this brevity.

**Philosophical (mouse keys, paraphrasing):**
> "Cryptography doesn't work without that link to the physical world."

*Notes:* one aphoristic line that summarizes the deep claim of the video.
