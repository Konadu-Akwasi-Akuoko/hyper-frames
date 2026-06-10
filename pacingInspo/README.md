# pacingInspo — scene-change & narration-pacing reference library

Whole-video pacing studies: how good creators time their scene changes against
their narration. Each entry is one ingested YouTube video — a deterministic
`<slug>-pace.json` manifest (machine truth), a mechanical `<slug>-pacing.md`
report (per-scene table), contact sheet(s) of one thumbnail per scene, and a
human-authored `Pacing:` note below. Produced by `tools/inspo-ingest pace`;
curated by hand. This library is about *temporal* craft (cut cadence,
narration alignment, hold lengths) — single-beat *motion* cadence lives in
`motionGraphicsInspo/`.

## Quick index

| slug | channel | runtime | scenes | cuts/min | median scene | wps | pacing in one line |
|---|---|---|---|---|---|---|---|
| [bytebytego-7-system-design-concepts](#bytebytego-7-system-design-concepts) | ByteByteGo | 10:44 | 29 | 2.61 | 15.4s | 2.41 | chaptered diagram explainer: long evolving branded canvases that breathe with the narration, cuts only at concept turns — with one 105s mega-hold carrying a whole sub-topic |
| [bytebytego-transformers-stepbystep](#bytebytego-transformers-stepbystep) | ByteByteGo | 10:03 | 11 | 0.90 | 2.7s | 2.36 | barbell pacing: a 95s cold-open hold, a frantic ~30s ad-read flurry, then one 8-minute evolving explainer canvas with no hard cuts |
| [cleo-deep-sea-unknown-species](#cleo-deep-sea-unknown-species) | Cleo Abram | 0:42 | 25 | 34.66 | 0.7s | 4.33 | Shorts machine-gun B-roll: a fresh image nearly every word through the setup, then two long holds that let the payoff and the punchline breathe |
| [cleo-how-old-diamonds-are](#cleo-how-old-diamonds-are) | Cleo Abram | 0:55 | 25 | 26.42 | 1.4s | 3.00 | Cleo Short, two-speed: a staccato word-by-word cold open, then long evolving timeline canvases that hold while the narration walks across them — cuts only when the visual subject changes |
| [cleo-nuclear-space-ship](#cleo-nuclear-space-ship) | Cleo Abram | 0:39 | 27 | 38.96 | 1.5s | 4.45 | relentless explainer cutting: a fresh visual roughly every breath (~1.5s), riding mid-sentence with almost no respect for clause or pause boundaries |
| [codehead-top-10-ides](#codehead-top-10-ides) | CodeHead | 6:12 | 144 | 22.11 | 1.7s | 2.86 | relentless listicle churn: ~22 cuts/min over a 1.67s median, every entry a B-roll/screen-recording montage, with word-by-word stutter bursts on emphasis and the sponsor read |
| [codingkoala-vercel-200m](#codingkoala-vercel-200m) | The Coding Koala | 6:27 | 165 | 24.51 | 2.0s | 3.09 | relentless mid-sentence B-roll churn: a fresh visual every ~2s riding straight over the narration, holds only for the chart payoffs and section-turn title cards |
| [codingsloth-docker-tutorial](#codingsloth-docker-tutorial) | The Coding Sloth | 11:53 | 424 | 35.19 | 1.3s | 4.17 | relentless meme-cut explainer: a new gag/screen roughly every breath (median 1.3s, 35 cuts/min), the only long holds being code/config screens that fill while the voice races |
| [codingsloth-get-rich-essay](#codingsloth-get-rich-essay) | The Coding Sloth | 15:02 | 637 | 41.53 | 1.1s | 3.70 | relentless mid-sentence cutting: a fresh visual roughly every breath (~1.1s), holds reserved for the few B-roll/data reveals, structure marked by title-card flashes not by slowing down |
| [devforge-200k-salaries-vanishing](#devforge-200k-salaries-vanishing) | DevForge | 6:46 | 134 | 18.64 | 1.8s | 3.08 | restless b-roll churn: a visual swap roughly every breath (median 1.78s) that ignores sentence seams, broken only by a handful of long monologue holds at the argument's pivots |
| [fireship-github-outage-news](#fireship-github-outage-news) | Fireship | 5:58 | 155 | 25.47 | 2.1s | 3.24 | relentless mid-sentence B-roll churn: a visual swap every ~2s that ignores sentence boundaries, holding only for the meme punchline and the sign-off |
| [latticx-cs-advice-tier-list](#latticx-cs-advice-tier-list) | Lattice | 11:34 | 89 | 6.49 | 5.9s | 3.42 | talking-head tier-list: brisk graphic swaps per ranked item (median ~6s), punctuated by 40s opinion-monologue holds where the face-cam argues and B-roll cuts vanish |
| [shadeofcode-underrated-ai-concepts](#shadeofcode-underrated-ai-concepts) | Shade of Code | 4:25 | 96 | 20.65 | 2.6s | 3.14 | relentless mid-sentence cutting: a fresh visual every ~2.6s that swaps under continuous fast narration, with cuts landing inside phrases far more than at sentence ends |
| [swagprof-every-language-7min](#swagprof-every-language-7min) | Swag Professor Explain  | 7:40 | 130 | 16.82 | 3.2s | 2.25 | listicle illustration-reel: a fresh logo/headshot/diagram every ~3s, cutting mid-sentence and never resting, with each of the 9 language segments its own visual chapter |
| [technetium-25-cybersec-terms](#technetium-25-cybersec-terms) | TECHNETIUM | 6:41 | 226 | 32.33 | 1.5s | 3.27 | machine-gun listicle: a visual change roughly every breath (~32 cuts/min, 1.48s median), each of 25 terms front-loaded by a big bold word-card then sprayed across stock b-roll |
| [bytebytego-chat-system](#bytebytego-chat-system) | ByteByteGo | 8:45 | 21 | 1.94 | 9.0s | 2.41 | chaptered whiteboard: minutes-long evolving canvases, cuts only at section turns |
| [awesome-real-problem](#awesome-real-problem) | Awesome | 10:11 | 146 | 10.51 | 3.4s | 3.35 | relentless mid-sentence cutting: a visual change every breath, holds only for quoted speakers |

## Entries

### bytebytego-chat-system

- Report: `bytebytego-chat-system-pacing.md`
- Manifest: `bytebytego-chat-system-pace.json`
- Sheet: `bytebytego-chat-system-scenes-sheet-001.png`
- Stats (from `aggregates`, mechanical copy): scene_count 21 · cuts_per_minute 1.94 ·
  soft_transition_count 3 · scene_duration_s median 9.00 / p25 5.68 / p75 24.44 /
  max 165.44 · longest_hold_s 165.44 · words_per_s_mean 2.41 ·
  pct_cuts_in_pause 0.05 · pct_sentence_aligned 0.35
- Source: https://www.youtube.com/watch?v=okrR1KXNLtA
- Pacing: One canvas per chapter, evolved rather than cut — the two longest
  "scenes" (104s and 165s) are continuous diagram builds where elements accrete
  and rearrange without ever swapping the frame, so the visual reset cadence is
  carried by in-scene animation, not by cuts. Hard swaps are reserved for
  chapter turns (their cut scores, 0.16–0.30, are 3–5× the in-section swaps)
  and land mid-sentence about two-thirds of the time, but a third snap to
  sentence ends — the narration bridges the cut so the topic handoff feels
  continuous. Narration is metronomic (~2.3–2.7 wps in almost every scene,
  no pause longer than 2s in 8:45); the outro abruptly switches register to
  1–7s card flips with two eased wipes.
- Use when: pacing a system-design or architecture explainer of ours — argues
  for fewer, bigger scene resets with long single-substrate evolution between
  them, and for letting the VO run through the cut instead of pausing on it.

### awesome-real-problem

- Report: `awesome-real-problem-pacing.md`
- Manifest: `awesome-real-problem-pace.json`
- Sheets: `awesome-real-problem-scenes-sheet-001.png`,
  `awesome-real-problem-scenes-sheet-002.png`
- Stats (from `aggregates`, mechanical copy): scene_count 146 · cuts_per_minute 10.51 ·
  soft_transition_count 38 · scene_duration_s median 3.38 / p25 1.26 / p75 5.57 /
  max 17.27 · longest_hold_s 17.27 · words_per_s_mean 3.35 ·
  pct_cuts_in_pause 0.00 · pct_sentence_aligned 0.04
- Source: https://www.youtube.com/watch?v=2AzUeddzxF0
- Pacing: A visual change roughly every clause — median scene 3.4s against
  ~200 WPM narration, with a quarter of all scenes under 1.3s (flash meme and
  reaction inserts on a 2–5 word phrase). Cuts almost never honor sentence
  structure (0% in pauses, 4% sentence-aligned): the frame changes mid-clause
  so the sentence pulls the viewer across the cut. Hard cuts and eased text
  builds interleave roughly 3:1, and the only real holds (8–17s) are quoted
  talking-head clips — the meta-pattern is "earn a hold with a primary source,
  spend it immediately on a cut burst."
- Use when: pacing a fast opinion/video-essay beat or a cold open — the
  reference for cutting mid-sentence on momentum; do not transplant onto
  explainer sections that need diagram comprehension time.

### bytebytego-7-system-design-concepts

- Report: `bytebytego-7-system-design-concepts-pacing.md`
- Manifest: `bytebytego-7-system-design-concepts-pace.json`
- Sheet: `bytebytego-7-system-design-concepts-scenes-sheet-001.png`
- Stats (from `aggregates`, mechanical copy): scene_count 29 · cuts_per_minute 2.61 · soft_transition_count 0 · scene_duration_s median 15.36 / p25 8.84 / p75 28.12 / max 105.08 · longest_hold_s 105.08 · words_per_s_mean 2.41 · pct_cuts_in_pause 0.00 · pct_sentence_aligned 0.68
- Source: https://www.youtube.com/watch?v=Qd9tJ3H_hPE
- Pacing: Slow and sectional: only 2.61 cuts/min across 29 scenes, median scene 15.4s but a wide spread (p25 8.8s / p75 28.1s) and a single 105.08s hold (scene 6) that walks through the CAP-theorem trade-off on one substrate without a cut. Narration is steady at 2.41 wps, so each cut lands at a new concept rather than a new breath — 68% of cuts are sentence-aligned and 0% fall in pauses, meaning the canvas evolves in place under continuous speech and only resets at section boundaries (the title-card turns visible in the sheet). The long holds earn their length by hosting animated diagrams (the consistent-hashing ring, circuit-breaker states) that mutate while the voice keeps talking; the shortest scenes (0.56s 'you might like', 2.48s 'Consistent') are punctuation, not pacing. soft_transition_count is 0 — every reset is a hard cut on a section turn.
- Use when: Pacing a system-design explainer of ours — argues for fewer, bigger resets with long single-substrate evolution (animate the diagram in place under continuous narration), cutting only when the concept changes, not every sentence.

### bytebytego-transformers-stepbystep

- Report: `bytebytego-transformers-stepbystep-pacing.md`
- Manifest: `bytebytego-transformers-stepbystep-pace.json`
- Sheet: `bytebytego-transformers-stepbystep-scenes-sheet-001.png`
- Stats (from `aggregates`, mechanical copy): scene_count 11 · cuts_per_minute 0.90 · soft_transition_count 1 · scene_duration_s median 2.71 / p25 1.44 / p75 6.49 / max 479.98 · longest_hold_s 479.98 · words_per_s_mean 2.36 · pct_cuts_in_pause 0.00 · pct_sentence_aligned 0.30
- Source: https://www.youtube.com/watch?v=avjX3QrYkls
- Pacing: The 11 detected scenes split into three regimes around a 2.36 wps narration: a 94.89s opening hold that lets the framing question breathe, a burst of nine ad-read cuts (scenes 2-10, durations 1.13-7.88s, median scene length only 2.71s) for the Clerk sponsor, then a single 479.98s scene (longest_hold_s = the full ~8 minutes) that carries the entire transformer explainer as one continuously-evolving canvas. cuts_per_minute is just 0.90 and soft_transition_count is 1 because nearly all the visual change happens IN-scene via diagram evolution, not at scene cuts. pct_cuts_in_pause is 0.00 and pct_sentence_aligned only 0.30, so the few real cuts land mid-thought (mostly inside the rapid ad read) rather than honoring sentence boundaries — the body teaches through animated transformation of one substrate, not through resets.
- Use when: Pacing a system-design or ML explainer of ours — argues for one big long-lived substrate that evolves continuously through the teaching, reserving hard cuts almost entirely for the front-loaded hook and a quarantined ad break.

### cleo-deep-sea-unknown-species

- Report: `cleo-deep-sea-unknown-species-pacing.md`
- Manifest: `cleo-deep-sea-unknown-species-pace.json`
- Sheet: `cleo-deep-sea-unknown-species-scenes-sheet-001.png`
- Stats (from `aggregates`, mechanical copy): scene_count 25 · cuts_per_minute 34.66 · soft_transition_count 0 · scene_duration_s median 0.67 / p25 0.33 / p75 1.79 / max 14.33 · longest_hold_s 14.33 · words_per_s_mean 4.33 · pct_cuts_in_pause 0.00 · pct_sentence_aligned 0.04
- Source: https://www.youtube.com/watch?v=MQwZdGiaPsw
- Pacing: Across 41.5s the median scene is just 0.67s against a brisk 4.33 words/s, so most of the video swaps the visual on roughly every breath — scenes 5-12 are a strict word-per-cut burst (eight tiles at ~0.33s each: 'to / discover / what / animals / - / are down / there.'). The cutting ignores grammar entirely (pct_sentence_aligned 0.04, pct_cuts_in_pause 0.00) — it rides the narration word-for-word, not sentence-for-sentence. The two earned exceptions are the answer reveal (scene 15, 6.25s, 14 words at a slowed 2.24 wps) and the big explainer block (scene 21, 14.33s, 47 words) — single substrates that hold while dense information lands, with 0 soft transitions meaning every reset is a hard cut.
- Use when: Pacing one of OUR vertical Shorts/CTA cut-downs — argues for word-rate B-roll churn through the hook and setup, with the only long holds reserved for the answer reveal and the one dense explainer beat.

### cleo-how-old-diamonds-are

- Report: `cleo-how-old-diamonds-are-pacing.md`
- Manifest: `cleo-how-old-diamonds-are-pace.json`
- Sheet: `cleo-how-old-diamonds-are-scenes-sheet-001.png`
- Stats (from `aggregates`, mechanical copy): scene_count 25 · cuts_per_minute 26.42 · soft_transition_count 0 · scene_duration_s median 1.38 / p25 0.46 / p75 2.08 / max 10.88 · longest_hold_s 10.88 · words_per_s_mean 3.00 · pct_cuts_in_pause 0.00 · pct_sentence_aligned 0.00
- Source: https://www.youtube.com/watch?v=B9vdFqX5qJc
- Pacing: Across 54.5s the median scene is 1.38s against 3.00 wps narration — fast on its face — but that median hides a bimodal shape: a staccato cold open (scenes 2-8) where each word of 'just / how old / diamonds / actually / are' gets its own ~0.42-0.46s tile, then three long holds that carry the explainer (10.88s on the 'if this is today / dinosaurs' timeline, 8.50s on the oldest-diamonds timeline, 6.50s on the oxygen-in-the-atmosphere timeline). Those long holds are earned: the camera sits on one evolving timeline substrate while narration walks new markers across it, so the visual reset rides the IDEA changing, not the sentence. pct_sentence_aligned is 0.00 and pct_cuts_in_pause is 0.00 (auto-caption word onsets land mid-phrase, and the Short never pauses), so cuts track when the visual SUBJECT swaps — pedestal diamonds, crown jewels, Earth — rather than grammar. soft_transition_count is 0: every boundary is a hard cut, and the 26.42 cuts/min average is inflated entirely by the punchy open and close around three patient middle canvases.
- Use when: Pacing a short, punchy explainer of ours where one timeline/scale substrate carries the spine — argues for a staccato word-by-word hook, then parking on a single evolving canvas for 6-11s and cutting only when the subject itself changes, not per sentence.

### cleo-nuclear-space-ship

- Report: `cleo-nuclear-space-ship-pacing.md`
- Manifest: `cleo-nuclear-space-ship-pace.json`
- Sheet: `cleo-nuclear-space-ship-scenes-sheet-001.png`
- Stats (from `aggregates`, mechanical copy): scene_count 27 · cuts_per_minute 38.96 · soft_transition_count 1 · scene_duration_s median 1.48 / p25 0.85 / p75 1.92 / max 3.17 · longest_hold_s 3.17 · words_per_s_mean 4.45 · pct_cuts_in_pause 0.00 · pct_sentence_aligned 0.08
- Source: https://www.youtube.com/watch?v=NV8jFpd4INk
- Pacing: Across 38.5s this runs 27 scenes at 38.96 cuts/min — a median hold of just 1.48s (p25 0.85s, p75 1.92s) against fast 4.45 words/s narration, so most shots carry only 3-8 words before the next visual lands. Cuts essentially ignore grammar: pct_sentence_aligned is 0.08 and pct_cuts_in_pause is 0.00 (every pause_before_s is 0.00 except one 0.21s gap), meaning the picture changes mid-clause to keep the eye moving while the voice runs continuously. The only real breathing room is two ~3.1s holds — the 'bringing all that fuel and oxygen is...' problem beat (sc9, 3.17s) and the '10 to 100 times more power' payoff stat (sc20, 3.12s) — earned by landing the central tension and the headline number. Soft transitions are basically absent (1 of 27); the entire rhythm is hard cuts, with the visual reset cadence outpacing the sentence cadence rather than tracking it.
- Use when: Reach for this when pacing a fast, dense explainer beat of ours where the visual must turn over every sentence-fragment to sustain energy — it argues for many short hard cuts riding mid-clause, reserving the only ~3s holds for the core problem statement and the headline payoff stat.

### codehead-top-10-ides

- Report: `codehead-top-10-ides-pacing.md`
- Manifest: `codehead-top-10-ides-pace.json`
- Sheets: `codehead-top-10-ides-scenes-sheet-001.png`, `codehead-top-10-ides-scenes-sheet-002.png`
- Stats (from `aggregates`, mechanical copy): scene_count 144 · cuts_per_minute 22.11 · soft_transition_count 6 · scene_duration_s median 1.67 / p25 0.69 / p75 3.35 / max 11.14 · longest_hold_s 11.14 · words_per_s_mean 2.86 · pct_cuts_in_pause 0.00 · pct_sentence_aligned 0.08
- Source: https://www.youtube.com/watch?v=TcOvs_DYMv0
- Pacing: At 22.11 cuts/min and a 1.67s median scene against 2.86 words/s narration, this is a screen-recording listicle that swaps visuals roughly every 5 spoken words and almost never lets a shot breathe (p25 0.69s, p75 3.35s). Cuts ignore prose structure — only 8% are sentence-aligned and 0% land in a pause (pct_cuts_in_pause 0.00) — because the editor is cutting to B-roll beats and on-screen demos, not to clauses. The longest holds (11.14s, 10.80s, 10.01s) are reserved for dense feature explanations (Windsurf's Cascade, WebStorm's refactor tools, the closing Scrimba CTA) where one screen-capture earns a sustained look, and only 6 of 143 boundaries are soft transitions, so the texture is overwhelmingly hard cuts. The most extreme region is a machine-gun stutter of ten consecutive 0.30s tiles (scenes 124-135) over the Scrimba sponsor read, plus word-by-word emphasis bursts (scenes 28-37, 76-84) that chop single words into their own frames.
- Use when: pacing a ranked-listicle or tool-roundup of ours — argues for a fast B-roll-driven floor (1-2s shots, cut to demo beats not sentences) with rare long holds saved for the single feature worth dwelling on, and a deliberate stutter-cut burst to punctuate the sponsor/CTA.

### codingkoala-vercel-200m

- Report: `codingkoala-vercel-200m-pacing.md`
- Manifest: `codingkoala-vercel-200m-pace.json`
- Sheets: `codingkoala-vercel-200m-scenes-sheet-001.png`, `codingkoala-vercel-200m-scenes-sheet-002.png`
- Stats (from `aggregates`, mechanical copy): scene_count 165 · cuts_per_minute 24.51 · soft_transition_count 6 · scene_duration_s median 1.96 / p25 1.25 / p75 3.00 / max 7.46 · longest_hold_s 7.46 · words_per_s_mean 3.09 · pct_cuts_in_pause 0.00 · pct_sentence_aligned 0.29
- Source: https://www.youtube.com/watch?v=Aiv9NwyfGnM
- Pacing: 165 scenes across 6.4 minutes at 24.5 cuts/min — a median 1.96s hold (p25 1.25s, p75 3.00s) against fast 3.09 words/s narration, so the visual resets roughly every six spoken words. Cutting is deliberately un-grammatical: pct_sentence_aligned is just 0.29 and pct_cuts_in_pause is 0.00, meaning ~71% of cuts land mid-sentence and none wait for a breath — the edit churns B-roll, screen-grabs, and brand cards underneath continuous speech rather than punctuating it. The few long holds (max 7.46s, plus 7.0–7.33s) are reserved for payoff beats — the '$200M / three-layer business model' chart reveals, the enterprise brand-name roll, the V0 ARR stat — while ~16% of scenes fire under a second in stutter bursts on emphasis words ('Vercel', 'numbers', 'limits'). Only 6 of 165 boundaries are soft transitions; the texture is overwhelmingly hard cuts.
- Use when: pacing a fast retention-driven explainer of ours where narration never stops — argues for many short mid-sentence visual swaps over a continuous VO, reserving the only long holds for the chart/stat payoff beats and section-turn title cards.

### codingsloth-docker-tutorial

- Report: `codingsloth-docker-tutorial-pacing.md`
- Manifest: `codingsloth-docker-tutorial-pace.json`
- Sheets: `codingsloth-docker-tutorial-scenes-sheet-001.png`, `codingsloth-docker-tutorial-scenes-sheet-002.png`, `codingsloth-docker-tutorial-scenes-sheet-003.png`, `codingsloth-docker-tutorial-scenes-sheet-004.png`, `codingsloth-docker-tutorial-scenes-sheet-005.png`
- Stats (from `aggregates`, mechanical copy): scene_count 424 · cuts_per_minute 35.19 · soft_transition_count 5 · scene_duration_s median 1.30 / p25 0.80 / p75 1.98 / max 17.23 · longest_hold_s 17.23 · words_per_s_mean 4.17 · pct_cuts_in_pause 0.00 · pct_sentence_aligned None
- Source: https://www.youtube.com/watch?v=DQdB7wFEygo
- Pacing: Narration runs hot at 4.17 words/s and the visuals match it: 424 scenes over ~12 min, 35.19 cuts/min, median scene 1.30s (p25 0.80s, p75 1.98s) — a fresh tile (reaction shot, Docker logo, sketch overlay, terminal) almost every breath, with effectively zero held beats in the bottom half. Cuts are NOT pause-aligned (pct_cuts_in_pause 0.00) and ride mid-sentence on the joke cadence rather than sentence structure (sentence-alignment wasn't computed — the source subs are unpunctuated). The five longest holds are the exception that proves the rule: 17.23s / 79 words on the compose.yml file, then 9.63s, 9.43s and 9.03s screens — all dense code/config canvases that stay put while typed-on content accumulates and the voice keeps sprinting; soft transitions are almost absent (5 of 424), so the whole video is hard-cut energy punctuated by a handful of evolving code screens.
- Use when: pacing a fast, joke-driven tutorial of ours where energy must never sag — argues for hard-cutting a new visual every 1-2s and reserving the only long single-substrate holds for code/config screens that fill on-screen while narration sprints.

### codingsloth-get-rich-essay

- Report: `codingsloth-get-rich-essay-pacing.md`
- Manifest: `codingsloth-get-rich-essay-pace.json`
- Sheets: `codingsloth-get-rich-essay-scenes-sheet-001.png`, `codingsloth-get-rich-essay-scenes-sheet-002.png`, `codingsloth-get-rich-essay-scenes-sheet-003.png`, `codingsloth-get-rich-essay-scenes-sheet-004.png`, `codingsloth-get-rich-essay-scenes-sheet-005.png`, `codingsloth-get-rich-essay-scenes-sheet-006.png`, `codingsloth-get-rich-essay-scenes-sheet-007.png`
- Stats (from `aggregates`, mechanical copy): scene_count 637 · cuts_per_minute 41.53 · soft_transition_count 12 · scene_duration_s median 1.13 / p25 0.73 / p75 1.80 / max 6.23 · longest_hold_s 6.23 · words_per_s_mean 3.70 · pct_cuts_in_pause 0.00 · pct_sentence_aligned 0.08
- Source: https://www.youtube.com/watch?v=tjW_5ZAttGo
- Pacing: 637 scenes over 15 minutes is 41.5 cuts/min with a 1.13s median scene (p25 0.73s, p75 1.80s) against 3.70 words/s narration, so most tiles carry only 3-7 words before the visual swaps. Cuts almost never wait for the talker: pct_cuts_in_pause is 0.00 and only 8% are sentence-aligned, so the edit slices straight through clauses ('how much work it / takes,' lands on two tiles). The handful of long holds (max 6.23s, plus the 4-5s scenes at 44, 47, 69, 78, 180, 303, 339) all earn it by parking on a single payload, a big dollar figure ($81M, $2M Apple bounty), a list reveal, or a key B-roll screen recording, while the 12 soft transitions are rare blends amid an otherwise all-hard-cut grammar.
- Use when: calibrating an upbeat, high-energy explainer of ours where momentum matters more than dwell, this argues for a sub-2s reset cadence that cuts on emphasis words rather than sentence ends, with deliberate 4-6s holds parked only on the one number or screen the viewer must actually read.

### devforge-200k-salaries-vanishing

- Report: `devforge-200k-salaries-vanishing-pacing.md`
- Manifest: `devforge-200k-salaries-vanishing-pace.json`
- Sheets: `devforge-200k-salaries-vanishing-scenes-sheet-001.png`, `devforge-200k-salaries-vanishing-scenes-sheet-002.png`
- Stats (from `aggregates`, mechanical copy): scene_count 134 · cuts_per_minute 18.64 · soft_transition_count 7 · scene_duration_s median 1.78 / p25 1.04 / p75 2.96 / max 30.33 · longest_hold_s 30.33 · words_per_s_mean 3.08 · pct_cuts_in_pause 0.03 · pct_sentence_aligned 0.23
- Source: https://www.youtube.com/watch?v=2ahtzV2OPwE
- Pacing: At 18.64 cuts/min the median scene runs just 1.78s (p25 1.04s, p75 2.96s) against a brisk 3.08 words/s narration, so most cuts land mid-phrase rather than at sentence boundaries — only 23% are sentence-aligned and a near-zero 3% fall in a pause, confirming the visuals are sliced to keep motion alive, not to honor grammar. The cadence isn't uniform: four long holds (scenes 31 at 19.8s, 65 at 26.6s, 104 at 30.3s, plus the 14.8s opening stat card) park the camera on a single substrate exactly where the script delivers its dense explanatory monologues — the 2021-22 hiring-boom history, the junior-developer collapse, and the three-tier bifurcation. Soft transitions are rare (7 total), so the texture is almost entirely hard cuts. The shape is a rapid-fire reaction/b-roll bed that resets every second or two, with the editor deliberately slowing to a long single-canvas hold whenever an argument needs room to breathe.
- Use when: Reach for this when pacing a fast retention-driven explainer of ours that wants relentless visual variety over the line — it argues for cutting on energy not on sentence seams, while reserving a few long single-substrate holds for the dense argument beats.

### fireship-github-outage-news

- Report: `fireship-github-outage-news-pacing.md`
- Manifest: `fireship-github-outage-news-pace.json`
- Sheets: `fireship-github-outage-news-scenes-sheet-001.png`, `fireship-github-outage-news-scenes-sheet-002.png`
- Stats (from `aggregates`, mechanical copy): scene_count 155 · cuts_per_minute 25.47 · soft_transition_count 2 · scene_duration_s median 2.13 / p25 1.31 / p75 2.94 / max 7.88 · longest_hold_s 7.88 · words_per_s_mean 3.24 · pct_cuts_in_pause 0.00 · pct_sentence_aligned 0.10
- Source: https://www.youtube.com/watch?v=d53Zk28esmU
- Pacing: 155 scenes over 358s = 25.5 cuts/min, with a 2.13s median hold against fast 3.24 words/s narration — roughly one fresh visual every 6-7 words, mid-phrase. The cutting is almost entirely insensitive to prose structure: pct_sentence_aligned 0.10 and pct_cuts_in_pause 0.00, so swaps land on whatever word arrives, not on clause ends or breaths (there are no real narration pauses to hide behind). Soft transitions are vestigial (2 total) — this is a hard-cut montage. The few long holds are deliberate beats, not breathers: the 7.88s max is split between the cold-open 'final final V2 fix' bit (sc4) and the dense end-card outro (sc154, 32 words crammed in), while the rapid 0.33-0.88s flickers cluster on stat callouts and the 'developers, developers' meme (sc104-106) for comedic machine-gun emphasis.
- Use when: calibrating a fast news/explainer of ours where dense B-roll carries energy — argues that decoupling cuts from sentence structure and swapping visuals every ~2s reads as urgency, but only works at Fireship's word-density; for slower narration it would feel jittery, so reserve this cadence for the hot-take montage stretches, not the teaching beats.

### latticx-cs-advice-tier-list

- Report: `latticx-cs-advice-tier-list-pacing.md`
- Manifest: `latticx-cs-advice-tier-list-pace.json`
- Sheet: `latticx-cs-advice-tier-list-scenes-sheet-001.png`
- Stats (from `aggregates`, mechanical copy): scene_count 89 · cuts_per_minute 6.49 · soft_transition_count 13 · scene_duration_s median 5.93 / p25 2.77 / p75 11.03 / max 41.00 · longest_hold_s 41.00 · words_per_s_mean 3.42 · pct_cuts_in_pause 0.00 · pct_sentence_aligned 0.06
- Source: https://www.youtube.com/watch?v=hQrOLDxKHzA
- Pacing: Median scene runs 5.93s against a steady 3.42 words/s narration (~20 words per visual), so most ranked items get one or two graphic swaps before the next entry — 6.49 cuts/min, brisk but not frantic. The shape is bimodal: a dense cloud of 1-3s micro-cuts (the 41 short scenes under p25=2.77s, mostly rapid B-roll under fast quips) bracketing a handful of 40s+ monologue holds (scene 34 = 41.0s / 133 words, scene 49 = 39.33s / 149 words) where the presenter stops cutting and just argues a point to camera. Cuts almost never honor sentence structure (pct_sentence_aligned 0.06, pct_cuts_in_pause 0.00) — every boundary lands mid-sentence on a word onset, so the visual reset is driven by the changing on-screen graphic/B-roll rather than by clause breaks. With only 13 soft transitions in 89 scenes, the reset vocabulary is overwhelmingly hard cuts; in-scene evolution carries the long holds while the short scenes machine-gun.
- Use when: pacing a ranked/tier-list or opinion explainer of ours — argues for a brisk per-item cut cadence (~6s graphic swaps) deliberately interrupted by long un-cut monologue holds when a single point needs to breathe and persuade.

### shadeofcode-underrated-ai-concepts

- Report: `shadeofcode-underrated-ai-concepts-pacing.md`
- Manifest: `shadeofcode-underrated-ai-concepts-pace.json`
- Sheet: `shadeofcode-underrated-ai-concepts-scenes-sheet-001.png`
- Stats (from `aggregates`, mechanical copy): scene_count 96 · cuts_per_minute 20.65 · soft_transition_count 4 · scene_duration_s median 2.58 / p25 1.63 / p75 3.48 / max 7.97 · longest_hold_s 7.97 · words_per_s_mean 3.14 · pct_cuts_in_pause 0.01 · pct_sentence_aligned 0.42
- Source: https://www.youtube.com/watch?v=BpIYoaFfW1w
- Pacing: At 20.65 cuts/min and a 2.58s median scene (p25 1.63s / p75 3.48s) under fast 3.14 words/s narration, this is a dense talking-head-plus-graphics edit that resets the frame roughly every 8 spoken words. Only 42% of cuts are sentence-aligned and essentially none (1%) fall in a pause, so most boundaries chop mid-phrase to keep visual novelty ahead of the voice — the cut rides momentum, not grammar. There are almost no held beats: the longest hold is just 7.97s (scene 60, a single sustained sentence about scaling surprising everyone), and the four soft transitions are isolated dissolves rather than a recurring rhythm. The section-turn title cards (Calibration / Second / Third / Last / Emergent Capabilities) are the only real structural anchors, but even they get the same short 1.5-3.5s treatment as everything else, so the whole video reads as one continuous high-churn texture rather than chaptered breathing room.
- Use when: pacing a fast, punchy concept-explainer of ours where energy must stay high — argues for frequent small visual swaps under continuous narration rather than long evolving substrates, but warns that cutting mid-phrase with no held beats gives the eye nowhere to rest

### swagprof-every-language-7min

- Report: `swagprof-every-language-7min-pacing.md`
- Manifest: `swagprof-every-language-7min-pace.json`
- Sheets: `swagprof-every-language-7min-scenes-sheet-001.png`, `swagprof-every-language-7min-scenes-sheet-002.png`
- Stats (from `aggregates`, mechanical copy): scene_count 130 · cuts_per_minute 16.82 · soft_transition_count 0 · scene_duration_s median 3.17 / p25 1.75 / p75 4.62 / max 10.70 · longest_hold_s 10.70 · words_per_s_mean 2.25 · pct_cuts_in_pause 0.00 · pct_sentence_aligned 0.14
- Source: https://www.youtube.com/watch?v=Nx5Kk-WEhAg
- Pacing: 130 scenes in 7:40 yields 16.82 cuts/min and a 3.17s median hold against a brisk 2.25 words/s narration — a new visual lands roughly every 7 words, never letting a frame breathe. The cuts ignore prose structure entirely: pct_cuts_in_pause is 0.00 and only 14% are sentence-aligned, so the video changes images on the noun being spoken (a logo, a creator's headshot, a memory diagram), slicing scenes as short as 0.53s on a single word ('However,', 'browsers,'). The few longer holds (max 10.70s, p75 only 4.62s) sit on dense capability run-downs — the C 'fast and efficient programs' beat, the Java portability list — where one substrate absorbs a multi-clause sentence. Zero soft transitions: every reset is a hard cut, and the per-language chaptering shows up as visual clustering (Python ~22 cuts, C ~17) rather than any pause-based pacing.
- Use when: pacing a fast listicle / 'X explained' explainer of ours — argues for illustration-per-noun hard cutting on a ~3s median, one mini visual chapter per item, and reserving the rare 8-10s hold for a dense capability list rather than honoring sentence boundaries

### technetium-25-cybersec-terms

- Report: `technetium-25-cybersec-terms-pacing.md`
- Manifest: `technetium-25-cybersec-terms-pace.json`
- Sheets: `technetium-25-cybersec-terms-scenes-sheet-001.png`, `technetium-25-cybersec-terms-scenes-sheet-002.png`, `technetium-25-cybersec-terms-scenes-sheet-003.png`
- Stats (from `aggregates`, mechanical copy): scene_count 226 · cuts_per_minute 32.33 · soft_transition_count 9 · scene_duration_s median 1.48 / p25 0.87 / p75 2.56 / max 5.53 · longest_hold_s 5.53 · words_per_s_mean 3.27 · pct_cuts_in_pause 0.00 · pct_sentence_aligned 0.49
- Source: https://www.youtube.com/watch?v=sTujlreIhPg
- Pacing: Median scene runs 1.48s against a 3.27 words/s delivery — that's only ~4-5 words per cut, so the picture changes nearly every clause, not every sentence. The cadence is relentless and even: p25 0.87s to p75 2.56s, with the longest hold just 5.53s, so nothing ever truly rests; the slightly longer holds (the 3.5-5.5s scenes) land on the meatiest explanation lines (the firewall 'monitors every packet', the OSINT and ransomware payoffs) while sub-0.5s flashes punch single words like 'online', 'payload', 'backdoor', 'dark'. Cuts honor sentence structure only half the time (pct_sentence_aligned 0.49) and zero land in pauses (pct_cuts_in_pause 0.00, words/s never drops to silence) — this editor cuts ON the talking, mid-phrase, riding momentum rather than breath. Soft transitions are almost absent (9 of 226), so the engine is hard cuts; the only recurring 'reset' is the typographic term-card that re-anchors each of the 25 chapters.
- Use when: Pacing a fast definitional listicle of ours (a 'N terms/tools explained' explainer) — argues for a hard-cut-per-clause spray over stock/diagram b-roll with a bold word-card stamping each new item, and explicitly against waiting for sentence ends or pauses to cut.
