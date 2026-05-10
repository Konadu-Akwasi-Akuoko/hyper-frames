---
name: voiceover-elevenlabs-v2
description: Turn an approved script.md into a voiceover (ElevenLabs Multilingual v2) and a word-level transcript (Scribe v2) in one run, with light annotation (ALL-CAPS anchors + SSML <break> tags) behind a hard checkpoint before any API credits are spent. Project default for YouTube videos — long-form stable, plain-prose match. Use when the user says "generate the voiceover", "voice this script", "tts the script", "make the audio", or after the script-writer skill's hand-off prompt. Outputs land at audio/voiceover.mp3 and transcript.json at the video folder root.
---

# voiceover-elevenlabs-v2

You are turning an approved `script.md` into both `audio/voiceover.mp3`
and `transcript.json` for a hyper-frames video, in one checkpointed
flow. The annotation step is **light**: strip BEAT comments, optionally
ALL-CAPS anchor terms, optionally insert SSML `<break>` tags at
structural pauses. v2 doesn't accept audio tags; expressiveness comes
from sentence rhythm + voice settings, not inline markup.

The deterministic work — calling Multilingual v2, calling Scribe v2 on
the rendered audio, mapping the response to the project's transcript
schema — lives in `tools/voiceover-elevenlabs-v2/`. This skill drives
that tool.

## What this skill does and doesn't do

**Does:**
- Locate the target video folder (`videos/<slug>-<date>/`).
- Read `script.md` (required) and `anchors.txt` (optional but strongly
  preferred — it's the source for ALL-CAPS candidates).
- Produce `voiceover.txt` with light v2 annotations per the taxonomy
  in §3.
- Run a hard checkpoint: show char count, cost estimate, annotation
  summary, list of additions. Wait for explicit `approve and generate`
  before any API call.
- Invoke `tools/voiceover-elevenlabs-v2/` to render audio + transcript.
- Confirm both outputs exist and report duration + word count.

**Does not:**
- Use audio tags. v2 doesn't support them; if the user pasted any in,
  strip them and surface the strips in the checkpoint.
- Vary voice settings per beat. Docs explicitly forbid this for related
  content.
- Auto-chunk over-limit scripts. Errors loudly with a "split into
  parts" message past 10,000 chars; user splits manually.
- Generate compositions, run `hyperframes preview`, or invoke
  `hyperframes render`. Same boundary as the v3 skill.

## Reference files

```
reference/
├── v2-quirks.md         engine-specific landmines + mitigations
└── voice-settings.md    the recommended stability/style/similarity recipe
```

Load `v2-quirks.md` once when the skill starts. Load `voice-settings.md`
if the user wants to tune.

## The flow

### Step 1 — Locate inputs

Same priority as the v3 skill: explicit path in user message → CWD match
→ ask user. Read `script.md` (required), `anchors.txt` (optional). Note
whether `<!-- BEAT n: <name> -->` markers are present.

### Step 2 — Annotate

Produce `<video-dir>/voiceover.txt` per §3. **Strip `<!-- BEAT -->` HTML
comments from the output**. The output is plain UTF-8 text, no markdown,
no headers. **Strip any v3 audio tags** (`[sighs]`, `[whispers]`,
etc.) the user may have pasted in; surface them in the checkpoint
additions list as "stripped".

Write `voiceover.txt` to disk before showing it to the user.

### Step 3 — Hard checkpoint

Show in one message:

1. **Char count** of `voiceover.txt`.
2. **Estimated cost**:
   - v2 TTS: `chars × 0.015` credits (≈ half v3's rate; verify on first
     real run).
   - Scribe v2: `(words / 170) / 60 × $0.40` USD.
3. **Annotation summary**: "Added N ALL-CAPS terms, M `<break>` tags,
   stripped X v3 audio tags."
4. **Numbered list of additions**: `Beat N · Line excerpt · Addition`.
5. **Char-limit warning** if `len(voiceover.txt) > 10_000`: tell the
   user the tool will error and offer to split `voiceover.txt`.

End with three explicit options:

- `approve and generate` — proceed to step 4.
- `edit` — user gives free-form feedback; revise `voiceover.txt` and
  re-show the checkpoint.
- `regenerate` — redo `voiceover.txt` from scratch with a different
  posture (e.g. fewer breaks). Re-show the checkpoint.

**Do not proceed until the user explicitly approves.**

### Step 4 — Generate

Invoke the tool:

```bash
uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/voiceover-elevenlabs-v2 \
  voiceover-elevenlabs-v2 <video-dir>/voiceover.txt \
  -o <video-dir>/audio/voiceover.mp3 \
  --output-transcript <video-dir>/transcript.json
```

Stream the output. On success, verify:
- `<video-dir>/audio/voiceover.mp3` exists and is non-empty.
- `<video-dir>/transcript.json` parses, has `audio_duration_secs > 0`.

Report: audio duration (from `transcript.json`), word count, file sizes.

### Step 5 — Done

Tell the user the next step:

> Audio + transcript are ready. Next:
> ```bash
> uv run --project ../../tools/narration-map narration-map \
>   transcript.json --anchors anchors.txt
> ```
> then start authoring compositions against `narration-map.json`.

This skill stops at `transcript.json`.

### Step 5b — Anchor reconciliation (if narration-map flags misses)

Scribe v2 normalizes numbers as words ("1950" → "nineteen fifty",
"2018" → "two thousand and eighteen") and may render ambiguous
proper-noun spellings differently across runs ("Houck"↔"Hauck"). The
first `narration-map` run will likely report some unmatched anchors.

When that happens:

1. Inspect `transcript.json` to see how Scribe spelled the missed
   phrase. (Grep the `words[].text` stream.)
2. Update the matching line in `anchors.txt` to the transcript
   spelling.
3. Re-run `narration-map`. Iterate until 100% matched.

**Do not regenerate the audio just to fix an anchor mismatch** —
the audio is correct; only the lookup table is stale. Audio regen
costs credits; anchor-sync is a free text edit.

## Annotation taxonomy

### 3.1 Allowed elements

| Element | Rule |
|---|---|
| ALL-CAPS on `anchors.txt` terms | Allowed; only on terms that appear in `anchors.txt`. No ad-hoc capitalization. If `anchors.txt` is missing, no ALL-CAPS at all. **If a single word in the phrase is a short proper noun (≤3 letters or initialism-shaped), demote that word to title case (`LUIS VON Ahn`, not `LUIS VON AHN`) — see v2-quirks §9.** |
| SSML `<break time="Xs"/>` | Allowed at hard structural pauses (before reframe, after thesis, between escalation cycles). Hard cap: ≤5 per 5-min script, ≤8 per 10-min. Durations: 0.3s, 0.5s, 0.8s, 1.5s, 2s, 3s. No values above 3s — v2's break ceiling. |
| Ellipses `…` | Allowed but use sparingly. v2 may treat `…` as periods more often than v3 does. Prefer `<break>` for deliberate pauses. |

### 3.2 Forbidden elements

| Element | Reason |
|---|---|
| Audio tags (`[sighs]`, `[whispers]`, `[curious]`, `[laughs]`, etc.) | v2 doesn't support them. Strip them and surface the strips in the checkpoint. |
| Per-beat voice setting variance | Docs: "identical parameter settings… across related content." |
| SSML `<break time="…"/>` over 3s | v2's break ceiling. Split into multiple breaks or rewrite the sentence. |

### 3.3 Per-beat rubric (loose — applies when `<!-- BEAT -->` markers exist)

| Beat | What gets added |
|---|---|
| 1 — Open | Plain. No breaks, no caps. |
| 2 — Subversion | Optional `<break time="0.5s"/>` after the "But" pivot. |
| 3 — Stakes | ALL-CAPS on named systems/numbers if in `anchors.txt`. |
| 4 — Thesis | ALL-CAPS on the three anchor terms. Optional `<break time="0.3s"/>` between the three parts. |
| 5 — Foundation | Plain. Optionally ALL-CAPS on the named concept being defined. |
| 6 — Escalation cycles | Optional `<break time="0.5s"/>` between naive→flaw→smarter→new flaw moves. ALL-CAPS on the smarter solution's name. |
| 7 — Synthesis | Plain. |
| 8 — Reframe | `<break time="0.8s"/>` after "The next time you…" for the gear-shift moment. |
| 9 — Closer | Optional `<break time="1.5s"/>` for deliberate slow-down. No caps — let the prose carry the weight. |

## Edge cases

- **No `<!-- BEAT -->` markers**: per-sentence beat-blind annotation, same hard caps. Warn the user.
- **No `anchors.txt`**: skip ALL-CAPS entirely. Annotation becomes `<break>` only. Warn the user.
- **Script over 10,000 chars**: tool errors. Tell the user to split `voiceover.txt` into parts and re-run; offer to do the split.
- **API key missing**: tool errors. Tell user to add `ELEVENLABS_API_KEY=…` to `.env` at repo root.
- **User wants to skip annotation entirely**: copy `script.md` → `voiceover.txt` (stripping `<!-- BEAT -->` comments and any v3 audio tags), show checkpoint, proceed.
- **User pasted v3 audio tags**: strip them in the annotation step, surface the strips in the checkpoint additions list as "stripped: `[sighs]` × 2, `[curious]` × 1".

## Done condition

You're done when:

- `<video-dir>/voiceover.txt` exists with the user-approved annotated text.
- `<video-dir>/audio/voiceover.mp3` exists and is non-empty.
- `<video-dir>/transcript.json` exists, parses, has `audio_duration_secs > 0`.
- The user has been told the next step is `narration-map`.
