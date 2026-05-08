# Text rephrase recipes

Patterns for turning a video's working title into a punchier thumbnail
text. The thumbnail text is **not** the video title — it's a bolder
rewrite per the research's rephrase pattern. The video title carries SEO
keywords; the thumbnail text wins the click.

These recipes are drawn from `research/pawel-code-stuff/analysis/script-patterns.md`
and the rephrase analysis in `research/pawel-code-stuff/analysis/thumbnail-patterns.md` §4.

## Hard constraints (every variant must satisfy)

- 7–11 words total.
- Exactly 3 rows.
- ALL CAPS.
- Fits in JetBrains Mono ExtraBold across 3 rows of ~13–14 monospace
  characters each at the target font size. The renderer does NOT silently
  shrink text to fit. If a rephrase doesn't fit, rewrite shorter or ask
  the user for a shorter wording — never let the renderer hide overflow.
- No question marks, ellipses, colons, parentheses.
- No adverbs except for emphasis ("INSANELY", "BRUTAL", "CATASTROPHIC").

## The rephrase moves

### Move 1 — Softer to harder

Replace softer phrasing with harder phrasing:

- "is intentionally" → "must"
- "can be" → "is"
- "how to make X" → imperative "make X"
- "why X is Y" (question) → "X is Y" (declarative)

**Example:** *"Why Good Password Hashing is Intentionally Slow"* →
**`GOOD PASSWORD / HASHING MUST / BE SLOW`**

### Move 2 — Question to declarative

If the title is a question, drop the question mark and assert the answer.

**Example:** *"Why is rendering text so complicated?"* →
**`TEXT RENDERING / IS INSANELY / DIFFICULT`**

### Move 3 — Narrow to sweeping

Replace a narrow technical claim with a sweeping one:

- "generates secure keys" → "secures the internet"
- "fixes a bug" → "saves your database"

**Example:** *"Why Moving Your Mouse Generates Secure Keys"* →
**`WHY YOUR MOUSE / SECURES THE / INTERNET`**

### Move 4 — Adjective upgrade

Push a soft adjective to a harder one:

- "complicated" → "insanely difficult"
- "fast" → "brutal"
- "important" → "catastrophic"
- "tricky" → "a fight"

The adverb is allowed *only* in upgrade position ("INSANELY", "ABSURDLY",
"DANGEROUSLY") — never as a hedge ("usually", "sort of", "kind of").

## Generating three variants

Each round produces 3 thumbnail-text rephrases. They should differ on
*direction*, not just on word choice — otherwise the user can't make a
real choice between them.

Recommended distribution per round:

1. **Variant A — direct upgrade.** Apply Move 1 + Move 4. Keep the title's
   topic noun front-and-center.
2. **Variant B — sweeping reframe.** Apply Move 3. Make the bigger claim.
3. **Variant C — punchy declarative.** Apply Move 2 + Move 4. Shortest
   wording; declares the surprising fact.

If the user says "all three feel safe", push Move 4 harder (escalate the
adjective) on all three. If "all three are too aggressive", soften Move 4
or drop it.

## Worked examples

### Example 1 — text rendering

- **Working title:** *Why is rendering text so complicated?*
- **Variant A (direct):** `TEXT RENDERING / IS INSANELY / DIFFICULT` (8 words)
- **Variant B (sweeping):** `A LETTER ON / YOUR SCREEN IS / A FIGHT` (8 words)
- **Variant C (punchy):** `YOUR FONT IS / LYING TO / YOU` (6 words — too short, expand to 7+)
  - Fixed: `YOUR FONT IS / LYING TO / YOUR EYES` (7 words)

### Example 2 — password hashing

- **Working title:** *Why good password hashing is intentionally slow*
- **Variant A:** `GOOD PASSWORD / HASHING MUST / BE SLOW` (7 words)
- **Variant B:** `THE FASTEST CODE / IS THE WORST / PASSWORD CODE` (10 words)
- **Variant C:** `HASHING SHOULD / TAKE A / WHOLE SECOND` (7 words)

### Example 3 — mouse keys

- **Working title:** *Why moving your mouse generates secure keys*
- **Variant A:** `YOUR MOUSE / GENERATES / SECURE KEYS` (6 — expand to 7+)
  - Fixed: `WHY YOUR MOUSE / GENERATES / SECURE KEYS` (7 words)
- **Variant B:** `WHY YOUR MOUSE / SECURES THE / INTERNET` (7 words)
- **Variant C:** `MOVE YOUR MOUSE / OR THE INTERNET / FAILS` (8 words)

## Anti-patterns

- "TOPIC EXPLAINED IN N MINUTES" — that's the formula pattern. The research
  shows it works for SEO-heavy topics but loses engagement; reserve it as a
  fallback when the user says "all three are too aggressive, give me one
  that's safer."
- Stacking adjectives ("INSANELY DIFFICULT IMPOSSIBLE") — pick one.
- Filler words ("ACTUALLY", "REALLY", "BASICALLY") — cut them.
- Apologetic framing ("MAYBE", "MIGHT", "PROBABLY") — never.
