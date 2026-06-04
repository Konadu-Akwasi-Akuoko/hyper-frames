# SFX arc and reconcile — the per-pass score and the final sweep

Step H scores the SFX for **only the scene(s) you authored in this pass**, while
this scene's GSAP tween times and transcript word timings are still fresh in
context. That freshness is the whole point: it is how a cue lands neither early
nor late. You are not scoring the whole video here — you are punctuating *this
beat's own motion*, and rationing a tiny set of heavy cues across the runtime by
reading what's already been spent.

The common case is **small punctuation cues driven by this scene's GSAP beats**,
not booms and risers. Lead with those. boom, riser, and the single hook silence
are the only cues rationed across the whole video.

## SFX is mostly punctuation, not impact

Read what each beat is *doing* and reach for the everyday cue. The trigger is the
verb, never a named scene or a CSS-class lookup table:

| The beat is doing this…                          | Reach for…                  |
| ------------------------------------------------ | --------------------------- |
| a thing **appears** / fades in / a label resolves | `ui-tick` or `pop`          |
| something **slides in** / crosses the frame       | `whoosh`                    |
| something is **highlighted** / called out         | `ui-tick` or `msg-ding`     |
| something **snaps** into place / settles          | `ui-tick`                   |
| a **card taps** in                                | `card-tap`                  |
| a **scene boundary** with a real visual cross      | `whoosh`                    |
| a payoff word **lands** in speech                  | `boom` (rationed) or none   |
| tension **climbs** toward a reveal                 | `riser` (rationed)          |
| the **single largest beat** of the whole video     | `data-sfx-hook` + one cue   |

Most passes produce one to three of the top rows and nothing from the bottom
three. A pass that touches no heavy cue at all is the normal pass. If you're
tempted to add a cue but can't say *what the moment is doing*, leave it silent —
silence is a tool, and an unused cue is cheaper than a wrong one.

**Skip texture.** A per-character typewriter, a continuous drift, an ambient
pulse, a swarm of markers popping on — these are the texture, not the
punctuation. Scoring each one turns the scene into a bleep festival and burns the
density budget the real beats need.

## Density as narrative — a shape inside the ceiling

The one hard floor `tools/sfx-plan` enforces is density: it measures a rolling
**6-second** window and **raises `DensityViolationError`** (fails the run) above
**1.0 cues/s** (≈ 1 per 1s); above **0.5 cues/s** (≈ 1 per 2s) it only *warns*.
The same-cue spacing you want (`ui-tick` ≥ 2s, `whoosh` ≥ 4s, `boom` ≥ 30s) is
**your editorial heuristic — the tool does not check it** (it has no cooldown
logic). As an editorial target keep the whole-video average ≤ ~1 cue per 3s, well
under the warn line. Mix-craft physics, not a quota — never approach the ceiling
for its own sake. The full enforced-vs-editorial split lives in
`sfx-cues-and-timing.md`.

Inside the ceiling, cue *frequency* is itself an editorial signal. Where hits
cluster, the moment reads as busy and high-stakes; where they thin, it reads as
calm or weighty. Spend the budget so its shape tracks the story's energy, not a
constant sprinkle.

Three shapes worth considering — none required, most videos blend them:

- **Rising toward a climax.** Sparse open, density builds as stakes rise, peaks
  at the payoff, then a deliberate near-silent beat just after. The cue-frequency
  curve mirrors the tension curve.
- **Sparse throughout.** A contemplative or essay-toned video. Few cues, each
  unmistakably earning its place. The restraint *is* the texture.
- **Front-loaded.** A high-energy open that sets the pace, then settles into a
  calmer body — right when the hook is doing the heavy lifting.

You don't compute a curve. You read the shape off material you already have:
where the script **escalates** (stakes naming, a chain of consequences) cues can
cluster; where it **breathes** (the >600ms pauses) cues thin or stop — a breathe
phase is not a slot to fill; the **payoff beat** is the natural density peak and
the natural home for the once-per-video `boom`.

Working per-pass, you only see one slice of this shape at a time. That is fine —
the per-pass ledger below keeps the heavy cues rationed, and the final reconcile
checks the whole curve once at the end. **"When in doubt, score less" governs
every pass.**

## The single hook moment

Each video has **at most one** hook — the largest emotional or informational
beat. Mark it on its element with `data-sfx-hook="true"`. The tag is a
breadcrumb; a later pass (`audio-bed-music`) uses it to carve pre-impact silence
under the bed. If you can't identify a single clear hook this pass, **omit the
tag** — it may belong to a scene you haven't authored yet, and the final
reconcile confirms exactly one exists.

The hook earns **restraint, not volume.** The instinct is to pile on — a tick for
the reveal, a whoosh for the motion, a boom for the weight. Resist it: the ear
can't parse three hits at once, so it hears mud where you wanted impact. Score the
hook one of two ways:

- **One decisive cue** — a single `boom` on the payoff word, or a single `riser`
  resolving into the reveal. One precise hit lands harder than three competing
  ones.
- **Silence into the hit** — the beat *before* the hook runs silent, so the
  single hook cue lands out of negative space. The strongest version when the
  visuals already carry the weight.

A stack on the hook, or a cue that competes with the visual's own loudest moment
instead of marking it, is the failure here. Pick one.

## The per-pass arc ledger — derived, not a sidecar

The heavy cues (boom, riser, the one hook) are rationed across the whole video.
But video-director's principle holds: **the mounted state is the source of truth;
there is no progress file.** So each pass you *reconstruct* the remaining
heavy-cue budget by derivation, the same way Step A reconstructs the frontier
from `index.html`.

Two reads, both cheap:

1. **Where the peaks fall.** Read `story-spine.md` if present (a 3–4 line note of
   where the hook, climax, and landing land) or fall back to `script.md`. This
   tells you whether *this* pass's scene is near a peak (heavy cue may be earned)
   or in the body (almost certainly punctuation-only). It is orientation, not an
   instruction — it never tells you which cue to use or how densely to score.

2. **What's already spent.** Scan the placed `data-sfx-*` across **all**
   compositions to see which heavy cues and the hook are already committed:

   ```bash
   grep -rn 'data-sfx-on-anchor="boom"\|data-sfx-on-anchor="riser"\|data-sfx-hook' compositions/
   ```

   Count the booms (and note their scene times for the ≥30s cooldown), count the
   risers, and check whether a `data-sfx-hook` already exists. That count *is* the
   ledger.

Then decide this pass against the derivation: if a boom is already spent within
30s of this scene, you cannot place another; if the hook is already tagged
elsewhere, this scene does not get one; if `story-spine.md` puts the climax in a
later scene, **save** the boom for it rather than spending it on the first big
number that scrolls past here. Saving density for the moment that earns it is as
deliberate an act as spending it.

## Timing mode — the load-bearing choice

Every cue needs exactly one timing reference, and picking the mode is the single
most common bug surface. Get it wrong and the SFX lands before the visual.

| Trigger of the cue                                | Mode                                          |
| ------------------------------------------------- | --------------------------------------------- |
| a **visual change** (entry, slide, snap, scale)   | `data-sfx-at-scene-ms`                        |
| a **spoken word** (label said, name read, line lands) | `data-sfx-anchor` + `data-sfx-anchor-index` |

These are **mutually exclusive** — the scanner raises if both or neither is set.
Because you just authored this scene's timeline, the at-scene-ms math is in front
of you; this is exactly when it's cheapest to get right.

**Visual change → at-scene-ms.** Read the tween whose target is the cued element
from the timeline at the bottom of the scene file. Its position parameter is
`tween_start_ms`; its `duration` is the motion length. Compute the *perceptual
landing* (the moment the eye registers the element as present), scene-local:

| Motion type                                    | Landing                                |
| ---------------------------------------------- | -------------------------------------- |
| fade-in (ease-in-out)                          | `start + duration × 0.5–0.7`           |
| fade-in (ease-out / expo.out / power3.out)     | `start + duration × 0.30–0.50`         |
| fade-in (ease-in / power2.in)                  | `start + duration × 0.65–0.85`         |
| slide / translate (any ease)                   | `start + duration` (settles at the end)|
| scale + fade combo                             | the slower of the two — usually the fade |
| opacity snap (duration ≤ 0.1s)                 | `start` exactly                        |

For a `stagger: { each: N }`, each target's start shifts by N seconds; duration
stays constant.

**Spoken word → anchor.** The anchor must resolve via `narration-map.json` at
write time. Prefer the conceptually-loaded word over a function word, prefer words
spoken with emphasis, and match the visual *peak* not the visual start. If the
word you want isn't yet an anchor, that's a `NEW ANCHORS NEEDED` line (handled
below).

**The forbidden bug:** using `data-sfx-anchor` + a large negative
`data-sfx-lead-ms` to *back up* from a spoken word onto a visual moment. That's
the SFX-before-visual desync. If you're reaching a visual with a negative lead,
you've picked the wrong mode — switch to `data-sfx-at-scene-ms`. `data-sfx-lead-ms`
is a **±100ms peak-tuning knob only** (compensating an asset's perceived attack
vs. its measured peak); ≥200ms on an anchor cue *prints* a `sfx-plan` warning
(the CLI still exits 0 — you treat it as blocking and fix it).
Peak alignment itself — landing the asset's `peak_time_s` on the anchor — is done
by `sfx-plan`; your job is to pick the anchor and the mode correctly.

**Every cue pins its asset** via `data-sfx-asset`. Picking the file is editorial,
on par with picking the cue. Browse the catalog's `assets:` pool for the cue and
pick the timbre that matches the moment; **prefer an asset already used elsewhere
in this video** so the same cue family always sounds the same. When the same cue
fires three times in a row (a "rack"), use one asset for all three — that's the
point of the rack. `sfx-plan`'s resolver runs as a safety net, but relying on it
produces timbrally inconsistent scores across scenes.

## Volume — 0.5 is the default and the ceiling

Every cue's volume is a flat **0.5 by default**, set once as `default_volume: 0.5`
in `sound-effects/sfx-catalog.yml` — the single source of truth. **Do not write
`data-sfx-volume="0.5"` on every element.** Write a `data-sfx-volume` *only* to
duck a cue **below** 0.5 when it would fight hot VO — never above. 0.5 is the
ceiling.

To decide whether a duck is needed, probe the VO amplitude at the cue's landing
time (next section).

## tools/sfx-level — the VO-amplitude probe

`tools/sfx-level` is a deterministic probe (it reuses `tools/cut-snap`'s numpy
RMS-envelope DSP). Given the voiceover and a timestamp it returns the VO RMS dBFS
+ peak dBFS in a small window and classifies the window as a **narration gap** vs.
**active speech**:

```bash
uv run --project ../../tools/sfx-level sfx-level audio/voiceover.mp3 --at <t>
```

Use it two ways per pass:

1. **Confirm the cue lands right.** A punctuation cue meant to fall in a breath
   between phrases should probe as a gap; a payoff cue should sit where you expect
   relative to the spoken word. If the classification surprises you, your landing
   math or anchor choice is off — fix it before writing.
2. **Recommend a duck.** If the probe says active speech and the VO is hot at the
   cue's moment, drop a `data-sfx-volume` below 0.5 on that element so the cue
   doesn't mask the word.

## The compact per-pass proposal + standing approval

The approval gate stays — annotations are written only on `yes` / `approve` /
`go` — but it's lightened to a compact, per-pass form so the autonomous loop
isn't interrupted. Print only the cues for **this pass's scene(s)**:

```
SFX — pass scene(s): <NN[-MM]>   ledger: boom <used>/<budget·peak@time> · riser <used> · hook <set?>
  ✓ mode=at-scene-ms(<N>)   cue=<name>  asset=<basename>  on <#id|short-ref>   (<short reason>)
  ✓ mode=anchor("<word>"#N) cue=<name>  asset=<basename>  on <#id|short-ref>   (<short reason>)
  ✗ skip  <ref>   (<why considered-and-dropped, 6–10 words>)
NEW ANCHORS NEEDED: <list — or "none">
Approve to write?  [yes / refine / abort]   (or "auto-approve SFX for the rest")
```

- `mode=` is **mandatory** on every `✓` line — it surfaces the load-bearing
  timing choice for review (picking the wrong mode is the SFX-before-visual bug).
- `asset=` is **mandatory** on every `✓` line — show the basename.
- Skips matter as much as writes: they make the editorial reasoning legible.
- Reasons stay short — the proposal is a contract surface, not a notebook.
- **Standing approval:** if the user replies *"auto-approve SFX for the rest"* (or
  similar), drop the per-pass gate for the remainder of the loop and write
  directly each pass — but still print the proposal block each pass for the record,
  and still run the deterministic backstops below.

On `refine`, treat the instruction as a transformation on the plan and re-print.
On `abort`, write nothing.

## After approval, per pass

1. If `NEW ANCHORS NEEDED` is non-empty, append each anchor on its own line to
   `anchors.txt` (preserve existing entries) and re-run:

   ```bash
   uv run --project ../../tools/narration-map narration-map transcript.json --anchors anchors.txt
   ```

   Verify the new anchors appear in the regenerated `narration-map.json` before
   writing any attribute.

2. Add `data-sfx-*` attributes with the `Edit` tool — **one element per call**,
   never reformatting surrounding HTML.

3. Regenerate the audio sub-composition (idempotent — it rewrites the whole
   `compositions/sfx.html` from the placed annotations every run):

   ```bash
   uv run --project ../../tools/sfx-plan sfx-plan --report
   ```

   Read the report's warning count. A `DensityViolationError` fails the run (fix
   it); a `large lead_ms`, density (>0.5/s in a 6s window), or `overlap on track`
   warning still exits 0, but treat it as blocking — fix and re-run.

4. On first run only, the sfx-layer host is mounted in `index.html`. Confirm its
   `data-duration` spans the **full runtime** (a short mount clips late cues).

## SFX correctness is partly ear-only

A snapshot can't show sound. So the **human listen-in-preview audit stays the gate
each pass** — the deterministic tools are the automated backstop, not a
replacement for the ear. After `sfx-plan` regenerates the layer, surface the seek
target so the user can listen:

> Scored scene NN. Seek to **{cue_time}s** to hear the cue land.

The user has `npx hyperframes preview` running in their own window and reloads it
themselves — **never start, restart, or kill the preview server.**

## Final whole-video reconcile (runs once, at the Done condition)

When the whole script is covered and every scene has had its per-pass score, run
one reconcile pass over the entire video before handing off. This is where the
density *shape* — which you only ever saw a slice of per pass — is checked as a
whole.

1. **Regenerate everything.** Re-run `tools/sfx-plan --report` over the full
   video. It rewrites `compositions/sfx.html` idempotently from all placed
   annotations.
2. **Density curve.** `--report` prints a per-cue table; the only density figure
   the tool surfaces is a stderr `density …/s` warning when a 6s window crosses
   0.5 cues/s (there is no global "1 cue / X.Xs" line — derive the shape yourself
   from the cue timestamps). Confirm the shape tracks the story's energy (rising /
   sparse / front-loaded) rather than a flat sprinkle, that no `DensityViolationError`
   fired, and that no window crowds the warn line for its own sake.
3. **Spacing + overlap.** The tool enforces only **per-track overlap** (an
   `overlap on track N` warning when a cue starts before the previous cue on its
   track ends) — treat any as blocking. Your same-cue spacing (`ui-tick` ≥ 2s,
   `whoosh` ≥ 4s, `boom` ≥ 30s) is **not** tool-checked; scan the cue timestamps
   yourself and fix any pair too close, especially across scene seams.
4. **boom / riser rationing.** Confirm each heavy cue was spent only on a genuine
   peak — the line the video is about, a real build-to-payoff — not on the first
   big number that scrolled past.
5. **Exactly one hook.** Confirm precisely one `data-sfx-hook` exists across all
   compositions, and that it's scored with restraint (one decisive cue, or silence
   into the hit — never a stack).
6. **sfx-level sweep.** Run `tools/sfx-level` across every cue's landing time to
   catch any cue fighting loud VO; duck the offenders below 0.5 with
   `data-sfx-volume` and re-run `sfx-plan`.
7. **Full-runtime mount.** Verify the `sfx-layer` host's `data-duration` spans the
   full runtime so no late cue is clipped.

Then **hand off to `audio-bed-music`.** Music sits *beneath* SFX and is a separate,
downstream skill — it is not video-director's job. You identify the climax beat
precisely (the hook, the climax `boom`) so the music pass can agree with it; you do
not score the music.

## Failure modes you must handle

- **`sfx-catalog.yml` missing** → stop; direct the user to
  `uv run --project tools/sfx-catalog sfx-catalog`. Don't author against an
  imaginary catalog.
- **Anchor not resolvable after extending `anchors.txt`** → the anchor text isn't
  a literal substring of the transcript. Surface nearby spoken words from the
  transcript and ask the user to pick a real one (or switch to at-scene-ms if the
  trigger was actually visual).
- **`sfx-plan` raises `DensityViolationError`** → the window is too dense even
  after honoring the ceiling. Drop the lowest-priority cues in the densest window
  (usually a punctuation tick that was riding texture) and re-run.
- **Composition has placeholder stubs** (`[ TO BE BUILT ]`, `PLACEHOLDER`) → that
  scene's visuals aren't settled; do not score it. SFX follows finished visuals.
- **A requested cue isn't in the catalog** → don't invent it. Name the available
  cues, suggest the closest, and offer a catalog-revision task. Adding cues is
  catalog work, outside this step.
