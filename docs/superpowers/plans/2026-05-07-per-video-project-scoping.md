# Per-Video Project Scoping Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the existing `why-text-is-hard` video sources, audio, transcript, and rendered output from the repo root into `videos/why-text-is-hard-2026-05-07/`, then update CLAUDE.md so future videos follow the same convention.

**Architecture:** Pure file relocation + one CLAUDE.md edit + one in-file path patch in `index.html`. The repo root becomes shared concerns only (`CLAUDE.md`, `README.md`, `.claude/`, `docs/`, `videos/`, `skills-lock.json`). Each video lives self-contained under `videos/<slug>-<YYYY-MM-DD>/`.

**Tech Stack:** HyperFrames CLI (`npx hyperframes`), shell. No git in this repo (verified via `git rev-parse` returning fatal). No commit steps; verification is per-task `lint`/`inspect` runs.

**Spec:** `docs/superpowers/specs/2026-05-07-per-video-project-scoping-design.md`

**Pre-flight findings (from spec self-review):**

- `index.html:568` contains `src="output/rendering-text-2min.mp3"` — must be patched to `src="audio/rendering-text-2min.mp3"` after the audio file moves.
- `hyperframes.json`, `design.md`, `package.json` contain no local path references that break under relocation.
- No `.gitignore` in the repo; no git history to preserve.

---

## File Structure (after migration)

**Created:**

- `videos/why-text-is-hard-2026-05-07/` (folder root)
- `videos/why-text-is-hard-2026-05-07/audio/`
- `videos/why-text-is-hard-2026-05-07/output/`

**Moved (from → to):**

| From                                          | To                                                                |
| --------------------------------------------- | ----------------------------------------------------------------- |
| `index.html`                                  | `videos/why-text-is-hard-2026-05-07/index.html`                   |
| `design.md`                                   | `videos/why-text-is-hard-2026-05-07/design.md`                    |
| `hyperframes.json`                            | `videos/why-text-is-hard-2026-05-07/hyperframes.json`             |
| `package.json`                                | `videos/why-text-is-hard-2026-05-07/package.json`                 |
| `Why is rendering text so complicated？.mp3`  | `videos/why-text-is-hard-2026-05-07/audio/why-is-rendering-text-so-complicated.mp3` |
| `output/rendering-text-2min.mp3`              | `videos/why-text-is-hard-2026-05-07/audio/rendering-text-2min.mp3` |
| `output/transcript.json`                      | `videos/why-text-is-hard-2026-05-07/transcript.json`              |
| `output/why-text-is-hard.mp4`                 | `videos/why-text-is-hard-2026-05-07/output/why-text-is-hard.mp4`  |

**Modified:**

- `videos/why-text-is-hard-2026-05-07/index.html` — line 568 audio src patched
- `CLAUDE.md` — new top-level "Project layout" section added before "Authoring workflow"

**Deleted:**

- `output/` (the original root directory, after its contents are moved)

---

### Task 1: Pre-flight verification

**Files:**
- Read-only checks against repo root

- [ ] **Step 1: Confirm the destination folder does not yet exist**

Run: `test ! -d videos/why-text-is-hard-2026-05-07 && echo OK || echo EXISTS`
Expected: `OK`

If `EXISTS`, stop and ask the user — the destination is occupied.

- [ ] **Step 2: Confirm all source files are present at the expected paths**

Run:

```bash
for f in \
  "index.html" \
  "design.md" \
  "hyperframes.json" \
  "package.json" \
  "Why is rendering text so complicated？.mp3" \
  "output/rendering-text-2min.mp3" \
  "output/transcript.json" \
  "output/why-text-is-hard.mp4"; do
  test -f "$f" && echo "OK   $f" || echo "MISS $f"
done
```

Expected: every line starts with `OK`. If any `MISS`, stop and reconcile with the user before moving on.

- [ ] **Step 3: Re-confirm the only local path reference inside `index.html` is the one we already know about**

Run:

```bash
grep -nE '(src=|href=|url\()' index.html \
  | grep -vE 'cdn\.jsdelivr|googleapis|fonts\.gstatic|https?://'
```

Expected: exactly one match — `568:        src="output/rendering-text-2min.mp3"></audio>`. If extra matches appear, treat each as a path that may need patching after the move and surface them before proceeding.

---

### Task 2: Create the destination folder skeleton

**Files:**
- Create: `videos/why-text-is-hard-2026-05-07/`
- Create: `videos/why-text-is-hard-2026-05-07/audio/`
- Create: `videos/why-text-is-hard-2026-05-07/output/`

- [ ] **Step 1: Create the three directories in one call**

Run:

```bash
mkdir -p videos/why-text-is-hard-2026-05-07/audio \
         videos/why-text-is-hard-2026-05-07/output
```

- [ ] **Step 2: Verify the structure**

Run: `ls -la videos/why-text-is-hard-2026-05-07/`
Expected: shows `audio/` and `output/` subdirectories, nothing else.

---

### Task 3: Move project source files into the folder root

**Files:**
- Move: `index.html` → `videos/why-text-is-hard-2026-05-07/index.html`
- Move: `design.md` → `videos/why-text-is-hard-2026-05-07/design.md`
- Move: `hyperframes.json` → `videos/why-text-is-hard-2026-05-07/hyperframes.json`
- Move: `package.json` → `videos/why-text-is-hard-2026-05-07/package.json`

- [ ] **Step 1: Move all four files**

Run:

```bash
mv index.html design.md hyperframes.json package.json \
   videos/why-text-is-hard-2026-05-07/
```

- [ ] **Step 2: Verify the move**

Run:

```bash
ls videos/why-text-is-hard-2026-05-07/
ls index.html design.md hyperframes.json package.json 2>&1 | head
```

Expected: first command lists the four files (plus `audio/`, `output/`); second command outputs `ls: ...: No such file or directory` for each — they are no longer at the root.

---

### Task 4: Move and rename the source audio files

**Files:**
- Move + rename: `Why is rendering text so complicated？.mp3` → `videos/why-text-is-hard-2026-05-07/audio/why-is-rendering-text-so-complicated.mp3`
- Move: `output/rendering-text-2min.mp3` → `videos/why-text-is-hard-2026-05-07/audio/rendering-text-2min.mp3`

- [ ] **Step 1: Move the original take with kebab-case rename**

Run:

```bash
mv "Why is rendering text so complicated？.mp3" \
   videos/why-text-is-hard-2026-05-07/audio/why-is-rendering-text-so-complicated.mp3
```

The fullwidth `？` is dropped during this rename; the file is kebab-cased.

- [ ] **Step 2: Move the trimmed cut**

Run:

```bash
mv output/rendering-text-2min.mp3 \
   videos/why-text-is-hard-2026-05-07/audio/rendering-text-2min.mp3
```

- [ ] **Step 3: Verify both files landed**

Run: `ls videos/why-text-is-hard-2026-05-07/audio/`
Expected:

```
rendering-text-2min.mp3
why-is-rendering-text-so-complicated.mp3
```

---

### Task 5: Move the transcript and rendered output

**Files:**
- Move: `output/transcript.json` → `videos/why-text-is-hard-2026-05-07/transcript.json`
- Move: `output/why-text-is-hard.mp4` → `videos/why-text-is-hard-2026-05-07/output/why-text-is-hard.mp4`

- [ ] **Step 1: Promote the transcript to the folder root**

Run:

```bash
mv output/transcript.json videos/why-text-is-hard-2026-05-07/transcript.json
```

The transcript is the timing source-of-truth, not an artifact, so it lives at the folder root rather than under `output/`.

- [ ] **Step 2: Move the rendered video into the per-video `output/`**

Run:

```bash
mv output/why-text-is-hard.mp4 \
   videos/why-text-is-hard-2026-05-07/output/why-text-is-hard.mp4
```

- [ ] **Step 3: Verify**

Run:

```bash
ls videos/why-text-is-hard-2026-05-07/
ls videos/why-text-is-hard-2026-05-07/output/
```

Expected: folder root shows `index.html design.md hyperframes.json package.json transcript.json audio/ output/`; `output/` shows `why-text-is-hard.mp4`.

---

### Task 6: Remove the now-empty root `output/` directory

**Files:**
- Delete: `output/` (root-level)

- [ ] **Step 1: Confirm the directory is empty before deleting**

Run: `ls -A output/`
Expected: no output (the directory is empty).

If anything is listed, **stop**. The contents need to be inspected and either moved into the video folder or surfaced to the user before deletion.

- [ ] **Step 2: Remove the empty directory**

Run: `rmdir output`

- [ ] **Step 3: Verify the repo root**

Run: `ls -1`
Expected (order may vary):

```
CLAUDE.md
README.md
docs
skills-lock.json
videos
```

Plus any dotfiles (`.claude/` shows under `ls -a`). No `index.html`, `design.md`, `hyperframes.json`, `package.json`, `output/`, or stray `.mp3` at the root.

---

### Task 7: Patch the audio path inside `index.html`

**Files:**
- Modify: `videos/why-text-is-hard-2026-05-07/index.html:568`

- [ ] **Step 1: Apply the path patch**

In `videos/why-text-is-hard-2026-05-07/index.html`, replace the audio source path. The exact substitution:

- Old: `src="output/rendering-text-2min.mp3"`
- New: `src="audio/rendering-text-2min.mp3"`

The audio file moved from the sibling `output/` directory to a sibling `audio/` directory; the `index.html` is now in the same folder as both, so the relative path simply swaps prefixes.

- [ ] **Step 2: Verify the patch**

Run:

```bash
grep -n 'rendering-text-2min.mp3' videos/why-text-is-hard-2026-05-07/index.html
```

Expected: exactly one match, showing `src="audio/rendering-text-2min.mp3"`. No remaining reference to `output/rendering-text-2min.mp3`.

- [ ] **Step 3: Sanity-check there are no other stale `output/` references**

Run:

```bash
grep -nE 'src=|href=|url\(' videos/why-text-is-hard-2026-05-07/index.html \
  | grep -vE 'cdn\.jsdelivr|googleapis|fonts\.gstatic|https?://'
```

Expected: only the patched `src="audio/rendering-text-2min.mp3"` line.

---

### Task 8: Verify the migrated project lints and inspects cleanly

**Files:** none modified — verification only.

- [ ] **Step 1: Run `hyperframes lint` from inside the video folder**

Run:

```bash
cd videos/why-text-is-hard-2026-05-07 && npx hyperframes lint
```

Expected: exit code 0, no errors. Warnings are acceptable but should be reviewed.

If lint fails, capture the output and stop — do not proceed to CLAUDE.md edits until the migration is verified clean. Failure modes to triage:

- Missing asset → a path inside `index.html` other than the one we patched is also stale; grep again.
- Schema error in `hyperframes.json` → unlikely, paths are folder-relative.

- [ ] **Step 2: Run `hyperframes inspect` from inside the video folder**

Run:

```bash
cd videos/why-text-is-hard-2026-05-07 && npx hyperframes inspect
```

Expected: exit code 0; the inspect output should describe the composition tree without reporting unresolved assets.

- [ ] **Step 3: (Optional but recommended) Smoke-test the preview**

Run:

```bash
cd videos/why-text-is-hard-2026-05-07 && npx hyperframes preview
```

Expected: preview launches, audio plays from the new `audio/rendering-text-2min.mp3` location, animations sync as before. Exit the preview (Ctrl-C) once verified.

This step catches the case where lint passes but the audio element silently fails to load at runtime.

---

### Task 9: Add the "Project layout" section to CLAUDE.md

**Files:**
- Modify: `CLAUDE.md` (insert new section before the existing "Authoring workflow" section)

- [ ] **Step 1: Insert the new section**

In `CLAUDE.md`, immediately after the title `# hyper-frames — project notes` (line 1) and before `## Authoring workflow`, insert this block:

```markdown
## Project layout — one repo, many videos

Every video is a self-contained folder under `videos/<slug>-<YYYY-MM-DD>/`, with
its own `index.html`, `design.md`, `hyperframes.json`, `package.json`,
`compositions/`, `assets/`, source audio, transcript, and rendered output.
Never author HyperFrames files at the repo root — the root is reserved for
shared concerns (CLAUDE.md, README, .claude/, docs/, the videos/ index).

When starting a new video:

1. Pick a kebab-case slug from the working title (short and recognizable, not
   the full sentence).
2. Create `videos/<slug>-<YYYY-MM-DD>/` (date = today, when work begins).
3. Run `npx hyperframes init` from inside that folder.
4. Drop the source audio in `audio/` and the user-supplied transcript at the
   folder root as `transcript.json`.
5. All subsequent CLI commands (`lint`, `inspect`, `preview`, `render`) run
   from inside that folder, never from the repo root.

The first video, `videos/why-text-is-hard-2026-05-07/`, is the canonical example
of this layout.

```

The trailing blank line separates the new section from the existing `## Authoring workflow` header.

- [ ] **Step 2: Verify the file structure**

Run:

```bash
grep -nE '^## ' CLAUDE.md
```

Expected: `## Project layout — one repo, many videos` appears as the first `##` heading, followed in order by `## Authoring workflow`, `## Composition structure`, `## Video generation`.

- [ ] **Step 3: Verify CLAUDE.md still reads cleanly end-to-end**

Read the full file. The new section should sit cleanly above "Authoring workflow", and the existing transcript/lint/composition guidance should still make sense in context — those sections now describe what happens **inside a video folder**, which the new section establishes.

---

### Task 10: Final acceptance check

**Files:** none modified — verification only.

- [ ] **Step 1: Repo root contents match the spec**

Run: `ls -1`
Expected exactly (order may vary):

```
CLAUDE.md
README.md
docs
skills-lock.json
videos
```

Plus `.claude/` under `ls -A`. Nothing else.

- [ ] **Step 2: Video folder contents match the spec**

Run: `ls -1 videos/why-text-is-hard-2026-05-07/`
Expected:

```
audio
design.md
hyperframes.json
index.html
output
package.json
transcript.json
```

Run: `ls -1 videos/why-text-is-hard-2026-05-07/audio/`
Expected:

```
rendering-text-2min.mp3
why-is-rendering-text-so-complicated.mp3
```

Run: `ls -1 videos/why-text-is-hard-2026-05-07/output/`
Expected:

```
why-text-is-hard.mp4
```

- [ ] **Step 3: Lint + inspect still pass**

Run:

```bash
cd videos/why-text-is-hard-2026-05-07 && npx hyperframes lint && npx hyperframes inspect
```

Expected: both exit 0. This re-runs Task 8's checks as a final gate after the CLAUDE.md edit (which can't affect them, but the gate is cheap).

- [ ] **Step 4: Hand back to the user**

Report the migration as complete. Surface any non-fatal lint warnings encountered during Task 8 so the user can decide whether to address them now or in a follow-up.

---

## Self-Review Notes

**Spec coverage:**

- Goal: layout under `videos/<slug>-<date>/` → Tasks 2, 3, 4, 5
- Naming convention (slug, date) → captured in CLAUDE.md edit (Task 9); the inaugural folder name is hard-coded in this plan
- Migration table (8 file moves) → Tasks 3, 4, 5
- Renames (drop fullwidth `？`, kebab-case) → Task 4 step 1
- Removal of root `output/` → Task 6
- CLAUDE.md addition → Task 9
- Acceptance criteria 1–6 (folder exists, root cleared, lint passes, inspect passes, CLAUDE.md updated, render reproducibility) → covered by Tasks 8 and 10
- Risk: asset path inside `index.html` → Task 1 step 3 (detection) + Task 7 (fix)
- Risk: `hyperframes.json` registry paths → confirmed folder-relative during pre-flight; no task needed

**Placeholder scan:** None. Every step has the exact command or exact text to insert.

**Type consistency:** N/A — no code interfaces. File paths are consistent across all tasks (`videos/why-text-is-hard-2026-05-07/...`).

**Skipped:** Git commits (no git repo). If the user initializes git later, each task would naturally become a commit boundary.
