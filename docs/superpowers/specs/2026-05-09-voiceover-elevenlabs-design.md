# voiceover-elevenlabs skill + tool — design

**Date:** 2026-05-09
**Status:** spec, ready for implementation plan
**Companion skill:** `script-writer` (this runs after the script is drafted)
**Replaces in workflow:** the `hyperframes-media tts` (Kokoro) path — for this project only. The `hyperframes-media` skill itself is not modified.

## 1. Purpose

Turn an approved `script.md` (from the `script-writer` skill) into a TTS-ready
voiceover and a word-level transcript that the rest of the project's pipeline
already consumes — `audio/voiceover.mp3` and `transcript.json` at the video
folder root, both produced from a single skill invocation.

The skill earns its keep at the **annotation** step: an LLM-driven, beat-aware
preprocessor that selectively inserts ElevenLabs v3 audio tags (`[sighs]`,
`[curious]`), pacing ellipses (`…`), and ALL-CAPS emphasis on named concepts
into a TTS-ready variant of the script before sending it to v3. The user
reviews the annotated text behind a hard checkpoint before any API credits are
spent.

The transcript is produced by a **second** ElevenLabs call (Scribe v2) on the
rendered audio — not from v3's native character alignment — because the
project's "transcript-as-timing-truth" invariant (`CLAUDE.md` §1) cannot
tolerate timing drift, and v3-derived alignment is unverified for this
project's videos.

## 2. Scope

**In scope:**
- Reading `script.md`, `anchors.txt`, and (when present) `<!-- BEAT n -->`
  comments from `videos/<slug>-<date>/`.
- LLM-driven beat-aware annotation: producing `voiceover.txt` with curated
  v3 audio tags, ellipses, and ALL-CAPS on anchor terms.
- Hard-checkpoint review: showing the user a diff of additions and a cost
  estimate before any API calls.
- Calling ElevenLabs v3 (`POST /v1/text-to-speech/{voice_id}`) to render the
  annotated text to MP3.
- Calling ElevenLabs Scribe v2 (`speech-to-text`) on the rendered audio to
  produce a word-level `transcript.json` matching the existing repo schema.
- Writing both outputs in one run, in the canonical locations.
- A `tools/voiceover-elevenlabs/` Python CLI that the skill drives and that
  remains usable standalone (e.g., a future skill, a one-off command, or a
  user who hand-edits `voiceover.txt`).

**Out of scope:**
- Modifying the existing `hyperframes-media` skill (Kokoro path stays
  untouched and parallel).
- Multi-voice / dialogue support. v3's `text-to-dialogue` endpoint is not
  used. Single-narrator only.
- Automatic chunking when a script exceeds v3's per-request character limit.
  Tool errors loudly with a clear "split into N parts" message; user splits
  manually. (5-min and 7-min scripts fit well within the limit; 10-min may
  not. Cross that bridge when a 10-min script lands.)
- Alternate-take generation ("give me three reads, I'll pick one"). Single
  take per run, overwrite on re-run.
- Using v3's native `with-timestamps` endpoint for transcript generation.
  Investigated and explicitly deferred — see §11.
- Generating `narration-map.json`. That remains a separate step the user
  runs after this skill completes.
- Generating compositions, running `hyperframes preview`, or invoking
  `hyperframes render`. Same boundary as `script-writer`.

## 3. Inputs and outputs

### Trigger conditions

The skill activates when the user asks to generate a voiceover for a
hyper-frames video — phrases like "generate the voiceover", "voice this
script", "tts the script", "make the audio for `videos/<slug>-<date>/`", or
when the `script-writer` skill's handoff prompt invokes it.

### Resolving the target video folder

Same priority order as the `thumbnail-creator` skill:

1. **Explicit path in the user's message.** If the user's message contains a
   path like `videos/<slug>-<date>/`, use that.
2. **CWD match.** If the CWD itself matches `**/videos/<slug>-<date>/`, use
   that.
3. **Ask.** If neither resolves, ask the user. List existing `videos/*`
   folders.

Resolved to an absolute path; used for every subsequent file read/write.

### Inputs (read by the skill at invocation)

Once `<video-dir>` is resolved:

- `<video-dir>/script.md` — required. The approved prose script. May contain
  `<!-- BEAT n: <name> -->` HTML comments delimiting beats.
- `<video-dir>/anchors.txt` — optional but strongly preferred. Source for
  ALL-CAPS candidates. One phrase per line, `#` comments and blank lines
  ignored (same format as the `tools/narration-map/` consumer).

### Outputs (written by the skill)

- `<video-dir>/voiceover.txt` — the LLM-annotated, user-approved TTS-ready
  variant of the script. Plain text, no HTML comments. Committed to git
  alongside `script.md` so the annotation history lives in version control.
- `<video-dir>/audio/voiceover.mp3` — rendered audio from v3. Committed to
  git (matches the existing repo convention; the inaugural video already
  commits its `audio/*.mp3`).
- `<video-dir>/transcript.json` — word-level transcript from Scribe v2 on
  the rendered audio. Schema matches the existing repo's transcript shape
  exactly (see §6.4). Committed to git.

The two MP3s already in `videos/why-text-is-hard-2026-05-07/audio/` are not
overwritten. This skill is opt-in for new videos; existing artifacts stay.

## 4. Architecture

Two pieces, clean split:

- **Tool** at `tools/voiceover-elevenlabs/` — uv-based Python package mirroring
  `tools/narration-map/`'s shape. Dumb and deterministic: takes a text file,
  calls the ElevenLabs APIs, writes audio + transcript. No LLM logic. Composable
  from any video folder via `uv run --project …`.
- **Skill** at `.claude/skills/voiceover-elevenlabs/` — the LLM-driven flow.
  Reads `script.md` + `anchors.txt`, produces `voiceover.txt`, runs the
  hard-checkpoint diff review, then invokes the tool.

The tool is callable on its own. The skill *uses* the tool but doesn't
*contain* it. This mirrors the `narration-map` pattern: the deterministic
work lives in `tools/`; the LLM intelligence lives in `.claude/skills/`.

### Data flow

```
script.md                        (input)
    │
    ▼
[skill: LLM annotation]          ──reads──▶  anchors.txt
    │                                       <!-- BEAT --> markers
    ▼
voiceover.txt                    (intermediate, committed)
    │
    ▼
[skill: hard-checkpoint diff]    ──asks──▶  user: approve / edit / regenerate
    │
    ▼ (on approve)
[tool: ElevenLabs v3 TTS]        ──API──▶  audio_bytes
    │
    ▼
audio/voiceover.mp3              (output)
    │
    ▼
[tool: ElevenLabs Scribe v2]     ──API──▶  word-level alignment
    │
    ▼
transcript.json                  (output)
```

## 5. Tool surface (CLI)

```bash
# From inside a video folder, with voiceover.txt next to script.md:
uv run --project /…/tools/voiceover-elevenlabs voiceover-elevenlabs voiceover.txt

# Flags (all optional):
#   -o, --output-audio PATH      default: audio/voiceover.mp3
#   --output-transcript PATH     default: transcript.json
#   --voice-id ID                default: UgBBYS2sOqTuMpoF3BR0
#   --model ID                   default: eleven_v3
#   --stability FLOAT            0.0–1.0, default 0.5 (Natural)
#   --similarity-boost FLOAT     0.0–1.0, default 0.75
#   --no-transcript              skip Scribe call; audio only
#   --dry-run                    print char count + estimated cost; no API call
#   --stdout                     write audio bytes to stdout (implies --no-transcript)
```

Behavior on existing files: **overwrite without prompting.** Per design
decision §Q3 — old MP3s are not preserved. If you want a prior take,
re-annotate and re-generate.

Exit codes:
- `0` success, both files written.
- `1` API error (network, auth, rate limit after retries).
- `2` validation error (input file missing, char count over v3 limit, schema
  mismatch from Scribe response).

## 6. Tool internals

Layout mirrors `tools/narration-map/`:

```
tools/voiceover-elevenlabs/
├── pyproject.toml
├── README.md
├── .python-version
├── .gitignore
└── src/
    └── voiceover_elevenlabs/
        ├── __init__.py     # exports synthesize, transcribe, generate
        ├── core.py         # high-level generate(text_path, audio_path, transcript_path)
        ├── tts.py          # ElevenLabs v3 TTS wrapper
        ├── scribe.py       # ElevenLabs Scribe v2 wrapper
        ├── transcript.py   # Scribe response → transcript.json schema
        └── cli.py          # argparse entry point
```

Dependencies: `elevenlabs` (official SDK), `python-dotenv`. That's it.

### 6.1 `tts.py` — TTS wrapper

```python
def synthesize(
    text: str,
    *,
    voice_id: str,
    model_id: str = "eleven_v3",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    output_format: str = "mp3_44100_128",
    api_key: str,
) -> bytes:
    """Render text to MP3 bytes via ElevenLabs v3. Raises on API error.
    Retries once on 429 with 5s backoff, again with 25s backoff."""
```

Endpoint: `client.text_to_speech.convert(...)` — the plain TTS variant, no
timestamps requested. v3's expressivity (audio tags, ellipses, ALL-CAPS) is
controlled via the `text` argument, not voice_settings.

Pre-check: if `len(text) > V3_CHAR_LIMIT` (we'll set this to 10_000 pending
verification), raise `ValueError` with a clear "split into N parts" message.

### 6.2 `scribe.py` — Scribe v2 wrapper

Mirrors the proven `transcribe.ts` from `learn-motion-canvas/skills/clean-audio/`,
ported to Python:

```python
def transcribe(
    audio_path: Path,
    *,
    api_key: str,
) -> ScribeResponse:
    """Transcribe an audio file with Scribe v2 at word granularity.
    Retries once on 429 with 5s backoff, again with 25s backoff.
    Raises on multichannel / webhook responses (unsupported here)."""
```

Calls `client.speech_to_text.convert(...)` with:
- `model_id="scribe_v2"`
- `timestamps_granularity="word"`
- `diarize=True`
- `tag_audio_events=True`

Defensive checks (matching the TS reference):
- Reject multichannel responses (`"transcripts" in raw`).
- Reject webhook responses (`"requestId" in raw`).
- Require `audioDurationSecs` to be present.

### 6.3 `transcript.py` — schema mapping

Maps the SDK's camelCase Scribe response into the project's snake_case
`transcript.json` shape (see §6.4). Coerces undefined per-word timestamps
to zero (matching the TS reference's defensive default — downstream Zod-style
validation would catch real schema breaks). Pure function; no I/O.

### 6.4 `transcript.json` schema (canonical)

The shape already used by `videos/why-text-is-hard-2026-05-07/transcript.json`
and consumed by `tools/narration-map/`:

```json
{
  "audio_duration_secs": 120.001,
  "language_code": "eng",
  "language_probability": 0.928,
  "text": "...",
  "words": [
    {
      "text": "You",
      "type": "word",
      "start": 0.18,
      "end": 0.26,
      "logprob": -7e-7,
      "speaker_id": "speaker_0"
    },
    {
      "text": " ",
      "type": "spacing",
      "start": 0.26,
      "end": 0.27
    }
  ]
}
```

`narration-map` reads `audio_duration_secs`, `language_code`, `words[].text`,
`words[].type`, `words[].start`, `words[].end`. It does not read `logprob`
or `language_probability` (those are preserved as a courtesy / for tooling
parity, not consumed).

### 6.5 `cli.py` — entry point

argparse-based. Loads `.env` from CWD upward via `python-dotenv`. Reads input
text file. Calls `core.generate(...)`. Prints char count + estimated cost
(v3: ~30 credits per 1k chars; Scribe: separate per-second pricing) on
`--dry-run`. On success, prints two `→ <path>` confirmation lines, one per
output file.

### 6.6 API key handling

`.env` at the repo root, loaded via `python-dotenv`:

```bash
ELEVENLABS_API_KEY=sk_...
```

Tool errors with a clear message if not set. `.env` is gitignored (verify
`.gitignore` covers it; add the line if it doesn't). The same key serves
both v3 and Scribe v2.

## 7. Skill flow

The skill at `.claude/skills/voiceover-elevenlabs/SKILL.md` runs the
LLM-driven side. Steps:

### Step 1 — Locate inputs

Resolve the target video folder per §3. Read `script.md` (required).
Read `anchors.txt` if present. Note whether `<!-- BEAT n -->` markers are
present in `script.md`; this drives the annotation posture.

### Step 2 — Annotate

Produce `voiceover.txt` per the taxonomy in §8. Strip `<!-- BEAT -->`
HTML comments from the output (they would be spoken otherwise). The annotation
follows the **conservative + beat-aware** posture (design decision §Q4):
selective tags, anchor-driven ALL-CAPS, ellipses at structural transitions.
If `<!-- BEAT -->` markers are absent, fall back to per-sentence
beat-blind annotation and warn the user.

Write `voiceover.txt` to the video folder root.

### Step 3 — Hard checkpoint

Show the user:

1. **Char count** of `voiceover.txt`.
2. **Estimated cost** in v3 credits (chars × 0.03) + Scribe per-second cost
   (estimated from char count assuming ~170 wpm). Convert to USD if their
   credit rate is known.
3. **Annotation summary**: "added N audio tags (`[sighs]` × 1, `[curious]`
   × 1), N ellipses, N capitalized concepts from anchors.txt".
4. **Diff view**: side-by-side or inline diff of additions, with tags / caps
   / ellipses highlighted. (Implementation detail: Claude Code's terminal
   doesn't render real diffs; we'll use a numbered list of additions.)
5. **Three options**: `approve and generate` / `edit` (user gives free-form
   feedback, I revise, re-show diff) / `regenerate` (start over with a
   different posture, e.g. more conservative or more liberal).

Do not proceed to step 4 until the user explicitly approves.

### Step 4 — Generate

Invoke the tool:

```bash
uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/voiceover-elevenlabs \
  voiceover-elevenlabs voiceover.txt
```

Stream stdout/stderr. On success, confirm:
- `audio/voiceover.mp3` exists and is non-empty.
- `transcript.json` exists and parses as JSON with the expected top-level
  keys.
- Report: audio duration (from transcript's `audio_duration_secs`), word
  count, file sizes.

### Step 5 — Done

Tell the user the next step is theirs:

> Audio + transcript are ready. Next:
> ```bash
> uv run --project ../../tools/narration-map narration-map \
>   transcript.json --anchors anchors.txt
> ```
> then start authoring compositions against `narration-map.json`.

## 8. Annotation taxonomy

This is the rubric the skill follows in step 2. Conservative posture,
beat-aware. Documented in the skill's `SKILL.md` so it's loaded into context
every run.

### 8.1 Per-beat rubric

| Beat | What gets added |
|---|---|
| 1 — Open | Light. Maybe one `…` after the opening clause for breathing room. No tags. |
| 2 — Subversion | Natural home for one `[sighs]` or `[curious]` on the "but" pivot. Single tag, max. |
| 3 — Stakes | ALL-CAPS on named systems/numbers if they appear in `anchors.txt`. |
| 4 — Thesis | ALL-CAPS on the three anchor terms in the three-part list. `…` between the three parts if present. |
| 5 — Foundation | Plain. Optionally ALL-CAPS on the named concept being defined. |
| 6 — Escalation cycles | `…` between naive→flaw→smarter→new flaw moves within each cycle. ALL-CAPS on the smarter solution's name (anchor). |
| 7 — Synthesis | If the script personifies a system, allow `[thoughtful]` once. Otherwise plain. |
| 8 — Reframe | `…` after "The next time you…" for the gear-shift moment. |
| 9 — Closer | `…` for deliberate slow-down. No tags — let the prose carry the weight. |

### 8.2 Hard caps (built into the skill)

These exist to prevent the theatrical failure mode:

- **≤ 3 audio tags total in a 5-minute script. ≤ 5 in a 10-minute script.**
- **ALL-CAPS only on terms that appear in `anchors.txt`.** No ad-hoc
  capitalization. (If `anchors.txt` is missing, no ALL-CAPS at all — the
  fallback is purely punctuation-driven.)
- **`…` is unbounded** but used only at structural transitions (between
  three-part list items, between escalation moves, before reframes), never
  mid-clause.
- **No `[laughs]`, `[applause]`, `[gunshot]`, `[explosion]`, accent tags,
  `[sings]`** — these are character-voice / SFX tags that don't fit
  narrative essay style.

### 8.3 Beat-blind fallback

If `<!-- BEAT n -->` markers are absent (user wrote `script.md` by hand or
heavily edited it), the skill falls back to per-sentence annotation with the
same hard caps and warns the user. Posture stays conservative.

## 9. script-writer handoff edit

Single-line edit in `.claude/skills/script-writer/SKILL.md`. Current
`Done condition` (line 207):

> Tell the user the next step is theirs: generate the TTS audio with
> `npx hyperframes-media tts` (or whichever TTS the project standardizes on),
> drop it into `audio/`, then run the user's transcript pipeline to produce
> `transcript.json`, then run `narration-map` with `anchors.txt`. This skill
> stops at `script.md`.

Replaces with:

> Once `script.md`, `outline.md`, and `anchors.txt` are written and approved,
> ask the user: *"Script is locked. Want me to generate the voiceover with
> ElevenLabs v3 now? (invokes the `voiceover-elevenlabs` skill)"* If yes,
> hand off to that skill — it produces both `audio/voiceover.mp3` and
> `transcript.json` in one run. If no, tell the user the next step is theirs:
> ```bash
> uv run --project ../../tools/voiceover-elevenlabs voiceover-elevenlabs voiceover.txt
> ```
> then run `narration-map` with `anchors.txt`. This skill stops at `script.md`.

No other edits to `script-writer`. The 9-beat arc, the drafting rules, the
TTS-gotcha learning loop, the done condition — all unchanged.

## 10. Cost handling

### Per-run cost model

For a 5-minute (~900-word, ~5,000-char) script:

- **v3 TTS:** ~5,000 × 0.03 = **~150 credits**.
- **Scribe v2:** ~5 minutes × 0.40 USD/hour = **~$0.03**.

The hard checkpoint in step 3 surfaces both numbers before any API call.
Re-runs (regenerating after a tweak) re-charge in full — no caching.

### `.env` and key safety

`.env` at the repo root:

```
ELEVENLABS_API_KEY=sk_...
```

Verified-or-added in `.gitignore`. Tool fails with a clear error if missing.
The same key serves both endpoints.

## 11. Out of scope (with rationale)

### v3-derived word alignment via `with-timestamps`

Investigated. v3 supports `POST /v1/text-to-speech/{voice_id}/with-timestamps`
and returns character-level alignment that we could post-process to
word-level. This would collapse the two API calls into one and eliminate
Scribe cost.

**Deferred** because:

1. The project's "transcript-as-timing-truth" invariant (`CLAUDE.md` §1)
   cannot tolerate timing drift. Animations land on the spoken word; off by
   one second breaks the video.
2. v3-derived alignment is unverified for this project's content. The
   marketing claim of "precise per-word timing" hasn't been measured by us.
3. Audio tags (`[sighs]`) and text normalization create alignment edge cases
   that need testing — particularly how the post-spoken word's start
   timestamp behaves around an inserted breath/sigh.
4. Scribe v2 produces transcripts in a format already proven to work with
   `narration-map` and the project's existing pipeline.
5. The cost saving is small (~$0.03 per video) and not worth the accuracy
   risk on the first videos through the pipeline.

**Future work** (see §12): once we have 2–3 videos through the
Scribe-on-rendered-audio path, run an offline experiment that produces both
transcripts for the same audio and diffs them. If TTS-derived word starts
are within a tight tolerance (target: <30 ms p99 word-start error vs.
Scribe), promote it to default behind a feature flag, then drop the Scribe
call.

### Other

- **Modifying `hyperframes-media`** — not touched. The Kokoro path stays
  parallel for any non-v3 use case.
- **`text-to-dialogue` (multi-voice)** — single-narrator only. If a future
  video needs dialogue, build a separate skill.
- **Automatic chunking** — YAGNI until a 10-min script actually exceeds
  v3's per-request limit. Tool errors loudly with a split message.
- **Alternate takes** — single take per run. Re-run for a different read.
- **Versioned filenames / archive** — overwrite by default per §Q3.
- **Auto-generating `narration-map.json`** — separate tool, separate step.

## 12. Future work

- **TTS-derived alignment experiment** (see §11). Side-by-side diff vs.
  Scribe on the same audio across 2–3 videos.
- **Promote `voiceover-elevenlabs` to a registry block** if a second project
  ever needs the same skill+tool combo. Today, single-project use only.
- **`--use-tts-alignment` flag** as the experimental on-ramp before
  switching defaults.
- **TTS-gotcha learning loop**, mirroring `script-writer`'s
  `reference/tts-gotchas.md` pattern. If a v3 audio tag turns out to fight
  the chosen voice (`UgBBYS2sOqTuMpoF3BR0`) in a specific way, append the
  failure mode + mitigation to the skill's reference.

## 13. Open questions for implementation plan

These are settled-but-need-verification, not architectural:

1. **v3 per-request character limit.** Docs don't state a number. Verify via
   the API reference or empirical test before locking the pre-check
   threshold (`tts.py` raises `ValueError` if exceeded). Working assumption:
   10,000 characters.
2. **v3 `voice_settings` shape.** v3 may use a slightly different settings
   object than v2 (the docs hint Stability is the master dial; other fields
   may be ignored). Verify with the SDK's typed interface.
3. **Exact SDK method name** for v3 plain TTS. Working assumption:
   `client.text_to_speech.convert(...)`. Confirm against the current
   `elevenlabs` Python SDK release.
4. **Scribe v2 cost per second** — verify before printing cost estimates;
   the working figure of ~$0.40/hour is approximate.

These don't change the design; they're checks the implementation plan
performs once before writing code.
