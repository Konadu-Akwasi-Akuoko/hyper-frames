# Design — How Rate Limiting Works: Token Bucket vs Leaky Bucket

Technical / editorial **dark mode** — a Computerphile / Fireship system-design
explainer with editorial restraint. Every scene reads as a **diagram**, not a
slide. The video is a **talking-head** take (creator on camera) carried mostly in
GRAPHICS mode, with real b-roll dropped in for the metaphors (buckets, gates,
collapse, attacks).

Dark canvas is deliberate: the on-camera footage is dark, so a dark canvas keeps
FACE↔GRAPHICS crossfades clean (no white flash), lets PIP borders read, and suits
the infrastructure / outage / DDoS subject matter.

## The spine — two buckets, two colors

The whole video turns on **token bucket vs leaky bucket** being mirror images.
Encode that in color so the eye learns the duality:

- **Amber = the token bucket** (tokens are gold; you *spend* them, count *down*).
- **Cyan = the leaky bucket** (water; it *drains*, counts *down to zero* / leaks).

When the "mirror image" reveal lands (script ¶17), the two colors meet — amber
counting up, cyan counting down — same cap, same rate, identical call. Hold the
amber/cyan discipline the entire video so that payoff is visual, not just verbal.

## Palette

| Token       | Value     | Use                                                            |
| ----------- | --------- | ------------------------------------------------------------- |
| `bg`        | `#0b0d12` | Background canvas (warm-tinted near-black)                     |
| `panel`     | `#11141b` | Inset cards, code blocks, bucket bodies                        |
| `border`    | `#1f242c` | Hairline rules and panel borders                              |
| `fg`        | `#e8eaed` | Headlines, primary text                                        |
| `muted`     | `#7a8493` | Captions, labels, metadata, eyebrows                          |
| `dim`       | `#3a4150` | De-emphasized strokes, very small text                        |
| `accent`    | `#ffb547` | **Amber phosphor — TOKEN bucket, tokens, focal callouts**      |
| `accent-2`  | `#67e8f9` | **Cyan — LEAKY bucket, water/queue, drain, secondary points**  |
| `danger`    | `#ff6b5d` | 429, attacks, retry storm, congestive collapse, outages        |
| `ok`        | `#7dd87d` | "allowed" / request waved through / resolved state             |

GRAPHICS scenes that cover the face MUST use an **opaque** fill (`bg` solid),
never a tinted-transparent white/dark — or the dark face footage ghosts through.
Verify on a held-graphics frame, not just the transition frame.

## Typography

- **Sans (display / body):** `Inter` (built-in). Weights 300, 500, 700, 900.
- **Mono (technical / numbers / code):** `JetBrains Mono` (built-in). Weights
  **400, 500** only — **never 600** (renders italic in HyperFrames on this Mac).
- Headlines: 96–140px / 800.
- Section eyebrows: 22px / 500 mono, uppercase, `letter-spacing: 0.18em`, `muted`.
- Body labels: 28–36px / 400.
- Stats / counters / rates / req-per-sec: JetBrains Mono, `tabular-nums`.
- **Human-voice (verbatim quotes):** the on-screen reproductions of the literal
  refusals — "You're doing that too much", "Try again in a minute", "429 Too Many
  Requests", "resets in 3h 18m" — render as a real **UI chip / system toast**
  (panel bg, rounded, mono), i.e. as the *artifact the viewer actually saw*, not
  as narration. That toast styling IS the human-voice treatment for this video.

## Motion (system-design register)

Calibrated to the chaptered-explainer pacing lane: **hold one evolving canvas
across a whole subtopic**, reset only at chapter boundaries. Median scene
**9–15s**, ~1–3 hard cuts/min — slow and deliberate, not a churny essay.

- Crossfade transitions between scenes (0.5s, `power2.inOut`); push/wipe at
  chapter seams so two text blocks never share the frame.
- Entrance staggers ≤ 500ms across a scene; vary eases (≥3 different per scene).
- Ambient motion on every decorative layer (slow drift, breathe, token-drip).
- The token-drip and the leak are the signature recurring motions — reuse them.

## Talking-head

```
talking-head: assets/video/talking-head.mp4
```

Continuous on-camera take (derived from the cut master). Mounted as the locked
seek-driven `#face-layer` (track-index 8, full runtime). Per-chunk mode decided
by the sentence:

- **FACE** — direct-to-viewer beats: the cold-open "you've seen this message",
  the CTA close ("I'm curious which gate you'd put on your own API"), and the
  landing line. The words are *to* the viewer.
- **GRAPHICS** (default, majority) — every mechanism/diagram beat: the buckets,
  the counters, the comparisons, the worked numbers, the incidents.
- **PIP** — occasional, when the creator is narrating *over* a diagram that
  benefits from presence (e.g. introducing "here's the only choice that matters").

## B-roll inventory (assets/video/b-roll/)

Real footage the creator supplied — drop into scenes as decorative clips
(`assets-and-media.md` decorative-video model: muted, seek-driven or autoplay+loop
per scene). Alpha-channel clips composite directly over the dark canvas.

| File | Dims / dur | Alpha | Maps to script beat |
| --- | --- | --- | --- |
| `water-bucket-3d-animation-alpha-channel-transpar-…utc.mov` | 3840×2160 · 6.0s | ✅ | The **literal bucket** — token bucket intro (¶11), leaky "bucket with a hole" (¶13). Hero metaphor object; composite over canvas. |
| `VOROTA_2017.mov` | 1920×1080 · 12.0s | ✅ (rgba) | **The gate** — "sits a gate" (¶2 hook), "plants a gate at the very edge" (¶9), "a bouncer at the door" (¶15). |
| `Skyscraper Destruction.mov` | 1920×1080 · 22.9s | ✅ | **Congestive collapse / outage** — DynamoDB 5h down (¶7), AWS 14h Oct-2025 collapse (¶7). |
| `cyber-attack-warning-with-glitch-effect-and-skull-…utc.mp4` | 1920×1080 · 15.0s | — | **Rapid Reset / DDoS** — 398M req/s flood (¶2 hook, ¶5). |
| `futuristic-cyber-attack-warning-and-protection-int-…utc.mov` | 1920×1080 · 20.0s | — | DDoS wave / "Cloudflare and Amazon hit in the same wave" (¶5); attack-vs-protection framing. |
| `man-choking-himself-with-pained-facial-expressions-…utc.mov` | 1920×1080 · 13.2s | — | **"a system strangles itself"** / retry storm (¶7); recursion close "keep from strangling itself" (¶25). |
| `man-stranglehold-violent-confrontation-…utc.mov` | 1920×1080 · 8.6s | — | Alt strangle beat — retry storm pile-on (¶7). |
| `Black Man Crying Video Meme Template [v-Sl_e9Gcfg].mp4` | 480×480 · 15.8s | — | **Reaction** — the personal "you're doing that too much" frustration (¶2 / landing ¶28). Low-res → small framed/PIP only. |
| `enough.jpg` | 460×726 · still | — | "something that can say **enough**" (¶5). |

Ration b-roll like any imagery — it punctuates the metaphor beats; the mechanism
diagrams stay authored vector graphics (buckets filling/leaking, counters,
windows). B-roll is the texture; the diagrams are the substance.

## Don'ts

- No gradient text. No purple→blue / neon gradients. No left-edge accent stripes.
- No identical card grids. No editorial chrome (scene labels, timecodes).
- Don't let amber and cyan drift off their meanings — they ARE the two algorithms.
- Don't play b-roll under a covering opaque graphic and call it GRAPHICS mode — if
  a clip is the point, it's on top; if the diagram is the point, the clip is gone.
