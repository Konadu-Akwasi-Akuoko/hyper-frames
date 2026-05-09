# voiceover-elevenlabs-v2 + rename + tts-gotchas pointer fix — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename the existing `voiceover-elevenlabs` skill+tool to `…-v3`, build a new `voiceover-elevenlabs-v2` skill+tool as the project default for YouTube videos, and fix an aspirational pointer in `script-writer/reference/tts-gotchas.md`.

**Architecture:** Two parallel skills (`voiceover-elevenlabs-v2` default, `voiceover-elevenlabs-v3` opt-in), each backed by its own Python tool under `tools/`. The v2 tool is single-shot (10,000-char ceiling, errors loudly past that — chunking is deferred). v2's annotation taxonomy uses ALL-CAPS on anchors + SSML `<break>` tags (no audio tags — v2 doesn't support them). Both tools share no code in MVP; refactor to a shared library only if drift becomes painful.

**Tech Stack:** Python 3.12 + `uv`, `elevenlabs>=1.0.0` SDK, `python-dotenv`, `pytest` + `pytest-mock`. Scribe v2 transcription is identical between v2 and v3 tools (the same `scribe.py` + `transcript.py` module shape). Spec: `docs/superpowers/specs/2026-05-09-voiceover-elevenlabs-v2-and-rename-design.md`.

---

## File structure

### Phase 1: Rename

| Action | Path |
|---|---|
| Move folder | `tools/voiceover-elevenlabs/` → `tools/voiceover-elevenlabs-v3/` |
| Move folder | `tools/voiceover-elevenlabs-v3/src/voiceover_elevenlabs/` → `tools/voiceover-elevenlabs-v3/src/voiceover_elevenlabs_v3/` |
| Move folder | `.claude/skills/voiceover-elevenlabs/` → `.claude/skills/voiceover-elevenlabs-v3/` |
| Modify | `tools/voiceover-elevenlabs-v3/pyproject.toml` (name, script entry) |
| Modify | All `.py` files in `tools/voiceover-elevenlabs-v3/src/` and `tools/voiceover-elevenlabs-v3/tests/` (imports) |
| Modify | `tools/voiceover-elevenlabs-v3/README.md` (title, paths) |
| Modify | `.claude/skills/voiceover-elevenlabs-v3/SKILL.md` (frontmatter + body) |
| Add header pointer | `docs/superpowers/specs/2026-05-09-voiceover-elevenlabs-design.md` |
| Add header pointer | `docs/superpowers/plans/2026-05-09-voiceover-elevenlabs.md` |
| Update inline refs | `docs/superpowers/plans/2026-05-09-youtube-seo-research.md` |
| Update inline refs | `docs/superpowers/specs/2026-05-09-pipeline-kanban-design.md` |

### Phase 2: tts-gotchas pointer fix

| Action | Path |
|---|---|
| Modify | `.claude/skills/script-writer/reference/tts-gotchas.md` (one paragraph) |

### Phase 3: Build v2 tool

```
tools/voiceover-elevenlabs-v2/
├── pyproject.toml          (new) name=voiceover-elevenlabs-v2; package=voiceover_elevenlabs_v2
├── README.md               (new) usage docs
├── .gitignore              (new) copy from v3
├── .python-version         (new) copy from v3
├── src/voiceover_elevenlabs_v2/
│   ├── __init__.py         (new) empty
│   ├── tts.py              (new) v2 TTS wrapper; 10k char limit; style + speaker_boost params
│   ├── scribe.py           (new) Scribe v2 wrapper — copy from renamed v3 tool
│   ├── transcript.py       (new) schema mapping — copy from renamed v3 tool
│   ├── core.py             (new) generate() orchestration with language_code=en
│   └── cli.py              (new) v2 defaults; char-limit guardrail; cost estimator
└── tests/
    ├── conftest.py         (new) Scribe response fixtures — copy from renamed v3 tool
    ├── test_tts.py         (new) v2-specific behavior
    ├── test_scribe.py      (new) copy from renamed v3 tool
    ├── test_transcript.py  (new) copy from renamed v3 tool
    ├── test_core.py        (new) language_code passthrough
    └── test_cli.py         (new) v2 defaults; over-10k error path
```

### Phase 4: Build v2 skill

```
.claude/skills/voiceover-elevenlabs-v2/
├── SKILL.md                (new)
└── reference/
    ├── v2-quirks.md        (new) eight engine landmines
    └── voice-settings.md   (new) recipe + rationale
```

### Phase 5: CLAUDE.md + script-writer hand-off

| Action | Path |
|---|---|
| Modify | `CLAUDE.md` (voiceover paragraph) |
| Modify | `.claude/skills/script-writer/SKILL.md` (Step 6 hand-off) |

### Phase 6: First real render verification

Manual verification step — no file changes; user runs the new skill against an existing video folder and confirms outputs.

---

## Phase 1 — Rename

### Task 1: Move folders and rename Python package

**Files:**
- Move: `tools/voiceover-elevenlabs/` → `tools/voiceover-elevenlabs-v3/`
- Move: `tools/voiceover-elevenlabs-v3/src/voiceover_elevenlabs/` → `tools/voiceover-elevenlabs-v3/src/voiceover_elevenlabs_v3/`
- Move: `.claude/skills/voiceover-elevenlabs/` → `.claude/skills/voiceover-elevenlabs-v3/`

- [ ] **Step 1: Move the tool folder**

```bash
git mv tools/voiceover-elevenlabs tools/voiceover-elevenlabs-v3
```

- [ ] **Step 2: Rename the inner Python package directory**

```bash
git mv tools/voiceover-elevenlabs-v3/src/voiceover_elevenlabs tools/voiceover-elevenlabs-v3/src/voiceover_elevenlabs_v3
```

- [ ] **Step 3: Move the skill folder**

```bash
git mv .claude/skills/voiceover-elevenlabs .claude/skills/voiceover-elevenlabs-v3
```

- [ ] **Step 4: Verify folder layout**

Run: `ls tools/voiceover-elevenlabs-v3/src/ .claude/skills/voiceover-elevenlabs-v3/`
Expected:
```
.claude/skills/voiceover-elevenlabs-v3/:
SKILL.md

tools/voiceover-elevenlabs-v3/src/:
voiceover_elevenlabs_v3
```

(No commit yet — the moved code is broken until Task 2 fixes pyproject and Task 3 fixes imports.)

---

### Task 2: Update pyproject.toml for the renamed package

**Files:**
- Modify: `tools/voiceover-elevenlabs-v3/pyproject.toml`

- [ ] **Step 1: Edit pyproject.toml**

Replace the file's contents with:

```toml
[project]
name = "voiceover-elevenlabs-v3"
version = "0.1.0"
description = "Generate voiceover audio (ElevenLabs v3) and word-level transcript (Scribe v2) from an annotated script."
readme = "README.md"
authors = [
    { name = "Akwasi Konadu Akuoko", email = "akwasikonadueverlasting@gmail.com" }
]
requires-python = ">=3.12"
dependencies = [
    "elevenlabs>=1.0.0",
    "python-dotenv>=1.0.0",
]

[project.scripts]
voiceover-elevenlabs-v3 = "voiceover_elevenlabs_v3.cli:main"

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-mock>=3.12.0",
]

[build-system]
requires = ["uv_build>=0.11.10,<0.12.0"]
build-backend = "uv_build"

[tool.pyright]
venvPath = "."
venv = ".venv"
extraPaths = ["src"]
```

The only changes from the original: `name`, the `[project.scripts]` key+value (both the binary name and the import path now end in `_v3`).

- [ ] **Step 2: Re-sync the venv to pick up the rename**

```bash
cd tools/voiceover-elevenlabs-v3 && uv sync
```

Expected: succeeds without errors. The `voiceover-elevenlabs-v3` binary is now installed in the local venv.

(No commit yet — imports inside the .py files still reference the old `voiceover_elevenlabs` package and will fail.)

---

### Task 3: Update Python imports in src/ and tests/

**Files:**
- Modify: `tools/voiceover-elevenlabs-v3/src/voiceover_elevenlabs_v3/cli.py`
- Modify: `tools/voiceover-elevenlabs-v3/src/voiceover_elevenlabs_v3/core.py`
- Modify: `tools/voiceover-elevenlabs-v3/tests/test_cli.py`
- Modify: `tools/voiceover-elevenlabs-v3/tests/test_core.py`
- Modify: `tools/voiceover-elevenlabs-v3/tests/test_tts.py`
- Modify: `tools/voiceover-elevenlabs-v3/tests/test_scribe.py`
- Modify: `tools/voiceover-elevenlabs-v3/tests/test_transcript.py`

- [ ] **Step 1: Audit which files reference the old package name**

Run: `grep -rn "voiceover_elevenlabs" tools/voiceover-elevenlabs-v3/ --include="*.py"`
Expected: shows every line that imports from the old package name. Note them; the next step rewrites them all.

- [ ] **Step 2: Rewrite imports across src/ and tests/**

Run:

```bash
find tools/voiceover-elevenlabs-v3 -name '*.py' -exec sed -i '' 's/voiceover_elevenlabs\b/voiceover_elevenlabs_v3/g' {} +
```

Note: `sed -i ''` is the macOS form (BSD sed). The `\b` word boundary prevents matching e.g. `voiceover_elevenlabs_v3` itself if it were already present.

- [ ] **Step 3: Verify the rewrite**

Run: `grep -rn "voiceover_elevenlabs\b" tools/voiceover-elevenlabs-v3/ --include="*.py"`
Expected: no matches (every occurrence is now `voiceover_elevenlabs_v3`).

Run: `grep -rn "voiceover_elevenlabs_v3" tools/voiceover-elevenlabs-v3/ --include="*.py" | head`
Expected: shows the rewritten import lines.

- [ ] **Step 4: Run the v3 test suite to confirm green**

```bash
cd tools/voiceover-elevenlabs-v3 && uv run pytest tests/ -v
```

Expected: all tests pass. The rename is now functionally complete on the code side.

(No commit yet — README, SKILL.md, and historical docs still reference the old name. Bundle them into one rename commit at the end of the phase.)

---

### Task 4: Update the v3 tool's README

**Files:**
- Modify: `tools/voiceover-elevenlabs-v3/README.md`

- [ ] **Step 1: Edit README.md**

Replace the file with:

```markdown
# voiceover-elevenlabs-v3

Generate voiceover audio (ElevenLabs v3) and a word-level transcript
(ElevenLabs Scribe v2 on the rendered audio) from an annotated script,
in a single command. Built for the hyper-frames video pipeline; produces
the canonical `audio/voiceover.mp3` + `transcript.json` shape the rest
of the project consumes.

> **Renamed from `voiceover-elevenlabs` on 2026-05-09** so the engine
> version is explicit. The companion `voiceover-elevenlabs-v2` tool is
> the project default for YouTube videos; this v3 tool stays available
> for content that genuinely benefits from per-beat audio tags.
> See `docs/superpowers/specs/2026-05-09-voiceover-elevenlabs-v2-and-rename-design.md`.

The transcript is generated from Scribe v2, **not** v3's native
character alignment. See the original spec at
`docs/superpowers/specs/2026-05-09-voiceover-elevenlabs-design.md` for
why (timing-truth invariant, v3-derived alignment unverified).

## Install

The project uses `uv`. From this directory:

```bash
uv sync
```

Set `ELEVENLABS_API_KEY` in `.env` at the repo root. The same key serves
both v3 and Scribe v2.

## Usage

```bash
# Inside a video folder, with voiceover.txt at the folder root:
uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/voiceover-elevenlabs-v3 \
  voiceover-elevenlabs-v3 voiceover.txt
```

Writes `audio/voiceover.mp3` and `transcript.json` next to the input.

### Flags

| Flag | Default | Notes |
| --- | --- | --- |
| `-o`, `--output-audio PATH` | `audio/voiceover.mp3` | MP3 destination. |
| `--output-transcript PATH` | `transcript.json` | Transcript destination (project schema). |
| `--voice-id ID` | `UgBBYS2sOqTuMpoF3BR0` | ElevenLabs voice ID. |
| `--model ID` | `eleven_v3` | TTS model. |
| `--stability FLOAT` | `0.5` (Natural) | v3 stability slider. |
| `--similarity-boost FLOAT` | `0.75` | v3 similarity boost. |
| `--no-transcript` | off | Skip Scribe call; produce audio only. |
| `--dry-run` | off | Print char count + cost estimate; no API call. |

### Input format

`voiceover.txt` is plain UTF-8 text — typically the LLM-annotated output
from the `voiceover-elevenlabs-v3` skill, with v3 audio tags (`[sighs]`),
ellipses (`…`), and ALL-CAPS emphasis applied. The tool sends the file
contents to v3 verbatim.

## Library use

```python
from pathlib import Path
from voiceover_elevenlabs_v3 import generate

generate(
    text_path=Path("voiceover.txt"),
    audio_path=Path("audio/voiceover.mp3"),
    transcript_path=Path("transcript.json"),
    voice_id="UgBBYS2sOqTuMpoF3BR0",
    api_key="sk_...",
)
```

## Testing

```bash
uv run pytest tests/ -v
```

All wrapper code is unit-tested with mocked SDK clients. The Scribe →
project-schema mapping has full coverage including the defensive cases
(missing `audio_duration_secs`, undefined per-word timestamps).

## Origin

Spec: `docs/superpowers/specs/2026-05-09-voiceover-elevenlabs-design.md`.
Replaces the `hyperframes-media tts` (Kokoro) path for this project's
videos. The Kokoro skill stays untouched and parallel for any non-v3
use case.
```

(Note: also update the Library use snippet — `from voiceover_elevenlabs import generate` → `from voiceover_elevenlabs_v3 import generate`.)

---

### Task 5: Update the v3 skill's SKILL.md

**Files:**
- Modify: `.claude/skills/voiceover-elevenlabs-v3/SKILL.md`

- [ ] **Step 1: Edit the frontmatter `name:` field**

Change:
```
name: voiceover-elevenlabs
```
to:
```
name: voiceover-elevenlabs-v3
```

- [ ] **Step 2: Edit the description field**

The description currently says "Replaces the hyperframes-media (Kokoro) TTS path for this project". Replace with:

```
description: Turn an approved script.md into a voiceover (ElevenLabs v3) and a word-level transcript (Scribe v2) in one run, with an LLM-driven beat-aware annotation step (curated audio tags, ellipses, anchor-driven ALL-CAPS) behind a hard checkpoint before any API credits are spent. Use when the user explicitly requests v3 (passes `with v3` to the script-writer hand-off) or when a video genuinely needs inline audio tags for per-beat emotional shifts. The project default for YouTube videos is `voiceover-elevenlabs-v2` — invoke that unless v3's tag-driven expressiveness is specifically wanted. Outputs land at audio/voiceover.mp3 and transcript.json at the video folder root.
```

- [ ] **Step 3: Update Step 4 invocation path**

Find the bash block under "Step 4 — Generate":

```bash
uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/voiceover-elevenlabs \
  voiceover-elevenlabs <video-dir>/voiceover.txt \
```

Replace with:

```bash
uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/voiceover-elevenlabs-v3 \
  voiceover-elevenlabs-v3 <video-dir>/voiceover.txt \
```

- [ ] **Step 4: Verify no other inline references to the old name remain**

Run: `grep -n "voiceover-elevenlabs\b" .claude/skills/voiceover-elevenlabs-v3/SKILL.md`
Expected: no matches (every reference is now `voiceover-elevenlabs-v3` or unrelated).

---

### Task 6: Add top-of-file pointers to historical docs

**Files:**
- Modify: `docs/superpowers/specs/2026-05-09-voiceover-elevenlabs-design.md`
- Modify: `docs/superpowers/plans/2026-05-09-voiceover-elevenlabs.md`

- [ ] **Step 1: Prepend pointer to the v3 spec**

Add as the second line of the file (after the `# title` line, before the metadata block):

```markdown
> **Note (2026-05-09):** The tool and skill described in this doc were renamed to `voiceover-elevenlabs-v3`. See [`2026-05-09-voiceover-elevenlabs-v2-and-rename-design.md`](2026-05-09-voiceover-elevenlabs-v2-and-rename-design.md) for the rename + the new v2 default.
```

- [ ] **Step 2: Prepend the same pointer to the v3 plan**

Same change in `docs/superpowers/plans/2026-05-09-voiceover-elevenlabs.md` (the spec link path will need adjusting — point at `../specs/2026-05-09-voiceover-elevenlabs-v2-and-rename-design.md` from the `plans/` folder).

---

### Task 7: Update inline mentions in other docs

**Files:**
- Modify: `docs/superpowers/plans/2026-05-09-youtube-seo-research.md`
- Modify: `docs/superpowers/specs/2026-05-09-pipeline-kanban-design.md`

- [ ] **Step 1: Find the inline references**

Run: `grep -n "voiceover-elevenlabs\b" docs/superpowers/plans/2026-05-09-youtube-seo-research.md docs/superpowers/specs/2026-05-09-pipeline-kanban-design.md`
Expected: a small number of textual references (not file paths — the rename only touches the runtime tool/skill folders, not historical doc filenames).

- [ ] **Step 2: Update each reference**

For each match, decide based on context:
- If the reference is to "the v3 voiceover skill" or "the existing voiceover tool", update to `voiceover-elevenlabs-v3` to disambiguate.
- If the reference is just narrative ("we use ElevenLabs for voiceover"), no change needed.

Use the `Edit` tool per file with the appropriate `old_string` / `new_string`.

- [ ] **Step 3: Verify the audit**

Run: `grep -rn "voiceover-elevenlabs\b" docs/ --include="*.md"`
Expected: no remaining bare references to `voiceover-elevenlabs` (everything is either `…-v2`, `…-v3`, or has a top-of-file pointer).

---

### Task 8: Run v3 tests one more time, then commit the entire rename

**Files:**
- All Phase 1 changes

- [ ] **Step 1: Run the v3 test suite**

```bash
cd tools/voiceover-elevenlabs-v3 && uv run pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 2: Review the diff**

```bash
git status
git diff --stat
```

Expected: shows the moves, the pyproject + README + SKILL.md edits, the import rewrites, and the doc pointers. Nothing else.

- [ ] **Step 3: Commit**

```bash
git add tools/voiceover-elevenlabs-v3 .claude/skills/voiceover-elevenlabs-v3 docs/superpowers/
git commit -m "$(cat <<'EOF'
refactor: rename voiceover-elevenlabs → voiceover-elevenlabs-v3

Makes the engine version explicit in every reference, in preparation for
the new voiceover-elevenlabs-v2 tool+skill becoming the project default
for YouTube videos. Behavior unchanged — folders, package, binary,
imports, README, and SKILL.md frontmatter all carry the -v3 suffix.

CLAUDE.md and script-writer hand-off are NOT updated in this commit;
they're updated in a later commit once both v2 and v3 skills exist by
their final names.

Spec: docs/superpowers/specs/2026-05-09-voiceover-elevenlabs-v2-and-rename-design.md
EOF
)"
```

---

## Phase 2 — tts-gotchas pointer fix

### Task 9: Replace the aspirational pronunciation-dictionary paragraph

**Files:**
- Modify: `.claude/skills/script-writer/reference/tts-gotchas.md`

- [ ] **Step 1: Edit the trailing paragraph of the "Phonetic respelling" section**

Use the `Edit` tool:

`old_string`:
```
For genuinely durable cases (recurring product names, recurring proper
nouns), promote the entry to the pronunciation dictionary in
`voiceover-elevenlabs` instead of carrying a respelling in every script.
```

`new_string`:
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

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/script-writer/reference/tts-gotchas.md
git commit -m "$(cat <<'EOF'
docs(script-writer): fix aspirational pronunciation-dictionary pointer

The previous pointer claimed durable respellings should be 'promoted to
the pronunciation dictionary in voiceover-elevenlabs', but no such
dictionary existed in either tool. Replace with current-reality guidance
(respell inline + intent comment) and add a 'Future' note describing the
ElevenLabs API surface that would back a real dictionary, gated on the
'same respelling repeats across 2+ videos' trigger.
EOF
)"
```

---

## Phase 3 — Build v2 tool

### Task 10: Scaffold the v2 tool directory + base files

**Files:**
- Create: `tools/voiceover-elevenlabs-v2/pyproject.toml`
- Create: `tools/voiceover-elevenlabs-v2/.python-version`
- Create: `tools/voiceover-elevenlabs-v2/.gitignore`
- Create: `tools/voiceover-elevenlabs-v2/README.md` (placeholder; finalized in Task 17)
- Create: `tools/voiceover-elevenlabs-v2/src/voiceover_elevenlabs_v2/__init__.py`
- Create: `tools/voiceover-elevenlabs-v2/tests/__init__.py`

- [ ] **Step 1: Create the directory tree**

```bash
mkdir -p tools/voiceover-elevenlabs-v2/src/voiceover_elevenlabs_v2 tools/voiceover-elevenlabs-v2/tests
```

- [ ] **Step 2: Create pyproject.toml**

Write to `tools/voiceover-elevenlabs-v2/pyproject.toml`:

```toml
[project]
name = "voiceover-elevenlabs-v2"
version = "0.1.0"
description = "Generate voiceover audio (ElevenLabs Multilingual v2) and word-level transcript (Scribe v2) from an annotated script."
readme = "README.md"
authors = [
    { name = "Akwasi Konadu Akuoko", email = "akwasikonadueverlasting@gmail.com" }
]
requires-python = ">=3.12"
dependencies = [
    "elevenlabs>=1.0.0",
    "python-dotenv>=1.0.0",
]

[project.scripts]
voiceover-elevenlabs-v2 = "voiceover_elevenlabs_v2.cli:main"

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-mock>=3.12.0",
]

[build-system]
requires = ["uv_build>=0.11.10,<0.12.0"]
build-backend = "uv_build"

[tool.pyright]
venvPath = "."
venv = ".venv"
extraPaths = ["src"]
```

- [ ] **Step 3: Copy `.python-version` and `.gitignore` from the v3 tool**

```bash
cp tools/voiceover-elevenlabs-v3/.python-version tools/voiceover-elevenlabs-v2/.python-version
cp tools/voiceover-elevenlabs-v3/.gitignore tools/voiceover-elevenlabs-v2/.gitignore
```

- [ ] **Step 4: Create the empty `__init__.py` files**

Write empty file: `tools/voiceover-elevenlabs-v2/src/voiceover_elevenlabs_v2/__init__.py`

Write empty file: `tools/voiceover-elevenlabs-v2/tests/__init__.py`

- [ ] **Step 5: Create a placeholder README**

Write to `tools/voiceover-elevenlabs-v2/README.md`:

```markdown
# voiceover-elevenlabs-v2

Placeholder — finalized in Task 17 of the implementation plan.
```

- [ ] **Step 6: Run `uv sync` to bootstrap the venv**

```bash
cd tools/voiceover-elevenlabs-v2 && uv sync
```

Expected: succeeds. The `voiceover-elevenlabs-v2` binary is registered (though `cli:main` doesn't exist yet — that's added in Task 16).

- [ ] **Step 7: Verify the layout**

Run: `ls -la tools/voiceover-elevenlabs-v2/ tools/voiceover-elevenlabs-v2/src/ tools/voiceover-elevenlabs-v2/tests/`
Expected: all five sub-paths exist (`pyproject.toml`, `.python-version`, `.gitignore`, `README.md`, `src/voiceover_elevenlabs_v2/__init__.py`, `tests/__init__.py`).

- [ ] **Step 8: Commit the scaffold**

```bash
git add tools/voiceover-elevenlabs-v2/
git commit -m "feat(v2): scaffold tools/voiceover-elevenlabs-v2 package"
```

---

### Task 11: Copy Scribe and transcript modules from v3 (they're engine-agnostic)

**Files:**
- Create: `tools/voiceover-elevenlabs-v2/src/voiceover_elevenlabs_v2/scribe.py`
- Create: `tools/voiceover-elevenlabs-v2/src/voiceover_elevenlabs_v2/transcript.py`
- Create: `tools/voiceover-elevenlabs-v2/tests/conftest.py`
- Create: `tools/voiceover-elevenlabs-v2/tests/test_scribe.py`
- Create: `tools/voiceover-elevenlabs-v2/tests/test_transcript.py`

`scribe.py` and `transcript.py` are independent of the TTS model — both call Scribe v2 on already-rendered audio and map the response to the project schema. Mechanical copy-then-rename-import.

- [ ] **Step 1: Copy the four files**

```bash
cp tools/voiceover-elevenlabs-v3/src/voiceover_elevenlabs_v3/scribe.py tools/voiceover-elevenlabs-v2/src/voiceover_elevenlabs_v2/scribe.py
cp tools/voiceover-elevenlabs-v3/src/voiceover_elevenlabs_v3/transcript.py tools/voiceover-elevenlabs-v2/src/voiceover_elevenlabs_v2/transcript.py
cp tools/voiceover-elevenlabs-v3/tests/conftest.py tools/voiceover-elevenlabs-v2/tests/conftest.py
cp tools/voiceover-elevenlabs-v3/tests/test_scribe.py tools/voiceover-elevenlabs-v2/tests/test_scribe.py
cp tools/voiceover-elevenlabs-v3/tests/test_transcript.py tools/voiceover-elevenlabs-v2/tests/test_transcript.py
```

- [ ] **Step 2: Rewrite imports in the copied files**

```bash
find tools/voiceover-elevenlabs-v2 -name '*.py' -exec sed -i '' 's/voiceover_elevenlabs_v3\b/voiceover_elevenlabs_v2/g' {} +
```

- [ ] **Step 3: Verify no v3 references remain**

Run: `grep -rn "voiceover_elevenlabs_v3\|voiceover_elevenlabs\b" tools/voiceover-elevenlabs-v2/ --include="*.py"`
Expected: no matches.

- [ ] **Step 4: Run the copied tests**

```bash
cd tools/voiceover-elevenlabs-v2 && uv run pytest tests/test_scribe.py tests/test_transcript.py -v
```

Expected: all tests pass (they're identical to v3's, only the import paths changed).

- [ ] **Step 5: Commit**

```bash
git add tools/voiceover-elevenlabs-v2/src/voiceover_elevenlabs_v2/scribe.py \
        tools/voiceover-elevenlabs-v2/src/voiceover_elevenlabs_v2/transcript.py \
        tools/voiceover-elevenlabs-v2/tests/conftest.py \
        tools/voiceover-elevenlabs-v2/tests/test_scribe.py \
        tools/voiceover-elevenlabs-v2/tests/test_transcript.py
git commit -m "feat(v2): scribe + transcript modules (copy of v3, engine-agnostic)"
```

---

### Task 12: TDD `tts.py` — v2 TTS wrapper

**Files:**
- Create: `tools/voiceover-elevenlabs-v2/tests/test_tts.py`
- Create: `tools/voiceover-elevenlabs-v2/src/voiceover_elevenlabs_v2/tts.py`

- [ ] **Step 1: Write the failing test**

Write to `tools/voiceover-elevenlabs-v2/tests/test_tts.py`:

```python
"""Unit tests for the v2 TTS wrapper."""
from unittest.mock import MagicMock, patch

import pytest

from voiceover_elevenlabs_v2.tts import V2_CHAR_LIMIT, synthesize


def _stub_convert_returns(audio_bytes: bytes):
    """Build a MagicMock whose convert() returns an iterable yielding audio_bytes once."""
    return MagicMock(return_value=iter([audio_bytes]))


def test_synthesize_calls_convert_with_v2_defaults():
    fake_audio = b"\xff\xfb\x90\x00fake-mp3-bytes"
    with patch("voiceover_elevenlabs_v2.tts.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        mock_client.text_to_speech.convert = _stub_convert_returns(fake_audio)
        mock_client_class.return_value = mock_client

        result = synthesize(
            "Hello world.",
            voice_id="VOICE",
            api_key="sk_test",
        )

        mock_client_class.assert_called_once_with(api_key="sk_test")
        call_kwargs = mock_client.text_to_speech.convert.call_args.kwargs
        assert call_kwargs["voice_id"] == "VOICE"
        assert call_kwargs["text"] == "Hello world."
        assert call_kwargs["model_id"] == "eleven_multilingual_v2"
        assert call_kwargs["output_format"] == "mp3_44100_128"
        assert call_kwargs["language_code"] == "en"
        assert result == fake_audio


def test_synthesize_passes_full_voice_settings():
    """v2 carries stability + similarity_boost + style + use_speaker_boost."""
    with patch("voiceover_elevenlabs_v2.tts.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        mock_client.text_to_speech.convert = _stub_convert_returns(b"x")
        mock_client_class.return_value = mock_client

        synthesize(
            "x",
            voice_id="V",
            stability=0.4,
            similarity_boost=0.75,
            style=0.35,
            use_speaker_boost=True,
            api_key="sk_test",
        )

        call_kwargs = mock_client.text_to_speech.convert.call_args.kwargs
        settings = call_kwargs["voice_settings"]
        assert settings.stability == 0.4
        assert settings.similarity_boost == 0.75
        assert settings.style == 0.35
        assert settings.use_speaker_boost is True


def test_synthesize_rejects_text_over_10k():
    long_text = "x" * (V2_CHAR_LIMIT + 1)
    with pytest.raises(ValueError, match="character limit"):
        synthesize(long_text, voice_id="V", api_key="sk_test")


def test_synthesize_concatenates_streamed_chunks():
    """The SDK's convert() returns an iterator of bytes chunks; we join them."""
    with patch("voiceover_elevenlabs_v2.tts.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        mock_client.text_to_speech.convert = MagicMock(return_value=iter([b"abc", b"def", b"ghi"]))
        mock_client_class.return_value = mock_client

        result = synthesize("hi", voice_id="V", api_key="sk_test")
        assert result == b"abcdefghi"


def test_synthesize_accepts_custom_language_code():
    """When the caller overrides language_code, that value is forwarded."""
    with patch("voiceover_elevenlabs_v2.tts.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        mock_client.text_to_speech.convert = _stub_convert_returns(b"x")
        mock_client_class.return_value = mock_client

        synthesize("x", voice_id="V", language_code="es", api_key="sk_test")

        call_kwargs = mock_client.text_to_speech.convert.call_args.kwargs
        assert call_kwargs["language_code"] == "es"
```

- [ ] **Step 2: Run the tests to confirm they fail**

```bash
cd tools/voiceover-elevenlabs-v2 && uv run pytest tests/test_tts.py -v
```

Expected: ImportError ("No module named voiceover_elevenlabs_v2.tts" or equivalent).

- [ ] **Step 3: Write the minimal implementation**

Write to `tools/voiceover-elevenlabs-v2/src/voiceover_elevenlabs_v2/tts.py`:

```python
"""ElevenLabs Multilingual v2 Text-to-Speech wrapper.

Thin layer over the official `elevenlabs` SDK. Single responsibility:
take a string of text + voice/model/settings, return MP3 bytes. No I/O,
no retries — the calling code (core.py) handles file writes.

Defaults reflect v2 docs guidance for long-form narration:
- stability=0.4 (long-form sweet spot per docs; above 0.7 paradoxically
  produces more monotone delivery)
- similarity_boost=0.75
- style=0.35 (docs recommend 0.3–0.5 for natural expression; cap at 0.5
  by convention — above ~0.6 produces erratic emphasis on long-form)
- use_speaker_boost=True (default per SDK)
- language_code='en' (mitigates v2's tendency to switch accent/language
  on individual proper nouns it thinks belong to another language)
"""
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

# v2 per-request character limit per the official models page (~10 minutes
# of audio). Scripts past this need manual splitting; chunked + stitched
# generation is deferred to a later iteration.
V2_CHAR_LIMIT = 10_000


def synthesize(
    text: str,
    *,
    voice_id: str,
    model_id: str = "eleven_multilingual_v2",
    stability: float = 0.4,
    similarity_boost: float = 0.75,
    style: float = 0.35,
    use_speaker_boost: bool = True,
    language_code: str = "en",
    output_format: str = "mp3_44100_128",
    api_key: str,
) -> bytes:
    """Render text to MP3 bytes via ElevenLabs Multilingual v2.

    Raises:
        ValueError: if `text` exceeds the v2 per-request character limit.
        elevenlabs.core.api_error.ApiError: on API failures (caller decides retry).
    """
    if len(text) > V2_CHAR_LIMIT:
        raise ValueError(
            f"Text is {len(text)} characters; v2 character limit is {V2_CHAR_LIMIT}. "
            f"Split the script into parts and re-run."
        )

    client = ElevenLabs(api_key=api_key)
    audio_iter = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id=model_id,
        language_code=language_code,
        voice_settings=VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
            style=style,
            use_speaker_boost=use_speaker_boost,
        ),
        output_format=output_format,
    )
    return b"".join(audio_iter)
```

- [ ] **Step 4: Run the tests to confirm they pass**

```bash
cd tools/voiceover-elevenlabs-v2 && uv run pytest tests/test_tts.py -v
```

Expected: all 5 tests pass.

- [ ] **Step 5: Commit**

```bash
git add tools/voiceover-elevenlabs-v2/src/voiceover_elevenlabs_v2/tts.py \
        tools/voiceover-elevenlabs-v2/tests/test_tts.py
git commit -m "feat(v2): tts.py wrapper — Multilingual v2 with style + language_code"
```

---

### Task 13: TDD `core.py` — generate() orchestration

**Files:**
- Create: `tools/voiceover-elevenlabs-v2/tests/test_core.py`
- Create: `tools/voiceover-elevenlabs-v2/src/voiceover_elevenlabs_v2/core.py`

- [ ] **Step 1: Write the failing tests**

Write to `tools/voiceover-elevenlabs-v2/tests/test_core.py`:

```python
"""Unit tests for the v2 core orchestrator."""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from voiceover_elevenlabs_v2.core import generate


def test_generate_writes_audio_and_transcript(tmp_path, scribe_response_minimal):
    text_path = tmp_path / "voiceover.txt"
    text_path.write_text("You open a text editor.")
    audio_path = tmp_path / "audio" / "voiceover.mp3"
    transcript_path = tmp_path / "transcript.json"

    with patch("voiceover_elevenlabs_v2.core.synthesize", return_value=b"FAKE_MP3") as mock_tts, \
         patch("voiceover_elevenlabs_v2.core.transcribe", return_value=scribe_response_minimal) as mock_scribe:
        generate(
            text_path=text_path,
            audio_path=audio_path,
            transcript_path=transcript_path,
            voice_id="V",
            api_key="sk_test",
        )

    # Audio: written, parent dir created
    assert audio_path.exists()
    assert audio_path.read_bytes() == b"FAKE_MP3"

    # Transcript: written as JSON matching project schema
    transcript = json.loads(transcript_path.read_text())
    assert transcript["audio_duration_secs"] == 0.48
    assert transcript["text"] == "You open"
    assert len(transcript["words"]) == 3

    # synthesize received the text and v2 defaults via kwargs
    tts_kwargs = mock_tts.call_args.kwargs
    assert tts_kwargs["voice_id"] == "V"
    assert tts_kwargs["api_key"] == "sk_test"
    assert tts_kwargs["model_id"] == "eleven_multilingual_v2"
    assert tts_kwargs["language_code"] == "en"
    assert tts_kwargs["stability"] == 0.4
    assert tts_kwargs["similarity_boost"] == 0.75
    assert tts_kwargs["style"] == 0.35
    assert tts_kwargs["use_speaker_boost"] is True

    # Scribe was called on the rendered audio
    mock_scribe.assert_called_once()
    assert mock_scribe.call_args.args[0] == audio_path


def test_generate_skips_transcript_when_disabled(tmp_path):
    text_path = tmp_path / "voiceover.txt"
    text_path.write_text("hi")
    audio_path = tmp_path / "audio.mp3"
    transcript_path = tmp_path / "transcript.json"

    with patch("voiceover_elevenlabs_v2.core.synthesize", return_value=b"X") as _, \
         patch("voiceover_elevenlabs_v2.core.transcribe") as mock_scribe:
        generate(
            text_path=text_path,
            audio_path=audio_path,
            transcript_path=transcript_path,
            voice_id="V",
            api_key="sk_test",
            generate_transcript=False,
        )

    assert audio_path.exists()
    assert not transcript_path.exists()
    mock_scribe.assert_not_called()


def test_generate_forwards_custom_voice_settings(tmp_path, scribe_response_minimal):
    text_path = tmp_path / "voiceover.txt"
    text_path.write_text("x")
    audio_path = tmp_path / "audio.mp3"
    transcript_path = tmp_path / "t.json"

    with patch("voiceover_elevenlabs_v2.core.synthesize", return_value=b"X") as mock_tts, \
         patch("voiceover_elevenlabs_v2.core.transcribe", return_value=scribe_response_minimal):
        generate(
            text_path=text_path,
            audio_path=audio_path,
            transcript_path=transcript_path,
            voice_id="V",
            api_key="sk_test",
            stability=0.5,
            similarity_boost=0.8,
            style=0.5,
            use_speaker_boost=False,
            language_code="es",
        )

    tts_kwargs = mock_tts.call_args.kwargs
    assert tts_kwargs["stability"] == 0.5
    assert tts_kwargs["similarity_boost"] == 0.8
    assert tts_kwargs["style"] == 0.5
    assert tts_kwargs["use_speaker_boost"] is False
    assert tts_kwargs["language_code"] == "es"
```

- [ ] **Step 2: Run the tests to confirm they fail**

```bash
cd tools/voiceover-elevenlabs-v2 && uv run pytest tests/test_core.py -v
```

Expected: ImportError ("cannot import name 'generate' from voiceover_elevenlabs_v2.core") because the file doesn't exist yet.

- [ ] **Step 3: Write the implementation**

Write to `tools/voiceover-elevenlabs-v2/src/voiceover_elevenlabs_v2/core.py`:

```python
"""High-level orchestrator: text file → audio + transcript on disk.

Orchestrates the two API calls (Multilingual v2 TTS, then Scribe v2 on the
rendered audio) and the schema mapping. Intentionally simple — no retry
logic beyond what the wrappers do; no parallelism (Scribe needs the audio).
"""
import json
from pathlib import Path

from voiceover_elevenlabs_v2.scribe import transcribe
from voiceover_elevenlabs_v2.transcript import to_transcript
from voiceover_elevenlabs_v2.tts import synthesize


def generate(
    *,
    text_path: Path,
    audio_path: Path,
    transcript_path: Path,
    voice_id: str,
    api_key: str,
    model_id: str = "eleven_multilingual_v2",
    stability: float = 0.4,
    similarity_boost: float = 0.75,
    style: float = 0.35,
    use_speaker_boost: bool = True,
    language_code: str = "en",
    output_format: str = "mp3_44100_128",
    generate_transcript: bool = True,
) -> None:
    """Read text, render audio via v2, transcribe via Scribe v2, write both files.

    Overwrites existing files at `audio_path` and `transcript_path` without
    prompting. Creates parent directories as needed.
    """
    text = text_path.read_text()

    audio_bytes = synthesize(
        text,
        voice_id=voice_id,
        model_id=model_id,
        stability=stability,
        similarity_boost=similarity_boost,
        style=style,
        use_speaker_boost=use_speaker_boost,
        language_code=language_code,
        output_format=output_format,
        api_key=api_key,
    )
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    audio_path.write_bytes(audio_bytes)

    if not generate_transcript:
        return

    response = transcribe(audio_path, api_key=api_key)
    transcript_data = to_transcript(response)
    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    transcript_path.write_text(json.dumps(transcript_data, indent=2))
```

- [ ] **Step 4: Run the tests to confirm they pass**

```bash
cd tools/voiceover-elevenlabs-v2 && uv run pytest tests/test_core.py -v
```

Expected: all 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add tools/voiceover-elevenlabs-v2/src/voiceover_elevenlabs_v2/core.py \
        tools/voiceover-elevenlabs-v2/tests/test_core.py
git commit -m "feat(v2): core.py — generate() orchestration with v2 defaults"
```

---

### Task 14: TDD `cli.py` — argparse, dry-run, char-limit guardrail

**Files:**
- Create: `tools/voiceover-elevenlabs-v2/tests/test_cli.py`
- Create: `tools/voiceover-elevenlabs-v2/src/voiceover_elevenlabs_v2/cli.py`

- [ ] **Step 1: Write the failing tests**

Write to `tools/voiceover-elevenlabs-v2/tests/test_cli.py`:

```python
"""Unit tests for the v2 CLI."""
from pathlib import Path
from unittest.mock import patch

import pytest

from voiceover_elevenlabs_v2.cli import build_parser, main


def test_parser_v2_defaults():
    parser = build_parser()
    args = parser.parse_args(["voiceover.txt"])
    assert args.input_path == Path("voiceover.txt")
    assert args.output_audio == Path("audio/voiceover.mp3")
    assert args.output_transcript == Path("transcript.json")
    assert args.voice_id == "UgBBYS2sOqTuMpoF3BR0"
    assert args.model == "eleven_multilingual_v2"
    assert args.stability == 0.4
    assert args.similarity_boost == 0.75
    assert args.style == 0.35
    assert args.use_speaker_boost is True
    assert args.language_code == "en"
    assert args.generate_transcript is True
    assert args.dry_run is False


def test_dry_run_prints_estimate_and_skips_api(tmp_path, capsys):
    txt = tmp_path / "voiceover.txt"
    txt.write_text("x" * 1000)  # 1000 chars

    with patch("voiceover_elevenlabs_v2.cli.generate") as mock_gen:
        rc = main([str(txt), "--dry-run"])

    assert rc == 0
    mock_gen.assert_not_called()
    out = capsys.readouterr().out
    assert "1000 characters" in out
    assert "v2 TTS" in out


def test_missing_input_returns_2(tmp_path, capsys):
    rc = main([str(tmp_path / "nope.txt")])
    assert rc == 2
    err = capsys.readouterr().err
    assert "not found" in err.lower()


def test_missing_api_key_returns_2(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    txt = tmp_path / "voiceover.txt"
    txt.write_text("hi")

    rc = main([str(txt)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "ELEVENLABS_API_KEY" in err


def test_input_over_10k_returns_2_before_api(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "sk_test")
    txt = tmp_path / "voiceover.txt"
    txt.write_text("x" * 10_001)

    with patch("voiceover_elevenlabs_v2.cli.generate") as mock_gen:
        rc = main([str(txt)])

    assert rc == 2
    mock_gen.assert_not_called()
    err = capsys.readouterr().err
    assert "10,000" in err or "10000" in err
    assert "split" in err.lower()


def test_main_invokes_generate_with_v2_kwargs(tmp_path, monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "sk_test")
    txt = tmp_path / "voiceover.txt"
    txt.write_text("hello world")

    with patch("voiceover_elevenlabs_v2.cli.generate") as mock_gen:
        rc = main([str(txt), "-o", str(tmp_path / "a.mp3"),
                   "--output-transcript", str(tmp_path / "t.json")])

    assert rc == 0
    kwargs = mock_gen.call_args.kwargs
    assert kwargs["text_path"] == txt
    assert kwargs["audio_path"] == tmp_path / "a.mp3"
    assert kwargs["transcript_path"] == tmp_path / "t.json"
    assert kwargs["voice_id"] == "UgBBYS2sOqTuMpoF3BR0"
    assert kwargs["api_key"] == "sk_test"
    assert kwargs["model_id"] == "eleven_multilingual_v2"
    assert kwargs["stability"] == 0.4
    assert kwargs["style"] == 0.35
    assert kwargs["language_code"] == "en"


def test_no_speaker_boost_flag(tmp_path, monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "sk_test")
    txt = tmp_path / "voiceover.txt"
    txt.write_text("hi")

    with patch("voiceover_elevenlabs_v2.cli.generate") as mock_gen:
        main([str(txt), "--no-use-speaker-boost"])

    assert mock_gen.call_args.kwargs["use_speaker_boost"] is False
```

- [ ] **Step 2: Run the tests to confirm they fail**

```bash
cd tools/voiceover-elevenlabs-v2 && uv run pytest tests/test_cli.py -v
```

Expected: ImportError on `build_parser` / `main`.

- [ ] **Step 3: Write the implementation**

Write to `tools/voiceover-elevenlabs-v2/src/voiceover_elevenlabs_v2/cli.py`:

```python
"""Command-line entry point for voiceover-elevenlabs-v2.

Usage:
    voiceover-elevenlabs-v2 voiceover.txt
    voiceover-elevenlabs-v2 voiceover.txt --dry-run
    voiceover-elevenlabs-v2 voiceover.txt --no-transcript -o audio/v.mp3
"""
import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from voiceover_elevenlabs_v2.core import generate
from voiceover_elevenlabs_v2.tts import V2_CHAR_LIMIT

# v2 cost per 1k characters in credits. Approximate — verify against actual
# billing on the first real run and adjust if needed (see plan §11 step 6).
V2_CREDITS_PER_1K_CHARS = 15
# Scribe v2 cost in USD per hour of audio.
SCRIBE_USD_PER_HOUR = 0.40
# Words per minute (project house style — 170 wpm per CLAUDE.md).
WORDS_PER_MINUTE = 170


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="voiceover-elevenlabs-v2",
        description="Generate Multilingual v2 voiceover + Scribe v2 transcript from an annotated script.",
    )
    parser.add_argument("input_path", type=Path, help="Path to the annotated script (e.g. voiceover.txt).")
    parser.add_argument("-o", "--output-audio", type=Path, default=Path("audio/voiceover.mp3"))
    parser.add_argument("--output-transcript", type=Path, default=Path("transcript.json"))
    parser.add_argument("--voice-id", default="UgBBYS2sOqTuMpoF3BR0")
    parser.add_argument("--model", default="eleven_multilingual_v2")
    parser.add_argument("--stability", type=float, default=0.4)
    parser.add_argument("--similarity-boost", type=float, default=0.75)
    parser.add_argument("--style", type=float, default=0.35)
    parser.add_argument("--use-speaker-boost", dest="use_speaker_boost", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--language-code", default="en")
    parser.add_argument("--no-transcript", dest="generate_transcript", action="store_false")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print char count + cost estimate without calling any API.")
    return parser


def _estimate_cost(text: str) -> str:
    chars = len(text)
    words = len(text.split())
    minutes = words / WORDS_PER_MINUTE
    credits = chars * V2_CREDITS_PER_1K_CHARS / 1000
    scribe_usd = minutes * SCRIBE_USD_PER_HOUR / 60
    return (
        f"{chars} characters · ~{words} words · ~{minutes:.1f} min audio\n"
        f"v2 TTS: ~{credits:.0f} credits (≈ half v3's rate)\n"
        f"Scribe v2: ~${scribe_usd:.2f}"
    )


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.input_path.exists():
        print(f"Input not found: {args.input_path}", file=sys.stderr)
        return 2

    text = args.input_path.read_text()

    if args.dry_run:
        print(_estimate_cost(text))
        return 0

    if len(text) > V2_CHAR_LIMIT:
        print(
            f"Input is {len(text)} chars; v2's per-request limit is 10,000.\n"
            f"Split voiceover.txt into parts and run again. Chunked + stitched\n"
            f"mode is not yet implemented (see design doc §2 'Out of scope').",
            file=sys.stderr,
        )
        return 2

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print(
            "ELEVENLABS_API_KEY is not set. Add it to .env at the repo root.",
            file=sys.stderr,
        )
        return 2

    print(_estimate_cost(text))
    print(f"Generating audio → {args.output_audio}", file=sys.stderr)

    try:
        generate(
            text_path=args.input_path,
            audio_path=args.output_audio,
            transcript_path=args.output_transcript,
            voice_id=args.voice_id,
            api_key=api_key,
            model_id=args.model,
            stability=args.stability,
            similarity_boost=args.similarity_boost,
            style=args.style,
            use_speaker_boost=args.use_speaker_boost,
            language_code=args.language_code,
            generate_transcript=args.generate_transcript,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"API error: {e}", file=sys.stderr)
        return 1

    print(f"Audio    → {args.output_audio}")
    if args.generate_transcript:
        print(f"Transcript → {args.output_transcript}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the tests to confirm they pass**

```bash
cd tools/voiceover-elevenlabs-v2 && uv run pytest tests/test_cli.py -v
```

Expected: all 7 tests pass.

- [ ] **Step 5: Run the full test suite**

```bash
cd tools/voiceover-elevenlabs-v2 && uv run pytest tests/ -v
```

Expected: all tests across all modules pass.

- [ ] **Step 6: Commit**

```bash
git add tools/voiceover-elevenlabs-v2/src/voiceover_elevenlabs_v2/cli.py \
        tools/voiceover-elevenlabs-v2/tests/test_cli.py
git commit -m "feat(v2): cli.py — v2 defaults, char-limit guardrail, BooleanOptionalAction speaker_boost"
```

---

### Task 15: Finalize the v2 README

**Files:**
- Modify: `tools/voiceover-elevenlabs-v2/README.md`

- [ ] **Step 1: Replace the placeholder README**

Write to `tools/voiceover-elevenlabs-v2/README.md`:

```markdown
# voiceover-elevenlabs-v2

Generate voiceover audio (ElevenLabs Multilingual v2) and a word-level
transcript (Scribe v2 on the rendered audio) from an annotated script,
in a single command. The **project default** for hyper-frames YouTube
videos — long-form stable per the official models page, plain-prose
match for the project's house style.

The companion `voiceover-elevenlabs-v3` tool stays available for content
that genuinely benefits from per-beat audio tags. See the design doc at
`docs/superpowers/specs/2026-05-09-voiceover-elevenlabs-v2-and-rename-design.md`.

## Install

```bash
uv sync
```

Set `ELEVENLABS_API_KEY` in `.env` at the repo root.

## Usage

```bash
# Inside a video folder, with voiceover.txt at the folder root:
uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/voiceover-elevenlabs-v2 \
  voiceover-elevenlabs-v2 voiceover.txt
```

Writes `audio/voiceover.mp3` and `transcript.json` next to the input.

### Flags

| Flag | Default | Notes |
| --- | --- | --- |
| `-o`, `--output-audio PATH` | `audio/voiceover.mp3` | MP3 destination. |
| `--output-transcript PATH` | `transcript.json` | Transcript destination (project schema). |
| `--voice-id ID` | `UgBBYS2sOqTuMpoF3BR0` | Same default voice as the v3 tool. |
| `--model ID` | `eleven_multilingual_v2` | Locked model — flag exists for symmetry. |
| `--stability FLOAT` | `0.4` | Long-form sweet spot per docs (0.35–0.4). |
| `--similarity-boost FLOAT` | `0.75` | Same as v3 default. |
| `--style FLOAT` | `0.35` | v2-only param; docs recommend 0.3–0.5. |
| `--use-speaker-boost / --no-use-speaker-boost` | `True` | v2-only param. |
| `--language-code STR` | `en` | Locks generation language; mitigates v2's tendency to switch accent on individual words. |
| `--no-transcript` | off | Skip Scribe call; produce audio only. |
| `--dry-run` | off | Print char count + cost estimate; no API call. |

### Input format

`voiceover.txt` is plain UTF-8 text — typically the output from the
`voiceover-elevenlabs-v2` skill, with ALL-CAPS on anchor terms and
optional SSML `<break time="Xs"/>` tags at structural pauses. **No audio
tags** — v2 doesn't support them. The tool sends the file contents to
v2 verbatim.

### Char limit

v2's per-request limit is **10,000 characters** (~10 minutes audio per
the official models page). The tool errors loudly past this; chunked +
stitched generation is not yet implemented. For 10+ min scripts, split
`voiceover.txt` into parts and run twice.

## Library use

```python
from pathlib import Path
from voiceover_elevenlabs_v2 import generate

generate(
    text_path=Path("voiceover.txt"),
    audio_path=Path("audio/voiceover.mp3"),
    transcript_path=Path("transcript.json"),
    voice_id="UgBBYS2sOqTuMpoF3BR0",
    api_key="sk_...",
)
```

## Testing

```bash
uv run pytest tests/ -v
```

All wrapper code is unit-tested with mocked SDK clients. The Scribe →
project-schema mapping has full coverage including the defensive cases.

## Origin

Spec: `docs/superpowers/specs/2026-05-09-voiceover-elevenlabs-v2-and-rename-design.md`.
```

- [ ] **Step 2: Commit**

```bash
git add tools/voiceover-elevenlabs-v2/README.md
git commit -m "docs(v2): finalize README with v2 flags, char limit, library use"
```

---

## Phase 4 — Build v2 skill

### Task 16: Create the v2 skill folder + SKILL.md

**Files:**
- Create: `.claude/skills/voiceover-elevenlabs-v2/SKILL.md`

- [ ] **Step 1: Create the skill folder**

```bash
mkdir -p .claude/skills/voiceover-elevenlabs-v2/reference
```

- [ ] **Step 2: Write SKILL.md**

Write to `.claude/skills/voiceover-elevenlabs-v2/SKILL.md`:

```markdown
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

## Annotation taxonomy

### 3.1 Allowed elements

| Element | Rule |
|---|---|
| ALL-CAPS on `anchors.txt` terms | Allowed; only on terms that appear in `anchors.txt`. No ad-hoc capitalization. If `anchors.txt` is missing, no ALL-CAPS at all. |
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
```

- [ ] **Step 3: Verify the file structure**

Run: `ls .claude/skills/voiceover-elevenlabs-v2/`
Expected: `SKILL.md` and `reference/` (empty so far).

(No commit yet — bundle with the reference files in Task 18.)

---

### Task 17: Write `reference/v2-quirks.md`

**Files:**
- Create: `.claude/skills/voiceover-elevenlabs-v2/reference/v2-quirks.md`

- [ ] **Step 1: Write the file**

Write to `.claude/skills/voiceover-elevenlabs-v2/reference/v2-quirks.md`:

```markdown
# v2-quirks — eight engine landmines

Multilingual v2's sharp edges, sourced from the official models page,
help center, and the project's own first-render observations. Apply
these mitigations during annotation and tool defaults; the SKILL.md
already wires the most important ones in.

## 1. Language switching mid-generation

v2 sometimes switches accent or even language on a single proper noun if
the model thinks it's in another language ("paella", "naïve", "café",
"jalapeño", "résumé"). The audio sounds like an English narrator briefly
became Spanish/French/etc. for one word.

**Mitigation:** Pass `language_code="en"` on every call. The v2 tool's
default does this. If a specific word still slips, respell phonetically
in `script.md` and add a `<!-- TTS: jalapeño → ha-la-pen-yo -->`
comment.

## 2. No phoneme tags

v2 doesn't accept `<phoneme>` SSML. Pronunciation control is via:

- Inline phonetic respelling per `script-writer/reference/tts-gotchas.md`
- Project-level pronunciation dictionary (alias rules) — not yet wired
  into our tools; see the "Future" note in `tts-gotchas.md`.

Don't reach for SSML phonemes — they silently fail.

## 3. SSML break tag bounds

v2 supports `<break time="Xs"/>` up to ~3 seconds. Longer pauses fail
silently or get clamped. For longer pauses, split into multiple breaks
(`<break time="2s"/><break time="2s"/>`) or rewrite the sentence so the
pause isn't needed.

Allowed values: 0.3s, 0.5s, 0.8s, 1.5s, 2s, 3s. The skill's hard cap
forbids anything above 3s.

## 4. Style slider trap

`style` above ~0.6 produces erratic emphasis on long-form (random words
get over-stressed, prosody becomes sing-songy). The docs recommend
0.3–0.5 for natural expression; cap at 0.5 by convention.

The tool default is `0.35` — safe. Don't push it higher without first
testing on a 30-second slice.

## 5. Stability paradox

`stability` above ~0.7 produces *more* monotone delivery, not "more
stable." The slider's name is misleading: it controls how rigidly the
voice adheres to a neutral baseline, and the baseline is flat. 0.4 is
the long-form sweet spot per docs.

The tool default is `0.4` — leave it.

## 6. `use_speaker_boost` × similarity stacking

Both push toward the cloned voice. Stacking high values (similarity ≥
0.85 + speaker_boost on) amplifies any flaws in the source recording —
breath noises, room tone, microphone artifacts.

The tool defaults to `similarity_boost=0.75 + use_speaker_boost=True`.
Don't push similarity higher; if the voice doesn't sound like the
source, the source recording probably has issues that need fixing.

## 7. Concurrency limits per plan

From the official models page:

| Plan | Multilingual v2 concurrent |
|---|---|
| Free | 2 |
| Starter | 3 |
| Creator | 5 |
| Pro | 10 |
| Scale / Business | 15 |
| Enterprise | Elevated |

Single-shot + single-user means we never hit this — the tool fires one
request per render. Documented for completeness.

## 8. PVC vs IVC

Professional Voice Clones are **fully supported** on v2 (unlike v3
alpha, where PVC support is partial). If the user upgrades from an
Instant Voice Clone to a Professional Voice Clone, no skill or tool
change is needed — only the `--voice-id` flag value changes.
```

(No commit yet.)

---

### Task 18: Write `reference/voice-settings.md` and commit the skill

**Files:**
- Create: `.claude/skills/voiceover-elevenlabs-v2/reference/voice-settings.md`

- [ ] **Step 1: Write the file**

Write to `.claude/skills/voiceover-elevenlabs-v2/reference/voice-settings.md`:

```markdown
# voice-settings — the recommended recipe

The project default voice settings tuple for v2:

```
stability=0.4
similarity_boost=0.75
style=0.35
use_speaker_boost=True
language_code="en"
```

These are wired into `tools/voiceover-elevenlabs-v2/` as flag defaults
and used uniformly across every render. The docs explicitly forbid
varying them per beat for related content; treat them as fixed.

## Per-knob rationale

### stability=0.4

The docs say 0.35–0.4 is the long-form sweet spot. Above ~0.7,
delivery becomes paradoxically monotone (the slider's name is
misleading; see `v2-quirks.md` §5). Below 0.3, prosody becomes erratic
and pronunciation gets unstable.

### similarity_boost=0.75

ElevenLabs' own default. Pushing higher amplifies source-recording
flaws when stacked with `use_speaker_boost=True`. Lower values let v2
drift away from the cloned voice over a long render.

### style=0.35

The docs recommend 0.3–0.5 for natural expression. v3's audio tags
play this role inline; v2 has only this single slider. Above ~0.6,
emphasis becomes erratic on long-form (sing-songy random stresses).

### use_speaker_boost=True

ElevenLabs' own default. Adds a small CPU cost per request but
materially helps the voice stay recognizable across a long render.

### language_code="en"

Mitigates v2's tendency to switch accent on individual proper nouns it
thinks belong to another language (`v2-quirks.md` §1). Without this,
the same script may pronounce "paella" with a Spanish accent, then
revert to English for the next sentence.

## When to tune

Default to never. The docs forbid per-beat variance. If a render comes
back consistently flat or consistently overwrought across an entire
script (not just one passage), consider tuning, but:

1. **Test on a 30-second slice first.** Re-rendering a full 5-min script
   to test a tuning change burns ~150 credits per attempt. A
   30-second slice burns ~15.
2. **A/B against the default.** Render the same slice with the default
   settings and the candidate settings. Compare side-by-side.
3. **Change one knob at a time.** If you change `stability` and `style`
   in the same test, you can't tell which knob did what.
4. **Never tune per-beat.** Even if it sounds tempting. The docs say
   "identical parameter settings… across related content." Render seams
   become audible if you don't.

## When the recipe stops working

If a render sounds wrong despite default settings, the issue is almost
never the voice settings. In order of likelihood:

1. **Source script issue** — re-read the affected passage aloud. Does
   it have a TTS-hostile construction (long parenthetical, weird
   number, homograph)? Fix the prose; see `script-writer/reference/tts-gotchas.md`.
2. **Voice issue** — is the voice clone good for long-form? Some IVCs
   sound great for 10 seconds and degrade over a minute. Try a
   different voice on the same script.
3. **Language drift** — did v2 accent-switch on a specific word?
   Mitigation in `v2-quirks.md` §1.
4. **Then** consider voice settings.
```

- [ ] **Step 2: Commit the skill**

```bash
git add .claude/skills/voiceover-elevenlabs-v2/
git commit -m "$(cat <<'EOF'
feat(skill): add voiceover-elevenlabs-v2 skill + reference docs

SKILL.md, reference/v2-quirks.md (8 engine landmines), and
reference/voice-settings.md (the recommended recipe + rationale).
Annotation taxonomy is light (ALL-CAPS anchors + SSML breaks; no audio
tags — v2 doesn't support them). Per-beat voice settings are forbidden
per docs.

Spec §7, §8.
EOF
)"
```

---

## Phase 5 — CLAUDE.md + script-writer hand-off

### Task 19: Update CLAUDE.md to declare v2 the project default

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Edit the voiceover paragraph**

Use the `Edit` tool:

`old_string`:
```
For voiceover generation in this project, use `voiceover-elevenlabs` (ElevenLabs
v3 + Scribe v2), not `hyperframes-media tts` (Kokoro). The Kokoro path stays
parallel and untouched for any non-v3 use case.
```

`new_string`:
```
For voiceover generation in this project, default to `voiceover-elevenlabs-v2`
(ElevenLabs Multilingual v2 + Scribe v2). It's the long-form stability champion
(per the official models page) and matches the project's plain-prose house
style. Use `voiceover-elevenlabs-v3` only when a video genuinely needs inline
audio tags for per-beat emotional shifts. The `hyperframes-media tts` (Kokoro)
path stays parallel and untouched for any non-ElevenLabs use case.
```

- [ ] **Step 2: Verify the edit**

Run: `grep -A 6 "For voiceover generation" CLAUDE.md`
Expected: shows the new paragraph mentioning v2 as default and v3 as opt-in.

(No commit yet — bundle with Task 20.)

---

### Task 20: Update the script-writer hand-off prompt + commit

**Files:**
- Modify: `.claude/skills/script-writer/SKILL.md`

- [ ] **Step 1: Edit Step 6's hand-off prompt**

Use the `Edit` tool:

`old_string`:
```
Once `script.md`, `outline.md`, and `anchors.txt` are written and approved, ask the user: *"Script is locked. Want me to generate the voiceover with ElevenLabs v3 now? (invokes the `voiceover-elevenlabs` skill)"* If yes, hand off to that skill — it produces both `audio/voiceover.mp3` and `transcript.json` in one run. If no, tell the user the next step is theirs (`uv run --project ../../tools/voiceover-elevenlabs voiceover-elevenlabs voiceover.txt`), then run `narration-map` with `anchors.txt`. This skill stops at `script.md`.
```

`new_string`:
```
Once `script.md`, `outline.md`, and `anchors.txt` are written and approved, ask the user: *"Script is locked. Want me to generate the voiceover with ElevenLabs v2 now? (invokes the `voiceover-elevenlabs-v2` skill — long-form stable, our project default. Pass `with v3` if you need the audio-tag path instead.)"* If the user replies affirmatively, hand off to `voiceover-elevenlabs-v2`. If they reply `with v3`, hand off to `voiceover-elevenlabs-v3` instead. Both skills produce `audio/voiceover.mp3` and `transcript.json` in one run. If the user declines both, tell them the next step is theirs (`uv run --project ../../tools/voiceover-elevenlabs-v2 voiceover-elevenlabs-v2 voiceover.txt`), then run `narration-map` with `anchors.txt`. This skill stops at `script.md`.
```

- [ ] **Step 2: Verify the edit**

Run: `grep -B 1 -A 8 "Script is locked" .claude/skills/script-writer/SKILL.md`
Expected: shows the new prompt mentioning both v2 and v3 paths.

- [ ] **Step 3: Commit both changes together**

```bash
git add CLAUDE.md .claude/skills/script-writer/SKILL.md
git commit -m "$(cat <<'EOF'
feat: declare voiceover-elevenlabs-v2 the project default

CLAUDE.md now lists v2 as the default for YouTube videos and v3 as the
opt-in path for content that needs inline audio tags. The script-writer
Step 6 hand-off prompt offers v2 by default and accepts 'with v3' to
route to the v3 skill instead.

These two updates land together so the docs and the actual skill flow
stay consistent.

Spec §9.
EOF
)"
```

---

## Phase 6 — First real render verification

### Task 21: Verification checklist (manual / user-driven)

**Files:**
- No file changes; this is a verification step.

The implementation is complete. This task is a manual verification the user runs before declaring the work done.

- [ ] **Step 1: Pick a target video folder**

The inaugural `videos/why-text-is-hard-2026-05-07/` is the natural candidate. Verify the prerequisites:

```bash
ls videos/why-text-is-hard-2026-05-07/
```

Expected: at least `script.md` and ideally `anchors.txt`. If `script.md` is missing, this verification can't run — pick a different folder.

- [ ] **Step 2: Invoke the v2 skill**

Run the skill end-to-end against the chosen folder (use the Claude `Skill` tool to invoke `voiceover-elevenlabs-v2`, or manually drive the flow). The skill will:

1. Read `script.md` + `anchors.txt`.
2. Produce `voiceover.txt` with light annotations.
3. Show the hard checkpoint with cost estimate.
4. On approval, call the v2 tool.
5. Produce `audio/voiceover.mp3` + `transcript.json`.

- [ ] **Step 3: Verify outputs**

```bash
ls -lh videos/why-text-is-hard-2026-05-07/audio/voiceover.mp3 videos/why-text-is-hard-2026-05-07/transcript.json
python3 -c "import json; d=json.load(open('videos/why-text-is-hard-2026-05-07/transcript.json')); print('duration:', d['audio_duration_secs'], 'words:', len(d['words']))"
```

Expected:
- MP3 exists and is several MB (depending on script length).
- Transcript JSON parses, has `audio_duration_secs > 0`, has a non-empty `words` array.

- [ ] **Step 4: Verify cost estimator accuracy**

After the run, check the ElevenLabs dashboard for actual credit consumption. Compare to the dry-run estimate the tool printed. If the estimate is off by more than 20%, update `V2_CREDITS_PER_1K_CHARS` in `tools/voiceover-elevenlabs-v2/src/voiceover_elevenlabs_v2/cli.py` and commit.

- [ ] **Step 5: Listen to a 30-second slice**

Open `voiceover.mp3` in any audio player. Listen for:
- Voice consistency across the slice (no language switching).
- Natural pacing (the `<break>` tags landed where you wanted).
- Pronunciation of any anchor terms (do they sound right?).

If something sounds wrong, the issue is one of: (1) source script (rewrite per `tts-gotchas.md`), (2) voice clone quality, (3) language drift on a specific word. See `v2-quirks.md` for diagnosis.

- [ ] **Step 6: Done**

If steps 3-5 all pass, the implementation is verified end-to-end. Mark all plan tasks as complete.

---

## Self-review checklist (run after writing the plan)

- [x] Spec §1 (purpose) — covered by overall plan.
- [x] Spec §2 (scope) — in-scope items mapped to Phases 1-5; out-of-scope items not introduced.
- [x] Spec §3 (why v2 is default) — informational; no task needed.
- [x] Spec §4 (tts-gotchas pointer fix) — Task 9.
- [x] Spec §5 (rename surface area) — Tasks 1-8.
- [x] Spec §6 (v2 tool) — Tasks 10-15.
- [x] Spec §7 (v2 skill) — Tasks 16-18.
- [x] Spec §8 (reference files) — Tasks 17, 18.
- [x] Spec §9 (CLAUDE.md + hand-off) — Tasks 19, 20.
- [x] Spec §10 (testing strategy) — Tasks 11, 12, 13, 14 (TDD per module).
- [x] Spec §11 (sequencing) — Phases ordered to match.
- [x] Spec §12 (open questions) — cost estimator verification is Task 21 step 4.
- [x] Spec §13 (done condition) — Task 21 covers final verification.
- [x] Type/method consistency — `synthesize()`, `generate()`, `transcribe()`, `to_transcript()` signatures consistent across tasks.
- [x] No placeholders.
```
