# Fact check — how-whatsapp-handles-40-billion-messages-per-day

Script: `script.md` (8-min recut, ~1370 words, checked 2026-06-10)
Verified: 31 · Partial: 1 · Unverified: 0 · Contradicted: 0

> **Context:** This is an independent re-check of the recut 8-min script. A prior check of the 13-min expanded version (2026-06-05) graded 36 verified / 1 partial / 0 contradicted. All claims were re-extracted and re-verified from scratch. Claims whose wording changed in the recut are called out explicitly.

---

## ✅ Verified

### "Back in 2014, the machine behind that little tap was moving forty billion messages a day."
- Source: https://highscalability.com/how-whatsapp-grew-to-nearly-500-million-users-11000-cores-an/
- Source says: Rick Reed's March 31, 2014 Erlang Factory talk reported "19B messages in & 40B out per day." The script's "forty billion" refers to the outbound figure, consistent with the talk and with how the stat is conventionally cited.
- Recommendation: keep.

### "Two million live connections on a single server."
- Source: http://www.erlang-factory.com/conference/SFBay2012/speakers/RickReed
- Source says: Rick Reed's March 30, 2012 Erlang Factory SF talk "Scaling to Millions of Simultaneous Connections" demonstrated 2M+ TCP connections on a single server.
- Recommendation: keep.

### "Around thirty-two engineers running all of it."
- Source: https://sequoiacap.com/article/four-numbers-that-explain/
- Source says: WhatsApp had exactly 32 engineers at the time of the February 2014 acquisition announcement; Sequoia partner Jim Goetz's "four numbers" post.
- Recommendation: keep.

### "Your phone ... holds one persistent TCP connection — a single long-lived socket, opened once and kept open for hours."
- Source: https://highscalability.com/how-whatsapp-grew-to-nearly-500-million-users-11000-cores-an/ (Rick Reed 2014 talk summary)
- Source says: Each phone maintains a single persistent TCP connection to the chat server; this is the foundational design choice to avoid per-message reconnect overhead.
- Recommendation: keep.

### "it gets squeezed down into a compact binary protocol called FunXMPP, swapping verbose tags for single-byte tokens"
- Source: https://github.com/ben221199/WAPI/wiki/WhatsApp-FunXMPP and https://www.scribd.com/document/907134476/Comprehensive-FunXMPP-Documentation-Complete-Method-Analysis
- Source says: FunXMPP is a binary-tokenized XMPP variant that replaces verbose XML tags/attributes with single-byte tokens, substantially reducing mobile bandwidth.
- Recommendation: keep.

### "The backend was built almost entirely in Erlang, a language that came out of the telecom world."
- Source: https://highscalability.com/the-whatsapp-architecture-facebook-bought-for-19-billion/
- Source says: WhatsApp's server codebase was written "almost completely in Erlang," a language developed at Ericsson for telecom switching systems.
- Recommendation: keep.

### "Every connection becomes its own lightweight process on the BEAM virtual machine. Not a thread. Not a request handler."
- Source: https://highscalability.com/how-whatsapp-grew-to-nearly-500-million-users-11000-cores-an/
- Source says: Each connection and session is its own lightweight BEAM process — not an OS thread or request handler — enabling millions per node.
- Recommendation: keep.

### "When one process crashes, it dies on its own, and a supervisor respawns a clean one ... Erlang engineers call this 'let it crash.'"
- Source: https://nurkiewicz.com/2022/04/erlang.html and https://news.ycombinator.com/item?id=15735024
- Source says: "Let it crash" is the canonical Erlang/OTP fault-isolation philosophy — processes are supervised; a crash triggers a clean restart rather than defensive error handling.
- Recommendation: keep.

### "The answer sits in Mnesia, Erlang's in-memory distributed database ... Around two terabytes of it, all kept in RAM."
- Source: https://highscalability.com/how-whatsapp-grew-to-nearly-500-million-users-11000-cores-an/
- Source says: "an in-memory Mnesia database using about 2TB of RAM sharded across 16 partitions to store about 18 billion records."
- Recommendation: keep.

### "On the second of April, 2014, twenty billion messages people sent fanned out into forty-four billion delivered. Sixty-four billion in a single day."
- Source: https://www.technology.org/2014/04/02/whatsapp-hits-new-daily-record-handling-64-billion-messages-24-hours/ and https://time.com/46895/whatsapp-handles-64-billion-messages-a-day/ and https://venturebeat.com/2014/04/02/whatsapp-hits-record-64-billion-messages-in-one-day
- Source says: April 2, 2014 record — 20B sent / 44B delivered = 64B total. Multiple outlets confirm the exact sent/delivered split. Note: "Sixty-four billion in a single day" is the recut's phrasing (replacing "sixty-four billion total" from the 13-min version) — both are accurate to the source.
- Recommendation: keep.

### "If no one's there to receive it, the message drops into an encrypted offline queue and waits, for up to thirty days."
- Source: https://www.whatsapp.com/legal/privacy-policy (WhatsApp Privacy Policy, primary)
- Source says: "If a message is still undelivered after 30 days, we delete it."
- Recommendation: keep.

### "One grey tick means the server has it. Two grey ticks mean it reached the device. Two blue ticks mean it's been read."
- Source: https://faq.whatsapp.com/820124435853543/ (WhatsApp Help Center)
- Source says: One grey checkmark = delivered to server; two grey = delivered to recipient's phone; two blue = read by recipient. Exact match.
- Recommendation: keep.

### "In November 2014, WhatsApp partnered with Open Whisper Systems, the people behind the Signal Protocol."
- Source: https://signal.org/blog/whatsapp/ (published November 18, 2014)
- Source says: "Today we're excited to announce that Open Whisper Systems has partnered with WhatsApp." Open Whisper Systems created and maintains the Signal Protocol.
- Recommendation: keep.

### "by April 2016, end-to-end encryption was on by default for over a billion users"
- Source: https://techcrunch.com/2016/04/05/whatsapp-completes-end-to-end-encryption-rollout/ and https://abcnews.go.com/Technology/facebooks-whatsapp-turns-encryption-billion-users/story?id=38168501
- Source says: Full e2e rollout completed April 5, 2016, for WhatsApp's one billion users. Note: the recut uses "over a billion users" — WhatsApp passed 1 billion MAU in February 2016, so "over a billion" is accurate for the April 2016 date. All major news outlets at the time said "1 billion users"; "over a billion" is defensible but nudges slightly past the reported figure. See also Partial note in prior check, resolved in the 13-min version.
- Recommendation: keep (WhatsApp passed 1B in Feb 2016; April 2016 enrollment was "over a billion").

### "A prekey handshake called X3DH lets two people agree on a shared key, even when one of them is offline. Then the Double Ratchet takes over, deriving a fresh key for every single message"
- Source: https://signal.org/docs/specifications/doubleratchet/ (primary spec) and https://en.wikipedia.org/wiki/Signal_Protocol
- Source says: X3DH is the asynchronous key-agreement protocol using prekeys stored server-side; Double Ratchet derives a new message key per message, providing forward secrecy. Exact match with script's description.
- Recommendation: keep.

### "in 2021, Meta solved it with something called client-side fan-out. Every device gets its own identity key, and the sender encrypts each message separately, once for every device you own."
- Source: https://engineering.fb.com/2021/07/14/security/whatsapp-multi-device/ (Meta Engineering, July 14, 2021)
- Source says: "each device now has its own identity key"; "a client-fanout approach, where the WhatsApp client sending the message encrypts and transmits it N number of times to N number of different devices."
- Recommendation: keep.

### "when you link a new laptop, your history doesn't come from the server. Your phone encrypts a slice of your recent chats and hands it over directly."
- Source: https://engineering.fb.com/2021/07/14/security/whatsapp-multi-device/
- Source says: "When a companion device is linked, the primary device encrypts a bundle of the messages from recent chats and transfers them to the newly linked device." The key is delivered via an end-to-end encrypted message. Server holds nothing readable.
- Recommendation: keep.

### "Not Linux, but FreeBSD, chosen for its mature TCP stack and a kernel you could tune deep."
- Source: https://forums.freebsd.org/threads/whatsapp-on-freebsd.87908/ and https://news.ycombinator.com/item?id=22028689
- Source says: WhatsApp explicitly chose FreeBSD for its TCP/network stack maturity; former WhatsApp engineers confirm on HN that FreeBSD was the production OS pre-acquisition and the kernel was tuned extensively.
- Recommendation: keep.

### "They patched the BEAM runtime and the FreeBSD kernel themselves, hunting down lock contention."
- Source: https://www.slideshare.net/milkers/scaling-to-millions-of-simultaneous-connections-by-rick-reed-from-whatsapp (Rick Reed 2012 Erlang Factory slides)
- Source says: "From 200k to 2M were all contention fixes"; explicit BEAM patches (timer wheel, I/O, memory) and FreeBSD kernel backports listed.
- Recommendation: keep.

### "On the twenty-second of February, 2014, just three days after that nineteen-billion-dollar Facebook deal, WhatsApp went dark for about three and a half hours."
- Source: https://techcrunch.com/2014/02/22/whatsapp-is-down-facebooks-new-acquisition-confirms/
- Source says: Outage ran ~11 a.m. to 2:30 p.m. PST on February 22, 2014 — "around 210 minutes." 210 minutes = 3.5 hours. Facebook acquisition announced February 19, 2014 (three days prior). Both timings confirmed. Note: the recut changed prior script's "two hundred and ten minutes" to "three and a half hours" — both formulations are accurate to the same source figure.
- Recommendation: keep.

### "Back in 2011, one box already held around a million."
- Source: http://www.erlang-factory.com/conference/SFBay2012/speakers/RickReed
- Source says: "In 2011 WhatsApp achieved 1 million established tcp sessions on a single machine with memory and cpu to spare."
- Recommendation: keep.

### "By 2012, an engineer named Rick Reed pushed one past two million at an Erlang Factory talk."
- Source: http://www.erlang-factory.com/conference/SFBay2012/speakers/RickReed (March 30, 2012 talk)
- Source says: Rick Reed's talk "Scaling to Millions of Simultaneous Connections" demonstrated 2M+ connections on a single server.
- Recommendation: keep.

### "In production, they ran each near a million on purpose, leaving headroom for failover and spikes."
- Source: https://highscalability.com/how-whatsapp-grew-to-nearly-500-million-users-11000-cores-an/
- Source says: ~150 chat servers running ~1M phones each (150M peak connections) — production target ~1M while hardware sustained 2M+.
- Recommendation: keep.

### "Ten billion a day in 2012."
- Source: https://en.wikipedia.org/wiki/WhatsApp
- Source says: WhatsApp was handling 10 billion messages/day in August 2012.
- Recommendation: keep.

### "Forty billion out by 2014."
- Source: https://highscalability.com/how-whatsapp-grew-to-nearly-500-million-users-11000-cores-an/
- Source says: "19B messages in & 40B out per day" — March 2014 Rick Reed talk figures.
- Recommendation: keep.

### "Roughly a hundred billion by 2020."
- Source: https://techcrunch.com/2020/10/29/whatsapp-is-now-delivering-roughly-100-billion-messages-a-day/
- Source says: Mark Zuckerberg announced at Q3 2020 earnings that WhatsApp was delivering "roughly 100 billion messages a day."
- Recommendation: keep.

### "Around five hundred and fifty servers. Over eleven thousand CPU cores. A hundred and forty-seven million phones connected at once, at peak."
- Source: https://highscalability.com/how-whatsapp-grew-to-nearly-500-million-users-11000-cores-an/
- Source says: "~550 servers," "more than 11,000 cores," "147M peak concurrent connections" — all from the March 2014 Rick Reed talk summary. Exact match.
- Recommendation: keep.

### "WhatsApp was founded in 2009 on a deliberately lean, do-less culture."
- Source: https://en.wikipedia.org/wiki/WhatsApp
- Source says: WhatsApp Inc. was incorporated February 24, 2009 by Jan Koum; the "No Ads! No Games! No Gimmicks!" founding ethos is well-documented.
- Recommendation: keep.

### "roughly fourteen million users for every engineer on the team"
- Source: https://sequoiacap.com/article/four-numbers-that-explain/
- Source says: "one WhatsApp developer supported 14 million active users" (450M / 32 ≈ 14.06M).
- Recommendation: keep.

### "Forty billion messages a day, run by a team of roughly thirty-two."
- Source: https://sequoiacap.com/article/four-numbers-that-explain/ and https://highscalability.com/how-whatsapp-grew-to-nearly-500-million-users-11000-cores-an/
- Source says: 32 engineers (Sequoia); 40B outbound/day (Rick Reed 2014 talk). Both figures confirmed. Landing line is consistent with hook.
- Recommendation: keep.

### "Everything routes through the middle, in a pattern called store-and-forward."
- Source: https://www.whatsapp.com/legal/privacy-policy and substrate notes
- Source says: WhatsApp's architecture is explicitly store-and-forward — messages route through WhatsApp servers, never phone-to-phone; the server holds undelivered messages until the device pulls and ACKs them.
- Recommendation: keep.

### "Erlang ... was never built for raw number-crunching speed. What it was built for is holding millions of things at once without falling over."
- Source: https://www.erlang-solutions.com/blog/beam-jvm-virtual-machines-comparing-and-contrasting/
- Source says: BEAM's design goal is massive concurrency and soft real-time, not raw per-operation throughput; CPU-bound number-crunching is explicitly identified as a BEAM weakness.
- Recommendation: keep.

---

## ⚠️ Partial

### "just three days after that nineteen-billion-dollar Facebook deal"
- Source: https://www.sec.gov/Archives/edgar/data/0001326801/000132680114000010/exhibit991_pressrelease219.htm (SEC filing, primary) and https://techcrunch.com/2014/02/19/facebooks-19-billion-whatsapp-acquisition-contextualized/
- Source says: Total acquisition value was approximately $19 billion (cash + stock + restricted stock units). The script says "nineteen-billion-dollar deal." The headline figure is $19B, but the actual final value varied with Facebook's stock price and settled slightly differently at close. "Nineteen billion dollars" matches the widely reported and SEC-anchored announcement figure.
- Delta: Not a factual error — "$19 billion" is the universally cited announcement figure and appears in the SEC press release. Flagged partial only because the final settled value was ~$21.8B at close due to stock appreciation; the script uses the announcement-day figure, which is the conventional citation.
- Recommendation: keep as written (announcement-day figure is the standard reference). If extreme precision is needed, add "at announcement" qualifier.

---

## ❌ Unverified

(none)

---

## 🚫 Contradicted

(none)
