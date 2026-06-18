# Transcript as timing truth

Animations must land on the spoken word, not on round numbers. A word-level
transcript (ElevenLabs Scribe v2-shaped) is the authoritative timing source.
Pull `start`/`end` for the exact word an animation punctuates and key entrances,
highlights, and cuts to those timestamps. Round numbers ("at 4.0s, fade in") are
a code smell — find the word and use its timestamp.

The transcript is supplied by the user's own pipeline (`transcribe-and-plan-cuts`
or the voiceover-* skills). Don't run `hyperframes-media transcribe` or assume
Whisper output — work from the `transcript.json` at the video folder root.

When a **talking-head source is present** (see `reference/talking-head.md`), the
transcript is derived from **that take's extracted audio** — not a separate TTS
or recording. Because picture and audio are **one recording**, each word's global
`start`/`end` is simultaneously the **audio anchor** *and* the exact **frame-seek
into the face layer**, with **zero offset** — the same timestamp keys the
narration and the picture.

This is the single biggest lever for the video feeling alive vs. merely synced.
It matters more, not less, as runtime grows.

## `transcript.json` schema (Scribe v2)

```ts
{
  audio_duration_secs?: number,          // present on most Scribe v2 outputs
  language_code: string,
  language_probability: number,
  text: string,                          // full concatenated text
  words: Array<                          // discriminated on `type`
    | {
        text: string,
        type: "word",
        start: number,                   // seconds, global to the audio
        end: number,                     // seconds, global to the audio
        speaker_id: string,
        logprob?: number,
      }
    | {
        text: string,
        type: "spacing",
        start: number,                   // seconds, global to the audio
        end: number,                     // seconds, global to the audio
      }
  >
}
```

`speaker_id` and `logprob` only appear on `"word"` rows; `"spacing"` rows are
bare timing markers between words. Discriminate on `type` when reading.

`start`/`end` are global audio timestamps. For scene-local time, subtract the
scene's start offset (the global timestamp of the scene's first word) — this is
the `chunk_start` you compute in Step C of the loop.

**CRITICAL — the face-video seek stays GLOBAL.** When a talking-head source is
present, the `#face-layer` host (track-index 8) spans the **whole runtime**, so
its `currentTime` is seeked with the **global** `start`, **zero offset**. Do
**not** apply the scene-local `global − data-start` subtraction to the face
seek — that math is *only* for per-scene tweens inside a chunk host. Using it on
the take lands every face reveal at the wrong frame (`reference/talking-head.md`).

## Do not `Read` `transcript.json` directly

It's ~1500+ word entries per video — reading it floods context with data you'll
mostly discard. Run a filtered `python3 -c` against it instead and only the
matching slice lands in context.

**Find every word in a time window** (seconds, global). Adjust START/END and the
scene start offset:

```bash
python3 -c "
import json
t = json.load(open('transcript.json'))
START, END, SCENE_START = 289.0, 305.0, 274.12
for w in t['words']:
    if w['type'] == 'word' and START <= w['start'] <= END:
        print(f\"{w['start']:.2f}  (local {w['start']-SCENE_START:.2f})  {w['text']}\")
"
```

**Locate a phrase** (to find a chunk's first/last word by text), printing the
timestamps you need:

```bash
python3 -c "
import json
t = json.load(open('transcript.json'))
PHRASE = 'built for mobility'
words = [w for w in t['words'] if w['type'] == 'word']
text = ' '.join(w['text'] for w in words).lower()
i = text.find(PHRASE.lower())
# walk the word list to the match; print each word's start/end
import itertools
acc = 0
for w in words:
    seg = w['text'].lower()
    if acc <= i < acc + len(seg) + 1 or PHRASE.lower().startswith(seg) and abs(acc-i) < 40:
        print(f\"{w['start']:.2f}-{w['end']:.2f}  {w['text']}\")
    acc += len(seg) + 1
"
```

(The phrase search above is a convenience; the time-window filter is the
workhorse — once you know roughly where a chunk sits, window it and read the
words.)

**Find the word at the frontier** (Step A resume point) — first word at or after
a time T:

```bash
python3 -c "
import json
t = json.load(open('transcript.json'))
T = 150.68
for w in t['words']:
    if w['type'] == 'word' and w['start'] >= T:
        print(f\"{w['start']:.2f}  {w['text']}\"); break
"
```

If the schema ever looks off, sanity-check with `head -c 500 transcript.json`
(cheap — no full read).

## narration-map — an optional planning aid

`tools/narration-map/` is an optional one-shot overview, **not** the source of
timing truth. Run it once per video when you want pause windows (gaps > 400ms),
scene-boundary candidates (pauses after `.!?`), and the top-N longest-duration
words (often the emphatic moments). For per-tween anchoring, the python filter
above is more direct.

When a **talking-head source is present**, these same pause windows (`>400ms`
gaps) and **sentence-boundary candidates** (after `.!?`) are the **source for
legal mode-transition points** — every FACE↔GRAPHICS↔PIP change must land on
one. **Sentence boundaries are the strong signal; the pause gaps secondary.**
See `reference/talking-head.md` for the mode grammar that consumes them.

```bash
# From inside the video folder:
uv run --project ../../tools/narration-map narration-map \
  transcript.json --anchors anchors.txt
```

Writes `narration-map.json` next to the transcript. See
`tools/narration-map/README.md` for the output shape and tunables.

## seo/research.json — a shared per-video artifact (FYI)

The `youtube-seo-research` skill generates `<video-dir>/seo/research.json` from
one topic phrase. It's consumed by `script-writer` and `thumbnail-and-title-generator`, not
by authoring directly — but it's the same per-video artifact, so know it exists.
Not your concern during composition authoring.
