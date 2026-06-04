# HyperFrames video pipeline

End-to-end pipeline used to produce `videos/how-does-captchas-work-2026-05-10/`. Each stage lists: what it produces, what to type, the captchas-video example, and pitfalls.

> **Companion read:** [composition-spec-over-restriction.md](./composition-spec-over-restriction.md) — why stages 5 and 6 stay deliberately lightweight.

## Pipeline at a glance

```
0. Pick topic + slug
        ↓
1. /youtube-seo-research          → seo/research.json
        ↓
2. /script-writer                 → outline.md, script.md
        ↓
3a. /transcribe-and-plan-cuts     → transcript.json, cuts.json
    (record your own voice —        (then edit in tools/audio-editor →
     DEFAULT)                        render audio/voiceover.mp3)
        — or —
3b. /voiceover-elevenlabs-v2      → audio/voiceover.mp3, transcript.json,
    (TTS — alternative)             voiceover.txt
        ↓
4. write anchors.txt + run narration-map tool
                                  → narration-map.json
        ↓
5. Write a slim design.md         → design.md (≤ ~50 lines)
        ↓
6. /hyperframes                   → index.html (+ compositions/*.html)
        ↓
7. preview + lint iteration       → fix issues
        ↓
8. /thumbnail-creator             → thumbnail-a/b/c.png
        ↓
9. render                         → output/*.mp4
        ↓
10. publish                       → shareable link
```

Stages 1–4 are sequential and one-shot (Stage 3 is one of two paths — see below). Stage 6 is the iterative authoring loop. Stage 8 (thumbnails) can run any time after stage 2.

---

## Stage 0 — Pick topic + slug

**What happens:** decide working title, pick a kebab-case slug. The `script-writer` skill can scaffold the folder for you in stage 2, so no manual folder creation is needed.

**What to type:** nothing yet — just have the title in your head.

**Captchas example:**
- Working title: *"How does a CAPTCHA actually work?"*
- Slug: `how-does-captchas-work`
- Folder (created at stage 2): `videos/how-does-captchas-work-2026-05-10/`

**Pitfalls:**
- Don't run `npx hyperframes init` manually at the repo root — `script-writer` handles the folder + scaffold inside `videos/<slug>-<date>/`.

---

## Stage 1 — YouTube SEO research

**Skill:** `/youtube-seo-research`

**What it produces:** `seo/research.json` — searchable nouns, demand phrases, saturation warnings, hook-shape data. Backed by yt-dlp + YouTube autocomplete; no API key, ~25s.

**What to type:**
```
/youtube-seo-research

Research SEO for a video about how CAPTCHAs actually work — the
behavioral-scoring story, the three generations, why the checkbox isn't
the test.
```

**Captchas example:** produced `videos/how-does-captchas-work-2026-05-10/seo/research.json` at 05:53. Used by `/script-writer` at the outline step and by `/thumbnail-creator` at the paired-title step.

**Pitfalls:**
- This is the only stage that benefits from being explicit about topic phrasing. Vague topic = generic research output. Give it the *angle*, not just the noun.

---

## Stage 2 — Script writing

**Skill:** `/script-writer`

**What it produces:**
- `outline.md` — beat breakdown (9-beat iceberg arc: mundane action revealed as unsuspected depth)
- `script.md` — final TTS-ready script in the house style

Also scaffolds the video folder if it doesn't exist yet, and runs `npx hyperframes init` inside it.

**What to type:**
```
/script-writer

Write a script about how CAPTCHAs actually work. Topic angle:
the test you think you're taking is not the test you're actually
taking — behavioral signals, the three generations of CAPTCHAs,
each broken in turn, and the GPT-4 / TaskRabbit incident as climax.
```

**Captchas example:**
- `outline.md` at 05:54 (1 minute after seo/research.json — skill auto-consumed the research)
- `script.md` at 06:28 (~35 minutes of outline → script iteration)

**Pitfalls:**
- The skill reads `seo/research.json` at the outline step. If `seo/` is missing it will offer to invoke `/youtube-seo-research` for you — accept and re-run.
- Don't impersonate any creator. The skill encodes a writing **style**, not a person.
- Review `outline.md` and push back if the beats feel generic before moving to `script.md` — the script is much harder to course-correct than the outline.

---

## Stage 3 — Voiceover + transcript

Two paths. **Recording your own voice is the default.** TTS is for when you need clean repeatable narration without a mic, faster iteration, or multi-language coverage.

### Stage 3a — Record your voice (DEFAULT)

**Skill:** `/transcribe-and-plan-cuts`
**Editor:** `tools/audio-editor` (Bun + Vite, runs on `:5173`)

**What it produces:**
- `audio/raw.mp3` — your recording (user-provided; the skill expects it here)
- `transcript.json` — word-level Scribe v2 transcript of the raw recording
- `cuts.json` — first-pass cut plan in the audio-editor schema (the `audio-cut-decider` agent writes this)

**What to type:**

1. Drop the recording at `<video-dir>/audio/raw.mp3`.
2. Invoke the skill:
   ```
   /transcribe-and-plan-cuts
   ```
3. Approve the cost checkpoint (ffprobe shows duration; Scribe is ~$0.40/hour).
4. Open `http://localhost:5173/#/edit/<slug>-<date>` (`bun dev` from `tools/audio-editor/` must already be running). Scrub the proposed cuts, drag region edges to refine, delete cuts you disagree with, add ones the agent missed. Click **Save cuts**.
5. Render the final `audio/voiceover.mp3` from `audio/raw.mp3` + `cuts.json`. **Phase A leaves this manual** — use ffmpeg's concat demuxer to splice the kept segments. A future `apply-recording-cuts` skill will automate this.

**Pitfalls:**
- The skill never modifies `audio/raw.mp3`. That's the source of truth — re-runs are non-destructive on the audio.
- `bun dev` for the audio-editor must already be running (see `tools/audio-editor/CLAUDE.md`). The skill doesn't start it.
- Re-running the skill clobbers `cuts.json`, which destroys any manual edits the editor has saved. The skill warns at the checkpoint when an existing `cuts.json` is about to be overwritten — heed it.
- Audio events in the transcript (`[cough]`, `[breath]`, `[mouth_noise]`) are first-class — the cut-decider uses them. The audio-editor's transcript schema was extended in 2026-05-19 to accept `audio_event` rows; pre-patch loads will Zod-fail.

### Stage 3b — TTS (alternative)

**Skill:** `/voiceover-elevenlabs-v2` (project default for the TTS path)

When to use `v3` instead: only when the video genuinely needs **inline audio tags for per-beat emotional shifts**. Long-form prose videos = v2.

**What it produces:**
- `audio/voiceover.mp3` — narration audio
- `transcript.json` — word-level transcript from Scribe v2 (this is the timing source of truth)
- `voiceover.txt` — the annotated input (ALL-CAPS anchors + SSML `<break>` tags) saved for reference

**What to type:**
```
/voiceover-elevenlabs-v2

Voice script.md.
```

The skill runs a **hard checkpoint** for annotation review before spending API credits. Approve the annotated `voiceover.txt`, then it generates the audio + transcript.

**Captchas example (TTS path):**
- `audio/voiceover.mp3` at 06:50 (6:27 runtime)
- `transcript.json` at 06:51
- `voiceover.txt` at 12:45 (overwritten later — that's fine)

**Pitfalls:**
- The annotation checkpoint matters. Read the annotated text and verify the ALL-CAPS anchors are on the words you actually want emphasized.
- After this stage runs, the audio is committed; re-generating costs credits.

---

## Stage 4 — Anchors + narration map

**Tool:** `tools/narration-map/` (Python CLI, run via `uv`)

**What it produces:** `narration-map.json` — anchor-word start times, pause windows, scene-boundary candidates, and the top-N longest-duration words. Keyed off `transcript.json`.

**What to type:**

1. **Write `anchors.txt`** — list of phrases (one per line, blank lines + `# Beat N` comments allowed) you want timestamped. Pull them from `script.md`'s emphatic words and proper nouns.

2. **Run the tool from inside the video folder:**
   ```bash
   uv run --project ../../tools/narration-map narration-map \
     transcript.json --anchors anchors.txt
   ```

Writes `narration-map.json` next to `transcript.json`.

**Captchas example:**
- `anchors.txt` at 06:51 (excerpt):
  ```
  # Beat 1 — Open
  I'm not a robot
  checkbox

  # Beat 2 — Subversion
  the test was never the checkbox
  the click was just the receipt
  ```
- `narration-map.json` at 06:51 (35 KB — anchor starts, pauses > 400ms, scene boundaries after `.!?`, top-N longest words)

**Pitfalls:**
- Don't grep `transcript.json` by hand for timestamps in stage 6. That's what `narration-map.json` is for. (Project CLAUDE.md flags hand-rolled `python3 -c` searches as a code smell.)
- If anchors don't match transcript words exactly, the tool skips them silently. Sanity-check the output.

---

## Stage 5 — Design.md (slim!)

**What it produces:** `design.md` — palette, typography, motion, don'ts. **Target: ≤ ~50 lines.**

**What to type:** either copy the maiden video's `design.md` and tweak palette to taste, or write a new one. Either way, keep it short.

**Minimum viable shape:**

```markdown
# Design — <Video title>

<One-paragraph mood description.>

## Palette
| Token | Value | Use |
| ... |

## Typography
- Sans (display / body): ...
- Mono (technical): ...

## Motion
- Crossfade transitions ...
- Stagger ≤ 500ms ...
- Vary eases ...

## Don'ts
- ...
```

**Captchas example:** `design.md` at 20:48, 43 lines, copied byte-for-byte from `videos/why-text-is-hard-2026-05-07/design.md`. The earlier 141-line version (with prescribed atmosphere layers, transition table, and component recipes) was the over-restriction failure documented in [composition-spec-over-restriction.md](./composition-spec-over-restriction.md).

**Pitfalls:**
- Resist the urge to pre-specify atmosphere layers, transition tables, or component recipes. Those close the lexicon and pre-empt invention.
- If the design picker (visual chooser at `.hyperframes/pick-design.html`) emits a long file, trim it before stage 6.
- Don't create `.hyperframes/expanded-prompt.md`. Stage 6 reads `design.md` + `script.md` + `transcript.json` directly.

---

## Stage 6 — HyperFrames composition (the authoring loop)

**Skill:** `/hyperframes`

**What it produces:** `index.html` and (optionally) `compositions/*.html` sub-compositions.

**What to type:**

```
/hyperframes

Build the composition using:
- script.md (narrative)
- transcript.json (timing source of truth — see narration-map.json
  for anchor starts, pause windows, scene boundaries)
- design.md (palette + tone)

Treat `videos/why-text-is-hard-2026-05-07/index.html` as the
QUALITY BAR. Invent worldbuilding (real-looking reCAPTCHA on a
real-looking webpage, real-looking research paper, real-looking
chat log) — NOT generic CSS primitives.

Multi-composition split is fine, but commit to building every scene
in this session. Do not leave PLACEHOLDER / TO BE BUILT stubs.

Surface the studio URL after authoring.
```

**The two sentences that do most of the work:**

1. **"Treat `videos/why-text-is-hard-2026-05-07/index.html` as the QUALITY BAR."** — anchors the model to a known-good reference so Scene 1 sets the right bar.
2. **"Invent worldbuilding — NOT generic CSS primitives."** — explicitly grants permission to leap from the script's vivid details to real-looking artifacts.

**Captchas example:** 11 scenes built in a single session, ranging from a real-looking reCAPTCHA widget (`scene-01-open.html`) through bold kinetic typography (`scene-02-subversion.html`) to a stat callout closer (`scene-11-closer.html`). Files at 22:35.

**Pitfalls:** see [composition-spec-over-restriction.md](./composition-spec-over-restriction.md) — every one of them is something the heavier earlier attempt did wrong.

---

## Stage 7 — Preview + lint iteration

**Commands** (run from inside the video folder):

```bash
npx hyperframes preview    # studio at http://localhost:<port>/#project/<name>
npm run check              # lint + validate + inspect
npx hyperframes lint --verbose
```

**What to do:**
- Open the studio URL, scrub the timeline, watch each scene at its hold frame.
- Treat lint findings as blocking. Fix everything.
- For UI / visual issues, inspect a scene at its t=mid frame, not t=0 (entrances haven't landed at 0).

**Captchas example:** the `.thumbnails/` folder contains JPGs at `<scene>_2.00.jpg` and at the timeline's scene-start times (`index.html_167.04__sc6.jpg`, etc.) — that's the preview thumbnail cache, useful for quick visual scan without booting the studio.

**Pitfalls:**
- Don't skip preview. After any composition edit, project CLAUDE.md requires running `npx hyperframes preview` and surfacing the studio URL.
- If lint warns about something that "looks fine in preview," fix the lint finding anyway. Those have caught shippable-looking bugs.

---

## Stage 8 — Thumbnails

**Skill:** `/thumbnail-creator`

**What it produces:**
- `thumbnail-a.png` / `thumbnail-b.png` / `thumbnail-c.png` (1280×720 YouTube)
- or `thumbnail-vertical-a/b/c.png` (1080×1920 Shorts/TikTok)

**What to type:**
```
/thumbnail-creator

Generate three thumbnail variants for this video.
```

For vertical/Shorts: add the word "vertical" (or "shorts", "tiktok", "9:16") to the prompt.

**Captchas example:** thumbnails not yet generated for the captchas video at time of writing. The maiden video shows the expected output shape: three horizontal + three vertical variants in the video folder root.

**Pitfalls:**
- The skill reads `seo/research.json` at the paired-title step. If `seo/` is missing it will offer to invoke `/youtube-seo-research` — accept.
- Don't run this before the script is approved — the thumbnail title needs to match the final script's framing.

---

## Stage 9 — Render

**Commands:**
```bash
npm run render                          # via package.json script
# or
npx hyperframes render                  # direct
```

**What it produces:** MP4(s) under `output/`.

**Pitfalls:**
- Render is slow. Run it once after lint passes and preview looks right, not during iteration.
- If you re-rendered after edits, delete the old MP4 first to avoid confusion.

---

## Stage 10 — Publish

**Commands:**
```bash
npm run publish     # or: npx hyperframes publish
```

**What it produces:** a shareable link.

**What to do after:** download the rendered MP4 to your local edit folder, upload to YouTube with the thumbnail variant chosen at stage 8.

---

## Quick-reference: the captchas video, by stage

| # | Stage | Artifact | When (2026-05-10) |
| - | ----- | -------- | ----------------- |
| 1 | YouTube SEO research | `seo/research.json` | 05:53 |
| 2 | Script writing | `outline.md` | 05:54 |
| 2 | Script writing | `script.md` | 06:28 |
| 3b | Voiceover + transcript (TTS path) | `audio/voiceover.mp3` | 06:50 |
| 3b | Voiceover + transcript (TTS path) | `transcript.json` | 06:51 |
| 4 | Anchors + narration map | `anchors.txt` | 06:51 |
| 4 | Anchors + narration map | `narration-map.json` | 06:51 |
| 5 | Design.md (slim, take 2) | `design.md` | 20:48 |
| 6 | HyperFrames composition | `index.html` + `compositions/*.html` | 22:35 |
| 7 | Preview + lint | `.thumbnails/`, `.waveform-cache/` | (rolling) |
| 8 | Thumbnails | *not yet generated* | — |
| 9 | Render | *not yet rendered* | — |
| 10 | Publish | *not yet published* | — |

Note the ~14-hour gap between stage 4 (06:51) and stage 5 (20:48). That gap covers the spec-over-restriction failure and the reset documented in [composition-spec-over-restriction.md](./composition-spec-over-restriction.md). The "real" stage 5 → 6 → preview cycle took ~2 hours of one session after the reset.



Big shift, and it makes the design much sharper. The skill becomes the editorial brain; the tools become deterministic mechanical steps. Phase A is now three subsystems with cleanly separated concerns:

A1.  tools/sfx-catalog/         (Python CLI)
     Repo-level. Runs rarely (only when sound-effects/ changes).
     Output: sound-effects/sfx-catalog.yml

A2.  video-director Step H  (Claude skill — folded in 2026-06; was the
     standalone .claude/skills/sfx-author/, now removed)
     Per-scene, right after each scene's visual QA. The editorial brain —
     decides WHICH elements deserve SFX and which cue type. Reads the HTML +
     narration-map + transcript + design.md + catalog, writes data-sfx-*
     annotations, and reconciles the whole video's sound at the end. Uses
     tools/sfx-level to place cues against VO loudness.

A3.  tools/sfx-plan/            (Python CLI)
     Per-video. Deterministic. Reads annotated HTML + narration-map
     + catalog. Picks files. Emits compositions/sfx.html.

Updated lifecycle:

ONCE per library state:
  sound-effects/  ──▶ A1 sfx-catalog ──▶ sfx-catalog.yml  (committed)

PER VIDEO, per scene (right after that scene's visual QA passes):
  video-director Step H (A2)
       │
       ├──▶ reads HTML, narration-map, transcript, design.md, catalog
       ├──▶ proposes a cue plan: "17 cues — 4 whooshes, 8 ticks, …"
       ├──▶ HUMAN REVIEW GATE: user approves / tweaks / rejects
       ├──▶ writes data-sfx-* attributes into HTML
       ├──▶ runs A3 sfx-plan → generates compositions/sfx.html
       └──▶ launches npx hyperframes preview, shows URL

  user audits in preview, asks skill to refine specific cues, repeat.
