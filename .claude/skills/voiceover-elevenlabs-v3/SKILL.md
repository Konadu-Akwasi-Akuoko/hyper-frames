---
name: voiceover-elevenlabs-v3
description: Turn an approved script.md into a voiceover (ElevenLabs v3) and a word-level transcript (Scribe v2) in one run, with an LLM-driven beat-aware annotation step (curated audio tags, ellipses, anchor-driven ALL-CAPS) behind a hard checkpoint before any API credits are spent. Use when the user explicitly requests v3 (passes `with v3` to the script-writer hand-off) or when a video genuinely needs inline audio tags for per-beat emotional shifts. The project default for YouTube videos is `voiceover-elevenlabs-v2` — invoke that unless v3's tag-driven expressiveness is specifically wanted. Outputs land at audio/voiceover.mp3 and transcript.json at the video folder root.
---

# voiceover-elevenlabs-v3

You are turning an approved `script.md` into both `audio/voiceover.mp3`
and `transcript.json` for a hyper-frames video, in one checkpointed flow.
The intelligence is in the **annotation** step: a beat-aware preprocessor
that selectively inserts v3 audio tags, pacing ellipses, and ALL-CAPS
emphasis to make the rendered audio land for YouTube viewers without
fighting the project's plain-prose house style.

The deterministic work — calling ElevenLabs v3, calling Scribe v2 on the
rendered audio, mapping the response to the project's transcript schema —
lives in `tools/voiceover-elevenlabs-v3/`. This skill drives that tool.

## What this skill does and doesn't do

**Does:**
- Locate the target video folder (`videos/<slug>-<date>/`) from the user's
  message, CWD, or by asking.
- Read `script.md` (required) and `anchors.txt` (optional but strongly
  preferred — it's the source for ALL-CAPS candidates).
- Produce `voiceover.txt` with curated v3 annotations per the taxonomy in §3.
- Run a hard checkpoint: show char count, cost estimate, annotation summary,
  and a list of additions. Wait for explicit `approve and generate` /
  `edit` / `regenerate` before any API call.
- Invoke `tools/voiceover-elevenlabs-v3/` to render audio and transcript.
- Confirm both outputs exist and report duration + word count.

**Does not:**
- Generate compositions, run `hyperframes preview`, or invoke
  `hyperframes render`. Same boundary as `script-writer`.
- Generate `narration-map.json`. The user runs that separately after this
  skill completes (the skill prints the next-step command).
- Touch `hyperframes-media`. The Kokoro path stays parallel.
- Use multi-voice / `text-to-dialogue`. Single-narrator only.
- Auto-chunk over-limit scripts. Errors loudly with a "split into parts"
  message; user splits manually.

## The flow

### Step 1 — Locate inputs

Resolve the target video folder, in this priority order:

1. Explicit path in the user's message (e.g. `videos/<slug>-<date>/`).
2. Current working directory if it matches `**/videos/<slug>-<date>/`.
3. Ask the user. List existing `videos/*` folders to make the choice
   concrete.

Once resolved (call it `<video-dir>`), read:

- `<video-dir>/script.md` — required. If missing, error and tell the user
  to run `script-writer` first.
- `<video-dir>/anchors.txt` — optional. Parse it as one phrase per line,
  ignore `#` comments and blank lines.

Note whether `<!-- BEAT n: <name> -->` markers are present in `script.md`.
Their presence drives the annotation posture in step 2.

### Step 2 — Annotate

Produce `<video-dir>/voiceover.txt` per the taxonomy in §3. **Strip
`<!-- BEAT n -->` HTML comments from the output** — they would be spoken
otherwise. The output is plain UTF-8 text, no markdown, no headers.

Posture: **conservative + beat-aware**. Specific rules:

- Use the `<!-- BEAT -->` markers to know which beat each sentence belongs to.
- Apply the per-beat rubric in §3.1.
- Honor the hard caps in §3.2 — no exceptions.
- If there are no `<!-- BEAT -->` markers, fall back to per-sentence
  beat-blind annotation with the same hard caps. Warn the user.

Write `voiceover.txt` to disk before showing it to the user — they may want
to inspect the file directly.

### Step 3 — Hard checkpoint

Show the user, in one message:

1. **Char count** of `voiceover.txt`.
2. **Estimated cost**:
   - v3 TTS: `chars × 0.030` credits (v3 rate).
   - Scribe v2: `(words / 170) / 60 × $0.40` USD.
3. **Annotation summary**: e.g. "Added 2 audio tags ([sighs] × 1, [curious]
   × 1), 5 ellipses (3 between escalation moves, 2 in beat 4 thesis), 7
   ALL-CAPS terms from anchors.txt".
4. **Numbered list of additions** (since real diff rendering isn't reliable
   in this terminal). Format: `Beat N · Line excerpt · Addition`.

End with three explicit options:

- `approve and generate` — proceed to step 4.
- `edit` — user gives free-form feedback; you revise `voiceover.txt` and
  re-show the checkpoint.
- `regenerate` — you redo `voiceover.txt` from scratch with a different
  posture (e.g. more conservative). Re-show the checkpoint.

**Do not proceed to step 4 until the user explicitly approves.** Cost is
real (~150 credits per 5-minute video).

### Step 4 — Generate

Invoke the tool:

```bash
uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/voiceover-elevenlabs-v3 \
  voiceover-elevenlabs-v3 <video-dir>/voiceover.txt \
  -o <video-dir>/audio/voiceover.mp3 \
  --output-transcript <video-dir>/transcript.json
```

Stream the output. On success, verify:

- `<video-dir>/audio/voiceover.mp3` exists and is non-empty.
- `<video-dir>/transcript.json` exists, parses as JSON, has the expected
  top-level keys (`audio_duration_secs`, `language_code`, `words`).

Report to the user: audio duration (from `transcript.json`'s
`audio_duration_secs`), word count, file sizes.

### Step 5 — Done

Tell the user the next step is theirs:

> Audio + transcript are ready. Next:
> ```bash
> uv run --project ../../tools/narration-map narration-map \
>   transcript.json --anchors anchors.txt
> ```
> then start authoring compositions against `narration-map.json`.

This skill stops at `transcript.json`.

### Step 5b — Anchor reconciliation (if narration-map flags misses)

Scribe v2 normalizes numbers as words ("1950" → "nineteen fifty")
and may render ambiguous proper-noun spellings differently across
runs. When `narration-map` reports unmatched anchors, inspect
`transcript.json` for the actual spelling and update `anchors.txt`
— don't regenerate audio just to fix a lookup mismatch.

## Annotation taxonomy

### 3.1 Per-beat rubric

| Beat | What gets added |
|---|---|
| 1 — Open | Light. Maybe one `…` after the opening clause for breathing room. No tags. |
| 2 — Subversion | Natural home for one `[sighs]` or `[curious]` on the "but" pivot. Single tag, max. |
| 3 — Stakes | ALL-CAPS on named systems/numbers if they appear in `anchors.txt`. |
| 4 — Thesis | ALL-CAPS on the three anchor terms in the three-part list. `…` between the three parts if present. |
| 5 — Foundation | Plain. Optionally ALL-CAPS on the named concept being defined (if in `anchors.txt`). |
| 6 — Escalation cycles | `…` between naive→flaw→smarter→new flaw moves within each cycle. ALL-CAPS on the smarter solution's name (anchor). |
| 7 — Synthesis | If the script personifies a system, allow `[thoughtful]` once. Otherwise plain. |
| 8 — Reframe | `…` after "The next time you…" for the gear-shift moment. |
| 9 — Closer | `…` for deliberate slow-down. No tags — let the prose carry the weight. |

### 3.2 Hard caps (no exceptions)

- **≤ 3 audio tags total in a 5-minute script. ≤ 5 in a 10-minute script.**
- **ALL-CAPS only on terms that appear in `anchors.txt`.** No ad-hoc
  capitalization. If `anchors.txt` is missing, no ALL-CAPS at all.
  **If a single word in the phrase is a short proper noun (≤3 letters
  or initialism-shaped), demote that word to title case (`LUIS VON Ahn`,
  not `LUIS VON AHN`) — short ALL-CAPS tokens get read
  letter-by-letter. For phonetic respells, look up the IPA on Wikipedia
  first; English orthography is unreliable (`AHN`/`AWN`/`OHN` map to
  different vowels).**
- **`…` is unbounded** but used only at structural transitions (between
  three-part list items, between escalation moves, before reframes), never
  mid-clause.
- **Banned tags**: `[laughs]`, `[applause]`, `[gunshot]`, `[explosion]`,
  `[strong X accent]`, `[sings]`, `[fart]`, `[woo]`. These don't fit
  narrative essay style.
- **Allowed tags** (use sparingly, max one per beat where applicable):
  `[sighs]`, `[curious]`, `[thoughtful]`, `[exhales]`. That's the whole
  list; resist the temptation to expand it.

## Edge cases

- **No `<!-- BEAT -->` markers in `script.md`**: fall back to per-sentence
  beat-blind annotation, same hard caps. Warn the user that `anchors.txt`
  ALL-CAPS still works but beat-specific tag placement won't.
- **No `anchors.txt`**: skip ALL-CAPS entirely. Annotation becomes
  punctuation + sparse tags only. Warn the user.
- **Script over v3 char limit**: the tool errors at the API call. Tell the
  user to split `voiceover.txt` into parts and re-run; offer to do the
  split.
- **API key missing**: the tool errors with a clear message. Tell the user
  to add `ELEVENLABS_API_KEY=...` to `.env` at the repo root.
- **User wants to skip annotation entirely**: respect that. Copy `script.md`
  → `voiceover.txt` (stripping `<!-- BEAT -->` comments), show the
  checkpoint, proceed.

## Done condition

You're done when:

- `<video-dir>/voiceover.txt` exists with the user-approved annotated text.
- `<video-dir>/audio/voiceover.mp3` exists and is non-empty.
- `<video-dir>/transcript.json` exists, parses, and has `audio_duration_secs > 0`.
- The user has been told the next step is `narration-map`.
