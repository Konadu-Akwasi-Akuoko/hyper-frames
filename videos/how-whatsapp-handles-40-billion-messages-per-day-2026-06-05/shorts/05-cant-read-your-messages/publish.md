# Publish — Short 05 · Can't read your messages

**Scheduled:** 2026-06-13 (Saturday — the final Short of the 5-clip batch; one-every-day cadence wrapped 06-13).
**File:** `out/05-cant-read-your-messages.mp4` (1080×1920 delivery, rendered at portrait-4k 2160×3840, 58.8s)
**Cover-prepend:** `out/05-cant-read-your-messages-cover.mp4` (same render, the cover held as the first ~1s — for the frame-trick in Path B below; stream-copied, no quality loss)
**Cover (chosen):** `thumbnail-vertical-a.png` (1080×1920 — faceless, WhatsApp mark + "WHATSAPP LITERALLY CAN'T"; the mono tell resolves it: "read your messages — here's why"). Alternates in `thumbnails/round-1-vertical/out/`: `b.png` ("EVEN WHATSAPP IS LOCKED OUT"), `c.png` ("STEAL ONE KEY... NOTHING ELSE").

---

## Title

> Why WhatsApp Can't Read Your Messages

(≤100 chars; the open "why" the cover's paradox sets up without spoiling the
end-to-end-encryption / Double Ratchet answer. Alternates if A/B testing later:
"WhatsApp literally can't read your texts — here's why" · "Even WhatsApp is
locked out of your chats".)

## Description

```
WhatsApp can't read your messages. Not "won't" — can't. The keys that would unlock them don't live on WhatsApp's servers at all. In 2016, end-to-end encryption switched on by default for over a billion people, built with the team behind Signal. A handshake called X3DH agrees on a shared secret — even when one phone is asleep and offline — and then the Double Ratchet derives a brand-new key for every single message. Steal one key, and you unlock exactly one message. Nothing else. The server still routes the envelope; it just never learns what's inside.

Full breakdown of how WhatsApp actually handles 40 billion messages a day (persistent connections, the actor model, "let it crash", and this encryption layer): [PARENT VIDEO URL — paste once the long-form is live]

But that blindness has a bill — and one thing it seemingly can't explain. So when you link a new laptop and your old chats appear anyway, where did they come from? More Shorts this week.

#Shorts #WhatsApp #Encryption
```

## Hashtags

`#Shorts` `#WhatsApp` `#Encryption` `#EndToEndEncryption` `#SystemDesign`

---

## The loop (per PLAN.md)

CTA ends on **"So when you link a new laptop and your old chats appear anyway —
where did they come from, if not the server? To find out, subscribe."** → solves
the headline question (the server is blind), then opens a fresh loop (then how do
linked-device chat backups appear at all?) and hands it to the subscribe button,
while pointing back at the parent long-form for the full system.

## Manual Studio upload (MCP v1 can't upload or schedule)

Two ways to set the custom cover — pick whichever Studio offers for this Short:

**Path A — direct custom thumbnail (simplest, if available):**
1. Studio → **Create → Upload videos** → select `out/05-cant-read-your-messages.mp4` (plain render).
2. **Title / Description:** paste from above — **fill the `[PARENT VIDEO URL]`** once the long-form is live.
3. **Thumbnail:** upload `thumbnail-vertical-a.png` (the chosen pick; `b`/`c` in `thumbnails/round-1-vertical/out/` are alternates).
4. **Hashtags:** already in the description; confirm `#Shorts` is present.
5. **Visibility → Schedule →** set **2026-06-13**.

**Path B — frame-trick (reliable fallback if Shorts won't accept a custom thumbnail):**
1. Studio → **Create → Upload videos** → select `out/05-cant-read-your-messages-cover.mp4` (cover held as the first ~1s).
2. **Title / Description / Hashtags:** same as Path A.
3. **Thumbnail → Select frame from video →** scrub to **00:00** (the held cover frame) → Save.
4. **Visibility → Schedule →** set **2026-06-13**.
5. Once it's live: **YouTube editor → Trim →** cut the **first ~1 second**. The Short then opens on the hook; the chosen thumbnail persists.

(Optional) After it's live, run `video-publish-qa` against it to catch thin tags / caption gaps.
