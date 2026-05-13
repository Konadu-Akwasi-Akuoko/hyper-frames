# Chapter stamping

How to derive `M:SS` chapter timestamps from `transcript.json` without
ever `Read`-ing it directly.

## The mandatory filter recipe

Per project `CLAUDE.md` lines 67–96, `transcript.json` has ~1500+ word
entries and floods context if read whole. Always slice via
`python3 -c` and only the matching slice lands in context.

### Recipe 1 — find the start time of a specific beat-opener phrase

Given the first 3–6 words of a beat's prose (e.g. "Let's start with
the Turing test"), find the global start time of the first matching
contiguous run:

```bash
python3 -c "
import json
t = json.load(open('<video-dir>/transcript.json'))
words = [w for w in t['words'] if w['type'] == 'word']

phrase = ['let\\'s', 'start', 'with', 'the', 'turing']  # lowercased
n = len(phrase)
def norm(s): return s.lower().strip('.,!?;:\"()')

for i in range(len(words) - n + 1):
    if all(norm(words[i+j]['text']) == phrase[j] for j in range(n)):
        s = words[i]['start']
        mm, ss = int(s // 60), int(s % 60)
        print(f'{mm}:{ss:02d}  (global {s:.2f}s)')
        break
else:
    print('NO_MATCH')
"
```

If `NO_MATCH` prints, the script and the voiceover diverged
(common — small reads-aloud edits during voiceover capture). Stop
and ask the user; do not invent a timestamp.

### Recipe 2 — list every word in a time window

Useful for double-checking chapter placement or finding a phrase you
half-remember:

```bash
python3 -c "
import json
t = json.load(open('<video-dir>/transcript.json'))
START, END = 120.0, 140.0  # seconds, global
for w in t['words']:
    if w['type'] == 'word' and START <= w['start'] <= END:
        print(f\"{w['start']:6.2f}  {w['text']}\")
"
```

## Year normalization — digits in script, words in transcript

Voiceover scripts say years out loud, but `script.md` often spells
them as digits. The Scribe v2 transcript captures what was *spoken*,
not what was *written*. Before matching, normalize digit-years in the
beat-opener to their spelled-out form.

| Digit-year | Spoken form (Scribe v2 will write this) |
|---|---|
| 1950 | nineteen fifty |
| 1997 | nineteen ninety-seven, nineteen ninety seven |
| 2001 | two thousand one, two thousand and one |
| 2003 | two thousand three, two thousand and three |
| 2010 | twenty ten |
| 2014 | twenty fourteen |
| 2017 | twenty seventeen |
| 2018 | twenty eighteen |
| 2023 | twenty twenty-three |
| 2024 | twenty twenty-four |

When the beat opener contains a digit-year, drop the year word from
the phrase you search on and anchor on the surrounding nouns instead
— e.g. for "In 1997, two teams independently invented…", search on
`["two", "teams", "independently", "invented"]`. This is more robust
than guessing whether Scribe wrote "nineteen ninety-seven" with or
without the hyphen.

Apostrophe handling: `let's` in `script.md` may be `let's` (U+2019,
typographic) or `let's` (U+0027, ASCII) in the transcript depending
on the TTS engine. The `norm()` strip in Recipe 1 catches the
trailing apostrophe-s issues — extend the strip set if needed:

```python
def norm(s): return s.lower().strip('.,!?;:"\'’()')
```

## Choosing the right anchor phrase

Pick the first 3–6 words of the beat's first prose sentence — long
enough to be unique, short enough to survive small voiceover edits.

Good anchors (specific nouns / verbs):
- `["in", "nineteen", "ninety", "seven", "two", "teams"]` (Beat 6
  Cycle 1)
- `["by", "twenty", "fourteen", "google", "was", "ready"]` (Beat 6
  Cycle 2)
- `["the", "yolo", "researchers", "exposed"]` (Beat 6 Cycle 3)

Bad anchors (too generic, will false-match):
- `["the", "next", "thing", "is"]`
- `["so", "in", "twenty"]`

If the first prose sentence opens with a generic stub, skip it and
anchor on the second sentence.

## Beat 1's `0:00` rule

YouTube requires the first chapter at `0:00` — even if Beat 1's first
spoken word starts at, say, 0.4s. Always write the first chapter
line as `0:00`. Do not round up. Do not search the transcript for
Beat 1; just write `0:00  <label>`.

## Verifying a derived timestamp

After deriving all chapter timestamps, run a quick sanity check —
they should be strictly increasing and the gaps should look
plausible (typically 20s–90s for a 5-min explainer, longer for
multi-cycle Beat 6 segments). If any gap is < 5s or > 180s, re-check
the anchor phrase for that beat; it likely matched the wrong run.
