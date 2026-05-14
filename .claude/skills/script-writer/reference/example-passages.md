# Example passages — annotated excerpts by move

Real passages from the studied corpus, organized by what each move *does*. Use these as cadence references when drafting. Do not copy the topic-specific words — copy the structural moves.

These passages came from earlier videos that did fit an iceberg-shaped arc. They are organized here by move type, not by beat slot, because **the move is portable; the slot isn't**. A "subversion" sentence works wherever the prose naturally arrives at a subversion, not because beat 2 demands one.

All quotes are verbatim from the clean transcripts in `research/pawel-code-stuff/transcripts/clean/`.

---

## Opening moves — placing the viewer inside a concrete moment

**Text rendering:**
> "You open a text editor, press the letter E, and it appears instantly. It feels like the simplest, most fundamental thing a computer can do."

*Notes:* 14 words, present tense, second person, three concrete verbs. Followed immediately by a one-sentence emotional reading ("It feels like...") that sets up whatever surprise the rest of the prose delivers.

**UUID:**
> "Every time you create a database table, you have to answer one fundamental question. How do you identify a record?"

*Notes:* opens with "Every time you", which is a project signature. Ends on a question that the rest of the prose will answer.

**Mouse keys:**
> "Every time you generate an SSH key, create a TLS certificate, or encrypt a file, something strange has to happen."

*Notes:* three-part list inside the opening sentence. "Something strange has to happen" is the subversion teased into the open.

**Password hashing:**
> "In software engineering, we spend our entire careers trying to make code run faster. We obsess over milliseconds."

*Notes:* first-person plural collegial. Sets up a universal expectation that the prose will then break.

---

## Subversion moves — naming the gap

**Text rendering:**
> "But under the hood, translating that keystroke into the shape you see on your monitor is a mathematical nightmare. Drawing a rectangle is easy. You tell the GPU to fill a block of pixels with a color. But drawing text is arguably one of the most complex, computationally expensive tasks your operating system handles."

*Notes:* sentence-initial "But". Followed by a 4-word declarative ("Drawing a rectangle is easy.") which is the 1-in-5 cadence in action. Then the comparison sets up the depth.

**UUID:**
> "But swapping a sequential integer for a UUID isn't just a simple format change in your application code. It completely alters how your database stores, indexes, and retrieves data at the disk level."

*Notes:* "But" opener. Three-part list ("stores, indexes, and retrieves") at sentence level.

**Password hashing:**
> "But there is exactly one place in your stack where optimizing for speed is a catastrophic security failure."

*Notes:* one sentence is enough when the subversion is sharp. The phrase "catastrophic security failure" does the emotional work.

---

## Stakes-naming moves — telling the viewer what depends on this

**Mouse keys:**
> "The entire security of the internet rests on a problem that shouldn't even be solvable on a deterministic machine."

**Text rendering:**
> "But text is arguably one of the most complex, computationally expensive tasks your operating system handles."

*Notes:* often this move is one big claim. It earns its space because the prose is about to back it up.

---

## Promise moves — signaling what the rest of the prose will do

These moves work when the prose naturally arrives at a moment where the viewer needs to know the shape of what's coming. They do **not** work as required openings.

**Text rendering:**
> "Today we're going to look at why making text readable is a fight against math, physics, and human biology."

*Notes:* three-part list ("math, physics, and human biology") that pre-promises the body's structure.

**UUID:**
> "Today we are going to look at what actually happens under the hood when you choose one over the other and why the UUID versus integer debate is missing a crucial third option."

*Notes:* longer promise because the topic has a genuine third option to reveal. Note the tease ("a crucial third option") that creates a curiosity gap held until late.

**Password hashing:**
> "Today we are going to look at what actually happens when you hash a password, why algorithms designed for speed are a liability, and how modern systems defend against hardware designed to crack them."

*Notes:* three-part list with escalating stakes ("what happens" → "why X" → "how to defend").

---

## Definitional moves — establishing a baseline before breaking it

**UUID:**
> "Let's start with auto incrementing integers. To understand their performance, we need to look at how relational databases manage indexes. Under the hood, your primary key is stored in a B-tree data structure. B-trees store data in sorted order across memory pages on your disk."

*Notes:* "Let's start with..." opener. Defines B-tree by structure and behavior. Names the concept.

**Mouse keys:**
> "Let's start with what computers can do on their own. Every modern operating system ships with a pseudo-random number generator, a PRNG."

*Notes:* defines the PRNG by introducing both the spelled-out name and the abbreviation in one sentence.

---

## Escalation moves — solution-then-broken-then-better

A 4-move chain (naive → flaw → smarter solution by name → new flaw) works *when the topic has that chain in its substrate*. If the substrate doesn't have it, do not force-fit it.

**Text rendering, anti-aliasing → hinting:**
> "If you're rendering a massive 3D model in a video game, anti-aliasing works brilliantly, but text is tiny. A lowercase E in a standard 12-point font might only be 8 pixels tall. If you blindly apply mathematical anti-aliasing to something that small, it doesn't look smooth. It turns into a smudgy, blurry mess. The critical stems of the letters fall right between the pixels, washing out the contrast and making it illegible.
>
> To solve this, typographers and software engineers created hinting. Hinting is quite literally a programming language embedded inside the font file itself. For every single character at various specific sizes, there are manually written or algorithmically generated instructions. These instructions tell the rendering engine, if this letter is being drawn at exactly 12 pixels tall, deliberately distort the mathematical curve so that the left vertical stem aligns perfectly with the physical pixel grid.
>
> Let's repeat that one more time. Fonts contain executable bytecode that distorts their own shapes just to survive the transition to a low-resolution screen."

*Notes:* "But text is tiny" is the 1-in-5 short declarative. Concrete numbers ("12-point font", "8 pixels tall") anchor the abstract claim. Closing sentence is personification ("fonts that survive the transition") — the mic-drop summary that lifts the technical move into a story.

Signature transition phrases between escalations, when the prose naturally arrives at one:
- "But here is where the nightmare begins."
- "But this hack introduces a new hell."
- "And that is where the problem begins."
- "But here is the catch — and it's a significant one."

These work as hinges only when the prose around them earns the escalation. Forcing them between paragraphs that don't actually escalate exposes the recipe.

---

## Synthesis-style sentences — the literary moment

**Mouse keys (long anaphoric sentence):**
> "Every SSH key you've ever generated, every HTTPS session your browser has negotiated, every encrypted message you've sent, somewhere in the lineage of the random numbers behind it, there is a bit that came from a tremor in somebody's hand, the jitter of a hard drive head, or the thermal noise of a few transistors."

*Notes:* anaphora ("every... every... every...") followed by a descending three-part list of physical sources ("a tremor... the jitter... the thermal noise..."). One long sentence; the rest of the prose earned this exception to the 22-word rule.

**Password hashing (personification stack):**
> "The password hash is the one piece of code standing at the gate, intentionally dragging its feet, burning cycles, and hoarding memory, ensuring that no one gets through quickly."

*Notes:* personification stack — five verbs of intent. Converts the technical idea into a character.

**Text rendering (one-sentence synthesis):**
> "Fonts contain executable bytecode that distorts their own shapes just to survive the transition to a low-resolution screen."

*Notes:* one-sentence synthesis can work when every word is loaded.

---

## Reframing moves — sending the viewer back to the opening with new eyes

**Text rendering:**
> "The next time you read a simple article online, remember what is happening. Your computer is interpreting raw math, dynamically compiling bytecode to distort perfect curves, and exploiting the physical properties of microscopic colored lights to trick your optical system."

*Notes:* "The next time you..." opener. Three-part list at the end recapping the body's three main moves. This move works when the prose's opening was a concrete action — there's something to send the viewer back to. If your prose didn't open on a concrete action, this move doesn't land.

---

## Landing moves — three archetypes

**Prescription (UUID):**
> "To summarize, if you are building a simple single-node application where IDs are strictly internal and never exposed to the client, auto incrementing integers are still the most efficient choice. But if you are building a distributed system or if your identifiers will ever be exposed in URLs or APIs, do not default to random UUIDv4. Adopt a time-ordered identifier like UUIDv7. You will save your database from a massive amount of unnecessary work."

*Notes:* if/else prescription is the actionable closer. "Do not default to X. Adopt Y." is direct.

**Vivid scale (text rendering):**
> "All happening thousands of times a second, completely invisibly."

*Notes:* 8 words. The rest of the prose earned this brevity.

**Philosophical (mouse keys, paraphrasing):**
> "Cryptography doesn't work without that link to the physical world."

*Notes:* one aphoristic line that summarizes the deep claim of the prose.
