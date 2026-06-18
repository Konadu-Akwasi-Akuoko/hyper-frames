---
name: transcribe-and-plan-cuts
description: Take a raw voice recording at `videos/<slug>/audio/raw.mp3`, transcribe it with ElevenLabs Scribe v2, dispatch the audio-cut-decider sub-agent to plan first-pass cuts, and write both `transcript.json` and `cuts.json` so the user can preview and refine in `tools/audio-editor`. Use when the user says "transcribe my recording", "plan cuts for this audio", "prep this recording for the editor", or hands you a path to a raw recording and asks to clean it up. This skill does NOT render the final `audio/voiceover.mp3` — saving cuts in the editor only writes `cuts.json`; rendering (apply cuts → cut audio) is a one-line `cut-video --mode audio` pass it hands off. The inverse flow (re-transcribing an already-rendered `voiceover.mp3`) is documented under "After the cuts are applied".
---

# transcribe-and-plan-cuts

You're turning a raw self-recording into the two files the `tools/audio-editor`
web app needs (`transcript.json` and `cuts.json`) so the user can scrub the
waveform, drag the proposed regions, and finalize their cuts visually.

Four pieces do the work, and this skill orchestrates them before handing off
to the editor:

1. The deterministic Scribe v2 call lives in `tools/transcribe-elevenlabs/`.
2. The cut planning (which word-spans to remove, and why) lives in the
   `audio-cut-decider` sub-agent at `.claude/agents/audio-cut-decider.md`.
3. Duplicate-take recovery (catching lines spoken twice near-verbatim) lives in
   `tools/dup-detect/` — deterministic transcript string-matching, not the
   agent. The agent *detects* repeats reliably but its judgment on them
   (rhetorical vs re-take, and which take to keep) varies run to run, so this
   step adds any identical-repeat cut the agent missed and picks the keeper by
   delivery tightness. Flagged for human verification.
4. Boundary precision (snapping each cut onto the true acoustic silence around
   the span) lives in `tools/cut-snap/` — deterministic waveform DSP, not the
   agent. The agent decides *which* words to cut; cut-snap decides the *exact*
   edges. They are split deliberately: an LLM can't reliably place sub-word
   boundaries from a transcript, but it's excellent at the editorial judgment.

## What this skill does and doesn't do

**Does:**
- Locate the raw recording (`videos/<slug>-<date>/audio/raw.mp3`).
- Run a hard cost checkpoint before any Scribe API call (audio duration,
  estimated USD, files about to be written). Wait for explicit approval.
- Invoke `tools/transcribe-elevenlabs/` to produce `transcript.json` next
  to the recording.
- Dispatch the `audio-cut-decider` sub-agent to produce `cuts.json` in the
  schema the audio-editor expects.
- Run `tools/dup-detect` to recover any duplicate take the agent missed
  (deterministic transcript matching) and merge it into `cuts.json`, flagged.
- Run `tools/cut-snap` to refine every cut boundary onto the true acoustic
  silence around its span (waveform RMS analysis + breath padding).
- Tell the user the exact `http://localhost:5173/#/edit/<slug>` URL to open.

**Does not:**
- Render `audio/voiceover.mp3` (i.e., apply the cuts to produce the final
  audio). The editor's **Save cuts** only PUTs `cuts.json` — it does not
  render. Rendering is a one-line `cut-video` pass over the kept
  (inverse-of-cuts) segments, leaving `raw.mp3` untouched:
  `cut-video <cuts.json> audio/raw.mp3 --mode audio -o audio/voiceover.mp3`.
  See "After the cuts are applied" below for the re-transcribe that follows
  a render. (For a VIDEO talking-head source the cuts land on the picture
  first — follow the prep order in `video-director`'s
  `reference/talking-head.md` instead of cutting the audio standalone.)
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

### Step 5 — Recover missed duplicate takes (dup-detect)

The agent reliably *notices* repeated takes, but its judgment on them is unstable
run to run — it may classify the same near-verbatim repeat as rhetorical and keep
both, or cut the wrong copy. `tools/dup-detect` makes that recall deterministic:
it scans the transcript for textually-identical word-runs spoken twice within a
short window, keeps the tighter-delivered take (defaulting to the later one — the
completed attempt — unless the earlier is clearly tighter), and merges any cut
the agent missed into `cuts.json`. Cuts it adds are flagged
`duplicate_or_rhetorical` so the user verifies them in the editor. Pure
transcript analysis — no audio, no model, zero variance. It only touches
identical repeats; non-verbatim re-takes stay the agent's job. Run it before
cut-snap so boundary refinement covers the recovered cuts too.

```bash
uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/dup-detect \
  dup-detect <video-dir>/transcript.json \
  --cuts <video-dir>/cuts.json \
  -o <video-dir>/cuts.json
```

It prints each duplicate it found, marking it `add` (merged in) or `skip
(already cut)` (the agent already covered that span), and re-numbers all ids.
Re-run the Step 4 invariant check on the merged `cuts.json`. If dup-detect finds
nothing, `cuts.json` is unchanged — that's fine, proceed.

### Step 6 — Refine boundaries onto silence (cut-snap)

The agent brackets each cut at word edges; `tools/cut-snap` then refines every
boundary onto the true acoustic silence around the span — it reads the waveform,
finds the real word edges (more accurate than the transcript's labels), and
leaves a natural ~0.3s breath on each side of the splice so nothing is clipped
and no dead air is left. This is deterministic DSP, not LLM guesswork; it
overwrites `cuts.json` in place. Requires `ffmpeg`.

```bash
uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/cut-snap \
  cut-snap <video-dir>/transcript.json <video-dir>/cuts.json <video-dir>/audio/raw.mp3 \
  -o <video-dir>/cuts.json
```

It prints a `before → after` table per cut — surface the total Δ so the user
sees the refinement happened. Then re-run the Step 4 invariant check on the
refined `cuts.json` (cut-snap sorts and de-overlaps, but verify it still parses
and passes). If cut-snap errors (e.g. `ffmpeg` missing, or the audio/transcript
timelines don't match), report it and hand off the agent's unrefined `cuts.json`
rather than blocking — the user can still refine by ear in the editor.

### Step 7 — Hand off to the audio editor

Report the count of proposed cuts + total removable seconds. Then point the
user at the editor:

> Open the audio editor:
> ```
> http://localhost:5173/#/edit/<slug>-<date>
> ```
> Scrub the proposed cuts, drag region edges to refine, delete any you
> disagree with, add any I missed. Click **Save cuts** when you're done —
> the editor PUTs the updated `cuts.json` back.

This skill stops here. Once the user has saved their cuts, render the cleaned
`audio/voiceover.mp3` from `audio/raw.mp3` + approved cuts with one `cut-video`
pass (it applies the inverse-of-cuts keep-windows, leaving `raw.mp3` untouched):

```bash
uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/cut-video \
  cut-video <video-dir>/cuts.json <video-dir>/audio/raw.mp3 \
  --mode audio -o <video-dir>/audio/voiceover.mp3
```

For a VIDEO (talking-head) source, don't cut the audio standalone — the cuts
land on the picture first so the mouth stays synced. Follow the prep order in
`video-director`'s `reference/talking-head.md` instead.

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
3. **Skip Steps 4–7 entirely.** The cuts are already applied — do not run the
   `audio-cut-decider`, `dup-detect`, or `cut-snap`, and never overwrite the
   finalized `cuts.json`.

## Edge cases

- **`audio/raw.mp3` missing** — stop, tell the user the expected location.
  Do not transcribe whatever else is in `audio/` (e.g. `voiceover.mp3`) —
  that's the cleaned output, not the source. The one exception is the
  deliberate post-render re-transcribe (see "After the cuts are applied").
- **`ELEVENLABS_API_KEY` missing** — the tool will error. Tell the user to
  add `ELEVENLABS_API_KEY=…` to `.env` at the repo root.
- **`transcript.json` already exists** — surface this in the checkpoint;
  proceeding overwrites it. If the user wants to skip the transcribe step
  (transcript already good), skip Steps 2–3 and start at **Step 4** (dispatch
  the agent), then continue through **Step 5** (dup-detect) and **Step 6**
  (cut-snap) exactly as normal — the post-agent refinement still applies, so
  don't stop after the agent.
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
