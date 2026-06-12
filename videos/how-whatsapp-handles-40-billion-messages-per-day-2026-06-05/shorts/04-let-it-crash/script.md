<!-- HOOK -->
WhatsApp's engineers wanted their code to crash.

<!-- COUNTER-TWIST -->
On purpose. There's an actual engineering philosophy for it: "let it crash."

<!-- BODY -->
Most systems are built to never fail — wrap everything in safety nets, try to recover from every error. WhatsApp's backend does the opposite, and it works because of the language underneath it: Erlang, born in the telecom world.

Every single phone that connects gets its own tiny, isolated process on the BEAM virtual machine. <!-- TTS: BEAM = "beam" --> Not a thread. Just one featherweight worker per person — millions of them running at once.

So when one breaks, it doesn't try to heal. It just dies, alone. A supervisor notices, spawns a fresh clean copy, and the other million processes never even feel it.

None of it comes free, though. Erlang is a niche language with a hiring pool to match, and it was never built for raw number-crunching speed. What it was built for is holding millions of things at once without falling over.

<!-- CTA -->
So what does a tiny team actually buy by betting everything on a language almost nobody hires for? To find out, subscribe.
