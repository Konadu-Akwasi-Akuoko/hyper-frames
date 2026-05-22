---
name: transcribe-and-plan-cuts
description: Take a raw voice recording at `videos/<slug>/audio/raw.mp3`, transcribe it with ElevenLabs Scribe v2, dispatch the audio-cut-decider sub-agent to plan first-pass cuts, and write both `transcript.json` and `cuts.json` so the user can preview and refine in `tools/audio-editor`. Use when the user says "transcribe my recording", "plan cuts for this audio", "prep this recording for the editor", or hands you a path to a raw recording and asks to clean it up. This skill does NOT render the final `audio/voiceover.mp3` — saving cuts in the editor only writes `cuts.json`; rendering (apply cuts → cut audio) is a separate manual ffmpeg step. The inverse flow (re-transcribing an already-rendered `voiceover.mp3`) is documented under "After the cuts are applied".
---

# transcribe-and-plan-cuts

You're turning a raw self-recording into the two files the `tools/audio-editor`
web app needs (`transcript.json` and `cuts.json`) so the user can scrub the
waveform, drag the proposed regions, and finalize their cuts visually.

The deterministic Scribe v2 call lives in `tools/transcribe-elevenlabs/`.
The cut planning lives in the `audio-cut-decider` sub-agent at
`.claude/agents/audio-cut-decider.md`. This skill orchestrates the two and
hands off to the editor.

## What this skill does and doesn't do

**Does:**
- Locate the raw recording (`videos/<slug>-<date>/audio/raw.mp3`).
- Run a hard cost checkpoint before any Scribe API call (audio duration,
  estimated USD, files about to be written). Wait for explicit approval.
- Invoke `tools/transcribe-elevenlabs/` to produce `transcript.json` next
  to the recording.
- Dispatch the `audio-cut-decider` sub-agent to produce `cuts.json` in the
  schema the audio-editor expects.
- Tell the user the exact `http://localhost:5173/#/edit/<slug>` URL to open.

**Does not:**
- Render `audio/voiceover.mp3` (i.e., apply the cuts to produce the final
  audio). The editor's **Save cuts** only PUTs `cuts.json` — it does not
  render. Rendering is a separate manual step today: ffmpeg `atrim` + `concat`
  of the kept (inverse-of-cuts) segments from `raw.mp3`, leaving `raw.mp3`
  untouched. See "After the cuts are applied" below for the re-transcribe that
  follows a render.
- Start, restart, or kill `bun dev` for the audio-editor. The user already
  has it running on `:5173` / `:3001` (per `tools/audio-editor/CLAUDE.md`).
- Touch the raw recording. `audio/raw.mp3` is the source of truth and is
  never modified.
- Read `transcript.json` directly after writing it (per repo CLAUDE.md —
  ~1500+ entries flood context). Verify with a `jq`/`python3 -c` summary
  instead.

## The flow

### Step 1 — Locate the recording

Priority order:

1. **Explicit path in user message** — if the user gave you a path
   (e.g. `videos/my-talk-2026-05-19/audio/raw.mp3`), use it.
2. **CWD match** — if the current working directory is a video folder
   (`videos/<slug>-<date>/`) and `audio/raw.mp3` exists, use it.
3. **Ask the user** — list the video folders that have `audio/raw.mp3` and
   ask which one.

Confirm the resolved path exists. If it doesn't, stop and tell the user
the expected location is `<video-dir>/audio/raw.mp3`.

Extract `<slug>` from the folder name (everything up to but excluding the
trailing `-YYYY-MM-DD` is fine, but the editor URL needs the **full
folder name** including the date suffix — that's what the editor's
`resolveSlug` expects).

### Step 2 — Hard cost checkpoint

Run the tool in dry-run mode to get the duration + cost estimate without
spending any credits:

```bash
uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/transcribe-elevenlabs \
  transcribe-elevenlabs <video-dir>/audio/raw.mp3 --dry-run
```

Then show in one message:

1. **Audio file** — path, size (MB), duration (mm:ss).
2. **Cost estimate** — `~$X.XX for N minutes of Scribe v2`.
3. **Files about to be written:**
   - `<video-dir>/transcript.json`
   - `<video-dir>/cuts.json`
4. **End with two options:**
   - `approve and transcribe` — proceed to step 3.
   - `cancel` — stop, no API call made.

**Do not proceed until the user explicitly approves.** If `transcript.json`
or `cuts.json` already exist at the target paths, surface that in the
checkpoint (they'll be overwritten).

### Step 3 — Transcribe

Invoke the tool for real:

```bash
uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/transcribe-elevenlabs \
  transcribe-elevenlabs <video-dir>/audio/raw.mp3 \
  -o <video-dir>/transcript.json
```

Stream the output. On success, verify `<video-dir>/transcript.json` exists.
Confirm `audio_duration_secs > 0` and the word count without reading the
full file:

```bash
python3 -c "
import json
t = json.load(open('<video-dir>/transcript.json'))
words = sum(1 for w in t['words'] if w['type'] == 'word')
events = sum(1 for w in t['words'] if w['type'] == 'audio_event')
print(f\"{t['audio_duration_secs']:.2f}s · {words} words · {events} audio events\")
"
```

### Step 4 — Dispatch the audio-cut-decider sub-agent

Spawn the sub-agent via the Agent tool with
`subagent_type: "audio-cut-decider"`. The prompt must be self-contained
(the agent starts cold). Hand it two absolute paths and nothing else:

> Read the Scribe v2 transcript at `<absolute-path>/transcript.json`,
> apply your cut policy, and write `cuts.json` to
> `<absolute-path>/cuts.json` in the `tools/audio-editor` schema you
> already know. Confirm back with one line: the path written and the
> cut count.

When the agent returns, verify `<video-dir>/cuts.json` exists and parses.
Spot-check invariants without reading the whole file:

```bash
python3 -c "
import json
c = json.load(open('<video-dir>/cuts.json'))
assert c['version'] == 1
ids = [x['id'] for x in c['cuts']]
assert len(set(ids)) == len(ids), 'duplicate ids'
prev_end = 0.0
for x in c['cuts']:
    assert x['end'] > x['start'], f'bad bounds: {x}'
    assert x['start'] >= prev_end, f'overlap or unsorted at {x[\"id\"]}'
    prev_end = x['end']
total = sum(x['end'] - x['start'] for x in c['cuts'])
print(f\"{len(c['cuts'])} cuts · {total:.2f}s removable\")
"
```

If the script fails, tell the user the agent produced invalid cuts and stop.
Don't try to silently fix the file.

### Step 5 — Hand off to the audio editor

Report the count of proposed cuts + total removable seconds. Then point the
user at the editor:

> Open the audio editor:
> ```
> http://localhost:5173/#/edit/<slug>-<date>
> ```
> Scrub the proposed cuts, drag region edges to refine, delete any you
> disagree with, add any I missed. Click **Save cuts** when you're done —
> the editor PUTs the updated `cuts.json` back.

This skill stops here. Rendering the cleaned `audio/voiceover.mp3` from
`audio/raw.mp3` + approved cuts is a separate concern.

## After the cuts are applied — re-transcribing the cut audio

This is the **inverse** of the main flow, for when `voiceover.mp3` has already
been rendered (cuts applied) and you need timing truth that matches the *cut*
audio the composition actually uses.

Once `voiceover.mp3` is rendered, the original `transcript.json` is stale: its
timestamps run on the raw timeline (full length), but the narration is now
shorter with the cut regions gone. Animations key off the transcript
(transcript-as-timing-truth), so it must match `voiceover.mp3`. To refresh it:

1. **Back up first** — copy `transcript.json` → `transcript.raw.json`. This
   preserves the raw-aligned transcript: `cuts.json` timestamps reference *that*
   timeline, and the audio-editor prefers `transcript.raw.json` (+ `raw.mp3`)
   so cuts stay re-editable after a render.
2. **Transcribe `voiceover.mp3`** — run Steps 2–3 but point the tool at
   `audio/voiceover.mp3` and write `transcript.json`. This is the **one
   sanctioned exception** to "do not transcribe `voiceover.mp3`" (see Edge
   cases). Sanity-check that the new `audio_duration_secs` is shorter than the
   raw, by roughly the total removable seconds from `cuts.json`.
3. **Skip Steps 4–5 entirely.** The cuts are already applied — do not run the
   `audio-cut-decider`, and never overwrite the finalized `cuts.json`.

## Edge cases

- **`audio/raw.mp3` missing** — stop, tell the user the expected location.
  Do not transcribe whatever else is in `audio/` (e.g. `voiceover.mp3`) —
  that's the cleaned output, not the source. The one exception is the
  deliberate post-render re-transcribe (see "After the cuts are applied").
- **`ELEVENLABS_API_KEY` missing** — the tool will error. Tell the user to
  add `ELEVENLABS_API_KEY=…` to `.env` at the repo root.
- **`transcript.json` already exists** — surface this in the checkpoint;
  proceeding overwrites it. If the user wants to skip the transcribe step
  (transcript already good), they should run the agent directly via the
  Agent tool with `subagent_type: "audio-cut-decider"`.
- **`cuts.json` already exists** — same: surface in the checkpoint, overwrite
  on approval. The editor saves cuts back to this same file, so re-running
  the skill on an already-edited video clobbers the user's manual work.
  Warn loudly.
- **`bun dev` not running for the editor** — the hand-off URL won't load.
  Don't start it yourself; tell the user to run `bun dev` from
  `tools/audio-editor/`.
- **Recording over ~2 hours** — Scribe v2 is fine with long-form, but
  cost-check the user (a 2-hour recording is ~$0.80). They'll see this in
  the checkpoint.
- **Recording not at `audio/raw.mp3`** — if the user has it elsewhere (e.g.
  `audio/take2.wav`), the tool accepts any path; just pass the explicit
  path in step 3. The convention is `audio/raw.mp3`, but it's not enforced.

## Done condition

You're done when:

- `<video-dir>/transcript.json` exists, parses, has `audio_duration_secs > 0`.
- `<video-dir>/cuts.json` exists, parses, satisfies all invariants in the
  agent's contract (version, unique ids, sorted, non-overlapping, bounded).
- The user has been told the exact editor URL to open.
