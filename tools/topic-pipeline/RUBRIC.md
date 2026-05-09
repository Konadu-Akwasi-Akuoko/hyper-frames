# topic-pipeline — scoring rubric v2

Status: design lock-in, pre-implementation. Nothing in `fetch.py` / `merge.py` /
`render.py` reflects this yet. This file is the agreement we point at before
code moves.

## Channel premise

Curiosity-driven videos about computing, software engineering, and technology.
The bar: a topic qualifies if it hits **at least one universal-experience
hook** *and* the honest answer requires computing knowledge.

- In: CAPTCHAs, why fonts look different on different screens, why phones get
  warm during video calls, passkeys, why search results take 200ms, why
  autocorrect feels psychic.
- Out: ARM64 register conventions, git rebase strategies, 5-leg office chairs.
- Borderline (case-by-case): Postgres MVCC — devs only by default, but if
  framed as "why your database doesn't lose your data when two people edit at
  once," it crosses over.

Technical content is welcome when it's also curious. Curious content is
welcome when the answer involves computing. Either alone is out of niche.

## Discovery sources (additive, no source replaces another)

### Tier A — text aggregators (kept, full discovery weight)
HN · Reddit (programming, compsci, webdev, databases, cpp, rust, golang) ·
Lobste.rs · daily.dev. Their job: surface stories before any video channel
does. Their *upvotes* are a minor scoring signal (see below); their
*coverage* is the primary value.

### Tier B — style-reference channels (NEW, drives demand + inspiration)
Channels we imitate. Their hits are demand-relevant for our channel. Their
recent titles become the daily-refreshed mood board for the angle generator.

- Pawel (`@pawel_code_stuff`) — closest house-style match
- Veritasium (`@veritasium`) — gold-standard curiosity hooks
- Cleo Abram (`@CleoAbram`) — optimistic-tech, AI/product angles
- Tom Scott (`@TomScottGo`) — universal-curiosity title shapes
- Computerphile (`@Computerphile`) — depth ceiling, brand-clarity titles
- Kurzgesagt (`@kurzgesagt`) — universal-touch curiosity at scale, animated
- rabbithole (`@rabbithole`) — small but exact-niche
- CodeAesthetic (`@CodeAesthetic`) — systems-curiosity, often deep
- Branch Education (`@BranchEducation`) — computing internals visualized
- Welch Labs (`@WelchLabs`) — visual math/computing
- LearnThatStack (`@LearnThatStack`) — closest direct comparable after Pawel
- CodeSource (`@CodeSource`) — software-history-as-curiosity
- TheCodingGopher (`@TheCodingGopher`) — computing-deep explainer-format

### Tier C — watchlist channels (NEW, monitor only — do not imitate)
Channels we monitor for topic coverage but whose title patterns we do *not*
feed into the inspiration set. Audience overlap is partial; their coverage of
a topic doesn't disqualify us. Used only for cooldown-window awareness.

- Shadeofcode (`@Shadeofcode`) — bro-dev hot takes
- awesome-coding (`@awesome-coding`) — opinion / industry commentary
- TheCodingSloth (`@TheCodingSloth`) — career / lifestyle clickbait
- devopstoolbox (`@devopstoolbox`) — tooling comparison
- Fireship (`@Fireship`) — high-velocity tech, partial overlap

### Tier D — YouTube cold search (NEW, scouting + demand)
Per-candidate `ytsearch10:<topic>`. Three jobs:
1. Demand signal (top-result view counts).
2. Cooldown check (any tracked channel in the top results?).
3. **Channel discovery** — if the same untracked channel keeps appearing on
   topics in our niche, flag it for human review and possible promotion to
   Tier B or Tier C.

## Scoring rubric (6 axes, 20 each → composite /120, displayed /100)

Three axes are properties of the **source/topic**, three are properties of
the **angle**. Each candidate carries 1–5 angles; angle composite uses the
candidate-level axes plus the angle-level axes.

### Source/topic axes

**1. Demand (0–20)** — *do people want this on video?*
Four sub-caps that sum:

| Sub-signal | Cap | Notes |
|---|---|---|
| Tier B reference-channel performance | 0–8 | View counts on the most-similar style-reference video. >1M = 8, 100K–1M = 5, 10K–100K = 3, <10K or none = 0. |
| Tier D cold-search top-result views | 0–5 | Median view count of the top 5 cold-search results. |
| YouTube autocomplete presence | 0–3 | 3 if the topic phrase autocompletes prominently, 1 if a related phrase does, 0 otherwise. |
| Tier A aggregator breadth | 0–4 | Breadth-not-depth: 1 source = 1, 2 = 2, 3 = 3, 4 = 4. Upvote *counts* are ignored once the source is registered. |

The aggregator cap is intentional: HN/Reddit/Lobsters/daily.dev voters are
not the YouTube audience. They are excellent at *discovery* and weak at
*demand-prediction*. Capping at 4/20 (20% of demand, ~3% of composite) keeps
their voice in the room without letting them dominate.

**2. Evergreen (0–20)** — kept from v1.
Mechanical regex on title/URL: ephemeral keywords (release, v1.0, today,
launches, raises, acquisition) penalize; evergreen keywords (internals, deep
dive, how X works, anatomy of, from scratch, under the hood) reward. URL
paths smelling of release-notes / changelogs penalize further. Default base 14.

**3. YT competition + cooldown (0–20)**
Search YouTube for the topic. Score:
- 20 = no high-quality video on this topic exists.
- 14 = one or two videos exist but old, low-engagement, or beginner-only.
- 8 = multiple recent videos but none high production quality.
- 0 = saturated; reference channel covered it well at scale.

Cooldown overlay: if a Tier B (style-reference) channel published a video on
this topic **within the last 30 days**, force this axis to ≤4 unless the
candidate's angle is meaningfully distinct from the reference video's angle
(judged in the angle generator). Tier C coverage triggers a softer penalty
(at most −4). Coverage older than 30 days is fair game — old hits actually
*indicate demand* (e.g. Techquickie's 2017 CAPTCHA video at 1.88M views
proves long-tail demand 8 years later). Cooldown is about head-on
competition, not demand decay; the two are separate.

### Angle axes (per angle, 1–5 angles per candidate)

**4. Audience reach (0–20)** — *who has experienced the thing?*
- 20 = every internet user (CAPTCHAs, password rules, autocorrect, Wi-Fi)
- 14 = every computer user (file-save dialogs, fonts, lossy JPEGs)
- 8 = every working developer (git, regex, JSON)
- 4 = every backend engineer (consensus, MVCC, CAP)
- 0 = a sub-niche (specific ISA dialects, kernel fastpath internals)

**5. Curiosity hook (0–20)** — *does the angle shape into a Tier B–style title?*
The LLM must attempt to phrase the title in 3 of these 5 hook patterns and
score how natural the fit is:
- Hidden-mechanism reveal — *"The X inside every Y"*, *"Why Y actually does X"*
- Counterintuitive twist — *"Why X is harder/slower/weirder than you think"*
- Personal-stake question — *"How easy is it to X?"*, *"Why can't I X?"*
- Hyper-claim with story — *"The most X Y ever made"*
- Mystery / unsolved — *"The X nobody can explain"*

If the topic resists 4+ patterns, it's a build-log topic, not a curiosity
topic. Score reflects how naturally a curious non-expert would form the
question on their own. The angle generator's outputs are the test data: if
all 5 produced titles feel forced, the angle scores low.

**6. Computing depth (0–20)** — *does the honest answer involve computing?*
Independent of curiosity; this keeps the channel on-brand.
- 20 = central computing topic (algorithms, OS internals, networking
  protocols, cryptography, compilers, distributed systems primitives,
  rendering pipelines, computer vision, ML internals).
- 14 = adjacent — answer touches computing meaningfully but isn't the core.
- 8 = answer mostly non-computing but has a computing angle if pulled.
- 0 = answer doesn't involve computing (mechanical engineering, biology
  alone, pure history with no computing component).

### Composite

```
composite = demand + evergreen + yt_competition
          + audience_reach + curiosity_hook + computing_depth
display   = round(composite / 1.2)   # 0–100 for the dashboard
best      = angle with max composite for the candidate
```

## Multi-angle generator (kept from v1, gains inspiration mode)

Per candidate, generate 1–5 angles:
- Angle 1 = the article's own framing (always present, scored honestly even
  if low — sometimes the article framing is the right video).
- Angles 2–5 = reframes, each meaningfully distinct, each a viable
  curiosity-driven 5–10 min video on its own.

**New: inspiration mode.** During angle generation, the LLM is given the top
3–5 most-similar Tier B titles from that day's competitor feed. These act
as a daily-refreshed mood board, keeping our title patterns aligned with
what's currently performing in our niche.

**New: cooldown-adjacent generation.** If Tier B coverage of the topic
exists within 30 days, the generator is told to produce angles
*meaningfully adjacent* to the existing video's angle. Direct duplicates of
recent reference-channel framings are forbidden.

## Auto-discovery loop

Tier D cold search returns top videos for each candidate. If the same
untracked channel surfaces ≥3 times across candidates in a single day, OR
≥5 times across a rolling 7-day window, write the channel handle to
`data/channels-pending-review.json` so the operator can decide whether to
promote to Tier B (style-reference) or Tier C (watchlist).

## Worked examples (sanity-check the rubric)

### Example 1 — "Google Cloud Fraud Defence is just WEI repackaged" (currently scores 31, would score…)

- Demand: ref-channel hit = Techquickie 2017 CAPTCHA at 1.88M (8/8) +
  cold-search median ~500K (5/5) + autocomplete strong (3/3) +
  HN+Reddit (2/4) = **18/20**
- Evergreen: 14 default, no ephemeral hits = **14/20**
- YT competition: many CAPTCHA videos exist, none on the WEI angle
  specifically, no Tier B coverage within 30 days = **14/20**
- Best angle ("How does a CAPTCHA actually decide you're human?"):
  - Audience reach: every internet user = **20/20**
  - Curiosity hook: fits 4/5 patterns (hidden mechanism, counterintuitive,
    personal-stake, mystery) = **20/20**
  - Computing depth: computer vision + ML + browser fingerprinting + adversarial bots = **18/20**
- Composite: 18+14+14+20+20+18 = **104** → display **87/100**.

### Example 2 — "Building a web server in raw arm64 assembly" (currently scores 87, would score…)

- Demand: no ref-channel hit on aarch64 server topic (0/8) + cold-search low (1/5)
  + autocomplete weak (0/3) + Lobsters+Reddit (2/4) = **3/20**
- Evergreen: 14 default, no ephemeral hits = **14/20**
- YT competition: many "build a web server" videos exist, none in pure aarch64
  assembly, no Tier B coverage = **16/20**
- Best angle ("Everything that happens between accept() and send()"):
  - Audience reach: every backend engineer = **6/20**
  - Curiosity hook: weak fit on all 5 patterns; "everything that happens
    between accept() and send()" is closer to a build-log than a curious
    question = **6/20**
  - Computing depth: syscalls, kernel networking = **20/20**
- Composite: 3+14+16+6+6+20 = **65** → display **54/100**.

### The inversion we wanted

|  | v1 score | v2 score | direction |
|---|---|---|---|
| WEI / CAPTCHA story | 31 | 87 | ↑ ↑ ↑ |
| ARM64 web server | 87 | 54 | ↓ ↓ |

The rubric correctly inverts the ranking on the two cases we used as
calibration. Before any code change, we should hand-rescore the day's
remaining 18 top-by-v1 candidates against this rubric to confirm the
ordering matches the operator's gut.

## Open questions (decide before implementation)

1. **Reference-channel similarity matching.** "Most-similar Tier B title"
   needs a definition. Options: (a) keyword-tag overlap, (b) embedding
   cosine similarity, (c) LLM-judged "is this the same topic?". (c) is most
   accurate, slowest, most expensive — probably the right call given low
   daily volume.

2. **Cold-search cost.** `ytsearch10:` per candidate × 60 candidates ≈ 600
   per-video metadata fetches per day. yt-dlp handles this fine but it's
   ~5–15 minutes of wall-clock. Acceptable for a daily run; flag if it
   creeps higher.

3. **Composite display normalization.** Divide by 1.2 to land /100, or
   accept /120? Dashboard UI assumes /100 — easier to keep that and divide.

4. **Tier C cooldown softness.** Currently spec'd as "at most −4" — needs a
   concrete formula. Probably: −2 if Tier C covered in last 30 days, −4 if
   in last 14 days.
