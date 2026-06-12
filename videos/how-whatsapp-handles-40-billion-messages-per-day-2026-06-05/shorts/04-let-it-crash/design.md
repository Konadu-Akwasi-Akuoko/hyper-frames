# Design — Short 04: WhatsApp Wants Its Code to Crash

**Portrait 1080×1920 Short.** Inherits the parent video's dark system-design
look — every scene reads as a *diagram of a machine*, not a slide. This Short's
single idea: **"let it crash."** WhatsApp runs one tiny isolated process per
connected phone on the Erlang/BEAM VM; when one breaks it doesn't try to heal —
it dies alone, a supervisor spawns a fresh copy, and the other million never
feel it. The counterintuitive payoff: deliberate failure is what buys
reliability at scale.

## Format

- **Canvas: 1080×1920 (9:16).** Root host, `html,body`, `.scene`, and the
  viewport meta are all 1080×1920 (scaffolded — confirm before authoring).
- **Vertical safe zones:** keep hero text and figures in the middle ~60% of the
  height. Top ~10% and bottom ~12% are phone-UI / caption territory — no
  critical text there. The final "Subscribe" cue lands **upper-middle**, never
  over where the phone's real Subscribe button sits (bottom).
- **Big and few.** One idea per scene, large type, generous negative space.
  Mobile viewers read at arm's length — headlines bigger than the long-form.

## The spine (visual idea, not a storyboard)

The recurring object is a **field of isolated processes** — a grid of tiny
identical worker cells, one per phone. Every beat re-reads that one mechanism:
- **Hook:** "they wanted their code to crash" — a single worker cell glitches
  red. The wrongness is the mystery (engineers wanting failure).
- **Counter-twist:** "on purpose" — the philosophy gets named: **let it crash**.
- **Contrast:** most systems wrap everything in safety nets (a tangle of
  try/catch armor); WhatsApp does the opposite — bare, isolated cells.
- **Erlang / BEAM:** name the substrate. One **featherweight process per phone**
  on the BEAM VM — not a thread — millions running at once (the grid fills).
- **The crash:** one cell dies alone (goes dark), a **supervisor** notices and
  spawns a fresh clean copy; neighbours never flicker. This is the payoff beat.
- **The trade:** none of it is free — Erlang is niche (small hiring pool) and
  was never built for raw speed; it was built to **hold millions of things at
  once without falling over**. A balance/ledger reads the cost vs. the buy.
- **CTA:** what does a tiny team buy by betting on a language almost nobody
  hires for? → "To find out, subscribe." The fresh loop hands back to leverage.

## Palette (inherited from the parent)

| Token | Hex | Use |
|---|---|---|
| `--bg` | `#0a0f0d` | near-black green-tinted base |
| `--panel` | `#101613` | cell / card fill |
| `--border` | `#1e2722` | hairline structure |
| `--fg` | `#e9edeb` | primary text |
| `--soft` | `#c3cbc7` | secondary text |
| `--muted` | `#79857f` | captions / labels |
| `--accent` | `#25d366` | WhatsApp green — healthy process, the supervisor's fresh copy |
| `--accent-2` | `#7dd3fc` | sky — BEAM / process identity, cool structure |
| `--cost` | `#f0b429` | amber — the trade-off / cost ledger |
| `--danger` | `#ff6b5d` | red — the crashing process (used once, at the death beat) |

`--danger` is rationed: it appears only on the cell that crashes, so the eye
goes straight to the failure. Everything else stays green/sky/amber.

## Type

- **Inter** — all narration / headline / figure text (700–900 for heroes).
- **JetBrains Mono** — process IDs, the "let it crash" term, the supervisor
  log line, the cost/buy ledger. The machine's own voice.
- Weights 400/500 for mono (never 600 — renders italic in HyperFrames).

## Motion

- Process cells pop in with a fast back-ease stagger (a swarm assembling).
- The crash: one cell flips to `--danger`, scale-punches, then snaps dark; the
  supervisor's replacement fades up green in its place a beat later.
- Constant low-amplitude idle drift on the grid so nothing sits perfectly still.
- Entrances only — no exit animations except the final CTA. Every element
  enters (scene-root crossfade or per-element `opacity:0` + `fromTo`).

## CTA (the Cleo loop)

Final scene resolves the headline (niche language buys fault-tolerance) then
opens a **new** loop in one sentence — *what does a tiny team actually buy?* —
and hands it to the subscribe button. Land "Subscribe" upper-middle on the VO's
"subscribe" word. Defer all branding to this final line.

## Hard rules

- No editorial chrome (no scene labels, timecodes, corner strips). Ambient
  decoratives (grid, glow, ghost type) are fine.
- Transcript is timing truth — anchor every beat to real word timestamps.
- Deterministic only — no `Math.random`, `Date.now`, `repeat: -1`.
