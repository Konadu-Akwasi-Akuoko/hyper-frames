# Per-video project scoping

**Date:** 2026-05-07
**Status:** Approved (design phase)

## Problem

The repo currently treats itself as a single HyperFrames project: `index.html`,
`design.md`, `hyperframes.json`, `package.json`, source audio, and rendered output
all live at the root. The first video (`why-text-is-hard.mp4`) shipped this way.

The moment a second video is started, the root files get overwritten, the previous
piece becomes unreproducible, and the shared CLAUDE.md / `.claude/skills/` become
inseparable from a single video's source. We need a layout that lets the same repo
host many videos without collisions, while keeping shared concerns shared.

## Goal

Make this repo a **multi-video workspace**: each piece is a self-contained folder
under `videos/<slug>-<YYYY-MM-DD>/`, while the repo root keeps only shared concerns
(CLAUDE.md, README, `.claude/`, the `videos/` index, and `docs/`).

## Out of scope

- A `videos/_template/` skeleton folder. `npx hyperframes init` already scaffolds;
  maintaining a parallel template would just drift.
- A workspace-level `package.json` orchestrating all videos. Each video's own
  `package.json` runs independently. No monorepo tooling needed.
- Renaming `output/` inside a video folder. The standard HyperFrames mental model
  keeps `output/` for renders; we honor that per-video.
- Migrating `skills-lock.json` — it stays at the repo root since it pins shared
  skill versions.

## Naming convention

- **Slug:** kebab-case of the working title. ASCII only, no punctuation, no spaces.
  Pick a short, recognizable form (`why-text-is-hard`), not the full sentence
  (`why-is-rendering-text-so-complicated`).
- **Date:** `YYYY-MM-DD`, fixed at the moment the video folder is **scaffolded**
  (when work begins). Not the publish date. Stable, known up front, never edited
  after creation.
- **Full folder name:** `<slug>-<YYYY-MM-DD>` (e.g., `why-text-is-hard-2026-05-07`).

## Final layout

```
hyper-frames/
├── CLAUDE.md                  # shared rules across every video
├── README.md
├── skills-lock.json
├── docs/
│   └── superpowers/specs/     # design specs (this file lives here)
├── .claude/                   # shared skills & settings
└── videos/
    └── why-text-is-hard-2026-05-07/
        ├── index.html
        ├── design.md
        ├── hyperframes.json
        ├── package.json
        ├── compositions/      # created when first block is added
        ├── assets/             # created when first asset is added
        ├── audio/
        │   ├── why-is-rendering-text-so-complicated.mp3   # original (5:19)
        │   └── rendering-text-2min.mp3                     # trimmed cut used in render (2:00)
        ├── transcript.json    # ElevenLabs-shaped, supplied by user
        └── output/
            └── why-text-is-hard.mp4
```

### Per-folder contracts

- **`videos/<slug>-<date>/` (folder root)** — every HyperFrames CLI command runs
  from here. `hyperframes.json`, `package.json`, `index.html`, `design.md`, and
  `transcript.json` all live at this level.
- **`audio/`** — source voiceover(s). With ElevenLabs as the TTS source, this
  typically holds a single clean `.mp3`; the folder leaves room for a second take
  or a music bed later without restructuring.
- **`transcript.json`** — at the folder root, not nested under `audio/`. It is the
  timing source-of-truth for animations (see CLAUDE.md → "Transcript-as-timing-truth"),
  not an artifact of the audio.
- **`compositions/`** — multi-block compositions per `hyperframes.json`. Created on
  demand by `hyperframes add` or by hand when the first block is authored.
- **`assets/`** — fonts, images, anything referenced by compositions.
- **`output/`** — rendered artifacts only (`.mp4`, intermediate renders). Source
  files never live here.

## Migration of the existing piece

The current root files become the inaugural example of the convention by moving
into `videos/why-text-is-hard-2026-05-07/`:

| From (repo root)                                       | To (inside the video folder)                                |
| ------------------------------------------------------ | ----------------------------------------------------------- |
| `index.html`                                           | `index.html`                                                |
| `design.md`                                            | `design.md`                                                 |
| `hyperframes.json`                                     | `hyperframes.json`                                          |
| `package.json`                                         | `package.json`                                              |
| `Why is rendering text so complicated？.mp3`           | `audio/why-is-rendering-text-so-complicated.mp3` (renamed)  |
| `output/transcript.json`                               | `transcript.json` (promoted to folder root)                 |
| `output/rendering-text-2min.mp3`                       | `audio/rendering-text-2min.mp3`                             |
| `output/why-text-is-hard.mp4`                          | `output/why-text-is-hard.mp4`                               |

**Renames during migration:**

- The fullwidth `？` in the original audio filename is dropped; the file is
  kebab-cased to `why-is-rendering-text-so-complicated.mp3`. The fullwidth
  character is a copy-paste artifact from the original prompt and would cause
  shell-escaping pain later.

**After migration, the repo root contains:**

```
CLAUDE.md
README.md
skills-lock.json
.claude/
docs/
videos/
```

The original `output/` directory at the root is removed.

## CLAUDE.md additions

A new top-level section is added near the top of `CLAUDE.md`, replacing the
implicit "everything at root" assumption:

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
```

The existing sections (Authoring workflow, Transcript-as-timing-truth, Lint
loop, Composition structure, Video generation / no editorial chrome) are
unchanged in content but now apply **inside each video folder**, not at the
repo root.

## Behavioral changes for Claude

- **Always `cd` into the video folder** before running `hyperframes` CLI
  commands. Never run them from the repo root.
- **Read `design.md` per-video**, not as a shared design system. Each video
  evolves its own palette/type/motion within the project's house style.
- **Existing CLAUDE.md guidance** (transcript-as-timing-truth, lint loop, no
  editorial chrome, multi-block compositions) applies inside each video folder,
  unchanged.
- **Never edit files at the repo root** during video authoring — the only root
  files Claude should touch during a video are CLAUDE.md (when codifying new
  cross-video rules) and `docs/` (when writing specs).

## Acceptance criteria

1. `videos/why-text-is-hard-2026-05-07/` exists and contains all sources, audio,
   transcript, and rendered output for the first video.
2. The repo root contains only `CLAUDE.md`, `README.md`, `skills-lock.json`,
   `.claude/`, `docs/`, and `videos/`. No `index.html`, `design.md`,
   `hyperframes.json`, `package.json`, or `output/` at the root.
3. `cd videos/why-text-is-hard-2026-05-07 && npx hyperframes lint` succeeds.
4. `cd videos/why-text-is-hard-2026-05-07 && npx hyperframes inspect` succeeds.
5. CLAUDE.md contains the "Project layout — one repo, many videos" section,
   placed before the "Authoring workflow" section so it sets context first.
6. The migration preserves the renderability of the existing video — running
   `npx hyperframes render` from inside the migrated folder produces the same
   output.

## Risks

- **Asset path references in `index.html`.** If the existing `index.html`
  references audio or assets via relative paths, those paths may need updating
  after the move. Verification: open `index.html`, grep for any path that
  resolves outside the new folder, fix to be folder-relative.
- **`hyperframes.json` registry paths.** The current `hyperframes.json` uses
  `compositions`, `compositions/components`, `assets` — all relative to the
  config file's directory, so they should "just work" after the move. Confirm
  during implementation.
- **Skill expectations.** The `hyperframes-cli` and `hyperframes-registry`
  skills assume commands run from the project root (where `hyperframes.json`
  lives). Since each video folder is its own project root, this is satisfied
  — but Claude must remember to `cd` first.
