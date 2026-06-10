# creator-patterns.md

Cross-channel script-craft reference, synthesized from 237 transcripts across 12 tech YouTube creators plus their title corpus. The consumer is the HyperFrames authoring pipeline for a small dev channel. The flagship video "Why you can't escape JavaScript anymore" lost 50% of viewers by 0:42 and had a retention cliff at ~4:49 (a subtopic ran ~2.5 min and dragged). Every section below is written to attack those two specific failures: the **early bleed** (weak first 10s) and the **mid-video drag** (a single idea held too long).

This is a wiring document, not an essay. Sections 1-5 are the evidence; section 6 is the per-workstream rule set to install.

---

## 1. Hook taxonomy

Cross-channel archetypes, ranked by transferability to a history/explainer dev channel (most transferable first). Every one of these is delivered in **sentence one, with zero preamble** — see Section 2.

### 1.1 The Hidden-Dependency / Quiet-Dominance reveal — TOP PICK for history explainers
**Mechanism.** Name something globally famous or assumed-trivial, then reveal it secretly depends on (or secretly is) an obscure, unglamorous thing. Exploits the curiosity gap between visible importance and invisible cause, and pays the viewer a status reward ("you're about to learn the secret layer"). This is the single most reusable frame for "the invisible thing you depend on until it breaks."
**Verbatim.**
- "In 2020, the most important chart in the world was made by a data journalist at the Financial Times. You've seen it... That chart was built in a programming language most people have never heard of, a language created as a joke between two guys in a corridor in New Zealand. The language is called R, just the letter." (@CodeSource)
- "As developers, we chase the new new frameworks, new runtimes, new modern stacks. But there's a quieter layer of computing that never got replaced. It didn't go viral. It didn't get rewritten in Rust... And yet, when the world panics, this is the language governments and banks still go looking for." (@CodeSource)
**Channels.** @CodeSource (signature), @thecodingkoalaa, @Fireship (deep-dive mode), @awesome-coding.
**Why #1 for us.** Our channel IS a history/explainer. "JavaScript runs everything and you can't escape it" is literally this frame — but the flagship apparently stated the conclusion flat instead of withholding it. Withhold the name, lead with the dependency.

### 1.2 The withheld-subject cold open (in medias res / concrete anchor)
**Mechanism.** Open on a concrete situation — a timestamp, a place+date, a single object, a person alone in a room — and do NOT name the actual topic for 20-130 words. The situation hooks; the reveal is its own payoff. Precise numbers ("2:19 a.m.", "311 MB ISO") read as documentary truth.
**Verbatim.**
- "At 2:19 a.m., a CI pipeline stops at the exact same line. It has passed every night for months. Not a little slow, not tests are flaky, it simply freezes, then fails. The log prints a sentence that feels insultingly small for how expensive it's about to become. Docker pool node 14." (@CodeSource)
- "This is an email address, jvnet@zeroflux.org. It belongs to a Canadian programmer named Judvet." (@CodeSource)
**Channels.** @CodeSource (signature), @Fireship ("It's 2009. You're at a Hannah Montana movie..."), @codehead01 ("Picture this"), @devforgehq ("It's 3:00 a.m. Production is down").
**Transfer note.** Pairs with 1.1 — open on the anomaly, not the encyclopedia entry. Must be closed at the end (see 3.1).

### 1.3 The contrarian reversal — concede, then "But here's what nobody tells you"
**Mechanism.** State the loud consensus, concede it's true (this disarms the skeptic and buys trust), then pivot hard on **"but"** to a reframe that makes the bad news good or the obvious thing wrong. The concession is load-bearing; the "but" is the engine.
**Verbatim.**
- "Everyone thinks web development is oversaturated. And they're right. It is. ... But what if I told you that saturation is actually the best thing that ever happened to you?" (@devforgehq)
- "Everyone's out here saying AI is going to kill programming jobs, and honestly, they're not entirely wrong, but they're not right either." (@codehead01)
- "AI will not replace programmers. I know that's not what you've been hearing." (@Latticx)
**Channels.** Nearly universal — @devforgehq, @Latticx, @Shadeofcode, @codehead01, @awesome-coding, @technetiumm, @thecodingkoalaa.
**Transfer note.** Highest-frequency device in the entire corpus. The structure `[consensus] + BUT + [reframe]` is the channel-wide pivot grammar; it also resets every sub-claim mid-body (Section 3).

### 1.4 The counterintuitive number / superlative drop
**Mechanism.** Lead with a precise, contradictory figure, no setup. False precision (6.1%, $9.3B, 0.2%, 21 years) reads as researched and triggers loss-aversion or a curiosity vacuum before context can soften it. Pin "free" or "small" against a giant figure.
**Verbatim.**
- "the company that just hosted your website for free is currently valued at $9.3 billion, and it made $200 million last year." (@thecodingkoalaa)
- "Computer science grads now face a 6.1% unemployment rate... even philosophy majors have better job prospects at 3.2%." (@devforgehq)
- "The deepest hole anyone has ever dug is 0.2% of the way to the Earth's center. But then, how do we know that the Earth has a solid core?" (@CleoAbram)
**Channels.** @thecodingkoalaa, @devforgehq, @CleoAbram, @awesome-coding ("MySQL took 21 years to fix this bug"), @codehead01.
**Transfer note.** For history, the "number" is a date, a magnitude, or a duration. Round numbers read as guessed; specific decimals read as journalism.

### 1.5 The provocative question / curiosity-gap
**Mechanism.** Open an information gap by phrasing a question whose obvious answer is wrong. The question IS the first words — no "have you ever wondered." Often the title restated.
**Verbatim.**
- "Why are there more tornadoes in the United States than anywhere else on Earth? By a lot." (@CleoAbram)
- "Have you ever asked yourself why are there like 700 programming languages? Why can't we just pick one, agree on it, and move on with our lives?" (@codehead01)
- "Why were 90s programmers so legendary compared to today's?" (@thecodingkoalaa)
**Channels.** @CleoAbram (signature for Shorts), @codehead01, @thecodingkoalaa, @Shadeofcode.

### 1.6 The "you're doing it wrong / you can't actually do X" competence-gap callout
**Mechanism.** Second-person accusation that the viewer's self-image is fragile — they think they know something but would freeze if put on the spot. Puts identity on the line; they watch to close the gap.
**Verbatim.**
- "You've been writing front-end code for a while now... But if someone put you on the spot right now and ask you what actually happens when your framework renders a component, could you walk through it? Most developers can't." (@codehead01)
- "Most people learn JavaScript backward. They learn syntax rules, memorize methods, and then wonder why they can't build anything." (@devforgehq)
**Channels.** @codehead01, @devforgehq, @Latticx, @technetiumm ("47 tabs open... a test.js file that just says 3 months in and you're stuck").
**Transfer note.** Use sparingly — it's ego-threat-heavy. Good for "you think you understand JS, but...".

### 1.7 The cinematic origin scene / "Picture this" mini-story
**Mechanism.** Open like film: weather, lighting, a named human alone with a feeling, present tense. Narrative transportation hijacks attention before the viewer decides whether to care about the subject. Humanizes an abstract technology as one person's problem.
**Verbatim.**
- "A summer storm rolls across the outskirts of Tokyo. Inside a quiet room lit only by the glow of an aging CRT monitor, Yukihiro Matsumoto sits with a feeling he can't shake... Why can't programming be joyful?" (@CodeSource)
- "Picture this. You graduated college in the early 2000s, top of your class, got a well-paying job at... Oracle... But on March 31st, 2026, you wake up... 'IF YOU SAY YOUR MOM, YOU'RE FIRED.'" (@codehead01)
**Channels.** @CodeSource, @codehead01, @TheCodingSloth (in-fiction roleplay: "You've recently been hired by Slothcorp"), @thecodingkoalaa ("imagine there is a tiny person living inside your computer").
**Transfer note.** Excellent for an origin video. Costs more production effort; reserve for tentpoles.

### 1.8 The cynical industry-truth axiom / nostalgic lament
**Mechanism.** Open on a sweeping, world-weary declaration stated as settled fact, fusing a real trend with a fatalistic joke. Flatters the in-group of jaded working devs and signals "this channel says the quiet part out loud" — instant tribal alignment.
**Verbatim.**
- "AWS will still be running most of the internet, and it will always find new ways to charge you for it." (@awesome-coding)
- "I miss the good old days when technical debt and student debt were the only debts we had to worry about in the software world." (@awesome-coding)
**Channels.** @awesome-coding (signature), @Shadeofcode.
**Transfer note.** Voice-dependent — needs a consistent persona. Lower priority unless the channel commits to a wry narrator.

### 1.9 The anthropomorphized-subject paradox
**Mechanism.** Give the topic a personality and a self-contradiction in one breath; it's funny, memorable, and raises the exact question the video answers ("so how DID it...").
**Verbatim.**
- "JavaScript is broken and somehow it runs the entire internet... your browser just shrugs and says, 'Sure, I'll run that.' ... So, how did this glitchy little goblin of a language end up running the world?" (@devforgehq)
- "AI agents are literally Jarvis from Iron Man. Well, more like Teimu Jarvis, the Bluetooth device." (@TheCodingSloth)
**Channels.** @devforgehq, @TheCodingSloth, @SwagProfessorExplain ("REST is like the old reliable pizza delivery guy").
**Transfer note.** This is the closest archetype to our flagship's own topic. Note @devforgehq's "glitchy little goblin" is the SAME subject as our failed video, handled with a paradox + character — a direct model for a rewrite.

### 1.10 The dated news cold-open
**Mechanism.** Anchor to a precise timestamp ("Yesterday", "Earlier this week", "It's 2009"). Recency + a named concrete subject signals "breaking, you're getting it first." For history, swap "yesterday" for a hard date.
**Verbatim.**
- "Yesterday in a federal courthouse in Oakland, the trial of the century, Musk versus Altman, began its closing arguments." (@Fireship)
- "In February 2025, a guy tweeted two words, vibe coding, and accidentally broke software engineering forever." (@codehead01)
**Channels.** @Fireship (signature), @codehead01, @awesome-coding.

---

## 2. The first 10 seconds — the playbook that fixes the 0:42 drop

**The diagnosis.** Losing 50% by 0:42 is an opening-credibility failure, not a topic failure. Across all 12 channels, **not one** opens with branding, a logo sting, "hey guys welcome back," or "in this video." The cost of any pre-roll is paid in exactly the window where the flagship bled out.

### What MUST happen before ~25-30 spoken words
1. **Sentence one IS the hook.** A complete claim, question, number, or scene — never a frame ("today we're going to look at...").
2. **The title's promise is confirmed inside the first sentence.** A viewer who clicked must know within ~10s they're in the right place. Fireship restates the title nearly verbatim in line one.
3. **By sentence 2-3: a pivot, an escalation, or a reveal.** Either the "but here's what nobody tells you" turn, a bigger second number, or the first laugh/shock. The viewer must be rewarded once before 0:15.
4. **The subject can be withheld, but the TENSION cannot.** @CodeSource hides the topic for 100+ words but the anomaly is live in sentence one.
5. **Branding/self-intro is DEFERRED to ~30-60s**, after the hook has earned it. @awesome-coding's "I've been a software developer for 16 years" lands at 30-60s; @TheCodingSloth's "I'm a terrible programmer" lands at ~30-60s; @codehead01's subscribe ask is a quick aside ("Oh, and quickly before we start...") placed AFTER the hook.

### DO (drawn from the corpus)
- DO open on the dependency: "You've seen [famous thing]. It runs on [obscure thing you've never heard of]." (1.1)
- DO open on a contradictory number with no setup: "...valued at $9.3 billion, and it made $200 million last year." (1.4)
- DO concede then pivot: "Everyone thinks X. And they're right. But..." (1.3)
- DO open on a precise scene: "It's 3:00 a.m. Production is down." (1.2)
- DO restate the title in line one so the click is confirmed.

### DON'T
- DON'T open with a greeting, logo, channel name, or music-before-voice. Music goes UNDER the talking (@devforgehq).
- DON'T say "in this video I'm going to show you..." before the hook. The "in this video" promise, where present, lands only AFTER the pivot (~15-25s, @devforgehq).
- DON'T state your thesis as a flat conclusion when you can state it as a withheld mystery. **This is the flagship's likely error**: "you can't escape JavaScript" was probably asserted, not discovered. Compare @devforgehq doing the identical subject as a question: "So, how did this glitchy little goblin of a language end up running the world?"
- DON'T front-load the self-intro or credentials before tension exists.

### Concrete rewrite target for the flagship's open
Bad (asserted, flat, no withholding): *"JavaScript is everywhere and you can't escape it. In this video we'll look at why."*
Good (withheld dependency + paradox + confirms title): *"The bank app you opened this morning, the dashboard at work, the spaceship telemetry at NASA — all of it runs on a language one guy built in ten days as a joke. It's broken in ways that should be illegal. And you cannot get away from it."*

---

## 3. Pacing & resets — the system that fixes the 4:49 cliff

**The diagnosis.** A subtopic ran ~2.5 minutes and dragged. Across the corpus, **no single idea is held without a reset for more than ~60-90 seconds.** The drag at 4:49 is a missing-reset failure: the segment had no open loop, no pivot, no frame change, and no payoff to pull viewers across.

### 3.0 The hard heuristic to install
> **Max 45-60 seconds on a single idea before a reset.** A "reset" is at least one of: a pivot conjunction, a frame change, a pattern interrupt, a closed loop, or a new numbered item. If a subtopic genuinely needs 2.5 minutes, it must contain **3-4 internal resets** — otherwise split it or cut it.

Evidence: @Fireship changes frame (timeframe / character / metaphor / register) every **1-2 sentences**; @CleoAbram every **1-2 sentences** via "but/then/turns out"; @SwagProfessorExplain hard-cuts to a new list item every **30-60s**; @codehead01 / @devforgehq / @thecodingkoalaa cycle numbered beats every **20-60s**; @CodeSource teleports geography/decade every **30-60s**. Nobody coasts for 2.5 minutes on one frame.

### 3.1 Open loops (the through-line that carries the middle)
Plant ONE big unresolved question up front and withhold the answer until the final third, filling the middle with background as *rising tension* rather than a flat infodump.
- "the reason this bug took 21 years to fix is actually pretty interesting" — held the whole runtime (@awesome-coding).
- "stick around until the end" / "wait until you see the last one — it's borderline magic" (@devforgehq).
- The cold-open scene is itself the master loop and must be **literally closed** at the end: "Which brings us back to 2:19 a.m." (@CodeSource). If you open on a scene (1.2), you owe the viewer that callback — it converts "ended" into "resolved."

### 3.2 Pivot conjunctions (the reset engine)
The corpus runs on monosyllabic turns: **But / Then / Until / So / Turns out / And then something happened.** Drop one every 30-60s to re-open attention right as it sags.
- "But here's the thing" / "Here's what most people miss" / "Here's where most people get confused" (@codehead01).
- "But / Then / Turns out / Until" chained micro-resets (@CleoAbram, @CodeSource, @SwagProfessorExplain).
- @thecodingkoalaa's whole structure is `SETUP -> "but" -> TWIST`, looped.

### 3.3 Pattern interrupts
Insert a non-content jolt right where a teaching beat threatens to drag:
- Fake-out negation: "No, they weren't forced to socialize with the opposite sex." (@awesome-coding/@Fireship).
- Pre-empt-and-mock the objection: "back pressure. And no, that is not a CrossFit term." / "calibration. And no, not the kind where you adjust your monitor." (@Shadeofcode).
- Geographic/temporal teleport: "Thousands of miles away, in a small web design company in Chicago..." (@CodeSource) — free visual + narrative reset.
- A verbal stinger that caps a beat and snaps focus forward: "Boom." (@SwagProfessorExplain).
- A comedic non-sequitur dropped exactly when a beat sags: "Wait, GTA 6 got delayed?" (@TheCodingSloth).

### 3.4 The numbered/listicle spine (the cheapest retention mechanic)
Chunk the body into enumerated beats so the frame and subject reset on a predictable cadence and the viewer can re-enter anywhere. Each item is its own micro-hook ("Skill number one...", "Level one...", "First...").
- @SwagProfessorExplain's entire format: every item is `name -> what it is -> why it matters -> one weakness`, and the **weakness sentence is the bridge to the next item** ("But Python is slower than C++..." -> next). That problem->but->next-tool loop is what turns a flat list into an unstoppable chain. **This is the direct antidote to a 2.5-min drag**: convert the dragging subtopic into 3-4 numbered beats, each ending on the tension that motivates the next.

### 3.5 Analogy as a comprehension reset
One vivid physical analogy per dry stretch doubles as a frame-change and a memory hook: "index.html is the front door to your house" (@devforgehq), "a fire hose connected to a garden hose" (@Shadeofcode), "Git is a time machine for code" (@SwagProfessorExplain), "backend = the restaurant kitchen behind the double doors" (@technetiumm). Rotate 2-3 analogies on the SAME subject to make a static concept feel like it's moving: Cursor as "co-pilot -> captain -> air traffic controller" (@Fireship).

### 3.6 Cadence variation
Alternate long explanatory sentences with 2-4 word fragments to re-grab attention: "Exactly." / "Let's fix that." / "No magic." (@technetiumm); "10 days. 10 days." (@Shadeofcode); "This one is different." (@codehead01). Density of distinct ideas, not speed of delivery, is what reads as "fast" (@Fireship: ~one idea per sentence).

### 3.7 The punchline metronome (for personality channels)
Append a one-clause sardonic aside to factual sentences every ~10-15s so dense technical material stays rewarding ("GPU instances if you want to train an AI model or burn money quickly"). Optional; only if the channel has a comic voice.

### 3.8 Measured pacing bands (pacingInspo, n=17 videos)

§3.0's "≤45–60s on one idea" is a *narrative* reset ceiling. The figures below measure the finer-grained **visual cut cadence** — how often the picture changes — across 17 per-video studies in the repo-root `pacingInspo/` library (scene-change timeline × narration alignment). They don't replace §3.0; they show how each register *looks* operating under it. Four registers separate cleanly (full per-video numbers + contact sheets are in the library — read the `README.md` Quick index, never a raw `<slug>-pace.json`):

| Register | cuts/min | median scene | longest hold | cuts ride… | exemplars (slugs) |
|---|---|---|---|---|---|
| **Chaptered diagram / system-design explainer** | 0.9–2.6 | 9–15s | **105–480s** (one *evolving* canvas) | section turns (sentence-align 0.30–0.68) | `bytebytego-7-system-design-concepts`, `bytebytego-chat-system`, `bytebytego-transformers-stepbystep` |
| **Brisk sectioned / tier-list talking-head** | 6.5–10.5 | 3.4–5.9s | 17–41s | the item swap, not grammar (align 0.04–0.06) | `latticx-cs-advice-tier-list`, `awesome-real-problem` |
| **Fast video essay / listicle B-roll churn** | 17–42 | 1.1–3.2s | 6–30s | the breath, mid-clause (align 0.08–0.49, med 0.19) | `fireship-github-outage-news`, `codehead-top-10-ides`, `swagprof-every-language-7min`, `technetium-25-cybersec-terms`, `codingsloth-get-rich-essay` (+4) |
| **Vertical Short (<60s)** | 26–39 | 0.7–1.5s | 3–14s | the word (align ≤0.08) | `cleo-deep-sea-unknown-species`, `cleo-nuclear-space-ship`, `cleo-how-old-diamonds-are` |

Two findings hold across all 17, regardless of register:

- **Cuts ride the narration, not the silence.** `pct_cuts_in_pause` is ≈0.00 in every video (max 0.05) — the visual changes *while the voice runs*, never waiting for a gap. Budget cuts to land on the next idea, not in a pause.
- **A faster register is *less* sentence-aligned, not faster-spoken.** Slow explainers cut at section/sentence turns (align 0.30–0.68); churn essays and Shorts cut mid-clause on the breath (align ≤0.19). Speed is bought by *decoupling* the cut from grammar — `words_per_s` only climbs ~2.4 → ~4.4 across the whole range while cuts/min climbs 0.9 → 42.

The R1 long holds (one canvas held 100s+) are **not** §3.0 violations: the substrate is *evolving in place* (a diagram mutating, markers walking a timeline), and that internal motion is itself the reset — §3.0's "3–4 internal resets" exception rendered visually instead of narratively. (R2 is the thinnest band, n=2; treat its numbers as provisional until more sectioned talking-heads land.)

### Fixing 4:49 specifically
The dragging subtopic almost certainly violated 3.0 (one frame > 90s), 3.1 (no live open loop), and 3.4 (not chunked). Rebuild it as: a sub-question planted ("but there's one part of this nobody explains") -> 2-3 numbered beats each on a new visual frame, each ending on a "but" that motivates the next -> a payoff that closes the sub-question and hands off to the next major section.

---

## 4. CTAs

### 4.1 Long-form
- **Placement is end-only.** Almost no mid-roll subscribe ask. The one exception pattern is a quick front aside placed AFTER the hook, not before: "Oh, and quickly before we start, I post three videos weekly. So, subscribe... All right, let's go." (@codehead01).
- **The sponsor read is the real mid-video CTA**, dropped at a natural cliffhanger/act break with an in-and-out signpost: "But before [the payoff], let me tell you about today's sponsor... Back to the video." (@awesome-coding) / "Before we continue, a quick but important note... And now, back to the story." (@CodeSource). Bridge it thematically and keep the narrator's voice unchanged.
- **Tone: low-pressure, value-framed, never begging.** "Smash all the buttons" parodies the cliché so the ask is in on the joke (@awesome-coding). "If you want [specific next outcome], I [already] made a video on it... Just click it and I'll see you there." (@devforgehq) routes to the creator's OWN next video, building a session-watch loop instead of sending viewers away.
- **A fixed sign-off becomes a brand asset.** "This has been the Code Report. Thanks for watching, and I will see you in the next one." (@Fireship, ~16/20 closes); "I'll see you guys in the next one." (@thecodingkoalaa, every video).
- **Comment-bait as service, not demand.** "comment if you want a deep dive on the hypervisor" (@awesome-coding) / "drop a comment if you want a part two" (@thecodingkoalaa) — doubles as topic research.
- **Forward-pushing offline imperative** as a close that reads as actionable: "Now, go break some code." / "Close those 47 tabs, pick one small project, start building." (@technetiumm).

### 4.2 Shorts — the Cleo Abram pattern (seeds the Shorts skill)
**Placement.** Always the **final sentence**, fused to a freshly-opened loop — never appended as a separate ask. She solves the stated question, then in the last 1-2 sentences raises a NEW, bigger related mystery and offers subscribing as the only way to resolve it. The CTA inherits an unresolved loop instead of asking cold. The video never reaches rest.

**Exact wording shapes (use verbatim as templates):**
- "But the moon is drifting away. So, where's it going? **To find out, subscribe.**"
- "**To see it, subscribe.**"
- "**If you want to know how, subscribe.**"
- "**For more optimistic science and tech stories, subscribe.**" (brand tagline rides the CTA, never the open)
- Audience-participation variant: "So which do you think is the biggest? **Subscribe.**"

**The shape to encode:** `[solve the headline question] -> [open a NEW bigger loop in 1 sentence] -> [subscribe framed as the way to close THAT loop].` Tone is warm and conspiratorial; the subscribe is the natural next step to satisfy a cliffhanger she just planted, not a favor. All branding is deferred to this final line.

---

## 5. Title formulas

Repeatable templates observed across the corpus. The first spoken line and the title are usually the same idea phrased two ways — write them together.

**For history / explainer (the "quiet dominance / untold origin" family — our lane):**
- **How [Tech] Quietly Took Over [Domain]** — "How PostgreSQL Quietly Took Over", "How Chromium Quietly Became The Web". The word "quietly" recurs verbatim.
- **The [Tech] You've Never Heard Of That Runs The World** / **The Shell That Runs the World** (@CodeSource).
- **The Untold / Secret History of [Tech]** — "The Untold Story of R".
- **Why [Tech] Quietly Disappeared** / **The Rise and Fall of [Tech]** — "Why Perl Quietly Disappeared", "The Rise and Fall of Sublime Text".
- **Why [Old Tech] Refuses To Die / Why The World Still Runs On [Old Tech]** (gravity/dependency framing).
- **The [Aged-bug / aged-decision] story** — "MySQL took 21 years to fix this bug". Restate the exact duration/date in line one.
- **[Tech] Was Built By [Improbable Origin]** — "a joke between two guys in a corridor in New Zealand".
- **The forgotten [person] who saved [Tech]** — "The forgotten developer who saved JavaScript..." (@Fireship).

**Anthropomorphized-paradox (directly applicable to our JS flagship):**
- **[Tech] Is Broken... So How Does It Run the Entire Internet?** (@devforgehq).
- **[Tech] is [provocative claim] (and won anyway)**.

**Contrarian / reversal:**
- **Why the "[X] Is Over" Narrative Is Wrong** (@devforgehq).
- **[Status object] Is Dead... And That's Your Opportunity** / **Everyone Thinks [X]. They're Wrong.**
- **[Famous Person] Said [Provocative Claim]. Here's the Truth** (@Shadeofcode).

**Numbered / list:**
- **Every [category] Explained in [N] Minutes** — "Every Major Programming Language Explained in 7 Minutes", "Every Linux Distro Explained in 4 Minutes" (@SwagProfessorExplain, @technetiumm). Strong recurring-search SEO.
- **N [Concepts/Skills/Mistakes] That [Verb]** — "10 Programming Mistakes That Will RUIN YOUR LIFE", "The N Concepts Nobody Teaches You".
- **The [Concepts] Nobody Talks About / Nobody Teaches You** (@Shadeofcode).

**Curiosity-question:**
- **Why [absurd-sounding true premise]?** — "Why are there 700 programming languages?", "Why were 90s programmers so legendary?".
- **Is [Credential/Skill] Dead?** / **Should You... Keep Coding?**

**Time-bounded promise (tutorials):**
- **[Tech] in 100 Seconds** / **Give Me [N] Minutes, I'll [Outcome]** (@technetiumm, @Fireship).

**Business-model reveal:**
- **The Genius Business Model Behind [Free Product]: $[N] a Year Giving It Away Free** (@thecodingkoalaa).

**Title craft rules:** specificity wins (exact number/date/duration); use ALL-CAPS on one or two charged words, not the whole line ("DOMINATING", "RUIN YOUR LIFE", "ELITE"); stamp the year ("in 2026") for freshness + recurring search; the title and first spoken sentence must restate each other.

---

## 6. Wiring recommendations (per workstream)

### WS1 — script-writer (the highest-leverage changes)
Add these as hard rules to the skill:

1. **Cold-open mandate.** The first sentence of `script.md` MUST be a complete hook — a claim, number, question, or scene. Forbid as the opening line: any greeting, channel name, logo cue, music-before-voice, "in this video," "today we're going to," or a self-intro. Lint the draft: if word 1-30 contains none of {a number, a question mark, a named concrete subject, a present-tense scene verb}, reject the open.
2. **Title-confirmation rule.** The title's core promise must appear in sentence one (paraphrase allowed). Write title and first line as a pair.
3. **Withhold-the-conclusion rule (the flagship's specific fix).** When the thesis is a quiet-dominance claim, state it as a *withheld mystery or paradox*, not a flat assertion. Prefer "How did [subject] end up [outcome]?" over "[Subject] is [outcome]." Reference: the failed "you can't escape JavaScript" vs. @devforgehq's "how did this glitchy little goblin of a language end up running the world?"
4. **Deferred-intro rule.** Any self-intro/credentials/branding goes at the 30-60s mark, only after the hook. Never before tension exists.
5. **One-master-loop rule.** Plant exactly one big open question in the first ~20s and do not resolve it until the final third. If the open is a cold-open scene, the script MUST close it with an explicit callback ("which brings us back to...").
6. **Subtopic-reset rule (the 4:49 fix).** No single idea may run longer than ~45-60s of narration without a reset (pivot conjunction / frame change / pattern interrupt / closed loop / new numbered item). Any subtopic budgeted over ~90s must be authored as 3-4 numbered sub-beats, each ending on a "but/then" tension that motivates the next beat. Flag any contiguous run of explanation with no "But/Then/Until/Turns out/So" and no new frame for >2 paragraphs.
7. **Pivot-grammar rule.** Build sub-claims on `[setup] -> But/Then/Turns out -> [twist]`. Seed at least one pivot conjunction per ~60s.
8. **Analogy-per-dry-stretch rule.** Every abstract mechanism gets one concrete physical analogy on first mention; rotate 2-3 analogies on a single subject across a long segment.
9. **Cadence rule.** Interleave 2-4 word fragments with longer sentences; never run more than ~3 long sentences without a short punch.
10. **End-CTA rule.** Close with a value-framed route to the channel's own next video plus a fixed sign-off catchphrase; treat the sponsor read (if any) as a mid/late act-break with thematic bridge + "back to the story," never a cold front-load.

### WS4 — shorts-creator
Hook + CTA spec, grounded in @CleoAbram and the Shorts patterns:

1. **One idea only.** Each Short orbits a single counterintuitive question; refuse scope creep. ~130-260 spoken words.
2. **Hook in the first 5-9 words**, present tense, no name/branding/"in this video." Use 1.5 (provocative why/what), 1.4 (shocking number), or the reframe ("X has an evil twin"). The first visual shows the literal subject so words and image confirm each other.
3. **Plant the counter-twist in sentences 2-3** ("By a lot." / "Turns out insanely hard." / "But then, how do we know...").
4. **Body = a chain of "but/then/turns out" pivots**, each invalidating the expectation just set; change the on-screen frame every 1-2 sentences. Use a numbered or zoom scaffold for countdown tension.
5. **One mid-Short meta-reward** at peak surprise only: "Subscribe if this is already blowing your mind."
6. **CTA = the final sentence, fused to a fresh loop** (the Cleo shape): `[solve headline] -> [open a bigger new loop in one sentence] -> "To find out, subscribe." / "To see it, subscribe." / "For more [tagline], subscribe."` Defer all branding to this line. Never end on resolution; end on the next mystery handed to the subscribe button.

### WS3 — publish-qa ("good packaging" per the corpus)
1. **Title.** Must match a Section-5 template; for our lane prefer the quiet-dominance/untold-origin family ("How [Tech] Quietly Took Over...", "The [Tech] That Runs the World", "Why [Tech] Refuses to Die"). Must contain a specific number/date/duration where the topic allows. ALL-CAPS limited to 1-2 charged words. Title and the script's first line must restate each other — QA should diff them and flag a mismatch.
2. **Title length & front-loading.** Put the most curiosity-loaded element first (the famous subject, the shock number, the question word) so it survives truncation.
3. **Description.** Lead with a one-paragraph restatement of the hook (the withheld-dependency framing), not a dry summary. Include the channel's fixed sign-off identity. Chapters/timestamps should mark each major reset boundary (Section 3) so the structure is legible to the algorithm and to skimmers. Comment-bait sequel offer in the description ("want a part two on X?") to drive engagement and seed future topics.
4. **Thumbnail/title pairing.** The thumbnail should carry the subject or the shock number; the title carries the paradox/question — they should not say the same thing twice.
5. **Year stamp** where the topic is evergreen-with-drift, for recurring-search SEO.

### WS2 — SRT
**Not informed by creator research.** The 12-channel script-craft corpus says nothing about subtitle segmentation, timing, line-length, or translation quality. WS2 should continue to follow the existing `create-srt-and-translate` skill and the Scribe v2 transcript-as-timing-truth convention. No hook/pacing/CTA rule from this document transfers to SRT generation; do not retrofit any.
