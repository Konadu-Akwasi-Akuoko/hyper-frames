# Reusable Prompts

---

## Full Autonomous Video Build — Icons + Memes + Motion Pass

Use this prompt after the composition scenes exist and you want a single autonomous run that
handles brand fidelity, meme sourcing, background removal, and word-level micro-animation
across the entire video. Paste it as-is; Claude picks up from the current video folder.

---

```
/hyperframes

I need you to do a full autonomous production pass on this video. You are going to make every
decision independently — do NOT use AskUserQuestion or ask clarifying questions at any point.
If something is ambiguous, pick the option that produces richer, more on-brand visuals and
leave a one-line comment in the code explaining the choice.

The scope is the ENTIRE video except Movement A of Scene 1 (that beat is already correct).
Everything else — all scenes, all movements, all beats — gets the full treatment below.

---

### Rule 1 — Every named technology gets its actual official icon/logo

Not a CSS approximation. Not a letter in a colored box. The actual mark.

- Download SVGs from simpleicons.org or devicons via WebFetch.
- If simpleicons doesn't carry it, try Iconify's API or the brand's own press kit.
- Save to `assets/icons/<name>.svg`. Inline or `<img>` — your call based on whether
  you need to tint it.
- Every technology named in the narration that has a visual identity gets its real mark
  on screen at the moment it's first named.

Examples of things that need real marks: Rust, Python, Java, C, Node.js, Netscape,
Electron, React Native, VS Code, Slack, Discord, Figma, 1Password, Obsidian, GitHub,
npm, Bun, Deno, Angular, React, jQuery, MongoDB, Apache, Express, Next.js.

---

### Rule 2 — Memes → search and download

Use WebSearch + WebFetch. If a site blocks you, try agent-browser on Google Images.
If that also fails, leave `<!-- PLACEHOLDER: <description> -->` in the HTML and move on.

Save raw images to `assets/memes/<name>-raw.png`.
Then apply Rule 3 to decide whether to remove the background.

---

### Rule 3 — Background removal: subject vs. scene

Remove the background when the image is a subject (person, character, animal) that needs
to float cleanly over the dark composition — the background would fight the design or
distract from the text alongside it.

Command:
  uvx --with "rembg[cpu,cli]" rembg i assets/memes/<name>-raw.png assets/memes/<name>.png

Keep the full background when the background IS the meme — the full frame, the context,
the setup is what makes it work. Cutting the subject would kill the joke.

Examples:
- Remove: skeptical dog, Mike Tyson portrait → subject is the message
- Keep: Drake approve/disapprove, distracted boyfriend → the scene IS the punchline

---

### Rule 4 — Word-level motion throughout every scene

Every 4–5 words spoken, something new must appear or move on screen. This is the
single most important rule for retention.

Prefer in this order:
1. A new element entering (the next diagram piece, icon, stat, label)
2. A scale pulse on an existing key element keyed to the exact word being spoken
3. A color flash (muted → accent or danger → ok) on the relevant element
4. A boxShadow glow pulse on a logo or badge

Never animate the same element twice in under 1.5s.
Never animate text that's already animating.
Entrance animations (`gsap.fromTo`) must finish before a pulse tween fires on the same
element — always check (entrance_start + duration) and add at least 0.01s gap.
For `back.out` eases, add 0.13–0.15s gap because the overshoot extends past nominal end.

**Dead zone detection workflow** (run after all entrances are placed):
```bash
scene="compositions/scene-XX-name.html"
grep -oP '(?<=\}, )\d+(\.\d+)?' "$scene" | sort -n | uniq | python3 -c "
import sys
times = [float(x.strip()) for x in sys.stdin if x.strip()]
times.sort()
for i in range(len(times)-1):
    gap = times[i+1] - times[i]
    if gap > 3.5:
        print(f'GAP {gap:.2f}s: {times[i]:.2f} → {times[i+1]:.2f}')
"
```

For each gap, pull the narration with:
```bash
python3 -c "
import json
t = json.load(open('transcript.json'))
START, END, SCENE_START = <global_gap_start>, <global_gap_end>, <scene_global_offset>
for w in t['words']:
    if w['type'] == 'word' and START <= w['start'] <= END:
        print(f'{w[\"start\"]:.2f}  (local {w[\"start\"]-SCENE_START:.2f})  {w[\"text\"]}')
"
```

Then add `tl.to()` pulses keyed to the timestamp of the most meaningful word in that window.

Scene global offsets:
  scene-01=0, scene-02=24.4, scene-03=82.0, scene-04=130.0, scene-05=150.68,
  scene-06=207.0, scene-07=257.0, scene-08=295.0, scene-09=340.0, scene-10=385.0,
  scene-11=462.0, scene-12=515.0

---

### Workflow

1. For each scene (01 → 12, skipping scene-01 Movement A):
   a. Read the composition HTML
   b. Identify every named technology → download its real SVG, wire it in
   c. Identify every meme → source it, apply bg removal decision
   d. Run the dead zone detection script
   e. Pull narration for each gap > 3.5s
   f. Add `tl.to()` pulses keyed to word timestamps
   g. Fix any boundary overlaps (exact end==start triggers lint)

2. After all scenes: `npm run check`
   - Fix all errors before continuing
   - `composition_file_too_large` warnings are informational — leave them
   - `overlapping_gsap_tweens` at exact boundary: add 0.01s to the recovery start

3. Commit in logical groups (scene batch, or thematic: "icons pass", "dead zones pass")

4. After each composition change, tell me which global timestamp to seek to in the
   already-open preview so I can verify without hunting.

---

### Design constraints (from design.md)

Palette: `--bg:#0b0d12` · `--panel:#11141b` · `--border:#1f242c` · `--fg:#e8eaed`
         `--soft:#c2c9d4` · `--muted:#7a8493` · `--dim:#3a4150`
         `--accent:#f7df1e` (JS yellow — reserved for JavaScript itself only)
         `--accent-2:#67e8f9` · `--danger:#ff6b5d` · `--ok:#7dd87d`

Pulse scale values: 1.02–1.08 for body elements, up to 1.15 for a key word slam.
Pulse duration: 0.15–0.22s up, 0.26–0.35s recovery.
Color flash: 0.18–0.22s to the bright value, 0.35–0.50s recovery.
No `repeat: -1`. No `Math.random()`. No `Date.now()`.
No editorial chrome (no corner labels, no scene counters, no timecodes).
```

---

## Notes on what worked / what to watch for

- **The gap threshold that matters is 3.5s, not 4.0s.** Start the sweep at 3.5s —
  gaps between 3.5–4.0s are where retention quietly drops. The 4.0s threshold catches
  the obvious dead zones; 3.5s catches the near-misses.

- **Boundary overlaps are silent bugs.** Any two consecutive tweens on the same
  element+property where `end_of_first == start_of_second` will trigger
  `overlapping_gsap_tweens`. Always add 0.01s gap. For `back.out`, add 0.13–0.15s.

- **`display: inline-block` required on `<span>` for scale.** GSAP can't apply
  `scale` transforms to inline elements. Add `display: inline-block` to any `<span>`
  you want to pulse.

- **Color in GSAP = literal hex, not CSS variables.** `tl.to(".el", { color: "var(--ok)" })`
  doesn't animate. Use `"#7dd87d"` directly.

- **Child animation during parent entrance is safe.** Animating a child element's
  `color` while the parent is doing `opacity`/`x` is not a GSAP conflict — different
  elements, different properties.

- **The `back.out` overshoot extends past nominal end time.** A tween with
  `back.out(2.5)` and `duration: 0.6` doesn't settle until ~0.75s — add 0.13–0.15s
  to any pulse that follows on the same element.
