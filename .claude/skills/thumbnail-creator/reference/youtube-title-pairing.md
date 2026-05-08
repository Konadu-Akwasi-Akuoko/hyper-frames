# YouTube title pairing

The thumbnail text and the YouTube title do **different jobs**. They
should differ. This file documents how to write the paired title for
each thumbnail variant.

Underlying observations:
`research/pawel-code-stuff/analysis/thumbnail-patterns.md` §7, §11.

## The two jobs

| Surface | Job | Optimized for |
|---|---|---|
| Thumbnail text | Win the click in the feed | ALL CAPS, punchy declarative, can make the BIGGER claim |
| YouTube title | Win search and the algorithm | Sentence case, contains the literal topic noun, one scannable line |

If the title and thumbnail say the same thing, you lose either:

- search reach (title is too undifferentiated/punchy to rank), or
- click-through (thumbnail is too keyword-stuffed and mealy).

Let them play different roles. The leverage is in the asymmetry.

## Rules

1. **Different from the thumbnail.** Verbatim duplication (or its
   sentence-cased twin) kills the pairing. If the thumbnail says
   `TEXT RENDERING IS INSANELY DIFFICULT`, do not title the video
   "Text rendering is insanely difficult." Rewrite.
2. **Sentence case.** Capitalize the first word and proper nouns;
   everything else lowercase. ALL CAPS is reserved for the thumbnail.
3. **Carry the searchable noun.** Include the literal topic word the
   viewer would type into YouTube. For a typography video that means
   "text", "rendering", or "font". For a database video, "database",
   "index", or "query".
4. **Length: 40–70 chars target. Hard cap 100.** YouTube truncates
   past ~70 chars in most feed layouts. Aim for one scannable line.
5. **Thumbnail amplifies, title earns.** The thumbnail can claim
   bigger than the title would dare. The title is the technical,
   defensible version of that claim. Pawel's pattern (analysis §7):
   `WHY YOUR MOUSE SECURES THE INTERNET` (thumbnail, sweeping) pairs
   with "Why moving your mouse generates secure keys" (title,
   narrower, searchable).
6. **No emoji, no SHOUT words, no keyword stuffing.** Cap
   parenthetical asides at one. One `:` or `—` maximum.

## Patterns that work

- **Question:** "Why is X so Y?" / "How does X work?"
- **Mechanism:** "How your computer does X" / "What happens when X"
- **Declarative claim:** "X is the reason Y" / "Inside the X that Y"
- **Honest technical:** "X explained" — fine for high-volume search
  topics where the search noun itself does the work (analysis §4
  notes Pawel returns to the formula for searchable topics like
  "auto-increment vs UUID")

## Patterns to reject

- "Ultimate guide to X" — clickbait shape, low information.
- "X explained in N minutes" — Pawel's old formula. It's now strongly
  associated with him; using it would put your titles next to his and
  lose on direct comparison. Pick your own variant.
- A paraphrase with the same length and grammar as the thumbnail —
  just say something genuinely different.

## Pairing examples (from the analysis corpus)

| Thumbnail | Paired title | Notes |
|---|---|---|
| TEXT RENDERING IS INSANELY DIFFICULT | Why is rendering text so complicated? | Title softens "insanely difficult" → "so complicated"; question form earns search |
| WHY YOUR MOUSE SECURES THE INTERNET | Why moving your mouse generates secure keys | Title narrows the sweep ("secures the internet" → "generates secure keys"); contains "mouse" + "secure keys" for SEO |
| GOOD PASSWORD HASHING MUST BE SLOW | Why good password hashing is intentionally slow | Title swaps imperative "must" for descriptive "is intentionally"; same nouns, calmer register |

Notice the title in each row is **softer, more searchable, and less
clickbait-shaped** than the thumbnail. That asymmetry is the point.

## Per-variant writing routine

For each of the 3 thumbnail variants:

1. Read the variant text aloud. What is the BIG claim?
2. Write the title that delivers the search-friendly version of that
   claim. Often this is close to the original working title from
   `outline.md` — that's expected; the working title was already
   shaped for SEO instinct.
3. Check it against the rules: length, sentence case, contains topic
   noun, different from thumbnail.
4. Two variants pairing to similar titles is fine, but try to vary
   form (sometimes question, sometimes declarative). The contact
   sheet shows them side-by-side; identical-shaped titles waste the
   review surface.

## What this skill does NOT do for titles

- **A/B-test titles.** YouTube's native A/B mechanism handles that
  (independent of thumbnails — you can test 3 thumbnails × 3 titles).
  The skill ships ONE paired title per variant. The user picks; the
  YouTube console tests.
- **Generate descriptions, tags, chapters, or end screens.** Out of
  scope. Title and thumbnail are the click-pull surfaces; the rest is
  metadata.
