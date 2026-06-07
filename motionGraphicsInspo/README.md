# motionGraphicsInspo — the motion reference index

The canonical motion-graphics reference for this project's videos. Unlike a folder
of look stills, every entry here teaches **motion** — the cadence that separates a
scene that's merely synced from one that's *alive*: what enters, in what order, the
easing and overshoot, where it settles, the camera move.

Each reference is derived from a real YouTube clip (a beat someone got right) into
two artifacts plus a written note:

- a **hero still** (`<slug>.png`) — the at-a-glance look,
- a **keyframe strip** (`<slug>-strip.png`) — several frames of the beat tiled
  left-to-right, so the *staging* (what appears when) is legible in one image,
- a **`Motion:` note** in this index — the *cadence* a still sequence can't encode
  (timing, ease, overshoot, drift).

> Why a strip and not a GIF: an animated GIF read by an agent collapses to its
> first frame — motion is invisible. A tiled strip reads in full. So motion reaches
> the reader as **strip + note**, never as animation.

## How this index is read (progressive disclosure, two tiers)

The reader is the **`scene-design-decider`** subagent (dispatched per chunk by
`video-director`), which does its own retrieval. The index is built in two tiers so
that retrieval stays cheap as the library grows:

1. **Scan the `## Quick index` table first.** One compact row per entry — `slug`,
   `archetype`, `motion` verbs, `energy`, `mood`, and a one-line `use-when`. This is
   the search surface: match a beat's *meaning* to a row from text alone. The table
   stays scannable even at a hundred entries; reading it is a few hundred tokens, not
   the whole library.
2. **Drill into the matching `## Entries` block, and open *only* that entry's strip.**
   When a row fits the beat in hand, jump to its full entry (the `Motion:` note carries
   the cadence the row can't) and `Read` its `<slug>-strip.png` for the staging. Don't
   vision-parse the whole folder — the two tiers exist so you open at most a couple of
   strips per decision.
3. **Adapt the cadence — never reproduce the scene.** A reference may land in the same
   *family* as your block; it must not be the same thing. Copy the reasoning (the
   stagger, the settle, the push), invent the scene. Lifting a reference's literal
   layout makes the work derivative and homogenises the channel. Citing nothing is a
   first-class outcome — most beats fit no entry; this is **not a quota**.

## Entry schema — two parts per reference

Every reference contributes **both** a Quick-index row **and** a full Entries block,
kept in sync (same slug, same PNG pair).

**Quick-index row** (one line in the `## Quick index` table):

```
| [<slug>](#<slug>) | <archetype> | <verb>, <verb> | <energy> | <mood> | <one-line use-when> |
```

**Entries block** (the full detail under `## Entries`):

```
### <kebab-slug>
- Hero: `<slug>.png` · Strip: `<slug>-strip.png`
- Tags: motion=[<verb>, <verb>] · archetype=<archetype> · energy=<energy> · mood=<mood>
- Use when: <one line — the beat meaning this fits>
- Motion: <2-4 sentences — what enters, in what order, easing/overshoot, where it settles, camera move>
- Motion-metrics: energy=<calm|measured|punchy|frenetic> · cadence=<punctuated|continuous> · spatial=<localized|full-frame> · gate=<eased|continuous> · src=scan
  (flow: motion_energy=<m> · eased_energy_share=<s> · sparsity=<p> · spatial_concentration=<c> · mov_texture=<t>)
- Source: <youtube-url> @ <MM:SS-MM:SS>
```

The `### <kebab-slug>` heading is what the Quick-index row's `[<slug>](#<slug>)` link
anchors to, so the reader jumps straight from row to detail.

The `Motion-metrics:` line carries **objective measured values** computed by a `scan`
pass over the source — distinct from the human-judged `energy`/`mood` in the `Tags:`
line, which are curatorial reads of mood, not measurements. It is present **only for
scan-sourced entries** and is omitted entirely for clip-mode hand-captured ones (which
have no manifest to copy from). The four categorical tokens (`energy`, `cadence`,
`spatial`, `gate`) are what `scene-design-decider` ranks on as a **secondary signal**
beneath the prose `Tags:`/`Motion:`; the parenthetical raw floats are provenance, not
something the reader matches on.

### Tag vocabulary

A controlled core so the index stays scannable — extend a dimension when a beat
genuinely needs a word that isn't here, but prefer an existing one.

- **motion** (multi-value, the cadence verbs): `stagger`, `overshoot`, `settle`,
  `slide-in`, `wipe`, `mask-reveal`, `marker-sweep`, `typewriter`, `count-up`,
  `morph`, `snap`, `pop`, `scale-bloom`, `kinetic-type`, `parallax-push`,
  `parallax-drift`, `camera-orbit`, `draw-on`, `card-flip`, `accordion-reflow`,
  `blur-rack`, `glitch`, `particle`.
- **archetype** (the layout family): `stat-hero`, `kinetic-type`, `diagram-build`,
  `side-cutout`, `split-contrast`, `quote-card`, `checklist`, `code-reveal`,
  `timeline`, `map`, `device-mockup`, `collage`, `title-card`, `lower-third`.
- **energy**: `calm` · `measured` · `punchy` · `frenetic`.
- **mood**: `neutral` · `serious` · `playful` · `triumphant` · `tense` · `ominous`
  · `warm` · `clinical`.

## Adding a reference

Use the **`motion-inspo-add`** skill — it runs the backing tool
(`tools/inspo-ingest`, which downloads the bounded clip, scene-detects the
keyframes, and tiles the strip), then reads the strip and authors the `Tags:` /
`Use when:` / `Motion:` lines (the judgment the tool can't make) and appends **both**
the Quick-index row and the Entries block below. Keep every `<slug>.png` /
`<slug>-strip.png` pair in sync with exactly one row and one entry.

---

## Quick index


| Slug | Archetype | Motion | Energy | Mood | Use when |
|---|---|---|---|---|---|
| [dual-label-kinetic-type-over-icon-pedestal-6mpsq](#dual-label-kinetic-type-over-icon-pedestal-6mpsq) | kinetic-type | kinetic-type, pop, settle | punchy | tense | two opposing words frame a stakes-defining either/or |
| [vertical-timeline-cards-drop-stagger-6mpsq](#vertical-timeline-cards-drop-stagger-6mpsq) | timeline | stagger, slide-in, settle | measured | serious | a sequence of events stacks up to explain how something changed over time |
| [glass-skyscraper-rises-from-black-6mpsq](#glass-skyscraper-rises-from-black-6mpsq) | device-mockup | draw-on, scale-bloom, settle | measured | neutral | an entity or platform is established as it is introduced |
| [logo-with-ring-draw-on-and-checklist-6mpsq](#logo-with-ring-draw-on-and-checklist-6mpsq) | logo | draw-on, particle, pop | punchy | triumphant | a brand or tool is spotlighted as the payoff of a point |
| [glass-feature-cards-cycle-flip-pl4sk](#glass-feature-cards-cycle-flip-pl4sk) | quote-card | slide-in, card-flip, settle | punchy | warm | a sequence of named tradeoffs cycles forward, each card swapping in for the last |
| [node-graph-morph-to-triangle-pl4sk](#node-graph-morph-to-triangle-pl4sk) | diagram-build | morph, scale-bloom, settle | punchy | serious | a connected system collapses into a single deploy or build symbol as the payoff |
| [checklist-panel-scale-push-pl4sk](#checklist-panel-scale-push-pl4sk) | checklist | scale-bloom, parallax-push, slide-in | punchy | neutral | a step-by-step instruction list zooms up to fill frame as the active how-to |
| [logo-chevron-wipe-into-dollar-particle-field-pl4sk](#logo-chevron-wipe-into-dollar-particle-field-pl4sk) | title-card | wipe, particle, snap | frenetic | playful | a brand mark hands off to a swarm of repeated icons as a fast scene transition |
| [parallax-corridor-push-kinetic-type-wcixo](#parallax-corridor-push-kinetic-type-wcixo) | kinetic-type | parallax-push, kinetic-type, slide-in | measured | serious | a transition that pulls the viewer forward into the next idea while a word lands |
| [dashboard-ui-mockup-reveal-caption-card-wcixo](#dashboard-ui-mockup-reveal-caption-card-wcixo) | device-mockup | slide-in, mask-reveal, settle | measured | neutral | a product or tool is introduced and its interface needs to be shown off |
| [document-card-tumble-in-overshoot-wcixo](#document-card-tumble-in-overshoot-wcixo) | quote-card | slide-in, overshoot, settle | measured | neutral | a quoted notice or release note is dropped in as a callout over a colored field |
| [kinetic-date-then-red-map-morph-wcixo](#kinetic-date-then-red-map-morph-wcixo) | map | kinetic-type, morph, draw-on | frenetic | tense | a date or location beat hits hard and a region shape needs to slam onto screen |
| [logo-over-rising-fire-then-doc-slide-ffx0s](#logo-over-rising-fire-then-doc-slide-ffx0s) | title-card | particle, slide-in, settle | punchy | ominous | a brand or institution is framed as the thing under fire — heat building beneath a logo before the receipt drops |
| [sketch-draw-to-glow-burn-title-ybgv0](#sketch-draw-to-glow-burn-title-ybgv0) | title-card | draw-on, scale-bloom, glitch | punchy | playful | a segment's title card stamps in as the show's signature ident |
| [tumbling-logo-collage-into-countup-chart-ybgv0](#tumbling-logo-collage-into-countup-chart-ybgv0) | collage | parallax-drift, count-up, draw-on | frenetic | triumphant | a scale stat lands as the payoff after a flurry of brand logos |
| [rotating-particle-torus-training-viz-ybgv0](#rotating-particle-torus-training-viz-ybgv0) | diagram-build | particle, camera-orbit, settle | punchy | ominous | an abstract system or training process is visualized as it churns |
| [benchmark-table-to-scatter-chart-wipe-ybgv0](#benchmark-table-to-scatter-chart-wipe-ybgv0) | diagram-build | wipe, slide-in, settle | frenetic | clinical | a dense benchmark comparison resolves into a single readable chart |
| [live-shot-to-dashboard-stat-cards-vparw](#live-shot-to-dashboard-stat-cards-vparw) | stat-hero | wipe, count-up, settle | punchy | neutral | a real-world clip hands off to a data dashboard that lands the headline numbers |
| [list-rows-marker-sweep-torn-strip-vparw](#list-rows-marker-sweep-torn-strip-vparw) | checklist | marker-sweep, pop, settle | punchy | playful | a specific row in a list or feed gets singled out as the point that matters |
| [ui-app-grid-pricing-panel-slide-vparw](#ui-app-grid-pricing-panel-slide-vparw) | device-mockup | slide-in, settle, stagger | measured | neutral | a product UI pivots from an overview grid to reveal a pricing or detail panel |
| [year-counter-roll-motionblur-temye](#year-counter-roll-motionblur-temye) | kinetic-type | count-up, slide-in, blur-rack | punchy | neutral | a date or version ticks forward to mark progression through a timeline |
| [code-editor-blur-rack-retype-temye](#code-editor-blur-rack-retype-temye) | code-reveal | blur-rack, typewriter, settle | measured | neutral | code transforms from a bare stub into the finished implementation as the explanation lands |
| [brand-logo-wall-pop-stagger-temye](#brand-logo-wall-pop-stagger-temye) | collage | pop, stagger, overshoot | punchy | playful | a roster of names or brands assembles to show breadth of adoption |
| [hdd-annotation-arrow-data-block-march-ycvya](#hdd-annotation-arrow-data-block-march-ycvya) | diagram-build | draw-on, slide-in, snap | punchy | playful | a mechanism is explained by annotating a real object with moving callouts |
| [word-stamp-pop-over-broll-8esmu](#word-stamp-pop-over-broll-8esmu) | kinetic-type | pop, snap | punchy | playful | a single keyword punches in to label or punctuate the moment |
| [strikethrough-stamp-over-caption-8esmu](#strikethrough-stamp-over-caption-8esmu) | kinetic-type | snap, wipe, pop | punchy | playful | a stated cliche gets contradicted or struck down on the punchline |
| [code-list-with-sticker-badge-swoop-in-silsu](#code-list-with-sticker-badge-swoop-in-silsu) | code-reveal | slide-in, snap, pop | frenetic | playful | a code/package list gets punctuated by a punchy headline call-out as the payoff |
| [red-stamp-stat-slam-over-skull-render-silsu](#red-stamp-stat-slam-over-skull-render-silsu) | stat-hero | snap, overshoot, settle | punchy | ominous | two alarming numbers land back-to-back as the gut-punch of a section |
| [orange-marker-sweep-on-tweet-thread-silsu](#orange-marker-sweep-on-tweet-thread-silsu) | quote-card | marker-sweep, draw-on | measured | serious | highlighting the damning line inside a screenshotted post or quote |
| [annotation-to-analytics-dashboard-reveal-silsu](#annotation-to-analytics-dashboard-reveal-silsu) | diagram-build | wipe, draw-on, slide-in | punchy | clinical | cutting from a flagged detail to the broader data that backs it up |
| [code-report-logo-glitch-bloom-v0b68](#code-report-logo-glitch-bloom-v0b68) | title-card | glitch, scale-bloom, snap | punchy | playful | a recurring segment ident slams on screen to mark the start of a beat |
| [opus-version-tag-pop-over-mascot-v0b68](#opus-version-tag-pop-over-mascot-v0b68) | kinetic-type | pop, snap, scale-bloom | frenetic | playful | a punchy label or version name pops to punctuate a cut off a UI screen |
| [highlight-then-orange-swirl-warp-out-v0b68](#highlight-then-orange-swirl-warp-out-v0b68) | title-card | glitch, morph, parallax-push | frenetic | playful | a designed transition tears away the current scene to hand off to the next |
| [title-card-flare-bloom-reveal-txxlk](#title-card-flare-bloom-reveal-txxlk) | title-card | scale-bloom, snap, settle | punchy | playful | a segment-break stinger announces the next chunk of the video |
| [logo-over-flames-flicker-hold-txxlk](#logo-over-flames-flicker-hold-txxlk) | title-card | pop, particle, settle | punchy | playful | a mascot or brand mark lands as a punchline with a year stamp |
| [interstitial-kinetic-time-skip-card-txxlk](#interstitial-kinetic-time-skip-card-txxlk) | kinetic-type | pop, snap, scale-bloom | frenetic | playful | a comedic time-skip or 'meanwhile' cut jumps the narrative forward |
| [code-terminal-into-radial-graph-build-vrajk](#code-terminal-into-radial-graph-build-vrajk) | code-reveal | draw-on, camera-orbit, particle | frenetic | tense | a technical concept resolves from raw code into a generated visual payoff |
| [logo-collage-into-editorial-title-card-vrajk](#logo-collage-into-editorial-title-card-vrajk) | title-card | morph, kinetic-type, mask-reveal | punchy | playful | a roster of brands collapses into a single named headline as the segment title lands |
| [ai-headline-collage-red-marker-strike-jl3pc](#ai-headline-collage-red-marker-strike-jl3pc) | collage | marker-sweep, scale-bloom, collage | punchy | tense | a loaded term gets named, then negated or called into question as the turn |
| [course-cards-stagger-in-then-slide-reveal-jl3pc](#course-cards-stagger-in-then-slide-reveal-jl3pc) | checklist | stagger, slide-in, settle | measured | neutral | a curriculum or feature set is enumerated, each item landing one after the next |
| [single-word-swap-center-dark-swt68](#single-word-swap-center-dark-swt68) | kinetic-type | kinetic-type, snap, settle | measured | serious | a sentence is delivered word-by-word to land a reframing claim |
| [course-card-scale-pop-icon-swt68](#course-card-scale-pop-icon-swt68) | device-mockup | scale-bloom, pop, settle | measured | warm | a named product or module is introduced as a tidy hero card |
| [gamified-correct-xp-streak-swt68](#gamified-correct-xp-streak-swt68) | checklist | pop, slide-in, count-up | punchy | playful | a success or reward moment needs a satisfying gamified payoff |
| [caption-to-code-title-crossfade-einri](#caption-to-code-title-crossfade-einri) | title-card | mask-reveal, settle | measured | neutral | a spoken rhetorical question hands off to the named example that answers it |
| [chained-method-code-build-line-reveal-einri](#chained-method-code-build-line-reveal-einri) | code-reveal | mask-reveal, stagger, settle | measured | clinical | a multi-step transformation is walked through one operation at a time |
| [highlight-bar-grow-under-caption-einri](#highlight-bar-grow-under-caption-einri) | kinetic-type | wipe, scale-bloom | measured | neutral | a single phrase needs a sweeping underline emphasis as it is read aloud |
| [course-card-to-phone-mockup-reveal-einri](#course-card-to-phone-mockup-reveal-einri) | device-mockup | slide-in, settle | measured | neutral | an abstract concept lands on a concrete product or app screen as proof |
| [doodle-gag-brain-drop-slap-bpgjq](#doodle-gag-brain-drop-slap-bpgjq) | kinetic-type | pop, snap, kinetic-type | punchy | playful | a beat lands a comedic 'figuring it out the hard way' punchline |
| [wordmark-shrinks-into-navbar-xkhza](#wordmark-shrinks-into-navbar-xkhza) | title-card | scale-bloom, settle, slide-in | punchy | warm | a brand or section title lands then docks itself as the running header |
| [phone-mockup-slides-up-code-output-xkhza](#phone-mockup-slides-up-code-output-xkhza) | device-mockup | slide-in, settle | measured | neutral | a result or app screen needs to enter as a tangible device the viewer can read |
| [glowing-cube-particle-dissipate-xacwy](#glowing-cube-particle-dissipate-xacwy) | title-card | particle, parallax-drift | frenetic | ominous | a scene needs an energetic particle-burst transition or atmospheric backdrop as one moment dissolves into the next |
| [sliding-poster-title-cards-on-starfield-hbszg](#sliding-poster-title-cards-on-starfield-hbszg) | title-card | slide-in, wipe, snap | punchy | playful | a rapid montage punches through a sequence of named chapters or labeled exhibits |
| [dispersing-particle-field-thinning-out-hbszg](#dispersing-particle-field-thinning-out-hbszg) | collage | particle, parallax-drift, settle | frenetic | tense | a dense swarm thins to a few survivors as the narration narrows a field down to the essentials |
| [italic-label-over-vfx-to-titlecard-fn7ca](#italic-label-over-vfx-to-titlecard-fn7ca) | title-card | kinetic-type, settle, mask-reveal | punchy | triumphant | a loaded phrase lands and then resolves into the section's title statement |
| [particle-field-disperse-thin-out-fn7ca](#particle-field-disperse-thin-out-fn7ca) | collage | particle, slide-in, settle | frenetic | ominous | an idea scatters or thins out — a swarm dissolving toward emptiness |
| [code-editor-annotation-sticker-reveal-gziey](#code-editor-annotation-sticker-reveal-gziey) | code-reveal | marker-sweep, pop, slide-in | measured | neutral | a point in code or a UI is called out and annotated as the narrator walks through it |
| [hex-cell-mask-wipe-panel-dissolve-gziey](#hex-cell-mask-wipe-panel-dissolve-gziey) | title-card | mask-reveal, wipe, particle | punchy | playful | a promo badge or callout panel is swept away to transition into the next scene |
| [voronoi-cellular-mask-reveal-transition-6ttw8](#voronoi-cellular-mask-reveal-transition-6ttw8) | title-card | mask-reveal, wipe, particle | punchy | playful | a scene cuts to the next on a designed organic transition rather than a hard cut |
| [spinning-3d-torus-kinetic-type-cards-lmktg](#spinning-3d-torus-kinetic-type-cards-lmktg) | kinetic-type | kinetic-type, camera-orbit, snap | punchy | playful | a cheeky one-liner punchline lands while a hero 3D object keeps turning behind it |
| [white-particle-field-disperse-settle-lmktg](#white-particle-field-disperse-settle-lmktg) | title-card | particle, settle, parallax-drift | frenetic | neutral | an abstract idea swarms in then thins out, clearing the frame for what comes next |
| [dark-course-ui-panel-scroll-reveal-qq90](#dark-course-ui-panel-scroll-reveal-qq90) | code-reveal | slide-in, mask-reveal, settle | measured | clinical | a product or course interface is walked through panel by panel as proof |
| [white-cube-particle-field-thin-out-qq90](#white-cube-particle-field-thin-out-qq90) | title-card | particle, parallax-drift, settle | punchy | neutral | an idea dissolves or clears away to reset into the next beat |
| [kinetic-phrase-with-drawn-arrow-pointer-o7ihi](#kinetic-phrase-with-drawn-arrow-pointer-o7ihi) | kinetic-type | draw-on, kinetic-type, pop | measured | warm | a phrase lands as the takeaway and a hand-drawn arrow points to the operative word |
| [comparison-table-columns-build-grid-o7ihi](#comparison-table-columns-build-grid-o7ihi) | diagram-build | slide-in, stagger, settle | measured | clinical | two or more options get compared and the comparison grid assembles to make the contrast legible |
| [drifting-particle-field-dissolve-o7ihi](#drifting-particle-field-dissolve-o7ihi) | collage | particle, parallax-drift, settle | frenetic | tense | a dense idea dissolves or scatters as a transition between graphic scenes |
| [particle-cell-dissolve-reveals-offer-c68](#particle-cell-dissolve-reveals-offer-c68) | title-card | particle, mask-reveal, wipe | punchy | playful | a promo callout or offer badge enters as a graphic transition between scenes |
| [glitch-distorted-character-portrait-to-label-awe40](#glitch-distorted-character-portrait-to-label-awe40) | kinetic-type | glitch, morph, wipe | punchy | tense | a concept gets unsettled or destabilized before its name lands |
| [dense-checklist-panel-with-qr-payoff-awe40](#dense-checklist-panel-with-qr-payoff-awe40) | checklist | stagger, settle, pop | measured | clinical | a long roster of items resolves into a single offer or call-to-action |
| [white-particle-field-dissolve-clearing-awe40](#white-particle-field-dissolve-clearing-awe40) | collage | particle, wipe, settle | frenetic | neutral | a scene clears or resets in a burst before the next idea |
| [prompt-card-arrow-to-terminal-team-slide-in-optb8](#prompt-card-arrow-to-terminal-team-slide-in-optb8) | diagram-build | slide-in, draw-on, wipe | measured | neutral | a step in a pipeline hands off to the next, then the scene swaps to introduce the people behind it |
| [annotated-code-windows-mascot-connector-fade-optb8](#annotated-code-windows-mascot-connector-fade-optb8) | diagram-build | draw-on, settle, wipe | measured | playful | an annotated explainer makes its point, then dims out to hand off to the next idea |
| [mascot-handoff-to-branching-diagram-iwzoa](#mascot-handoff-to-branching-diagram-iwzoa) | diagram-build | draw-on, slide-in, settle | calm | playful | a concept title hands off from a friendly mascot into the diagram that explains it |
| [logo-fade-scale-settle-on-white-wvkrq](#logo-fade-scale-settle-on-white-wvkrq) | title-card | mask-reveal, scale-bloom, settle | measured | neutral | a brand or tool name is introduced as a clean section opener |
| [vs-comparison-build-then-money-slide-in-wvkrq](#vs-comparison-build-then-money-slide-in-wvkrq) | split-contrast | slide-in, wipe, settle | measured | neutral | two options are weighed against each other, then the takeaway swaps in |
| [logo-desaturate-fade-up-then-recede-a4lq](#logo-desaturate-fade-up-then-recede-a4lq) | title-card | mask-reveal, settle, scale-bloom | measured | neutral | a brand or product is named and you want its logo to introduce itself, then bow out |
| [brand-card-crossfade-to-logo-pop-a4lq](#brand-card-crossfade-to-logo-pop-a4lq) | title-card | mask-reveal, pop, settle | measured | playful | you hand off from one product to the next and want the outgoing card to dissolve as the incoming one announces itself |
| [marker-arrow-money-payoff-illustration-3caa](#marker-arrow-money-payoff-illustration-3caa) | title-card | draw-on, marker-sweep, slide-in | measured | playful | an opening thesis lands and the cost/stakes of the wrong choice are named |
| [chat-ui-panel-reveal-dashed-arrow-3caa](#chat-ui-panel-reveal-dashed-arrow-3caa) | device-mockup | slide-in, draw-on, settle | measured | neutral | a product or tool is introduced and its interface is the proof point |
| [cloud-provider-logos-stagger-then-link-3caa](#cloud-provider-logos-stagger-then-link-3caa) | collage | stagger, pop, draw-on | measured | neutral | a set of competing options or players is enumerated before a comparison |
| [wordpress-hosting-label-then-diagram-build-3caa](#wordpress-hosting-label-then-diagram-build-3caa) | diagram-build | mask-reveal, slide-in, settle | measured | clinical | a concept is restated then unpacked into its full supporting structure |
| [character-pop-into-cloud-diagram-nk6k8](#character-pop-into-cloud-diagram-nk6k8) | side-cutout | pop, draw-on, settle | measured | playful | an explainer introduces a reaction or consequence beside a standing diagram |
| [isometric-server-grid-kinetic-headline-nk6k8](#isometric-server-grid-kinetic-headline-nk6k8) | diagram-build | mask-reveal, slide-in, settle | measured | serious | a scene cuts from a small motif to a large data-center visual that makes the point land |
| [gear-monitor-scale-pop-to-node-graph-nk6k8](#gear-monitor-scale-pop-to-node-graph-nk6k8) | diagram-build | scale-bloom, draw-on, stagger | measured | clinical | a concept icon appears and then visibly grows into a more complex one |
| [nginx-staggered-capability-checklist-nk6k8](#nginx-staggered-capability-checklist-nk6k8) | checklist | stagger, slide-in, settle | measured | neutral | a feature or capability list reveals item by item as each is named |
| [explainer-wipe-to-logo-scale-bloom-c0lhc](#explainer-wipe-to-logo-scale-bloom-c0lhc) | title-card | wipe, scale-bloom, pop | calm | neutral | a section ends and you cut to a clean title card that introduces the next topic by its logo |
| [callout-card-build-to-logo-compare-c0lhc](#callout-card-build-to-logo-compare-c0lhc) | diagram-build | mask-reveal, stagger, pop | calm | neutral | a claim resolves into a designed callout that then sets up a head-to-head comparison |
| [glossy-badge-tumble-settle-amtnq](#glossy-badge-tumble-settle-amtnq) | logo | overshoot, settle, snap | punchy | playful | a brand or sponsor mark needs a confident, tactile entrance before its call-to-action |
| [quiz-ui-screens-with-result-card-slideup-amtnq](#quiz-ui-screens-with-result-card-slideup-amtnq) | device-mockup | slide-in, snap, pop | punchy | playful | stepping through an app's interaction flow where each screen answers and a verdict lands |
| [oversized-word-scale-bloom-over-code-2n6sg](#oversized-word-scale-bloom-over-code-2n6sg) | kinetic-type | scale-bloom, blur-rack, pop | punchy | playful | a single payoff word slams in to punctuate the point being made |
| [deck-title-card-typewriter-code-2n6sg](#deck-title-card-typewriter-code-2n6sg) | title-card | typewriter, mask-reveal, slide-in | measured | neutral | a section title lands and a supporting line types itself in beneath it |
| [landing-scroll-into-stat-block-countup-ccr2g](#landing-scroll-into-stat-block-countup-ccr2g) | stat-hero | parallax-push, count-up, settle | punchy | triumphant | a product claim hands off to a big number that lands as the payoff |
| [review-comment-cards-with-diff-reveal-ccr2g](#review-comment-cards-with-diff-reveal-ccr2g) | code-reveal | slide-in, mask-reveal, settle | measured | clinical | a tool surfaces inline feedback and the supporting code change is exposed beneath it |
| [sticky-node-system-design-diagram-collage-ccr2g](#sticky-node-system-design-diagram-collage-ccr2g) | diagram-build | draw-on, slide-in, pop | punchy | playful | an architecture is sketched out node-by-node alongside the surrounding context |
| [dashboard-stat-cards-with-count-up-chart-saggi](#dashboard-stat-cards-with-count-up-chart-saggi) | stat-hero | count-up, settle, slide-in | measured | neutral | a dashboard headline number and its chart land as the payoff of a section |
| [tech-stack-logo-grid-reveal-saggi](#tech-stack-logo-grid-reveal-saggi) | collage | pop, stagger, settle | punchy | playful | a 'here's the stack' moment names the tools a project is built on |
| [config-diff-reveal-side-code-panel-saggi](#config-diff-reveal-side-code-panel-saggi) | code-reveal | slide-in, mask-reveal, settle | measured | clinical | a config or code change is walked through line by line as proof |
| [ui-zoom-push-into-nav-target-saggi](#ui-zoom-push-into-nav-target-saggi) | device-mockup | parallax-push, scale-bloom, settle | punchy | neutral | the eye is pushed toward one control or word inside a busy product UI |
| [labeled-pixel-grid-diagram-scroll-9zep8](#labeled-pixel-grid-diagram-scroll-9zep8) | diagram-build | slide-in, draw-on, settle | measured | clinical | a spatial/grid concept gets explained cell-by-cell with a callout label |
| [spec-table-panels-slide-zoom-9zep8](#spec-table-panels-slide-zoom-9zep8) | diagram-build | slide-in, scale-bloom, settle | measured | clinical | a reference spec or lookup table is introduced and one row is brought into focus |
| [matrix-code-rain-to-kinetic-caption-9zep8](#matrix-code-rain-to-kinetic-caption-9zep8) | kinetic-type | particle, kinetic-type, wipe | punchy | playful | a 'this is how computers really work' beat lands with a digital-machine flourish |
| [green-check-checklist-stack-build-pb5hy](#green-check-checklist-stack-build-pb5hy) | checklist | stagger, pop, settle | punchy | playful | a short list of guarantees or kept promises lands item by item as reassurance |
| [title-lockup-side-cutout-to-spin-icon-pb5hy](#title-lockup-side-cutout-to-spin-icon-pb5hy) | side-cutout | settle, snap, morph | punchy | playful | a labeled concept is introduced as a titled exhibit before the segment opens up |
| [checklist-wipe-to-skill-kinetic-word-pb5hy](#checklist-wipe-to-skill-kinetic-word-pb5hy) | kinetic-type | wipe, slide-in, snap | punchy | playful | a list of rules collapses into a single one-word punchline |
| [replit-logo-block-assemble-wordmark-mask-pb5hy](#replit-logo-block-assemble-wordmark-mask-pb5hy) | diagram-build | mask-reveal, settle, draw-on | measured | neutral | a brand or product is named and its logo assembles as the reveal |
| [logo-tile-assemble-over-starfield-7stda](#logo-tile-assemble-over-starfield-7stda) | title-card | pop, settle, wipe | punchy | neutral | a brand or product name lands as the reveal after setup |
| [cash-particle-storm-quote-card-7stda](#cash-particle-storm-quote-card-7stda) | quote-card | particle, parallax-drift, settle | frenetic | tense | a pointed quote or claim lands while a chaotic backdrop churns behind it |
| [status-checklist-with-progress-bars-7stda](#status-checklist-with-progress-bars-7stda) | checklist | stagger, draw-on, settle | measured | neutral | a few labeled items resolve to pass/fail states as a payoff |
| [vintage-card-swaps-to-stacked-title-build-vzmr8](#vintage-card-swaps-to-stacked-title-build-vzmr8) | title-card | slide-in, wipe, settle | punchy | playful | a topic name is introduced as the segment's title |
| [logo-lockup-blur-racks-to-replacement-name-vzmr8](#logo-lockup-blur-racks-to-replacement-name-vzmr8) | title-card | blur-rack, mask-reveal, settle | measured | serious | one named option is dismissed and a replacement takes its place |
| [pull-quote-card-cuts-to-but-why-kinetic-vzmr8](#pull-quote-card-cuts-to-but-why-kinetic-vzmr8) | quote-card | slide-in, snap, pop | punchy | tense | a quoted statement lands and the beat snaps to a single pointed question |
| [checklist-overlay-builds-to-q-day-slam-vzmr8](#checklist-overlay-builds-to-q-day-slam-vzmr8) | checklist | stagger, wipe, snap | punchy | ominous | a set of conditions checks off and resolves into a single named threat |
| [relational-keyword-card-pop-with-stacked-reveal-xoffa](#relational-keyword-card-pop-with-stacked-reveal-xoffa) | kinetic-type | pop, slide-in, settle | punchy | playful | a key term snaps on as the punchline, then earns a second word that defines it |
| [logo-assembles-from-paper-debris-parallax-xoffa](#logo-assembles-from-paper-debris-parallax-xoffa) | title-card | particle, parallax-drift, settle | frenetic | neutral | a brand or system name resolves out of churning visual noise into a clean lockup |
| [icon-checklist-blur-wipes-to-typing-keyboard-xoffa](#icon-checklist-blur-wipes-to-typing-keyboard-xoffa) | checklist | blur-rack, wipe, slide-in | punchy | neutral | a list of steps hands off to a concrete demo of doing the work |
| [two-tier-architecture-diagram-collapses-to-storage-xoffa](#two-tier-architecture-diagram-collapses-to-storage-xoffa) | diagram-build | wipe, settle, pop | measured | clinical | a layered system diagram drops a layer to focus on the one that matters |
| [marker-scribble-mastery-annotation-quhpy](#marker-scribble-mastery-annotation-quhpy) | diagram-build | marker-sweep, draw-on | punchy | playful | a single word gets hand-circled to flag the one idea that matters |
| [vibe-coding-bold-title-doodle-quhpy](#vibe-coding-bold-title-doodle-quhpy) | title-card | pop, snap | frenetic | playful | a punchy two-word concept gets named as a section header |
| [app-ui-panel-wipe-icon-grid-quhpy](#app-ui-panel-wipe-icon-grid-quhpy) | device-mockup | wipe, slide-in | measured | neutral | a product screen is revealed and then resolves into its component options |
| [main-problem-kinetic-slam-glitch-quhpy](#main-problem-kinetic-slam-glitch-quhpy) | kinetic-type | snap, glitch, scale-bloom | frenetic | tense | the section pivots to name the core problem with a hard tonal slam |
| [concept-label-then-illustration-pop-64g8k](#concept-label-then-illustration-pop-64g8k) | diagram-build | mask-reveal, pop, settle | punchy | playful | a named concept gets defined and then punctuated by a character or illustration |
| [meme-title-to-branded-logo-card-build-64g8k](#meme-title-to-branded-logo-card-build-64g8k) | title-card | snap, slide-in, settle | punchy | playful | a playful cold-open beat hands off into a branded sponsor or section card |
| [staggered-checklist-red-x-marker-strike-64g8k](#staggered-checklist-red-x-marker-strike-64g8k) | checklist | marker-sweep, stagger, pop | measured | serious | a list of negatives is dismissed one by one as the narrator strikes each down |
| [labeled-icon-stack-then-wipe-out-aufmm](#labeled-icon-stack-then-wipe-out-aufmm) | diagram-build | settle, wipe, slide-in | measured | neutral | a small set of labeled tech/tooling icons assembles to make a point, then clears for the next idea |
| [lightning-logo-typed-label-then-tag-popon-aufmm](#lightning-logo-typed-label-then-tag-popon-aufmm) | title-card | settle, typewriter, pop | punchy | playful | a product or feature name lands as a titled logo build, capped by a status/category tag snapping on |
| [icon-trio-clears-to-chevron-text-wipe-aufmm](#icon-trio-clears-to-chevron-text-wipe-aufmm) | diagram-build | settle, wipe, mask-reveal | punchy | neutral | two or three concept icons resolve into a single labeled takeaway line |
| [rainbow-arc-swoosh-10x-headline-hq7pq](#rainbow-arc-swoosh-10x-headline-hq7pq) | kinetic-type | slide-in, wipe, pop | punchy | playful | a punchy claim or multiplier lands as a hype headline |
| [logo-title-card-mask-reveal-from-black-hq7pq](#logo-title-card-mask-reveal-from-black-hq7pq) | title-card | mask-reveal, settle, scale-bloom | measured | serious | a product or brand name is introduced as the section title |
| [scale-bloom-glow-tagline-green-hq7pq](#scale-bloom-glow-tagline-green-hq7pq) | kinetic-type | scale-bloom, blur-rack, glitch | punchy | triumphant | a feature tagline punches in as the emphasis beat |
| [orange-particle-burst-over-puzzle-tiles-c3qrq](#orange-particle-burst-over-puzzle-tiles-c3qrq) | diagram-build | particle, scale-bloom, pop | frenetic | tense | a single idea detonates outward as the emphatic payoff of a point |
| [chrome-skull-cash-debris-orbit-c3qrq](#chrome-skull-cash-debris-orbit-c3qrq) | collage | particle, parallax-drift, settle | punchy | ominous | money or stakes swirl around a menacing central subject |
| [gpu-card-ram-slide-in-arrow-drawon-c3qrq](#gpu-card-ram-slide-in-arrow-drawon-c3qrq) | device-mockup | draw-on, slide-in, settle | measured | clinical | a hardware concept assembles part by part to explain how it fits together |
| [logo-scatter-into-captioned-api-reveal-ytiou](#logo-scatter-into-captioned-api-reveal-ytiou) | title-card | particle, morph, mask-reveal | punchy | tense | a familiar brand dissolves to hand off to its replacement |
| [icon-pair-with-handwritten-spec-annotation-ytiou](#icon-pair-with-handwritten-spec-annotation-ytiou) | diagram-build | draw-on, settle, pop | measured | neutral | a product detail gets called out with a handwritten spec note |
| [code-block-dissolve-to-logo-version-badge-ytiou](#code-block-dissolve-to-logo-version-badge-ytiou) | code-reveal | particle, parallax-push, pop | frenetic | tense | code is shown then swept aside to land a single version number |
| [comparison-stat-grid-to-reaction-cut-ytiou](#comparison-stat-grid-to-reaction-cut-ytiou) | split-contrast | slide-in, wipe, settle | frenetic | playful | two options are compared by the numbers before a punchline cut |
| [social-feed-ui-build-over-matrix-efdss](#social-feed-ui-build-over-matrix-efdss) | diagram-build | slide-in, stagger, pop | frenetic | playful | a busy app or social-feed mockup assembles itself to illustrate platform overload |
| [database-types-panel-beside-presenter-efdss](#database-types-panel-beside-presenter-efdss) | side-cutout | slide-in, stagger, settle | measured | clinical | a presenter walks through a labeled taxonomy or option grid before the architecture pays off |
| [qr-reveal-with-start-free-kinetic-cta-efdss](#qr-reveal-with-start-free-kinetic-cta-efdss) | code-reveal | mask-reveal, kinetic-type, pop | punchy | warm | an end-card CTA snaps in alongside a scannable code to close the video |
| [logo-lockup-wipe-tagline-reveal-y19so](#logo-lockup-wipe-tagline-reveal-y19so) | title-card | wipe, mask-reveal, settle | punchy | triumphant | a product or brand name is introduced as the reveal a beat builds toward |
| [logo-wordmark-blur-streak-reveal-m3xi](#logo-wordmark-blur-streak-reveal-m3xi) | title-card | blur-rack, slide-in, settle | punchy | playful | a product or brand name is introduced as a hard beat |
| [golden-light-burst-bloom-transition-m3xi](#golden-light-burst-bloom-transition-m3xi) | title-card | scale-bloom, particle, wipe | frenetic | triumphant | a scene change needs a bright, celebratory wipe between graphic beats |
| [staggered-label-reveal-over-fade-up-figure-gij8k](#staggered-label-reveal-over-fade-up-figure-gij8k) | kinetic-type | slide-in, stagger, mask-reveal | punchy | playful | three named items land one after another as a punchline list builds |
| [frenetic-meme-thumbnail-collage-glitch-gij8k](#frenetic-meme-thumbnail-collage-glitch-gij8k) | collage | snap, glitch, pop | frenetic | playful | an overwhelming flood of options or content is dumped on screen at once |
| [perspective-tilted-text-panels-slide-in-icioa](#perspective-tilted-text-panels-slide-in-icioa) | code-reveal | slide-in, parallax-push, settle | punchy | neutral | a wall of text or code is introduced as a reference the narrator is about to walk through |
| [rendered-torus-with-scaling-kinetic-payoff-icioa](#rendered-torus-with-scaling-kinetic-payoff-icioa) | kinetic-type | scale-bloom, kinetic-type, settle | frenetic | playful | a punchline or reductive payoff lands hard over a hero render ('it's all just X') |
| [glitch-clipped-name-title-over-board-icioa](#glitch-clipped-name-title-over-board-icioa) | title-card | glitch, kinetic-type, snap | frenetic | playful | a name or section title slams on screen as a hard scene-change stinger |
| [two-line-verdict-caption-build-rnxx0](#two-line-verdict-caption-build-rnxx0) | kinetic-type | typewriter, slide-in, settle | measured | playful | a two-part verdict lands — the upbeat clause first, then the deadpan turn underneath |
| [data-table-row-reveal-highlight-payoff-2opwe](#data-table-row-reveal-highlight-payoff-2opwe) | stat-hero | mask-reveal, stagger, settle | measured | clinical | a single row in a data table is the answer the rest of the table exists to frame |
| [pyramid-to-card-flow-whip-blur-transition-2opwe](#pyramid-to-card-flow-whip-blur-transition-2opwe) | diagram-build | blur-rack, slide-in, snap | punchy | neutral | a hard scene change from one diagram into a connected node/flow layout |
| [terminal-card-recede-with-lower-third-swap-2nn4g](#terminal-card-recede-with-lower-third-swap-2nn4g) | lower-third | settle, scale-bloom, slide-in | measured | serious | a confident claim gets set up, then quietly undercut by the reality that follows |
| [file-tree-mockup-push-zoom-2nn4g](#file-tree-mockup-push-zoom-2nn4g) | device-mockup | scale-bloom, slide-in, parallax-push | measured | serious | a small UI detail is pulled forward to make a complexity point land |
| [editorial-report-card-rise-fade-in-2nn4g](#editorial-report-card-rise-fade-in-2nn4g) | title-card | slide-in, settle, blur-rack | measured | ominous | a sourced headline or finding is introduced as the turning point of the argument |
| [red-radial-network-pulse-with-counter-2nn4g](#red-radial-network-pulse-with-counter-2nn4g) | diagram-build | particle, pop, count-up | punchy | tense | a sprawling, interconnected problem is shown as more tangled than expected |
| [staggered-product-cards-fade-up-d9r3o](#staggered-product-cards-fade-up-d9r3o) | collage | stagger, slide-in, settle | calm | neutral | a small set of named components or tools assembles one at a time to show a stack coming together |
| [icon-pair-whip-pan-motion-blur-d9r3o](#icon-pair-whip-pan-motion-blur-d9r3o) | diagram-build | slide-in, blur-rack, wipe | punchy | neutral | two concept icons hold on a settings screen, then the scene whips away to the next idea |
| [floating-callout-pills-around-orb-d9r3o](#floating-callout-pills-around-orb-d9r3o) | device-mockup | parallax-drift, pop, settle | calm | warm | an interface gets annotated with floating labels that name its qualities or features |
| [kinetic-title-blur-rack-out-d9r3o](#kinetic-title-blur-rack-out-d9r3o) | title-card | kinetic-type, blur-rack, scale-bloom | measured | serious | a section title lands as a statement then defocuses to hand off to the next scene |
| [infinity-logo-style-morph-cycle-dhmva](#infinity-logo-style-morph-cycle-dhmva) | title-card | morph, mask-reveal, scale-bloom | punchy | playful | a brand or section title lands and you want it to feel like a stylized logo stinger |
| [card-wall-reflow-to-center-title-dhmva](#card-wall-reflow-to-center-title-dhmva) | collage | accordion-reflow, slide-in, settle | frenetic | neutral | a dense field of evidence collapses into the single headline it all proves |
| [lvl-zero-to-hundred-badge-pop-dhmva](#lvl-zero-to-hundred-badge-pop-dhmva) | stat-hero | snap, pop, scale-bloom | punchy | triumphant | a before/after number jumps to its max as the triumphant payoff |
| [read-watch-for-free-stacked-type-build-dhmva](#read-watch-for-free-stacked-type-build-dhmva) | kinetic-type | kinetic-type, snap, mask-reveal | frenetic | playful | a short call-to-action phrase hits hard line by line before the content plays |
| [concentric-ring-ripple-expand-50kxu](#concentric-ring-ripple-expand-50kxu) | diagram-build | scale-bloom, draw-on, settle | punchy | tense | a single idea radiates outward and a focal point lands at center |
| [article-card-slide-scale-on-grid-50kxu](#article-card-slide-scale-on-grid-50kxu) | collage | slide-in, parallax-push, settle | measured | serious | a headline or source card is presented as evidence for a claim |
| [job-posting-icon-pop-on-grid-50kxu](#job-posting-icon-pop-on-grid-50kxu) | device-mockup | pop, scale-bloom, settle | measured | neutral | a single concept icon punches in to label the topic of a beat |
| [playbook-title-reveal-dissolve-50kxu](#playbook-title-reveal-dissolve-50kxu) | title-card | mask-reveal, blur-rack, settle | measured | serious | a section or chapter title lands then dissolves into the next scene |
| [ui-card-assembles-on-grid-canvas-heplm](#ui-card-assembles-on-grid-canvas-heplm) | device-mockup | slide-in, blur-rack, settle | measured | neutral | a product UI is being introduced and the interface assembles itself before the viewer's eyes |
| [code-block-parallax-push-into-grid-heplm](#code-block-parallax-push-into-grid-heplm) | code-reveal | parallax-push, scale-bloom, blur-rack | measured | clinical | a code snippet is shown and then pushed back to make room for the next idea |
| [rotating-stamp-badges-radial-dial-title-heplm](#rotating-stamp-badges-radial-dial-title-heplm) | title-card | snap, kinetic-type, draw-on | punchy | playful | a punchline word lands as the payoff with a stamped-on emphasis |
| [error-callout-over-code-lines-reveal-ftlro](#error-callout-over-code-lines-reveal-ftlro) | code-reveal | mask-reveal, slide-in, settle | punchy | tense | a bug or error gets called out the instant it surfaces in code |
| [device-card-hold-caption-swap-emphasis-ftlro](#device-card-hold-caption-swap-emphasis-ftlro) | device-mockup | kinetic-type, mask-reveal, settle | measured | warm | a punchline caption swaps to reland the claim under a held product UI |
| [net-io-load-streaming-pill-dots-e0nnw](#net-io-load-streaming-pill-dots-e0nnw) | diagram-build | slide-in, stagger, draw-on | frenetic | clinical | data or requests flowing through a pipeline as a system processes load |
| [word-by-word-pop-grid-then-cutout-e0nnw](#word-by-word-pop-grid-then-cutout-e0nnw) | kinetic-type | pop, scale-bloom, slide-in | punchy | playful | a two-word rhetorical turn lands as the punchline, then cuts to a subject |
| [legacy-systems-adapter-diagram-build-e0nnw](#legacy-systems-adapter-diagram-build-e0nnw) | diagram-build | draw-on, slide-in, settle | measured | neutral | naming an architecture concept by drawing its node-and-connector diagram |
| [chat-card-with-tree-overlay-fade-to-dark-e0nnw](#chat-card-with-tree-overlay-fade-to-dark-e0nnw) | diagram-build | mask-reveal, draw-on, settle | punchy | serious | a structural diagram surfaces over a conversation as the scene hands off |
| [title-swap-over-filling-ui-progressbar-zh4pq](#title-swap-over-filling-ui-progressbar-zh4pq) | title-card | slide-in, mask-reveal, settle | calm | neutral | a section title hands off to a demo while a loading bar primes the payoff |
| [segmented-timeline-fills-to-failure-spark-zh4pq](#segmented-timeline-fills-to-failure-spark-zh4pq) | diagram-build | wipe, snap, particle | measured | tense | a multi-stage process advances stage by stage until the final step fails |
| [countdown-card-with-cost-countup-tweets-zh4pq](#countdown-card-with-cost-countup-tweets-zh4pq) | stat-hero | count-up, slide-in, pop | measured | ominous | a running cost climbs while the clock holds and complaints pile up |
| [the-fork-blur-rack-into-ship-it-split-zh4pq](#the-fork-blur-rack-into-ship-it-split-zh4pq) | split-contrast | blur-rack, parallax-drift, mask-reveal | measured | serious | a decision point splits into two diverging paths |
| [pixel-grid-triangle-grows-cell-by-cell-mvlw4](#pixel-grid-triangle-grows-cell-by-cell-mvlw4) | diagram-build | draw-on, scale-bloom, settle | punchy | clinical | a concept is constructed from primitives, each unit snapping into place to assemble a whole |
| [title-then-console-panel-fades-up-mvlw4](#title-then-console-panel-fades-up-mvlw4) | title-card | mask-reveal, settle, slide-in | measured | serious | a section name lands, then its supporting detail panel quietly resolves beneath it |
| [rotated-grid-card-settles-with-drop-shadow-mvlw4](#rotated-grid-card-settles-with-drop-shadow-mvlw4) | device-mockup | overshoot, settle, parallax-drift | measured | clinical | an artifact is presented and rotated into its hero pose as the focus object of the beat |
| [staggered-command-cards-slide-in-dcm24](#staggered-command-cards-slide-in-dcm24) | code-reveal | stagger, slide-in, settle | calm | clinical | a list of concrete examples accumulates one card at a time under a framing header |
| [typewriter-question-emphasis-word-dcm24](#typewriter-question-emphasis-word-dcm24) | kinetic-type | typewriter, kinetic-type | measured | serious | a central question builds word by word and the final emphasis word lands the hook |
| [count-up-possible-keys-stat-hero-dcm24](#count-up-possible-keys-stat-hero-dcm24) | stat-hero | count-up, settle | calm | clinical | a single large number ticks upward to land a magnitude payoff |
| [entropy-pipeline-diagram-build-dcm24](#entropy-pipeline-diagram-build-dcm24) | diagram-build | draw-on, stagger, settle | calm | clinical | a multi-stage pipeline assembles top-to-bottom to show inputs flowing into outputs |
| [linked-list-node-insert-pointer-rewire-cuijk](#linked-list-node-insert-pointer-rewire-cuijk) | diagram-build | draw-on, accordion-reflow, slide-in | measured | clinical | a data structure mutates as a new element is inserted and the connections rewire to accommodate it |
| [ui-card-node-slide-in-connector-hgjo](#ui-card-node-slide-in-connector-hgjo) | diagram-build | slide-in, settle | measured | clinical | a secondary element joins an existing object to show a relationship being added |
| [staggered-table-cards-build-cursor-hgjo](#staggered-table-cards-build-cursor-hgjo) | diagram-build | stagger, slide-in, settle | measured | clinical | a multi-part schema or pipeline assembles piece by piece as it is explained |
| [index-cells-to-byte-bars-countup-hgjo](#index-cells-to-byte-bars-countup-hgjo) | stat-hero | morph, count-up, settle | measured | serious | a measured comparison resolves into a payoff stat that contrasts two values |
| [uuid-hash-typewriter-tail-emphasis-hgjo](#uuid-hash-typewriter-tail-emphasis-hgjo) | kinetic-type | typewriter, slide-in, pop | calm | neutral | a specific string or token is called out and one part of it is emphasized |
| [recap-checklist-items-check-on-stagger-ump1y](#recap-checklist-items-check-on-stagger-ump1y) | checklist | stagger, pop, settle | measured | triumphant | a payoff beat tallies up the properties just earned, one confirmation at a time |
| [request-token-sweeps-node-chain-build-ump1y](#request-token-sweeps-node-chain-build-ump1y) | diagram-build | draw-on, slide-in, settle | punchy | neutral | a request is traced step by step through a service pipeline |
| [labeled-card-grid-scatters-parallax-drift-ump1y](#labeled-card-grid-scatters-parallax-drift-ump1y) | collage | parallax-drift, slide-in, settle | punchy | serious | a tidy inventory of pieces breaks apart to signal complexity or sprawl |
| [terraform-config-lines-typewriter-beside-card-ump1y](#terraform-config-lines-typewriter-beside-card-ump1y) | code-reveal | typewriter, mask-reveal, settle | measured | clinical | a config file fills in line by line to show the concrete implementation |
| [kinetic-title-blurs-out-to-arch-cards-xo5da](#kinetic-title-blurs-out-to-arch-cards-xo5da) | diagram-build | blur-rack, mask-reveal, settle | measured | neutral | a headline concept dissolves and resolves into the system it labels |
| [word-by-word-caption-typewriter-greyed-tail-xo5da](#word-by-word-caption-typewriter-greyed-tail-xo5da) | kinetic-type | typewriter, kinetic-type | calm | neutral | a sentence builds clause by clause to land its closing word |
| [socket-list-rows-light-ready-into-epoll-card-xo5da](#socket-list-rows-light-ready-into-epoll-card-xo5da) | diagram-build | stagger, pop, settle | measured | clinical | a queue of items is processed by a single worker to show throughput |
| [snapshot-timeline-draws-and-pans-left-xo5da](#snapshot-timeline-draws-and-pans-left-xo5da) | timeline | draw-on, slide-in, parallax-drift | calm | neutral | a series of events is plotted along time as a sequence of markers |
| [repeating-decimal-digit-cascade-dd27m](#repeating-decimal-digit-cascade-dd27m) | kinetic-type | kinetic-type, slide-in, typewriter | frenetic | playful | a value spills into an endless repeating sequence and you want to feel the 'forever' |
| [binary-expansion-progressive-typeout-dd27m](#binary-expansion-progressive-typeout-dd27m) | code-reveal | typewriter, count-up, settle | measured | clinical | a clean decimal turns out to be an ugly never-ending value once converted |
| [bit-field-fill-sign-exponent-mantissa-dd27m](#bit-field-fill-sign-exponent-mantissa-dd27m) | diagram-build | wipe, stagger, settle | punchy | clinical | a fixed-size data structure fills up region by region as you explain each part |
| [price-times-integer-card-flow-dd27m](#price-times-integer-card-flow-dd27m) | split-contrast | slide-in, settle, blur-rack | measured | serious | a takeaway lands, then the supporting cards dissolve to leave only the result |
| [phrase-swap-line-builds-dim-out-8xfog](#phrase-swap-line-builds-dim-out-8xfog) | kinetic-type | kinetic-type, mask-reveal, settle | measured | serious | a spoken sentence reframes mid-thought and you want the words to update in place as the narrator pivots |
| [doc-cards-with-side-panel-fade-in-8xfog](#doc-cards-with-side-panel-fade-in-8xfog) | diagram-build | slide-in, mask-reveal, settle | measured | clinical | introducing a data structure where a source list sits on the left and a derived view assembles beside it |
| [segment-cards-merge-into-optimized-stack-8xfog](#segment-cards-merge-into-optimized-stack-8xfog) | diagram-build | slide-in, morph, accordion-reflow | measured | clinical | showing several separate pieces consolidating into one combined, optimized whole |
| [bar-chart-grows-bar-by-bar-8xfog](#bar-chart-grows-bar-by-bar-8xfog) | diagram-build | stagger, count-up, settle | punchy | neutral | a distribution or trend resolves into its full shape as the payoff of a data point |
| [grid-cells-fill-row-sweep-under-titlecard-8e62y](#grid-cells-fill-row-sweep-under-titlecard-8e62y) | diagram-build | draw-on, slide-in, settle | calm | clinical | a concept is introduced and a grid/queue diagram fills in to embody it |
| [multi-panel-grids-populate-then-red-stateflip-8e62y](#multi-panel-grids-populate-then-red-stateflip-8e62y) | diagram-build | slide-in, morph, settle | measured | tense | parallel work units run side by side and one flips to an error/alert state |
| [countdown-counter-over-draining-grid-progressbar-8e62y](#countdown-counter-over-draining-grid-progressbar-8e62y) | stat-hero | count-up, settle, wipe | measured | serious | a running tally drops as a metric resolves toward a target |
| [big-number-count-up-toward-round-target-ieszg](#big-number-count-up-toward-round-target-ieszg) | stat-hero | count-up, settle | calm | neutral | a single big number is the payoff and you want the audience to feel it climb to a milestone |
| [staggered-bar-chart-panels-build-left-to-right-ieszg](#staggered-bar-chart-panels-build-left-to-right-ieszg) | diagram-build | stagger, slide-in, settle | measured | neutral | a series of comparable data panels accumulate one by one to show a repeating pattern |
| [device-card-recedes-into-node-graph-parallax-ieszg](#device-card-recedes-into-node-graph-parallax-ieszg) | device-mockup | parallax-push, scale-bloom, settle | measured | neutral | a single labeled item shrinks into the background to reveal it as one node among many in a larger structure |
| [relational-table-collapses-into-single-graph-node-ieszg](#relational-table-collapses-into-single-graph-node-ieszg) | diagram-build | morph, settle, slide-in | calm | neutral | contrasting two data models by dissolving the old structure into the shape of the new one |
| [neon-grid-plane-arrows-drawon-pgn4o](#neon-grid-plane-arrows-drawon-pgn4o) | diagram-build | draw-on, parallax-push, scale-bloom | frenetic | tense | an abstract system or concept gets established as a glowing tech substrate at the top of a section |
| [green-waveform-grid-chart-sweep-pgn4o](#green-waveform-grid-chart-sweep-pgn4o) | stat-hero | draw-on, marker-sweep, settle | punchy | neutral | a trend line or signal climbs to make a single rising-data point land |
| [magenta-typewriter-title-reveal-ip0sw](#magenta-typewriter-title-reveal-ip0sw) | title-card | typewriter, kinetic-type | punchy | playful | a defining statement lands as the opening claim, typed out for emphasis |
| [blue-tunnel-warp-into-equation-build-fu4cm](#blue-tunnel-warp-into-equation-build-fu4cm) | diagram-build | parallax-push, mask-reveal, kinetic-type | frenetic | tense | a concept warps from abstract chaos into a single resolved formula or insight |
| [retro-my-computer-icon-pulse-reveal-fu4cm](#retro-my-computer-icon-pulse-reveal-fu4cm) | device-mockup | scale-bloom, pop, kinetic-type | punchy | playful | a single familiar UI element is spotlighted as the punchline or subject of the beat |
| [equation-overlay-energy-burst-hniiq](#equation-overlay-energy-burst-hniiq) | diagram-build | scale-bloom, mask-reveal, particle | frenetic | tense | an abstract concept gets visualized as it crescendos into a payoff |
| [kinetic-type-does-not-compute-glitch-build-vybwk](#kinetic-type-does-not-compute-glitch-build-vybwk) | kinetic-type | kinetic-type, glitch, pop | punchy | tense | a punchline lands word-by-word as a hard reaction beat |
| [code-reveal-with-side-cutout-react-vybwk](#code-reveal-with-side-cutout-react-vybwk) | code-reveal | slide-in, mask-reveal, settle | frenetic | playful | code or config is explained while a reacting character punctuates it |
| [book-preview-card-slide-in-beside-portrait-vybwk](#book-preview-card-slide-in-beside-portrait-vybwk) | quote-card | slide-in, settle, mask-reveal | measured | neutral | a source or citation is introduced as the authority behind a claim |
| [stacked-headline-list-stagger-then-punchline-card-4edok](#stacked-headline-list-stagger-then-punchline-card-4edok) | kinetic-type | stagger, slide-in, settle | measured | tense | a list of mounting problems stacks up before a single relieving payoff line lands |
| [3d-crowd-render-slow-camera-push-4edok](#3d-crowd-render-slow-camera-push-4edok) | collage | camera-orbit, parallax-push, settle | punchy | ominous | a beat needs to convey scale — 'everyone', a faceless mass, the whole market — without naming individuals |
| [money-rain-icon-collage-over-black-yfgnm](#money-rain-icon-collage-over-black-yfgnm) | collage | particle, slide-in, settle | frenetic | playful | cost or spending spirals as the painful payoff beat |
| [dashboard-ui-panels-reveal-chart-to-wordmark-yfgnm](#dashboard-ui-panels-reveal-chart-to-wordmark-yfgnm) | code-reveal | slide-in, draw-on, settle | punchy | clinical | a product or dashboard is introduced and its capabilities tour past |
| [tiered-pyramid-diagram-build-money-rain-yfgnm](#tiered-pyramid-diagram-build-money-rain-yfgnm) | diagram-build | draw-on, particle, settle | frenetic | playful | a pricing or hierarchy is laid out in stacked tiers as the structural payoff |
| [staggered-checklist-fade-up-over-broll-ykpvk](#staggered-checklist-fade-up-over-broll-ykpvk) | checklist | stagger, slide-in, settle | calm | serious | a short list of principles or steps is enumerated one line at a time as the payoff |
| [isometric-city-title-with-stepped-build-w1dtc](#isometric-city-title-with-stepped-build-w1dtc) | title-card | kinetic-type, slide-in, settle | measured | warm | an opening promise/headline lands over a designed illustrated scene before the lesson begins |
| [illustrated-tv-labels-pop-collage-zw1u](#illustrated-tv-labels-pop-collage-zw1u) | collage | pop, scale-bloom, snap | punchy | playful | a noisy roundup of options or features is dumped on screen all at once before being summarized |
| [code-bg-money-particles-3d-fly-zw1u](#code-bg-money-particles-3d-fly-zw1u) | code-reveal | particle, parallax-push, pop | punchy | triumphant | a payoff moment lands the idea of code turning into money or revenue |
| [minecraft-character-render-scale-bloom-xlggy](#minecraft-character-render-scale-bloom-xlggy) | collage | scale-bloom, pop, settle | punchy | playful | a cluster of themed icons or character renders pops in as a payoff cutaway |
| [webpage-layouts-slide-swap-7uxwo](#webpage-layouts-slide-swap-7uxwo) | device-mockup | slide-in, wipe, settle | punchy | neutral | a sequence of source pages or screenshots fans past to establish breadth of evidence |
| [document-form-rise-behind-mascot-7uxwo](#document-form-rise-behind-mascot-7uxwo) | device-mockup | slide-in, parallax-push, settle | frenetic | playful | a paperwork or form artifact looms up as the on-screen subject reacts to it |
| [subscribe-cta-buttons-pop-in-7uxwo](#subscribe-cta-buttons-pop-in-7uxwo) | lower-third | pop, slide-in, stagger | punchy | playful | an end-card call-to-action stacks up its subscribe/notify prompts as the closing ask |
| [tilted-document-flip-beside-cutout-ab3fc](#tilted-document-flip-beside-cutout-ab3fc) | side-cutout | card-flip, slide-in, settle | punchy | serious | a long quote or source document is revealed beside the speaker as supporting evidence |
| [tilted-credential-card-flip-reveal-ab3fc](#tilted-credential-card-flip-reveal-ab3fc) | lower-third | card-flip, slide-in, settle | punchy | serious | a person's name and credential lands as an at-a-glance identity card |
| [vs-versus-title-card-logo-assemble-wdl3o](#vs-versus-title-card-logo-assemble-wdl3o) | split-contrast | mask-reveal, pop, settle | punchy | tense | a head-to-head comparison kicks off and you need to frame the two sides squaring up |
| [connecting-line-draws-to-globe-node-wdl3o](#connecting-line-draws-to-globe-node-wdl3o) | map | draw-on, slide-in, settle | measured | neutral | a point connects to a place or network node and you want the link to physically trace its way to the destination |
| [wireframe-logo-glow-bloom-title-wdl3o](#wireframe-logo-glow-bloom-title-wdl3o) | title-card | scale-bloom, settle | measured | warm | a brand or movement gets named and you want its emblem to glow up as the section title |
| [product-page-headline-then-code-panel-reveal-pb6y0](#product-page-headline-then-code-panel-reveal-pb6y0) | code-reveal | mask-reveal, slide-in, settle | measured | clinical | a product or tool is introduced and its core promise plus a screenshot of it working land together |
| [electric-title-card-logo-reveal-jejkw](#electric-title-card-logo-reveal-jejkw) | title-card | kinetic-type, scale-bloom, settle | punchy | tense | a chapter or section opens on its name with high-voltage attitude |
| [blur-rack-into-blueprint-spec-card-puexo](#blur-rack-into-blueprint-spec-card-puexo) | diagram-build | blur-rack, mask-reveal, settle | measured | clinical | a technical spec or blueprint resolves into focus as the explanation gets concrete |
| [smoke-particle-dissolve-screen-swap-puexo](#smoke-particle-dissolve-screen-swap-puexo) | device-mockup | particle, wipe, morph | punchy | neutral | one screen or scene dissolves into the next as a designed transition beat |
| [grid-wipe-into-product-poster-reveal-puexo](#grid-wipe-into-product-poster-reveal-puexo) | title-card | wipe, slide-in, settle | punchy | triumphant | a hero product and headline land together as the payoff reveal |
| [scribble-tangle-brain-draw-on-puexo](#scribble-tangle-brain-draw-on-puexo) | diagram-build | draw-on, scale-bloom, pop | frenetic | tense | a beat depicts confusion, overthinking, or a tangled mental state |
| [word-scale-bloom-with-lower-third-yzuvu](#word-scale-bloom-with-lower-third-yzuvu) | title-card | scale-bloom, blur-rack, slide-in | measured | serious | a single key term is named as the anchor concept of a segment |
| [year-badge-pop-on-warm-gradient-yzuvu](#year-badge-pop-on-warm-gradient-yzuvu) | title-card | pop, overshoot, settle | measured | warm | a pivotal year lands as the marker for a turning point |
| [year-compare-into-world-map-reveal-yzuvu](#year-compare-into-world-map-reveal-yzuvu) | map | slide-in, mask-reveal, wipe | measured | neutral | two consecutive years are compared, then the scope widens to a global picture |
| [tagline-words-stagger-settle-bokeh-sv4ko](#tagline-words-stagger-settle-bokeh-sv4ko) | kinetic-type | stagger, slide-in, settle | measured | warm | a tagline or thesis line assembles word by word as the calm payoff of a section |
| [cascading-clause-redword-emphasis-sv4ko](#cascading-clause-redword-emphasis-sv4ko) | kinetic-type | stagger, slide-in, pop | punchy | serious | a long claim unspools clause by clause with one charged word punched in red |
| [matrix-rain-into-kinetic-payoff-sv4ko](#matrix-rain-into-kinetic-payoff-sv4ko) | kinetic-type | particle, kinetic-type, pop | punchy | triumphant | a wall of falling data resolves into the headline takeaway of a section |

## Entries


### tilted-document-flip-beside-cutout-ab3fc
- Hero: `tilted-document-flip-beside-cutout-ab3fc.png` · Strip: `tilted-document-flip-beside-cutout-ab3fc-strip.png`
- Tags: motion=[card-flip, slide-in, settle] · archetype=side-cutout · energy=punchy · mood=serious
- Use when: a long quote or source document is revealed beside the speaker as supporting evidence
- Motion: A person cutout holds the left third while a document panel sweeps in from the right edge sharply skewed on its vertical axis, leading corner forward like a turning page. Across the strip it counter-rotates as it travels left, the 3D tilt flattening out until the panel snaps square and fills the right two-thirds with a settled wall of body text. The cutout stays locked; only the card moves, giving a single decisive flip-in with no overshoot.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.5189 · eased_energy_share=0.937 · sparsity=0.5644 · spatial_concentration=0.6919 · mov_texture=18.7359)
- Source: https://www.youtube.com/watch?v=0hD4K3Ab3Fc @ 9:50-9:53

### tilted-credential-card-flip-reveal-ab3fc
- Hero: `tilted-credential-card-flip-reveal-ab3fc.png` · Strip: `tilted-credential-card-flip-reveal-ab3fc-strip.png`
- Tags: motion=[card-flip, slide-in, settle] · archetype=lower-third · energy=punchy · mood=serious
- Use when: a person's name and credential lands as an at-a-glance identity card
- Motion: A subject photo sits center while a compact info card enters from the right under a steep skew, its near edge swung toward camera. As the strip advances the card rotates flat and slides into place, name and affiliation (Michael Dion, MIT) resolving line by line as the tilt unwinds. It settles square at the right edge as a clean credential card, one crisp flip with the type only legible once the panel squares up.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=3.0165 · eased_energy_share=0.9936 · sparsity=0.7026 · spatial_concentration=0.7929 · mov_texture=23.1247)
- Source: https://www.youtube.com/watch?v=0hD4K3Ab3Fc @ 10:10-10:12

### vs-versus-title-card-logo-assemble-wdl3o
- Hero: `vs-versus-title-card-logo-assemble-wdl3o.png` · Strip: `vs-versus-title-card-logo-assemble-wdl3o-strip.png`
- Tags: motion=[mask-reveal, pop, settle] · archetype=split-contrast · energy=punchy · mood=tense
- Use when: a head-to-head comparison kicks off and you need to frame the two sides squaring up
- Motion: Reads left-to-right as a versus title-card assembling: a glowing cyan 'VS' glyph pops in first, then the 'Free Software Foundation' lockup builds beside it one tier at a time, the abbreviated 'SF/FSF' caps materializing before the full stacked wordmark resolves underneath. Each element snaps in with a soft electric bloom and settles without overshoot. By the final frames both halves sit balanced around the central VS, the whole card glowing steady against the dark blue substrate.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.738 · eased_energy_share=0.937 · sparsity=0.0165 · spatial_concentration=0.3682 · mov_texture=4.5286)
- Source: https://www.youtube.com/watch?v=D6MwzBwdl3o @ 0:53-0:56

### connecting-line-draws-to-globe-node-wdl3o
- Hero: `connecting-line-draws-to-globe-node-wdl3o.png` · Strip: `connecting-line-draws-to-globe-node-wdl3o-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=map · energy=measured · mood=neutral
- Use when: a point connects to a place or network node and you want the link to physically trace its way to the destination
- Motion: Opens on a soft-focus webcam figure with a lower-third name ('Stéphane') fading up, then a luminous cyan path draws on from the left and snakes across the frame in a long S-curve. The line lands on a small wireframe globe that pops into the right third, a labeled node ('Chat Remoy') settling beside it. The curve animates as a continuous draw-on rather than a slide, so the eye follows the connection being made from caption to globe.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=17.474 · eased_energy_share=0.965 · sparsity=0.0102 · spatial_concentration=0.0209 · mov_texture=8.8175)
- Source: https://www.youtube.com/watch?v=D6MwzBwdl3o @ 7:20-7:22

### wireframe-logo-glow-bloom-title-wdl3o
- Hero: `wireframe-logo-glow-bloom-title-wdl3o.png` · Strip: `wireframe-logo-glow-bloom-title-wdl3o-strip.png`
- Tags: motion=[scale-bloom, settle] · archetype=title-card · energy=measured · mood=warm
- Use when: a brand or movement gets named and you want its emblem to glow up as the section title
- Motion: A cyan wireframe GNU-head emblem holds center-frame and blooms brighter while the 'Open Source' wordmark glows steady over it, the glyph edges pulsing with electric light across the first frames. The title holds, then the strip cuts to a dark terminal where green command-line text begins to type on. The motion is a sustained glow-bloom on the logo that settles before the hard cut to the code panel.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.1009 · eased_energy_share=0.9932 · sparsity=0.1366 · spatial_concentration=0.3648 · mov_texture=18.1886)
- Source: https://www.youtube.com/watch?v=D6MwzBwdl3o @ 8:26-8:30

### product-page-headline-then-code-panel-reveal-pb6y0
- Hero: `product-page-headline-then-code-panel-reveal-pb6y0.png` · Strip: `product-page-headline-then-code-panel-reveal-pb6y0-strip.png`
- Tags: motion=[mask-reveal, slide-in, settle] · archetype=code-reveal · energy=measured · mood=clinical
- Use when: a product or tool is introduced and its core promise plus a screenshot of it working land together
- Motion: On a near-black backdrop the centered headline 'Cut code review time & bugs in half instantly.' resolves first with a small UI card and CTA beneath it. As the strip advances a dark code-review panel slides/masks in to the right of the headline, its rows of code and inline annotations populating left-to-right. The composition settles into a balanced two-column product-page layout — copy left of center, the live code panel right — with no overshoot, an even measured build rather than a snappy pop.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.434 · eased_energy_share=0.8884 · sparsity=0.3223 · spatial_concentration=0.5123 · mov_texture=9.1065)
- Source: https://www.youtube.com/watch?v=FjSPm1PB6Y0 @ 4:48-4:58

### electric-title-card-logo-reveal-jejkw
- Hero: `electric-title-card-logo-reveal-jejkw.png` · Strip: `electric-title-card-logo-reveal-jejkw-strip.png`
- Tags: motion=[kinetic-type, scale-bloom, settle] · archetype=title-card · energy=punchy · mood=tense
- Use when: a chapter or section opens on its name with high-voltage attitude
- Motion: Opens on an empty electric-blue field where jagged lightning filaments crackle and shift across the frame left-to-right, energizing the negative space before any title lands. Mid-strip a glowing cyan 3D logo (a mascot perched on a fluted column) rises into center and a chunky cyan title word blooms in over it, scaling up with a slight glow swell rather than a hard cut. By the last frames the title and logo have settled to full opacity while the lightning keeps animating behind, so the card holds with a live, charged background instead of a static plate.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.694 · eased_energy_share=0.8151 · sparsity=0.2874 · spatial_concentration=0.6047 · mov_texture=11.4645)
- Source: https://www.youtube.com/watch?v=RCHhAEjEjKw @ 0:47-0:51

### blur-rack-into-blueprint-spec-card-puexo
- Hero: `blur-rack-into-blueprint-spec-card-puexo.png` · Strip: `blur-rack-into-blueprint-spec-card-puexo-strip.png`
- Tags: motion=[blur-rack, mask-reveal, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a technical spec or blueprint resolves into focus as the explanation gets concrete
- Motion: The strip opens on out-of-focus metallic panels that rack from soft blur into a sharp green blueprint-style schematic with dimension callouts ('7ft' with arrows). The dashed measurement lines and labeled diagram resolve first, then the frame hands off to a bordered product-spec card with a grid of component icons. The motion is the rack from blur to sharp plus the wipe to the spec layout — measured, no overshoot, settling crisply on the labeled diagram.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.8133 · eased_energy_share=0.9568 · sparsity=0.0063 · spatial_concentration=0.2368 · mov_texture=24.6138)
- Source: https://www.youtube.com/watch?v=gSjV9BPueXo @ 2:02-2:05

### smoke-particle-dissolve-screen-swap-puexo
- Hero: `smoke-particle-dissolve-screen-swap-puexo.png` · Strip: `smoke-particle-dissolve-screen-swap-puexo-strip.png`
- Tags: motion=[particle, wipe, morph] · archetype=device-mockup · energy=punchy · mood=neutral
- Use when: one screen or scene dissolves into the next as a designed transition beat
- Motion: A dense black smoke/particle cloud blooms from the left and sweeps across a desktop UI screenshot, eating the old screen and uncovering a new phone/app mockup underneath as it passes. The particle mass grows frame to frame then dissipates to the right, leaving the fresh screen settled. It reads as a smoke-dissolve transition wiping left-to-right between two graphic screens.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.887 · eased_energy_share=0.9557 · sparsity=0.0135 · spatial_concentration=0.2091 · mov_texture=15.1724)
- Source: https://www.youtube.com/watch?v=gSjV9BPueXo @ 4:55-4:57

### grid-wipe-into-product-poster-reveal-puexo
- Hero: `grid-wipe-into-product-poster-reveal-puexo.png` · Strip: `grid-wipe-into-product-poster-reveal-puexo-strip.png`
- Tags: motion=[wipe, slide-in, settle] · archetype=title-card · energy=punchy · mood=triumphant
- Use when: a hero product and headline land together as the payoff reveal
- Motion: The strip starts on a glowing blue grid panel that wipes away to expose a red sports car on a poster layout. The 'DECLARE INDEPENDENCE / THE NEW ROADSTER' headline fades up over the car, and across the frames the composition tightens into a framed magazine-style title card. The car holds center while the type resolves on top — a wipe-in to a settled product poster, no bounce.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.9744 · eased_energy_share=0.8877 · sparsity=0.0032 · spatial_concentration=0.2283 · mov_texture=12.469)
- Source: https://www.youtube.com/watch?v=gSjV9BPueXo @ 9:22-9:25

### scribble-tangle-brain-draw-on-puexo
- Hero: `scribble-tangle-brain-draw-on-puexo.png` · Strip: `scribble-tangle-brain-draw-on-puexo-strip.png`
- Tags: motion=[draw-on, scale-bloom, pop] · archetype=diagram-build · energy=frenetic · mood=tense
- Use when: a beat depicts confusion, overthinking, or a tangled mental state
- Motion: From a black hold, an orange hand-drawn scribble explodes into a tangled mass above a profile-silhouette head, the loops accumulating to read as a knotted, overloaded brain. The scribble blooms in fast and holds, then the frame cuts to a two-figure silhouette conversation under a caption header. The draw-on of the chaotic orange tangle is the designed motion — frenetic, scribbled, no easing.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.4297 · eased_energy_share=0.9787 · sparsity=0.3391 · spatial_concentration=0.5584 · mov_texture=8.3041)
- Source: https://www.youtube.com/watch?v=gSjV9BPueXo @ 13:44-13:50

### word-scale-bloom-with-lower-third-yzuvu
- Hero: `word-scale-bloom-with-lower-third-yzuvu.png` · Strip: `word-scale-bloom-with-lower-third-yzuvu-strip.png`
- Tags: motion=[scale-bloom, blur-rack, slide-in] · archetype=title-card · energy=measured · mood=serious
- Use when: a single key term is named as the anchor concept of a segment
- Motion: The strip opens on a screen-capture of a 'Language' reference article, then racks out of that B-roll into a clean light field where the word 'Language' sits centered and blooms up in scale across the final frames, gaining weight as it settles. A thin lower-third attribution ('ABACO Knowledge') slides in beneath it on the right. The cadence is a soft blur-to-sharp rack from busy footage to a single calm display word.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=7.4798 · eased_energy_share=0.866 · sparsity=0.0215 · spatial_concentration=0.4361 · mov_texture=11.5386)
- Source: https://www.youtube.com/watch?v=oDttLGYzuvU @ 1:16-1:23

### year-badge-pop-on-warm-gradient-yzuvu
- Hero: `year-badge-pop-on-warm-gradient-yzuvu.png` · Strip: `year-badge-pop-on-warm-gradient-yzuvu-strip.png`
- Tags: motion=[pop, overshoot, settle] · archetype=title-card · energy=measured · mood=warm
- Use when: a pivotal year lands as the marker for a turning point
- Motion: A warm sunset gradient (magenta-to-amber) holds and breathes across the first five frames with no foreground, then on the final frame a solid blue circular badge pops in dead-center carrying the year '2020'. The badge arrives as a single punctuated event against the steady gradient, reading as an overshoot-and-settle disc rather than a slow fade. The contrast of the cool blue token over the warm wash makes the number snap forward.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=18.4293 · eased_energy_share=0.9456 · sparsity=0.0869 · spatial_concentration=0.2628 · mov_texture=1.6137)
- Source: https://www.youtube.com/watch?v=oDttLGYzuvU @ 7:12-7:15

### year-compare-into-world-map-reveal-yzuvu
- Hero: `year-compare-into-world-map-reveal-yzuvu.png` · Strip: `year-compare-into-world-map-reveal-yzuvu-strip.png`
- Tags: motion=[slide-in, mask-reveal, wipe] · archetype=map · energy=measured · mood=neutral
- Use when: two consecutive years are compared, then the scope widens to a global picture
- Motion: The strip starts with two year labels '2022' and '2023' set side by side on a purple field, repeats them on a black field as a beat-marking restate, then wipes to a pink hold and resolves into a satellite world map that reveals continent-by-continent across the last frames. The cadence steps from a paired numeric compare to a global map mask-reveal, the warm amber landmasses emerging out of darker ocean. Camera stays locked; the motion is the map masking on, not a push.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.8754 · eased_energy_share=0.9747 · sparsity=0.0001 · spatial_concentration=0.175 · mov_texture=9.5908)
- Source: https://www.youtube.com/watch?v=oDttLGYzuvU @ 8:54-8:58

### tagline-words-stagger-settle-bokeh-sv4ko
- Hero: `tagline-words-stagger-settle-bokeh-sv4ko.png` · Strip: `tagline-words-stagger-settle-bokeh-sv4ko-strip.png`
- Tags: motion=[stagger, slide-in, settle] · archetype=kinetic-type · energy=measured · mood=warm
- Use when: a tagline or thesis line assembles word by word as the calm payoff of a section
- Motion: Over a soft dark-blue bokeh field the phrase builds one word at a time: 'Arch,' then 'but for' arrive upper-left, then 'normal' and 'people' drop in lower-right on a diagonal, each word fading up from blur and easing to rest. The stagger step is gentle, roughly a beat between words, with no overshoot — words settle softly into a loose two-tier diagonal layout. By the last frame the full line holds static, italic, evenly spaced.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.954 · eased_energy_share=0.9567 · sparsity=0.0316 · spatial_concentration=0.3915 · mov_texture=3.8384)
- Source: https://www.youtube.com/watch?v=y8ts6ZSv4ko @ 3:41-3:43

### cascading-clause-redword-emphasis-sv4ko
- Hero: `cascading-clause-redword-emphasis-sv4ko.png` · Strip: `cascading-clause-redword-emphasis-sv4ko-strip.png`
- Tags: motion=[stagger, slide-in, pop] · archetype=kinetic-type · energy=punchy · mood=serious
- Use when: a long claim unspools clause by clause with one charged word punched in red
- Motion: Against a dark grungy texture a sentence cascades across the frame clause by clause — 'Open source' (red) anchors top-left, then 'has a long', 'history of', 'leaders', 'refusing' each slide in staggered down a stepped diagonal. Words fade up from low opacity and snap to position with little overshoot, the red emphasis word popping brighter than the white body. The reveal is brisker than beat 3, packing more words per second, and the layout keeps stair-stepping downward rather than settling into a fixed block.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.6054 · eased_energy_share=0.9085 · sparsity=0.0253 · spatial_concentration=0.4489 · mov_texture=4.7982)
- Source: https://www.youtube.com/watch?v=y8ts6ZSv4ko @ 8:04-8:06

### matrix-rain-into-kinetic-payoff-sv4ko
- Hero: `matrix-rain-into-kinetic-payoff-sv4ko.png` · Strip: `matrix-rain-into-kinetic-payoff-sv4ko-strip.png`
- Tags: motion=[particle, kinetic-type, pop] · archetype=kinetic-type · energy=punchy · mood=triumphant
- Use when: a wall of falling data resolves into the headline takeaway of a section
- Motion: The strip opens on a full-frame field of green matrix-style character rain streaming downward, columns brightening and dimming as glyphs fall. A short red marker bar and body text flash in over the rain mid-strip, then the scene cuts to a dark panel where the payoff line 'it gets the most public validation' pops in staggered — 'most' and 'public' arriving first, 'validation' lighting up blue last. The transition is a hard cut from texture to type rather than a morph; the closing words land with a quick scale-pop, no slow settle.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.764 · eased_energy_share=0.8753 · sparsity=0.082 · spatial_concentration=0.3262 · mov_texture=5.013)
- Source: https://www.youtube.com/watch?v=y8ts6ZSv4ko @ 13:10-13:14

### dual-label-kinetic-type-over-icon-pedestal-6mpsq
- Hero: `dual-label-kinetic-type-over-icon-pedestal-6mpsq.png` · Strip: `dual-label-kinetic-type-over-icon-pedestal-6mpsq-strip.png`
- Tags: motion=[kinetic-type, pop, settle] · archetype=kinetic-type · energy=punchy · mood=tense
- Use when: two opposing words frame a stakes-defining either/or
- Motion: Two bold words, REVOLUTION at left and SURVIVAL at right, sit flanking a small pixel-icon mounted on a tall pedestal, all over a soft sky gradient. Across the strip the background recolors from lavender to a saturated blue then to warm dusk while the words hold their anchored positions and pulse in weight, the icon staying centered on its column. The beat then hard-cuts to a static 3D-rendered open-doorway room, so the designed motion lives entirely in the first half, a held kinetic-type pairing rather than a travelling one.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.4888 · eased_energy_share=0.9777 · sparsity=0.4413 · spatial_concentration=0.5195 · mov_texture=13.4205)
- Source: https://www.youtube.com/watch?v=-8EDhm6mpsQ @ 4:26-4:31

### vertical-timeline-cards-drop-stagger-6mpsq
- Hero: `vertical-timeline-cards-drop-stagger-6mpsq.png` · Strip: `vertical-timeline-cards-drop-stagger-6mpsq-strip.png`
- Tags: motion=[stagger, slide-in, settle] · archetype=timeline · energy=measured · mood=serious
- Use when: a sequence of events stacks up to explain how something changed over time
- Motion: A vertical spine line runs down the frame and rounded text cards attach to it in top-to-bottom order, the topmost (THE ORIGINAL PLATFORM) landing first, then THE COMPANY REMOVED, then ANOTHER PLATFORM below, each sliding in to its node and settling with no overshoot. The background drifts from violet to teal to amber dusk under the building stack, keeping the cards readable. By the last frames the timeline dissolves out to a crowd silhouette, so the usable cadence is the measured staggered drop-in of nodes onto a connector line.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.0499 · eased_energy_share=0.9362 · sparsity=0.5784 · spatial_concentration=0.6911 · mov_texture=8.5934)
- Source: https://www.youtube.com/watch?v=-8EDhm6mpsQ @ 6:33-6:35

### glass-skyscraper-rises-from-black-6mpsq
- Hero: `glass-skyscraper-rises-from-black-6mpsq.png` · Strip: `glass-skyscraper-rises-from-black-6mpsq-strip.png`
- Tags: motion=[draw-on, scale-bloom, settle] · archetype=device-mockup · energy=measured · mood=neutral
- Use when: an entity or platform is established as it is introduced
- Motion: Against a near-black field with a faint blue ribbon texture, a 3D glass-and-steel skyscraper builds upward from the bottom edge frame by frame, gaining stories and reflective blue facets as it climbs until it dominates the upper frame. The growth reads as a steady draw-on extrusion rather than a bounce, the tower settling at full height in the final frame with crisp glass highlights. A slow vertical reveal that establishes a single hero object.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.5974 · eased_energy_share=0.9207 · sparsity=0.528 · spatial_concentration=0.582 · mov_texture=31.5821)
- Source: https://www.youtube.com/watch?v=-8EDhm6mpsQ @ 7:42-7:45

### logo-with-ring-draw-on-and-checklist-6mpsq
- Hero: `logo-with-ring-draw-on-and-checklist-6mpsq.png` · Strip: `logo-with-ring-draw-on-and-checklist-6mpsq-strip.png`
- Tags: motion=[draw-on, particle, pop] · archetype=logo · energy=punchy · mood=triumphant
- Use when: a brand or tool is spotlighted as the payoff of a point
- Motion: The strip opens on a left-aligned checklist of three bullet rows beside a small blue logo, then snaps to a centered blue container-ship logo with a bright green circular ring sweeping on around it. The ring draws as a stroke that closes into a full circle while faint particles scatter in the dark blue field, the logo holding dead-center and the ring pulsing once it completes. A logo-spotlight with a draw-on accent ring, more energetic and triumphant than the other kept beats.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.9157 · eased_energy_share=0.9608 · sparsity=0.3323 · spatial_concentration=0.5718 · mov_texture=10.5745)
- Source: https://www.youtube.com/watch?v=-8EDhm6mpsQ @ 7:54-7:56

### glass-feature-cards-cycle-flip-pl4sk
- Hero: `glass-feature-cards-cycle-flip-pl4sk.png` · Strip: `glass-feature-cards-cycle-flip-pl4sk-strip.png`
- Tags: motion=[slide-in, card-flip, settle] · archetype=quote-card · energy=punchy · mood=warm
- Use when: a sequence of named tradeoffs cycles forward, each card swapping in for the last
- Motion: Two frosted glassmorphic cards hold center-frame: a coral 'Commands Over UI' card on the left and a paler plugin-note card labeled 'Second' on the right. Across the strip the pair slides leftward in short punchy steps as a 'Third' card pushes in from the right, so the set advances one slot at a time rather than dissolving. On the final frame the right card peels into a curled card-flip, tipping the stack over to reveal the next label. The cycle is even and measured, each card settling flat before the next nudge.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=6.6669 · eased_energy_share=0.8754 · sparsity=0.092 · spatial_concentration=0.0594 · mov_texture=10.5313)
- Source: https://www.youtube.com/watch?v=8605poPL4Sk @ 2:48-2:51

### node-graph-morph-to-triangle-pl4sk
- Hero: `node-graph-morph-to-triangle-pl4sk.png` · Strip: `node-graph-morph-to-triangle-pl4sk-strip.png`
- Tags: motion=[morph, scale-bloom, settle] · archetype=diagram-build · energy=punchy · mood=serious
- Use when: a connected system collapses into a single deploy or build symbol as the payoff
- Motion: Opens on a grid of green glowing diamond nodes (gear, chip, wrench icons) linked by dashed connector lines, reading as a small flow diagram. Across the strip the camera pushes in and the dashed network compresses and morphs, the glowing diamonds blooming and merging toward a single shape. By the last two frames everything has resolved into one large solid green triangle that settles dead-center with a soft glow. The motion is a continuous zoom-and-consolidate, not a cut.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.3884 · eased_energy_share=0.9649 · sparsity=0.0075 · spatial_concentration=0.2467 · mov_texture=3.8937)
- Source: https://www.youtube.com/watch?v=8605poPL4Sk @ 3:54-3:57

### checklist-panel-scale-push-pl4sk
- Hero: `checklist-panel-scale-push-pl4sk.png` · Strip: `checklist-panel-scale-push-pl4sk-strip.png`
- Tags: motion=[scale-bloom, parallax-push, slide-in] · archetype=checklist · energy=punchy · mood=neutral
- Use when: a step-by-step instruction list zooms up to fill frame as the active how-to
- Motion: A small 'Package Control Solution' panel with an ordered list (Open Command Palette / Type install / Select plugin / Plugin installs) sits left of an orange Sublime 'S' badge. Across the strip the whole panel scales up hard and pushes toward camera, the list text growing past readable size while the layout drifts left, so the early steps slide out of frame and the later ones magnify. It reads as an aggressive zoom-push onto the checklist rather than a settle; the 'S' badge holds position as the anchor on the right.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.3585 · eased_energy_share=0.8722 · sparsity=0.3092 · spatial_concentration=0.4785 · mov_texture=5.3409)
- Source: https://www.youtube.com/watch?v=8605poPL4Sk @ 6:29-6:32

### logo-chevron-wipe-into-dollar-particle-field-pl4sk
- Hero: `logo-chevron-wipe-into-dollar-particle-field-pl4sk.png` · Strip: `logo-chevron-wipe-into-dollar-particle-field-pl4sk-strip.png`
- Tags: motion=[wipe, particle, snap] · archetype=title-card · energy=frenetic · mood=playful
- Use when: a brand mark hands off to a swarm of repeated icons as a fast scene transition
- Motion: The Sublime 'S' logo on its dark circle holds, then an orange chevron wipes across frame from the right, sweeping the logo away. The wipe resolves into a dense tiled grid of small orange '$' symbols that flickers and shimmers like a particle field for several frames. On the last frame a single black download arrow snaps in over the field. Fast and punctuated — a hard wipe into a busy repeating-icon texture.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.5313 · eased_energy_share=0.9868 · sparsity=0.0358 · spatial_concentration=0.2533 · mov_texture=8.8149)
- Source: https://www.youtube.com/watch?v=8605poPL4Sk @ 8:03-8:05

### parallax-corridor-push-kinetic-type-wcixo
- Hero: `parallax-corridor-push-kinetic-type-wcixo.png` · Strip: `parallax-corridor-push-kinetic-type-wcixo-strip.png`
- Tags: motion=[parallax-push, kinetic-type, slide-in] · archetype=kinetic-type · energy=measured · mood=serious
- Use when: a transition that pulls the viewer forward into the next idea while a word lands
- Motion: The strip pushes the camera straight down a grey 3D corridor — the perspective walls widen frame to frame as if moving forward, a steady parallax-push rather than a cut. A figure slides in from the right edge mid-strip, and the kinetic word 'DON'T' types/snaps on in the lower-left, building letter by letter ('DO' then 'DON'T') as the push continues. The text settles flush bottom-left while the corridor keeps gliding, so motion never fully stops.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.0395 · eased_energy_share=0.9459 · sparsity=0.3795 · spatial_concentration=0.5042 · mov_texture=2.0073)
- Source: https://www.youtube.com/watch?v=hXrQbgWCIxo @ 1:00-1:07

### dashboard-ui-mockup-reveal-caption-card-wcixo
- Hero: `dashboard-ui-mockup-reveal-caption-card-wcixo.png` · Strip: `dashboard-ui-mockup-reveal-caption-card-wcixo-strip.png`
- Tags: motion=[slide-in, mask-reveal, settle] · archetype=device-mockup · energy=measured · mood=neutral
- Use when: a product or tool is introduced and its interface needs to be shown off
- Motion: A dark dashboard UI mockup slides up into frame over a desktop background, the browser chrome and panels revealing top-down across the first frames. A black caption card ('Cut code review time & bugs in half instantly') wipes in over it, then the view swaps to a second dashboard state showing populated stat panels and an 'Industry-leading contest' header. Each UI swap settles cleanly before the next, ending on a hard green wipe-out at the right.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.4066 · eased_energy_share=0.6559 · sparsity=0.4945 · spatial_concentration=0.5306 · mov_texture=9.902)
- Source: https://www.youtube.com/watch?v=hXrQbgWCIxo @ 4:24-4:40

### document-card-tumble-in-overshoot-wcixo
- Hero: `document-card-tumble-in-overshoot-wcixo.png` · Strip: `document-card-tumble-in-overshoot-wcixo-strip.png`
- Tags: motion=[slide-in, overshoot, settle] · archetype=quote-card · energy=measured · mood=neutral
- Use when: a quoted notice or release note is dropped in as a callout over a colored field
- Motion: Over a flat green field, a white document/note card flies in from the upper-left on a slight tilt, rotated like a sheet of paper mid-toss, with a small sticky-note icon trailing it lower-right. The card holds its skew through the middle frames, then on the final frame it squares up and resolves into a readable titled card ('Notepad++ v7.8.9 — Stand with Hong Kong') with body text — an overshoot-then-settle from rotated to upright.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=1.6509 · eased_energy_share=0.9785 · sparsity=0.639 · spatial_concentration=0.6764 · mov_texture=14.1081)
- Source: https://www.youtube.com/watch?v=hXrQbgWCIxo @ 5:58-6:00

### kinetic-date-then-red-map-morph-wcixo
- Hero: `kinetic-date-then-red-map-morph-wcixo.png` · Strip: `kinetic-date-then-red-map-morph-wcixo-strip.png`
- Tags: motion=[kinetic-type, morph, draw-on] · archetype=map · energy=frenetic · mood=tense
- Use when: a date or location beat hits hard and a region shape needs to slam onto screen
- Motion: First half is full-frame kinetic type: 'IN AUGUST 2020' jitters and scales across the green field, flanked by document-and-clock icons that bob in from both sides, the whole title nudging position frame to frame for a restless, frenetic feel. Then it cuts sharply and a solid red landmass/region shape morphs and grows in from the lower area, drawing on its silhouette and enlarging across the last two frames. Energetic, punchy hand-off from text to map graphic.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.8707 · eased_energy_share=0.9499 · sparsity=0.3799 · spatial_concentration=0.5817 · mov_texture=6.8353)
- Source: https://www.youtube.com/watch?v=hXrQbgWCIxo @ 6:04-6:07

### logo-over-rising-fire-then-doc-slide-ffx0s
- Hero: `logo-over-rising-fire-then-doc-slide-ffx0s.png` · Strip: `logo-over-rising-fire-then-doc-slide-ffx0s-strip.png`
- Tags: motion=[particle, slide-in, settle] · archetype=title-card · energy=punchy · mood=ominous
- Use when: a brand or institution is framed as the thing under fire — heat building beneath a logo before the receipt drops
- Motion: A white OpenAI logo holds dead-center on black while a band of animated orange fire creeps up from the bottom edge, frame by frame — the flames are low and sparse at first, then climb and brighten across the strip until they lick a third of the way up. The logo never moves; the energy is all in the rising particle fire underneath it. In the final frame the whole fire-logo composition is shoved aside and a dark email/document panel slides in from the right and settles flush, reading as the payoff receipt after the slow-burn build.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.5201 · eased_energy_share=0.9436 · sparsity=0.238 · spatial_concentration=0.4889 · mov_texture=8.4939)
- Source: https://www.youtube.com/watch?v=3tbB2dffx0s @ 5:27-5:31

### sketch-draw-to-glow-burn-title-ybgv0
- Hero: `sketch-draw-to-glow-burn-title-ybgv0.png` · Strip: `sketch-draw-to-glow-burn-title-ybgv0-strip.png`
- Tags: motion=[draw-on, scale-bloom, glitch] · archetype=title-card · energy=punchy · mood=playful
- Use when: a segment's title card stamps in as the show's signature ident
- Motion: Opens on a cluster of small webcam thumbnails that collapse into a single hand-drawn wireframe sketch of a face on black. The sketch then ignites: 'THE CODE REPORT' wordmark burns up from the center with a hot white scale-bloom that overexposes the whole frame, settling as the letters cool back into a contained glowing title. The bloom peaks hard mid-strip with red scanline accents, then clamps down — no easing tail, it just snaps to the held logo.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.9961 · eased_energy_share=0.9205 · sparsity=0.1205 · spatial_concentration=0.4046 · mov_texture=16.4711)
- Source: https://www.youtube.com/watch?v=9OQ5vaYbGV0 @ 0:55-1:01

### tumbling-logo-collage-into-countup-chart-ybgv0
- Hero: `tumbling-logo-collage-into-countup-chart-ybgv0.png` · Strip: `tumbling-logo-collage-into-countup-chart-ybgv0-strip.png`
- Tags: motion=[parallax-drift, count-up, draw-on] · archetype=collage · energy=frenetic · mood=triumphant
- Use when: a scale stat lands as the payoff after a flurry of brand logos
- Motion: A loose collage of app/brand logos (Maps pin, YouTube, Chrome, Android, Google) tumbles with heavy motion blur while kinetic '>1B USERS' then '>3B USERS' text skews across the frame. The logos drift and clear, then a line chart draws on from left to right against a dark plot, the trend line sweeping up to a '9.7T' callout that settles at the upper right. The handoff is a clean wipe from chaotic logo motion to a calm, axis-anchored chart.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=7.8774 · eased_energy_share=0.9151 · sparsity=0.0031 · spatial_concentration=0.371 · mov_texture=10.6666)
- Source: https://www.youtube.com/watch?v=9OQ5vaYbGV0 @ 1:10-1:13

### rotating-particle-torus-training-viz-ybgv0
- Hero: `rotating-particle-torus-training-viz-ybgv0.png` · Strip: `rotating-particle-torus-training-viz-ybgv0-strip.png`
- Tags: motion=[particle, camera-orbit, settle] · archetype=diagram-build · energy=punchy · mood=ominous
- Use when: an abstract system or training process is visualized as it churns
- Motion: Starts with a sparse scatter of small glowing chip nodes drifting on black, one boxed as the focus. The field then resolves into a dense torus built entirely of golden particle dots that slowly rotates in 3D, the surface shimmering as points catch light along the ring. A 'TRAINING' label and a single highlighted chip mockup punch in at the tail. The motion is a steady orbital churn rather than a snap — it builds density and holds the rotation.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.7866 · eased_energy_share=0.9905 · sparsity=0.0013 · spatial_concentration=0.2482 · mov_texture=21.1658)
- Source: https://www.youtube.com/watch?v=9OQ5vaYbGV0 @ 1:45-1:50

### benchmark-table-to-scatter-chart-wipe-ybgv0
- Hero: `benchmark-table-to-scatter-chart-wipe-ybgv0.png` · Strip: `benchmark-table-to-scatter-chart-wipe-ybgv0-strip.png`
- Tags: motion=[wipe, slide-in, settle] · archetype=diagram-build · energy=frenetic · mood=clinical
- Use when: a dense benchmark comparison resolves into a single readable chart
- Motion: Holds on a multi-column benchmark table with a highlighted result column, then the whole table wipes off to the left as a titled scatter plot ('Artificial Analysis Intelligence Index vs Output Speed') slides in from the right. The chart settles with labeled dots scattered across the axes and a '3.5 Flash' point called out. The transition is a hard horizontal swap — table out, chart in — with the chart easing to rest as the last frame shrinks slightly to seat it in frame.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=17.4582 · eased_energy_share=0.9678 · sparsity=0 · spatial_concentration=0.0079 · mov_texture=16.671)
- Source: https://www.youtube.com/watch?v=9OQ5vaYbGV0 @ 2:58-3:00

### live-shot-to-dashboard-stat-cards-vparw
- Hero: `live-shot-to-dashboard-stat-cards-vparw.png` · Strip: `live-shot-to-dashboard-stat-cards-vparw-strip.png`
- Tags: motion=[wipe, count-up, settle] · archetype=stat-hero · energy=punchy · mood=neutral
- Use when: a real-world clip hands off to a data dashboard that lands the headline numbers
- Motion: Opens on a live TED-stage shot, then a hard horizontal wipe cuts to a dark analytics dashboard. A row of colored stat cards (612 / 472 / 448 / 128) and a 'Beverity breakdown' panel populate, and the 'Engineering the future of AI' title resolves crisp at lower-right. The wipe is fast and full-frame; the numbers read as already-counted on arrival, settling without overshoot into a static dashboard hold.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=20.586 · eased_energy_share=0.9943 · sparsity=0.0003 · spatial_concentration=0.188 · mov_texture=9.7175)
- Source: https://www.youtube.com/watch?v=FM5-R4VPArw @ 0:54-0:56

### list-rows-marker-sweep-torn-strip-vparw
- Hero: `list-rows-marker-sweep-torn-strip-vparw.png` · Strip: `list-rows-marker-sweep-torn-strip-vparw-strip.png`
- Tags: motion=[marker-sweep, pop, settle] · archetype=checklist · energy=punchy · mood=playful
- Use when: a specific row in a list or feed gets singled out as the point that matters
- Motion: A dark scrolling feed of list rows sits static, then a blue marker sweep lights up one row left-to-right. Across the next frames a torn-paper emphasis strip (white with blue text) pops over the highlighted rows, growing from one to two stacked strips that tilt slightly off-axis like taped notes. The sweep is quick and the strips snap in with a paper-pop, settling skewed rather than aligned for a scrappy hand-annotated feel.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.7548 · eased_energy_share=0.9087 · sparsity=0.0154 · spatial_concentration=0.1221 · mov_texture=11.916)
- Source: https://www.youtube.com/watch?v=FM5-R4VPArw @ 2:22-2:26

### ui-app-grid-pricing-panel-slide-vparw
- Hero: `ui-app-grid-pricing-panel-slide-vparw.png` · Strip: `ui-app-grid-pricing-panel-slide-vparw-strip.png`
- Tags: motion=[slide-in, settle, stagger] · archetype=device-mockup · energy=measured · mood=neutral
- Use when: a product UI pivots from an overview grid to reveal a pricing or detail panel
- Motion: A light Hostinger dashboard holds on a grid of app-icon tiles, steady through the first frames. Then a dark pricing panel slides in from the right, carrying VPS plan cards ($5.99 / $8.99 / $12.00) that resolve in a left-to-right stagger. The slide is measured and horizontal; the panel settles flush at frame-right with the cards arriving cleanly, no overshoot, ending on a static pricing layout.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.3639 · eased_energy_share=0.9925 · sparsity=0.6996 · spatial_concentration=0.0261 · mov_texture=16.3429)
- Source: https://www.youtube.com/watch?v=FM5-R4VPArw @ 3:17-3:20

### year-counter-roll-motionblur-temye
- Hero: `year-counter-roll-motionblur-temye.png` · Strip: `year-counter-roll-motionblur-temye-strip.png`
- Tags: motion=[count-up, slide-in, blur-rack] · archetype=kinetic-type · energy=punchy · mood=neutral
- Use when: a date or version ticks forward to mark progression through a timeline
- Motion: A single large year numeral sits centered on near-black. Each frame the old number rolls upward and out while the next one slides up to replace it (2009, then 2009/2010, 2012/2013, 2014, 2017/2018), the in-between frames smeared with vertical motion blur so the swap reads as a fast odometer flip. The numeral lands crisp and centered before the next tick. No camera move; the whole motion is a quick vertical roll-and-settle on one element.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.6067 · eased_energy_share=0.7044 · sparsity=0 · spatial_concentration=0.3819 · mov_texture=5.2589)
- Source: https://www.youtube.com/watch?v=JfPWbttemYE @ 0:43-0:45

### code-editor-blur-rack-retype-temye
- Hero: `code-editor-blur-rack-retype-temye.png` · Strip: `code-editor-blur-rack-retype-temye-strip.png`
- Tags: motion=[blur-rack, typewriter, settle] · archetype=code-reveal · energy=measured · mood=neutral
- Use when: code transforms from a bare stub into the finished implementation as the explanation lands
- Motion: Opens on a dark editor (functions.js) holding a 3-line empty function stub with a blinking cursor. The middle frames rack fully out of focus into a colored blur smear, the screen-recording dissolve standing in for re-typing. It resolves sharp onto a complete filter/map/reduce/sort block of syntax-highlighted code, then a cursor hand-pointer taps to settle. The motion is a defocus-then-refocus crossfade between two code states rather than a literal per-character type, ending static and readable.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=15.3376 · eased_energy_share=0.9714 · sparsity=0 · spatial_concentration=0.1855 · mov_texture=2.4992)
- Source: https://www.youtube.com/watch?v=JfPWbttemYE @ 3:06-3:08

### brand-logo-wall-pop-stagger-temye
- Hero: `brand-logo-wall-pop-stagger-temye.png` · Strip: `brand-logo-wall-pop-stagger-temye-strip.png`
- Tags: motion=[pop, stagger, overshoot] · archetype=collage · energy=punchy · mood=playful
- Use when: a roster of names or brands assembles to show breadth of adoption
- Motion: Brand marks build onto a black field in a loose grid, one cohort per frame. Codecademy, 37signals and thoughtbot/Stripe are already present, then Trello and a rotating square logo pop in late, each scaling up with a slight rotational overshoot before settling upright (the square mark visibly tumbles a few degrees then locks square). The stagger is one or two logos per step, so the wall accretes rather than arriving all at once; everything holds in place once landed.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.9772 · eased_energy_share=0.9114 · sparsity=0.3159 · spatial_concentration=0.6022 · mov_texture=11.1091)
- Source: https://www.youtube.com/watch?v=JfPWbttemYE @ 3:40-3:43

### hdd-annotation-arrow-data-block-march-ycvya
- Hero: `hdd-annotation-arrow-data-block-march-ycvya.png` · Strip: `hdd-annotation-arrow-data-block-march-ycvya-strip.png`
- Tags: motion=[draw-on, slide-in, snap] · archetype=diagram-build · energy=punchy · mood=playful
- Use when: a mechanism is explained by annotating a real object with moving callouts
- Motion: Over a photo of an open hard-disk drive, a green annotation arrow draws on left-to-right while a cluster of blue pixelated data-blocks marches inward toward the platter, stepping a few blocks per frame. The blocks slide and snap into position rather than easing smoothly, giving a punchy stop-motion feel against the static photo. By the fourth frame the annotation has mostly collapsed/cleared, then the beat hard-cuts to a full Windows desktop screenshot with no transition.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.7242 · eased_energy_share=0.9324 · sparsity=0.2743 · spatial_concentration=0.5123 · mov_texture=6.1284)
- Source: https://www.youtube.com/watch?v=MtxP2pyCvYA @ 3:47-3:50

### word-stamp-pop-over-broll-8esmu
- Hero: `word-stamp-pop-over-broll-8esmu.png` · Strip: `word-stamp-pop-over-broll-8esmu-strip.png`
- Tags: motion=[pop, snap] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: a single keyword punches in to label or punctuate the moment
- Motion: The strip opens on plain footage with no overlay, then a bold red all-caps word ('DOWNTIME') snaps in center-frame with no slide — it appears at near-full size in one step rather than easing, the Fireship hard-cut stamp. It holds dead-still across the next several frames while the underlying footage keeps moving, then the strip cuts to a new B-roll shot. No drift, no fade: the word is on or off, punctuating the line it lands on.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.1244 · eased_energy_share=0.9505 · sparsity=0.0785 · spatial_concentration=0.3955 · mov_texture=14.5363)
- Source: https://www.youtube.com/watch?v=d53Zk28esmU @ 1:50-1:56

### strikethrough-stamp-over-caption-8esmu
- Hero: `strikethrough-stamp-over-caption-8esmu.png` · Strip: `strikethrough-stamp-over-caption-8esmu-strip.png`
- Tags: motion=[snap, wipe, pop] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: a stated cliche gets contradicted or struck down on the punchline
- Motion: First frames show only a quote caption ('follow your passion') lower on the frame over moving B-roll. Then a bold tilted red 'DON'T' stamp snaps in over the line and a strike effect wipes across the caption in the same beat, negating it. The stamp lands at full size in one hard step with no ease-in, and the strike sweeps left-to-right as it settles. The contradiction reads as a single punch: caption present, then overruled. Subtle camera/subject motion continues underneath but the type does the work.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.0027 · eased_energy_share=0.7596 · sparsity=0.0412 · spatial_concentration=0.2281 · mov_texture=11.2519)
- Source: https://www.youtube.com/watch?v=d53Zk28esmU @ 5:15-5:22

### code-list-with-sticker-badge-swoop-in-silsu
- Hero: `code-list-with-sticker-badge-swoop-in-silsu.png` · Strip: `code-list-with-sticker-badge-swoop-in-silsu-strip.png`
- Tags: motion=[slide-in, snap, pop] · archetype=code-reveal · energy=frenetic · mood=playful
- Use when: a code/package list gets punctuated by a punchy headline call-out as the payoff
- Motion: Left column holds a static dependency/code list while the action happens on the right. A pink-and-black diagonal sticker badge whips in from off-frame and snaps to a tilted angle, and the kinetic headline '100s of PACKAGES' slams to full size beside it. Across the strip the badge keeps its skewed sticker tilt rather than settling flat, and a round token element pops in alongside. Punchy single-beat entrance with no slow settle — everything arrives on the same accent.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.8938 · eased_energy_share=0.782 · sparsity=0.1617 · spatial_concentration=0.3374 · mov_texture=12.2934)
- Source: https://www.youtube.com/watch?v=gwTQLZSIlsU @ 0:46-0:49

### red-stamp-stat-slam-over-skull-render-silsu
- Hero: `red-stamp-stat-slam-over-skull-render-silsu.png` · Strip: `red-stamp-stat-slam-over-skull-render-silsu-strip.png`
- Tags: motion=[snap, overshoot, settle] · archetype=stat-hero · energy=punchy · mood=ominous
- Use when: two alarming numbers land back-to-back as the gut-punch of a section
- Motion: A scrolling code/package list sits on the left as red diagonal stamp labels slam in over a desaturated 3D skull render on the right. '373 POISONED' lands first at a hard tilt, then '169 PACKAGES' stamps in below it, each arriving with a quick overshoot before settling into its angled rest pose. The final frames push past the stamps into the bare skull render, reading like a hard cut-away after the numbers hit. Aggressive, percussive stat reveal.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.1978 · eased_energy_share=0.7638 · sparsity=0.215 · spatial_concentration=0.5077 · mov_texture=10.5909)
- Source: https://www.youtube.com/watch?v=gwTQLZSIlsU @ 3:33-3:40

### orange-marker-sweep-on-tweet-thread-silsu
- Hero: `orange-marker-sweep-on-tweet-thread-silsu.png` · Strip: `orange-marker-sweep-on-tweet-thread-silsu-strip.png`
- Tags: motion=[marker-sweep, draw-on] · archetype=quote-card · energy=measured · mood=serious
- Use when: highlighting the damning line inside a screenshotted post or quote
- Motion: A dark-mode X/Twitter thread holds steady while a hand-drawn orange marker stroke sweeps left-to-right across the key lines of the embedded code/quote. Across the strip the highlight extends progressively, tracing under successive lines as if drawn live, with the rest of the card unchanged. Calm, deliberate annotation cadence — the only motion is the marker building over the static evidence.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.7151 · eased_energy_share=0.6306 · sparsity=0.3463 · spatial_concentration=0.4821 · mov_texture=16.3225)
- Source: https://www.youtube.com/watch?v=gwTQLZSIlsU @ 4:03-4:05

### annotation-to-analytics-dashboard-reveal-silsu
- Hero: `annotation-to-analytics-dashboard-reveal-silsu.png` · Strip: `annotation-to-analytics-dashboard-reveal-silsu-strip.png`
- Tags: motion=[wipe, draw-on, slide-in] · archetype=diagram-build · energy=punchy · mood=clinical
- Use when: cutting from a flagged detail to the broader data that backs it up
- Motion: Opens on a screenshot with an orange marker scribble and a circled call-out, then wipes to a light analytics dashboard. The dashboard panels arrive as a grid of purple bar charts, sliding in across the right half of the strip and filling out the layout column by column. The early annotated frames give way cleanly to the data view, reading as a designed transition from a single highlighted point to the supporting charts. Brisk, evidence-stacking cadence.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=8.226 · eased_energy_share=0.98 · sparsity=0.1193 · spatial_concentration=0.3934 · mov_texture=21.0392)
- Source: https://www.youtube.com/watch?v=gwTQLZSIlsU @ 5:46-5:48

### code-report-logo-glitch-bloom-v0b68
- Hero: `code-report-logo-glitch-bloom-v0b68.png` · Strip: `code-report-logo-glitch-bloom-v0b68-strip.png`
- Tags: motion=[glitch, scale-bloom, snap] · archetype=title-card · energy=punchy · mood=playful
- Use when: a recurring segment ident slams on screen to mark the start of a beat
- Motion: On black, a boxed wordmark ("CODE REPORT" stacked inside a hard rectangular frame) snaps in already near full size, then is hit by a white overexposure bloom that washes the whole logo out for a frame or two before settling back to the clean outlined mark. A thin red baseline streak flickers under the box during the blowout. The motion is a hard cut-in plus a glitchy light-flash, no easing glide — it arrives, flares, and resolves in well under a second.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.5195 · eased_energy_share=0.9768 · sparsity=0.5684 · spatial_concentration=0.5883 · mov_texture=8.4954)
- Source: https://www.youtube.com/watch?v=jeA-KBv0b68 @ 0:46-0:52

### opus-version-tag-pop-over-mascot-v0b68
- Hero: `opus-version-tag-pop-over-mascot-v0b68.png` · Strip: `opus-version-tag-pop-over-mascot-v0b68-strip.png`
- Tags: motion=[pop, snap, scale-bloom] · archetype=kinetic-type · energy=frenetic · mood=playful
- Use when: a punchy label or version name pops to punctuate a cut off a UI screen
- Motion: A pale dashboard screenshot is overtaken by a red all-caps tag ("OPUS 4.8...") that pops in oversized on the left, then the frame cuts to black with the same red tag holding beside a small mascot sprite (Sonic) centered. The type doesn't slide — it snaps to size with a slight scale punch and trailing ellipsis, sitting flat and bold against black. Energy is fast and meme-paced, each frame a hard cut rather than a continuous tween.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.3223 · eased_energy_share=0.7148 · sparsity=0.8654 · spatial_concentration=0.8687 · mov_texture=5.266)
- Source: https://www.youtube.com/watch?v=jeA-KBv0b68 @ 4:10-4:14

### highlight-then-orange-swirl-warp-out-v0b68
- Hero: `highlight-then-orange-swirl-warp-out-v0b68.png` · Strip: `highlight-then-orange-swirl-warp-out-v0b68-strip.png`
- Tags: motion=[glitch, morph, parallax-push] · archetype=title-card · energy=frenetic · mood=playful
- Use when: a designed transition tears away the current scene to hand off to the next
- Motion: Opens on a code/doc screen with the word "AUTOSCALES" boxed in a yellow highlight, held for two frames. The frame then explodes into a frenetic swirling warp: black-and-orange radial smears stretch and rotate across the whole canvas, the underlying text fragments and curls along the swirl lines, dissolving any readable layout into a spinning vortex. It reads as a deliberate whip/warp transition out of the scene rather than a content beat — fast, full-frame, no settle.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.3634 · eased_energy_share=0.92 · sparsity=0.4249 · spatial_concentration=0.305 · mov_texture=14.5023)
- Source: https://www.youtube.com/watch?v=jeA-KBv0b68 @ 4:58-5:03

### title-card-flare-bloom-reveal-txxlk
- Hero: `title-card-flare-bloom-reveal-txxlk.png` · Strip: `title-card-flare-bloom-reveal-txxlk-strip.png`
- Tags: motion=[scale-bloom, snap, settle] · archetype=title-card · energy=punchy · mood=playful
- Use when: a segment-break stinger announces the next chunk of the video
- Motion: From near-black the boxed 'CODE REPORT' wordmark snaps in small, then a hard white flare blows out the whole frame at peak before the energy collapses back and the bordered lockup settles crisp and centered. The cadence is a fast pop into an overexposed bloom and a quick decay to the resting plate, with a red underline streak flashing through the blowout. Roughly a third-of-a-second spike, not a slow build.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.3689 · eased_energy_share=0.5272 · sparsity=0.0499 · spatial_concentration=0.3273 · mov_texture=9.6144)
- Source: https://www.youtube.com/watch?v=lkifbWtxxlk @ 1:12-1:16

### logo-over-flames-flicker-hold-txxlk
- Hero: `logo-over-flames-flicker-hold-txxlk.png` · Strip: `logo-over-flames-flicker-hold-txxlk-strip.png`
- Tags: motion=[pop, particle, settle] · archetype=title-card · energy=punchy · mood=playful
- Use when: a mascot or brand mark lands as a punchline with a year stamp
- Motion: The Tux penguin logo holds center-frame with a '2017...' caption to its right while a bed of orange flames and embers licks and flickers along the bottom edge, the fire intensifying frame to frame until it nearly engulfs the lower half. The logo itself barely moves; the motion lives in the looping flame particles and rising heat-glow. It cuts hard to a plain 'What? / How?' framed card, snapping the playful held gag into a question beat.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.6166 · eased_energy_share=0.9926 · sparsity=0.4017 · spatial_concentration=0.6195 · mov_texture=9.9833)
- Source: https://www.youtube.com/watch?v=lkifbWtxxlk @ 2:08-2:12

### interstitial-kinetic-time-skip-card-txxlk
- Hero: `interstitial-kinetic-time-skip-card-txxlk.png` · Strip: `interstitial-kinetic-time-skip-card-txxlk-strip.png`
- Tags: motion=[pop, snap, scale-bloom] · archetype=kinetic-type · energy=frenetic · mood=playful
- Use when: a comedic time-skip or 'meanwhile' cut jumps the narrative forward
- Motion: A 3D meme character delivers captioned lines across most of the strip, then the beat hard-cuts to a green 'GO LOOK' tag and finally a bold wavy 'ONE HOUR LATER...' interstitial that pops on in a chunky outlined SpongeBob-style display face. The kinetic-type cards snap in at full scale rather than easing, landing as punchy comedic punctuation between the talking frames. The cadence is staccato: hold, cut, pop, cut, pop.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.7334 · eased_energy_share=0.892 · sparsity=0.4206 · spatial_concentration=0.5508 · mov_texture=10.2018)
- Source: https://www.youtube.com/watch?v=lkifbWtxxlk @ 3:42-3:48

### code-terminal-into-radial-graph-build-vrajk
- Hero: `code-terminal-into-radial-graph-build-vrajk.png` · Strip: `code-terminal-into-radial-graph-build-vrajk-strip.png`
- Tags: motion=[draw-on, camera-orbit, particle] · archetype=code-reveal · energy=frenetic · mood=tense
- Use when: a technical concept resolves from raw code into a generated visual payoff
- Motion: Opens on a dark terminal/code panel — dense syntax-highlighted lines holding steady on the left while a teal status bar pulses across the top. Across the strip the right half spawns a radial wheel of curved spokes that arc outward and rotate, reading like a graph or particle burst being rendered live from the code. The final frames push in on that circular structure as it tightens into a near-symmetric orbiting ring, the camera drifting closer so the spokes fill frame. Cadence is fast and punctuated: code holds, then the radial form blooms and spins to settle.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=7.4111 · eased_energy_share=0.8913 · sparsity=0.0014 · spatial_concentration=0.3021 · mov_texture=9.9329)
- Source: https://www.youtube.com/watch?v=qPuzWFvRajk @ 0:16-0:20

### logo-collage-into-editorial-title-card-vrajk
- Hero: `logo-collage-into-editorial-title-card-vrajk.png` · Strip: `logo-collage-into-editorial-title-card-vrajk-strip.png`
- Tags: motion=[morph, kinetic-type, mask-reveal] · archetype=title-card · energy=punchy · mood=playful
- Use when: a roster of brands collapses into a single named headline as the segment title lands
- Motion: First two frames cluster several app icons (Telegram paper-plane, Slack hash, a colored AI/O bubble) drifting and orbiting around a central node against black, like a logo collage settling. It then hard-cuts to a designed editorial card: a cream organic blob mask wipes in carrying serif display type, 'The Founding 500.', with a small Telegram glyph tucked in. Across the last frames the headline and its body line snap into place and hold, the blob shape settling under them. Cadence is brisk — float, cut, mask-reveal, settle on the typographic hold.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.8039 · eased_energy_share=0.9718 · sparsity=0.0248 · spatial_concentration=0.337 · mov_texture=19.0224)
- Source: https://www.youtube.com/watch?v=qPuzWFvRajk @ 6:47-6:50

### ai-headline-collage-red-marker-strike-jl3pc
- Hero: `ai-headline-collage-red-marker-strike-jl3pc.png` · Strip: `ai-headline-collage-red-marker-strike-jl3pc-strip.png`
- Tags: motion=[marker-sweep, scale-bloom, collage] · archetype=collage · energy=punchy · mood=tense
- Use when: a loaded term gets named, then negated or called into question as the turn
- Motion: A bold black 'AI' sits stamped over a torn newspaper-clipping collage that shifts behind it frame to frame. Across the strip a red hand-drawn marker stroke sweeps in, first slashing a diagonal through the 'AI', then closing into a full circle-and-line 'no' symbol over it. The clipping backdrop swaps and the red mark accumulates rather than easing, so the cadence is a hard escalating stamp — clean black type first, red negation built on top — landing on the crossed-out symbol.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.4029 · eased_energy_share=1 · sparsity=0.0234 · spatial_concentration=0.3331 · mov_texture=24.7718)
- Source: https://www.youtube.com/watch?v=4MAupwjl3pc @ 3:06-3:09

### course-cards-stagger-in-then-slide-reveal-jl3pc
- Hero: `course-cards-stagger-in-then-slide-reveal-jl3pc.png` · Strip: `course-cards-stagger-in-then-slide-reveal-jl3pc-strip.png`
- Tags: motion=[stagger, slide-in, settle] · archetype=checklist · energy=measured · mood=neutral
- Use when: a curriculum or feature set is enumerated, each item landing one after the next
- Motion: From a blank white field, three rounded course cards ('Thinking in Code', 'Programming with Variables', 'Programming with Python') stagger in left-to-right, each with its purple icon, title and a lesson-count line, settling into a tidy row. The row then slides leftward to push the first cards off and reveal the next set ('Programming with Functions', 'CS Fundamentals', 'How AI Works'), with a small kinetic word ('on') popping over the final frame. Easing is calm — cards settle without overshoot, the slide is a steady horizontal track that dims under a gray overlay at the end.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.5983 · eased_energy_share=0.386 · sparsity=0.1725 · spatial_concentration=0.4302 · mov_texture=16.1236)
- Source: https://www.youtube.com/watch?v=4MAupwjl3pc @ 5:46-5:51

### single-word-swap-center-dark-swt68
- Hero: `single-word-swap-center-dark-swt68.png` · Strip: `single-word-swap-center-dark-swt68-strip.png`
- Tags: motion=[kinetic-type, snap, settle] · archetype=kinetic-type · energy=measured · mood=serious
- Use when: a sentence is delivered word-by-word to land a reframing claim
- Motion: One word holds dead-center on a near-black, faintly star-textured field, then is swapped out for the next ('misconception' to 'is' to 'syntax' to 'was' to 'skill.'). Each word snaps in cleanly and holds with no drift, punctuated rather than crossfaded, so the eye resets to the same center point each beat. The cadence is measured and even, one word per emphasis; the final word carries a period to close the line.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.7174 · eased_energy_share=0.9574 · sparsity=0.3919 · spatial_concentration=0.5401 · mov_texture=0.2745)
- Source: https://www.youtube.com/watch?v=JFlH9isWT68 @ 1:07-1:11

### course-card-scale-pop-icon-swt68
- Hero: `course-card-scale-pop-icon-swt68.png` · Strip: `course-card-scale-pop-icon-swt68-strip.png`
- Tags: motion=[scale-bloom, pop, settle] · archetype=device-mockup · energy=measured · mood=warm
- Use when: a named product or module is introduced as a tidy hero card
- Motion: A rounded course card ('Thinking in Python', 5 Levels, 42 Lessons) with a purple icon scales up from a slightly smaller, lower-contrast state into a crisp, fully-formed card with a drop shadow. The bloom is gentle, no overshoot, settling square in frame. Around it the surrounding UI fades from a flat washed state to legible, reinforcing the card as the focal pop.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.1644 · eased_energy_share=0.9523 · sparsity=0.2549 · spatial_concentration=0.3419 · mov_texture=3.0364)
- Source: https://www.youtube.com/watch?v=JFlH9isWT68 @ 8:37-8:42

### gamified-correct-xp-streak-swt68
- Hero: `gamified-correct-xp-streak-swt68.png` · Strip: `gamified-correct-xp-streak-swt68-strip.png`
- Tags: motion=[pop, slide-in, count-up] · archetype=checklist · energy=punchy · mood=playful
- Use when: a success or reward moment needs a satisfying gamified payoff
- Motion: A green 'Correct! +14 XP' banner pops in over a code panel, the sparkle icon and XP value snapping in together. The strip then cuts to a day-streak row (T / W / Th lightning icons) and a large '0' with a yellow bolt sliding into place. Motion is quick and bouncy, each gamified element popping rather than easing, with the reward feedback front-loaded for punch.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.7124 · eased_energy_share=0.9839 · sparsity=0.0628 · spatial_concentration=0.404 · mov_texture=5.889)
- Source: https://www.youtube.com/watch?v=JFlH9isWT68 @ 8:51-8:55

### caption-to-code-title-crossfade-einri
- Hero: `caption-to-code-title-crossfade-einri.png` · Strip: `caption-to-code-title-crossfade-einri-strip.png`
- Tags: motion=[mask-reveal, settle] · archetype=title-card · energy=measured · mood=neutral
- Use when: a spoken rhetorical question hands off to the named example that answers it
- Motion: A white sentence caption ('But what if you do want elegance?') sits centered in the early frames while a faint code title ghosts behind it. Across the strip the caption dissolves out and a large 'Version 1: Clever' title rises into full opacity, with its monospace code line resolving from blurred to crisp beneath it. The two layers cross-dissolve rather than cut — the caption never fully clears before the title begins, so the handoff reads as one continuous swap that settles on the sharp code title.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.2283 · eased_energy_share=0.9572 · sparsity=0.1217 · spatial_concentration=0.3257 · mov_texture=1.7396)
- Source: https://www.youtube.com/watch?v=NwDUbheiNrI @ 2:15-2:17

### chained-method-code-build-line-reveal-einri
- Hero: `chained-method-code-build-line-reveal-einri.png` · Strip: `chained-method-code-build-line-reveal-einri-strip.png`
- Tags: motion=[mask-reveal, stagger, settle] · archetype=code-reveal · energy=measured · mood=clinical
- Use when: a multi-step transformation is walked through one operation at a time
- Motion: A JavaScript chain ('const names = users .filter... .map... .sort... .slice') assembles top-to-bottom across the strip. Early frames show only the first two or three lines crisp while later lines sit blurred/jittered as placeholders; each subsequent frame resolves one more method onto the chain, the syntax-highlight colors snapping in as each line locks. By the last frames the full block is sharp and static — a measured line-by-line build that settles into a clean, complete code listing.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.3638 · eased_energy_share=0.9353 · sparsity=0.005 · spatial_concentration=0.226 · mov_texture=2.9538)
- Source: https://www.youtube.com/watch?v=NwDUbheiNrI @ 4:17-4:19

### highlight-bar-grow-under-caption-einri
- Hero: `highlight-bar-grow-under-caption-einri.png` · Strip: `highlight-bar-grow-under-caption-einri-strip.png`
- Tags: motion=[wipe, scale-bloom] · archetype=kinetic-type · energy=measured · mood=neutral
- Use when: a single phrase needs a sweeping underline emphasis as it is read aloud
- Motion: A monospace caption 'Too big for one line' holds near the top while a solid teal bar sits beneath it. Left-to-right the bar widens horizontally — from a short block to nearly full-width — wiping outward like a growing highlight, while the caption above simultaneously fades from solid to nearly gone. The bar's growth is steady and linear with no overshoot, settling as the dominant element once the text recedes.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.3205 · eased_energy_share=0.9551 · sparsity=0.2246 · spatial_concentration=0.385 · mov_texture=2.8586)
- Source: https://www.youtube.com/watch?v=NwDUbheiNrI @ 4:32-4:34

### course-card-to-phone-mockup-reveal-einri
- Hero: `course-card-to-phone-mockup-reveal-einri.png` · Strip: `course-card-to-phone-mockup-reveal-einri-strip.png`
- Tags: motion=[slide-in, settle] · archetype=device-mockup · energy=measured · mood=neutral
- Use when: an abstract concept lands on a concrete product or app screen as proof
- Motion: The strip opens on a blank stage, then an 'Algorithmic Thinking' course card with level/lesson counts pops in centered. From there a phone device-mockup slides up from the lower edge into frame, its screen filling with a green pseudocode listing and a scheduling-grid UI. The final frames widen to show the schedule board with placeholder blocks settled in place — a staged reveal that moves from title card to a populated device screen.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.0355 · eased_energy_share=0.9443 · sparsity=0.4495 · spatial_concentration=0.6113 · mov_texture=17.0898)
- Source: https://www.youtube.com/watch?v=NwDUbheiNrI @ 7:26-7:32

### doodle-gag-brain-drop-slap-bpgjq
- Hero: `doodle-gag-brain-drop-slap-bpgjq.png` · Strip: `doodle-gag-brain-drop-slap-bpgjq-strip.png`
- Tags: motion=[pop, snap, kinetic-type] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: a beat lands a comedic 'figuring it out the hard way' punchline
- Motion: A hand-drawn cartoon gag builds left-to-right: it opens on a thinking-face emoji pop-in, then cuts to a doodled stick figure with a scrawled 'hmm…' caption. A '(sigh)' beat resolves into a question-mark-and-brain icon hovering above a second figure's open skull. The cadence then escalates through punctuated caption pops — '*swing*' as an arm winds up, '(slap)' as it strikes — and settles on the brain snapping down into the head with little impact dashes. Each caption snaps in hard with no easing, matching the punchy comic-panel rhythm; no camera move, the frame holds while elements pop in sequence.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.9339 · eased_energy_share=0.9864 · sparsity=0.2296 · spatial_concentration=0.6379 · mov_texture=11.157)
- Source: https://www.youtube.com/watch?v=R8LaiXbpGjQ @ 2:19-2:24

### wordmark-shrinks-into-navbar-xkhza
- Hero: `wordmark-shrinks-into-navbar-xkhza.png` · Strip: `wordmark-shrinks-into-navbar-xkhza-strip.png`
- Tags: motion=[scale-bloom, settle, slide-in] · archetype=title-card · energy=punchy · mood=warm
- Use when: a brand or section title lands then docks itself as the running header
- Motion: The wordmark holds huge and centered on a clean white frame, then scales down and migrates up-left to seat itself as the logo in a top nav bar. As it settles, the nav items (Home, Courses, with small icons) fade and slide in to its right, completing the header. The move reads as a single continuous shrink-and-dock with a soft settle, no overshoot.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.2583 · eased_energy_share=0.9661 · sparsity=0.0084 · spatial_concentration=0.3887 · mov_texture=3.1056)
- Source: https://www.youtube.com/watch?v=hQrOLDxKHzA @ 9:40-9:43

### phone-mockup-slides-up-code-output-xkhza
- Hero: `phone-mockup-slides-up-code-output-xkhza.png` · Strip: `phone-mockup-slides-up-code-output-xkhza-strip.png`
- Tags: motion=[slide-in, settle] · archetype=device-mockup · energy=measured · mood=neutral
- Use when: a result or app screen needs to enter as a tangible device the viewer can read
- Motion: A phone device mockup rises from the bottom edge into frame, screen-first, carrying a dark terminal panel of code and console output. It slides up and settles into a centered resting position, then the framed result panel (return values, a Check button) is revealed as the phone seats. The entrance is a clean vertical glide with a gentle decelerating settle rather than a bounce.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.7217 · eased_energy_share=0.5769 · sparsity=0.0011 · spatial_concentration=0.3645 · mov_texture=14.3216)
- Source: https://www.youtube.com/watch?v=hQrOLDxKHzA @ 10:08-10:24

### glowing-cube-particle-dissipate-xacwy
- Hero: `glowing-cube-particle-dissipate-xacwy.png` · Strip: `glowing-cube-particle-dissipate-xacwy-strip.png`
- Tags: motion=[particle, parallax-drift] · archetype=title-card · energy=frenetic · mood=ominous
- Use when: a scene needs an energetic particle-burst transition or atmospheric backdrop as one moment dissolves into the next
- Motion: A dense field of glowing pale-blue cubes fills the frame in the first panel, then thins progressively left-to-right: the cluster spreads outward and the particle count drops by roughly half each panel until only a scatter of dim points remains in the final frame. Each cube drifts independently with slight blur, reading as a swarm dissipating against pure black rather than a directional sweep. No text or camera move — the motion is the decay of particle density itself.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=6.5649 · eased_energy_share=0.879 · sparsity=0.0486 · spatial_concentration=0.2563 · mov_texture=26.2796)
- Source: https://www.youtube.com/watch?v=3cAsW0xACwY @ 2:54-2:56

### sliding-poster-title-cards-on-starfield-hbszg
- Hero: `sliding-poster-title-cards-on-starfield-hbszg.png` · Strip: `sliding-poster-title-cards-on-starfield-hbszg-strip.png`
- Tags: motion=[slide-in, wipe, snap] · archetype=title-card · energy=punchy · mood=playful
- Use when: a rapid montage punches through a sequence of named chapters or labeled exhibits
- Motion: On a dark starfield, full-height poster cards march through frame one at a time, each swapping the last with a hard horizontal cut rather than a crossfade. The headline reads big and bold at the top (TESTING, then FROM SCRATCH, then CLASSIC SEASON 5) over a body of small mono text and a thumbnail inset, so every card lands the same compositional way. The cadence is a steady one-card-per-beat snap with no overshoot, and the strip ends by cutting to a separate animated cluster of small figures against the same starfield.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.4103 · eased_energy_share=0.9094 · sparsity=0.5264 · spatial_concentration=0.6075 · mov_texture=35.9061)
- Source: https://www.youtube.com/watch?v=BErlQ_HBsZg @ 1:29-1:36

### dispersing-particle-field-thinning-out-hbszg
- Hero: `dispersing-particle-field-thinning-out-hbszg.png` · Strip: `dispersing-particle-field-thinning-out-hbszg-strip.png`
- Tags: motion=[particle, parallax-drift, settle] · archetype=collage · energy=frenetic · mood=tense
- Use when: a dense swarm thins to a few survivors as the narration narrows a field down to the essentials
- Motion: A black frame fills the left third with a dense cloud of small white square particles, then thins dramatically across the strip until only a sparse scatter of a dozen glowing dots remains at the right. The dispersal reads as an outward drift with the cloud emptying top-to-bottom and edges-first, each particle a soft-bloomed pixel rather than a sharp dot. The motion is fast and continuous with no settle frame, leaving a near-empty field by the final panel.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=7.6199 · eased_energy_share=0.8952 · sparsity=0.019 · spatial_concentration=0.2809 · mov_texture=26.3045)
- Source: https://www.youtube.com/watch?v=BErlQ_HBsZg @ 2:55-2:57

### italic-label-over-vfx-to-titlecard-fn7ca
- Hero: `italic-label-over-vfx-to-titlecard-fn7ca.png` · Strip: `italic-label-over-vfx-to-titlecard-fn7ca-strip.png`
- Tags: motion=[kinetic-type, settle, mask-reveal] · archetype=title-card · energy=punchy · mood=triumphant
- Use when: a loaded phrase lands and then resolves into the section's title statement
- Motion: An italic label ('The power of Taste', accent word in orange) holds pinned top-center while a roaring blue-and-orange particle/VFX bloom churns full-frame behind it. Across the strip the energy peaks mid-way then the whole busy background drops away and the frame cuts to a calm near-black field where a clean centered title ('In 2026' with a smaller subline) settles in. The motion is the loud-to-quiet resolve: chaotic full-frame texture giving way to a single composed title card.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.8047 · eased_energy_share=0.8167 · sparsity=0.3912 · spatial_concentration=0.5926 · mov_texture=30.2669)
- Source: https://www.youtube.com/watch?v=Gh_4ozFN7cA @ 0:24-0:30

### particle-field-disperse-thin-out-fn7ca
- Hero: `particle-field-disperse-thin-out-fn7ca.png` · Strip: `particle-field-disperse-thin-out-fn7ca-strip.png`
- Tags: motion=[particle, slide-in, settle] · archetype=collage · energy=frenetic · mood=ominous
- Use when: an idea scatters or thins out — a swarm dissolving toward emptiness
- Motion: A dense field of glowing white cubes fills the upper frame on black, then thins dramatically left-to-right: the first frames are a packed snowfall of particles, and each successive frame sheds more until only a sparse scatter of bright points drifts in the final frame. The dispersal is steady and gravity-light, particles falling and clearing rather than settling into a shape — reads as a swarm draining out of frame.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=6.6167 · eased_energy_share=0.8595 · sparsity=0.0261 · spatial_concentration=0.2494 · mov_texture=26.2371)
- Source: https://www.youtube.com/watch?v=Gh_4ozFN7cA @ 3:57-3:59

### code-editor-annotation-sticker-reveal-gziey
- Hero: `code-editor-annotation-sticker-reveal-gziey.png` · Strip: `code-editor-annotation-sticker-reveal-gziey-strip.png`
- Tags: motion=[marker-sweep, pop, slide-in] · archetype=code-reveal · energy=measured · mood=neutral
- Use when: a point in code or a UI is called out and annotated as the narrator walks through it
- Motion: The strip holds on a dark code-editor / GitHub-style screen across the first frames while a marker-sweep highlight and a small angled sticker-label pop in over the content, drawing the eye to a specific region. The annotation enters with a quick scale-pop rather than a slow fade, then settles in place while the underlying editor stays static. The final frame cuts to a separate dark UI panel, reading as a clean hand-off between two screen states.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.9054 · eased_energy_share=0.8776 · sparsity=0.6268 · spatial_concentration=0.6536 · mov_texture=9.2611)
- Source: https://www.youtube.com/watch?v=NDifawgzIeY @ 3:20-3:29

### hex-cell-mask-wipe-panel-dissolve-gziey
- Hero: `hex-cell-mask-wipe-panel-dissolve-gziey.png` · Strip: `hex-cell-mask-wipe-panel-dissolve-gziey-strip.png`
- Tags: motion=[mask-reveal, wipe, particle] · archetype=title-card · energy=punchy · mood=playful
- Use when: a promo badge or callout panel is swept away to transition into the next scene
- Motion: A dark '40% OFF' panel sits framed at left in the first two frames, then a field of outlined blue hexagonal cells floods in from screen-right as a mask, eating the dark panel away left-to-right across the strip. The hex-cell front advances steadily and uniformly, so the panel doesn't fade but is wiped by the growing cell texture until the frame is almost fully filled with the honeycomb pattern. It reads as a designed mask-wipe transition, fast and even, with no overshoot — the cells simply consume the frame.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.7416 · eased_energy_share=0.9096 · sparsity=0.1646 · spatial_concentration=0.293 · mov_texture=13.6223)
- Source: https://www.youtube.com/watch?v=NDifawgzIeY @ 3:47-3:49

### voronoi-cellular-mask-reveal-transition-6ttw8
- Hero: `voronoi-cellular-mask-reveal-transition-6ttw8.png` · Strip: `voronoi-cellular-mask-reveal-transition-6ttw8-strip.png`
- Tags: motion=[mask-reveal, wipe, particle] · archetype=title-card · energy=punchy · mood=playful
- Use when: a scene cuts to the next on a designed organic transition rather than a hard cut
- Motion: An organic cellular / voronoi bubble pattern eats across the frame left-to-right as a mask. The first frames hold a dark panel with a circled '40% OFF' call-out; the bubble field then floods in from the bottom and right, dissolving the dark panel cell-by-cell until the whole frame is the pale blue voronoi texture by the last frame. The wipe reads as a foamy, irregular-edged reveal rather than a clean line — the leading edge is ragged and clustered, settling once the field fully covers.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.3997 · eased_energy_share=1 · sparsity=0.1887 · spatial_concentration=0.2978 · mov_texture=12.5039)
- Source: https://www.youtube.com/watch?v=VMlRLN6tTw8 @ 3:39-3:41

### spinning-3d-torus-kinetic-type-cards-lmktg
- Hero: `spinning-3d-torus-kinetic-type-cards-lmktg.png` · Strip: `spinning-3d-torus-kinetic-type-cards-lmktg-strip.png`
- Tags: motion=[kinetic-type, camera-orbit, snap] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: a cheeky one-liner punchline lands while a hero 3D object keeps turning behind it
- Motion: The strip opens on a code-editor card typing out 'I want to build a...' with a blinking caret, then hard-cuts into a sequence of full-bleed dark cards each pairing a slowly orbiting glossy 3D torus (a 'bagel') with stacked all-caps kinetic type. The headline swaps card to card in punchy snaps — 'MATTERS', 'IT'S ALL JUST A BAGEL', 'TYPE IS A LIVING THING' — with a small 'Immersive 3D Scrolling' label pinned bottom-left for continuity. The torus rotates continuously and steadily across frames while the type cuts are abrupt; the last frame flips to a light paper-textured card, a designed scene transition rather than a fade.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.3264 · eased_energy_share=0.7555 · sparsity=0.1975 · spatial_concentration=0.4918 · mov_texture=20.059)
- Source: https://www.youtube.com/watch?v=XnhqJKLMkTg @ 3:22-3:24

### white-particle-field-disperse-settle-lmktg
- Hero: `white-particle-field-disperse-settle-lmktg.png` · Strip: `white-particle-field-disperse-settle-lmktg-strip.png`
- Tags: motion=[particle, settle, parallax-drift] · archetype=title-card · energy=frenetic · mood=neutral
- Use when: an abstract idea swarms in then thins out, clearing the frame for what comes next
- Motion: A dense field of soft white cube-like particles fills the black frame in the left frames, then thins out left-to-right as the cloud disperses — early frames are a near-solid blizzard, later frames drop to scattered specks drifting apart at slightly different depths. The motion reads as a swarm settling and clearing rather than a directional sweep, with the density decay carrying the cadence from saturated to sparse across the strip.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=7.0972 · eased_energy_share=0.8645 · sparsity=0.027 · spatial_concentration=0.2487 · mov_texture=26.2859)
- Source: https://www.youtube.com/watch?v=XnhqJKLMkTg @ 3:59-4:01

### dark-course-ui-panel-scroll-reveal-qq90
- Hero: `dark-course-ui-panel-scroll-reveal-qq90.png` · Strip: `dark-course-ui-panel-scroll-reveal-qq90-strip.png`
- Tags: motion=[slide-in, mask-reveal, settle] · archetype=code-reveal · energy=measured · mood=clinical
- Use when: a product or course interface is walked through panel by panel as proof
- Motion: A dark course/documentation UI ('Master TypeScript') holds in the first two frames, then the view scrolls downward so successive content panels and checklist rows wipe up into the viewport in even steps. Each panel arrives without overshoot and settles flat against the dark substrate, keeping a calm reading cadence. The final frame cuts to a different settings-style panel with a small bright accent, closing the walkthrough.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.3109 · eased_energy_share=0.9853 · sparsity=0.3856 · spatial_concentration=0.4338 · mov_texture=7.4412)
- Source: https://www.youtube.com/watch?v=bnHoR5QQ_90 @ 2:43-2:46

### white-cube-particle-field-thin-out-qq90
- Hero: `white-cube-particle-field-thin-out-qq90.png` · Strip: `white-cube-particle-field-thin-out-qq90-strip.png`
- Tags: motion=[particle, parallax-drift, settle] · archetype=title-card · energy=punchy · mood=neutral
- Use when: an idea dissolves or clears away to reset into the next beat
- Motion: A dense field of small white cubes fills the black frame, then thins out frame by frame as the particles drift outward and fall away. The density drops sharply across the first three frames and tapers to a sparse scatter by the end, reading as a fast dissolve rather than a build. The black background stays constant so the motion is entirely the depleting particle cloud.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=6.4587 · eased_energy_share=0.9032 · sparsity=0.0351 · spatial_concentration=0.2499 · mov_texture=25.6268)
- Source: https://www.youtube.com/watch?v=bnHoR5QQ_90 @ 3:19-3:21

### kinetic-phrase-with-drawn-arrow-pointer-o7ihi
- Hero: `kinetic-phrase-with-drawn-arrow-pointer-o7ihi.png` · Strip: `kinetic-phrase-with-drawn-arrow-pointer-o7ihi-strip.png`
- Tags: motion=[draw-on, kinetic-type, pop] · archetype=kinetic-type · energy=measured · mood=warm
- Use when: a phrase lands as the takeaway and a hand-drawn arrow points to the operative word
- Motion: After a B-roll lead-in, a two-line phrase resolves on screen: 'Which is Exactly' sits on top with the last word in a contrasting accent color, and a short curved hand-drawn arrow sweeps in beneath to point at the underlined sub-label 'real learning'. The arrow draws on as a stroke (marker-sweep feel) and the sub-label pops in at its tip; the type holds steady and settles without further movement across the final two frames.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.9565 · eased_energy_share=0.7642 · sparsity=0.4488 · spatial_concentration=0.6398 · mov_texture=18.0398)
- Source: https://www.youtube.com/watch?v=iV9tBio7IHI @ 0:53-0:55

### comparison-table-columns-build-grid-o7ihi
- Hero: `comparison-table-columns-build-grid-o7ihi.png` · Strip: `comparison-table-columns-build-grid-o7ihi-strip.png`
- Tags: motion=[slide-in, stagger, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: two or more options get compared and the comparison grid assembles to make the contrast legible
- Motion: The strip moves from a scattered article/thumbnail screen into a structured comparison: labeled column headers appear first, then a row-and-column grid of compared items fills in left-to-right, staggering across cells until the full table is populated. It resolves into a designed card ('Improve how you architect webapps') so the build reads as the assembly of a comparison matrix that settles into a tidy grid rather than a single pop.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.3222 · eased_energy_share=0.5028 · sparsity=0.1885 · spatial_concentration=0.2959 · mov_texture=25.6499)
- Source: https://www.youtube.com/watch?v=iV9tBio7IHI @ 1:45-1:51

### drifting-particle-field-dissolve-o7ihi
- Hero: `drifting-particle-field-dissolve-o7ihi.png` · Strip: `drifting-particle-field-dissolve-o7ihi-strip.png`
- Tags: motion=[particle, parallax-drift, settle] · archetype=collage · energy=frenetic · mood=tense
- Use when: a dense idea dissolves or scatters as a transition between graphic scenes
- Motion: A full-frame field of soft white particles fills the dark frame, dense at the top and thinning downward. Across the strip the cloud thins and the particles drift and dissolve, the count dropping frame to frame as they fall away and disperse toward the lower frame. The motion is continuous and atmospheric rather than punctuated, reading as a scatter/dissolve transition that empties the frame to black.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=8.3966 · eased_energy_share=0.8965 · sparsity=0.002 · spatial_concentration=0.2632 · mov_texture=26.3814)
- Source: https://www.youtube.com/watch?v=iV9tBio7IHI @ 3:25-3:27

### particle-cell-dissolve-reveals-offer-c68
- Hero: `particle-cell-dissolve-reveals-offer-c68.png` · Strip: `particle-cell-dissolve-reveals-offer-c68-strip.png`
- Tags: motion=[particle, mask-reveal, wipe] · archetype=title-card · energy=punchy · mood=playful
- Use when: a promo callout or offer badge enters as a graphic transition between scenes
- Motion: A field of cell-like rounded particles fills the frame, then erodes from the edges inward to expose a dark card carrying a '40% OFF' callout pinned top-left. Across the strip the particle mass thins steadily left-to-right — dense full-frame, then breaking into a horizontal band, then scattering to a sparse spray that clears to black. The dissolve is even and continuous rather than staggered, reading as a single particle wipe that hands off to the offer text before fully clearing.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.7397 · eased_energy_share=0.9059 · sparsity=0.1635 · spatial_concentration=0.3008 · mov_texture=13.8815)
- Source: https://www.youtube.com/watch?v=u18KeiC_6-8 @ 3:13-3:16

### glitch-distorted-character-portrait-to-label-awe40
- Hero: `glitch-distorted-character-portrait-to-label-awe40.png` · Strip: `glitch-distorted-character-portrait-to-label-awe40-strip.png`
- Tags: motion=[glitch, morph, wipe] · archetype=kinetic-type · energy=punchy · mood=tense
- Use when: a concept gets unsettled or destabilized before its name lands
- Motion: An illustrated portrait (exposed-brain character) sits on a dark grid and is torn through by horizontal scanline glitch and chromatic tearing frame to frame, its expression morphing from alert to alarmed to mouth-agape as the distortion intensifies. The displacement bands snap rather than ease, giving a digital-corruption flicker. On the final frame the character clears and a right-aligned 'Engineering Patterns' label wipes in on clean black, the glitch resolving into a settled title.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.0675 · eased_energy_share=0.7129 · sparsity=0.2875 · spatial_concentration=0.4977 · mov_texture=29.5866)
- Source: https://www.youtube.com/watch?v=yVvW0NaWe40 @ 1:58-2:00

### dense-checklist-panel-with-qr-payoff-awe40
- Hero: `dense-checklist-panel-with-qr-payoff-awe40.png` · Strip: `dense-checklist-panel-with-qr-payoff-awe40-strip.png`
- Tags: motion=[stagger, settle, pop] · archetype=checklist · energy=measured · mood=clinical
- Use when: a long roster of items resolves into a single offer or call-to-action
- Motion: A dark two-column panel holds a long checklist of resource rows with a bold 'Best Structured Resources' headline locked center-right; the rows hold steady across the early frames as a small QR/badge element sits at the lower edge. The frames read as a settled, dense list rather than a row-by-row build, holding its composition. The final frame cuts to a centered '25% off pro plan' promo card with a large QR code popping to foreground, swapping the dense panel for a single focused payoff.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.2742 · eased_energy_share=0.9634 · sparsity=0.5106 · spatial_concentration=0.6024 · mov_texture=11.2918)
- Source: https://www.youtube.com/watch?v=yVvW0NaWe40 @ 2:49-2:52

### white-particle-field-dissolve-clearing-awe40
- Hero: `white-particle-field-dissolve-clearing-awe40.png` · Strip: `white-particle-field-dissolve-clearing-awe40-strip.png`
- Tags: motion=[particle, wipe, settle] · archetype=collage · energy=frenetic · mood=neutral
- Use when: a scene clears or resets in a burst before the next idea
- Motion: The frame opens packed with a dense field of small white cube-like particles on black, then thins rapidly left-to-right as the particles dissipate and fall away. The clearing reads as a directional wipe driven by the particle dissolve, density dropping by roughly half each frame until only scattered specks remain. No easing into a settle so much as a fast, frenetic clear-out that empties the frame for what follows.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=7.1699 · eased_energy_share=0.8115 · sparsity=0.0387 · spatial_concentration=0.2609 · mov_texture=26.2271)
- Source: https://www.youtube.com/watch?v=yVvW0NaWe40 @ 3:34-3:36

### prompt-card-arrow-to-terminal-team-slide-in-optb8
- Hero: `prompt-card-arrow-to-terminal-team-slide-in-optb8.png` · Strip: `prompt-card-arrow-to-terminal-team-slide-in-optb8-strip.png`
- Tags: motion=[slide-in, draw-on, wipe] · archetype=diagram-build · energy=measured · mood=neutral
- Use when: a step in a pipeline hands off to the next, then the scene swaps to introduce the people behind it
- Motion: Opens with a rounded prompt card reading 'add user email verification' on the left, a green hand-drawn arrow curving from it to a terminal-output panel on the right, and a row of labeled illustration icons (folder, coder, browser, person-at-laptop) sitting along the bottom. Across the strip that whole prompt-and-icons assembly fades and dims toward black, and a fresh graphic of three illustrated team figures slides up from the lower right with thin orange connector arrows fanning out beside them. The cadence is a clean two-state wipe: the first diagram settles, holds, then darkens out as the second slides in to replace it rather than overlapping.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.3741 · eased_energy_share=0.9827 · sparsity=0.4915 · spatial_concentration=0.5397 · mov_texture=6.1066)
- Source: https://www.youtube.com/watch?v=3Cz2MzopTB8 @ 1:54-1:56

### annotated-code-windows-mascot-connector-fade-optb8
- Hero: `annotated-code-windows-mascot-connector-fade-optb8.png` · Strip: `annotated-code-windows-mascot-connector-fade-optb8-strip.png`
- Tags: motion=[draw-on, settle, wipe] · archetype=diagram-build · energy=measured · mood=playful
- Use when: an annotated explainer makes its point, then dims out to hand off to the next idea
- Motion: A composed scene: stacked code-editor windows on the left with red hand-drawn annotation arrows pointing into them, a caption 'It is not just completing your code' beneath, a large pixel-art crab mascot floating top-right, and an illustrated person seated at a multi-monitor desk lower-center linked by a yellow zig-zag connector line. Through the first four frames the layout holds nearly static while the mascot and code windows read crisp. Then over the last frames everything ramps to black in a slow fade-out wipe — mascot first, then the code and figure — leaving only the title bar and a faint ghost of the next graphic. The motion is a hold-then-dim transition, not an entrance.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.4111 · eased_energy_share=0.988 · sparsity=0.6575 · spatial_concentration=0.5936 · mov_texture=3.7127)
- Source: https://www.youtube.com/watch?v=3Cz2MzopTB8 @ 2:01-2:04

### mascot-handoff-to-branching-diagram-iwzoa
- Hero: `mascot-handoff-to-branching-diagram-iwzoa.png` · Strip: `mascot-handoff-to-branching-diagram-iwzoa-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=diagram-build · energy=calm · mood=playful
- Use when: a concept title hands off from a friendly mascot into the diagram that explains it
- Motion: A 'Version Control' title sits fixed up top while a monitor showing a branching tree, a small clock, and a yellow robot mascot hold the frame. Across the middle frames the mascot animates in place, turning and then leaning/diving forward in a small arc rather than translating across the frame. The final frame cuts the character and substrate away to a red Git mark whose three arrows fan outward to the right, a clean branch-reveal that lands as the payoff. The cadence is calm and punctuated: long mascot hold, then a quick settle into the branching diagram.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.3426 · eased_energy_share=0.9824 · sparsity=0.5823 · spatial_concentration=0.6695 · mov_texture=11.9779)
- Source: https://www.youtube.com/watch?v=7YbYHjIwZOA @ 2:54-2:57

### logo-fade-scale-settle-on-white-wvkrq
- Hero: `logo-fade-scale-settle-on-white-wvkrq.png` · Strip: `logo-fade-scale-settle-on-white-wvkrq-strip.png`
- Tags: motion=[mask-reveal, scale-bloom, settle] · archetype=title-card · energy=measured · mood=neutral
- Use when: a brand or tool name is introduced as a clean section opener
- Motion: A single logo (mark + wordmark) fades up from near-zero opacity while easing slightly up in scale, centered on a flat white field. Across the strip it brightens to full saturation by the middle frame and holds dead-center, with no overshoot — a calm settle rather than a bounce. In the final frame the logo retreats to a small top-left lockup as a hand-drawn character drops into frame, handing the focus from title to scene.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.7314 · eased_energy_share=0.9802 · sparsity=0 · spatial_concentration=0.2188 · mov_texture=2.1265)
- Source: https://www.youtube.com/watch?v=NLqE-7WVKRQ @ 0:00-0:02

### vs-comparison-build-then-money-slide-in-wvkrq
- Hero: `vs-comparison-build-then-money-slide-in-wvkrq.png` · Strip: `vs-comparison-build-then-money-slide-in-wvkrq-strip.png`
- Tags: motion=[slide-in, wipe, settle] · archetype=split-contrast · energy=measured · mood=neutral
- Use when: two options are weighed against each other, then the takeaway swaps in
- Motion: A two-sided comparison sits assembled — a code/laptop side versus a phone-UI side joined by a central 'VS', with labeled platform rows beneath. Across the first three frames the panel holds while small accents settle, then the whole diagram wipes away to a near-empty white frame. A dollar-bill graphic then slides in from upper-left along a short curved arrow path, easing to rest mid-frame as the punchline of the contrast.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.5574 · eased_energy_share=0.8678 · sparsity=0.5436 · spatial_concentration=0.483 · mov_texture=8.2644)
- Source: https://www.youtube.com/watch?v=NLqE-7WVKRQ @ 0:26-0:28

### logo-desaturate-fade-up-then-recede-a4lq
- Hero: `logo-desaturate-fade-up-then-recede-a4lq.png` · Strip: `logo-desaturate-fade-up-then-recede-a4lq-strip.png`
- Tags: motion=[mask-reveal, settle, scale-bloom] · archetype=title-card · energy=measured · mood=neutral
- Use when: a brand or product is named and you want its logo to introduce itself, then bow out
- Motion: The Google Cloud lockup starts ghosted — grey, low-opacity — and saturates upward to full brand color over the first three frames, the cloud icon's red/yellow/blue/green filling in as it firms up. It holds centered at full strength, then in the final frames fades back toward grey and shrinks slightly toward the center as it recedes. A single clean color-and-opacity reveal with a symmetrical dismiss; no slide, the lockup stays put while only its presence dials in and out.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.3734 · eased_energy_share=0.9697 · sparsity=0.0076 · spatial_concentration=0.1965 · mov_texture=3.0738)
- Source: https://www.youtube.com/watch?v=Sjw8TqA4L_Q @ 1:42-1:44

### brand-card-crossfade-to-logo-pop-a4lq
- Hero: `brand-card-crossfade-to-logo-pop-a4lq.png` · Strip: `brand-card-crossfade-to-logo-pop-a4lq-strip.png`
- Tags: motion=[mask-reveal, pop, settle] · archetype=title-card · energy=measured · mood=playful
- Use when: you hand off from one product to the next and want the outgoing card to dissolve as the incoming one announces itself
- Motion: An 'in simple terms / Vercel' card — wordmark plus Speed and Simplicity ribbons and a small illustrated figure at a laptop — holds for two frames, then dissolves out as a faint grey CLOUDFLARE wordmark and cloud icon cross-fade up beneath it. The Cloudflare mark lingers ghosted for a couple frames, then in the final frame snaps to full strength with its orange cloud icon popping in above the bold wordmark. A two-stage transition: soft dissolve between cards, then a crisp pop to land the incoming brand.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.4863 · eased_energy_share=0.9791 · sparsity=0.0062 · spatial_concentration=0.155 · mov_texture=4.1112)
- Source: https://www.youtube.com/watch?v=Sjw8TqA4L_Q @ 3:22-3:24

### marker-arrow-money-payoff-illustration-3caa
- Hero: `marker-arrow-money-payoff-illustration-3caa.png` · Strip: `marker-arrow-money-payoff-illustration-3caa-strip.png`
- Tags: motion=[draw-on, marker-sweep, slide-in] · archetype=title-card · energy=measured · mood=playful
- Use when: an opening thesis lands and the cost/stakes of the wrong choice are named
- Motion: A hand-drawn stick-figure-at-a-workstation sits left; across the strip a bold orange arrow sweeps right and resolves onto a stack of cash, drawing the cause-to-cost link in one marker stroke. A line of caption text ('Most developers are throwing money away on the wrong hosting') holds beneath while a faint cloud/server illustration settles in the lower right. The cadence is deliberate and punctuated, not snappy: the arrow is the single hero gesture, everything else holds steady around it.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.5086 · eased_energy_share=0.9927 · sparsity=0.6562 · spatial_concentration=0.4439 · mov_texture=10.6035)
- Source: https://www.youtube.com/watch?v=X9-QSQ-3CAA @ 0:02-0:04

### chat-ui-panel-reveal-dashed-arrow-3caa
- Hero: `chat-ui-panel-reveal-dashed-arrow-3caa.png` · Strip: `chat-ui-panel-reveal-dashed-arrow-3caa-strip.png`
- Tags: motion=[slide-in, draw-on, settle] · archetype=device-mockup · energy=measured · mood=neutral
- Use when: a product or tool is introduced and its interface is the proof point
- Motion: A purple app-logo tile sits anchored left while a dashed yellow connector arc draws on from it toward the right, where a clean 'Kodee' chat-assistant window scales/slides up into place. Across the later strip frames the chat panel's content (greeting, the three suggestion rows, the input field) fills in and the whole window settles to full opacity. The dashed arc is the through-line; the UI reveal lands second and stays put.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.3291 · eased_energy_share=0.9749 · sparsity=0.2264 · spatial_concentration=0.4145 · mov_texture=4.2702)
- Source: https://www.youtube.com/watch?v=X9-QSQ-3CAA @ 1:17-1:19

### cloud-provider-logos-stagger-then-link-3caa
- Hero: `cloud-provider-logos-stagger-then-link-3caa.png` · Strip: `cloud-provider-logos-stagger-then-link-3caa-strip.png`
- Tags: motion=[stagger, pop, draw-on] · archetype=collage · energy=measured · mood=neutral
- Use when: a set of competing options or players is enumerated before a comparison
- Motion: Logos enter one at a time left-to-right on a black field: AWS pops in first, then Google Cloud, then a dark Azure 'A', each landing with a small settle before the next arrives, so the row builds as an even stagger. Late in the strip a globe icon pops below and two arching yellow arrows draw on across the top, tying the providers together. The cadence is calm and additive rather than punchy.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.3641 · eased_energy_share=0.9296 · sparsity=0.6354 · spatial_concentration=0.5715 · mov_texture=3.2998)
- Source: https://www.youtube.com/watch?v=X9-QSQ-3CAA @ 3:25-3:29

### wordpress-hosting-label-then-diagram-build-3caa
- Hero: `wordpress-hosting-label-then-diagram-build-3caa.png` · Strip: `wordpress-hosting-label-then-diagram-build-3caa-strip.png`
- Tags: motion=[mask-reveal, slide-in, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a concept is restated then unpacked into its full supporting structure
- Motion: A small 'Wordpress hosting' label and cloud-server icon fade up alone for the first frames, holding the idea bare. Then the frame jumps to a fully built explainer diagram ('Think of it as shared hosting but specifically optimized for WordPress') with a title, two labeled comparison columns, a central WordPress-hosting node, and rows of feature icons all present at once. The motion is a two-stage reveal: quiet single-element setup, then the dense structured panel arrives and settles.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.7191 · eased_energy_share=0.9947 · sparsity=0.0482 · spatial_concentration=0.2817 · mov_texture=2.1755)
- Source: https://www.youtube.com/watch?v=X9-QSQ-3CAA @ 3:38-3:40

### character-pop-into-cloud-diagram-nk6k8
- Hero: `character-pop-into-cloud-diagram-nk6k8.png` · Strip: `character-pop-into-cloud-diagram-nk6k8-strip.png`
- Tags: motion=[pop, draw-on, settle] · archetype=side-cutout · energy=measured · mood=playful
- Use when: an explainer introduces a reaction or consequence beside a standing diagram
- Motion: A cloud-to-brain diagram holds at left, an orange connector line draws from the cloud toward a pink brain icon. In the right half of the strip a cartoon character clutching a green book pops in from the dark on the right, punctuated by short radial emphasis lines around its head. The character scales up to full opacity and settles in place while the left diagram stays static, giving a two-stage reveal: established context, then a surprised reaction beat.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.598 · eased_energy_share=0.9747 · sparsity=0.5027 · spatial_concentration=0.5142 · mov_texture=4.1564)
- Source: https://www.youtube.com/watch?v=g5UiQKnk6k8 @ 2:57-2:59

### isometric-server-grid-kinetic-headline-nk6k8
- Hero: `isometric-server-grid-kinetic-headline-nk6k8.png` · Strip: `isometric-server-grid-kinetic-headline-nk6k8-strip.png`
- Tags: motion=[mask-reveal, slide-in, settle] · archetype=diagram-build · energy=measured · mood=serious
- Use when: a scene cuts from a small motif to a large data-center visual that makes the point land
- Motion: Opens on a small 'infrastructure as code' lightbulb-and-infinity motif on black, then transitions into a wide dark-blue isometric grid of glowing server racks that fills the frame. A two-line headline ('Modern cloud systems simply scale too fast for manual management anymore') resolves in over the grid, the highlighted phrase brightening last. The server field arrives as a full-frame substrate and settles with little drift, so the motion is a scene swap plus a kinetic headline rather than a per-element stagger.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.8273 · eased_energy_share=0.9791 · sparsity=0.5092 · spatial_concentration=0.5562 · mov_texture=7.0088)
- Source: https://www.youtube.com/watch?v=g5UiQKnk6k8 @ 3:28-3:31

### gear-monitor-scale-pop-to-node-graph-nk6k8
- Hero: `gear-monitor-scale-pop-to-node-graph-nk6k8.png` · Strip: `gear-monitor-scale-pop-to-node-graph-nk6k8-strip.png`
- Tags: motion=[scale-bloom, draw-on, stagger] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a concept icon appears and then visibly grows into a more complex one
- Motion: Against black, a monitor-with-gears icon scales up from near-zero with a slight overshoot, blooming into full size across the first few frames. The caption 'As systems' fades up beneath it, color shifting from dim to bright as it settles. In the final frames a teal arrow draws rightward toward a faint network-node graph labelled 'complex', so the build reads as a clean staged sequence: icon pops, label settles, connector draws out to the second element.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.5963 · eased_energy_share=0.9611 · sparsity=0.5248 · spatial_concentration=0.5399 · mov_texture=4.252)
- Source: https://www.youtube.com/watch?v=g5UiQKnk6k8 @ 3:59-4:01

### nginx-staggered-capability-checklist-nk6k8
- Hero: `nginx-staggered-capability-checklist-nk6k8.png` · Strip: `nginx-staggered-capability-checklist-nk6k8-strip.png`
- Tags: motion=[stagger, slide-in, settle] · archetype=checklist · energy=measured · mood=neutral
- Use when: a feature or capability list reveals item by item as each is named
- Motion: An NGINX hexagon logo and a small earth/rocket thumbnail sit fixed at upper-left while a right-hand list builds top-down. 'Traffic balancing', 'reverse proxying', and 'caching' are present early, then 'performance optimization' slides in as a fourth line in the later frames. Each line lands at full opacity with no overshoot, a steady one-line-at-a-time stagger that keeps pace with narration while the logo and thumbnail hold steady.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.6077 · eased_energy_share=0.9142 · sparsity=0.6255 · spatial_concentration=0.7054 · mov_texture=8.7577)
- Source: https://www.youtube.com/watch?v=g5UiQKnk6k8 @ 4:21-4:24

### explainer-wipe-to-logo-scale-bloom-c0lhc
- Hero: `explainer-wipe-to-logo-scale-bloom-c0lhc.png` · Strip: `explainer-wipe-to-logo-scale-bloom-c0lhc-strip.png`
- Tags: motion=[wipe, scale-bloom, pop] · archetype=title-card · energy=calm · mood=neutral
- Use when: a section ends and you cut to a clean title card that introduces the next topic by its logo
- Motion: The strip opens on a busy three-panel explainer layout (a code-editor screenshot, a neural-net diagram, and a curved yellow arrow linking them) held across the first frames. It then wipes to a near-black title scene: the word 'Today' slides in from the left and settles, the red 'K' Keras logo scale-blooms up from small to full size at center with a slight overshoot, and a bold '+' pops in beside it on the final frame. Cadence is calm and staged — hold, hard cut to black, then a one-two-three reveal of word, logo, plus-sign.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.2064 · eased_energy_share=0.9094 · sparsity=0.869 · spatial_concentration=0.7856 · mov_texture=8.3425)
- Source: https://www.youtube.com/watch?v=z0kDvnC0lHc @ 2:22-2:24

### callout-card-build-to-logo-compare-c0lhc
- Hero: `callout-card-build-to-logo-compare-c0lhc.png` · Strip: `callout-card-build-to-logo-compare-c0lhc-strip.png`
- Tags: motion=[mask-reveal, stagger, pop] · archetype=diagram-build · energy=calm · mood=neutral
- Use when: a claim resolves into a designed callout that then sets up a head-to-head comparison
- Motion: Starts on a dark, near-empty frame, then a designed callout card mask-reveals into center: a two-line headline ('It abstracts away the complexity without sacrificing capability') with red and blue emphasis words, a staggered row of small icons, and supporting text blocks beneath. After the card holds, it clears and a comparison row pops in — the XGBoost and LightGBM logos arrive side by side as the payoff. Cadence is measured and calm: card builds, holds for reading, then snaps to the logo face-off.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.4587 · eased_energy_share=0.5402 · sparsity=0.4547 · spatial_concentration=0.4376 · mov_texture=8.0818)
- Source: https://www.youtube.com/watch?v=z0kDvnC0lHc @ 2:35-2:39

### glossy-badge-tumble-settle-amtnq
- Hero: `glossy-badge-tumble-settle-amtnq.png` · Strip: `glossy-badge-tumble-settle-amtnq-strip.png`
- Tags: motion=[overshoot, settle, snap] · archetype=logo · energy=punchy · mood=playful
- Use when: a brand or sponsor mark needs a confident, tactile entrance before its call-to-action
- Motion: A glossy 'Sloth Bytes / The Newsletter' sticker-badge enters hard-tilted (rotated counter-clockwise off-axis) and swings clockwise toward upright across the first three frames, overshooting slightly before settling flat-on to camera. Once level it holds, then hard-cuts to the resolved newsletter signup card with its 'Join For Free' button. The tumble reads like a physical sticker being flipped into place rather than a soft fade — the rotation does the work, scale stays roughly constant.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.6969 · eased_energy_share=0.9315 · sparsity=0.0432 · spatial_concentration=0.3277 · mov_texture=19.8094)
- Source: https://www.youtube.com/watch?v=2ERbh7amtNQ @ 5:02-5:18

### quiz-ui-screens-with-result-card-slideup-amtnq
- Hero: `quiz-ui-screens-with-result-card-slideup-amtnq.png` · Strip: `quiz-ui-screens-with-result-card-slideup-amtnq-strip.png`
- Tags: motion=[slide-in, snap, pop] · archetype=device-mockup · energy=punchy · mood=playful
- Use when: stepping through an app's interaction flow where each screen answers and a verdict lands
- Motion: A clean Duolingo-style exercise UI advances screen by screen: a 'Write this in English' prompt with laid-out word-bank tiles, then a centered zoom into the active question where a green-bordered 'Answer correct' result card slides up and in from the bottom-right corner. It then cuts to a 'Select the correct meaning' multiple-choice screen with three answer rows stacked top-to-bottom. The motion is the slide-up verdict card and the snap between exercise states — tiles and rows themselves sit static once placed.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.3655 · eased_energy_share=0.9601 · sparsity=0.0207 · spatial_concentration=0.3507 · mov_texture=3.1686)
- Source: https://www.youtube.com/watch?v=2ERbh7amtNQ @ 14:30-14:33

### oversized-word-scale-bloom-over-code-2n6sg
- Hero: `oversized-word-scale-bloom-over-code-2n6sg.png` · Strip: `oversized-word-scale-bloom-over-code-2n6sg-strip.png`
- Tags: motion=[scale-bloom, blur-rack, pop] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: a single payoff word slams in to punctuate the point being made
- Motion: A bold white word 'Value' starts small and tucked behind a code-editor panel on the left, then scales up frame by frame until it dominates the full frame by the last panel. As the word blooms larger the code editor behind it racks out of focus and drops away, so the type is the only sharp element left. The growth reads as a few large steps with a slight overshoot before it settles full-bleed; a sloth mascot sits low in frame underneath, static, anchoring the comedic emphasis.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.6901 · eased_energy_share=0.9832 · sparsity=0.0069 · spatial_concentration=0.3026 · mov_texture=9.8495)
- Source: https://www.youtube.com/watch?v=Fuzvl32N6sg @ 5:57-5:59

### deck-title-card-typewriter-code-2n6sg
- Hero: `deck-title-card-typewriter-code-2n6sg.png` · Strip: `deck-title-card-typewriter-code-2n6sg-strip.png`
- Tags: motion=[typewriter, mask-reveal, slide-in] · archetype=title-card · energy=measured · mood=neutral
- Use when: a section title lands and a supporting line types itself in beneath it
- Motion: A clean centered title card reads 'AI. Chat. Experience.' with a 'Generating code...' line beneath where the mid-word characters fill in like a typewriter cursor crawling left to right across the strip. Around it the presentation-tool thumbnail grid stays static while one slide panel enlarges and slides toward center, masking up the title as it settles. Easing is gentle and measured; the type reveal is the only moving element, the deck chrome holds still.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.32 · eased_energy_share=0.9726 · sparsity=0 · spatial_concentration=0.048 · mov_texture=23.4069)
- Source: https://www.youtube.com/watch?v=Fuzvl32N6sg @ 3:17-3:21

### landing-scroll-into-stat-block-countup-ccr2g
- Hero: `landing-scroll-into-stat-block-countup-ccr2g.png` · Strip: `landing-scroll-into-stat-block-countup-ccr2g-strip.png`
- Tags: motion=[parallax-push, count-up, settle] · archetype=stat-hero · energy=punchy · mood=triumphant
- Use when: a product claim hands off to a big number that lands as the payoff
- Motion: The strip opens on a hero landing page ("Cut Code Review Time & Bugs in Half") holding for the first three frames, then pushes/scrolls vertically into a dark product-UI panel, and resolves on a stat band where large figures ("0M" / "4M") read like a count-up settling into place. The motion is a vertical parallax push from marketing copy down into the proof, with the stat block arriving last and holding. Cadence is a single decisive scroll-and-settle rather than a stagger.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.661 · eased_energy_share=0.9481 · sparsity=0.3063 · spatial_concentration=0.5908 · mov_texture=3.1223)
- Source: https://www.youtube.com/watch?v=cgOPg5cCr2g @ 3:56-4:00

### review-comment-cards-with-diff-reveal-ccr2g
- Hero: `review-comment-cards-with-diff-reveal-ccr2g.png` · Strip: `review-comment-cards-with-diff-reveal-ccr2g-strip.png`
- Tags: motion=[slide-in, mask-reveal, settle] · archetype=code-reveal · energy=measured · mood=clinical
- Use when: a tool surfaces inline feedback and the supporting code change is exposed beneath it
- Motion: Across the strip a review thread builds left-to-right: comment cards slide in and stack, then a red/green code diff masks open below them with the changed lines highlighted. The reveal is sequential, panel first then diff, each block sliding up and settling without overshoot. Energy is steady and procedural, matching a UI populating itself rather than a punchy graphic hit.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=8.0597 · eased_energy_share=0.9207 · sparsity=0.002 · spatial_concentration=0.0621 · mov_texture=6.6944)
- Source: https://www.youtube.com/watch?v=cgOPg5cCr2g @ 4:26-4:29

### sticky-node-system-design-diagram-collage-ccr2g
- Hero: `sticky-node-system-design-diagram-collage-ccr2g.png` · Strip: `sticky-node-system-design-diagram-collage-ccr2g-strip.png`
- Tags: motion=[draw-on, slide-in, pop] · archetype=diagram-build · energy=punchy · mood=playful
- Use when: an architecture is sketched out node-by-node alongside the surrounding context
- Motion: The strip shows a whiteboard/excalidraw-style system-design graph of colored sticky nodes with connector lines, sitting in a collage beside a browser window and numbered steps ("Step 2: Create a high level design"). Nodes and links read as drawing/popping on across the frames while side panels slide in around them. It is a busy, multi-element build — diagram on one side, UI context on the other — settling into a full annotated board.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=8.3078 · eased_energy_share=0.7273 · sparsity=0.0001 · spatial_concentration=0.093 · mov_texture=25.5429)
- Source: https://www.youtube.com/watch?v=cgOPg5cCr2g @ 7:50-7:53

### dashboard-stat-cards-with-count-up-chart-saggi
- Hero: `dashboard-stat-cards-with-count-up-chart-saggi.png` · Strip: `dashboard-stat-cards-with-count-up-chart-saggi-strip.png`
- Tags: motion=[count-up, settle, slide-in] · archetype=stat-hero · energy=measured · mood=neutral
- Use when: a dashboard headline number and its chart land as the payoff of a section
- Motion: The first three frames show a dark analytics dashboard assembling: a balance card sits top-left while a big '350' headline number and a bar histogram resolve to the right, the bars filling in and a smooth area curve settling beneath. There is no overshoot; everything eases to rest cleanly, reading like a count-up plus chart-draw landing together. The later frames cut to a populated listing grid, so the usable motion is the dashboard build in the first half.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=6.1539 · eased_energy_share=0.8817 · sparsity=0.0947 · spatial_concentration=0.2433 · mov_texture=16.1755)
- Source: https://www.youtube.com/watch?v=gFWZM0saGGI @ 3:48-3:51

### tech-stack-logo-grid-reveal-saggi
- Hero: `tech-stack-logo-grid-reveal-saggi.png` · Strip: `tech-stack-logo-grid-reveal-saggi-strip.png`
- Tags: motion=[pop, stagger, settle] · archetype=collage · energy=punchy · mood=playful
- Use when: a 'here's the stack' moment names the tools a project is built on
- Motion: A 'TECH STACK' label anchors top-left while a tidy grid of product logos (Convex, Next.js, Clerk, Vercel, shadcn/ui, Tailwind) pops into place in rows, each logo arriving with its wordmark. The reveal is quick and grid-aligned with no overshoot, settling immediately. The remaining frames swap to a money-themed meme overlay, so the designed motion to draw from is the staggered logo-grid reveal.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=7.6563 · eased_energy_share=0.7827 · sparsity=0.0053 · spatial_concentration=0.3081 · mov_texture=26.7472)
- Source: https://www.youtube.com/watch?v=gFWZM0saGGI @ 6:42-6:45

### config-diff-reveal-side-code-panel-saggi
- Hero: `config-diff-reveal-side-code-panel-saggi.png` · Strip: `config-diff-reveal-side-code-panel-saggi-strip.png`
- Tags: motion=[slide-in, mask-reveal, settle] · archetype=code-reveal · energy=measured · mood=clinical
- Use when: a config or code change is walked through line by line as proof
- Motion: A dark editor holds a column of colored config/diff lines on the left; across the strip a second syntax-highlighted code panel slides in from the right and settles flush, so the frame goes from one column to a two-panel code layout. Motion is a clean horizontal slide-in plus a top-down reveal of lines, no overshoot, easing to rest. Reads as a deliberate code walkthrough rather than a raw scroll.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=8.6581 · eased_energy_share=0.9909 · sparsity=0.0004 · spatial_concentration=0.2999 · mov_texture=9.0293)
- Source: https://www.youtube.com/watch?v=gFWZM0saGGI @ 8:32-8:36

### ui-zoom-push-into-nav-target-saggi
- Hero: `ui-zoom-push-into-nav-target-saggi.png` · Strip: `ui-zoom-push-into-nav-target-saggi-strip.png`
- Tags: motion=[parallax-push, scale-bloom, settle] · archetype=device-mockup · energy=punchy · mood=neutral
- Use when: the eye is pushed toward one control or word inside a busy product UI
- Motion: The first frames show a full product onboarding screen with a row of framework logos and an install panel. Across the strip the camera pushes in and scales up on the top nav, magnifying the 'Subscriptions / Configure' breadcrumb with its cursor until 'Configure' fills the right of the frame. It is a smooth zoom/parallax push toward a single target that settles on the word, not a cut — a designed emphasis move on a UI element.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=8.0842 · eased_energy_share=0.9859 · sparsity=0.0002 · spatial_concentration=0.2147 · mov_texture=6.1469)
- Source: https://www.youtube.com/watch?v=gFWZM0saGGI @ 13:59-14:02

### labeled-pixel-grid-diagram-scroll-9zep8
- Hero: `labeled-pixel-grid-diagram-scroll-9zep8.png` · Strip: `labeled-pixel-grid-diagram-scroll-9zep8-strip.png`
- Tags: motion=[slide-in, draw-on, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a spatial/grid concept gets explained cell-by-cell with a callout label
- Motion: A two-row grid of saturated color cells (yellow, blue, magenta, cyan) sits low on a near-black field while a 'Direction pointer (DP)' label with a hand-drawn down-arrow annotates the top-left cell. Across the strip the grid scrolls steadily leftward, new colored columns sliding in from the right at a constant cadence so the palette continuously refreshes; the triangle DP marker stays pinned to one cell as the field moves under it. No overshoot — the motion is an even, conveyor-belt drift that settles on each new column, reading as a deliberate walk through the structure.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=9.4646 · eased_energy_share=0.994 · sparsity=0 · spatial_concentration=0.169 · mov_texture=6.3451)
- Source: https://www.youtube.com/watch?v=lD3Z3d9zEP8 @ 10:38-10:42

### spec-table-panels-slide-zoom-9zep8
- Hero: `spec-table-panels-slide-zoom-9zep8.png` · Strip: `spec-table-panels-slide-zoom-9zep8-strip.png`
- Tags: motion=[slide-in, scale-bloom, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a reference spec or lookup table is introduced and one row is brought into focus
- Motion: Two-column instruction tables (Description / Pseudocode / Op) slide in from the right while a boxed inset of the same table scales up in the center as a focus zoom. The left frames show partial column headers ('de' / 'Op') with the body still filling, then later frames resolve into a fully populated pseudocode table that settles to the right. The cadence is a horizontal slide paired with a centered scale-bloom on the highlighted block, no overshoot — panels glide to rest cleanly.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.5329 · eased_energy_share=0.9811 · sparsity=0 · spatial_concentration=0.3296 · mov_texture=8.3296)
- Source: https://www.youtube.com/watch?v=lD3Z3d9zEP8 @ 5:29-5:33

### matrix-code-rain-to-kinetic-caption-9zep8
- Hero: `matrix-code-rain-to-kinetic-caption-9zep8.png` · Strip: `matrix-code-rain-to-kinetic-caption-9zep8-strip.png`
- Tags: motion=[particle, kinetic-type, wipe] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: a 'this is how computers really work' beat lands with a digital-machine flourish
- Motion: The strip opens on dense green Matrix-style character rain streaming down a black field, columns of glyphs falling at staggered speeds for a full-frame particle wash. It then wipes to spec-table screenshots overlaid with bold kinetic captions — 'ALL computers' snapping in at top, 'USE binary' at bottom — set over game B-roll. The code-rain reads as the designed backdrop and the two-word caption punches on as the payoff.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.8187 · eased_energy_share=0.9635 · sparsity=0.003 · spatial_concentration=0.2375 · mov_texture=37.4486)
- Source: https://www.youtube.com/watch?v=lD3Z3d9zEP8 @ 4:21-4:24

### green-check-checklist-stack-build-pb5hy
- Hero: `green-check-checklist-stack-build-pb5hy.png` · Strip: `green-check-checklist-stack-build-pb5hy-strip.png`
- Tags: motion=[stagger, pop, settle] · archetype=checklist · energy=punchy · mood=playful
- Use when: a short list of guarantees or kept promises lands item by item as reassurance
- Motion: Left of frame holds a bold two-line kinetic lockup (white 'STILL HAVE' over a red 'JOBS'). On the right a green-checkmark checklist stacks in one row at a time: 'Hopes', then 'Dreams', then 'Will' each pop on with its checkmark in a quick top-to-bottom stagger, roughly one item per strip frame. Each row settles flush against the prior one with no overshoot, building a tidy three-item column by the final frame.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.1281 · eased_energy_share=0.9528 · sparsity=0.3681 · spatial_concentration=0.6532 · mov_texture=13.5809)
- Source: https://www.youtube.com/watch?v=32ts_ppb5HY @ 0:13-0:18

### title-lockup-side-cutout-to-spin-icon-pb5hy
- Hero: `title-lockup-side-cutout-to-spin-icon-pb5hy.png` · Strip: `title-lockup-side-cutout-to-spin-icon-pb5hy-strip.png`
- Tags: motion=[settle, snap, morph] · archetype=side-cutout · energy=punchy · mood=playful
- Use when: a labeled concept is introduced as a titled exhibit before the segment opens up
- Motion: A composed title lockup holds: a small icon badge above the word 'VOLUME', a heavy 'BACKUPS' baseline, and a high-contrast vintage cutout of a woman occupying the right third like a collaged side-cutout. Across the strip the full lockup dissolves to black and resolves into a single centered radioactive icon with 'Volume' beside it, snapping from busy composition down to one clean icon-plus-word mark. The move reads as a designed scene wipe collapsing a collage into a minimal lower-third.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.3248 · eased_energy_share=0.9281 · sparsity=0.1602 · spatial_concentration=0.6084 · mov_texture=23.3259)
- Source: https://www.youtube.com/watch?v=32ts_ppb5HY @ 2:07-2:10

### checklist-wipe-to-skill-kinetic-word-pb5hy
- Hero: `checklist-wipe-to-skill-kinetic-word-pb5hy.png` · Strip: `checklist-wipe-to-skill-kinetic-word-pb5hy-strip.png`
- Tags: motion=[wipe, slide-in, snap] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: a list of rules collapses into a single one-word punchline
- Motion: Opens on a green-check rule list ('DON'T GUESS', 'ACT AS A SENIOR DEV', 'DON'T MAKE MISTAKES') stacked left of frame. It wipes to black mid-strip, and a single heavy word 'SKILL' slides in from the right edge, settling pinned to the right side over a dim background image. The motion is a hard scene wipe that trades a three-line checklist for one large kinetic word with no overshoot, just a clean slide-and-stop.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.489 · eased_energy_share=0.9738 · sparsity=0.2598 · spatial_concentration=0.5041 · mov_texture=12.9626)
- Source: https://www.youtube.com/watch?v=32ts_ppb5HY @ 2:34-2:37

### replit-logo-block-assemble-wordmark-mask-pb5hy
- Hero: `replit-logo-block-assemble-wordmark-mask-pb5hy.png` · Strip: `replit-logo-block-assemble-wordmark-mask-pb5hy-strip.png`
- Tags: motion=[mask-reveal, settle, draw-on] · archetype=diagram-build · energy=measured · mood=neutral
- Use when: a brand or product is named and its logo assembles as the reveal
- Motion: Starts on a dark terminal card showing a curl/GraphQL mutation with a hand-drawn pink 'deleted' arrow annotation scribbled over it. The card cuts to a starfield, then the orange Replit mark builds: the offset block glyph holds center while the lowercase 'replit' wordmark wipes up from a blurred grey state into a crisp white lockup beneath the icon. The wordmark sharpens via a mask/blur-rack over the last frames, settling into a clean centered logo with no bounce.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.3469 · eased_energy_share=0.9317 · sparsity=0.3379 · spatial_concentration=0.5314 · mov_texture=9.018)
- Source: https://www.youtube.com/watch?v=32ts_ppb5HY @ 3:43-3:46

### logo-tile-assemble-over-starfield-7stda
- Hero: `logo-tile-assemble-over-starfield-7stda.png` · Strip: `logo-tile-assemble-over-starfield-7stda-strip.png`
- Tags: motion=[pop, settle, wipe] · archetype=title-card · energy=punchy · mood=neutral
- Use when: a brand or product name lands as the reveal after setup
- Motion: A newspaper-style headline card sits centered over a black starfield, then a red ticker of code wipes across its lower band. The strip ends on the four colored squares of a logo popping into place tile-by-tile against the dark field — top tiles first, bottom pair settling a beat behind, so the mark assembles quadrant by quadrant rather than fading as a whole. The starfield holds steady the entire time, keeping the assembling mark as the only moving element.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.4093 · eased_energy_share=0.9714 · sparsity=0.168 · spatial_concentration=0.3366 · mov_texture=7.0998)
- Source: https://www.youtube.com/watch?v=46PcZ47StDA @ 1:58-2:01

### cash-particle-storm-quote-card-7stda
- Hero: `cash-particle-storm-quote-card-7stda.png` · Strip: `cash-particle-storm-quote-card-7stda-strip.png`
- Tags: motion=[particle, parallax-drift, settle] · archetype=quote-card · energy=frenetic · mood=tense
- Use when: a pointed quote or claim lands while a chaotic backdrop churns behind it
- Motion: A small attributed quote card holds pinned to the left while a storm of cash notes and a red-eyed robot illustration churns across the right two-thirds of the frame. The bills drift and tumble frame to frame at varied speeds, with a single large $100 note swinging through the middle of the strip before the swarm reflows. The text card stays fixed and legible throughout, so the motion reads as a restless particle bed under a stable caption.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.8466 · eased_energy_share=0.9416 · sparsity=0.123 · spatial_concentration=0.4871 · mov_texture=25.4982)
- Source: https://www.youtube.com/watch?v=46PcZ47StDA @ 4:44-4:49

### status-checklist-with-progress-bars-7stda
- Hero: `status-checklist-with-progress-bars-7stda.png` · Strip: `status-checklist-with-progress-bars-7stda-strip.png`
- Tags: motion=[stagger, draw-on, settle] · archetype=checklist · energy=measured · mood=neutral
- Use when: a few labeled items resolve to pass/fail states as a payoff
- Motion: Three left-aligned checklist rows — READ THE NEWS, WATCH YOUTUBE CONTENT, UNNECESSARY NOISE — hold with green and red status dots, then the strip wipes to a set of horizontal progress bars that fill left-to-right in a staggered cascade beside an entering side cutout. The first two bars complete green while the third resolves red, so the rows settle into a clear pass/fail readout. The cadence is steady rather than bouncy — bars draw on in sequence and stop, no overshoot.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.6086 · eased_energy_share=0.9791 · sparsity=0.3467 · spatial_concentration=0.6358 · mov_texture=13.1736)
- Source: https://www.youtube.com/watch?v=46PcZ47StDA @ 8:59-9:02

### vintage-card-swaps-to-stacked-title-build-vzmr8
- Hero: `vintage-card-swaps-to-stacked-title-build-vzmr8.png` · Strip: `vintage-card-swaps-to-stacked-title-build-vzmr8-strip.png`
- Tags: motion=[slide-in, wipe, settle] · archetype=title-card · energy=punchy · mood=playful
- Use when: a topic name is introduced as the segment's title
- Motion: Opens on a kitschy vintage 'BRO QUANTUM' card, which collapses to a thin horizontal pill that wipes the old graphic away. From that seam the word 'QUANTUM' snaps in large and magenta, then 'COMPUTING' drops in beneath it on the next frame, stacking into a two-line title. The build is staged line-by-line rather than all at once, and the type settles centered with no overshoot.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.776 · eased_energy_share=0.9812 · sparsity=0.1288 · spatial_concentration=0.4276 · mov_texture=14.2795)
- Source: https://www.youtube.com/watch?v=Bl1smivZMR8 @ 3:25-3:28

### logo-lockup-blur-racks-to-replacement-name-vzmr8
- Hero: `logo-lockup-blur-racks-to-replacement-name-vzmr8.png` · Strip: `logo-lockup-blur-racks-to-replacement-name-vzmr8-strip.png`
- Tags: motion=[blur-rack, mask-reveal, settle] · archetype=title-card · energy=measured · mood=serious
- Use when: one named option is dismissed and a replacement takes its place
- Motion: A 'BetterDB' wordmark over a blue hex icon and a red script 'Redis' logo hold sharp, then progressively rack out of focus across the middle frames until both names go soft and ghosted. As they dissolve, 'Valkey' fades up in the same slot on the final frame, swapping the old lockup for the new name. The whole move is a slow defocus-and-replace rather than a hard cut; the incoming name settles quietly without bounce.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.6433 · eased_energy_share=0.9596 · sparsity=0.3141 · spatial_concentration=0.6161 · mov_texture=10.7214)
- Source: https://www.youtube.com/watch?v=Bl1smivZMR8 @ 4:28-4:30

### pull-quote-card-cuts-to-but-why-kinetic-vzmr8
- Hero: `pull-quote-card-cuts-to-but-why-kinetic-vzmr8.png` · Strip: `pull-quote-card-cuts-to-but-why-kinetic-vzmr8-strip.png`
- Tags: motion=[slide-in, snap, pop] · archetype=quote-card · energy=punchy · mood=tense
- Use when: a quoted statement lands and the beat snaps to a single pointed question
- Motion: A pull-quote with a large decorative open-quotation mark and bolded fragments ('stop publishing', 'too much info') sits beside a small portrait, holding for the first frames. Mid-strip it wipes to black, then 'BUT' appears small at the top and 'WHY?' slams in huge beneath it, snapping into the frame at full scale. The cut from reasoned quote to one-word kinetic payoff is abrupt — no easing on the title, it just pops to its final size and holds.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.3454 · eased_energy_share=0.957 · sparsity=0.446 · spatial_concentration=0.6244 · mov_texture=16.2005)
- Source: https://www.youtube.com/watch?v=Bl1smivZMR8 @ 7:03-7:08

### checklist-overlay-builds-to-q-day-slam-vzmr8
- Hero: `checklist-overlay-builds-to-q-day-slam-vzmr8.png` · Strip: `checklist-overlay-builds-to-q-day-slam-vzmr8-strip.png`
- Tags: motion=[stagger, wipe, snap] · archetype=checklist · energy=punchy · mood=ominous
- Use when: a set of conditions checks off and resolves into a single named threat
- Motion: Three green-ticked items — 'RECORDS', '10-15 YEARS', 'DECRYPT' — sit stacked over a portrait and hold through the left frames. As the strip moves right the checklist clears and a bold all-caps 'Q-DAY' wipes up from the lower right, snapping in over the portrait at full weight. The payoff title arrives in one decisive step rather than building gradually, settling flush without overshoot.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.3357 · eased_energy_share=0.9427 · sparsity=0.4584 · spatial_concentration=0.6488 · mov_texture=23.4555)
- Source: https://www.youtube.com/watch?v=Bl1smivZMR8 @ 8:12-8:15

### relational-keyword-card-pop-with-stacked-reveal-xoffa
- Hero: `relational-keyword-card-pop-with-stacked-reveal-xoffa.png` · Strip: `relational-keyword-card-pop-with-stacked-reveal-xoffa-strip.png`
- Tags: motion=[pop, slide-in, settle] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: a key term snaps on as the punchline, then earns a second word that defines it
- Motion: A retro illustration scene hard-cuts to a black field where a green highlighter-marked word RELATIONAL pops in center-frame, slightly oversized then settling. A beat later DATABASE slides up from below and locks beneath it, completing the stacked label. The cadence is snap-then-resolve: the headline word lands first as emphasis, the qualifier arrives second, no camera move.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.824 · eased_energy_share=0.9557 · sparsity=0.0917 · spatial_concentration=0.395 · mov_texture=15.8108)
- Source: https://www.youtube.com/watch?v=Fy20O1xOffA @ 1:45-1:47

### logo-assembles-from-paper-debris-parallax-xoffa
- Hero: `logo-assembles-from-paper-debris-parallax-xoffa.png` · Strip: `logo-assembles-from-paper-debris-parallax-xoffa-strip.png`
- Tags: motion=[particle, parallax-drift, settle] · archetype=title-card · energy=frenetic · mood=neutral
- Use when: a brand or system name resolves out of churning visual noise into a clean lockup
- Motion: A dense field of shredded paper and document fragments tumbles across the full frame with parallax depth, lighter pieces drifting faster than the deep ones. Through the churn the blue Sun Microsystems hatch-logo and wordmark hold steady at center, the debris thinning frame by frame until the lockup reads clean. The motion is constant turbulence around a fixed anchor rather than a directional entrance.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.2597 · eased_energy_share=0.4636 · sparsity=0.0894 · spatial_concentration=0.4643 · mov_texture=21.905)
- Source: https://www.youtube.com/watch?v=Fy20O1xOffA @ 4:51-4:56

### icon-checklist-blur-wipes-to-typing-keyboard-xoffa
- Hero: `icon-checklist-blur-wipes-to-typing-keyboard-xoffa.png` · Strip: `icon-checklist-blur-wipes-to-typing-keyboard-xoffa-strip.png`
- Tags: motion=[blur-rack, wipe, slide-in] · archetype=checklist · energy=punchy · mood=neutral
- Use when: a list of steps hands off to a concrete demo of doing the work
- Motion: A four-row icon checklist (monitor, understand, deploy, test) holds crisply, then the whole stack smears into horizontal motion-blur and wipes leftward off-frame. As it clears, a 3D keyboard with typing hands rises in from the bottom against a starfield and a colorful folder tab slides in from upper-left. The cadence is hold, blur-out, reveal — one designed transition swapping an abstract list for a literal scene.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.2243 · eased_energy_share=0.9831 · sparsity=0.3303 · spatial_concentration=0.5758 · mov_texture=12.7888)
- Source: https://www.youtube.com/watch?v=Fy20O1xOffA @ 5:54-5:57

### two-tier-architecture-diagram-collapses-to-storage-xoffa
- Hero: `two-tier-architecture-diagram-collapses-to-storage-xoffa.png` · Strip: `two-tier-architecture-diagram-collapses-to-storage-xoffa-strip.png`
- Tags: motion=[wipe, settle, pop] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a layered system diagram drops a layer to focus on the one that matters
- Motion: A stacked diagram shows SQL LAYER above a divider over a highlighted STORAGE ENGINE block. The top SQL LAYER tier and its underline wipe away, leaving STORAGE ENGINE to settle into center as the sole subject. A handwritten green checkmark and the word Reads then pop in beneath it. The cadence is deliberate: remove the upper layer, recenter, annotate.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.5304 · eased_energy_share=0.8524 · sparsity=0.5043 · spatial_concentration=0.5113 · mov_texture=17.4214)
- Source: https://www.youtube.com/watch?v=Fy20O1xOffA @ 7:34-7:36

### marker-scribble-mastery-annotation-quhpy
- Hero: `marker-scribble-mastery-annotation-quhpy.png` · Strip: `marker-scribble-mastery-annotation-quhpy-strip.png`
- Tags: motion=[marker-sweep, draw-on] · archetype=diagram-build · energy=punchy · mood=playful
- Use when: a single word gets hand-circled to flag the one idea that matters
- Motion: Over a muted UI screenshot, a hand-drawn red 'mastery' label scrawls on in marker style with a curving arrow sweeping in to point at it, drawn left-to-right as if written live. The annotation lands fast and stays put for two frames, then the whole frame hard-cuts to a clean research-paper slide. The scribble is the hero motion: rough marker texture, no easing on the stroke itself, just an instant hand-drawn reveal.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=6.6124 · eased_energy_share=0.9579 · sparsity=0.0001 · spatial_concentration=0.0982 · mov_texture=7.5418)
- Source: https://www.youtube.com/watch?v=NJg4_3qUHPY @ 0:30-0:32

### vibe-coding-bold-title-doodle-quhpy
- Hero: `vibe-coding-bold-title-doodle-quhpy.png` · Strip: `vibe-coding-bold-title-doodle-quhpy-strip.png`
- Tags: motion=[pop, snap] · archetype=title-card · energy=frenetic · mood=playful
- Use when: a punchy two-word concept gets named as a section header
- Motion: A full-bleed 'VIBE CODING' title in heavy black + magenta type snaps on with a scribbled doodle accent looping above it, holding hard for the first three frames. Then the title cuts away to a dark chat/code UI that wipes in from the left edge. The title itself doesn't drift — it's a held graphic punch, with the energy carried by the doodle overlay and the abrupt cut to the working UI.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.8695 · eased_energy_share=0.9854 · sparsity=0.0044 · spatial_concentration=0.053 · mov_texture=18.0657)
- Source: https://www.youtube.com/watch?v=NJg4_3qUHPY @ 3:55-3:58

### app-ui-panel-wipe-icon-grid-quhpy
- Hero: `app-ui-panel-wipe-icon-grid-quhpy.png` · Strip: `app-ui-panel-wipe-icon-grid-quhpy-strip.png`
- Tags: motion=[wipe, slide-in] · archetype=device-mockup · energy=measured · mood=neutral
- Use when: a product screen is revealed and then resolves into its component options
- Motion: A 'How can I help you build?' app screen slides in from the right, a busy sidebar panel wiping off-frame to the left to clear the stage for the centered prompt box. The composition holds on the clean prompt UI for several frames, then the final frame reveals a full grid of app/service icons sliding in from the right edge. Steady horizontal wipes, no overshoot — a calm product walkthrough cadence.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=8.5754 · eased_energy_share=0.957 · sparsity=0.0147 · spatial_concentration=0.4404 · mov_texture=5.1639)
- Source: https://www.youtube.com/watch?v=NJg4_3qUHPY @ 5:03-5:06

### main-problem-kinetic-slam-glitch-quhpy
- Hero: `main-problem-kinetic-slam-glitch-quhpy.png` · Strip: `main-problem-kinetic-slam-glitch-quhpy-strip.png`
- Tags: motion=[snap, glitch, scale-bloom] · archetype=kinetic-type · energy=frenetic · mood=tense
- Use when: the section pivots to name the core problem with a hard tonal slam
- Motion: A pull-quote card ('Each feature landed clean...') holds quietly for the first two frames, then the frame hard-flips to a 'Main PROBLEM' title that slams in big — 'Main' in white script, 'PROBLEM' in a magenta highlight bar — over a glitchy red-eyed cyborg face. The title scales up and sharpens across the last frames as the glitch texture intensifies. Sharp snap-in, no settle: it lands at full size and stays aggressive.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.8968 · eased_energy_share=0.9299 · sparsity=0.4076 · spatial_concentration=0.4271 · mov_texture=18.0975)
- Source: https://www.youtube.com/watch?v=NJg4_3qUHPY @ 8:11-8:14

### concept-label-then-illustration-pop-64g8k
- Hero: `concept-label-then-illustration-pop-64g8k.png` · Strip: `concept-label-then-illustration-pop-64g8k-strip.png`
- Tags: motion=[mask-reveal, pop, settle] · archetype=diagram-build · energy=punchy · mood=playful
- Use when: a named concept gets defined and then punctuated by a character or illustration
- Motion: A persistent top-left badge label ('Ringelmann effect') anchors the frame while a quote/definition block mask-reveals line by line below it. Across the back half of the strip the text clears and a cartoon illustration pops in centered, then duplicates into a paired arrangement with a small settle. The cadence is reveal-the-text, then punch-in-the-visual rather than simultaneous.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=7.0103 · eased_energy_share=0.8843 · sparsity=0.0554 · spatial_concentration=0.5158 · mov_texture=13.9675)
- Source: https://www.youtube.com/watch?v=TI-QdJ64g8k @ 2:03-2:05

### meme-title-to-branded-logo-card-build-64g8k
- Hero: `meme-title-to-branded-logo-card-build-64g8k.png` · Strip: `meme-title-to-branded-logo-card-build-64g8k-strip.png`
- Tags: motion=[snap, slide-in, settle] · archetype=title-card · energy=punchy · mood=playful
- Use when: a playful cold-open beat hands off into a branded sponsor or section card
- Motion: Opens on a kinetic meme title ('VIBEZ' with cutout image and floating question marks) that holds for two frames, then hard-cuts to a dark branded card. The logo lockup ('BOOT.DEV') fades up first, then a green-outlined 'FUNDAMENTALS' label slides up and snaps into place beneath it, stacking the wordmark. The build is staged top-then-bottom and settles quickly with no overshoot.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.0923 · eased_energy_share=0.9697 · sparsity=0.1703 · spatial_concentration=0.4953 · mov_texture=11.8453)
- Source: https://www.youtube.com/watch?v=TI-QdJ64g8k @ 4:48-4:51

### staggered-checklist-red-x-marker-strike-64g8k
- Hero: `staggered-checklist-red-x-marker-strike-64g8k.png` · Strip: `staggered-checklist-red-x-marker-strike-64g8k-strip.png`
- Tags: motion=[marker-sweep, stagger, pop] · archetype=checklist · energy=measured · mood=serious
- Use when: a list of negatives is dismissed one by one as the narrator strikes each down
- Motion: A persistent 'Broken Window Theory' badge holds top-left through a brief live-action cut. Then three list items enter and get struck: 'minor bugs', 'sloppy code', then 'bad practices', each preceded by a hand-drawn red X that pops on with a quick marker-sweep. The items stagger top-to-bottom roughly one per frame, so by the last frame all three are crossed out and settled in place.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=1.4579 · eased_energy_share=0.9635 · sparsity=0.605 · spatial_concentration=0.7578 · mov_texture=11.2163)
- Source: https://www.youtube.com/watch?v=TI-QdJ64g8k @ 5:55-5:58

### labeled-icon-stack-then-wipe-out-aufmm
- Hero: `labeled-icon-stack-then-wipe-out-aufmm.png` · Strip: `labeled-icon-stack-then-wipe-out-aufmm-strip.png`
- Tags: motion=[settle, wipe, slide-in] · archetype=diagram-build · energy=measured · mood=neutral
- Use when: a small set of labeled tech/tooling icons assembles to make a point, then clears for the next idea
- Motion: A stack of labeled icons holds in place left-of-center: an orange down-arrow inside big parentheses, a Rust 'R' badge tagged 'based', a JS square tagged 'bundler'. They sit settled for the first two frames, then a dark-red logo swoops in from the right and the whole stack wipes away frame by frame, the JS and arrow dimming out last until the field is nearly black. The exit is a directional clear-out, not a fade — the incoming red shape pushes the old elements off.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.3598 · eased_energy_share=0.938 · sparsity=0.4652 · spatial_concentration=0.63 · mov_texture=9.8769)
- Source: https://www.youtube.com/watch?v=V12-LkaUfmM @ 0:51-0:55

### lightning-logo-typed-label-then-tag-popon-aufmm
- Hero: `lightning-logo-typed-label-then-tag-popon-aufmm.png` · Strip: `lightning-logo-typed-label-then-tag-popon-aufmm-strip.png`
- Tags: motion=[settle, typewriter, pop] · archetype=title-card · energy=punchy · mood=playful
- Use when: a product or feature name lands as a titled logo build, capped by a status/category tag snapping on
- Motion: A blue-to-purple lightning-bolt logo settles dead-center over a dark starfield. Once it stills, a handwritten '2-bundler' label types in to its right one chunk at a time. Then a green 'ARCHITECTURE' pill tag pops on beneath the label with a bright glow bloom, scaling up from a blurred green smear to a crisp outlined tag in the final two frames. Three staged reveals — logo, then name, then tag — each landing cleanly before the next.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.2893 · eased_energy_share=0.9826 · sparsity=0.4776 · spatial_concentration=0.5247 · mov_texture=8.5681)
- Source: https://www.youtube.com/watch?v=V12-LkaUfmM @ 1:53-1:56

### icon-trio-clears-to-chevron-text-wipe-aufmm
- Hero: `icon-trio-clears-to-chevron-text-wipe-aufmm.png` · Strip: `icon-trio-clears-to-chevron-text-wipe-aufmm-strip.png`
- Tags: motion=[settle, wipe, mask-reveal] · archetype=diagram-build · energy=punchy · mood=neutral
- Use when: two or three concept icons resolve into a single labeled takeaway line
- Motion: Three icons hold across the left and center: a yellow double-chevron badge, the lightning-bolt logo, and a red Rust-style mark. Over the next frames the chevron and red mark drop away while the lightning logo drifts up and shrinks toward the corner, emptying the frame. In the last frame a red double-chevron and the line 'two transformation pipelines' wipe in left-to-right at lower-right, the takeaway replacing the icon cluster.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.3964 · eased_energy_share=0.9781 · sparsity=0.2386 · spatial_concentration=0.5756 · mov_texture=8.3016)
- Source: https://www.youtube.com/watch?v=V12-LkaUfmM @ 2:41-2:43

### rainbow-arc-swoosh-10x-headline-hq7pq
- Hero: `rainbow-arc-swoosh-10x-headline-hq7pq.png` · Strip: `rainbow-arc-swoosh-10x-headline-hq7pq-strip.png`
- Tags: motion=[slide-in, wipe, pop] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: a punchy claim or multiplier lands as a hype headline
- Motion: A bold 'PRODUCTIVITY' lockup is already set, then a rainbow arc swooshes in from the left and parks above the '10X', which pops to full weight as the arc lands. The headline holds dead-center for a couple frames, then the whole card hard-cuts to a B-roll subject — no easing on the out, just a snap dissolve. The arc-in is the hero move: a quick left-to-right slide that settles with no overshoot.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.7801 · eased_energy_share=0.9752 · sparsity=0.2947 · spatial_concentration=0.4594 · mov_texture=12.6848)
- Source: https://www.youtube.com/watch?v=W9Hk4khQ7pQ @ 2:00-2:02

### logo-title-card-mask-reveal-from-black-hq7pq
- Hero: `logo-title-card-mask-reveal-from-black-hq7pq.png` · Strip: `logo-title-card-mask-reveal-from-black-hq7pq-strip.png`
- Tags: motion=[mask-reveal, settle, scale-bloom] · archetype=title-card · energy=measured · mood=serious
- Use when: a product or brand name is introduced as the section title
- Motion: A code/terminal panel with a spinner logo holds, then cuts to black and the '▲ zero' wordmark mask-reveals out of the dark, growing slightly as it resolves to crisp center. It settles and holds without overshoot, then a faint earlier-state code line ghosts at the bottom on the way out. The reveal reads as a clean brand bump from black — restrained, no bounce.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.5722 · eased_energy_share=0.9804 · sparsity=0.1598 · spatial_concentration=0.286 · mov_texture=10.9159)
- Source: https://www.youtube.com/watch?v=W9Hk4khQ7pQ @ 2:08-2:11

### scale-bloom-glow-tagline-green-hq7pq
- Hero: `scale-bloom-glow-tagline-green-hq7pq.png` · Strip: `scale-bloom-glow-tagline-green-hq7pq-strip.png`
- Tags: motion=[scale-bloom, blur-rack, glitch] · archetype=kinetic-type · energy=punchy · mood=triumphant
- Use when: a feature tagline punches in as the emphasis beat
- Motion: The '▲ zero / explicit effects' lockup holds sharp, then 'explicit effects' detaches and scale-blooms upward, going soft and glowing cyan-green as it grows past frame. The bloom racks into a blur and the type smears into colored vertical bars on the tail, dissolving rather than settling. It's a deliberate blow-up-and-glow accent, not a clean entrance — the emphasis is in the swell and the green bloom, not a resting state.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.142 · eased_energy_share=0.9755 · sparsity=0.1583 · spatial_concentration=0.4821 · mov_texture=8.7728)
- Source: https://www.youtube.com/watch?v=W9Hk4khQ7pQ @ 2:52-2:55

### orange-particle-burst-over-puzzle-tiles-c3qrq
- Hero: `orange-particle-burst-over-puzzle-tiles-c3qrq.png` · Strip: `orange-particle-burst-over-puzzle-tiles-c3qrq-strip.png`
- Tags: motion=[particle, scale-bloom, pop] · archetype=diagram-build · energy=frenetic · mood=tense
- Use when: a single idea detonates outward as the emphatic payoff of a point
- Motion: Opens on a static label graphic, then a grey pixelated puzzle-tile field fills the frame. From roughly center an orange starburst of spokes pops into being and scale-blooms outward, each radial spike extending further frame to frame like a firework freezing at full reach. The burst holds its radial spread against the noisy tile background rather than settling back, reading as a hard accent hit.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.4072 · eased_energy_share=0.3184 · sparsity=0.0771 · spatial_concentration=0.367 · mov_texture=18.7173)
- Source: https://www.youtube.com/watch?v=caJUD2c3QRQ @ 4:17-4:22

### chrome-skull-cash-debris-orbit-c3qrq
- Hero: `chrome-skull-cash-debris-orbit-c3qrq.png` · Strip: `chrome-skull-cash-debris-orbit-c3qrq-strip.png`
- Tags: motion=[particle, parallax-drift, settle] · archetype=collage · energy=punchy · mood=ominous
- Use when: money or stakes swirl around a menacing central subject
- Motion: A chrome Terminator-style skull sits dead center while dollar bills and metallic debris fan outward and tumble around it in 3D. Across the strip the cash scatters wide early, drifts with parallax depth, then thins and resettles closer as the cloud calms. The skull stays fixed and glints; the motion is entirely the orbiting debris field decelerating into a looser settle.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.9104 · eased_energy_share=0.9421 · sparsity=0.043 · spatial_concentration=0.4479 · mov_texture=22.1975)
- Source: https://www.youtube.com/watch?v=caJUD2c3QRQ @ 4:31-4:36

### gpu-card-ram-slide-in-arrow-drawon-c3qrq
- Hero: `gpu-card-ram-slide-in-arrow-drawon-c3qrq.png` · Strip: `gpu-card-ram-slide-in-arrow-drawon-c3qrq-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=device-mockup · energy=measured · mood=clinical
- Use when: a hardware concept assembles part by part to explain how it fits together
- Motion: Begins on a clean Apple-silicon title card reading UNIFIED MEMORY ARCHITECTURE, then cuts to a dark product stage with a graphics card. A red curved arrow draws on from upper-left, sweeping toward the board, and a stack of memory modules slides in from the right to dock beside the GPU. Each successive frame brings the RAM modules further into place until the labeled assembly settles, a measured exploded-diagram build.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.6347 · eased_energy_share=0.9602 · sparsity=0.3063 · spatial_concentration=0.6073 · mov_texture=7.482)
- Source: https://www.youtube.com/watch?v=caJUD2c3QRQ @ 6:45-6:48

### logo-scatter-into-captioned-api-reveal-ytiou
- Hero: `logo-scatter-into-captioned-api-reveal-ytiou.png` · Strip: `logo-scatter-into-captioned-api-reveal-ytiou-strip.png`
- Tags: motion=[particle, morph, mask-reveal] · archetype=title-card · energy=punchy · mood=tense
- Use when: a familiar brand dissolves to hand off to its replacement
- Motion: A browser-window logo holds, then the Google wordmark detaches and scatters into a loose starfield of particles drifting apart over a black field. As it clears, a top caption 'USE A CLOUD API' snaps in beside a yellow hand emoji and handwritten 'all my sensitive data', and a target logo (OpenAI swirl) fades up at right and resolves to full opacity. The cadence is hold, then a sharp scatter, then a captioned settle — two punctuated events, no easing back.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.1486 · eased_energy_share=0.8939 · sparsity=0.3776 · spatial_concentration=0.6628 · mov_texture=10.1479)
- Source: https://www.youtube.com/watch?v=seKv8ZyTiOU @ 1:35-1:39

### icon-pair-with-handwritten-spec-annotation-ytiou
- Hero: `icon-pair-with-handwritten-spec-annotation-ytiou.png` · Strip: `icon-pair-with-handwritten-spec-annotation-ytiou-strip.png`
- Tags: motion=[draw-on, settle, pop] · archetype=diagram-build · energy=measured · mood=neutral
- Use when: a product detail gets called out with a handwritten spec note
- Motion: A large Chrome ring and a rainbow Gemini star sit paired with a 'Nano' label centered low. The Chrome ring scales down and exits frame-left while the star and label hold steady mid-frame. In the final frames a green check and handwritten '2 to 4B param range' draw on at top-right in a marker-script reveal. The cadence is a calm settle of the icons followed by a single annotation that writes itself on — one eased event, no overshoot.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.375 · eased_energy_share=0.9693 · sparsity=0.201 · spatial_concentration=0.3253 · mov_texture=14.2597)
- Source: https://www.youtube.com/watch?v=seKv8ZyTiOU @ 2:17-2:20

### code-block-dissolve-to-logo-version-badge-ytiou
- Hero: `code-block-dissolve-to-logo-version-badge-ytiou.png` · Strip: `code-block-dissolve-to-logo-version-badge-ytiou-strip.png`
- Tags: motion=[particle, parallax-push, pop] · archetype=code-reveal · energy=frenetic · mood=tense
- Use when: code is shown then swept aside to land a single version number
- Motion: A full editor of syntax-highlighted JS holds, then its glyphs shear and dissolve into vertical streaks of colored particles, collapsing the code away. A Chrome logo parallax-pushes in from depth, growing as it centers. In the last two frames a teal version badge ('13' then '138') pops in beside the logo with a snap. Cadence: dense code hold, a violent particle dissolve, then a pushed-in logo and a hard badge pop — high motion energy, two punctuated events.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=7.4158 · eased_energy_share=0.9641 · sparsity=0.1297 · spatial_concentration=0.2989 · mov_texture=8.8199)
- Source: https://www.youtube.com/watch?v=seKv8ZyTiOU @ 3:38-3:41

### comparison-stat-grid-to-reaction-cut-ytiou
- Hero: `comparison-stat-grid-to-reaction-cut-ytiou.png` · Strip: `comparison-stat-grid-to-reaction-cut-ytiou-strip.png`
- Tags: motion=[slide-in, wipe, settle] · archetype=split-contrast · energy=frenetic · mood=playful
- Use when: two options are compared by the numbers before a punchline cut
- Motion: A two-by-two stat grid (Chrome and Edge icons against 15/24 and 24/30 percentages) sits framed by a purple crosshair divider. The whole panel slides left and a vertical wipe band sweeps across, dissolving the numbers. The wipe hands off to a black-and-white reaction shot of a wide-eyed screaming face that fills frame. Cadence: stat panel holds, a fast horizontal slide plus wipe, then a hard cut to the gag b-roll — punctuated, no settle back into the grid.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.7721 · eased_energy_share=0.9647 · sparsity=0.2207 · spatial_concentration=0.3208 · mov_texture=17.9069)
- Source: https://www.youtube.com/watch?v=seKv8ZyTiOU @ 7:18-7:21

### social-feed-ui-build-over-matrix-efdss
- Hero: `social-feed-ui-build-over-matrix-efdss.png` · Strip: `social-feed-ui-build-over-matrix-efdss-strip.png`
- Tags: motion=[slide-in, stagger, pop] · archetype=diagram-build · energy=frenetic · mood=playful
- Use when: a busy app or social-feed mockup assembles itself to illustrate platform overload
- Motion: Left-to-right the strip builds a fake social-feed UI on a green matrix backdrop: a header card and avatar row appear first, then stacked post cards and engagement pills stagger in beneath, filling the frame columns over several frames. A cartoon meme-face overlay grows in scale from screen-left toward center as the feed fills, layering a comedic foreground over the UI assembly. Motion is dense and punchy rather than eased, with elements popping in roughly in reading order; it settles full-frame with the feed packed and the face dominating the right half.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.7636 · eased_energy_share=0.8223 · sparsity=0.1992 · spatial_concentration=0.2891 · mov_texture=34.8792)
- Source: https://www.youtube.com/watch?v=4tiaWcEfdSs @ 0:19-0:24

### database-types-panel-beside-presenter-efdss
- Hero: `database-types-panel-beside-presenter-efdss.png` · Strip: `database-types-panel-beside-presenter-efdss-strip.png`
- Tags: motion=[slide-in, stagger, settle] · archetype=side-cutout · energy=measured · mood=clinical
- Use when: a presenter walks through a labeled taxonomy or option grid before the architecture pays off
- Motion: A 'Types of Databases' panel holds on the left third while a presenter cutout gestures toward it on the right; across the strip the labeled icon tiles in the panel light up and settle row by row rather than all at once, giving a measured reveal cadence. The presenter's pointing hand tracks left toward the panel, anchoring attention. The final frame swaps to a 'Serverless Architecture' node-tree diagram beside the same presenter, signalling a clean cut from the taxonomy panel to the payoff diagram.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.6652 · eased_energy_share=0.9696 · sparsity=0.5287 · spatial_concentration=0.6691 · mov_texture=9.3548)
- Source: https://www.youtube.com/watch?v=4tiaWcEfdSs @ 2:43-2:46

### qr-reveal-with-start-free-kinetic-cta-efdss
- Hero: `qr-reveal-with-start-free-kinetic-cta-efdss.png` · Strip: `qr-reveal-with-start-free-kinetic-cta-efdss-strip.png`
- Tags: motion=[mask-reveal, kinetic-type, pop] · archetype=code-reveal · energy=punchy · mood=warm
- Use when: an end-card CTA snaps in alongside a scannable code to close the video
- Motion: The strip moves from a settings/form screen-grab to a large QR code that resolves into focus center-frame across the middle frames, as if masking-in from a placeholder. Along the bottom a 'START FOR FREE' kinetic title pops in and recolors word-by-word, with 'FREE' picking up an accent color in the final frames for emphasis. The cadence is a quick punchy snap rather than a slow ease: form, then code, then the CTA lands and holds as the closing call-to-action.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.5509 · eased_energy_share=0.9472 · sparsity=0.1439 · spatial_concentration=0.3034 · mov_texture=8.8753)
- Source: https://www.youtube.com/watch?v=4tiaWcEfdSs @ 5:02-5:06

### logo-lockup-wipe-tagline-reveal-y19so
- Hero: `logo-lockup-wipe-tagline-reveal-y19so.png` · Strip: `logo-lockup-wipe-tagline-reveal-y19so-strip.png`
- Tags: motion=[wipe, mask-reveal, settle] · archetype=title-card · energy=punchy · mood=triumphant
- Use when: a product or brand name is introduced as the reveal a beat builds toward
- Motion: A bold red-and-white 'OPENCLAW' wordmark with a claw glyph wipes in from the left across the first frames, the mask sweeping the letters into place rather than fading them. As the logo settles centered, the 'Open Source AI agent' tagline appears beneath it in clean white type. The last frames drift the locked-up logo toward darker product-shot backgrounds, handing off to the next scene. Crisp, confident pacing with no overshoot — the wipe does all the work.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=11.6533 · eased_energy_share=0.9066 · sparsity=0 · spatial_concentration=0.1975 · mov_texture=19.9976)
- Source: https://www.youtube.com/watch?v=8GjyOQy19so @ 1:47-1:49

### logo-wordmark-blur-streak-reveal-m3xi
- Hero: `logo-wordmark-blur-streak-reveal-m3xi.png` · Strip: `logo-wordmark-blur-streak-reveal-m3xi-strip.png`
- Tags: motion=[blur-rack, slide-in, settle] · archetype=title-card · energy=punchy · mood=playful
- Use when: a product or brand name is introduced as a hard beat
- Motion: The strip opens on a horizontal red motion-blur streak with no legible form, as if the logo is whipping in from the right. By the next frame the claw icon and the OPENCLAW wordmark snap into focus together, the blur racking off in roughly one frame. Once the lockup is sharp, the 'Open Source AI agent' tagline sits in a clean line beneath it and holds steady against a black field for the rest of the strip. No overshoot — it resolves directly from blur to a locked, centered title card.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=12.1616 · eased_energy_share=0.9253 · sparsity=0 · spatial_concentration=0.1755 · mov_texture=20.2513)
- Source: https://www.youtube.com/watch?v=9GpWELm3_XI @ 1:53-1:55

### golden-light-burst-bloom-transition-m3xi
- Hero: `golden-light-burst-bloom-transition-m3xi.png` · Strip: `golden-light-burst-bloom-transition-m3xi-strip.png`
- Tags: motion=[scale-bloom, particle, wipe] · archetype=title-card · energy=frenetic · mood=triumphant
- Use when: a scene change needs a bright, celebratory wipe between graphic beats
- Motion: A burst of golden light rays radiates outward from a low center point, the spokes lengthening and brightening frame to frame like a sunrise flaring up. The bloom intensifies and spreads across each successive frame, the warm core widening until it overexposes the whole frame to near-white in the final panel. It reads as a designed light-burst transition that blows out to white to mask the cut into the next scene — fast, expanding, and one-directional with no settle.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.4282 · eased_energy_share=0.8511 · sparsity=0.0521 · spatial_concentration=0.3997 · mov_texture=5.8391)
- Source: https://www.youtube.com/watch?v=9GpWELm3_XI @ 4:08-4:10

### staggered-label-reveal-over-fade-up-figure-gij8k
- Hero: `staggered-label-reveal-over-fade-up-figure-gij8k.png` · Strip: `staggered-label-reveal-over-fade-up-figure-gij8k-strip.png`
- Tags: motion=[slide-in, stagger, mask-reveal] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: three named items land one after another as a punchline list builds
- Motion: Frame opens on near-black. A white line-art figure fades up from the lower-right shadow, gaining contrast frame to frame until it reads clearly. As it settles, a left-aligned label stack types/slides in top-down — 'RAG APP', then 'CONTENT GENERATOR', then a half-masked 'CLASSIFIER' — each line arriving on its own beat with the lowest line still partially wiped/clipped. The stagger step is roughly one line per frame; the figure holds its pose while the text completes.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.9577 · eased_energy_share=0.951 · sparsity=0.3564 · spatial_concentration=0.5388 · mov_texture=15.1139)
- Source: https://www.youtube.com/watch?v=DtE5KogIj8k @ 2:45-2:47

### frenetic-meme-thumbnail-collage-glitch-gij8k
- Hero: `frenetic-meme-thumbnail-collage-glitch-gij8k.png` · Strip: `frenetic-meme-thumbnail-collage-glitch-gij8k-strip.png`
- Tags: motion=[snap, glitch, pop] · archetype=collage · energy=frenetic · mood=playful
- Use when: an overwhelming flood of options or content is dumped on screen at once
- Motion: A dense grid of browser screenshots and video thumbnails cuts in hard against a dark glitch-textured backdrop, with oversized meme faces ('coolface', a STUPID/crying-laugh head) punched in over the top. The collage reshuffles in rapid hard snaps rather than easing — tiles swap and meme overlays pop frame to frame at high churn. It resolves into a clean right-aligned 'AI ENGINEER' title card on black, the chaos collapsing into a single calm caption.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.8877 · eased_energy_share=0.9355 · sparsity=0.1804 · spatial_concentration=0.2805 · mov_texture=36.0519)
- Source: https://www.youtube.com/watch?v=DtE5KogIj8k @ 0:20-0:28

### perspective-tilted-text-panels-slide-in-icioa
- Hero: `perspective-tilted-text-panels-slide-in-icioa.png` · Strip: `perspective-tilted-text-panels-slide-in-icioa-strip.png`
- Tags: motion=[slide-in, parallax-push, settle] · archetype=code-reveal · energy=punchy · mood=neutral
- Use when: a wall of text or code is introduced as a reference the narrator is about to walk through
- Motion: A blue panel densely packed with left-aligned text lines rides in from the right on a slight 3D perspective tilt, the right edge held back so the plane reads as turned toward camera. Across the first four frames the panel pushes forward and squares up, the perspective easing out of the tilt as it settles flat. The final two frames hard-cut away to a near-black abstract field, so the panel reveal is a single decisive entrance rather than a loop.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.5237 · eased_energy_share=0.9909 · sparsity=0.4787 · spatial_concentration=0.5595 · mov_texture=25.0444)
- Source: https://www.youtube.com/watch?v=aFkImxIcIoA @ 3:27-3:30

### rendered-torus-with-scaling-kinetic-payoff-icioa
- Hero: `rendered-torus-with-scaling-kinetic-payoff-icioa.png` · Strip: `rendered-torus-with-scaling-kinetic-payoff-icioa-strip.png`
- Tags: motion=[scale-bloom, kinetic-type, settle] · archetype=kinetic-type · energy=frenetic · mood=playful
- Use when: a punchline or reductive payoff lands hard over a hero render ('it's all just X')
- Motion: A glossy 3D-rendered torus sits center-frame, slowly turning, while stacked kinetic type builds the punchline beneath it word by word. 'IT'S ALL JUST' holds, then 'A BAGEL' scale-blooms in big and settles, the type swelling on the payoff word before locking. The torus stays the steady anchor while the caption does the timed reveal, ending on the full 'IT'S ALL JUST A BAGEL' lockup.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.6752 · eased_energy_share=0.991 · sparsity=0.2183 · spatial_concentration=0.57 · mov_texture=20.3855)
- Source: https://www.youtube.com/watch?v=aFkImxIcIoA @ 4:20-4:22

### glitch-clipped-name-title-over-board-icioa
- Hero: `glitch-clipped-name-title-over-board-icioa.png` · Strip: `glitch-clipped-name-title-over-board-icioa-strip.png`
- Tags: motion=[glitch, kinetic-type, snap] · archetype=title-card · energy=frenetic · mood=playful
- Use when: a name or section title slams on screen as a hard scene-change stinger
- Motion: A large display name title flickers in with a glitch-clip read — 'KATARINA KNES' resolving, then a frame where only 'RINA KNES' survives the clip before snapping back to full. It sits over a dark, color-saturated board of pink and purple cards and a wireframe 3D pyramid, those graphic elements parallaxing slightly behind the title. The cut is staccato: the title doesn't ease, it snaps between glitch states, then the strip resolves into a clean panel on the right.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.3301 · eased_energy_share=0.9413 · sparsity=0.0573 · spatial_concentration=0.264 · mov_texture=21.1101)
- Source: https://www.youtube.com/watch?v=aFkImxIcIoA @ 5:04-5:16

### two-line-verdict-caption-build-rnxx0
- Hero: `two-line-verdict-caption-build-rnxx0.png` · Strip: `two-line-verdict-caption-build-rnxx0-strip.png`
- Tags: motion=[typewriter, slide-in, settle] · archetype=kinetic-type · energy=measured · mood=playful
- Use when: a two-part verdict lands — the upbeat clause first, then the deadpan turn underneath
- Motion: A bold all-caps line, 'IT'S GOOD AT THE CODE PART', is already set across the upper third in the first frames over a blue code-screen background. A beat later a second line, 'SUCKS AT EVERYTHING ELSE', drops in just beneath it and holds, so the gag reads as a setup-then-punchline reveal rather than both landing at once. Both lines are flat, axis-aligned, and sit locked in place once present — no overshoot or drift, the motion is purely the sequenced appearance of the second clause.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.9173 · eased_energy_share=0.9822 · sparsity=0.5358 · spatial_concentration=0.6256 · mov_texture=29.8893)
- Source: https://www.youtube.com/watch?v=kcTuLLRnxx0 @ 2:20-2:22

### data-table-row-reveal-highlight-payoff-2opwe
- Hero: `data-table-row-reveal-highlight-payoff-2opwe.png` · Strip: `data-table-row-reveal-highlight-payoff-2opwe-strip.png`
- Tags: motion=[mask-reveal, stagger, settle] · archetype=stat-hero · energy=measured · mood=clinical
- Use when: a single row in a data table is the answer the rest of the table exists to frame
- Motion: The full NYT-style table starts greyed near-zero opacity, then rows resolve to full ink in a top-down stagger as the frame scrolls down. One row -- Computer Science -- is anchored and washed in pale yellow as its payoff highlight, holding steady while the surrounding rows settle around it; the Overall Average row arrives last at the bottom. No overshoot, no bounce -- a calm, editorial fade-and-scroll that lets the highlighted row read as the conclusion.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.4277 · eased_energy_share=0.8962 · sparsity=0.2032 · spatial_concentration=0.2587 · mov_texture=3.4585)
- Source: https://www.youtube.com/watch?v=2ahtzV2OPwE @ 0:07-0:10

### pyramid-to-card-flow-whip-blur-transition-2opwe
- Hero: `pyramid-to-card-flow-whip-blur-transition-2opwe.png` · Strip: `pyramid-to-card-flow-whip-blur-transition-2opwe-strip.png`
- Tags: motion=[blur-rack, slide-in, snap] · archetype=diagram-build · energy=punchy · mood=neutral
- Use when: a hard scene change from one diagram into a connected node/flow layout
- Motion: Opens on a tiered pyramid diagram, then a heavy horizontal motion-blur whip smears the whole frame to mask the cut. It resolves into a pair of UI cards that slide in from opposite sides and lock into place, joined by short colored connector arrows snapping between them. The transition does the work -- the blur-rack carries the eye across the cut and the cards settle hard with no float, reading as a deliberate diagram-to-flow handoff.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.1951 · eased_energy_share=0.9127 · sparsity=0.5923 · spatial_concentration=0.6725 · mov_texture=11.5943)
- Source: https://www.youtube.com/watch?v=2ahtzV2OPwE @ 4:25-4:31

### terminal-card-recede-with-lower-third-swap-2nn4g
- Hero: `terminal-card-recede-with-lower-third-swap-2nn4g.png` · Strip: `terminal-card-recede-with-lower-third-swap-2nn4g-strip.png`
- Tags: motion=[settle, scale-bloom, slide-in] · archetype=lower-third · energy=measured · mood=serious
- Use when: a confident claim gets set up, then quietly undercut by the reality that follows
- Motion: A green-on-black terminal card sits centered over a dark dotted grid while a boxed lower-third caption reads the claim ('AI can build a to-do app in 30 seconds. Impressive.'). Across the strip the terminal card shrinks and recedes toward the back as a faint grid of dim cards comes up behind it, and the lower-third hard-cuts to the counter-line ('But here's the reality...'). Motion is calm and continuous — the card eases back rather than snapping, and the caption swaps in place under it.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.7205 · eased_energy_share=0.9772 · sparsity=0.1945 · spatial_concentration=0.3408 · mov_texture=1.8951)
- Source: https://www.youtube.com/watch?v=MjSUCg2NN4g @ 1:30-1:32

### file-tree-mockup-push-zoom-2nn4g
- Hero: `file-tree-mockup-push-zoom-2nn4g.png` · Strip: `file-tree-mockup-push-zoom-2nn4g-strip.png`
- Tags: motion=[scale-bloom, slide-in, parallax-push] · archetype=device-mockup · energy=measured · mood=serious
- Use when: a small UI detail is pulled forward to make a complexity point land
- Motion: A blue-outlined window showing a multi-pane file tree starts small and low on a black stage, then over the strip it scales up and drifts up-and-right into a larger centered position, pushing toward the viewer like a slow dolly-in. The fixed lower-third caption ('So, when you ask it to refactor a feature that touches 47 different files?') holds steady while only the mockup moves, easing to a settle at full size.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.1934 · eased_energy_share=0.9606 · sparsity=0.294 · spatial_concentration=0.5584 · mov_texture=2.0179)
- Source: https://www.youtube.com/watch?v=MjSUCg2NN4g @ 1:40-1:43

### editorial-report-card-rise-fade-in-2nn4g
- Hero: `editorial-report-card-rise-fade-in-2nn4g.png` · Strip: `editorial-report-card-rise-fade-in-2nn4g-strip.png`
- Tags: motion=[slide-in, settle, blur-rack] · archetype=title-card · energy=measured · mood=ominous
- Use when: a sourced headline or finding is introduced as the turning point of the argument
- Motion: Opens on near-black, then a dark report card fades up and rises slightly into frame, its headline 'New Data Suggests Downward Pressure on Code Quality from AI' resolving first and the body paragraphs settling in beneath it. The card softens from blurred to crisp as it lands, easing to a static hold by the last frames — a calm editorial reveal with no overshoot.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.7744 · eased_energy_share=0.8578 · sparsity=0.2576 · spatial_concentration=0.5403 · mov_texture=1.1128)
- Source: https://www.youtube.com/watch?v=MjSUCg2NN4g @ 1:46-1:49

### red-radial-network-pulse-with-counter-2nn4g
- Hero: `red-radial-network-pulse-with-counter-2nn4g.png` · Strip: `red-radial-network-pulse-with-counter-2nn4g-strip.png`
- Tags: motion=[particle, pop, count-up] · archetype=diagram-build · energy=punchy · mood=tense
- Use when: a sprawling, interconnected problem is shown as more tangled than expected
- Motion: A dense radial network of labeled nodes radiates from a glowing red core, with edges fanning out in every direction over black. Across the strip the node cloud shimmers and individual nodes flicker/pop while a red '50' counter sits in the lower-right corner. Motion is a tense, energetic pulse rather than a clean build — the graph breathes and twinkles in place around the hot center.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.7651 · eased_energy_share=0.9508 · sparsity=0.2015 · spatial_concentration=0.3105 · mov_texture=5.6213)
- Source: https://www.youtube.com/watch?v=MjSUCg2NN4g @ 2:24-2:27

### staggered-product-cards-fade-up-d9r3o
- Hero: `staggered-product-cards-fade-up-d9r3o.png` · Strip: `staggered-product-cards-fade-up-d9r3o-strip.png`
- Tags: motion=[stagger, slide-in, settle] · archetype=collage · energy=calm · mood=neutral
- Use when: a small set of named components or tools assembles one at a time to show a stack coming together
- Motion: On a dark dotted-grid field with soft radial color glows, labeled cards enter one at a time left-to-right. Frame one is the empty grid; then a single dim card resolves, then a second and third ('Hostinger VPS', 'OpenClaw', 'Telegram Bot') fade up and brighten in an even stagger, each settling into a row with no overshoot. The cadence is gentle and additive — each new card lands before the next begins, building a three-item lineup by the final frame.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.1924 · eased_energy_share=0.5018 · sparsity=0.8319 · spatial_concentration=0.7689 · mov_texture=3.8531)
- Source: https://www.youtube.com/watch?v=QE712dd9r3o @ 5:58-6:02

### icon-pair-whip-pan-motion-blur-d9r3o
- Hero: `icon-pair-whip-pan-motion-blur-d9r3o.png` · Strip: `icon-pair-whip-pan-motion-blur-d9r3o-strip.png`
- Tags: motion=[slide-in, blur-rack, wipe] · archetype=diagram-build · energy=punchy · mood=neutral
- Use when: two concept icons hold on a settings screen, then the scene whips away to the next idea
- Motion: Two large flat icons — a padlock-and-gear and a notepad-with-pencil — sit composited over a dashboard. They hold steady for the first frames, then the entire frame launches into a hard horizontal motion-blur whip: the icons and UI smear into streaked vertical bands as the camera rips sideways. The blur intensifies across the last two frames into near-total streak, a fast directional wipe-out rather than a settle.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=1.5528 · eased_energy_share=0.9682 · sparsity=0.7223 · spatial_concentration=0.7594 · mov_texture=18.5343)
- Source: https://www.youtube.com/watch?v=QE712dd9r3o @ 2:18-2:22

### floating-callout-pills-around-orb-d9r3o
- Hero: `floating-callout-pills-around-orb-d9r3o.png` · Strip: `floating-callout-pills-around-orb-d9r3o-strip.png`
- Tags: motion=[parallax-drift, pop, settle] · archetype=device-mockup · energy=calm · mood=warm
- Use when: an interface gets annotated with floating labels that name its qualities or features
- Motion: A dark chat-app card holds center-frame with a glowing blue 3D atom/orb pulsing inside it. Three rounded callout pills — 'Personality', 'Default Tone', 'Sense of Self' — sit pinned around the card and drift with a slow parallax as the mock tilts. Across the strip the orb's rings rotate and its glow breathes while the pills hold their anchors, giving a calm annotated-product feel with subtle continuous drift rather than discrete entrances.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.3533 · eased_energy_share=0.9718 · sparsity=0.7945 · spatial_concentration=0.8239 · mov_texture=9.4614)
- Source: https://www.youtube.com/watch?v=QE712dd9r3o @ 3:40-3:43

### kinetic-title-blur-rack-out-d9r3o
- Hero: `kinetic-title-blur-rack-out-d9r3o.png` · Strip: `kinetic-title-blur-rack-out-d9r3o-strip.png`
- Tags: motion=[kinetic-type, blur-rack, scale-bloom] · archetype=title-card · energy=measured · mood=serious
- Use when: a section title lands as a statement then defocuses to hand off to the next scene
- Motion: A bold two-tone title, 'Autonomous AI Workflow' (the 'AI Workflow' in magenta), sits over a dark purple gradient with a small glowing app icon above it. The title holds crisp for the first frames, then racks out of focus: across the final frames the type softens and the whole frame blooms into a defocused purple haze, the words dissolving into glow as the scene blurs away.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.9887 · eased_energy_share=0.9962 · sparsity=0.5406 · spatial_concentration=0.6752 · mov_texture=1.8929)
- Source: https://www.youtube.com/watch?v=QE712dd9r3o @ 6:08-6:10

### infinity-logo-style-morph-cycle-dhmva
- Hero: `infinity-logo-style-morph-cycle-dhmva.png` · Strip: `infinity-logo-style-morph-cycle-dhmva-strip.png`
- Tags: motion=[morph, mask-reveal, scale-bloom] · archetype=title-card · energy=punchy · mood=playful
- Use when: a brand or section title lands and you want it to feel like a stylized logo stinger
- Motion: Across the strip a single infinity-symbol 'INFINITE / To Infinity & Beyond' lockup cycles through distinct visual treatments frame to frame — a hand-drawn outline, a purple neon loop, a gilded foil version, a sunset-gradient fill. Each variant fills the same center slot, so it reads as one mark restyling itself rather than four separate cards. The infinity loop holds its position while the texture and color swap underneath, giving a punchy treatment-morph stinger with no positional travel.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.7868 · eased_energy_share=0.4593 · sparsity=0.1453 · spatial_concentration=0.5704 · mov_texture=15.8737)
- Source: https://www.youtube.com/watch?v=XUQxIRdhmVA @ 0:50-0:53

### card-wall-reflow-to-center-title-dhmva
- Hero: `card-wall-reflow-to-center-title-dhmva.png` · Strip: `card-wall-reflow-to-center-title-dhmva-strip.png`
- Tags: motion=[accordion-reflow, slide-in, settle] · archetype=collage · energy=frenetic · mood=neutral
- Use when: a dense field of evidence collapses into the single headline it all proves
- Motion: The strip opens on a packed grid of dark blue info cards tiling the full frame, then the wall recedes and resolves into a single centered statement card ('JavaScript developers in the US over $100,000 per year'). Motion runs from many small elements to one focal panel — the surrounding tiles thin out and a hero card settles dead center with its supporting chips lined up beneath. It reads as a busy-to-focused reflow: maximal density up front, one payoff line on the settle.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.7047 · eased_energy_share=0.9684 · sparsity=0.0046 · spatial_concentration=0.2924 · mov_texture=9.0573)
- Source: https://www.youtube.com/watch?v=XUQxIRdhmVA @ 3:31-3:35

### lvl-zero-to-hundred-badge-pop-dhmva
- Hero: `lvl-zero-to-hundred-badge-pop-dhmva.png` · Strip: `lvl-zero-to-hundred-badge-pop-dhmva-strip.png`
- Tags: motion=[snap, pop, scale-bloom] · archetype=stat-hero · energy=punchy · mood=triumphant
- Use when: a before/after number jumps to its max as the triumphant payoff
- Motion: Oversized white type carries the beat: 'LVL 0' fills the frame, then snaps to 'LVL 100' with a gilded laurel/sun badge popping in beneath the number on the later frames. The value change is a hard cut between states rather than a count-up, and the badge scales in to seal the level-100 payoff. Big centered numerals on dark, minimal travel — the punch comes from the snap and the badge bloom.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.1045 · eased_energy_share=0.8032 · sparsity=0.2024 · spatial_concentration=0.5132 · mov_texture=7.8771)
- Source: https://www.youtube.com/watch?v=XUQxIRdhmVA @ 3:36-3:51

### read-watch-for-free-stacked-type-build-dhmva
- Hero: `read-watch-for-free-stacked-type-build-dhmva.png` · Strip: `read-watch-for-free-stacked-type-build-dhmva-strip.png`
- Tags: motion=[kinetic-type, snap, mask-reveal] · archetype=kinetic-type · energy=frenetic · mood=playful
- Use when: a short call-to-action phrase hits hard line by line before the content plays
- Motion: A three-line lockup stacks in on a blurred dark backdrop — 'READ & WATCH' top, 'for' mid, a huge 'FREE' filling the lower frame — with the 'FREE' word snapping up to full size across the early frames. Once the type is set, a play-button triangle appears over a video still, handing off from the title to the content. The cadence is bold display type slamming into place line-by-line, then a clean cut to the player.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=8.1671 · eased_energy_share=0.9319 · sparsity=0 · spatial_concentration=0.1236 · mov_texture=9.9687)
- Source: https://www.youtube.com/watch?v=XUQxIRdhmVA @ 4:18-4:28

### concentric-ring-ripple-expand-50kxu
- Hero: `concentric-ring-ripple-expand-50kxu.png` · Strip: `concentric-ring-ripple-expand-50kxu-strip.png`
- Tags: motion=[scale-bloom, draw-on, settle] · archetype=diagram-build · energy=punchy · mood=tense
- Use when: a single idea radiates outward and a focal point lands at center
- Motion: On black, a tight nest of red concentric rings is drawn from a glowing center, then the rings scale outward and thin as they grow — the cluster blooms from a small dense knot to one large dominant ellipse that fills most of the frame. The growth eases out and settles, leaving a single bright ring and a warm dot pinned at center. Reads as a radar/shockwave pulse expanding from a point.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=2.2351 · eased_energy_share=0.8608 · sparsity=0.6221 · spatial_concentration=0.722 · mov_texture=7.5341)
- Source: https://www.youtube.com/watch?v=_TVzBm50KxU @ 1:03-1:05

### article-card-slide-scale-on-grid-50kxu
- Hero: `article-card-slide-scale-on-grid-50kxu.png` · Strip: `article-card-slide-scale-on-grid-50kxu-strip.png`
- Tags: motion=[slide-in, parallax-push, settle] · archetype=collage · energy=measured · mood=serious
- Use when: a headline or source card is presented as evidence for a claim
- Motion: Against a blueprint grid, a magazine-style article card ('Entry-Level Tech Jobs Down 67%') enters small and low-right, then slides up-left and scales up frame by frame as the camera pushes in. Each step reveals more of the card — title first, then byline, then the POSTINGS body block and body copy. The push is steady and even, no overshoot, settling once the headline and body fill the upper half.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.0502 · eased_energy_share=0.7948 · sparsity=0.486 · spatial_concentration=0.5035 · mov_texture=9.9338)
- Source: https://www.youtube.com/watch?v=_TVzBm50KxU @ 1:15-1:22

### job-posting-icon-pop-on-grid-50kxu
- Hero: `job-posting-icon-pop-on-grid-50kxu.png` · Strip: `job-posting-icon-pop-on-grid-50kxu-strip.png`
- Tags: motion=[pop, scale-bloom, settle] · archetype=device-mockup · energy=measured · mood=neutral
- Use when: a single concept icon punches in to label the topic of a beat
- Motion: On a dark grid, a 'JOB' posting/newspaper icon with a briefcase pops in at center-left and holds, growing slightly larger across the middle frames before settling. There is little lateral travel — the motion is a centered scale-in pop. The final frame hard-cuts to unrelated live-action B-roll, so the designed motion is only the icon entrance, not the cut.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.2441 · eased_energy_share=0.7728 · sparsity=0.3112 · spatial_concentration=0.5407 · mov_texture=13.8552)
- Source: https://www.youtube.com/watch?v=_TVzBm50KxU @ 1:27-1:34

### playbook-title-reveal-dissolve-50kxu
- Hero: `playbook-title-reveal-dissolve-50kxu.png` · Strip: `playbook-title-reveal-dissolve-50kxu-strip.png`
- Tags: motion=[mask-reveal, blur-rack, settle] · archetype=title-card · energy=measured · mood=serious
- Use when: a section or chapter title lands then dissolves into the next scene
- Motion: On a deep navy vignette, a square logo mark and the wordmark 'THE PLAYBOOK' resolve into focus, hold crisply for a beat, then rack out of focus and fade — the lettering softens and darkens frame by frame until it dissolves entirely. The final frame transitions to a red 'STOP' graphic, making this a title card handing off to the next scene via a soft blur-out.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.6499 · eased_energy_share=0.9208 · sparsity=0.7601 · spatial_concentration=0.7883 · mov_texture=4.3414)
- Source: https://www.youtube.com/watch?v=_TVzBm50KxU @ 3:32-3:35

### ui-card-assembles-on-grid-canvas-heplm
- Hero: `ui-card-assembles-on-grid-canvas-heplm.png` · Strip: `ui-card-assembles-on-grid-canvas-heplm-strip.png`
- Tags: motion=[slide-in, blur-rack, settle] · archetype=device-mockup · energy=measured · mood=neutral
- Use when: a product UI is being introduced and the interface assembles itself before the viewer's eyes
- Motion: On a dark blueprint-grid canvas, a single soft-focus placeholder row drifts up from the bottom edge first. Successive frames stack more blurred content blocks left-of-center, each racking from blur toward focus as it lands. The final frame resolves into a crisp 'Schedule Your Appointment' CalendarSync card pinned to the right — header, date-picker grid, and form column all sharp. The cadence is unhurried, one block per beat, settling without overshoot.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.1422 · eased_energy_share=0.8584 · sparsity=0.1594 · spatial_concentration=0.4041 · mov_texture=13.4229)
- Source: https://www.youtube.com/watch?v=b1auSFhePLM @ 2:32-2:38

### code-block-parallax-push-into-grid-heplm
- Hero: `code-block-parallax-push-into-grid-heplm.png` · Strip: `code-block-parallax-push-into-grid-heplm-strip.png`
- Tags: motion=[parallax-push, scale-bloom, blur-rack] · archetype=code-reveal · energy=measured · mood=clinical
- Use when: a code snippet is shown and then pushed back to make room for the next idea
- Motion: A syntax-highlighted code panel sits centered on a dark grid in the first frames, fully legible. Across the strip it scales down and pushes away from camera into the grid depth, the panel shrinking toward the upper-mid frame while a second faint block trails behind it. The text racks into blur as it recedes, and the final frame washes almost fully white as the scene transitions out. A steady parallax-into-depth move, not a hard cut.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.2348 · eased_energy_share=0.9781 · sparsity=0.1651 · spatial_concentration=0.4548 · mov_texture=12.6022)
- Source: https://www.youtube.com/watch?v=b1auSFhePLM @ 4:55-4:58

### rotating-stamp-badges-radial-dial-title-heplm
- Hero: `rotating-stamp-badges-radial-dial-title-heplm.png` · Strip: `rotating-stamp-badges-radial-dial-title-heplm-strip.png`
- Tags: motion=[snap, kinetic-type, draw-on] · archetype=title-card · energy=punchy · mood=playful
- Use when: a punchline word lands as the payoff with a stamped-on emphasis
- Motion: Against black, red 'UNTOUCHABLE' stamp badges snap in at jaunty angles and jitter frame-to-frame while a dashed amber radial dial draws on and rotates clockwise at frame-right. The badges shuffle position and rotation each frame like rubber stamps being slapped down, with the dial sweeping in parallel. The final frame resolves to a bold yellow 3D-extruded 'UNTOUCHABLE' wordmark snapping center-stage. Fast and percussive.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.2616 · eased_energy_share=0.9461 · sparsity=0.0898 · spatial_concentration=0.3766 · mov_texture=14.787)
- Source: https://www.youtube.com/watch?v=b1auSFhePLM @ 5:38-5:41

### error-callout-over-code-lines-reveal-ftlro
- Hero: `error-callout-over-code-lines-reveal-ftlro.png` · Strip: `error-callout-over-code-lines-reveal-ftlro-strip.png`
- Tags: motion=[mask-reveal, slide-in, settle] · archetype=code-reveal · energy=punchy · mood=tense
- Use when: a bug or error gets called out the instant it surfaces in code
- Motion: An editor pane with numbered code lines (41/42/43, an `if (in...` continuation) holds at left while a white 'Error on line 42' callout card masks in across the top, settling without overshoot. Across the strip the callout firms up from a soft blur to a crisp label as the code lines underneath sharpen in sync. A small face cutout sits pinned at the right edge, static, so the eye stays on the error landing over the code.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.944 · eased_energy_share=0.9616 · sparsity=0.028 · spatial_concentration=0.4379 · mov_texture=14.1891)
- Source: https://www.youtube.com/watch?v=pUOwlDFTlro @ 0:00-0:02

### device-card-hold-caption-swap-emphasis-ftlro
- Hero: `device-card-hold-caption-swap-emphasis-ftlro.png` · Strip: `device-card-hold-caption-swap-emphasis-ftlro-strip.png`
- Tags: motion=[kinetic-type, mask-reveal, settle] · archetype=device-mockup · energy=measured · mood=warm
- Use when: a punchline caption swaps to reland the claim under a held product UI
- Motion: A dark weather-app mockup ('WEATHER.JS', 'London', a big 11 degrees readout) holds dead still and centered through the whole beat while the caption beneath does the work: 'I didn't copy-paste that from a tutorial.' fades down and is replaced by 'I built it from scratch.', with the words 'from scratch' wiping into bright cyan as the emphasis lands. The swap is a soft cross-dissolve, no slide, so the held card anchors the frame and only the line below changes.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.7139 · eased_energy_share=0.972 · sparsity=0.42 · spatial_concentration=0.5295 · mov_texture=1.4114)
- Source: https://www.youtube.com/watch?v=pUOwlDFTlro @ 0:56-1:01

### net-io-load-streaming-pill-dots-e0nnw
- Hero: `net-io-load-streaming-pill-dots-e0nnw.png` · Strip: `net-io-load-streaming-pill-dots-e0nnw-strip.png`
- Tags: motion=[slide-in, stagger, draw-on] · archetype=diagram-build · energy=frenetic · mood=clinical
- Use when: data or requests flowing through a pipeline as a system processes load
- Motion: A boxed 'NET_IO :: LOAD' label sits fixed top-center while a magenta cluster of stacked database/table glyphs holds at lower-left. The hero motion is a dark pill-shaped channel that fills left-to-right: a magenta head-token leads and cyan dots stream in behind it one at a time, adding roughly one dot per frame in an even stagger across the strip. As the dots accumulate the right-hand status label swaps from SQL::QUERY_PLAN to HTTP/2::STREAM, syncing the type change to the packet flow. Cadence is fast and mechanical with no overshoot — a steady conveyor, not a bounce.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.1251 · eased_energy_share=0.9257 · sparsity=0.107 · spatial_concentration=0.3447 · mov_texture=1.7453)
- Source: https://www.youtube.com/watch?v=wTT8QaE0nnw @ 2:22-2:25

### word-by-word-pop-grid-then-cutout-e0nnw
- Hero: `word-by-word-pop-grid-then-cutout-e0nnw.png` · Strip: `word-by-word-pop-grid-then-cutout-e0nnw-strip.png`
- Tags: motion=[pop, scale-bloom, slide-in] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: a two-word rhetorical turn lands as the punchline, then cuts to a subject
- Motion: On a thin white grid, bold black-shadowed words arrive one at a time: 'but' pops in left-of-center, then 'you?' blooms in larger and slightly right, each scaling up to settle with a small overshoot rather than sliding flat. The words read as discrete beats, not a continuous reveal. On the final frame a cutout photo of a man with a telescope snaps into frame at the right edge, an off-grid side-cutout punctuating the line. Energy is snappy and comedic; each element is a single hard hit.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.1797 · eased_energy_share=1 · sparsity=0.0977 · spatial_concentration=0.3143 · mov_texture=15.8478)
- Source: https://www.youtube.com/watch?v=wTT8QaE0nnw @ 4:12-4:14

### legacy-systems-adapter-diagram-build-e0nnw
- Hero: `legacy-systems-adapter-diagram-build-e0nnw.png` · Strip: `legacy-systems-adapter-diagram-build-e0nnw-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=diagram-build · energy=measured · mood=neutral
- Use when: naming an architecture concept by drawing its node-and-connector diagram
- Motion: Opens on a rounded dark card titled 'Legacy Systems / INTEGRATION' holding an Adapter→API→Module node chain with an underline that draws in along the bottom. The card then clears and a grid takes over, onto which a cluster of flat-style markers steps in left-to-right: a thinking-person icon with a red '?' and yellow lightbulb appears first, then a checklist-and-pencil note slides in to its right, repeating across the remaining frames. The diagram build is calm and deliberate; the icon cluster pops in as discrete additions with no easing flourish.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.2108 · eased_energy_share=0.9509 · sparsity=0.1705 · spatial_concentration=0.4034 · mov_texture=11.545)
- Source: https://www.youtube.com/watch?v=wTT8QaE0nnw @ 4:25-4:31

### chat-card-with-tree-overlay-fade-to-dark-e0nnw
- Hero: `chat-card-with-tree-overlay-fade-to-dark-e0nnw.png` · Strip: `chat-card-with-tree-overlay-fade-to-dark-e0nnw-strip.png`
- Tags: motion=[mask-reveal, draw-on, settle] · archetype=diagram-build · energy=punchy · mood=serious
- Use when: a structural diagram surfaces over a conversation as the scene hands off
- Motion: Starts on a light chat UI — a dark 'App is slow under load' question bubble above a red-tinted answer card and a green reply chip. A green hierarchical tree/org diagram then draws on from the top, its branching nodes appearing over the chat. Across the back half the whole frame dims progressively to near-black, the chat bleeding out while the green linework stays brightest, ending the beat as a fade-to-dark transition. The build is quick and the dimming is a smooth continuous ramp, reading as a graphic handoff between scenes.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.9409 · eased_energy_share=0.9693 · sparsity=0.0834 · spatial_concentration=0.4531 · mov_texture=6.2523)
- Source: https://www.youtube.com/watch?v=wTT8QaE0nnw @ 2:15-2:18

### title-swap-over-filling-ui-progressbar-zh4pq
- Hero: `title-swap-over-filling-ui-progressbar-zh4pq.png` · Strip: `title-swap-over-filling-ui-progressbar-zh4pq-strip.png`
- Tags: motion=[slide-in, mask-reveal, settle] · archetype=title-card · energy=calm · mood=neutral
- Use when: a section title hands off to a demo while a loading bar primes the payoff
- Motion: Frame one holds a centered title (The AI Reality Check) above a dim AI Generator UI card. The title fades out and a new headline (Coding: Lightning Fast) cross-fades in up top, while inside the card a thin progress bar wipes left-to-right, filling a few percent per frame and settling once full. The cadence is slow and measured — one element resolves before the next moves — with no overshoot, just a clean mask-reveal fill.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.4881 · eased_energy_share=0.9256 · sparsity=0.6256 · spatial_concentration=0.6642 · mov_texture=1.5359)
- Source: https://www.youtube.com/watch?v=ya6520zh4pQ @ 2:10-2:12

### segmented-timeline-fills-to-failure-spark-zh4pq
- Hero: `segmented-timeline-fills-to-failure-spark-zh4pq.png` · Strip: `segmented-timeline-fills-to-failure-spark-zh4pq-strip.png`
- Tags: motion=[wipe, snap, particle] · archetype=diagram-build · energy=measured · mood=tense
- Use when: a multi-stage process advances stage by stage until the final step fails
- Motion: A bold PRODUCTION FAILURE headline sits above a horizontal segmented bar (teal, gold, orange stages). Left-to-right across the strip each colored segment locks in and the playhead pushes rightward, until a red hatched FAILURE segment snaps into the rightmost slot with a small burst of red spark particles. The fill is sequential and stepped rather than continuous, and the failure segment lands with a punchy snap that the sparks punctuate.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.55 · eased_energy_share=0.9424 · sparsity=0.6095 · spatial_concentration=0.7018 · mov_texture=6.7904)
- Source: https://www.youtube.com/watch?v=ya6520zh4pQ @ 2:21-2:23

### countdown-card-with-cost-countup-tweets-zh4pq
- Hero: `countdown-card-with-cost-countup-tweets-zh4pq.png` · Strip: `countdown-card-with-cost-countup-tweets-zh4pq-strip.png`
- Tags: motion=[count-up, slide-in, pop] · archetype=stat-hero · energy=measured · mood=ominous
- Use when: a running cost climbs while the clock holds and complaints pile up
- Motion: A large 03:00 PRODUCTION DOWN countdown card holds steady center-stage while a red cost ticker in the lower-right corner counts up frame by frame from -$210 through -$575, -$682, -$718 to -$1,280, the figure popping as each new value lands. Concurrently, dark tweet/notification cards slide in from the top-left and stack. The countdown is static; the motion is all in the accelerating count-up and the staggered card arrivals, giving a mounting-pressure feel.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.9053 · eased_energy_share=0.9881 · sparsity=0.3873 · spatial_concentration=0.5581 · mov_texture=2.8757)
- Source: https://www.youtube.com/watch?v=ya6520zh4pQ @ 3:18-3:20

### the-fork-blur-rack-into-ship-it-split-zh4pq
- Hero: `the-fork-blur-rack-into-ship-it-split-zh4pq.png` · Strip: `the-fork-blur-rack-into-ship-it-split-zh4pq-strip.png`
- Tags: motion=[blur-rack, parallax-drift, mask-reveal] · archetype=split-contrast · energy=measured · mood=serious
- Use when: a decision point splits into two diverging paths
- Motion: A heavy THE FORK title sits sharp in frame one over a code-style <choose_your_destiny/> subtitle, then racks progressively out of focus across the next frames as it drifts subtly, blurring to a soft ghost. As it clears, a new SHIP_IT lightning-bolt path card and a Deep Understanding label mask-reveal in their place, completing a transition from the single question to the two diverging choices. The pacing is deliberate, carried entirely by the focus pull and crossfade rather than any hard cut.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.6643 · eased_energy_share=0.9021 · sparsity=0.5551 · spatial_concentration=0.5855 · mov_texture=0.6897)
- Source: https://www.youtube.com/watch?v=ya6520zh4pQ @ 5:04-5:07

### pixel-grid-triangle-grows-cell-by-cell-mvlw4
- Hero: `pixel-grid-triangle-grows-cell-by-cell-mvlw4.png` · Strip: `pixel-grid-triangle-grows-cell-by-cell-mvlw4-strip.png`
- Tags: motion=[draw-on, scale-bloom, settle] · archetype=diagram-build · energy=punchy · mood=clinical
- Use when: a concept is constructed from primitives, each unit snapping into place to assemble a whole
- Motion: On a dark dotted grid a small white right-triangle of filled cells starts tiny in frame one and grows outward step by step, the diagonal staircase lengthening left-to-right across the strip until it fills the lower-left quadrant. The fill reads as cell-by-cell accretion rather than a uniform scale — each frame adds another rank of squares along the hypotenuse. The final frame partially clears back to a sparser staircase, suggesting a quick reset or re-draw at the tail. Camera holds static; all energy is in the grid filling.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.602 · eased_energy_share=0.9683 · sparsity=0.0017 · spatial_concentration=0.3476 · mov_texture=7.2988)
- Source: https://www.youtube.com/watch?v=4soZ33MvlW4 @ 1:27-1:30

### title-then-console-panel-fades-up-mvlw4
- Hero: `title-then-console-panel-fades-up-mvlw4.png` · Strip: `title-then-console-panel-fades-up-mvlw4-strip.png`
- Tags: motion=[mask-reveal, settle, slide-in] · archetype=title-card · energy=measured · mood=serious
- Use when: a section name lands, then its supporting detail panel quietly resolves beneath it
- Motion: The word 'Hinting' with a thin subtitle sits centered, then migrates: across the strip the heading shrinks and parks to a small top-left label while a dark code/console panel fades up in the center from near-black to a faintly readable card. The reveal is a slow opacity settle, not a wipe — the panel's text emerges gradually as contrast builds. No overshoot; everything eases to a calm rest. A clean title-to-detail handoff transition.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.5876 · eased_energy_share=0.9805 · sparsity=0.4448 · spatial_concentration=0.401 · mov_texture=0.6165)
- Source: https://www.youtube.com/watch?v=4soZ33MvlW4 @ 2:26-2:28

### rotated-grid-card-settles-with-drop-shadow-mvlw4
- Hero: `rotated-grid-card-settles-with-drop-shadow-mvlw4.png` · Strip: `rotated-grid-card-settles-with-drop-shadow-mvlw4-strip.png`
- Tags: motion=[overshoot, settle, parallax-drift] · archetype=device-mockup · energy=measured · mood=clinical
- Use when: an artifact is presented and rotated into its hero pose as the focus object of the beat
- Motion: A white gridded card floats over a soft offset drop-shadow and rotates through the strip — tilted hard counter-clockwise at the start, swinging upright toward portrait and easing past center before settling near-vertical. The shadow lags the card as it turns, giving a parallax depth cue. A small pill label slides in at right and holds. The rotation eases with a gentle overshoot rather than a hard snap, reading as a deliberate present-the-object move under a fixed 'Hardware-Bound' label.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.9758 · eased_energy_share=0.9186 · sparsity=0.2947 · spatial_concentration=0.4538 · mov_texture=6.2112)
- Source: https://www.youtube.com/watch?v=4soZ33MvlW4 @ 4:05-4:08

### staggered-command-cards-slide-in-dcm24
- Hero: `staggered-command-cards-slide-in-dcm24.png` · Strip: `staggered-command-cards-slide-in-dcm24-strip.png`
- Tags: motion=[stagger, slide-in, settle] · archetype=code-reveal · energy=calm · mood=clinical
- Use when: a list of concrete examples accumulates one card at a time under a framing header
- Motion: Under a small 'EVERY TIME YOU...' eyebrow, three dark command cards (SSH KEY, TLS CERT, ENCRYPT FILE) enter one at a time left-to-right, each carrying a monospace shell command and a faint caption line. The stagger is even and unhurried, roughly one card per strip frame, and each card simply fades and settles into place with no overshoot. By the last frames all three sit in a stable row, so the cadence reads as a measured accumulation rather than a snap.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.2972 · eased_energy_share=0.9481 · sparsity=0.6423 · spatial_concentration=0.6243 · mov_texture=0.7561)
- Source: https://www.youtube.com/watch?v=DB0dEPDCm24 @ 0:00-0:02

### typewriter-question-emphasis-word-dcm24
- Hero: `typewriter-question-emphasis-word-dcm24.png` · Strip: `typewriter-question-emphasis-word-dcm24-strip.png`
- Tags: motion=[typewriter, kinetic-type] · archetype=kinetic-type · energy=measured · mood=serious
- Use when: a central question builds word by word and the final emphasis word lands the hook
- Motion: Starting from a lone glyph under a 'TODAY'S QUESTION' eyebrow, the line 'How does a deterministic machine produce true randomness' types in left-to-right and wraps to a second centered line. The reveal is steady and per-word, holding a clean centered block as it grows. The closing words 'true r...' arrive in an accent color, so the emphasis lands as a color shift on the payoff phrase rather than a scale move.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.6311 · eased_energy_share=0.84 · sparsity=0.6381 · spatial_concentration=0.6637 · mov_texture=1.2922)
- Source: https://www.youtube.com/watch?v=DB0dEPDCm24 @ 0:26-0:29

### count-up-possible-keys-stat-hero-dcm24
- Hero: `count-up-possible-keys-stat-hero-dcm24.png` · Strip: `count-up-possible-keys-stat-hero-dcm24-strip.png`
- Tags: motion=[count-up, settle] · archetype=stat-hero · energy=calm · mood=clinical
- Use when: a single large number ticks upward to land a magnitude payoff
- Motion: A big centered numeral over a tiny 'POSSIBLE KEYS' label rolls upward across the strip: 1,613 then 29,891 then 30,843 (held for a frame) then 31,171 (held again). The increments shrink as it climbs, so the count-up decelerates and eases into its final value rather than overshooting. The label stays fixed beneath while only the digits change, keeping the focus on the rising number.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.3828 · eased_energy_share=1 · sparsity=0.4037 · spatial_concentration=0.3633 · mov_texture=8.2993)
- Source: https://www.youtube.com/watch?v=DB0dEPDCm24 @ 1:06-1:09

### entropy-pipeline-diagram-build-dcm24
- Hero: `entropy-pipeline-diagram-build-dcm24.png` · Strip: `entropy-pipeline-diagram-build-dcm24-strip.png`
- Tags: motion=[draw-on, stagger, settle] · archetype=diagram-build · energy=calm · mood=clinical
- Use when: a multi-stage pipeline assembles top-to-bottom to show inputs flowing into outputs
- Motion: Three labeled source nodes (HAND TREMOR, DISK HEAD JITTER, THERMAL NOISE) sit across the top, each feeding a connector down into a row of bit cells that fill in, then into a result node (SSH KEY, TLS HANDSHAKE, SESSION KEY), then a small outcome caption ('your git push', 'your bank HTTPS', 'your encrypted message'). Across the strip the bit rows populate and the lower nodes firm up column by column, so the whole flow chart resolves downward in parallel lanes. Motion is subtle and settling, with no camera move — the layout is stable while the bits and connectors come alive.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.3593 · eased_energy_share=0.906 · sparsity=0.6425 · spatial_concentration=0.2348 · mov_texture=3.6731)
- Source: https://www.youtube.com/watch?v=DB0dEPDCm24 @ 9:12-9:15

### linked-list-node-insert-pointer-rewire-cuijk
- Hero: `linked-list-node-insert-pointer-rewire-cuijk.png` · Strip: `linked-list-node-insert-pointer-rewire-cuijk-strip.png`
- Tags: motion=[draw-on, accordion-reflow, slide-in] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a data structure mutates as a new element is inserted and the connections rewire to accommodate it
- Motion: Boxed character nodes spell a word in monospace, with labeled cursor tags ('alice 4', 'bob 1') popping in above the insertion point and pointer arrows drawn beneath each node. A new highlighted node ('H') inserts mid-word; the arrows below redraw left-to-right to re-thread the linked list around it, and a second concurrent-edit row builds underneath in parallel. In the final frames the inserted node detaches and drops down a tier while the remaining row dims and reflows, settling into the rewired structure. The cadence is deliberate and step-wise — each pointer and tag lands on its own beat rather than all at once.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.2202 · eased_energy_share=0.9683 · sparsity=0.0151 · spatial_concentration=0.1268 · mov_texture=4.1731)
- Source: https://www.youtube.com/watch?v=EL-VoBcUIJk @ 5:26-5:28

### ui-card-node-slide-in-connector-hgjo
- Hero: `ui-card-node-slide-in-connector-hgjo.png` · Strip: `ui-card-node-slide-in-connector-hgjo-strip.png`
- Tags: motion=[slide-in, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a secondary element joins an existing object to show a relationship being added
- Motion: The title 'It's not just a format change' holds fixed at top while a table card sits at left. A small 'UUID' badge node, linked by a short connector arrow, slides in from the right edge and eases to rest beside the table across the strip. The motion is a single restrained lateral slide with a gentle settle, no overshoot; the connector reads as drawing the link between the existing card and the new node.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.541 · eased_energy_share=0.8932 · sparsity=0.4007 · spatial_concentration=0.3429 · mov_texture=0.4193)
- Source: https://www.youtube.com/watch?v=JbdvmQ_HgJo @ 0:26-0:28

### staggered-table-cards-build-cursor-hgjo
- Hero: `staggered-table-cards-build-cursor-hgjo.png` · Strip: `staggered-table-cards-build-cursor-hgjo-strip.png`
- Tags: motion=[stagger, slide-in, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a multi-part schema or pipeline assembles piece by piece as it is explained
- Motion: Under a fixed 'AUTO-INCREMENTING INTEGERS' caption, a central server box appears first, then table panels populate left-to-right in a staggered cascade: one panel, then a second, then a third that carries a small blinking cursor/insert highlight. Each card eases up into place with a short settle and a modest per-card stagger step. The build reads as a database growing column by column, calm and clinical.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.4113 · eased_energy_share=0.9209 · sparsity=0.4797 · spatial_concentration=0.329 · mov_texture=0.4167)
- Source: https://www.youtube.com/watch?v=JbdvmQ_HgJo @ 1:12-1:14

### index-cells-to-byte-bars-countup-hgjo
- Hero: `index-cells-to-byte-bars-countup-hgjo.png` · Strip: `index-cells-to-byte-bars-countup-hgjo-strip.png`
- Tags: motion=[morph, count-up, settle] · archetype=stat-hero · energy=measured · mood=serious
- Use when: a measured comparison resolves into a payoff stat that contrasts two values
- Motion: The strip opens on a table of blue index cells with a '16 B' size label, the rows fading down in brightness across the early frames. It then transforms into a two-column bar chart: a tall purple bar count-up to 90% beside a shorter grey bar at 30%. The transition is a clean morph from the granular cell grid into the headline comparison, the bars rising and settling at their final heights. Strong, deliberate, payoff-shaped.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.2524 · eased_energy_share=0.9298 · sparsity=0.8469 · spatial_concentration=0.3779 · mov_texture=0.075)
- Source: https://www.youtube.com/watch?v=JbdvmQ_HgJo @ 3:48-3:51

### uuid-hash-typewriter-tail-emphasis-hgjo
- Hero: `uuid-hash-typewriter-tail-emphasis-hgjo.png` · Strip: `uuid-hash-typewriter-tail-emphasis-hgjo-strip.png`
- Tags: motion=[typewriter, slide-in, pop] · archetype=kinetic-type · energy=calm · mood=neutral
- Use when: a specific string or token is called out and one part of it is emphasized
- Motion: A full UUID string '018f4a2b-9c1d-7e8ab4c2-d9f1a7e3b502' holds centered at the top for the first several frames. It then drops to a lower position and re-renders larger, where the trailing segment ('b4c2-d9f1a7e3b502') pops to full white while the leading bytes stay dimmed grey, isolating the random tail. The emphasis arrives as a typewriter-style reveal of the hash with a brightness pop on the final chunk.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.6162 · eased_energy_share=0.9691 · sparsity=0 · spatial_concentration=0.2582 · mov_texture=1.4281)
- Source: https://www.youtube.com/watch?v=JbdvmQ_HgJo @ 4:38-4:41

### recap-checklist-items-check-on-stagger-ump1y
- Hero: `recap-checklist-items-check-on-stagger-ump1y.png` · Strip: `recap-checklist-items-check-on-stagger-ump1y-strip.png`
- Tags: motion=[stagger, pop, settle] · archetype=checklist · energy=measured · mood=triumphant
- Use when: a payoff beat tallies up the properties just earned, one confirmation at a time
- Motion: A centered, letter-spaced RECAP eyebrow holds steady at the top while pill-shaped checklist chips appear left to right under it. The first two frames show SELF-HEALING then DYNAMICALLY ROUTED already checked and settled; across the back half of the strip a third chip, HIGHLY AVAILABLE, fades up dimmer and pops into the checked state. Each chip arrives with its green check already filling — a quick stagger of roughly one chip per frame, no overshoot, items just snap on and hold their row.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.6089 · eased_energy_share=0.9778 · sparsity=0.0103 · spatial_concentration=0.3046 · mov_texture=1.1718)
- Source: https://www.youtube.com/watch?v=OJIRCMUmP1Y @ 5:31-5:33

### request-token-sweeps-node-chain-build-ump1y
- Hero: `request-token-sweeps-node-chain-build-ump1y.png` · Strip: `request-token-sweeps-node-chain-build-ump1y-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=diagram-build · energy=punchy · mood=neutral
- Use when: a request is traced step by step through a service pipeline
- Motion: Opens on a left-side checkout/EDGE GATEWAY card pair with a small POST request panel beside it, then cuts to a horizontal node chain — FRONTEND, AUTH, PAYMENT, DATABASE — that is fully laid out with connector lines. A purple trace-id token rides along the top of the row, sitting above FRONTEND, then AUTH, then PAYMENT, then DATABASE across successive frames, while the node directly under it lights with a violet outline. The highlight steps node by node at a brisk, even cadence, settling on DATABASE at the end with no overshoot.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.6137 · eased_energy_share=0.8998 · sparsity=0.7359 · spatial_concentration=0.7474 · mov_texture=0.9739)
- Source: https://www.youtube.com/watch?v=OJIRCMUmP1Y @ 6:28-6:32

### labeled-card-grid-scatters-parallax-drift-ump1y
- Hero: `labeled-card-grid-scatters-parallax-drift-ump1y.png` · Strip: `labeled-card-grid-scatters-parallax-drift-ump1y-strip.png`
- Tags: motion=[parallax-drift, slide-in, settle] · archetype=collage · energy=punchy · mood=serious
- Use when: a tidy inventory of pieces breaks apart to signal complexity or sprawl
- Motion: Under a faint THE INFRASTRUCTURE eyebrow, a clean 3x3 grid of labeled cards (LOAD BALANCER, DATABASE, KUBERNETES, CACHE, DNS, OBJECT STORE, NETWORK RULE, REGISTRY) sits aligned with NETWORK/STORAGE subcaptions. Across the strip the corner cards rotate slightly and drift outward at different rates — KUBERNETES tilts and slides up-right, LOAD BALANCER and OBJECT STORE slip down-left and skew — so the lattice loosens into a scattered parallax spread while the center column (DATABASE, DNS, REGISTRY) stays put. The drift is gentle and continuous, easing apart rather than snapping, leaving the frame sparser by the last panel.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.7769 · eased_energy_share=0.9842 · sparsity=0.4469 · spatial_concentration=0.6554 · mov_texture=1.6967)
- Source: https://www.youtube.com/watch?v=OJIRCMUmP1Y @ 7:52-7:55

### terraform-config-lines-typewriter-beside-card-ump1y
- Hero: `terraform-config-lines-typewriter-beside-card-ump1y.png` · Strip: `terraform-config-lines-typewriter-beside-card-ump1y-strip.png`
- Tags: motion=[typewriter, mask-reveal, settle] · archetype=code-reveal · energy=measured · mood=clinical
- Use when: a config file fills in line by line to show the concrete implementation
- Motion: A Terraform configuration / init.tf editor panel sits on the left, blank with just line numbers, while a Secrets Manager card holding password and tls_cert rows stays fixed on the right. Across the strip the editor types in: first an empty numbered gutter, then a resource "aws_db" "main" block reveals line by line — username, password, tls_cert assignments appearing top-down with syntax color. The reveal is a steady typewriter cadence, each line masking on in order with no easing flourish, settling on the closed brace at the end.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.7035 · eased_energy_share=0.9779 · sparsity=0.1741 · spatial_concentration=0.1811 · mov_texture=1.5208)
- Source: https://www.youtube.com/watch?v=OJIRCMUmP1Y @ 9:38-9:40

### kinetic-title-blurs-out-to-arch-cards-xo5da
- Hero: `kinetic-title-blurs-out-to-arch-cards-xo5da.png` · Strip: `kinetic-title-blurs-out-to-arch-cards-xo5da-strip.png`
- Tags: motion=[blur-rack, mask-reveal, settle] · archetype=diagram-build · energy=measured · mood=neutral
- Use when: a headline concept dissolves and resolves into the system it labels
- Motion: A bold lowercase 'use cache' wordmark holds sharp center-frame, then softens and racks out of focus over the middle frames as it loses contrast. As it clears, three labelled architecture cards (API /users, DATABASE PostgreSQL, CACHE Redis) mask in at their grid positions on the right. The handoff is a clean crossfade, not a slide; the cards arrive already settled with no overshoot, framed by thin colored borders.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.701 · eased_energy_share=0.9797 · sparsity=0.3557 · spatial_concentration=0.2596 · mov_texture=1.6517)
- Source: https://www.youtube.com/watch?v=S7_SOmxO5DA @ 0:08-0:10

### word-by-word-caption-typewriter-greyed-tail-xo5da
- Hero: `word-by-word-caption-typewriter-greyed-tail-xo5da.png` · Strip: `word-by-word-caption-typewriter-greyed-tail-xo5da-strip.png`
- Tags: motion=[typewriter, kinetic-type] · archetype=kinetic-type · energy=calm · mood=neutral
- Use when: a sentence builds clause by clause to land its closing word
- Motion: A single centered line grows left-to-right one phrase at a time ('For' then 'For a lot of us, the' then '...mental model of Redis stops'). Each newly arriving word appears greyed/dim a beat ahead, then settles to full white as the line advances and wraps to a second line. The cadence is even and unhurried, roughly a word-group per frame, with no scale or slide, just opacity-staged reveal.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.4869 · eased_energy_share=0.9226 · sparsity=0.555 · spatial_concentration=0.522 · mov_texture=1.0045)
- Source: https://www.youtube.com/watch?v=S7_SOmxO5DA @ 0:14-0:16

### socket-list-rows-light-ready-into-epoll-card-xo5da
- Hero: `socket-list-rows-light-ready-into-epoll-card-xo5da.png` · Strip: `socket-list-rows-light-ready-into-epoll-card-xo5da-strip.png`
- Tags: motion=[stagger, pop, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a queue of items is processed by a single worker to show throughput
- Motion: A SOCKETS column lists numbered rows; select rows flip to a purple READY state in a staggered cascade down the list while an EPOLL card ('1 thread / POLLING') holds steady to the right. Late in the strip a QUEUE label pops in at top-right. Motion is contained and crisp, each row toggling state rather than moving, conveying the single thread sweeping the ready set.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.3109 · eased_energy_share=0.9693 · sparsity=0.6321 · spatial_concentration=0.4998 · mov_texture=0.8491)
- Source: https://www.youtube.com/watch?v=S7_SOmxO5DA @ 4:12-4:14

### snapshot-timeline-draws-and-pans-left-xo5da
- Hero: `snapshot-timeline-draws-and-pans-left-xo5da.png` · Strip: `snapshot-timeline-draws-and-pans-left-xo5da-strip.png`
- Tags: motion=[draw-on, slide-in, parallax-drift] · archetype=timeline · energy=calm · mood=neutral
- Use when: a series of events is plotted along time as a sequence of markers
- Motion: Under a centered 'POINT-IN-TIME SNAPSHOTS' label a horizontal axis runs across frame with tick markers (#01, #02, #03... with T+ timestamps). Across the strip the marker set advances leftward as new ticks draw on at the right end, a gentle continuous pan that scrolls earlier snapshots off-frame. The motion is slow and even with no overshoot, reading as time progressing along a track.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.9403 · eased_energy_share=0.9136 · sparsity=0.5059 · spatial_concentration=0.5972 · mov_texture=0.5872)
- Source: https://www.youtube.com/watch?v=S7_SOmxO5DA @ 5:18-5:23

### repeating-decimal-digit-cascade-dd27m
- Hero: `repeating-decimal-digit-cascade-dd27m.png` · Strip: `repeating-decimal-digit-cascade-dd27m-strip.png`
- Tags: motion=[kinetic-type, slide-in, typewriter] · archetype=kinetic-type · energy=frenetic · mood=playful
- Use when: a value spills into an endless repeating sequence and you want to feel the 'forever'
- Motion: Above the centered equation '1 / 3 = 0.3333', a filmstrip-style row of monospace '3' glyphs scrolls horizontally beneath it, frame after frame, as if the digit never stops. The last decimal digit in the equation flickers a faint purple tint to mark the live trailing digit. There is no settle — the strip keeps streaming left across every frame, selling an infinite repeat rather than a single landed value.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=6.6074 · eased_energy_share=0.4593 · sparsity=0.0804 · spatial_concentration=0.1668 · mov_texture=3.4042)
- Source: https://www.youtube.com/watch?v=UOqpfGdd27M @ 1:23-1:29

### binary-expansion-progressive-typeout-dd27m
- Hero: `binary-expansion-progressive-typeout-dd27m.png` · Strip: `binary-expansion-progressive-typeout-dd27m-strip.png`
- Tags: motion=[typewriter, count-up, settle] · archetype=code-reveal · energy=measured · mood=clinical
- Use when: a clean decimal turns out to be an ugly never-ending value once converted
- Motion: A small fraction card ('1/5 = 5, REPEATS FOREVER IN BINARY') holds steady on the left while the binary result types out on the right in stages: first a bare '0', then '0.0', then '0.00110...', then '0.0011001100...', each step extending the previous string with an eased reveal. The card stays fixed as the anchor; all motion is the rightward growth of the number, ending on a full grey '0.000110011001100...' overflow line that fills the width. No overshoot — it accretes digit-groups and settles.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.4196 · eased_energy_share=0.326 · sparsity=0.3934 · spatial_concentration=0.5478 · mov_texture=3.2626)
- Source: https://www.youtube.com/watch?v=UOqpfGdd27M @ 3:37-3:44

### bit-field-fill-sign-exponent-mantissa-dd27m
- Hero: `bit-field-fill-sign-exponent-mantissa-dd27m.png` · Strip: `bit-field-fill-sign-exponent-mantissa-dd27m-strip.png`
- Tags: motion=[wipe, stagger, settle] · archetype=diagram-build · energy=punchy · mood=clinical
- Use when: a fixed-size data structure fills up region by region as you explain each part
- Motion: Under a '64 BITS' title and '± 10^x' annotation, a long horizontal bit-strip fills with saturated purple left-to-right in a single eased wipe: it starts grey-empty, the sign+exponent region lights first, then the wipe sweeps across the mantissa until nearly the whole bar is purple. Labels SIGN (1 BIT) and EXPONENT (11 BITS) sit beneath the front segments. In the final frame a faint binary string fades in across the top edge, capping the fill. Confident, single-pass sweep with a clean settle, no rebound.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.6542 · eased_energy_share=0.9237 · sparsity=0.5474 · spatial_concentration=0.7006 · mov_texture=2.1411)
- Source: https://www.youtube.com/watch?v=UOqpfGdd27M @ 4:18-4:20

### price-times-integer-card-flow-dd27m
- Hero: `price-times-integer-card-flow-dd27m.png` · Strip: `price-times-integer-card-flow-dd27m-strip.png`
- Tags: motion=[slide-in, settle, blur-rack] · archetype=split-contrast · energy=measured · mood=serious
- Use when: a takeaway lands, then the supporting cards dissolve to leave only the result
- Motion: A headline 'Integers do not suffer from rounding errors' sits above three elements: a PRICE card '$10.99', a '× 100' arrow, and an INTEGER card '1099'. The three read as a left-to-right equation that holds, then the exit is staged — the headline and the '$10.99' and '× 100' fade and blur away first while the '1099' card stays sharp, until only INTEGER 1099 remains alone. The motion is the selective dissolve that strips everything but the payoff value, settling on the lone integer card.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.9696 · eased_energy_share=0.912 · sparsity=0.2439 · spatial_concentration=0.4399 · mov_texture=1.8078)
- Source: https://www.youtube.com/watch?v=UOqpfGdd27M @ 6:52-6:54

### phrase-swap-line-builds-dim-out-8xfog
- Hero: `phrase-swap-line-builds-dim-out-8xfog.png` · Strip: `phrase-swap-line-builds-dim-out-8xfog-strip.png`
- Tags: motion=[kinetic-type, mask-reveal, settle] · archetype=kinetic-type · energy=measured · mood=serious
- Use when: a spoken sentence reframes mid-thought and you want the words to update in place as the narrator pivots
- Motion: A centered line of body text holds, then dims to grey and fades out as a fresh phrase takes its place. The new clause arrives word-grouped, with the operative noun ('time', 'database') landing last and a beat brighter than the muted lead-in. Each frame swaps one clause for the next on a single anchored baseline, so the eye never tracks position, only the changing words. Calm, editorial cadence with a soft fade between states rather than any slide.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.5161 · eased_energy_share=0.8295 · sparsity=0.3872 · spatial_concentration=0.4394 · mov_texture=0.9832)
- Source: https://www.youtube.com/watch?v=aGv1kd8XFog @ 0:16-0:18

### doc-cards-with-side-panel-fade-in-8xfog
- Hero: `doc-cards-with-side-panel-fade-in-8xfog.png` · Strip: `doc-cards-with-side-panel-fade-in-8xfog-strip.png`
- Tags: motion=[slide-in, mask-reveal, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: introducing a data structure where a source list sits on the left and a derived view assembles beside it
- Motion: Three labeled document cards (DOC_1/2/3) sit stacked at left, fully present from the first frame. A second TERM/DOCS panel materializes at right, fading up from near-invisible to a faint outlined container across the strip without sliding far. The reveal is slow and even, the right panel settling into place as a quiet companion to the left stack. No overshoot; a measured, schematic build.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.1749 · eased_energy_share=0.9817 · sparsity=0.3142 · spatial_concentration=0.3498 · mov_texture=2.138)
- Source: https://www.youtube.com/watch?v=aGv1kd8XFog @ 1:27-1:30

### segment-cards-merge-into-optimized-stack-8xfog
- Hero: `segment-cards-merge-into-optimized-stack-8xfog.png` · Strip: `segment-cards-merge-into-optimized-stack-8xfog-strip.png`
- Tags: motion=[slide-in, morph, accordion-reflow] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: showing several separate pieces consolidating into one combined, optimized whole
- Motion: Under a 'BACKGROUND MERGE' header, three labeled segment columns (SEG 1/2/3) each hold a small stack of doc cards. Across the strip the SEG headers fade out and the three stacks slide inward and overlap, the loose cards cascading together into a single ordered column under a 'MERGED & OPTIMIZED' label. Red-flagged docs drift to the margins as the merged stack settles. The motion is a deliberate left-to-right collapse, cards reflowing into one tidy list rather than snapping.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.4412 · eased_energy_share=0.912 · sparsity=0.2394 · spatial_concentration=0.4857 · mov_texture=2.6942)
- Source: https://www.youtube.com/watch?v=aGv1kd8XFog @ 4:57-4:59

### bar-chart-grows-bar-by-bar-8xfog
- Hero: `bar-chart-grows-bar-by-bar-8xfog.png` · Strip: `bar-chart-grows-bar-by-bar-8xfog-strip.png`
- Tags: motion=[stagger, count-up, settle] · archetype=diagram-build · energy=punchy · mood=neutral
- Use when: a distribution or trend resolves into its full shape as the payoff of a data point
- Motion: Under 'RELEVANCE PER KERNEL APPEARANCE', two purple bars stand first, then additional bars sprout left-to-right one index at a time until a full eight-bar distribution fills the frame. Each new bar grows up from the axis to its height, the staggered entrance tracing the curve's rise-and-fall as it completes. Bars settle at final height without bounce; the build is quick and confident, reading as a histogram assembling in real time.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.2608 · eased_energy_share=0.94 · sparsity=0.4567 · spatial_concentration=0.6944 · mov_texture=4.8848)
- Source: https://www.youtube.com/watch?v=aGv1kd8XFog @ 5:33-5:36

### grid-cells-fill-row-sweep-under-titlecard-8e62y
- Hero: `grid-cells-fill-row-sweep-under-titlecard-8e62y.png` · Strip: `grid-cells-fill-row-sweep-under-titlecard-8e62y-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=diagram-build · energy=calm · mood=clinical
- Use when: a concept is introduced and a grid/queue diagram fills in to embody it
- Motion: A centered title line ('Parallelism is the weapon') holds static while below it a wide grid populates with purple cells. Cells flood in left-to-right and top-down across the strip — the first frame shows a single sparse top row, then successive frames pack more rows in with a slightly uneven, hand-of-cells leading edge. No overshoot; the fill simply accretes and settles into a partially-loaded grid. The cadence is measured tile-by-tile growth rather than a single wipe.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.3916 · eased_energy_share=1 · sparsity=0.5275 · spatial_concentration=0.5057 · mov_texture=2.5271)
- Source: https://www.youtube.com/watch?v=lLDZ9O8E62Y @ 2:09-2:11

### multi-panel-grids-populate-then-red-stateflip-8e62y
- Hero: `multi-panel-grids-populate-then-red-stateflip-8e62y.png` · Strip: `multi-panel-grids-populate-then-red-stateflip-8e62y-strip.png`
- Tags: motion=[slide-in, morph, settle] · archetype=diagram-build · energy=measured · mood=tense
- Use when: parallel work units run side by side and one flips to an error/alert state
- Motion: Three grid panels sit in a row. Early frames show only the left panel filled; the middle and then the right panel populate with purple cells one panel at a time, building a left-to-right comparison. The payoff is the final frame, where the rightmost panel's cells snap from purple to red — a hard color-state morph signalling failure/contention. The build is calm and staged; the red flip lands as the punctuation.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.4265 · eased_energy_share=0.9805 · sparsity=0.635 · spatial_concentration=0.6919 · mov_texture=1.6632)
- Source: https://www.youtube.com/watch?v=lLDZ9O8E62Y @ 4:08-4:10

### countdown-counter-over-draining-grid-progressbar-8e62y
- Hero: `countdown-counter-over-draining-grid-progressbar-8e62y.png` · Strip: `countdown-counter-over-draining-grid-progressbar-8e62y-strip.png`
- Tags: motion=[count-up, settle, wipe] · archetype=stat-hero · energy=measured · mood=serious
- Use when: a running tally drops as a metric resolves toward a target
- Motion: A horizontal progress bar with a numeric readout sits above a large purple grid. Across the strip the counter steps down (286 -> 285 -> 283 -> ... -> 50) while the grid below thins out — rows of cells empty from the bottom up, leaving a shrinking purple band. The progress bar's fill recedes in step with the number. Motion is even and metronomic, the count and the drain locked together, settling on the final low value.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.2627 · eased_energy_share=0.6998 · sparsity=0.7823 · spatial_concentration=0.6546 · mov_texture=4.979)
- Source: https://www.youtube.com/watch?v=lLDZ9O8E62Y @ 4:43-4:46

### big-number-count-up-toward-round-target-ieszg
- Hero: `big-number-count-up-toward-round-target-ieszg.png` · Strip: `big-number-count-up-toward-round-target-ieszg-strip.png`
- Tags: motion=[count-up, settle] · archetype=stat-hero · energy=calm · mood=neutral
- Use when: a single big number is the payoff and you want the audience to feel it climb to a milestone
- Motion: One oversized purple numeral fills the frame and ticks upward across the strip: 3,379,623 then 3,639,054, 4,133,496, 4,193,139, 4,199,906, and finally settling exactly on 4,200,000. The early steps jump in large increments and the later ones shrink to a near-stop, an ease-out deceleration that lands precisely on the round target rather than overshooting. The numeral holds dead-center the whole time with a small label fixed beneath it; nothing else moves, so all attention is on the rolling digits.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.49 · eased_energy_share=0.9698 · sparsity=0.4258 · spatial_concentration=0.4476 · mov_texture=4.7919)
- Source: https://www.youtube.com/watch?v=rZbJLJIESZg @ 1:55-1:58

### staggered-bar-chart-panels-build-left-to-right-ieszg
- Hero: `staggered-bar-chart-panels-build-left-to-right-ieszg.png` · Strip: `staggered-bar-chart-panels-build-left-to-right-ieszg-strip.png`
- Tags: motion=[stagger, slide-in, settle] · archetype=diagram-build · energy=measured · mood=neutral
- Use when: a series of comparable data panels accumulate one by one to show a repeating pattern
- Motion: Under a centered 'one file per week' caption, purple bar-chart panels populate one at a time from the left. The first frame is empty, the second shows a single small histogram, then a second fuller chart joins, and by the final frames four equal-width bar panels sit in a row, each with its own little label header. The bars themselves appear to grow up from the baseline as each panel arrives, and the panels hold their positions once placed — a clean left-to-right accumulation with one panel per beat rather than an overshoot.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.3761 · eased_energy_share=1 · sparsity=0.5723 · spatial_concentration=0.6236 · mov_texture=0.8848)
- Source: https://www.youtube.com/watch?v=rZbJLJIESZg @ 3:41-3:44

### device-card-recedes-into-node-graph-parallax-ieszg
- Hero: `device-card-recedes-into-node-graph-parallax-ieszg.png` · Strip: `device-card-recedes-into-node-graph-parallax-ieszg-strip.png`
- Tags: motion=[parallax-push, scale-bloom, settle] · archetype=device-mockup · energy=measured · mood=neutral
- Use when: a single labeled item shrinks into the background to reveal it as one node among many in a larger structure
- Motion: A centered 'Tesla Model S' card sits above a small line-chart readout and holds for the first three frames. Then the whole card-plus-chart cluster scales down and pushes back toward the upper-center of the frame, shrinking across the last three frames while faint connector lines and sibling nodes begin resolving beneath it. The recession is smooth and eased, reframing the hero card as a single node in an emerging graph rather than snapping.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.409 · eased_energy_share=0.9342 · sparsity=0.2967 · spatial_concentration=0.4969 · mov_texture=0.1907)
- Source: https://www.youtube.com/watch?v=rZbJLJIESZg @ 1:51-1:54

### relational-table-collapses-into-single-graph-node-ieszg
- Hero: `relational-table-collapses-into-single-graph-node-ieszg.png` · Strip: `relational-table-collapses-into-single-graph-node-ieszg-strip.png`
- Tags: motion=[morph, settle, slide-in] · archetype=diagram-build · energy=calm · mood=neutral
- Use when: contrasting two data models by dissolving the old structure into the shape of the new one
- Motion: A 'RELATIONAL' panel with a join table and two query chips holds for the first three frames on the left. Across the back half the table fades and its columns slough away, the layout shifts rightward, and a single circular graph node labeled at the far right resolves into place under a 'GRAPH' header. It reads as a controlled morph from the dense relational grid to one clean node rather than a hard cut — the old structure thins out as the new one settles in.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.2859 · eased_energy_share=0.9407 · sparsity=0.0141 · spatial_concentration=0.2471 · mov_texture=0.2228)
- Source: https://www.youtube.com/watch?v=rZbJLJIESZg @ 6:16-6:18

### neon-grid-plane-arrows-drawon-pgn4o
- Hero: `neon-grid-plane-arrows-drawon-pgn4o.png` · Strip: `neon-grid-plane-arrows-drawon-pgn4o-strip.png`
- Tags: motion=[draw-on, parallax-push, scale-bloom] · archetype=diagram-build · energy=frenetic · mood=tense
- Use when: an abstract system or concept gets established as a glowing tech substrate at the top of a section
- Motion: A dark 3D plane tilted in perspective holds a glowing blue circuit/grid. Across the strip a neon cyan arrow and a flat diamond/quad outline draw themselves on over the surface, the camera pushing in and the grid scaling up frame to frame. It ends on a near-overhead bloom where the whole plane lights up with vertical light streaks rising off the grid — the energy builds rather than settling, a frenetic parallax push into a luminous payoff.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=11.5946 · eased_energy_share=0.887 · sparsity=0.0023 · spatial_concentration=0.2963 · mov_texture=15.2927)
- Source: https://www.youtube.com/watch?v=HGYOqGPGn4o @ 0:00-0:04

### green-waveform-grid-chart-sweep-pgn4o
- Hero: `green-waveform-grid-chart-sweep-pgn4o.png` · Strip: `green-waveform-grid-chart-sweep-pgn4o-strip.png`
- Tags: motion=[draw-on, marker-sweep, settle] · archetype=stat-hero · energy=punchy · mood=neutral
- Use when: a trend line or signal climbs to make a single rising-data point land
- Motion: Centered on a green dotted graph grid, a bright green waveform line draws left-to-right, oscillating then ramping into a sustained upward climb across the middle frames. The sweep advances the line a steady step each frame so the rise reads as a continuous trend rather than discrete bars, settling at a high peak on the right of the graph segment. (The flanking frames are talking-head webcam; only the central graph carries the designed motion.)
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=9.7162 · eased_energy_share=0.7502 · sparsity=0.0001 · spatial_concentration=0.1797 · mov_texture=6.4253)
- Source: https://www.youtube.com/watch?v=HGYOqGPGn4o @ 3:35-3:40

### magenta-typewriter-title-reveal-ip0sw
- Hero: `magenta-typewriter-title-reveal-ip0sw.png` · Strip: `magenta-typewriter-title-reveal-ip0sw-strip.png`
- Tags: motion=[typewriter, kinetic-type] · archetype=title-card · energy=punchy · mood=playful
- Use when: a defining statement lands as the opening claim, typed out for emphasis
- Motion: A single line of bold magenta text types on character by character, centered on a near-black field. Across the strip it grows from 'Rust is a systems prog' to the full 'Rust is a systems programming language', the second word wrapping to a second line as it overflows the width. Cadence is steady, one cluster of glyphs per frame with no overshoot; the text simply holds once complete. No camera move, no easing flourish beyond the constant typing rhythm.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.4906 · eased_energy_share=0.9768 · sparsity=0.305 · spatial_concentration=0.7202 · mov_texture=1.0898)
- Source: https://www.youtube.com/watch?v=MD5Y2DIP0sw @ 0:00-0:02

### blue-tunnel-warp-into-equation-build-fu4cm
- Hero: `blue-tunnel-warp-into-equation-build-fu4cm.png` · Strip: `blue-tunnel-warp-into-equation-build-fu4cm-strip.png`
- Tags: motion=[parallax-push, mask-reveal, kinetic-type] · archetype=diagram-build · energy=frenetic · mood=tense
- Use when: a concept warps from abstract chaos into a single resolved formula or insight
- Motion: Opens on a crystalline static texture that snaps into a blue radial zoom, then accelerates into a deep particle light-tunnel rushing toward the viewer (strong parallax-push toward the vanishing point). The push resolves abruptly into a dark equation panel where a silhouette head and the formula 'E = C + 2/3' sit amid scattered physics annotations. It settles there for two near-identical frames before a red kinetic caption 'Specifically, the' pops in at frame right. The cadence is a hard rush-then-land: continuous forward motion collapsing into a held diagram.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=6.9939 · eased_energy_share=0.9751 · sparsity=0.0011 · spatial_concentration=0.3259 · mov_texture=12.7782)
- Source: https://www.youtube.com/watch?v=W_XbFufu4cM @ 0:49-0:53

### retro-my-computer-icon-pulse-reveal-fu4cm
- Hero: `retro-my-computer-icon-pulse-reveal-fu4cm.png` · Strip: `retro-my-computer-icon-pulse-reveal-fu4cm-strip.png`
- Tags: motion=[scale-bloom, pop, kinetic-type] · archetype=device-mockup · energy=punchy · mood=playful
- Use when: a single familiar UI element is spotlighted as the punchline or subject of the beat
- Motion: A classic Windows 'My Computer' desktop icon sits centered on a teal field; across the first five frames the icon and its label bloom up in scale with a small cursor parked at its edge, the label color shifting (white to yellow) as it pops to full size. The scale step is modest and bouncy, an emphasis pulse rather than an entrance, holding the icon dead-center. The strip then hard-cuts to vintage stock footage of a man at a beige CRT, ending the designed beat. Cadence: a quick centered scale-bloom that lands and holds, then a flat cut-away.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.5603 · eased_energy_share=0.8183 · sparsity=0.1828 · spatial_concentration=0.4715 · mov_texture=2.7565)
- Source: https://www.youtube.com/watch?v=W_XbFufu4cM @ 4:42-4:44

### equation-overlay-energy-burst-hniiq
- Hero: `equation-overlay-energy-burst-hniiq.png` · Strip: `equation-overlay-energy-burst-hniiq-strip.png`
- Tags: motion=[scale-bloom, mask-reveal, particle] · archetype=diagram-build · energy=frenetic · mood=tense
- Use when: an abstract concept gets visualized as it crescendos into a payoff
- Motion: The strip opens on a textured field, then a radial light-burst blooms from center and rack-blurs into a flat teal plane. Over that plane a 'C = 273' equation fades up as faint scattered formula text. The last frames push into a glowing human-head silhouette haloed in white light with 'mc2' energy text bleeding in around it. Each frame swaps the whole graphic rather than staggering elements, so it reads as a fast cross-dissolving build that intensifies toward the bright head-and-equation climax.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=8.0673 · eased_energy_share=0.5986 · sparsity=0.0005 · spatial_concentration=0.3032 · mov_texture=13.2465)
- Source: https://www.youtube.com/watch?v=qx_xC-hniiQ @ 1:32-1:36

### kinetic-type-does-not-compute-glitch-build-vybwk
- Hero: `kinetic-type-does-not-compute-glitch-build-vybwk.png` · Strip: `kinetic-type-does-not-compute-glitch-build-vybwk-strip.png`
- Tags: motion=[kinetic-type, glitch, pop] · archetype=kinetic-type · energy=punchy · mood=tense
- Use when: a punchline lands word-by-word as a hard reaction beat
- Motion: Over a dense multicolor glitch/static field, big chunky green caps build the phrase one word per frame: 'DOES' alone, then 'DOES N', 'DOES NOT', 'DOES NOT COMPUTE' stacking line by line. Each added word pops in at full size with no slide, snapping onto the grid against the flickering noise backdrop. The final frame holds the complete two-line lockup as a small caption card wipes in at the right edge.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.2422 · eased_energy_share=0.9482 · sparsity=0.1237 · spatial_concentration=0.4656 · mov_texture=29.5664)
- Source: https://www.youtube.com/watch?v=5hzX-SvYBwk @ 3:55-3:58

### code-reveal-with-side-cutout-react-vybwk
- Hero: `code-reveal-with-side-cutout-react-vybwk.png` · Strip: `code-reveal-with-side-cutout-react-vybwk-strip.png`
- Tags: motion=[slide-in, mask-reveal, settle] · archetype=code-reveal · energy=frenetic · mood=playful
- Use when: code or config is explained while a reacting character punctuates it
- Motion: A dark IDE panel of syntax-highlighted code occupies the left while a cutout character (a dog) sits anchored bottom-right. Across the strip the code panel swaps and scrolls through successive blocks, then slides fully off-frame to leave the character alone on black before a fresh single-method code card slides back in from the right. The cutout stays planted and reframes slightly, giving the code reveals a reacting foreground anchor.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=12.8422 · eased_energy_share=1 · sparsity=0 · spatial_concentration=0.2451 · mov_texture=4.9485)
- Source: https://www.youtube.com/watch?v=5hzX-SvYBwk @ 2:39-2:41

### book-preview-card-slide-in-beside-portrait-vybwk
- Hero: `book-preview-card-slide-in-beside-portrait-vybwk.png` · Strip: `book-preview-card-slide-in-beside-portrait-vybwk-strip.png`
- Tags: motion=[slide-in, settle, mask-reveal] · archetype=quote-card · energy=measured · mood=neutral
- Use when: a source or citation is introduced as the authority behind a claim
- Motion: A portrait of a man rises in from the bottom edge against black, settling toward the right. As he lands, a white content-preview card wipes/slides in from the left and parks beside him, its text revealing top-down: a 'Content preview from...' line, then the chapter title, then the author byline. The card and portrait reflow so the card ends up dominant on the left with the portrait tucked to the right, a clean lower-third-style attribution build.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.7127 · eased_energy_share=0.9789 · sparsity=0.567 · spatial_concentration=0.5456 · mov_texture=20.8509)
- Source: https://www.youtube.com/watch?v=5hzX-SvYBwk @ 0:35-0:37

### stacked-headline-list-stagger-then-punchline-card-4edok
- Hero: `stacked-headline-list-stagger-then-punchline-card-4edok.png` · Strip: `stacked-headline-list-stagger-then-punchline-card-4edok-strip.png`
- Tags: motion=[stagger, slide-in, settle] · archetype=kinetic-type · energy=measured · mood=tense
- Use when: a list of mounting problems stacks up before a single relieving payoff line lands
- Motion: Four left-aligned headlines build top-to-bottom over a dimmed background — 'Layoffs', then 'More Layoffs', then an indented 'High Competition', then 'Fewer Job Postings' — each line sliding/fading in on its own beat with a small downward stagger step so the stack reads as accumulating dread. The list holds fully assembled, then the frame hard-cuts to a clean dark card with a single right-placed 'Good News' line, flipping the cadence from many-small to one-big as the punchline.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.1235 · eased_energy_share=0.9763 · sparsity=0.2397 · spatial_concentration=0.4575 · mov_texture=7.5258)
- Source: https://www.youtube.com/watch?v=8_qhiv4EDOk @ 0:16-0:20

### 3d-crowd-render-slow-camera-push-4edok
- Hero: `3d-crowd-render-slow-camera-push-4edok.png` · Strip: `3d-crowd-render-slow-camera-push-4edok-strip.png`
- Tags: motion=[camera-orbit, parallax-push, settle] · archetype=collage · energy=punchy · mood=ominous
- Use when: a beat needs to convey scale — 'everyone', a faceless mass, the whole market — without naming individuals
- Motion: A dense field of identical blue 3D figures fills the frame and a slow camera push drifts across and into the crowd, the foreground figures sliding past while the receding ranks compress toward the back — depth parallax doing the work rather than the figures themselves moving. The push decelerates into the final frames, settling on a tighter cluster so a few front figures read as near-individuals against the anonymous mass behind them.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.3796 · eased_energy_share=0.8463 · sparsity=0.0093 · spatial_concentration=0.2213 · mov_texture=22.0751)
- Source: https://www.youtube.com/watch?v=8_qhiv4EDOk @ 2:28-2:30

### money-rain-icon-collage-over-black-yfgnm
- Hero: `money-rain-icon-collage-over-black-yfgnm.png` · Strip: `money-rain-icon-collage-over-black-yfgnm-strip.png`
- Tags: motion=[particle, slide-in, settle] · archetype=collage · energy=frenetic · mood=playful
- Use when: cost or spending spirals as the painful payoff beat
- Motion: On a flat black field a white person-glyph and outlined building icons sit static while flat dollar-bill cutouts tumble and rain across the frame, scattered at varied rotations so the cash reads as falling particles. The bills keep churning frame to frame with little settle, sustaining a busy frenetic loop rather than resolving. On the final frame the money clears and a dense left-aligned UI/text panel snaps in, hard-cutting from the icon collage to a settled content screen.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=7.2772 · eased_energy_share=0.8867 · sparsity=0.1167 · spatial_concentration=0.3678 · mov_texture=13.4848)
- Source: https://www.youtube.com/watch?v=Aiv9NwyfGnM @ 4:42-4:45

### dashboard-ui-panels-reveal-chart-to-wordmark-yfgnm
- Hero: `dashboard-ui-panels-reveal-chart-to-wordmark-yfgnm.png` · Strip: `dashboard-ui-panels-reveal-chart-to-wordmark-yfgnm-strip.png`
- Tags: motion=[slide-in, draw-on, settle] · archetype=code-reveal · energy=punchy · mood=clinical
- Use when: a product or dashboard is introduced and its capabilities tour past
- Motion: Dark dashboard panels and website mockups cycle left-to-right, each screen swapping in with a quick settle while a small red node-graph and copy block hold center. Mid-strip a green bar chart draws up bar by bar inside one of the cards, the data-viz beat punctuating the UI tour. The sequence lands on a clean light-on-dark 'mono' wordmark, resolving the montage into a single branded end card.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.3799 · eased_energy_share=0.8796 · sparsity=0.0146 · spatial_concentration=0.1406 · mov_texture=20.9154)
- Source: https://www.youtube.com/watch?v=Aiv9NwyfGnM @ 5:41-5:43

### tiered-pyramid-diagram-build-money-rain-yfgnm
- Hero: `tiered-pyramid-diagram-build-money-rain-yfgnm.png` · Strip: `tiered-pyramid-diagram-build-money-rain-yfgnm-strip.png`
- Tags: motion=[draw-on, particle, settle] · archetype=diagram-build · energy=frenetic · mood=playful
- Use when: a pricing or hierarchy is laid out in stacked tiers as the structural payoff
- Motion: A three-band pyramid outlines over a centered talking figure, its tiers labelling in sequence from the apex down — 1, 2, 3 paired with Free Tier, Pro Tier, Enterprise — so the structure reads as a build from top to base. Dollar bills rain past the pyramid throughout, the same money-particle motif churning behind the static diagram. The labels hold their positions while the cash keeps tumbling, giving a settled diagram over a frenetic background.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.7947 · eased_energy_share=0.5102 · sparsity=0.2633 · spatial_concentration=0.5478 · mov_texture=14.6456)
- Source: https://www.youtube.com/watch?v=Aiv9NwyfGnM @ 6:01-6:04

### staggered-checklist-fade-up-over-broll-ykpvk
- Hero: `staggered-checklist-fade-up-over-broll-ykpvk.png` · Strip: `staggered-checklist-fade-up-over-broll-ykpvk-strip.png`
- Tags: motion=[stagger, slide-in, settle] · archetype=checklist · energy=calm · mood=serious
- Use when: a short list of principles or steps is enumerated one line at a time as the payoff
- Motion: Over a darkened, blurred B-roll backdrop, three short label lines stack and reveal top-to-bottom with a clear stagger. The strip opens with all three already present on the left ('Think Logically', 'Breakdown Complex Tasks', 'Write Structured Code'), each line set in a different weight/size to imply a hierarchy. Across the later frames the list dissolves out and the backdrop pushes back to full B-roll, so the cadence is a gentle fade-up entrance with a small upward settle on each line, then a soft fade-down exit rather than a snap. Low energy, no overshoot.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.4116 · eased_energy_share=0.928 · sparsity=0.6549 · spatial_concentration=0.6732 · mov_texture=11.6998)
- Source: https://www.youtube.com/watch?v=EMccFrYkPVk @ 2:37-2:42

### isometric-city-title-with-stepped-build-w1dtc
- Hero: `isometric-city-title-with-stepped-build-w1dtc.png` · Strip: `isometric-city-title-with-stepped-build-w1dtc-strip.png`
- Tags: motion=[kinetic-type, slide-in, settle] · archetype=title-card · energy=measured · mood=warm
- Use when: an opening promise/headline lands over a designed illustrated scene before the lesson begins
- Motion: The strip opens on a two-line headline ("Your Career in Web Development Starts Here") set above a low-poly isometric city block, with a colored keyword tinting on the second word. Across the early frames the headline holds while the isometric scene completes, then the camera scrolls/pans down the illustrated road so successive "step" panels slide up into frame one after another. Each step card settles cleanly with no overshoot; the cadence is a steady measured downward reveal rather than a snappy stagger, anchored throughout by the consistent isometric perspective.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.0641 · eased_energy_share=0.8291 · sparsity=0.0193 · spatial_concentration=0.1593 · mov_texture=15.4164)
- Source: https://www.youtube.com/watch?v=Mr-pbsw1dTc @ 1:23-1:28

### illustrated-tv-labels-pop-collage-zw1u
- Hero: `illustrated-tv-labels-pop-collage-zw1u.png` · Strip: `illustrated-tv-labels-pop-collage-zw1u-strip.png`
- Tags: motion=[pop, scale-bloom, snap] · archetype=collage · energy=punchy · mood=playful
- Use when: a noisy roundup of options or features is dumped on screen all at once before being summarized
- Motion: A hand-illustrated cluster of cartoon TV sets fills the frame, each screen stamped with a different garish label (FREE, TV, APP, AD) that pops in at a slightly different beat so the collage reads as a churning wall of competing messages rather than a clean stagger. The labels scale-bloom from small to full size with a quick snap and jitter, keeping the whole arrangement restless across the middle frames. The strip then hard-cuts to a flat black title card where 'You Can Publish Your API' settles with one word color-accented, the chaos resolving into a single clean statement.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.0661 · eased_energy_share=1 · sparsity=0.005 · spatial_concentration=0.3372 · mov_texture=35.7358)
- Source: https://www.youtube.com/watch?v=wBBNNUZw1-U @ 4:57-4:59

### code-bg-money-particles-3d-fly-zw1u
- Hero: `code-bg-money-particles-3d-fly-zw1u.png` · Strip: `code-bg-money-particles-3d-fly-zw1u-strip.png`
- Tags: motion=[particle, parallax-push, pop] · archetype=code-reveal · energy=punchy · mood=triumphant
- Use when: a payoff moment lands the idea of code turning into money or revenue
- Motion: Lines of source code sit on a deep-blue backdrop while photoreal cash bills tumble through 3D space toward camera, the nearer notes blurring and overshooting past frame as the swarm parallax-pushes forward between the first two frames. The motion is a continuous particle drift rather than a staged build, giving a sense of money pouring out of the code. The strip then cuts to black and a clean white PayPal logo card pops in centered, punctuating the beat with the brand as the literal cash-out.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.8435 · eased_energy_share=0.9129 · sparsity=0.2629 · spatial_concentration=0.5084 · mov_texture=13.2336)
- Source: https://www.youtube.com/watch?v=wBBNNUZw1-U @ 5:22-5:25

### minecraft-character-render-scale-bloom-xlggy
- Hero: `minecraft-character-render-scale-bloom-xlggy.png` · Strip: `minecraft-character-render-scale-bloom-xlggy-strip.png`
- Tags: motion=[scale-bloom, pop, settle] · archetype=collage · energy=punchy · mood=playful
- Use when: a cluster of themed icons or character renders pops in as a payoff cutaway
- Motion: On full black the frame starts empty except a tiny orange shard low-left, then the whole Minecraft collage (Steve flanked by a creeper, pig, fox, chicken) scale-blooms up from nothing to near-full size in a single fast pop. Once in, it barely moves — only a small lateral drift and a hint of continued scale as Steve's pose shifts slightly across the last frames. It settles centered with no overshoot rebound; the entrance is the whole event.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.966 · eased_energy_share=0.9806 · sparsity=0 · spatial_concentration=0.1469 · mov_texture=9.5554)
- Source: https://www.youtube.com/watch?v=wC7NS9xlggY @ 3:13-3:16

### webpage-layouts-slide-swap-7uxwo
- Hero: `webpage-layouts-slide-swap-7uxwo.png` · Strip: `webpage-layouts-slide-swap-7uxwo-strip.png`
- Tags: motion=[slide-in, wipe, settle] · archetype=device-mockup · energy=punchy · mood=neutral
- Use when: a sequence of source pages or screenshots fans past to establish breadth of evidence
- Motion: A full-bleed article/landing page holds for two frames, then horizontally slides off as a new layout wipes in from the right; the strip cycles through three distinct page designs (a headline article, a blue 'Markets' data grid, then a 'News & Press Releases' list) each settling flush full-frame before the next swap. The cadence is brisk and even, roughly one page per beat, with no overshoot — a clean lateral push-cut between screen captures rather than a soft cross-dissolve.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=8.7642 · eased_energy_share=0.9746 · sparsity=0.0628 · spatial_concentration=0.4401 · mov_texture=16.7065)
- Source: https://www.youtube.com/watch?v=xof5OZ7uXWo @ 3:10-3:13

### document-form-rise-behind-mascot-7uxwo
- Hero: `document-form-rise-behind-mascot-7uxwo.png` · Strip: `document-form-rise-behind-mascot-7uxwo-strip.png`
- Tags: motion=[slide-in, parallax-push, settle] · archetype=device-mockup · energy=frenetic · mood=playful
- Use when: a paperwork or form artifact looms up as the on-screen subject reacts to it
- Motion: The blue koala mascot sits anchored left of frame while a tall 'JOB APPLICATION FORM' sheet slides up and forward from behind it, growing larger and more detailed across the six frames as its filled fields resolve. The document rises with a steady parallax push rather than a snap, ending dominant in the right half of the frame; the mascot stays put, so the contrast reads as the looming paperwork crowding the character.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.8808 · eased_energy_share=0.818 · sparsity=0.1159 · spatial_concentration=0.3506 · mov_texture=14.1471)
- Source: https://www.youtube.com/watch?v=xof5OZ7uXWo @ 4:21-4:23

### subscribe-cta-buttons-pop-in-7uxwo
- Hero: `subscribe-cta-buttons-pop-in-7uxwo.png` · Strip: `subscribe-cta-buttons-pop-in-7uxwo-strip.png`
- Tags: motion=[pop, slide-in, stagger] · archetype=lower-third · energy=punchy · mood=playful
- Use when: an end-card call-to-action stacks up its subscribe/notify prompts as the closing ask
- Motion: Over a held shot of the presenter, a wooden plank and a stack of YouTube UI chips (a red subscribe button, like/bell badges) pop in one after another, each card snapping to position with a small bounce before the next lands. The buttons accumulate in a staggered vertical stack center-frame, briefly clear out, then re-enter — a punchy, looping CTA assembly rather than a single settle.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.354 · eased_energy_share=0.9279 · sparsity=0.1134 · spatial_concentration=0.4295 · mov_texture=15.6556)
- Source: https://www.youtube.com/watch?v=xof5OZ7uXWo @ 5:29-5:33
