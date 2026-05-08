# TTS gotchas — living list

This is the only reference file the skill modifies during a session. When the user catches a new TTS failure ("Kokoro mangled X"), append it here under the appropriate section so the next video benefits.

## Why this matters for this project

The user has to use TTS (Kokoro or similar) — there is no real-voice option. The research on the channel we're modeling found that **52 separate top comments across 7 of 8 videos flagged AI voice failures**, and two specific glitches kept getting cited as "this is what told me it was AI":

- "two point five-ty eight bits" (the TTS rendered "2.58" oddly)
- "lives" pronounced as "lie-vs" instead of "livs" (homograph collision)

Modern TTS handles 90% of words perfectly; the 10% that breaks gets noticed. For technical content with unusual numbers, dates, and units, that 10% is a constant landmine.

The mitigation is simple: **rewrite the script around what TTS does well, not around what's most natural to write.** This is a script-side intervention, not a post-render fix.

## Meta-rules

Apply these while drafting, not as a post-pass:

1. **Spell out decimals where they would be unusual.** "2.58 bits" → "roughly two and a half bits" or "about two point six bits". The TTS often glitches on "point five-ty eight" or similar.
2. **Avoid English homographs.** Words like "lives" (verb vs plural noun), "wound" (verb vs noun), "lead" (verb vs metal), "row" (verb vs noun). Rewrite to disambiguate by context, or pick a synonym.
3. **Prefer two short sentences over one long sentence with a parenthetical.** TTS prosody on long sentences with embedded clauses is fragile — it often misplaces emphasis or drops the inflection at the end.
4. **Avoid abbreviations the TTS doesn't expand consistently.** TLS, SSH, GPU, RGB are usually fine because the TTS spells them as letters; UID, IDOR, UUIDv7 may glitch. Spell out the first time, then use the abbreviation.
5. **Numbers with unusual units need rewording.** "45ms" might become "45 milliseconds" reliably; "1/3 of a pixel" usually works; "128-bit value" works; "2.58" does not.
6. **Test suspicious lines before committing.** If you're not sure how the TTS will read a line, render just that sentence first.

## Pre-seeded gotcha list

### Decimals

| Failing input | Failure mode | Rewrite recipe |
|---|---|---|
| "2.58 bits" | Renders as "two point five-ty eight bits" | "roughly two and a half bits" / "about two point six bits" / "around 2.6 bits" |
| Any decimal in a number-of-bits context | TTS treats decimal as ordinal | Round to one decimal place and spell out: "two point six" |

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

### Long parenthetical sentences

| Failing input | Failure mode | Rewrite recipe |
|---|---|---|
| "X (which is Y) does Z" | Prosody collapses around the parenthetical | Two sentences: "X does Z. X is Y." |
| Sentences over 22 words with embedded clauses | Inflection drops mid-sentence | Break at the natural conjunction |

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
