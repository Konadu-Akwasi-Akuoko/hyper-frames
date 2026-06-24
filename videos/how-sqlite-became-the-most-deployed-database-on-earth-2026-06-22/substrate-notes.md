# How SQLite became the most-deployed database on earth — substrate notes

Runtime target: 7 min · ~1,190 words · Kind = long · Spine A (origin story → world)
Full materials + sources + correction guardrails: `research/dossier.md` (the invention boundary).

## Named concepts
- Serverless / in-process — SQLite is a library linked into the app; no separate server process to crash.
- Single-file database — whole DB (tables, indexes, schema) is one ordinary file you can copy/email/move.
- "Competes with fopen()" — verbatim positioning: not a rival to Oracle, a replacement for opening a file by hand.
- Public-domain dedication — not MIT/BSD; no copyright at all; drop it into anything, no permission, no fee.
- 100% MC/DC test coverage — modified condition/decision coverage, the avionics-grade bar.

## Real dated incidents
- 2000 — D. Richard Hipp writes damage-control (valve-isolation) software for the US Navy.
- 2000-08-17 — SQLite 1.0 ships, two days before USS Oscar Austin (DDG-79) is commissioned (19 Aug 2000).
- Page updated 2026-04-21 — sqlite.org's own "over one trillion databases in active use" estimate.

## Concrete numbers and figures
- ~590× — test code vs library code (155.8 KSLOC core vs 92,053 KSLOC tests, as of v3.42.0 / 2023-05-16).
- ~1 billion — fuzz mutations dbsqlfuzz throws per day; FOUR independent test harnesses.
- >1 trillion (1e12) — SQLite's OWN hedged estimate of active database files; hundreds per phone × ~4B phones.
- Through 2050 — pledged support window + on-disk-format backward compatibility.

## Named people and organizations
- D. Richard Hipp — sole original author, still project lead.
- Hwaci (Hipp, Wyrick & Co.) — husband-and-wife NC company; employs all SQLite devs; source in Fossil, not GitHub.
- Ships in: every Android/iPhone/Mac/Windows; Chrome, Firefox, Safari. A350 maintenance log. US Library of Congress recommended format.
- Forward: WASM-in-browser, Turso/libSQL, Cloudflare D1, Litestream/LiteFS.

## Load-bearing moments
- The failing server on the warship → "why do we even need a server? why don't you just write one?" — the seed of everything.
- The paradox: the most-deployed database on Earth has no company, no marketing, no owner — given away, not conquered.

## Honesty guardrails (dossier §8 — do not violate)
- "destroyer," NEVER "battleship." A350 = maintenance LOGGING, not safety-critical flight control.
- Trillion / "most-deployed" = SQLite's OWN estimate — attribute, never present as audited census.
- Four harnesses (not three); MC/DC testing predates the A350 (don't causally link them).

## SEO context (seo/research.json, 2026-06-22 — added post-draft, for title/description/thumbnail)
- Niche is tutorial-dominated (top nouns: python, tutorial, create, beginners, course). Our origin-story explainer is the under-served lane — story/opinion entries are rare but overperform (the libSQL video at 538K). Don't chase tutorial nouns.
- Zero saturation warnings: the "how SQLite became…" framing is uncontested. Front-load "SQLite"; discovery will skew browse/suggested over search, so title + thumbnail must win on curiosity, not keyword match.
- "World's most-used SQL database" is a real in-the-wild competitor phrasing — our "most-deployed" promise matches how SQLite is actually described. Keep it.
