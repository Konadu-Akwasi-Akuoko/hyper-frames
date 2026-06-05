# How WhatsApp Handles 40 Billion Messages Per Day — substrate notes

Runtime target: **10 min · ~1700 words** · **system-design style** (architecture, components, message flow, scaling). Expanded from the 5-min cut (2026-06-05).

## Named concepts
- **One persistent TCP connection** — each phone holds a single long-lived socket to a chat server, not a request-per-message. Reconnecting from scratch is expensive in battery and time, so the socket stays open for hours.
- **Erlang / BEAM VM** — the concurrency language the backend was "almost completely" built in; telecom heritage (lightweight processes, fault isolation, built-in distributed messaging, soft real-time).
- **Actor model / process-per-connection** — every connection and session is its own lightweight BEAM process (millions per node), scheduled by BEAM. Not a thread, not an OS process. Isolation is what lets one box hold millions of live sessions.
- **"Let it crash" / OTP supervision** — a failing process dies and a supervisor restarts a clean one, instead of defensive error-handling everywhere. Fault isolation per-connection is why ~10 engineers could operate it.
- **ejabberd → FunXMPP** — server began as a fork of the open-source ejabberd XMPP server, then heavily rewritten. FunXMPP is a binary-tokenized, compressed XMPP variant (single-byte tokens instead of verbose XML) to save mobile bandwidth and battery.
- **Mnesia** — Erlang's in-memory distributed database holding the routing table (user → server), offline queues, and session state in RAM (~2 TB across 16 partitions, ~18B records in 2014), replicated for fault tolerance. In-RAM lookup is what makes per-message routing fast at fan-out time.
- **Store-and-forward** — messages route through WhatsApp's servers, never phone-to-phone; the server holds a message only until the device pulls and ACKs it, then deletes it. Undelivered messages sit encrypted up to 30 days, then are deleted. Forwarded media is a documented exception — cached temporarily (encrypted) for faster re-delivery.
- **Delivery receipts (the ticks)** — one grey tick = reached the server; two grey = delivered to the device (fires when it reconnects and drains the queue); two blue = read.
- **Server-side group fan-out** — sender transmits one message tagged with a group ID; the server expands it to all members and delivers/queues per recipient. Group/presence routing partitioned 32 ways with pg2 (Erlang distributed process groups). Fan-out is why "delivered" counts exceed "sent" counts (the 64B-record day: 20B sent / 44B delivered).
- **Presence / last-seen / typing** — tracked as a separate notification stream from core message delivery; server-tracked session state, not client-to-client.
- **End-to-end encryption (Signal Protocol)** — X3DH prekey handshake + Double Ratchet (originally "Axolotl Ratchet"); the server only ever routes ciphertext it cannot read. Forward secrecy via a new message key per message.
- **Multi-device (client fan-out)** — each device has its own identity key; the server keeps a directory mapping an account to all its devices, and the sender encrypts the message once per device. The server is a key *directory*, not a key holder. An e2e-encrypted copy of "application state" (contacts, chat metadata) syncs across a user's devices. **History-sync detail:** when a new device is linked, its past message history is transferred from the user's PRIMARY device (the phone encrypts a recent-history bundle and sends it, key delivered over an e2e message) — NOT a server download, because the server holds nothing readable. History is a limited recent window; if the phone is offline/gone at link time, there's nothing to inherit.
- **Hot code loading** — Erlang ships fixes/features into a *running* system without restarts or traffic shifting, supporting near-zero downtime and a tiny ops footprint.
- **Headroom philosophy** — servers tuned to hold 2M+ connections but deliberately run near ~1M for failover and spike capacity.
- **Bare-metal + kernel tuning** — big boxes, tuned deep (patched BEAM runtime + patched FreeBSD kernel to kill lock contention), rather than many small horizontal nodes. Custom monitoring (wsar) to find bottlenecks.

## Real dated incidents
- **2009** — WhatsApp founded by Jan Koum and Brian Acton (both ex-Yahoo); lean "do less" culture; the "No Ads! No Games! No Gimmicks!" desk note.
- **2011** — ~1 million live TCP connections on a single server, CPU/RAM to spare.
- **March 30, 2012** — Rick Reed's Erlang Factory talk "Scaling to Millions of Simultaneous Connections"; one server pushed past **2 million** TCP connections.
- **August 2012** — 10 billion messages/day total (1B Oct 2011 → 2B Apr 2012 → 10B Aug 2012).
- **February 2013** — 200 million monthly active users.
- **December 31, 2012** — ~18 billion messages in one day (NYE record; reported by CBS News Jan 3, 2013). NOTE: earlier facet research mis-dated this to 2013 — corrected per fact-check.
- **February 19, 2014** — Facebook announces ~$19B acquisition: ~450M monthly users, ~32 engineers, ~55 total employees.
- **February 22, 2014** — major ~210-minute (3.5 hr) outage, three days after the acquisition announcement; attributed to a server issue, not the deal. (The counterpoint to "near-zero downtime.")
- **March 31, 2014** — Rick Reed's "That's Billion with a B" talk: ~19B in / **~40B out** per day, 465M users, the scale snapshot below.
- **April 2, 2014** — single-day record of 64 billion messages (20B sent / 44B delivered — the gap is group fan-out).
- **Nov 18, 2014** — Open Whisper Systems partnership; Signal Protocol e2e first ships on Android.
- **February 1, 2016** — 1 billion monthly active users.
- **April 5, 2016** — full end-to-end encryption by default for ~1 billion users (largest e2e deployment at the time).
- **~2017** — Facebook *begins* migrating WhatsApp off IBM SoftLayer onto its own data centers (completion date not publicly confirmed).
- **February 2020** — 2 billion users.
- **October 2020** — WhatsApp reported delivering ~100 billion messages/day (the "today" number — far past the 2014 figure).
- **July 2021** — Meta Engineering ships multi-device support (per-device keys, encrypted app-state sync).

## Concrete numbers and figures
- **40 billion outbound messages/day** — 2014 figure (19B in + 40B out). *The title's number. 2014-specific; NOT current.* (high)
- **2 million+ TCP connections on a single server** — 2012 talk; the headline feat. ~1M in 2011. Peak ~2.8M "reportedly" — soften. (high / medium)
- **342,000 in / 712,000 out** — peak user messages per second (2014). **230,000** logins/sec peak. (high) [Do NOT confuse with 70M/sec, which is INTERNAL Erlang IPC, not user messages.]
- **~32 engineers / ~450 million users** — ~14 million users per engineer (Sequoia's "four numbers": 450 / 32 / $1 / 0). ~10 engineers on the Erlang stack. (high)
- **~550 servers** — ~150 chat + ~250 multimedia + the rest standby — for 465M users. **>11,000 CPU cores**; **147 million** peak concurrent connections (2014). (high)
- **Hardware** — compute nodes: dual Intel Xeon E5-2690 v2, 20 cores / 40 threads, 64 GB RAM; DB nodes 512 GB RAM; FreeBSD 9.2; Erlang R16B01 + custom patches; IBM SoftLayer bare metal (700+ servers, dual datacenter, ~$2M/month). (high)
- **~2 TB** in-memory Mnesia, 16 partitions, ~18B records. ~98% write-back cache hit rate on the media path. (high / medium)
- **30 days** — max an undelivered message is held (encrypted) before deletion. (high)
- **~210 minutes** — the Feb 22, 2014 outage. (high)
- ~460,000 messages/second — *derived* color: 40B ÷ 86,400s ≈ 463k/s.
- **~$19 billion** — Facebook acquisition price, Feb 19, 2014. (high)

## Named people and organizations
- **Rick Reed** — WhatsApp engineer; his two Erlang Factory talks (2012 "Scaling to Millions", 2014 "That's Billion with a B") are the primary source for nearly every scale figure.
- **Jan Koum & Brian Acton** — co-founders (ex-Yahoo, both came from a FreeBSD-heavy Yahoo); the "No Ads! No Games! No Gimmicks!" desk note.
- **Jim Goetz** — Sequoia partner; authored the 450 / 32 / $1 / 0 "four numbers" framing (Feb 19, 2014).
- **Open Whisper Systems** (Moxie Marlinspike, Trevor Perrin) — built the Signal Protocol WhatsApp adopted.
- **IBM SoftLayer** — bare-metal host WhatsApp ran on for years (700+ servers, dual datacenter, ~$2M/month).
- **Meta Engineering** — shipped WhatsApp multi-device (July 2021).

## Load-bearing moments
- **~32 engineers serving ~450 million users** — the emotional core. The absurd leverage that frames every architecture choice as "how do so few people run so much?"
- **2 million-plus live TCP connections on one server** — the single most quotable feat; the visceral "one box, millions of phones" image, and the concrete justification for the Erlang/actor-model choice.
- **The Feb 2014 outage right after the $19B deal** — a human counterpoint that makes the "near-zero downtime" architecture feel real, not magic.

## System-design spine (the natural component walk — material, not a forced arc; ~12-14 movements for 10 min)
1. Hook: the impossible numbers (40B out/day 2014, 2M+ per server, ~32 engineers).
2. One phone = one persistent open socket to a chat server (mobile-network constraint).
3. The wire: FunXMPP compresses the message before it leaves the phone.
4. Land in a per-user Erlang process — the actor model; built in Erlang/BEAM; why telecom.
5. "Let it crash" + OTP supervision — fault isolation as the operability lever.
6. Route: Mnesia in-RAM routing table; lookup → recipient's session process.
7. Groups: server-side fan-out (pg2, 32-way); the sent-vs-delivered gap.
8. Store-and-forward: ephemeral encrypted offline queue (30 days); forwarded-media cache exception.
9. Delivery receipts: the ticks as the protocol made visible.
10. Presence / last-seen / typing: a separate notification stream.
11. End-to-end encryption: Nov 2014 → April 2016; X3DH prekeys + Double Ratchet; server routes ciphertext.
12. Multi-device: client fan-out, per-device keys, encrypted app-state sync (2021).
13. The metal: FreeBSD, big bare-metal boxes, SoftLayer, kernel + BEAM tuning; hot code loading and the 2014 outage as counterpoint.
14. The connections feat + scale payoff: 1M (2011) → 2M (2012), headroom; ~550 servers, 11,000+ cores, 147M concurrent; growth curve (10B/day 2012 → 40B out 2014 → ~100B/day 2020).
15. The lean-team payoff: ~32 engineers, ~14M users each; "do less" culture as architecture.

## Design trade-offs / opportunity costs (every choice has a bill — system-design framing)
- **Persistent socket** — pro: a warm pipe, no handshake per message. Con: the server must hold millions of *idle* open sockets (memory + a file descriptor each) even when nothing is being sent; keeping the connections alive is itself the scaling problem.
- **Erlang / BEAM** — pro: massive cheap concurrency + fault isolation. Con: niche language → small hiring pool; not built for raw CPU-bound number-crunching speed (C/C++ is faster per op); you bet the stack on an uncommon skillset.
- **"Let it crash"** — pro: simple, self-healing. Con: in-flight/transient state in a crashed process is lost; forces everything to be restartable/idempotent and retried.
- **In-RAM Mnesia** — pro: lookups fast enough to run per-message at fan-out. Con: RAM is expensive and capacity-bounded; in-memory must be replicated for durability; Mnesia is famously tricky under network partition (split-brain) and has table-size limits. Trades durability/cost for speed.
- **Store-and-forward, delete-after-delivery (30-day cap)** — pro: lean server, privacy, no archive to defend. Con: the server is no safety net — miss the 30-day window (or lose your phone without a backup) and the message/history is gone; no server-side search.
- **Server-side group fan-out** — pro: phone uploads once (saves mobile data). Con: the server bears the multiplication; load scales with group *size*, not how many people type; big groups are quietly one of the most expensive operations. (Contrast: multi-device uses *client*-side fan-out.)
- **End-to-end encryption** — pro: privacy; the server is a blind, low-liability pipe. Con: a blind server can't search your messages, can't scan content for spam/abuse, can't rebuild history on a new device; every content-reading convenience moves to the client or disappears. Encrypted backups become the weak point.
- **Multi-device client-fanout** — pro: each device independent; phone can be offline. Con: the sender encrypts every message once *per device*; the server forwards several copies where it used to forward one (forwarding load × device count); a new device's history must come from the *primary device*, so a dead/absent phone at link time = no history; cross-device state reconciliation is complex. Opportunity cost: they gave up the simple "thin mirror" WhatsApp Web.
- **Bare-metal + FreeBSD** — pro: control, performance, low cost at steady scale. Con: no cloud elasticity (can't autoscale on demand), you carry the capacity and the failures, you tune the kernel yourself; FreeBSD's ecosystem/ops talent pool is smaller than Linux's.
- **Tiny "do less" team** — pro: absurd leverage, coherence, low cost. Con: bus factor / key-person risk; a product that says no to almost every feature; thin coverage for edge cases and incidents.

## SEO context
- Title carries searchable nouns: **WhatsApp** + **40 Billion Messages (Per Day)**, with **System Design**/**Architecture** nearby. Primary: "How WhatsApp Handles 40 Billion Messages Per Day." Avoid the word "Interview".
- Differentiation: lean INTO the "whatsapp system design" lane but make **scale the spine** and tell the *real* architecture (Erlang, 2M/server, ~32 engineers) that 25–60 min interview videos gloss over. A 10-min cut can go deeper than the 9-10 min animated incumbents while staying tighter than the 25-58 min interview marathons.
- Hook budget: front-load the 40B / 2M / ~32-engineers payoff in the first ~8–10s before any deepening.
