In 2014, WhatsApp was moving 40 billion messages a day on roughly 550 servers — run by a team of about 32 engineers. A team that small should not have been able to move that much. Here's exactly how.

This is a deep dive into WhatsApp's system design — the real architecture behind one of the largest messaging systems ever built, not the whiteboard version. We follow a single message from the moment your thumb hits send: the persistent socket, the FunXMPP binary protocol, the per-connection Erlang process on the BEAM, the in-RAM Mnesia routing table, server-side fan-out, store-and-forward queues, and end-to-end encryption with the Signal Protocol.

If you've ever studied WhatsApp system design for an interview, this is the actual engineering it's based on — why the numbers never quite add up, why the ticks on your screen are the architecture leaking through, and why a do-less culture of ~14 million users per engineer was the whole point.

Chapters
0:00  The 40-billion-message machine
0:27  One socket, kept open for hours
1:19  FunXMPP: shrinking the message
1:43  The actor model and Erlang
2:14  "Let it crash" supervision
2:51  Mnesia: routing held in RAM
3:43  Server-side fan-out
4:34  Store-and-forward and the ticks
5:43  End-to-end encryption
6:57  Multi-device and client-side fan-out
7:37  Bare metal: FreeBSD and hot code
9:02  Scaling to millions per box
9:58  14 million users per engineer
10:49  One message, start to finish

Sources & further reading
• How WhatsApp Grew to ~500M Users, 11,000 Cores (Rick Reed, 2014 talk) — HighScalability: https://highscalability.com/how-whatsapp-grew-to-nearly-500-million-users-11000-cores-an/
• Scaling to Millions of Simultaneous Connections (2012) — Rick Reed, WhatsApp / Erlang Factory: https://www.slideshare.net/milkers/scaling-to-millions-of-simultaneous-connections-by-rick-reed-from-whatsapp
• Four numbers that explain why Facebook acquired WhatsApp — Sequoia Capital: https://sequoiacap.com/article/four-numbers-that-explain/
• WhatsApp hits 64 billion messages in a day (April 2, 2014) — TIME: https://time.com/46895/whatsapp-handles-64-billion-messages-a-day/
• Open Whisper Systems partners with WhatsApp (Nov 2014) — Signal: https://signal.org/blog/whatsapp/
• How WhatsApp enabled multi-device capability (client-side fan-out, 2021) — Meta Engineering: https://engineering.fb.com/2021/07/14/security/whatsapp-multi-device/

Which of WhatsApp's trades would you have made differently — betting the backend on Erlang, holding the whole routing table in RAM, or running bare metal instead of the cloud? Tell me in the comments. Want a part two that goes deep on the Signal Protocol — X3DH, the Double Ratchet, and multi-device encryption? Say so and I'll build it.

Subscribe if taking a system apart like this is your idea of a good time — that's the whole channel.

#WhatsApp #SystemDesign #SoftwareArchitecture
