# Fact check — how-whatsapp-handles-40-billion-messages-per-day

Script: `script.md` (13-min expanded version, ~2204 words, checked 2026-06-05)
Verified: 36 · Partial: 1 · Unverified: 0 · Contradicted: 0

> **Resolution log — items fixed in script between earlier rounds and this one:**
> - Contradicted: "eighteen billion on New Year's Eve, 2013" → corrected to **2012** (script line 35; substrate-notes updated).
> - Partial: "around a billion users" (Apr 2016 e2e) → **"over a billion"** (script line 25).
> - Partial: "Not the acquisition, not the load" outage framing → softened to **"WhatsApp blamed a server problem, not the deal itself"** (script line 33).
> - Partial: server-split "the rest for photos and video" → phrasing removed from script; only "around five hundred and fifty servers" remains.

---

## Verified

### "Forty billion outbound messages a day ... Back in 2014"
- Source: https://highscalability.com/how-whatsapp-grew-to-nearly-500-million-users-11000-cores-an/ (published March 31, 2014)
- Source says: "19B messages in & 40B out per day" — exact inbound/outbound split from Rick Reed's March 2014 Erlang Factory talk.
- Note: Script correctly labels these as "outbound" and anchors to 2014 throughout, including the landing. Does not imply a current figure.
- Recommendation: keep.

### "Around thirty-two engineers running the whole thing"
- Source: https://sequoiacap.com/article/four-numbers-that-explain/ (Sequoia Capital, February 2014)
- Source says: WhatsApp had exactly 32 engineers at the time of the acquisition announcement.
- Recommendation: keep.

### "roughly fourteen million users for every engineer on the team"
- Source: https://sequoiacap.com/article/four-numbers-that-explain/
- Source says: "one WhatsApp developer supported 14 million active users" — 450M users / 32 engineers ≈ 14.06M.
- Recommendation: keep.

### "Back in 2012, at an Erlang Factory talk, engineer Rick Reed pushed a single box past two million"
- Source: http://www.erlang-factory.com/conference/SFBay2012/speakers/RickReed (March 30, 2012)
- Source says: Talk "Scaling to Millions of Simultaneous Connections"; demonstrated 2M+ TCP connections on one server; optimization peak reached 2.8M in testing.
- Recommendation: keep.

### "Back in 2011, one server already held around a million live connections, with CPU and memory to spare"
- Source: http://www.erlang-factory.com/conference/SFBay2012/speakers/RickReed
- Source says: "In 2011 WhatsApp achieved 1 million established tcp sessions on a single machine with memory and cpu to spare."
- Recommendation: keep.

### "In production they ran each near a million on purpose, leaving headroom for failover and spikes"
- Source: https://highscalability.com/how-whatsapp-grew-to-nearly-500-million-users-11000-cores-an/
- Source says: "~150 chat servers (~1M phones each, 150 million peak connections)" — production target ~1M while hardware could sustain 2M+.
- Recommendation: keep.

### "Around two terabytes of it, kept in RAM" (Mnesia)
- Source: https://highscalability.com/how-whatsapp-grew-to-nearly-500-million-users-11000-cores-an/
- Source says: "about 2TB of RAM sharded across 16 partitions to store about 18 billion records."
- Recommendation: keep.

### "Around five hundred and fifty servers"
- Source: https://highscalability.com/how-whatsapp-grew-to-nearly-500-million-users-11000-cores-an/
- Source says: "~550 servers + standby gear."
- Recommendation: keep.

### "Over eleven thousand CPU cores"
- Source: https://highscalability.com/how-whatsapp-grew-to-nearly-500-million-users-11000-cores-an/
- Source says: "~11,000 cores run the Erlang system."
- Recommendation: keep.

### "A hundred and forty-seven million phones connected at once, at peak"
- Source: https://highscalability.com/how-whatsapp-grew-to-nearly-500-million-users-11000-cores-an/
- Source says: "147M peak concurrent connections — phones connected to the systems."
- Recommendation: keep.

### "up to thirty days" (offline queue ceiling)
- Source: https://www.whatsapp.com/legal/privacy-policy (WhatsApp Privacy Policy, primary)
- Source says: "If a message is still undelivered after 30 days, we delete it."
- Recommendation: keep.

### "on the fifth of April, 2016, end-to-end encryption switched on by default for over a billion users — the largest such deployment at the time"
- Source: https://techcrunch.com/2016/04/05/whatsapp-completes-end-to-end-encryption-rollout/ and https://www.eff.org/deeplinks/2016/04/whatsapp-rolls-out-end-end-encryption-its-1bn-users
- Source says: Full e2e rollout completed April 5, 2016; WhatsApp had "over one billion" MAU (passed 1B in Feb 2016). EFF and TechCrunch describe it as the largest ever e2e deployment at the time.
- Recommendation: keep.

### "WhatsApp was founded in 2009"
- Source: https://en.wikipedia.org/wiki/WhatsApp
- Source says: WhatsApp Inc. incorporated in California on February 24, 2009, by Jan Koum.
- Recommendation: keep.

### "On the second of April, 2014, twenty billion messages users sent fanned out into forty-four billion delivered — sixty-four billion in total"
- Source: https://www.technology.org/2014/04/02/whatsapp-hits-new-daily-record-handling-64-billion-messages-24-hours/ and https://time.com/46895/whatsapp-handles-64-billion-messages-a-day/
- Source says: April 2, 2014 record — 20B sent / 44B delivered = 64B total. Multiple outlets confirm exact split.
- Recommendation: keep.

### "group and presence routing was partitioned thirty-two ways across Erlang's distributed process groups"
- Source: https://highscalability.com/how-whatsapp-grew-to-nearly-500-million-users-11000-cores-an/
- Source says: "WhatsApp partitions services between 2 and 32 ways, with most services partitioned 32 ways. pg2 addressing is used to address partitions across the cluster."
- Recommendation: keep.

### "The small signals beside them — the 'typing' dots, the 'last seen' timestamp, the green presence dot ... ride their own lightweight notification stream, deliberately kept off the message path"
- Source: https://medium.com/@ygsh0816/inside-whatsapps-real-time-infrastructure-the-magic-behind-online-and-typing-f9ac648fb2e7
- Source says: Presence, last-seen, and typing are tracked as separate ephemeral session state (TTL-keyed, in-memory), not routed through the durable message pipeline.
- Recommendation: keep.

### "On the eighteenth of November, 2014, WhatsApp partnered with Open Whisper Systems — Moxie Marlinspike and Trevor Perrin, the people behind the Signal Protocol"
- Source: https://signal.org/blog/whatsapp/ (published November 18, 2014)
- Source says: "Today we're excited to announce that Open Whisper Systems has partnered with WhatsApp." Moxie Marlinspike founded OWS; Trevor Perrin co-authored the Signal Protocol spec.
- Recommendation: keep.

### "a prekey handshake called X3DH lets two people agree on a shared key even when one of them is offline ... Then the Double Ratchet takes over, deriving a fresh key for every single message. That gives you forward secrecy."
- Source: https://en.wikipedia.org/wiki/Signal_Protocol and https://signal.org/docs/specifications/doubleratchet/
- Source says: Signal Protocol uses X3DH for asynchronous initial key agreement (prekeys stored server-side), then Double Ratchet produces a new message key per message, providing forward secrecy.
- Recommendation: keep.

### "In 2021, Meta's engineers solved it with a quiet change. Each device gets its own identity key ... The server keeps a directory that maps your account to every device you own ... client-side fan-out — the sealing happens on the sender's phone, once per recipient device."
- Source: https://engineering.fb.com/2021/07/14/security/whatsapp-multi-device/ (Meta Engineering, July 14, 2021)
- Source says: "With multi-device, each device now has its own identity key"; "The WhatsApp server maintains a mapping between each person's account and all their device identities"; uses "a client-fanout approach, where the WhatsApp client sending the message encrypts and transmits it N number of times to N number of different devices."
- Recommendation: keep.

### "Not Linux — FreeBSD, chosen for a mature TCP stack and a kernel you could tune deep. Both Koum and Reed came out of a FreeBSD-heavy Yahoo"
- Source: https://forums.freebsd.org/threads/whatsapp-on-freebsd.87908/ and https://news.ycombinator.com/item?id=8711715
- Source says: WhatsApp chose FreeBSD explicitly; about half the early server team had FreeBSD experience from Yahoo; Koum and Reed both had Yahoo backgrounds with heavy FreeBSD use.
- Recommendation: keep.

### "Compute boxes ran dual ten-core Intel Xeon chips, sixty-four gigabytes of RAM, half a terabyte on the database machines"
- Source: https://highscalability.com/how-whatsapp-grew-to-nearly-500-million-users-11000-cores-an/
- Source says: "2x2690v2 Ivy Bridge 10-core (40 threads total with hyperthreading)"; compute nodes "64GB of RAM"; database nodes "512GB of RAM." 512 GB = half a terabyte — exact match.
- Recommendation: keep.

### "All of it sat on IBM SoftLayer bare metal — seven hundred-plus servers across two datacenters, for roughly two million dollars a month"
- Source: https://www.datacenterdynamics.com/en/news/facebook-to-move-whatsapp-workloads-from-ibms-cloud-to-its-own-data-centers/ and https://www.networkworld.com/article/963727/whatsapp-leaves-ibms-softlayer-cloud-for-facebook-data-center-what-it-really-means.html
- Source says: 700+ servers in California and Washington D.C. datacenters, costing Facebook "up to $2 million a month."
- Recommendation: keep.

### "They patched the BEAM runtime and the FreeBSD kernel both, hunting down lock contention"
- Source: https://www.slideshare.net/milkers/scaling-to-millions-of-simultaneous-connections-by-rick-reed-from-whatsapp (Rick Reed 2012 Erlang Factory slides, primary)
- Source says: "From 200k to 2M were all contention fixes"; explicit BEAM patches (timer wheel, I/O, memory) and FreeBSD kernel backports listed.
- Recommendation: keep.

### "On the twenty-second of February, 2014 — three days after Facebook announced the nineteen-billion-dollar deal — WhatsApp went dark for about two hundred and ten minutes ... WhatsApp blamed a server problem, not the deal itself."
- Source: https://techcrunch.com/2014/02/22/whatsapp-is-down-facebooks-new-acquisition-confirms/
- Source says: Outage ran ~11 a.m. to 2:30 p.m. PST February 22, 2014 — ~210 minutes; three days after the February 19 announcement. Jan Koum told the WSJ "we had a server outage." TechCrunch speculated acquisition-driven load; Koum did not confirm that.
- Note: "WhatsApp blamed a server problem, not the deal itself" accurately represents Koum's public statement without overclaiming a ruled-out cause.
- Recommendation: keep.

### "Ten billion messages a day by August 2012"
- Source: https://en.wikipedia.org/wiki/WhatsApp
- Source says: WhatsApp was handling 10 billion messages/day in August 2012, up from 2 billion in April 2012.
- Recommendation: keep.

### "Around eighteen billion on New Year's Eve, 2012"
- Source: https://www.cbsnews.com/news/whatsapp-reports18-billion-messages-on-new-years-eve/ (published January 3, 2013)
- Source says: "On Dec 31st we had a new record day: 7B msgs inbound, 11B msgs outbound = 18 billion total" — December 31, 2012. CBS News published the report January 3, 2013; ITProPortal (June 2013) confirmed the "previous NYE record" had been superseded.
- Recommendation: keep.

### "Then nineteen billion in and forty billion out, every day, by the 2014 talk"
- Source: https://highscalability.com/how-whatsapp-grew-to-nearly-500-million-users-11000-cores-an/ (March 31, 2014)
- Source says: "19B messages in & 40B out per day" — the March 2014 Rick Reed "That's Billion with a B" talk figures.
- Recommendation: keep.

### "By 2020, WhatsApp was carrying roughly a hundred billion a day"
- Source: https://techcrunch.com/2020/10/29/whatsapp-is-now-delivering-roughly-100-billion-messages-a-day/
- Source says: Mark Zuckerberg announced at Q3 2020 earnings that WhatsApp was delivering "roughly 100 billion messages a day."
- Recommendation: keep.

### "FunXMPP, trading verbose tags for single-byte tokens"
- Source: https://www.scribd.com/document/907134476/Comprehensive-FunXMPP-Documentation-Complete-Method-Analysis
- Source says: FunXMPP is a binary-tokenized XMPP variant replacing verbose XML tags with single-byte tokens, substantially reducing bandwidth.
- Recommendation: keep.

### "One grey tick means the server received it. Two grey means it reached the recipient's device ... Two blue means it was read."
- Source: WhatsApp FAQ on message checkmarks (primary WhatsApp help documentation)
- Source says: One grey = server received; two grey = delivered to device; two blue = read.
- Recommendation: keep.

### "your phone does it. It encrypts a slice of your recent chats and hands them straight to the new device, with the key wrapped in its own end-to-end message. You're not downloading your past; you're uploading it, phone to laptop."
- Source: https://engineering.fb.com/2021/07/14/security/whatsapp-multi-device/ (Meta Engineering, July 14, 2021)
- Source says: "When a companion device is linked, the primary device encrypts a bundle of the messages from recent chats and transfers them to the newly linked device." The key is "delivered to the newly linked device via an end-to-end encrypted message." This is a phone-to-device transfer; the server holds nothing readable to send.
- Note: "slice of your recent chats" is accurate — the Meta Engineering article uses "recent chats" without defining an exact window. The direction (phone → new device, not server → new device) is confirmed exactly.
- Recommendation: keep.

### "The sender now seals every message several times over, once per device. The server forwards several copies where it used to forward one."
- Source: https://engineering.fb.com/2021/07/14/security/whatsapp-multi-device/
- Source says: Client-fanout means "the WhatsApp client sending the message encrypts and transmits it N number of times to N number of different devices." The server receives and forwards each separately encrypted copy.
- Recommendation: keep.

### "Erlang ... was never built for raw number-crunching speed. What it was built for is holding millions of things at once without falling over."
- Source: https://erlangforums.com/t/what-are-some-possible-solutions-to-make-the-beam-faster-for-cpu-calculations/5417 and https://www.erlang-solutions.com/blog/beam-jvm-virtual-machines-comparing-and-contrasting/
- Source says: BEAM is not designed for CPU-bound computation — "number crunching is best left to the JVM, Go, or other languages which compile to native code"; BEAM's design goal is massive concurrency and soft real-time, not raw per-operation throughput.
- Recommendation: keep.

### "an in-memory store has to be replicated carefully — lose a node, and you lose state"
- Source: https://medium.com/@jlouis666/mnesia-and-cap-d2673a92850 and Mnesia documentation
- Source says: In-memory Mnesia tables lose data on node crash unless explicitly replicated to surviving nodes; Mnesia replication has well-documented split-brain weaknesses under network partition; in-memory tables have table-size limits and replication adds write overhead.
- Recommendation: keep.

### "the cost scales with the size of the group, not with how many people are typing"
- Source: https://highscalability.com/how-whatsapp-grew-to-nearly-500-million-users-11000-cores-an/ and substrate-notes group fan-out description
- Source says: Server-side fan-out means the server queues one copy per group member per message; delivery load is proportional to group membership count times message count, independent of how many members are actively sending.
- Recommendation: keep.

### "A server that can't read your messages can't search them for you, can't scan them for spam or abuse, and can't quietly rebuild your history on a new device."
- Source: https://arxiv.org/pdf/2106.05184v2 (academic study of WhatsApp spam under e2e encryption) and https://www.theregister.com/2021/09/07/whatsapp_privacy_propublica
- Source says: WhatsApp's e2e encryption prevents server-side content scanning; abuse detection relies on metadata and user reports, not message content; server cannot read and therefore cannot re-deliver ciphertext as readable history. All three constraints are accurate and uncontroversial in the security literature.
- Recommendation: keep.

### "Bare-metal boxes are cheap and fast at a steady scale, but they don't appear on demand the way cloud instances do."
- Source: https://medium.com/kuberiter/bare-metal-kubernetes-907597ce2780 and https://github.com/kubernetes/autoscaler/issues/1060
- Source says: Bare metal lacks cloud-style autoscaling; Kubernetes Cluster Autoscaler is not supported for on-premises bare-metal infrastructure because automatic machine provisioning is unavailable; you carry capacity and failures.
- Recommendation: keep.

---

## Partial

### "if your phone is dead or gone the moment you link, there's no history to inherit"
- Source: https://engineering.fb.com/2021/07/14/security/whatsapp-multi-device/
- Source says: History transfer comes from "the primary device" encrypting a bundle and transferring it — by implication, an absent or powered-off primary device cannot perform this transfer. The Meta Engineering article does not explicitly address the phone-offline-at-link-time scenario, and the WhatsApp Help Center FAQ page was inaccessible during this check.
- Delta: The inference is sound and consistent with the mechanism described, but no source explicitly states "if the phone is gone, no history is transferred." This is an engineering deduction, not a directly quoted claim.
- Recommendation: keep as written (the deduction is watertight from the described mechanism), or soften slightly to "if your phone is offline when you link, there may be no history to inherit."

---

## Unverified

(none)

---

## Contradicted

(none)
