# Shorts Plan — How WhatsApp Handles 40 Billion Messages Per Day

Five vertical 1080×1920 Shorts cut from the parent video, each orbiting **one**
self-contained, counterintuitive question and ending on a Cleo-style subscribe
CTA fused to a fresh loop. Parent runtime ~11:23; trade-off motif and palette
inherited from the parent's `design.md` (green = the message, sky = the machine,
amber = the bill).

## The five beats

| NN | Slug | The ONE question | Words | Parent source (reuse) | Working title | Publish (proposed) |
|----|------|------------------|-------|------------------------|---------------|--------------------|
| 01 | `32-engineers-40-billion` | How did ~32 engineers move 40B messages a day? | ~165 | Hook + socket + actor model + leverage (script ¶1, ¶5, ¶7, ¶25) | **How 32 People Ran 40 Billion Messages a Day** | 2026-06-11 (today) |
| 02 | `ticks-are-architecture` | What are WhatsApp's ticks actually telling you? | ~185 | Store-and-forward + ticks + offline queue (script ¶15) | **What WhatsApp's Ticks Are Actually Telling You** | 2026-06-11 (today) |
| 03 | `numbers-dont-add-up` | Why don't WhatsApp's message counts add up? | ~190 | Server-side fan-out, the 20B→64B day (script ¶13) | **Why WhatsApp's Message Count Doesn't Add Up** | 2026-06-12 (tomorrow) |
| 04 | `let-it-crash` | Why does WhatsApp *want* its code to crash? | ~190 | Actor model + "let it crash" + Erlang trade (script ¶7–9) | **Why WhatsApp Wants Its Code to Crash** | 2026-06-12 (tomorrow) |
| 05 | `cant-read-your-messages` | Why can't WhatsApp read your messages — even if it wanted to? | ~190 | E2E encryption, X3DH + Double Ratchet + the bill (script ¶17) | **Why WhatsApp Can't Read Your Messages** | 2026-06-13 (Sat) |

Each Short is a full portrait mini-project under its `NN-slug/` folder; `script.md`
for all five is already drafted (CTA included). Build order = table order.

## The loop chain (each CTA hands to the next mystery)

- **01** ends on the bus-factor crack → curiosity about the limits.
- **02** ends on "the server carries every message but can't read one" → sets up **05**.
- **03** ends on "they flipped fan-out inside-out for laptops" → multi-device tease.
- **04** ends on "what does betting on a niche language buy a tiny team" → back to leverage (**01**).
- **05** ends on "where does your linked-laptop history come from, if not the server" → client-side fan-out tease.

All five point the curiosity back at the parent long-form for the full answer.

## Stagger schedule

**Locked cadence (user-set 2026-06-11):** front-loaded — two today, two tomorrow,
the closer Saturday. Lead with the two most universally relatable beats (the
leverage shock and the ticks), then the shock-number and engineering-philosophy
beats, closing on encryption.

| NN | Short | Publish date |
|----|-------|--------------|
| 01 | 32-engineers-40-billion | 2026-06-11 (today) |
| 02 | ticks-are-architecture | 2026-06-11 (today) |
| 03 | numbers-dont-add-up | 2026-06-12 (tomorrow) |
| 04 | let-it-crash | 2026-06-12 (tomorrow) |
| 05 | cant-read-your-messages | 2026-06-13 (Sat) |

## Per-Short copy (draft — finalized in each `publish.md` during Phase 2)

- **Common hashtags:** `#Shorts #WhatsApp #SystemDesign` + 1–2 per-beat nouns
  (`#SoftwareEngineering`, `#Erlang`, `#Encryption`, `#Tech`).
- **Description shape:** lead with the hook line, link the parent video, end with
  a comment-bait sequel offer.

## Publishing = manual

The `youtube-studio` MCP is v1 and **cannot upload or schedule**. Phase 2 renders
each 1080×1920 MP4 and writes its `publish.md`; uploading + scheduling to the
proposed dates is a manual Studio hand-off.
