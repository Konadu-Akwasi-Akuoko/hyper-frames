# Design — Short 05: WhatsApp Can't Read Your Messages

**Portrait 1080×1920 Short.** Inherits the parent video's dark system-design
look — every scene reads as a *diagram of a machine*, not a slide. This Short's
single idea: **WhatsApp literally can't read your messages.** The keys that would
unlock them never exist on WhatsApp's servers. End-to-end encryption (built with
Signal, default-on since 2016) gives every message its own key via the X3DH
handshake + the Double Ratchet — so the server routes a sealed envelope it can
never open. The counterintuitive payoff: that blindness has a real bill (no
search, no spam-scan, no history restore), and paying it is the whole point.

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

The recurring object is a **sealed envelope with a lock** — a message the server
carries but cannot open. Every beat re-reads that one mechanism:
- **Hook:** "WhatsApp can't read your messages" — a chat bubble slams shut behind
  a lock; an eye over it goes dark. The wrongness is the mystery (a messaging
  company blind to its own messages).
- **Counter-twist:** "not won't — can't" — a keyhole with **no key on the server
  side**. The key simply isn't there to seize.
- **2016 / Signal:** the milestone — E2EE on by default, **a billion+ people**,
  built with the Signal team. A switch flips green across a crowd.
- **X3DH handshake:** two phones agree on one **shared secret key** — even with
  one party **asleep, phone off** (the offline-prekey trick). Two keys converge
  into one.
- **Double Ratchet:** a **fresh key per message** — a ratchet advancing, a new
  key minted each step. "Steal one key, unlock exactly one message." The rest
  stay sealed.
- **The blind relay:** the server routes the **sealed envelope** to the right
  place but never learns what's inside (a blindfolded courier).
- **The bill:** blindness costs — **can't search, can't scan spam, can't rebuild
  history** on a new phone. A ledger of three struck-through capabilities.
- **CTA:** link a new laptop and old chats appear anyway — *where from, if not
  the server?* → "To find out, subscribe." The fresh loop hands forward to the
  multi-device mystery.

## Palette (inherited from the parent)

| Token | Hex | Use |
|---|---|---|
| `--bg` | `#0a0f0d` | near-black green-tinted base |
| `--panel` | `#101613` | card / envelope fill |
| `--border` | `#1e2722` | hairline structure |
| `--fg` | `#e9edeb` | primary text |
| `--soft` | `#c3cbc7` | secondary text |
| `--muted` | `#79857f` | captions / labels |
| `--accent` | `#25d366` | WhatsApp green — the lock engaged, encryption healthy |
| `--accent-2` | `#7dd3fc` | sky — keys, the handshake, cryptographic structure |
| `--cost` | `#f0b429` | amber — the bill (what blindness costs) |
| `--danger` | `#ff6b5d` | red — the blinded server / "steal one key" threat (rationed) |

`--accent-2` (sky) carries the **key/crypto** motif throughout — it's the visual
spine of this Short the way the process-grid was Short 04's. `--danger` is
rationed: the dark/blinded eye and the single stolen key only.

## Type

- **Inter** — all narration / headline / figure text (700–900 for heroes).
- **JetBrains Mono** — key fingerprints, `X3DH` / `Double Ratchet` labels, the
  cost ledger lines. The machine's own voice.
- Weights 400/500 for mono (never 600 — renders italic in HyperFrames).

## Motion

- Keys mint with a fast back-ease pop; the Double Ratchet advances in discrete
  clicks (a new key each step), never a smooth slide.
- The lock engages with a decisive snap; the eye over it dims to `--danger`.
- The envelope travels the relay (slide) while staying sealed.
- Constant low-amplitude idle drift so nothing sits perfectly still.
- Entrances only — no exit animations except the final CTA. Every element
  enters (scene-root crossfade or per-element `opacity:0` + `fromTo`).

## CTA (the Cleo loop)

Final scene resolves the headline (the server is blind by design) then opens a
**new** loop in one sentence — *if the server can't store your chats, where do
they come from when you link a new laptop?* — and hands it to the subscribe
button. Land "Subscribe" upper-middle on the VO's "subscribe" word. Defer all
branding to this final line.

## Hard rules

- No editorial chrome (no scene labels, timecodes, corner strips). Ambient
  decoratives (grid, glow, ghost type) are fine.
- Transcript is timing truth — anchor every beat to real word timestamps.
- Deterministic only — no `Math.random`, `Date.now`, `repeat: -1`.
