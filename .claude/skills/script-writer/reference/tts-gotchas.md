# TTS gotchas — living list

This is the only reference file the skill modifies during a session. When the user catches a new TTS failure ("Kokoro mangled X"), append it here under the appropriate section so the next video benefits.

## Why this matters for this project

The user has to use TTS — there is no real-voice option. This project ships
on **ElevenLabs v3** via the `voiceover-elevenlabs` skill (Kokoro stays
parallel for non-project use). The research on the channel we're modeling
found **52 separate top comments across 7 of 8 videos flagged AI voice
failures**, and two specific glitches kept getting cited as "this is what
told me it was AI":

- "two point five-ty eight bits" (the TTS rendered "2.58" oddly)
- "lives" pronounced as "lie-vs" instead of "livs" (homograph collision)

Modern TTS handles 90% of words perfectly; the 10% that breaks gets noticed. For technical content with unusual numbers, dates, and units, that 10% is a constant landmine.

The mitigation is simple: **rewrite the script around what TTS does well, not around what's most natural to write.** This is a script-side intervention, not a post-render fix.

### Scope: script-side only

This file is consumed by the `script-writer` skill at drafting time. It is
about **prose rewrites a writer makes before annotation**. Things that
belong in `voiceover-elevenlabs` instead (do **not** put them here):

- Audio tags (`[whispers]`, `[laughs]`, `[curious]`, etc.)
- ALL-CAPS emphasis decisions
- Ellipsis insertion for pacing
- ElevenLabs voice / stability / similarity settings
- Pronunciation dictionary entries (the `voiceover-elevenlabs` tool is the
  durable place for those)

Keep `script.md` plain prose. Annotation happens downstream.

## Meta-rules

Apply these while drafting, not as a post-pass:

1. **Spell out decimals where they would be unusual.** "2.58 bits" → "roughly two and a half bits" or "about two point six bits". The TTS often glitches on "point five-ty eight" or similar.
2. **Avoid English homographs.** Words like "lives" (verb vs plural noun), "wound" (verb vs noun), "lead" (verb vs metal), "row" (verb vs noun). Rewrite to disambiguate by context, or pick a synonym.
3. **Prefer two short sentences over one long sentence with a parenthetical.** TTS prosody on long sentences with embedded clauses is fragile — it often misplaces emphasis or drops the inflection at the end. v3 is especially sensitive here; embedded clauses inside em-dash pairs collapse the inflection on the second half.
4. **Avoid abbreviations the TTS doesn't expand consistently.** TLS, SSH, GPU, RGB are usually fine because the TTS spells them as letters; UID, IDOR, UUIDv7 may glitch. Spell out the first time, then use the abbreviation.
5. **Numbers with unusual units need rewording.** "45ms" might become "45 milliseconds" reliably; "1/3 of a pixel" usually works; "128-bit value" works; "2.58" does not.
6. **Test suspicious lines before committing.** If you're not sure how the TTS will read a line, render just that sentence first.
7. **Don't reach for SSML.** ElevenLabs v3 does not support `<break time="…"/>` tags. Pauses come from punctuation (commas, ellipses, em dashes) and audio tags. SSML phoneme tags are also v3-unsupported (they only work on Flash v2 / English v1). If you find yourself wanting to mark up the prose, write it so it doesn't need markup — that's the whole point of this file.
8. **Voice-first.** A naturally calm voice asked to deliver a shouted line will sound muted, no matter how the script is written. If a beat genuinely requires a register the chosen voice can't hit, convey intensity through word choice and short sentences rather than counting on the TTS to lift it.
9. **Mind the chunk floor.** v3 generation gets unstable below ~250 characters per request. Not usually a problem inside a 5-min script, but if a beat ever has to be rendered as its own chunk (re-take, splice), pad it or merge it with a neighbor.
10. **Letter-spelled vs word-shaped acronyms behave differently.** Two-to-four-letter acronyms the model already knows as letter strings (HTTP, TLS, GPU, RGB, CSS, SQL-as-letters) read fine. Anything the model might try to say as a *word* (IDOR, SQL-as-"sequel", JWT-as-"jot") needs explicit handling — see the acronyms table.

## Pre-seeded gotcha list

### Decimals

| Failing input | Failure mode | Rewrite recipe |
|---|---|---|
| "2.58 bits" | Renders as "two point five-ty eight bits" | "roughly two and a half bits" / "about two point six bits" / "around 2.6 bits" |
| Any decimal in a number-of-bits context | TTS treats decimal as ordinal | Round to one decimal place and spell out: "two point six" |
| "1.5x faster" | "one point five-x faster" / "one and a half ex faster" | "one and a half times faster" |
| "v1.2", "v2.5" | "vee one point two" / version numbers garble | "version one point two" the first time, then "v one two" if you must reuse |

### Dates, currencies, units

| Failing input | Failure mode | Rewrite recipe |
|---|---|---|
| "2024-01-01" | Reads as a phone-like number string | "January first, twenty twenty-four" |
| "1/3" | Often "one slash three" instead of "one third" | "one third" |
| "$1,234.56" | Comma + decimal + dollar sign trips it | "one thousand two hundred thirty-four dollars and fifty-six cents" — or round: "about twelve hundred dollars" |
| "100GB", "5MB", "200ms" | Concatenated number+unit may glitch on the unit | Add a space and spell the unit: "100 gigabytes", "5 megabytes", "200 milliseconds" |
| "10°C", "60°" | Degree symbol skipped or read literally | "10 degrees Celsius", "60 degrees" |
| "%" mid-sentence | Sometimes dropped | Spell it: "70 percent" |
| Phone numbers ("555-1234") | Read as "five hundred fifty-five minus…" | Comma-separated digits or fully spelled: "five five five, one two three four" |
| URLs ("elevenlabs.io/docs") | Punctuation read literally | Spell connectors: "eleven labs dot io slash docs" |
| Roman numerals ("Section IV") | Read as the letters "I-V" | "Section four" |

### Homographs

| Failing input | Failure mode | Rewrite recipe |
|---|---|---|
| "lives" (as verb, e.g. "the data lives in RAM") | Pronounced "lie-vs" | "the data is alive in RAM" / "sits in RAM" / "exists in RAM" |
| "rows" (as in database rows) | Sometimes lands as "raus" | "records" / "entries" if context is database-y |
| "row" (verb vs noun) | Same | Same — pick the unambiguous synonym |

### Abbreviations and acronyms

| Failing input | Failure mode | Rewrite recipe |
|---|---|---|
| "UUIDv7" | Stumbles on the version suffix | "UUID version 7" — spell out fully on first and second use |
| "IDOR" | TTS may read as a word | "an insecure direct object reference, or IDOR" — name it once before abbreviating |
| "SQL" | Inconsistent: sometimes "ess-cue-ell", sometimes "sequel" | Pick one and force it: "S-Q-L" with hyphens for the letter reading, or "sequel" spelled phonetically. Don't leave it ambiguous. |
| "JWT" | "jot" vs "J-W-T" varies by voice | "a JSON Web Token, or J-W-T" the first time |
| "API" | Usually fine, occasionally "appy" | "A-P-I" with hyphens if the voice slips |
| "i.e." / "e.g." | Read as "ee-eye" / "ee-gee" | "for example" / "that is" — never use the Latin abbreviations in TTS scripts |
| "etc." | Sometimes "et cetera", sometimes "ee-tee-cee" | Spell it: "and so on" or "et cetera" |
| "vs" / "vs." | "vee-ess" instead of "versus" | "versus" — always spell it out |
| Anything with a slash ("HTTP/2", "TCP/IP") | Slash read literally | "HTTP version 2" / "TCP IP" without the slash |

### Phonetic respelling — escape hatch for proper nouns

When a rewrite isn't possible (a person's name, a product, a place), force
the pronunciation by respelling it phonetically. Tricks the model honors:

- **Hyphens** to separate syllables: `Argon-2` → reads as "ar-gon two" cleanly.
- **Capital letters** to mark stress or letter-reading: `S-Q-L` reads as
  letters; `kayBOR` puts the stress on the second syllable.
- **Apostrophes / single quotes** around individual letters: `R'G'B` to
  force letter spelling when the bare token would be read as a word.
- **Alternate spelling** by ear: write what you want it to sound like, not
  how it's actually spelled. `Caching` reading as "cashing" wrong? Try
  `cashing`. `Schema` as "shee-ma" wrong? Try `skee-ma`.

This is a last resort — every respelling is a maintenance burden and looks
weird in the script. Prefer rewording around the problem token first. When
you do respell, leave a comment in `script.md` (`<!-- TTS: Argon-2 -->`)
so the next reader knows it's intentional.

For genuinely durable cases (recurring product names, recurring proper
nouns), respell inline and leave a `<!-- TTS: Argon-2 -->` comment so
the next reader knows it's intentional.

> Future: ElevenLabs supports project-level pronunciation dictionaries
> (alias rules for v2; phoneme tags for some v1/Flash models; max 3
> locators per request via `pronunciation_dictionary_locators`). Not
> wired into our tools yet — add when the same respelling shows up
> across two or more videos.

### Long parenthetical sentences

| Failing input | Failure mode | Rewrite recipe |
|---|---|---|
| "X (which is Y) does Z" | Prosody collapses around the parenthetical | Two sentences: "X does Z. X is Y." |
| Sentences over 22 words with embedded clauses | Inflection drops mid-sentence | Break at the natural conjunction |
| "X — and this is the part that matters — does Z" | Em-dash pair eats the second-half emphasis on v3 | Either two sentences, or move the aside to its own short sentence after: "X does Z. And that's the part that matters." |
| Trailing "— but only when Y" tagged onto a long sentence | Final clause loses pitch and reads flat | Promote the qualifier to its own short sentence so it lands. |

### Register and emotional range

These aren't pronunciation bugs — they're places where the rendered audio
will sound *off* even though every word is correct. The fix is script-side,
not annotation-side.

| Failing input | Failure mode | Rewrite recipe |
|---|---|---|
| A line that needs to be shouted, voiced by a calm-voice clone | Comes out muted regardless of `[shouting]` tag | Convey intensity through word choice and short sentences instead. "It exploded." beats "[shouting] It exploded!" on a calm voice. |
| Sarcasm written deadpan | Lands as sincere — viewers miss the irony | Make the sarcasm structurally obvious (juxtapose with the literal claim immediately) or drop the sarcastic register entirely. |
| Long stretch of single-tone exposition (>60s without rhetorical pivot) | Voice drifts into monotone even on Natural stability | Insert a "But" pivot or a rhetorical question every ~45s. The 1-in-5-short-sentences rule already buys most of this. |
| A question written without a question mark | Read as a statement, no upward inflection | Always punctuate questions, even rhetorical ones. |

## How to add a new gotcha

When the user surfaces a new TTS failure during a session:

1. Identify the failing token, the failure mode (what it sounded like), and a working rewrite.
2. Find the right section in this file (decimals, homographs, abbreviations, etc.) — or add a new section if needed.
3. Append a row to the table in that section.
4. Apply the rewrite to the current script immediately.

Format for a new entry:

```
| <failing input> | <what TTS produced> | <rewrite recipe> |
```

Keep the entry short. The point is recall, not exhaustive documentation.
