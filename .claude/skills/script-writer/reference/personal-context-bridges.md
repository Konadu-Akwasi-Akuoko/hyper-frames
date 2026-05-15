# Personal context bridges — finding the "you've done this" moment

Move 10 in `sentence-rhythm.md` asks for one personal-context bridge per video — a moment
that connects the topic to something the viewer has done themselves. The audience
responds to these more than to almost any other single move (one comment about
VeraCrypt's mouse-movement key generation got 155 likes). Move 10 says *that* you need
one and *where* it goes. This file is about *finding* it. Its retention mechanism — the
curiosity of recognition — is explained in `rhythm-and-retention.md`.

**This file does not change the count.** One bridge per video is still usually enough,
and it still lives in the hook or the landing. This is a craft aid for a decision the
skill already asks you to make once — not a new required slot.

## A bridge is an action, not a fact

The failure mode is naming a fact the viewer "knows" instead of an action they have
*done*. "You use encryption every day" is a fact — it creates no recognition. "Every
time you generate an SSH key, create a TLS certificate, or encrypt a file" is an action
— the viewer remembers doing it. The bridge works because it triggers a specific memory,
not because it states something true.

Test: can the viewer picture themselves in the moment? "You open a text editor, press
the letter E" — yes. "Text rendering is something you interact with constantly" — no.

## Where to look in the substrate

The bridge is usually already in `substrate-notes.md`, in the **Load-bearing moments**
section or implied by the named concepts. The question to ask the substrate:

> What does the viewer physically *do* that this system sits underneath?

Every named system in the notes has a surface the viewer touches. A B-tree sits under
"every time you create a database table". A PRNG sits under "every time you generate an
SSH key". Rasterization sits under "you press the letter E and it appears". Find the
system's surface and you have found the bridge.

## Three patterns from the corpus

**The "every time you..." opening.** Names a recurring action, then immediately teases
the strangeness underneath it.
> "Every time you generate an SSH key, create a TLS certificate, or encrypt a file,
> something strange has to happen."

The action is the bridge; "something strange has to happen" is the subversion teased into
the same sentence. The bridge and Move 3's three-part list often share a sentence.

**The opening action as the bridge.** The viewer is placed *inside* a concrete action,
present tense, second person — the bridge and the hook are the same sentence.
> "You open a text editor, press the letter E, and it appears instantly."

The most economical form: no separate bridge sentence, the hook *is* the bridge.

**The "next time you..." reframe.** Sends the viewer back to the action they started
with, now understanding what it costs.
> "The next time you read a simple article online, remember what is happening."

This lands only if the prose *opened* on a concrete action — there has to be something to
send them back to. If the hook was abstract, the landing reframe has no anchor.

## Connecting an abstract system to a concrete action

When the topic is genuinely abstract — a memory barrier, a consensus algorithm, a garbage
collector — the bridge is harder but more valuable. Tactics:

- **Find the symptom, not the system.** The viewer hasn't "used a garbage collector",
  but they have watched an app freeze for half a second. The bridge is the symptom they
  have felt, not the mechanism they haven't seen.
- **Find the decision they've made.** They may not know B-trees, but they have chosen a
  primary key. The bridge is the choice, not the internals.
- **Find the thing they trust without thinking.** "Every HTTPS session your browser has
  negotiated" works because the viewer has trusted that lock icon thousands of times
  without once thinking about where the randomness came from.

## When a bridge doesn't land

- **It's generic.** "We've all used computers" is not a bridge. The action has to be
  specific enough to trigger one memory.
- **It's invented.** If the substrate doesn't connect to a viewer action, do not invent
  one — a forced "you've probably..." is worse than no bridge. Soften to one honest
  bridge, or let the strongest concrete moment carry the recognition on its own.
- **There are three of them.** More than one bridge dilutes the move. Pick the single
  strongest action and place it once.
