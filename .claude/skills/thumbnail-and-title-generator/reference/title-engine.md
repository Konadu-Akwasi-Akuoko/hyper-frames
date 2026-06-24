# Title engine

The corpus-derived rules for writing the paired YouTube title for each
thumbnail variant. Source: `research/thumbnail-title-corpus-2026-06-09/ANALYSIS.md`
§3 ("Title engine — what correlates with HIGH views") and §5
(winners-vs-losers throughline), distilled from 11 competitor profiles
across the coding/tech lane.

The thumbnail and the title do **different jobs**, so they must say
**different things**. This file is the asymmetry: the thumbnail makes the
bigger claim, the title is the searchable, grounded version of it.

## The two jobs

| Surface | Job | Optimized for |
|---|---|---|
| Thumbnail headline | Win the click in the feed | UPPERCASE 2-tone punch + a concrete `.mono-tell` stat — can make the BIGGER claim |
| YouTube title | Win search and the algorithm | Sentence case, carries ONE searchable noun, one scannable line |

If the title and the thumbnail say the same thing you lose one of two
ways: the title is too punchy/undifferentiated to rank, or the thumbnail
is too keyword-stuffed to pull the click. Let them play different roles.
The leverage is in the asymmetry.

### The Specimen claim/ground split

The SPECIMEN signature already encodes this split in the thumbnail. The
2-tone punch row makes the sweeping emotional claim; the `.mono-tell`
line (`// <span class="stat">98.8%</span> of all websites`) plants the
concrete, authority-grounded number. The **title carries the noun that
makes that stat searchable** — never the stat's swagger.

- Thumbnail (claim): punch row `JAVASCRIPT WON` + mono-tell
  `// 98.8% of all websites`.
- Title (ground): "Why JavaScript runs 98.8% of the web" — softer,
  carries the searchable noun `JavaScript`, defensible.

The thumbnail can claim bigger than the title would dare; the title is
the technical, searchable version of that claim.

## Winning patterns

Pull from these five shapes. Each names a *specific thing* and rides one
emotional beat on top of it — never a mood instead of a noun.

1. **One concrete searchable noun + a 1-2 word emotional verb.** Name a
   specific target — a company, a tool, a dollar figure, a tribe — then
   load one short verb on it. Winners: `CLAUDE / CRACKED`, an `AI CEO …
   finally`, `$10,000,000`. The noun is specific (Claude, Postgres, ML
   frameworks, $10M, CERN), never a category mood ("coding," "tech").
2. **Curiosity gap that resolves to a named enemy or a reversal.** A
   withheld referent only works if the gap pays off in a *nameable
   stake*. The trailing "…" alone is NOT the edge — the strongest losers
   also trail off. The edge is the reversal (`…Until It Couldn't`,
   `…And That's Your Opportunity`) or the named enemy/stake behind the
   ellipsis.
3. **Open What / Why / How naming a real thing.** Broad evergreen-
   curiosity questions massively outperform niche/meme framings —
   "Why do computers suck at math?" is the single highest-view item in
   the corpus. The question must name a real, searchable noun, not a
   vibe.
4. **Assumption-flip / contrarian claim.** "Frameworks don't matter
   anymore," "Dinosaurs were weirder than we thought." Flip a belief the
   target audience holds, anchored on a concrete noun.
5. **Audience-identity / status hook** (advice content only). Name the
   tribe ("computer science students need to hear this") or promise
   elite status ("think like A GENIUS programmer"). Beats generic
   how-tos for advice/mindset topics.

The rigid completeness formula — "Every [broad category] explained in
[N] minutes!" — wins ONLY on maximally-searched nouns (APIs, ML
frameworks). Narrow the category and it craters; do not reach for it on
a niche topic.

## Avoid

Every entry here is a documented corpus floor.

- **Vague pronoun with no named target.** "It's a disease…," "We are all
  not ok…," "The dumbest thing ever…" — curiosity without an
  identifiable enemy. The most common failure mode in the doom lane.
- **Generic mindset/advice with no concrete noun.** "Stay Average,"
  "Nobody Taught You," "my most valuable programming advice," "Code
  Easily." Bottom-floor pattern.
- **Plain scolds / commands with no curiosity.** "Quit Cybersecurity
  Now," "STOP STUDYING CYBER SECURITY."
- **"For fun" / list-for-its-own-sake** with no deliverable, no N-minute
  promise, no no-prior-knowledge promise. "Ranking random programming
  languages for fun," "Canon events."
- **Pure doom-restatement without a reversal or in-group secret.** "Why
  the coding-is-over narrative is wrong" reads as commentary, not threat,
  and stalls.
- **Breaking the proven house formula on the same topic.** A
  question/colon variant cost one channel ~340x the views of the
  "Every… in N minutes!" version of the *same* ML topic. Formula
  discipline is itself a lever.
- **Verbatim duplication of the thumbnail** (or its sentence-cased
  twin). If the punch row says `JAVASCRIPT WON`, do not title it
  "JavaScript won." Rewrite to the searchable, grounded version.

## Length sweet spot — 38-46 characters

The strongest channels cluster tight: 35-48 chars (awesome-coding 35,
shadeofcode 36, cleoabram 38, technetiumm 41, codehead 41, latticx 42,
fireship 44). The longest-titled channel (52) pays for it with cramped,
less-legible titles. **Aim 38-46 chars** — long enough for one
searchable noun plus one emotional beat, short enough to survive mobile
truncation. Hard cap 100, but anything past ~70 truncates in most feed
layouts.

Other mechanics: sentence case (UPPERCASE is reserved for the
thumbnail); no emoji, no SHOUT words, no keyword stuffing; one
parenthetical aside maximum; one `:` or `—` maximum.

## The one-searchable-noun rule

Carry **exactly ONE** concrete searchable noun, front-or-mid, and let the
emotion ride on it — never instead of it. The winners' noun is *specific*
(Claude, Postgres, ML frameworks, $10M, CERN); the abstract floors drop
the noun for pure vibe and lose search AND click.

**Litmus test:** *If a viewer searched the one noun in your title, would
this video be a satisfying result?* If no, the noun is too vague —
swap "coding" for "Rust," "tech" for "Postgres," "AI" for "Claude."

## SEO-research routing

When `<video-dir>/seo/research.json` is loaded (probed at Step 2 of the
skill), the digest from Step 4 feeds the per-variant routine. Apply these
on top of the base rules. See the "Using SEO research" section below for
the per-signal codification.

The routing in one line: **the title is where SEO signals bind** — the
thumbnail rides on emotion, the title rides on the noun viewers actually
type. When the corpus is thin or open, fall back to your own judgment per
the base rules; never skip the routine because the data was sparse.

## Per-variant writing routine

For each of the 3 thumbnail variants:

1. Read the variant's punch row and `.mono-tell` aloud. What is the BIG
   claim, and what is the concrete number?
2. Identify the ONE searchable noun. If SEO data is loaded, prefer a
   top-3 entry from `signals.top_nouns`.
3. Write the title that delivers the search-grounded version of the
   claim, pinned on that noun, riding one of the five winning patterns.
   Often this lands close to the working title from `outline.md` — that's
   expected; the working title already had SEO instinct.
4. Check against the rules: 38-46 chars, sentence case, one searchable
   noun, different shape from the thumbnail, passes the litmus test.
5. Vary form across variants — sometimes a Why/How question, sometimes a
   declarative claim, sometimes an assumption-flip. The contact sheet
   shows them side by side; identical-shaped titles waste the review
   surface. Ideally each of the 3 carries a *different* top-3 noun.

## Reference title shape — a prior, not a mandate

Every `thumbnailInspo/` entry now carries the real title that ran with that
layout, classified as `title_shape` + `title_pattern`. When you pick a reference
for a variant, read its `title_shape` and **default to writing the paired title in
that shape** — the layout and the title shape are a proven pair, so they should
move together.

But the shape is a *prior*, not a lock. Override it when the engine says so:

- If SEO data (`signals.top_nouns`, `signals.saturation_warnings`) or one of the
  five winning patterns makes a different shape stronger for OUR noun, take it.
- Never inherit `every-x-explained` unless the noun is maximally searched, and
  never inherit `meme-skit` for our lane — both are documented floors.
- **Never copy the reference's actual title words.** The shape transfers; the words
  are always ours, grounded and searchable per the rules above. This is the title
  analogue of "lift the layout, never the pixels."

## Using SEO research

When `seo/research.json` is loaded, apply these in addition to the base
routine:

- **Always carry a search anchor.** Include at least one of the top 3
  entries from `signals.top_nouns`. Without it you lose search reach
  regardless of how sharp the claim is.
- **Avoid verbatim saturation patterns.** If `signals.saturation_warnings`
  lists `"how X works"` and your draft is "How JavaScript works," you are
  competing head-on with 5+ recent >100K-view incumbents. Rephrase
  ("What JavaScript really does," "Inside the JavaScript engine") or
  commit to the lane deliberately because your thumbnail claim is
  genuinely sharper. Recall: topic choice can outweigh craft — the same
  template on an AI-panic noun beat a commodity-CSS noun by ~60-70x.
- **Prefer demand phrases when natural.** Entries in
  `signals.demand_phrases` are recurring autocomplete completions — real
  queries. If one fits the variant's claim shape without contortion, use
  it verbatim. Don't force-fit.
- **Vary across variants.** With 3 variants, ideally each carries a
  different noun from the top-3 list. Don't orbit them all on the same
  noun — that wastes the A/B surface.
- **Empty signals are informative, not blocking.** If `top_nouns` is
  empty (sparse niche) or `saturation_warnings` is empty (open lane),
  draft from your own judgment per the base rules. Never skip the routine
  because the data was thin.

## Pairing examples

| Thumbnail (punch + mono-tell) | Paired title | Why it works |
|---|---|---|
| `JAVASCRIPT WON` / `// 98.8% of all websites` | Why JavaScript quietly took over the web | Softens "won" → "quietly took over"; carries `JavaScript`; assumption-flip shape |
| `POSTGRES WON THE WAR` / `// 90% of new apps` | Why Postgres beat every other database | Narrows the sweep to a searchable comparison; carries `Postgres` + `database` |
| `YOUR PASSWORD IS SLOW ON PURPOSE` / `// 600,000 hashes` | Why good password hashing is intentionally slow | Swaps imperative claim for descriptive; same noun, calmer register; carries `password hashing` |

In every row the title is **softer, more searchable, and less
clickbait-shaped** than the thumbnail. That asymmetry is the point.

## What this skill does NOT do for titles

- **A/B-test titles.** YouTube's native mechanism handles that
  independently of thumbnails — you can test 3 thumbnails × 3 titles. The
  skill ships ONE paired title per variant; the user picks, the YouTube
  console tests.
- **Generate descriptions, tags, chapters, or end screens.** Out of
  scope. Title and thumbnail are the click-pull surfaces; the rest is
  metadata (see `description-writer`).
