# SRT chunking rules

The `transcript_to_srt.py` script groups Scribe v2 word entries into SRT
caption blocks. These are the parameters that govern how blocks are sized
and where they break. Read this if you ever need to tune the chunker for a
different content type (faster speech, slower speech, etc.).

## Hard limits (block boundaries)

| Parameter | Value | Why |
|---|---:|---|
| `MAX_CHARS` | 84 | YouTube's caption window comfortably holds ~42 chars × 2 lines. Past this, the second line wraps onto a third. |
| `MAX_DUR` | 7.0 seconds | A block longer than 7 s of speech is uncomfortable to read in one go; the viewer's eye loses its place. |
| `MIN_DUR` | 1.2 seconds | A block that flashes for under a second is unreadable, even if the underlying audio is that short. Pad it. |

## Soft preferences (break placement)

Break at sentence-end punctuation (`.`, `!`, `?` plus a trailing quote or
bracket if present) **once the block has accumulated either**:

- 4 or more words, **or**
- 25 or more characters

This avoids "Yes." sitting alone on a flash card while still letting
short emphatic sentences land on their own lines.

## Two-line wrap

Long single-line blocks split onto two lines at a space close to the
midpoint. The split point is the space nearest the literal halfway
character — left or right, whichever is closer. No hyphenation, no
mid-word splits.

A block of 42 chars or fewer is rendered on a single line.

## Why these specific values

These were tuned against a 387-second / 2045-word HyperFrames explainer
(narrated voiceover, ~3.5 words per second). At that speech rate, a 7 s
block holds ~24-25 words, which lines up well with English's natural
sentence cadence in this style.

If you're captioning very fast speech (rap, auctioneer-style narration)
you may want to drop `MAX_DUR` to 5.0 and `MAX_CHARS` to 70 — too much
text in a short window becomes a wall. For very slow speech (slow
narration, ambient documentary), bumping `MAX_DUR` to 9.0 and dropping
`MIN_DUR` is fine.

## What the script does NOT do

- **No translation.** The script just chunks the transcript text as-is.
  Translation happens in the skill's later steps.
- **No word-level alignment with voiceover.txt.** Scribe v2's transcribed
  text occasionally differs from the original script (e.g. expanded
  numbers, slight word substitutions). The chunker uses transcript.json's
  text exactly. If the captions need to use the original script's casing
  and spelling, that's a manual post-edit.
- **No speaker labels or color cues.** Single-speaker channel; not
  relevant here.

## File output shape

The script writes plain SRT with a trailing blank line after each block
and UTF-8 encoding. Timestamps use the SRT convention `HH:MM:SS,mmm`
(comma before milliseconds, not a period).
