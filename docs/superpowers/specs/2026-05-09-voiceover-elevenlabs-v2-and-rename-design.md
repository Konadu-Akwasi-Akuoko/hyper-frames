# voiceover-elevenlabs-v2 + rename + tts-gotchas pointer fix — design

**Date:** 2026-05-09
**Status:** spec, ready for implementation plan
**Companion skills:** `script-writer` (upstream — drafts the script), `voiceover-elevenlabs-v3` (sibling — the renamed existing skill, kept opt-in)
**Replaces in workflow:** `voiceover-elevenlabs` becomes the *opt-in* path under its new name; `voiceover-elevenlabs-v2` becomes the new project default for YouTube videos.

## 1. Purpose

Three coordinated changes:

1. **Rename** the existing `voiceover-elevenlabs` skill + tool to `voiceover-elevenlabs-v3` so the engine version is explicit in every reference. The implementation is unchanged; only names move.
2. **Build a new `voiceover-elevenlabs-v2` skill + tool** that drives ElevenLabs Multilingual v2 + Scribe v2. v2 is the docs-stated "most stable on long-form generations" model, fits the project's plain-prose house style, and lifts the per-request ceiling from ~5 min (v3) to ~10 min (v2). It becomes the project default; v3 is reserved for videos that genuinely need inline audio tags for per-beat emotional shifts.
3. **Fix an aspirational pointer** in `script-writer/reference/tts-gotchas.md` that referenced a project-level pronunciation dictionary that does not exist. Replace with current-reality guidance and a "future" note.

## 2. Scope

**In scope:**
- Rename the `tools/voiceover-elevenlabs/` folder, its Python package (`voiceover_elevenlabs` → `voiceover_elevenlabs_v3`), its CLI script entry, its README, and the `.claude/skills/voiceover-elevenlabs/` skill folder — all to `…-v3`.
- Build `tools/voiceover-elevenlabs-v2/` (new Python package) — single-shot v2 TTS + Scribe v2 transcript, mirroring the v3 tool's CLI shape with v2-appropriate defaults and a SSML-break-aware annotation contract.
- Build `.claude/skills/voiceover-elevenlabs-v2/SKILL.md` with `reference/v2-quirks.md` and `reference/voice-settings.md`.
- Update `script-writer/SKILL.md` Step 6 hand-off to default to v2 and offer v3 as `with v3` opt-in.
- Update `CLAUDE.md` to declare v2 the project default.
- Update `tts-gotchas.md` pronunciation-dictionary paragraph to match reality + add a "future" note.
- Add one-line top-of-file pointers to historical spec/plan docs that reference the old name, so future readers can navigate to this doc.

**Out of scope:**
- Building project-level pronunciation dictionary support in either tool (deferred — add when the same respelling repeats across two or more videos).
- Automatic chunking + request stitching for v2 scripts that exceed the 10,000-char limit. The tool errors loudly with a "split into parts" message, same pattern v3 already uses for its 5,000-char limit. Add chunking only when a real 10+ min script lands.
- Multi-voice / dialogue support. Single-narrator only, same as v3.
- Alternate-take generation. Single take per run, overwrite on re-run.
- Modifying the `hyperframes-media` (Kokoro) path. Stays parallel and untouched.
- A shared core library between v2 and v3 tools. The two tools intentionally duplicate ~5 small files (Scribe pass, transcript schema mapping, client init). Refactor to a shared lib only if drift becomes painful; YAGNI for now.
- Updating the existing v3 spec (`2026-05-09-voiceover-elevenlabs-design.md`) beyond a one-line top-of-file pointer.

## 3. Why v2 is the new default

From the canonical models page (https://elevenlabs.io/docs/overview/models#text-to-speech):

| Property | Eleven v3 | Multilingual v2 |
|---|---|---|
| Per-request char limit | 5,000 (~5 min) | 10,000 (~10 min) |
| Stated strength | "Most expressive" | "Most stable on long-form generations" |
| Audio tags (`[sighs]`, `[whispers]`) | Supported | **Not supported** |
| SSML `<break time="Xs"/>` | Not supported | **Supported** |
| Phoneme tags | Not supported | Not supported (use respelling or alias dictionary) |
| Style slider | n/a | 0–1, default 0 |
| Status | Alpha (Jan 2026) | Production |
| Professional Voice Clones | Partial (alpha) | Fully supported |
| Cost per 1k chars | ~30 credits | ~15 credits (verify on first run) |

For this project's videos — long-form (5–10 min), single-narrator, technical didactic content, plain-prose house style with restraint baked in — v2 wins on:

1. **Char budget.** A 5-min script (~5,400 chars) fits comfortably; a 7-min script (~7,200 chars) fits; a 10-min script (~10,200 chars) is borderline. v3 forces manual splitting at any script ≥5 min.
2. **Production maturity.** v2 is "first take usually fine"; v3 alpha "requires more prompt engineering, results vary between generations."
3. **Style match.** The 9-beat iceberg arc (script-writer house style) restrains theatrics. v3's headline feature is inline emotional control via tags — exactly the dimension the writing style suppresses. v2's contextual emotional model + the prose's own sentence rhythm carries the load.
4. **Cost.** Roughly half v3's credits per char. Lower iteration cost.

v3 stays a real option for videos that genuinely benefit from per-beat audio tags — character voice, dialogue scenes, anything where `[whispers]` or `[laughs softly]` materially changes the read.

## 4. Pointer fix in `tts-gotchas.md`

Change the trailing paragraph of the "Phonetic respelling — escape hatch for proper nouns" section from:

```
For genuinely durable cases (recurring product names, recurring proper
nouns), promote the entry to the pronunciation dictionary in
`voiceover-elevenlabs` instead of carrying a respelling in every script.
```

to:

```
For genuinely durable cases (recurring product names, recurring proper
nouns), respell inline and leave a `<!-- TTS: Argon-2 -->` comment so
the next reader knows it's intentional.

> Future: ElevenLabs supports project-level pronunciation dictionaries
> (alias rules for v2; phoneme tags for some v1/Flash models; max 3
> locators per request via `pronunciation_dictionary_locators`). Not
> wired into our tools yet — add when the same respelling shows up
> across two or more videos.
```

No other content changes in `tts-gotchas.md`.

## 5. Rename surface area

Eleven files reference the string `voiceover-elevenlabs` (no version suffix). The rename touches all of them.

### 5.1 Folders renamed

| Old | New |
|---|---|
| `tools/voiceover-elevenlabs/` | `tools/voiceover-elevenlabs-v3/` |
| `tools/voiceover-elevenlabs/src/voiceover_elevenlabs/` | `tools/voiceover-elevenlabs-v3/src/voiceover_elevenlabs_v3/` |
| `.claude/skills/voiceover-elevenlabs/` | `.claude/skills/voiceover-elevenlabs-v3/` |

The internal Python package is renamed too (`voiceover_elevenlabs` → `voiceover_elevenlabs_v3`). Mismatched names (binary `voiceover-elevenlabs-v3` calling package `voiceover_elevenlabs`) age badly; rename is cheap now.

### 5.2 Files modified

| File | Change |
|---|---|
| `tools/voiceover-elevenlabs-v3/pyproject.toml` | `name = "voiceover-elevenlabs-v3"`; `[project.scripts]` entry `voiceover-elevenlabs-v3 = "voiceover_elevenlabs_v3.cli:main"`; `[tool.pyright]` extraPaths still `["src"]` |
| `tools/voiceover-elevenlabs-v3/src/voiceover_elevenlabs_v3/*.py` | All `from voiceover_elevenlabs.X import` → `from voiceover_elevenlabs_v3.X import` |
| `tools/voiceover-elevenlabs-v3/tests/*.py` | Same import updates |
| `tools/voiceover-elevenlabs-v3/README.md` | Title, code blocks, `uv run --project …` paths |
| `.claude/skills/voiceover-elevenlabs-v3/SKILL.md` | `name:` frontmatter; description (mention "renamed from voiceover-elevenlabs"); Step 4 tool invocation path |
| `.claude/skills/script-writer/SKILL.md` | Step 6 hand-off prompt → see §8 |
| `CLAUDE.md` | "Authoring workflow" voiceover paragraph → see §8 |
| `docs/superpowers/specs/2026-05-09-voiceover-elevenlabs-design.md` | Add one-line top-of-file pointer: *"Tool/skill was renamed to `voiceover-elevenlabs-v3` on 2026-05-09. See `2026-05-09-voiceover-elevenlabs-v2-and-rename-design.md`."* |
| `docs/superpowers/plans/2026-05-09-voiceover-elevenlabs.md` | Same one-line pointer |
| `docs/superpowers/plans/2026-05-09-youtube-seo-research.md` | Update any inline mentions (no path renames inside docs — text only) |
| `docs/superpowers/specs/2026-05-09-pipeline-kanban-design.md` | Update any inline mentions (text only) |

### 5.3 Files NOT modified by the rename

- `script-writer/reference/tts-gotchas.md` — the pointer change in §4 supersedes the rename concern (the pointer no longer references `voiceover-elevenlabs` by name).
- The existing v3 spec/plan content beyond their one-line top pointers — historical docs are frozen.

## 6. The v2 tool — `tools/voiceover-elevenlabs-v2/`

Built from scratch. Mirrors the renamed v3 tool's file layout, dependencies (`elevenlabs>=1.0.0`, `python-dotenv>=1.0.0`), test layout (`test_cli.py`, `test_core.py`, `test_scribe.py`, `test_transcript.py`, `test_tts.py`), and `[tool.pyright]` config.

### 6.1 Package layout

```
tools/voiceover-elevenlabs-v2/
├── pyproject.toml          name = "voiceover-elevenlabs-v2"; package = voiceover_elevenlabs_v2
├── README.md
├── .gitignore
├── .python-version
├── src/voiceover_elevenlabs_v2/
│   ├── __init__.py
│   ├── cli.py              argparse, dry-run, char-limit guardrail, generate() dispatch
│   ├── core.py             generate(): orchestrates TTS → save MP3 → Scribe → save transcript
│   ├── tts.py              ElevenLabs v2 client wrapper
│   ├── scribe.py           Scribe v2 client wrapper (identical to v3 tool's)
│   └── transcript.py       Scribe response → project schema mapping (identical to v3 tool's)
└── tests/
    ├── conftest.py
    ├── test_cli.py
    ├── test_core.py
    ├── test_scribe.py
    ├── test_transcript.py
    └── test_tts.py
```

### 6.2 CLI surface

```
voiceover-elevenlabs-v2 INPUT_PATH [options]
```

Required: `INPUT_PATH` — path to `voiceover.txt`.

Flags:

| Flag | Default | Notes |
|---|---|---|
| `-o`, `--output-audio PATH` | `audio/voiceover.mp3` | MP3 destination, relative to CWD |
| `--output-transcript PATH` | `transcript.json` | Transcript destination |
| `--voice-id ID` | `UgBBYS2sOqTuMpoF3BR0` | Same default voice as v3 tool (consistency across renders) |
| `--model ID` | `eleven_multilingual_v2` | Locked model — flag exists for symmetry only |
| `--stability FLOAT` | `0.4` | v2 long-form sweet spot per docs (0.35–0.4) |
| `--similarity-boost FLOAT` | `0.75` | Same as v3 default |
| `--style FLOAT` | `0.35` | v2-only param; docs recommend 0.3–0.5 for natural expression |
| `--use-speaker-boost / --no-use-speaker-boost` | `true` | v2-only param |
| `--language-code STR` | `en` | Locks generation language; mitigates the "language switching mid-generation" gotcha (v2-quirk #1) |
| `--no-transcript` | off | Skip Scribe call; produce audio only |
| `--dry-run` | off | Print char count + cost estimate; no API call |

### 6.3 Char-limit guardrail

```python
V2_CHAR_LIMIT = 10_000

if len(text) > V2_CHAR_LIMIT:
    print(
        f"Input is {len(text)} chars; v2's per-request limit is {V2_CHAR_LIMIT}.\n"
        f"Split voiceover.txt into parts and run again. Chunked + stitched mode\n"
        f"is not yet implemented (see design doc §2 'Out of scope').",
        file=sys.stderr,
    )
    return 2
```

Same loud-error-no-fallback pattern v3 uses.

### 6.4 Cost estimator

```python
V2_CREDITS_PER_1K_CHARS = 15  # verify against actual billing on first real run
SCRIBE_USD_PER_HOUR = 0.40
WORDS_PER_MINUTE = 170
```

Output format identical to v3's dry-run text, swap `v3 TTS:` for `v2 TTS:`. The `15` figure is approximate; the implementation plan should include a "verify on first real render" step.

### 6.5 What `core.generate()` does

1. Read `text` from `INPUT_PATH`.
2. Build `VoiceSettings(stability, similarity_boost, style, use_speaker_boost)`.
3. Call `client.text_to_speech.convert(text=text, voice_id=…, model_id="eleven_multilingual_v2", language_code="en", voice_settings=…, output_format="mp3_44100_128")`.
4. Write the returned audio bytes to `output_audio`.
5. If `generate_transcript`: call Scribe v2 on the rendered audio (identical wrapper to v3 tool), map to project schema, write to `output_transcript`.
6. Return.

No chunking. No request stitching. No `previous_text` / `next_text` / `previous_request_ids` plumbing in MVP.

## 7. The v2 skill — `.claude/skills/voiceover-elevenlabs-v2/`

Mirrors the v3 skill's flow shape (Step 1 locate → Step 2 annotate → Step 3 hard checkpoint → Step 4 generate → Step 5 done) so users moving between v2 and v3 see the same five-step pattern. All differences from v3 are captured below.

### 7.1 SKILL.md frontmatter

```
---
name: voiceover-elevenlabs-v2
description: Turn an approved script.md into a voiceover (ElevenLabs Multilingual v2) and a word-level transcript (Scribe v2) in one run, with light annotation (ALL-CAPS anchors + SSML <break> tags) behind a hard checkpoint before any API credits are spent. Project default for YouTube videos — long-form stable, plain-prose match. Use when the user says "generate the voiceover", "voice this script", "tts the script", "make the audio", or after the script-writer skill's hand-off prompt. Outputs land at audio/voiceover.mp3 and transcript.json at the video folder root.
---
```

### 7.2 Step 2 annotation taxonomy

Differences from v3's taxonomy:

| Element | v3 | v2 |
|---|---|---|
| Audio tags (`[sighs]`, `[curious]`, `[thoughtful]`, `[exhales]`) | Allowed, hard cap of 3 per 5-min script | **Forbidden** — v2 doesn't support inline tags |
| ALL-CAPS on `anchors.txt` terms | Allowed; only on anchor terms | **Same rule** |
| Ellipses `…` at structural transitions | Allowed | **Allowed but use sparingly** — v2 may treat ellipses as periods more often than v3 does. Prefer `<break>` for deliberate pauses |
| SSML `<break time="0.5s"/>` … `<break time="3s"/>` | Forbidden (v3 doesn't support) | **Allowed — v2's load-bearing pacing primitive.** Use at hard structural pauses (before reframe, after thesis, between escalation cycles). Hard cap: ≤5 per 5-min script, ≤8 per 10-min |
| Per-beat voice setting variance | Forbidden | **Forbidden** — docs: "identical parameter settings… across related content" |
| `<!-- BEAT n -->` HTML comments | Stripped from output | **Stripped from output** (same as v3) |

### 7.3 Hard caps (no exceptions)

- ≤ 5 SSML `<break>` tags in a 5-min script. ≤ 8 in a 10-min script.
- `<break>` durations: 0.3s, 0.5s, 0.8s, 1.5s, 2s, 3s. No values above 3s — v2's break ceiling.
- ALL-CAPS only on terms that appear in `anchors.txt`. No ad-hoc capitalization. If `anchors.txt` is missing, no ALL-CAPS at all.
- No audio tags. None. If the writer pasted in v3 tags by accident, strip them and warn the user in the checkpoint.

### 7.4 Step 3 hard checkpoint

Same shape as v3's: char count, cost estimate, annotation summary, numbered list of additions, three options (`approve and generate` / `edit` / `regenerate`).

Cost estimate line: `v2 TTS: ~{credits:.0f} credits (≈ half v3's rate)`. Scribe line unchanged.

### 7.5 Step 4 tool invocation

```bash
uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/voiceover-elevenlabs-v2 \
  voiceover-elevenlabs-v2 <video-dir>/voiceover.txt \
  -o <video-dir>/audio/voiceover.mp3 \
  --output-transcript <video-dir>/transcript.json
```

### 7.6 Step 5 done message

Same as v3: report duration, word count, point at the next step (`narration-map`).

### 7.7 Edge cases (added or differing from v3)

- **Script over 10,000 chars:** tool errors. Tell the user to split `voiceover.txt` into parts and re-run; offer to do the split.
- **`<!-- BEAT -->` markers missing:** fall back to per-sentence beat-blind annotation, same hard caps. Warn the user.
- **`anchors.txt` missing:** skip ALL-CAPS entirely. Annotation becomes punctuation + `<break>` only. Warn the user.
- **API key missing:** tool errors. Tell user to add `ELEVENLABS_API_KEY=…` to `.env` at repo root.
- **User wants to skip annotation entirely:** copy `script.md` → `voiceover.txt` (stripping `<!-- BEAT -->` comments), show checkpoint, proceed.
- **User pasted v3 tags into script.md:** strip them in the annotation step, surface the strips in the checkpoint additions list.

## 8. Reference files

The v3 skill's taxonomy lives entirely in its SKILL.md. v2 needs more — the engine has more sharp edges that need explaining, not just listing.

### 8.1 `reference/v2-quirks.md`

Eight engine-specific landmines + mitigations:

1. **Language switching mid-generation.** v2 sometimes switches accent or language on a single proper noun if the model thinks it's in another language ("paella", "naïve", "café"). Mitigation: pass `language_code="en"` on every call (wired into the tool default), or respell phonetically.
2. **No phoneme tags.** v2 doesn't accept `<phoneme>`. Pronunciation control is via inline respelling (per `tts-gotchas.md`) or alias-based pronunciation dictionary (deferred).
3. **SSML break tag bounds.** Up to ~3 seconds per `<break>`. Longer pauses → split or rewrite.
4. **Style slider trap.** Style above ~0.6 produces erratic emphasis on long-form. Cap at 0.5 by convention; the tool default of 0.35 is safe.
5. **Stability paradox.** Stability above ~0.7 produces *more* monotone delivery, not "more stable." Misleading name. 0.4 is the long-form sweet spot per docs.
6. **`use_speaker_boost` × similarity stacking.** Both push toward the cloned voice. Stacking high values amplifies source recording flaws. Keep similarity at 0.75 and speaker_boost on; don't push similarity higher.
7. **Concurrency limits per plan.** From the docs models page: Free=2, Starter=3, Creator=5, Pro=10 simultaneous v2 requests. Single-shot + single-user means we never hit this. Documented for completeness.
8. **PVC vs IVC.** Professional Voice Clones fully supported on v2 (unlike v3 alpha). If the user upgrades from IVC to PVC, no skill change needed.

### 8.2 `reference/voice-settings.md`

Documents the chosen `(stability=0.4, similarity_boost=0.75, style=0.35, use_speaker_boost=true)` tuple as the project default with one-paragraph rationale per knob, plus the procedure for tuning if the user wants to experiment (test on a 30-second slice, A/B against the default, never tune per-beat — docs explicitly forbid per-chunk variance within "related content").

## 9. CLAUDE.md and script-writer hand-off updates

### 9.1 `CLAUDE.md` — voiceover paragraph

Current:

> For voiceover generation in this project, use `voiceover-elevenlabs` (ElevenLabs v3 + Scribe v2), not `hyperframes-media tts` (Kokoro). The Kokoro path stays parallel and untouched for any non-v3 use case.

Replacement:

> For voiceover generation in this project, default to `voiceover-elevenlabs-v2` (ElevenLabs Multilingual v2 + Scribe v2). It's the long-form stability champion (per the official models page) and matches the project's plain-prose house style. Use `voiceover-elevenlabs-v3` only when a video genuinely needs inline audio tags for per-beat emotional shifts. The `hyperframes-media tts` (Kokoro) path stays parallel and untouched for any non-ElevenLabs use case.

### 9.2 `script-writer/SKILL.md` — Step 6 hand-off

Current:

> Once `script.md`, `outline.md`, and `anchors.txt` are written and approved, ask the user: *"Script is locked. Want me to generate the voiceover with ElevenLabs v3 now? (invokes the `voiceover-elevenlabs` skill)"* If yes, hand off to that skill — it produces both `audio/voiceover.mp3` and `transcript.json` in one run.

Replacement:

> Once `script.md`, `outline.md`, and `anchors.txt` are written and approved, ask the user: *"Script is locked. Want me to generate the voiceover with ElevenLabs v2 now? (invokes the `voiceover-elevenlabs-v2` skill — long-form stable, our project default. Pass `with v3` if you need the audio-tag path instead.)"* If the user replies affirmatively, hand off to `voiceover-elevenlabs-v2`. If they reply `with v3`, hand off to `voiceover-elevenlabs-v3` instead. Both skills produce `audio/voiceover.mp3` and `transcript.json` in one run.

## 10. Testing strategy

The v2 tool's tests mirror the v3 tool's structure. Each module has a unit test file with mocked SDK clients.

- `test_cli.py` — argparse, dry-run output, char-limit guardrail (test the over-10k error path), env-var error path.
- `test_core.py` — generate() orchestration with mocked tts/scribe/transcript modules. Verify `language_code="en"` is passed.
- `test_tts.py` — ElevenLabs client wrapper. Verify VoiceSettings shape (stability, similarity_boost, style, use_speaker_boost). Verify `model_id="eleven_multilingual_v2"`.
- `test_scribe.py` — Scribe v2 client wrapper. Same shape as v3 tool's test.
- `test_transcript.py` — schema mapping. Same shape as v3 tool's test, including defensive cases (missing `audio_duration_secs`, undefined per-word timestamps).

Real API calls are not made in tests. A README "first real run" checklist verifies (a) credit estimator accuracy, (b) audio quality on a short test script, (c) language_code lock prevents accent drift on a deliberate trigger word ("paella" or similar).

## 11. Migration / sequencing

The implementation order matters because the rename touches files the new v2 work also touches.

1. **Rename pass first.** Move folders, rename Python package, update pyproject + imports + tests, update v3 SKILL.md self-references, run v3 tool tests to confirm green. CLAUDE.md and script-writer hand-off are NOT updated in this pass — they would temporarily reference a v2 skill that doesn't exist yet.
2. **tts-gotchas pointer fix** can land with the rename pass — small, independent.
3. **Build v2 tool** — scaffold with `uv init`, copy structure from renamed v3 tool, adapt defaults, run tests.
4. **Build v2 skill** — write SKILL.md and the two reference files. No tests; skill validation is by use.
5. **CLAUDE.md + script-writer hand-off updates** — done now that both skills exist by their final names. Single commit so the docs are consistent with reality.
6. **First real render** — pick an existing `videos/<slug>-<date>/` with a `script.md` (the inaugural `videos/why-text-is-hard-2026-05-07/` is the natural target). Run the new v2 skill end-to-end. Verify cost estimator. Verify Scribe transcript shape matches the project schema.

After step 6, the existing v3 path remains fully usable via `voiceover-elevenlabs-v3` for the rare video that needs it.

## 12. Open questions

- **Cost-estimator constant.** `15 credits per 1k chars` for v2 is approximate from third-party sources; verify against ElevenLabs billing on the first real run and adjust if needed.
- **Default voice id.** Both tools use the same `UgBBYS2sOqTuMpoF3BR0`. If the user later picks a different voice optimized for v2's contextual emotional model, change the v2 tool's default (no design implication).
- **Whether to add a `--language-code` flag at all** vs hardcode `"en"`. Flag is cheaper to add now than to retrofit; keep it.

## 13. Done condition

The combined work is complete when:

- `tools/voiceover-elevenlabs-v3/` exists with passing tests; `tools/voiceover-elevenlabs/` no longer exists.
- `.claude/skills/voiceover-elevenlabs-v3/` exists; `.claude/skills/voiceover-elevenlabs/` no longer exists.
- `tools/voiceover-elevenlabs-v2/` exists with passing tests.
- `.claude/skills/voiceover-elevenlabs-v2/SKILL.md`, `reference/v2-quirks.md`, and `reference/voice-settings.md` exist.
- `CLAUDE.md` declares v2 the project default.
- `script-writer/SKILL.md` Step 6 hand-off offers v2 by default with `with v3` opt-in.
- `tts-gotchas.md` pronunciation-dictionary paragraph reflects current reality.
- Historical specs/plans referencing the old name carry one-line top-of-file pointers to this design doc.
- One real render has been performed end-to-end with the v2 skill against an existing video folder, verifying the cost estimator and the Scribe transcript shape.
