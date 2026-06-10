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
| [tilting-balance-scale-compare-gra0](#tilting-balance-scale-compare-gra0) | split-contrast | settle, slide-in, wipe | measured | clinical | a beat weighs two options against each other before naming the tradeoff |
| [db-table-columns-stagger-build-gra0](#db-table-columns-stagger-build-gra0) | diagram-build | stagger, slide-in, settle | measured | clinical | a structured record or schema assembles column by column as the payoff |
| [paired-device-nodes-arrow-pop-gra0](#paired-device-nodes-arrow-pop-gra0) | diagram-build | pop, slide-in, settle | measured | clinical | two endpoints sync over a link and a transaction lands between them |
| [article-ui-reveal-subscribe-lowerthird-gra0](#article-ui-reveal-subscribe-lowerthird-gra0) | device-mockup | scale-bloom, slide-in, settle | measured | warm | a product or page is shown off and a subscribe prompt slides in to close the beat |
| [graphql-flow-diagram-draw-on-r88xu](#graphql-flow-diagram-draw-on-r88xu) | diagram-build | draw-on, slide-in, settle | calm | clinical | an architecture flows step by step from request to backing store |
| [ai-logo-grid-row-pop-r88xu](#ai-logo-grid-row-pop-r88xu) | collage | pop, stagger, settle | measured | neutral | a roster of brands or options reveals as a populating grid |
| [stateful-stateless-balance-scale-build-r88xu](#stateful-stateless-balance-scale-build-r88xu) | diagram-build | slide-in, stagger, settle | calm | neutral | two approaches are weighed against each other as a tradeoff |
| [icon-row-detection-labels-slide-in-vo7cy](#icon-row-detection-labels-slide-in-vo7cy) | diagram-build | slide-in, typewriter, settle | punchy | clinical | a capability list builds up node-by-node as each feature is named |
| [pipeline-ml-node-scale-bloom-vo7cy](#pipeline-ml-node-scale-bloom-vo7cy) | diagram-build | scale-bloom, slide-in, settle | measured | clinical | a processing stage lands as the centerpiece of a pipeline diagram |
| [architecture-http-arrow-draw-backend-pop-vo7cy](#architecture-http-arrow-draw-backend-pop-vo7cy) | diagram-build | draw-on, pop, settle | measured | clinical | a request hop connects two services in a high-level architecture sketch |
| [digit-counter-rolls-up-beside-static-icons-kphlu](#digit-counter-rolls-up-beside-static-icons-kphlu) | stat-hero | count-up, settle, mask-reveal | calm | neutral | a running tally or scale number ticks up to its landing value as the payoff |
| [code-panel-slides-from-monitor-then-red-x-stamps-kphlu](#code-panel-slides-from-monitor-then-red-x-stamps-kphlu) | code-reveal | slide-in, pop, overshoot | measured | serious | you reveal a code snippet or approach and then mark it as wrong or rejected |
| [url-link-tree-draws-on-node-by-node-kphlu](#url-link-tree-draws-on-node-by-node-kphlu) | diagram-build | draw-on, stagger, slide-in | measured | neutral | a branching structure or graph builds out to show how something fans out from a root |
| [typeahead-suggestion-rows-stack-in-kphlu](#typeahead-suggestion-rows-stack-in-kphlu) | kinetic-type | typewriter, stagger, slide-in | measured | neutral | a search box or list autocompletes and suggestion rows populate beneath an input |
| [logo-wordmark-scale-reveal-over-particle-field-9rb5i](#logo-wordmark-scale-reveal-over-particle-field-9rb5i) | title-card | scale-bloom, pop, settle | measured | neutral | an opening title card brands the topic before the explainer begins |
| [staggered-partition-table-build-with-cursor-labels-9rb5i](#staggered-partition-table-build-with-cursor-labels-9rb5i) | diagram-build | stagger, slide-in, settle | measured | clinical | a concept builds up column by column as each piece of the system is introduced |
| [code-panel-wipe-reveal-json-message-9rb5i](#code-panel-wipe-reveal-json-message-9rb5i) | code-reveal | wipe, mask-reveal, typewriter | measured | clinical | a payload or code snippet is revealed to show the concrete shape of the data |
| [sliding-panel-scene-transition-to-write-consume-9rb5i](#sliding-panel-scene-transition-to-write-consume-9rb5i) | diagram-build | slide-in, wipe, settle | measured | neutral | the scene transitions from one diagram state into the next stage of the system |
| [staggered-tech-logo-intro-build-kpu7k](#staggered-tech-logo-intro-build-kpu7k) | title-card | stagger, pop, settle | measured | neutral | an intro names the topic and pops in the key tools/players one by one before the explainer starts |
| [hash-ring-key-route-callout-kpu7k](#hash-ring-key-route-callout-kpu7k) | diagram-build | pop, draw-on, settle | punchy | clinical | a diagram shows one input being processed and routed to its destination on a structure |
| [cart-fill-buy-cta-outro-collage-kpu7k](#cart-fill-buy-cta-outro-collage-kpu7k) | collage | slide-in, pop, settle | measured | playful | an outro chains a worked example into a product/subscribe call-to-action before the end card |
| [book-cover-wipe-up-pair-kpu7k](#book-cover-wipe-up-pair-kpu7k) | card-flip | wipe, slide-in, settle | frenetic | triumphant | a product or cover reveals fast as the payoff, then a second item joins it |
| [typewriter-stat-into-result-chip-qaxm](#typewriter-stat-into-result-chip-qaxm) | stat-hero | typewriter, slide-in, count-up | measured | neutral | a big number lands and then resolves into a concrete worked example |
| [icons-feed-database-stack-count-up-qaxm](#icons-feed-database-stack-count-up-qaxm) | diagram-build | count-up, slide-in, settle | measured | neutral | a running total climbs as inputs accumulate into a growing store |
| [database-fan-out-to-replicas-draw-on-qaxm](#database-fan-out-to-replicas-draw-on-qaxm) | diagram-build | draw-on, slide-in, settle | measured | neutral | a single node splits its load across multiple downstream copies |
| [request-flow-numbered-steps-draw-on-qaxm](#request-flow-numbered-steps-draw-on-qaxm) | diagram-build | draw-on, slide-in, settle | measured | clinical | walking a request through an architecture left-to-right, step by numbered step |
| [branching-usecase-panels-stagger-reveal-g1xlo](#branching-usecase-panels-stagger-reveal-g1xlo) | diagram-build | draw-on, stagger, mask-reveal | measured | clinical | one parent concept fans out into three parallel use-cases, each unpacking its own detail |
| [matrix-scale-up-grid-grow-g1xlo](#matrix-scale-up-grid-grow-g1xlo) | diagram-build | scale-bloom, count-up, slide-in | punchy | neutral | a small example explodes into a massive scaled-up version to convey order-of-magnitude growth |
| [scalar-to-tensor-ladder-buildout-g1xlo](#scalar-to-tensor-ladder-buildout-g1xlo) | diagram-build | slide-in, stagger, typewriter | measured | clinical | stepping up a conceptual hierarchy one rung at a time, each rung a richer version of the last |
| [labeled-product-cards-pop-in-accent-wipe-odd0](#labeled-product-cards-pop-in-accent-wipe-odd0) | title-card | pop, slide-in, wipe | measured | neutral | an intro that names the two subjects a video will compare or build |
| [vector-presenter-scene-draw-on-build-odd0](#vector-presenter-scene-draw-on-build-odd0) | collage | draw-on, scale-bloom, settle | measured | neutral | a narrated scenario assembles its cast one element at a time |
| [sequence-diagram-lifelines-arrows-draw-on-odd0](#sequence-diagram-lifelines-arrows-draw-on-odd0) | diagram-build | draw-on, stagger, settle | measured | clinical | a protocol or request/response flow is explained step by step |
| [diagram-cards-build-chip-rows-typein-hhpe](#diagram-cards-build-chip-rows-typein-hhpe) | diagram-build | stagger, slide-in, typewriter | measured | clinical | a system's components assemble one labeled node at a time as the explanation lays out the parts |
| [green-particle-shatter-scene-transition-hhpe](#green-particle-shatter-scene-transition-hhpe) | title-card | particle, wipe, snap | punchy | neutral | a hard cut between two graphic scenes needs a designed dissolve instead of a plain jump |
| [time-axis-cells-fill-flow-to-logstack-hhpe](#time-axis-cells-fill-flow-to-logstack-hhpe) | timeline | draw-on, slide-in, settle | measured | clinical | a sequence of events accumulates along a time axis and feeds into a downstream sink |
| [recap-topic-icon-grid-popin-collage-hhpe](#recap-topic-icon-grid-popin-collage-hhpe) | collage | pop, stagger, settle | punchy | triumphant | a closing recap fans out every concept covered as a labeled icon grid |
| [logo-trio-connector-draw-on-bwqaa](#logo-trio-connector-draw-on-bwqaa) | title-card | draw-on, settle | measured | neutral | an intro card establishes the players or sponsors before the topic begins |
| [request-packets-flow-with-red-pulse-bwqaa](#request-packets-flow-with-red-pulse-bwqaa) | diagram-build | slide-in, pop, settle | measured | clinical | a request path is traced node-to-node and one stage lights up to mark a limit or rejection |
| [token-bucket-fill-with-checklist-bwqaa](#token-bucket-fill-with-checklist-bwqaa) | diagram-build | count-up, stagger, settle | measured | clinical | an algorithm or rule set is explained step by step with pass/fail outcomes |
| [sponsor-logo-icon-assemble-rykls](#sponsor-logo-icon-assemble-rykls) | title-card | snap, morph, settle | measured | warm | a sponsor or brand logo lands and resolves into its final mark |
| [transformer-layer-stack-boxes-assemble-rykls](#transformer-layer-stack-boxes-assemble-rykls) | diagram-build | slide-in, stagger, settle | measured | clinical | a layered architecture diagram assembles from its labeled parts |
| [positional-encoding-heatmap-wipe-split-rykls](#positional-encoding-heatmap-wipe-split-rykls) | diagram-build | mask-reveal, wipe, morph | measured | clinical | a continuous data-viz field resolves, then fractures to expose its internal structure |
| [qkv-attention-matrix-grid-build-rykls](#qkv-attention-matrix-grid-build-rykls) | diagram-build | slide-in, stagger, draw-on | punchy | clinical | a math pipeline lays out its matrices and operators left-to-right |
| [title-card-speaker-roster-slide-in-8y3gm](#title-card-speaker-roster-slide-in-8y3gm) | title-card | slide-in, stagger, settle | measured | neutral | a session opens and you introduce the panel — big topic title locked left while the speaker lineup is credited |
| [hub-spoke-node-graph-builds-out-abkiy](#hub-spoke-node-graph-builds-out-abkiy) | diagram-build | draw-on, slide-in, settle | measured | clinical | an architecture grows from a core out to its connected services |
| [brand-logo-grid-pops-in-rows-abkiy](#brand-logo-grid-pops-in-rows-abkiy) | collage | pop, stagger, settle | punchy | neutral | a roster of tools or vendors is enumerated as a grid |
| [numbered-card-typewriter-title-icon-fill-abkiy](#numbered-card-typewriter-title-icon-fill-abkiy) | card-flip | typewriter, pop, settle | measured | neutral | a numbered section header builds and names itself as a new topic opens |
| [isometric-cube-stack-build-gmqsw](#isometric-cube-stack-build-gmqsw) | diagram-build | slide-in, stagger, settle | measured | neutral | an abstract system is assembled piece-by-piece from primitive blocks |
| [chunk-bar-blocks-grow-insert-gmqsw](#chunk-bar-blocks-grow-insert-gmqsw) | diagram-build | count-up, scale-bloom, snap | punchy | neutral | a sequence is shown filling up unit-by-unit, with one element highlighted as inserted |
| [video-fanout-tree-draw-on-gmqsw](#video-fanout-tree-draw-on-gmqsw) | diagram-build | draw-on, slide-in, settle | measured | neutral | one source node branches into several derived outputs |
| [manifest-code-panel-reveal-gmqsw](#manifest-code-panel-reveal-gmqsw) | code-reveal | wipe, mask-reveal, slide-in | punchy | clinical | a spec or config diagram resolves into the actual file contents |
| [radial-branch-callout-pills-reveal-p6vm](#radial-branch-callout-pills-reveal-p6vm) | diagram-build | draw-on, stagger, slide-in | measured | clinical | one central concept fans out into its named sub-options as the payoff |
| [staggered-labeled-arrows-into-node-p6vm](#staggered-labeled-arrows-into-node-p6vm) | diagram-build | stagger, slide-in, draw-on | measured | clinical | several parallel inputs converge on one component, then hand off downstream |
| [icon-card-grid-pop-with-header-pills-p6vm](#icon-card-grid-pop-with-header-pills-p6vm) | checklist | pop, stagger, slide-in | punchy | neutral | a set of related concepts is enumerated as a recap or menu of options |
| [server-db-replica-fanout-with-red-accent-p6vm](#server-db-replica-fanout-with-red-accent-p6vm) | diagram-build | slide-in, draw-on, stagger | measured | serious | a single source scales out into multiple downstream copies |
| [staggered-logo-grid-pop-in-xnlta](#staggered-logo-grid-pop-in-xnlta) | collage | stagger, pop, settle | measured | neutral | naming the field of players an example sits among — competitor or ecosystem logos arriving as a set |
| [checklist-checkmarks-sequence-xnlta](#checklist-checkmarks-sequence-xnlta) | checklist | stagger, draw-on, settle | measured | neutral | a requirements or feature list gets confirmed item by item as the payoff |
| [routing-dataflow-highlight-sweep-xnlta](#routing-dataflow-highlight-sweep-xnlta) | diagram-build | marker-sweep, slide-in, settle | measured | neutral | tracing a path or routing decision live across an already-built system diagram |
| [endcard-book-covers-wipe-up-xnlta](#endcard-book-covers-wipe-up-xnlta) | title-card | wipe, slide-in, settle | punchy | warm | an outro or CTA card resolving on screen at the very end of a piece |
| [diagram-reflow-title-typewriter-qdkqk](#diagram-reflow-title-typewriter-qdkqk) | diagram-build | accordion-reflow, typewriter, settle | measured | clinical | an old labeled diagram collapses to make room for the concept you're really introducing |
| [banner-card-rise-over-logo-backdrop-qdkqk](#banner-card-rise-over-logo-backdrop-qdkqk) | title-card | slide-in, mask-reveal, settle | measured | neutral | a named concept lands as a payoff title against a faint brand backdrop |
| [object-slides-then-staggered-file-grid-qdkqk](#object-slides-then-staggered-file-grid-qdkqk) | diagram-build | slide-in, stagger, settle | measured | clinical | a store/container fills with its contents as you enumerate what lives inside it |
| [tech-logos-slide-swap-kinetic-qdkqk](#tech-logos-slide-swap-kinetic-qdkqk) | kinetic-type | slide-in, kinetic-type, morph | punchy | neutral | two competing tools or brands are name-dropped back to back as alternatives |
| [labeled-icon-grid-staggered-build-lpqv4](#labeled-icon-grid-staggered-build-lpqv4) | diagram-build | stagger, pop, slide-in | measured | clinical | a system's components are introduced one cluster at a time so the whole architecture assembles before the viewer |
| [connector-arrow-draws-across-to-server-cluster-lpqv4](#connector-arrow-draws-across-to-server-cluster-lpqv4) | diagram-build | draw-on, slide-in, settle | measured | clinical | showing a request or handshake travelling from a client node across to a server, with the connection itself as the payoff |
| [green-endcard-panel-wipe-up-reveal-lpqv4](#green-endcard-panel-wipe-up-reveal-lpqv4) | title-card | wipe, slide-in, mask-reveal | frenetic | triumphant | a hard cut to an outro or promo panel that should arrive fast and fill the frame as the closing beat |
| [cyan-pipeline-banner-mask-reveal-bgbjw](#cyan-pipeline-banner-mask-reveal-bgbjw) | diagram-build | mask-reveal, slide-in, settle | measured | clinical | a group of items gets named and wrapped under one labeled concept |
| [labeled-card-slide-then-arrow-draw-to-node-bgbjw](#labeled-card-slide-then-arrow-draw-to-node-bgbjw) | diagram-build | slide-in, draw-on, settle | measured | clinical | a batched input flows into a single processing unit as the payoff of a comparison |
| [primary-replica-fanout-arrows-draw-down-bgbjw](#primary-replica-fanout-arrows-draw-down-bgbjw) | diagram-build | draw-on, slide-in, settle | measured | clinical | one source node fans out to multiple downstream copies as a topology reveals |
| [isometric-ram-sticks-render-with-label-list-bgbjw](#isometric-ram-sticks-render-with-label-list-bgbjw) | diagram-build | parallax-push, slide-in, draw-on | measured | clinical | a hardware or storage concept renders in 3D while supporting labels stack alongside |
| [depth-scale-descent-arrow-draw-xjyio](#depth-scale-descent-arrow-draw-xjyio) | diagram-build | draw-on, slide-in, parallax-drift | measured | serious | establishing a measured descent down a scale toward a goal depth/value |
| [giant-eye-iris-bloom-reveal-xjyio](#giant-eye-iris-bloom-reveal-xjyio) | diagram-build | mask-reveal, scale-bloom, settle | measured | ominous | a hidden presence or threat slowly reveals itself as the payoff to a setup line |
| [earth-to-basketball-scale-morph-weizq](#earth-to-basketball-scale-morph-weizq) | diagram-build | scale-bloom, slide-in, settle | measured | serious | an abstract measurement is made tangible by mapping it onto a familiar object |
| [sphere-stack-build-then-diagonal-reflow-weizq](#sphere-stack-build-then-diagonal-reflow-weizq) | diagram-build | stagger, accordion-reflow, count-up | measured | serious | a count is built up unit by unit and then re-laid-out to read as a total |
| [elliptical-orbit-marker-sweep-distance-diagram-weizq](#elliptical-orbit-marker-sweep-distance-diagram-weizq) | map | draw-on, marker-sweep, settle | calm | clinical | a spatial relationship resolves into a labeled distance or comparison readout |
| [orbital-zone-diagram-label-settle-zzdk](#orbital-zone-diagram-label-settle-zzdk) | diagram | parallax-push, slide-in, settle | measured | serious | an explainer establishes a spatial system and labels each part as it settles into place |
| [diagram-badge-pop-to-planet-render-zzdk](#diagram-badge-pop-to-planet-render-zzdk) | diagram | pop, scale-bloom, snap | punchy | warm | a question or callout pops onto a diagram and then hard-cuts to a hero subject that answers it |
| [probe-line-drop-pin-annotation-blhpk](#probe-line-drop-pin-annotation-blhpk) | diagram-build | draw-on, slide-in, typewriter | calm | serious | a measurement probes into a layered medium and the reading is annotated as it lands |
| [impactor-object-enters-on-leader-line-blhpk](#impactor-object-enters-on-leader-line-blhpk) | diagram-build | slide-in, scale-bloom, settle | measured | serious | a second object enters the frame to collide with or annotate a focal subject |
| [moon-shatter-debris-render-zccg8](#moon-shatter-debris-render-zccg8) | diagram-build | particle, scale-bloom, kinetic-type | frenetic | ominous | a catastrophic transformation lands as the dramatic payoff of an explainer |
| [orbit-rings-draw-on-earth-zccg8](#orbit-rings-draw-on-earth-zccg8) | map | draw-on, slide-in | measured | neutral | an orbital or spatial relationship is set up before the reveal of where something sits |
| [earth-cross-section-layer-scroll-reveal-c7awq](#earth-cross-section-layer-scroll-reveal-c7awq) | diagram-build | parallax-push, slide-in, settle | punchy | warm | a layered structure is introduced top-to-bottom and each stratum is named as it arrives |
| [seismic-raypath-sketch-draw-on-c7awq](#seismic-raypath-sketch-draw-on-c7awq) | diagram-build | draw-on, stagger, settle | measured | clinical | a mechanism is explained by tracing paths through a system and a legend builds alongside |
| [measure-line-overlay-then-title-slide-hvnhy](#measure-line-overlay-then-title-slide-hvnhy) | diagram-build | draw-on, slide-in, settle | measured | clinical | a measured quantity gets annotated on a real subject before its name lands |
| [twin-stat-card-count-up-compare-hvnhy](#twin-stat-card-count-up-compare-hvnhy) | stat-hero | count-up, pop, settle | punchy | triumphant | a headline number lands as the payoff and a second figure pops in to dwarf or contrast it |
| [geology-cross-section-magma-shift-hvnhy](#geology-cross-section-magma-shift-hvnhy) | diagram-build | slide-in, morph, settle | measured | serious | a hidden structure or mechanism is revealed beneath the surface to explain a cause |
| [stacked-place-label-kinetic-list-hvnhy](#stacked-place-label-kinetic-list-hvnhy) | kinetic-type | stagger, pop, slide-in | frenetic | playful | several named items are racked up in quick succession to build a ranked or growing list |
| [sonic-boom-waveform-to-kinetic-onomatopoeia-17j60](#sonic-boom-waveform-to-kinetic-onomatopoeia-17j60) | kinetic-type | draw-on, scale-bloom, kinetic-type | punchy | playful | a sound or invisible force gets visualized as the concept lands |
| [perspective-grid-timeline-build-x5qjc](#perspective-grid-timeline-build-x5qjc) | timeline | draw-on, stagger, slide-in | measured | serious | a deep-time sequence of events lays itself out and you orient the viewer in history |
| [3d-diamond-popup-callout-x5qjc](#3d-diamond-popup-callout-x5qjc) | device-mockup | pop, scale-bloom, particle | punchy | neutral | a hidden mechanism inside an object is revealed as the payoff of a setup |
| [element-card-particle-decay-flash-x5qjc](#element-card-particle-decay-flash-x5qjc) | code-reveal | glitch, particle, wipe | punchy | tense | a technical specimen or data record is examined and then transformed |
| [exponential-decay-curve-drawon-x5qjc](#exponential-decay-curve-drawon-x5qjc) | diagram-build | draw-on, count-up, slide-in | measured | clinical | a relationship is explained by a curve and a moving readout proves the point |
| [species-catalog-cards-stagger-in-grid-iapsw](#species-catalog-cards-stagger-in-grid-iapsw) | diagram-build | stagger, slide-in, settle | measured | clinical | a dataset or catalog populates to back up a claim — entries accumulating into a labeled grid as evidence |
| [kinetic-headline-over-ion-particle-render-d4ink](#kinetic-headline-over-ion-particle-render-d4ink) | kinetic-type | typewriter, particle, kinetic-type | punchy | neutral | a technical term is named and progressively qualified as the concept is introduced |
| [icon-scale-bloom-over-atom-grid-fill-d4ink](#icon-scale-bloom-over-atom-grid-fill-d4ink) | diagram-build | scale-bloom, pop, stagger | punchy | tense | a single charged concept lands as the payoff above a field of supporting units |
| [red-word-emphasis-pop-over-talking-head-v6l0s](#red-word-emphasis-pop-over-talking-head-v6l0s) | kinetic-type | pop, scale-bloom | punchy | playful | a single word in the narration needs to land hard as the emphasized beat |
| [subscribe-cta-button-pop-lower-third-v6l0s](#subscribe-cta-button-pop-lower-third-v6l0s) | lower-third | pop, scale-bloom | measured | warm | the end-card subscribe ask, dropping a CTA chip over a closing shot |
| [single-bar-overshoot-vs-flag-row-y9m4](#single-bar-overshoot-vs-flag-row-y9m4) | stat-hero | count-up, overshoot, slide-in | punchy | playful | one value dwarfs a row of peers and the gap is the punchline |
| [map-annotation-dashed-region-to-heat-glow-y9m4](#map-annotation-dashed-region-to-heat-glow-y9m4) | map | draw-on, scale-bloom, morph | measured | serious | two regional forces are introduced in sequence to set up a cause |
| [typed-headline-into-stacked-timeline-list-s2uos](#typed-headline-into-stacked-timeline-list-s2uos) | timeline | typewriter, stagger, accordion-reflow | punchy | serious | a single named item resolves into the full ordered series it belongs to |
| [lunar-render-camera-track-to-rocket-reveal-s2uos](#lunar-render-camera-track-to-rocket-reveal-s2uos) | map | parallax-push, slide-in, mask-reveal | measured | serious | a rendered environment establishes the scene, then the hero object is revealed at the end of a move |
| [numbered-theory-diagram-build-aqzyi](#numbered-theory-diagram-build-aqzyi) | diagram-build | draw-on, stagger, kinetic-type | punchy | serious | an explainer enumerates a set of competing options before naming the one it will follow |
| [giant-number-countup-then-page-peel-aqzyi](#giant-number-countup-then-page-peel-aqzyi) | kinetic-type | count-up, scale-bloom, wipe | frenetic | playful | a number balloons to an absurd magnitude to dramatize scale, then hands off to the next idea |
| [wordwise-caption-over-data-field-lightburst-aqzyi](#wordwise-caption-over-data-field-lightburst-aqzyi) | kinetic-type | typewriter, mask-reveal, scale-bloom | measured | ominous | narration builds toward a reveal over a moody textured backdrop and resolves into a glowing payoff |
| [moon-name-typewriter-over-emerging-planet-ebnz4](#moon-name-typewriter-over-emerging-planet-ebnz4) | kinetic-type | typewriter, mask-reveal, slide-in | measured | serious | a single named subject is introduced and its one key fact lands underneath |
| [scale-comparison-labels-pop-over-celestial-collage-ebnz4](#scale-comparison-labels-pop-over-celestial-collage-ebnz4) | collage | pop, slide-in, settle | punchy | serious | you cut from a presenter into a stack of compared items, each tagged as it appears |
| [multi-line-chart-draw-on-climb-m7jxy](#multi-line-chart-draw-on-climb-m7jxy) | diagram-build | draw-on, count-up, settle | measured | serious | two trends diverge and the gap between them is the point |
| [kinetic-caption-over-product-render-to-logo-card-m7jxy](#kinetic-caption-over-product-render-to-logo-card-m7jxy) | title-card | kinetic-type, slide-in, wipe | measured | serious | a turn in the argument lands, then hands off to a named brand or entity |
| [acronym-stack-pop-yellow-6n1k8](#acronym-stack-pop-yellow-6n1k8) | kinetic-type | pop, stagger, snap | punchy | playful | an acronym or term gets spelled out and decoded word-by-word as the punchline |
| [captcha-cursor-path-draw-on-6n1k8](#captcha-cursor-path-draw-on-6n1k8) | device-mockup | draw-on, slide-in, settle | calm | clinical | you demonstrate a UI interaction and trace the path of a pointer to explain how it works |
| [logo-wordmark-scale-down-dock-tcjw](#logo-wordmark-scale-down-dock-tcjw) | title-card | scale-bloom, settle, slide-in | punchy | neutral | a product or brand name is introduced before the segment about it begins |
| [title-card-bloom-flash-snap-tcjw](#title-card-bloom-flash-snap-tcjw) | title-card | scale-bloom, snap, glitch | punchy | playful | a recurring segment or chapter title card stamps in as a hard scene break |
| [glitch-kinetic-type-datamosh-tcjw](#glitch-kinetic-type-datamosh-tcjw) | kinetic-type | glitch, kinetic-type, snap | frenetic | tense | an error state or breaking-point phrase needs to read as system failure |
| [glitch-flicker-title-card-8ctzy](#glitch-flicker-title-card-8ctzy) | title-card | glitch, snap, scale-bloom | punchy | playful | a recurring segment ident slams in to mark a hard topic cut |
| [ui-card-reveal-drawn-arrow-cta-8ctzy](#ui-card-reveal-drawn-arrow-cta-8ctzy) | device-mockup | draw-on, slide-in, settle | punchy | neutral | a product UI lands and a hand-drawn pointer flags the exact action to take |
| [benchmark-bar-chart-panel-slide-xmvwe](#benchmark-bar-chart-panel-slide-xmvwe) | diagram-build | slide-in, wipe, settle | punchy | clinical | a model or product wins a head-to-head benchmark and the comparison is the payoff |
| [glitch-wipe-reveal-logotype-xmvwe](#glitch-wipe-reveal-logotype-xmvwe) | title-card | glitch, wipe, snap | frenetic | tense | a hard cut or name-drop punches in and you want a aggressive transition into a title word |
| [benchmark-bar-chart-fill-then-photo-snap-kpto](#benchmark-bar-chart-fill-then-photo-snap-kpto) | stat-hero | wipe, settle, pop | punchy | playful | two competing numbers land side by side as the proof point |
| [logo-title-card-glow-flicker-reveal-kpto](#logo-title-card-glow-flicker-reveal-kpto) | title-card | scale-bloom, glitch, settle | frenetic | playful | a recurring segment ident slams in to open a new chapter |
| [kinetic-headline-with-sweeping-arrow-annotation-g8zpu](#kinetic-headline-with-sweeping-arrow-annotation-g8zpu) | kinetic-type | kinetic-type, marker-sweep, draw-on | measured | playful | a headline term lands and a hand-drawn arrow ties it to a piece of evidence on screen |
| [title-card-glitch-flash-bloom-g8zpu](#title-card-glitch-flash-bloom-g8zpu) | title-card | glitch, scale-bloom, snap | punchy | tense | a recurring section title slams in as a hard scene break between segments |
| [strobe-flash-logo-title-card-dt9i](#strobe-flash-logo-title-card-dt9i) | title-card | glitch, scale-bloom, settle | frenetic | playful | a recurring segment ID slams in as a hard scene break |
| [constellation-word-map-labels-scale-in-dt9i](#constellation-word-map-labels-scale-in-dt9i) | kinetic-type | scale-bloom, parallax-drift, stagger | punchy | playful | loosely-related concepts surface one after another across a connected field |
| [title-lockup-bloom-flash-reveal-yohyk](#title-lockup-bloom-flash-reveal-yohyk) | title-card | scale-bloom, pop, settle | frenetic | playful | a recurring segment-title lockup slams in to open a new section |
| [logo-glitch-blur-to-sharp-yohyk](#logo-glitch-blur-to-sharp-yohyk) | title-card | blur-rack, glitch, snap | measured | neutral | a brand or product logo resolves into focus as it is named |
| [glitch-bloom-logo-badge-settle-vo2q](#glitch-bloom-logo-badge-settle-vo2q) | title-card | glitch, scale-bloom, settle | frenetic | playful | a recurring segment badge slams in to announce a new section |
| [paired-logo-connector-blur-rack-reveal-vo2q](#paired-logo-connector-blur-rack-reveal-vo2q) | collage | slide-in, blur-rack, settle | punchy | playful | two named things get linked into a before/after or A-pipes-to-B relationship |
| [logo-titlecard-glow-bloom-lcrvs](#logo-titlecard-glow-bloom-lcrvs) | title-card | scale-bloom, pop, settle | punchy | playful | a segment-branding bumper punches in to announce a recurring section |
| [reflow-list-stack-reveal-slam-label-lcrvs](#reflow-list-stack-reveal-slam-label-lcrvs) | kinetic-type | slide-in, stagger, snap | frenetic | playful | a punchline term lands while a list of API/method names stacks up as the receipt |
| [angled-slam-label-then-arrow-annotation-lcrvs](#angled-slam-label-then-arrow-annotation-lcrvs) | kinetic-type | snap, pop, draw-on | punchy | playful | a key term slams over a screen-grab, then a hand-drawn arrow points to the one thing to watch |
| [glitch-flare-logo-badge-snap-k0mns](#glitch-flare-logo-badge-snap-k0mns) | title-card | glitch, scale-bloom, snap | frenetic | playful | a recurring segment ident slams in to announce a new section |
| [icon-collage-swap-price-flip-k0mns](#icon-collage-swap-price-flip-k0mns) | collage | pop, slide-in, snap | punchy | playful | a value comparison lands — cheap option versus expensive option side by side |
| [labeled-nodes-dashed-arc-draw-on-k0mns](#labeled-nodes-dashed-arc-draw-on-k0mns) | diagram-build | draw-on, slide-in, settle | measured | serious | a concept gets framed as a set of named parts encircled by one binding idea |
| [pixel-block-logo-assemble-stagger-xlvss](#pixel-block-logo-assemble-stagger-xlvss) | title-card | stagger, slide-in, settle | punchy | playful | a brand mark or title assembles itself piece by piece at the cold open |
| [quiz-option-select-correct-card-pop-xlvss](#quiz-option-select-correct-card-pop-xlvss) | checklist | snap, pop, mask-reveal | punchy | triumphant | a choice is committed and the answer is confirmed as the payoff |
| [vector-triangle-rocket-path-draw-xlvss](#vector-triangle-rocket-path-draw-xlvss) | diagram-build | draw-on, slide-in, pop | measured | warm | a relationship is demonstrated by animating an object along a constructed diagram |
| [ui-slider-drag-into-bar-chart-reveal-hgp5y](#ui-slider-drag-into-bar-chart-reveal-hgp5y) | device-mockup | slide-in, snap, draw-on | measured | clinical | a UI interaction resolves into the data it produces — input handled, then the result chart appears |
| [hand-drawn-arrow-callout-label-sweep-lwfom](#hand-drawn-arrow-callout-label-sweep-lwfom) | lower-third | draw-on, slide-in, settle | measured | playful | a meme or B-roll shot needs a term named and pointed at as the punchline lands |
| [draw-on-arrow-points-to-pixel-card-ffw1w](#draw-on-arrow-points-to-pixel-card-ffw1w) | kinetic-type | draw-on, kinetic-type | measured | playful | a key term gets defined and a hand-drawn pointer ties the words to a concrete example |
| [logo-build-line-to-card-to-glyph-pop-ffw1w](#logo-build-line-to-card-to-glyph-pop-ffw1w) | title-card | draw-on, pop, scale-bloom | measured | triumphant | a brand or product logo assembles itself as the payoff at the end of a section |
| [ui-modal-crossfade-screen-swap-ffw1w](#ui-modal-crossfade-screen-swap-ffw1w) | device-mockup | mask-reveal, blur-rack, slide-in | measured | neutral | a product UI step finishes and the view transitions to the next screen in a flow |
| [logo-particle-dissolve-wipe-iwjys](#logo-particle-dissolve-wipe-iwjys) | title-card | particle, wipe, mask-reveal | punchy | playful | a sponsor or section card exits and hands off to the next scene |
| [sdk-card-grid-parallax-pan-to-mockup-x0rro](#sdk-card-grid-parallax-pan-to-mockup-x0rro) | collage | parallax-push, slide-in, settle | punchy | neutral | an ecosystem of options or integrations is surveyed before zooming to one concrete product |
| [ui-panel-build-then-marker-highlight-stat-ymaug](#ui-panel-build-then-marker-highlight-stat-ymaug) | code-reveal | mask-reveal, marker-sweep, kinetic-type | measured | neutral | a tooled interface fills in, then a count payoff gets underlined as the takeaway |
| [promo-card-particle-dissolve-wipe-ymaug](#promo-card-particle-dissolve-wipe-ymaug) | title-card | particle, wipe, mask-reveal | punchy | playful | a discount or promo card clears off-screen via a textured dissolve into the next scene |
| [icon-cluster-bloom-over-hero-figure-673fa](#icon-cluster-bloom-over-hero-figure-673fa) | collage | scale-bloom, pop, settle | punchy | playful | a concept's pieces all crowd in at once to make a single overwhelming idea land |
| [particle-cloud-disperse-thin-out-673fa](#particle-cloud-disperse-thin-out-673fa) | title-card | particle, parallax-drift | frenetic | tense | a dense mass breaks apart and clears the frame as a transition out of an intense moment |
| [cell-particle-flood-wipe-kinetic-title-cugvq](#cell-particle-flood-wipe-kinetic-title-cugvq) | title-card | particle, wipe, kinetic-type | frenetic | triumphant | a defiant one-line claim lands and you hard-cut to the next section |
| [whiteboard-sketch-then-query-text-reveal-tkfyw](#whiteboard-sketch-then-query-text-reveal-tkfyw) | diagram-build | draw-on, kinetic-type, slide-in | calm | neutral | a posed question or query is introduced and a hand-sketched diagram begins assembling alongside it |
| [character-react-over-flag-collage-build-tkfyw](#character-react-over-flag-collage-build-tkfyw) | collage | pop, settle, mask-reveal | measured | playful | a lively reaction lands as a dense grid of items or logos fills a panel, then clears for the next scene |
| [html-code-panel-typewriter-build-n5diy](#html-code-panel-typewriter-build-n5diy) | code-reveal | typewriter, draw-on | calm | clinical | source code or markup assembles line by line as a concept is explained |
| [whiteboard-type-on-phrase-with-hand-drawn-figure-lkss](#whiteboard-type-on-phrase-with-hand-drawn-figure-lkss) | kinetic-type | typewriter, draw-on, slide-in | measured | playful | a narrated phrase lands as a labelled idea while a hand-drawn character reacts to it |
| [linked-list-node-chain-builds-s45yu](#linked-list-node-chain-builds-s45yu) | diagram-build | mask-reveal, pop, draw-on | measured | neutral | an abstract concept resolves into its concrete structure as the payoff |
| [scene-scale-out-shrink-transition-s45yu](#scene-scale-out-shrink-transition-s45yu) | title-card | settle, parallax-push | measured | neutral | one section closes and the frame pulls back to hand off to the next beat |
| [data-structure-icon-grid-collage-s45yu](#data-structure-icon-grid-collage-s45yu) | collage | mask-reveal, settle | measured | neutral | a recap fans the whole topic set out at once as an overview grid |
| [whiteboard-logo-arrow-callout-reflow-ifoog](#whiteboard-logo-arrow-callout-reflow-ifoog) | diagram-build | draw-on, slide-in, settle | measured | playful | a named concept is introduced and annotated with a hand-drawn callout before clearing for the next point |
| [low-poly-render-camera-push-to-pip-wue78](#low-poly-render-camera-push-to-pip-wue78) | device-mockup | camera-orbit, parallax-push, scale-bloom | frenetic | playful | a 3D/game-render moment lands, then collapses into an inset to hand off to the next scene |
| [lesson-card-collage-with-rgb-colorwheel-wue78](#lesson-card-collage-with-rgb-colorwheel-wue78) | collage | pop, slide-in, mask-reveal | punchy | playful | a rapid montage of distinct concept cards sells a sequence of ideas, each landing with its own hero graphic |
| [device-mockup-zoom-with-block-code-build-wue78](#device-mockup-zoom-with-block-code-build-wue78) | device-mockup | scale-bloom, slide-in, settle | punchy | playful | a UI/device mockup is the hero while a control panel assembles step by step beneath it |
| [code-typewriter-with-definition-lower-third-feygo](#code-typewriter-with-definition-lower-third-feygo) | lower-third | typewriter, slide-in | measured | neutral | a single term gets defined as the code is written that introduces it |
| [code-line-zoom-punch-emphasis-feygo](#code-line-zoom-punch-emphasis-feygo) | code-reveal | scale-bloom, settle | punchy | neutral | one command in a code block is the line that matters and needs to pop |
| [step-title-card-with-logo-build-feygo](#step-title-card-with-logo-build-feygo) | title-card | slide-in, stagger, settle | punchy | playful | a numbered step or chapter break announces the next section |
| [logo-card-spin-flip-settle-feygo](#logo-card-spin-flip-settle-feygo) | title-card | card-flip, snap, settle | frenetic | playful | a brand or logo is called out with a quick, energetic flourish |
| [but-pivot-word-with-year-compare-panel-ki7uc](#but-pivot-word-with-year-compare-panel-ki7uc) | kinetic-type | pop, snap, settle | punchy | tense | a one-word pivot interrupts the momentum right before the turn ('but...') |
| [logo-scale-bloom-soft-glow-over-code-ki7uc](#logo-scale-bloom-soft-glow-over-code-ki7uc) | device-mockup | scale-bloom, pop | punchy | playful | a named product or brand drops in as the punchline over a working screen |
| [bridge-truss-diagram-build-node-by-node-ki7uc](#bridge-truss-diagram-build-node-by-node-ki7uc) | diagram-build | draw-on, stagger, settle | measured | neutral | a structure or system assembles piece by piece to show how the parts connect |
| [agent-pipeline-node-graph-build-htrji](#agent-pipeline-node-graph-build-htrji) | diagram-build | draw-on, slide-in, parallax-push | measured | clinical | a multi-stage pipeline assembles node-by-node as you narrate how the parts hand off |
| [colored-block-flow-diagram-into-title-card-htrji](#colored-block-flow-diagram-into-title-card-htrji) | diagram-build | draw-on, pop, wipe | measured | neutral | a control-flow pattern builds in colored blocks and then resolves to a clean section title |
| [landing-hero-headline-into-ui-reveal-htrji](#landing-hero-headline-into-ui-reveal-htrji) | title-card | scale-bloom, slide-in, settle | punchy | triumphant | a product hero headline lands first, then its supporting UI and sections reveal underneath |
| [oversized-quote-resolves-to-definition-card-utlno](#oversized-quote-resolves-to-definition-card-utlno) | title-card | slide-in, wipe, settle | punchy | playful | a punchline term gets defined as the payoff of a setup |
| [scrolling-caption-banner-panel-wipe-utlno](#scrolling-caption-banner-panel-wipe-utlno) | lower-third | slide-in, kinetic-type, wipe | punchy | playful | a quoted aside or punchline scrolls across as a caption banner |
| [breaking-news-banner-logo-row-pop-qqmes](#breaking-news-banner-logo-row-pop-qqmes) | title-card | pop, stagger, settle | punchy | playful | a mock breaking-news banner stamps in to frame a topic as urgent or hyped |
| [rounded-logo-scale-pop-overshoot-qqmes](#rounded-logo-scale-pop-overshoot-qqmes) | title-card | scale-bloom, overshoot, settle | punchy | warm | a brand or section logo bounces on as a cheerful interstitial stamp |
| [node-graph-glow-to-promo-card-6crlc](#node-graph-glow-to-promo-card-6crlc) | diagram-build | draw-on, slide-in, settle | measured | neutral | a connected-system idea resolves into a single call-to-action payoff |
| [feature-card-grid-then-kinetic-pullquote-6crlc](#feature-card-grid-then-kinetic-pullquote-6crlc) | kinetic-type | stagger, slide-in, scale-bloom | measured | triumphant | a product's features assemble, then a bold quote lands as the closing flourish |
| [kinetic-future-of-title-build-dzxf0](#kinetic-future-of-title-build-dzxf0) | title-card | kinetic-type, slide-in, settle | punchy | neutral | a section title lands to frame the next claim |
| [handwritten-verdict-text-slide-settle-dzxf0](#handwritten-verdict-text-slide-settle-dzxf0) | kinetic-type | slide-in, kinetic-type, settle | punchy | playful | a blunt verdict or punchline lands over a quote or clip |
| [green-check-list-build-then-wipe-dzxf0](#green-check-list-build-then-wipe-dzxf0) | checklist | draw-on, stagger, wipe | punchy | warm | two or three supporting points tick off as the payoff |
| [title-checklist-glitch-dissolve-to-icons-jeab0](#title-checklist-glitch-dissolve-to-icons-jeab0) | checklist | glitch, mask-reveal, settle | frenetic | playful | a labeled concept resolves into its concrete parts as the explanation lands |
| [lock-hub-orbiting-labels-to-icon-set-jeab0](#lock-hub-orbiting-labels-to-icon-set-jeab0) | diagram-build | pop, stagger, settle | frenetic | neutral | a central concept's facets are introduced one by one before the topic is named |
| [server-stack-dissolve-spiking-arrow-draw-jeab0](#server-stack-dissolve-spiking-arrow-draw-jeab0) | diagram-build | draw-on, mask-reveal, scale-bloom | punchy | tense | a cost or metric spikes as the consequence of the prior point |
| [cash-particle-scatter-over-logo-stack-mz0rc](#cash-particle-scatter-over-logo-stack-mz0rc) | collage | particle, scale-bloom, settle | frenetic | playful | a money/cost claim lands and you want the value to feel like it's raining down on a brand mark |
| [logo-reveal-with-evaporative-kinetic-type-mz0rc](#logo-reveal-with-evaporative-kinetic-type-mz0rc) | kinetic-type | slide-in, scale-bloom, settle | punchy | neutral | a named product or spec drops in as the headline while a two-word label punches up beneath it |
| [google-letters-assemble-then-searchbar-slide-mz0rc](#google-letters-assemble-then-searchbar-slide-mz0rc) | title-card | pop, settle, slide-in | measured | neutral | a recognizable brand/logo assembles from its colored parts and a UI element rises to complete the scene |
| [handwritten-checklist-then-3d-skull-render-mz0rc](#handwritten-checklist-then-3d-skull-render-mz0rc) | checklist | draw-on, settle, scale-bloom | punchy | playful | a set of requirements or features gets ticked off one by one before the scene hard-cuts to a payoff visual |
| [scribble-annotated-title-swap-ffam](#scribble-annotated-title-swap-ffam) | title-card | marker-sweep, wipe, snap | punchy | playful | a phrase gets a hand-drawn aside before the idea hard-cuts to its punchline |
| [green-streak-wipe-title-handoff-ffam](#green-streak-wipe-title-handoff-ffam) | title-card | wipe, glitch, snap | punchy | neutral | one labeled idea cuts to the next through a charged transition rather than a clean dissolve |
| [ai-logo-icon-cluster-to-custom-ffam](#ai-logo-icon-cluster-to-custom-ffam) | collage | pop, scale-bloom, snap | punchy | playful | a roster of tools or brands clusters around a subject before the takeaway word lands |
| [kinetic-headline-over-retro-plate-trapq](#kinetic-headline-over-retro-plate-trapq) | kinetic-type | pop, slide-in, settle | punchy | playful | a single concept word lands as a punchy on-screen label over a stylized background image |
| [code-block-wipe-to-image-trapq](#code-block-wipe-to-image-trapq) | code-reveal | wipe, slide-in, snap | punchy | neutral | a code sample hands off to its visual result via a hard scene swap |
| [handwritten-word-under-brand-logo-side-cutout-trapq](#handwritten-word-under-brand-logo-side-cutout-trapq) | title-card | slide-in, draw-on, settle | measured | warm | a brand or tool name is introduced as a friendly titled callout with a supporting cutout |
| [badge-collage-arrow-connect-trapq](#badge-collage-arrow-connect-trapq) | collage | pop, draw-on, stagger | frenetic | playful | two tools or icons connect to each other as the punchline of a busy collage frame |
| [split-flap-board-to-filetree-reveal-enuju](#split-flap-board-to-filetree-reveal-enuju) | device-mockup | slide-in, wipe, settle | punchy | playful | an app or product mockup is introduced, then swapped for the underlying data or file structure behind it |
| [vibe-coding-highlight-wipe-to-solopreneur-enuju](#vibe-coding-highlight-wipe-to-solopreneur-enuju) | title-card | marker-sweep, wipe, kinetic-type | punchy | playful | a punchline label needs to land with emphasis, then hard-cut into a contrasting payoff card |
| [card-dissolve-to-wordmark-logo-dmkia](#card-dissolve-to-wordmark-logo-dmkia) | title-card | mask-reveal, blur-rack, pop | punchy | playful | a named concept resolves into its branded wordmark as the payoff |
| [year-count-up-over-wordmark-dmkia](#year-count-up-over-wordmark-dmkia) | kinetic-type | count-up, snap, wipe | frenetic | neutral | a year or running figure spins up to its final value as a reveal |
| [render-skull-checklist-wipe-to-table-dmkia](#render-skull-checklist-wipe-to-table-dmkia) | checklist | wipe, slide-in, draw-on | punchy | playful | a verdict checklist gives way to the supporting data it summarizes |
| [logo-lockup-3d-petal-bloom-unfurl-alwxs](#logo-lockup-3d-petal-bloom-unfurl-alwxs) | title-card | draw-on, scale-bloom, morph | measured | serious | a brand mark resolves and a designed organic form blooms in to give the title weight |
| [sponsor-logo-confetti-pop-ui-panel-alwxs](#sponsor-logo-confetti-pop-ui-panel-alwxs) | title-card | pop, particle, slide-in | punchy | playful | a sponsor or product name lands as a celebratory beat before its UI is revealed |
| [two-tone-title-word-build-cutout-pop-9013y](#two-tone-title-word-build-cutout-pop-9013y) | kinetic-type | kinetic-type, slide-in, pop | punchy | playful | a named concept is introduced and the label assembles itself on screen |
| [checklist-beside-cutout-blur-wipe-to-title-9013y](#checklist-beside-cutout-blur-wipe-to-title-9013y) | checklist | mask-reveal, blur-rack, wipe | frenetic | neutral | a labeled list of requirements gives way to the next section header |
| [annotated-curve-drawon-arrow-to-title-9013y](#annotated-curve-drawon-arrow-to-title-9013y) | diagram-build | draw-on, marker-sweep, blur-rack | frenetic | playful | a curve illustrates a trade-off and a hand-drawn note calls out its peak |
| [headline-card-motionblur-wipe-out-8pm](#headline-card-motionblur-wipe-out-8pm) | quote-card | wipe, blur-rack, mask-reveal | punchy | serious | a headline or quote lands, holds to be read, then clears to reveal the next subject |
| [handwritten-keyword-popon-formula-field-8pm](#handwritten-keyword-popon-formula-field-8pm) | kinetic-type | pop, scale-bloom, draw-on | punchy | playful | a single concept word punches in to name the idea the narrator just said |
| [red-x-checklist-build-then-wipe-8pm](#red-x-checklist-build-then-wipe-8pm) | checklist | stagger, pop, wipe | punchy | serious | two or three negatives stack up as a list before the scene clears to the payoff |
| [logo-grid-icon-cycle-swap-t0nfu](#logo-grid-icon-cycle-swap-t0nfu) | collage | pop, morph, settle | punchy | neutral | an ecosystem or category list lands as a tidy roster of branded tools/options at once |
| [beveled-letterform-over-parallax-bg-zi0es](#beveled-letterform-over-parallax-bg-zi0es) | title-card | parallax-drift, settle | measured | serious | a single brand letter or monogram opens the piece and needs to feel weighty |
| [comparison-card-grid-build-promo-callout-zi0es](#comparison-card-grid-build-promo-callout-zi0es) | diagram-build | stagger, slide-in, settle | punchy | clinical | a sponsor or product comparison resolves into a clean card grid with a price callout |
| [level-slate-bold-type-over-swirl-diagram-1dook](#level-slate-bold-type-over-swirl-diagram-1dook) | title-card | kinetic-type, settle, wipe | measured | serious | a new chapter or difficulty tier opens and you want a bold slate to announce it |
| [free-cta-serif-blur-rack-over-code-1dook](#free-cta-serif-blur-rack-over-code-1dook) | kinetic-type | blur-rack, scale-bloom, settle | punchy | triumphant | a payoff word lands as the CTA — the free / now / done moment that closes a section |
| [esports-mascot-logo-zap-settle-9rvlc](#esports-mascot-logo-zap-settle-9rvlc) | title-card | slide-in, settle, overshoot | punchy | playful | a brand or product name stamps in as a high-energy intro sting |
| [landing-page-blur-rack-resolve-9rvlc](#landing-page-blur-rack-resolve-9rvlc) | device-mockup | blur-rack, settle, slide-in | frenetic | neutral | a product or website is unveiled as the reveal payoff after a fast cut-in |
| [tilted-annotation-words-pop-over-screen-recording-lfu0](#tilted-annotation-words-pop-over-screen-recording-lfu0) | kinetic-type | pop, kinetic-type, wipe | punchy | playful | a spoken metric gets called out and stamped onto live footage as an annotation |
| [code-editor-autocomplete-dropdown-filter-u1ns8](#code-editor-autocomplete-dropdown-filter-u1ns8) | code-reveal | typewriter, pop, snap | punchy | clinical | a code idea lands by showing the editor finishing the thought for you |
| [dashboard-checklist-columns-reveal-niyfy](#dashboard-checklist-columns-reveal-niyfy) | checklist | slide-in, stagger, settle | measured | clinical | a multi-column project tracker / checklist dashboard fills in as proof of a system |
| [logo-slide-up-settle-zmea](#logo-slide-up-settle-zmea) | title-card | slide-in, scale-bloom, settle | measured | neutral | a brand or tool logo establishes the topic at the open |
| [token-teleport-between-targets-zmea](#token-teleport-between-targets-zmea) | diagram-build | slide-in, snap, settle | measured | playful | a moving token jumps between two targets to illustrate a link or jump |
| [code-card-reveal-list-then-button-pop-zmea](#code-card-reveal-list-then-button-pop-zmea) | code-reveal | slide-in, mask-reveal, pop | measured | neutral | code reveals incrementally and its rendered output lands as payoff |
| [word-pop-scale-on-grid-bohy4](#word-pop-scale-on-grid-bohy4) | kinetic-type | pop, scale-bloom, settle | measured | neutral | a short phrase lands beat-by-beat as the spoken line is emphasized |
| [fast-forward-chevron-streak-transition-bohy4](#fast-forward-chevron-streak-transition-bohy4) | title-card | scale-bloom, blur-rack, wipe | punchy | playful | a 'skip ahead / speed up' moment punctuates a section change |
| [blur-rack-keyword-with-meme-cutouts-bohy4](#blur-rack-keyword-with-meme-cutouts-bohy4) | kinetic-type | blur-rack, slide-in, settle | measured | playful | a punchline keyword resolves out of blur after a setup contrast line |
| [title-card-to-code-blur-streak-cut-bohy4](#title-card-to-code-blur-streak-cut-bohy4) | title-card | blur-rack, wipe, slide-in | punchy | serious | a named mistake or chapter title hands off into the live code that demonstrates it |
| [grid-icon-stagger-reveal-8sa5g](#grid-icon-stagger-reveal-8sa5g) | diagram-build | stagger, pop, slide-in | punchy | playful | a short list of concept tokens lands one after another as the beat enumerates them |
| [blur-rack-word-then-site-push-in-kkqqe](#blur-rack-word-then-site-push-in-kkqqe) | kinetic-type | blur-rack, parallax-push, settle | punchy | neutral | a single keyword lands first, then the product it names rushes onto frame |
| [twin-logo-drift-morph-over-editor-kkqqe](#twin-logo-drift-morph-over-editor-kkqqe) | collage | morph, parallax-drift, scale-bloom | frenetic | playful | two competing tools or stacks are weighed side by side before one gives way |
| [staggered-benefit-cards-around-cube-spotlight-kkqqe](#staggered-benefit-cards-around-cube-spotlight-kkqqe) | diagram-build | stagger, slide-in, marker-sweep | measured | neutral | a feature set assembles around a central object as the value proposition builds |
| [tumbling-js-logo-card-overshoot-7ir3e](#tumbling-js-logo-card-overshoot-7ir3e) | title-card | overshoot, settle, pop | punchy | playful | a brand or language mark gets introduced as a bouncy cold-open emblem |
| [tech-stack-spec-card-swap-7ir3e](#tech-stack-spec-card-swap-7ir3e) | device-mockup | mask-reveal, slide-in, settle | measured | clinical | you swap one labeled spec or tech-stack card for the next in a comparison |
| [nope-card-pop-to-sticky-note-7ir3e](#nope-card-pop-to-sticky-note-7ir3e) | kinetic-type | scale-bloom, snap, slide-in | punchy | playful | a punchline word lands hard then flips to its cheeky opposite |
| [flexbox-cards-redistribute-with-code-label-qwlgk](#flexbox-cards-redistribute-with-code-label-qwlgk) | diagram-build | slide-in, settle, morph | measured | clinical | a parameter change is demonstrated by re-laying-out the same elements side-by-side with the code that drives it |
| [axis-key-title-card-labeled-chips-qwlgk](#axis-key-title-card-labeled-chips-qwlgk) | title-card | mask-reveal, settle | calm | clinical | a definition or mnemonic lands as the takeaway before returning to the demo |
| [rgb-split-glitch-hero-transition-0iqw4](#rgb-split-glitch-hero-transition-0iqw4) | title-card | glitch, blur-rack, snap | frenetic | tense | a hard cut into a new section that should feel disruptive, like a system glitching to a reveal |
| [numbered-checklist-row-reveal-0iqw4](#numbered-checklist-row-reveal-0iqw4) | checklist | stagger, slide-in, settle | punchy | playful | enumerating a ranked list of items where each row should land one at a time as a payoff |
| [stacked-logo-scale-bloom-reveal-0iqw4](#stacked-logo-scale-bloom-reveal-0iqw4) | title-card | scale-bloom, pop, settle | punchy | neutral | introducing a second product or brand alongside one already on screen, as a head-to-head pairing |
| [code-panel-sweep-to-stat-ring-0iqw4](#code-panel-sweep-to-stat-ring-0iqw4) | code-reveal | marker-sweep, draw-on, count-up | punchy | clinical | a build or processing step resolves into a single metric that quantifies the payoff |
| [labeled-skill-cards-orbit-build-bs9sk](#labeled-skill-cards-orbit-build-bs9sk) | diagram-build | slide-in, settle, stagger | measured | neutral | two or more category labels populate around a central concept as the structure is introduced |
| [logo-tile-snap-wordmark-blur-rack-bs9sk](#logo-tile-snap-wordmark-blur-rack-bs9sk) | kinetic-type | blur-rack, snap, pop | punchy | neutral | a named tool or brand lands as a beat punctuation on a dark grid |
| [sticker-card-collage-blur-in-bs9sk](#sticker-card-collage-blur-in-bs9sk) | collage | pop, blur-rack, stagger | punchy | playful | a payoff list of benefits or proof items assembles under a headline |
| [centered-word-swap-on-grid-xutwk](#centered-word-swap-on-grid-xutwk) | kinetic-type | kinetic-type, snap, settle | punchy | neutral | a single emphasis word lands one at a time to drive a point home |
| [motion-blur-smear-word-morph-xutwk](#motion-blur-smear-word-morph-xutwk) | title-card | morph, blur-rack, wipe | frenetic | playful | a fast graphic transition smears between two labelled concepts |
| [ui-card-tumble-zoom-in-xutwk](#ui-card-tumble-zoom-in-xutwk) | device-mockup | scale-bloom, blur-rack, settle | punchy | playful | a UI or product panel slams into frame as the reveal of a result |
| [code-editor-demo-then-chrome-title-xutwk](#code-editor-demo-then-chrome-title-xutwk) | code-reveal | typewriter, scale-bloom, kinetic-type | punchy | neutral | a code example runs live before its concept name is stamped on screen |
| [equation-overlay-warp-build-1kvyq](#equation-overlay-warp-build-1kvyq) | kinetic-type | parallax-push, mask-reveal, kinetic-type | frenetic | tense | an abstract idea or formula is being introduced and the screen builds toward a concept reveal |
| [equation-swarm-into-section-title-1kvyq](#equation-swarm-into-section-title-1kvyq) | title-card | kinetic-type, settle, pop | frenetic | serious | a dense build resolves into a section header that names the next part of the argument |
| [kinetic-label-stack-over-3d-tunnel-nlpu](#kinetic-label-stack-over-3d-tunnel-nlpu) | kinetic-type | kinetic-type, pop, settle | punchy | serious | naming the parts of a system one label at a time as the narration introduces them |
| [flame-particle-overlay-on-desktop-nlpu](#flame-particle-overlay-on-desktop-nlpu) | code-reveal | particle, scale-bloom, draw-on | frenetic | tense | dramatizing a screen or interface under threat or being consumed |
| [ui-panel-slide-then-perspective-scroll-push-adso](#ui-panel-slide-then-perspective-scroll-push-adso) | device-mockup | slide-in, parallax-push, snap | punchy | neutral | a product UI is introduced and then its content rushes past as the camera dives in |
| [logo-then-typewriter-caption-4uhkm](#logo-then-typewriter-caption-4uhkm) | kinetic-type | typewriter, slide-in | measured | neutral | a named subject is introduced and its tagline types itself out beside the brand mark |
| [swiss-army-icon-tools-unfold-4uhkm](#swiss-army-icon-tools-unfold-4uhkm) | diagram-build | draw-on, pop, settle | punchy | playful | a single icon assembles part by part to dramatize a 'one thing, many capabilities' point |
| [two-option-language-pick-icon-pop-v0vw](#two-option-language-pick-icon-pop-v0vw) | kinetic-type | pop, slide-in | punchy | playful | an either/or choice resolves and the second option lands as the punchline |
| [code-panels-reveal-with-kinetic-caption-sjsm0](#code-panels-reveal-with-kinetic-caption-sjsm0) | code-reveal | mask-reveal, kinetic-type, slide-in | punchy | neutral | a list of things-you'll-learn lands while code fills the frame and a phrase punches in word-by-word |
| [brain-bowl-character-lift-label-card-jxylk](#brain-bowl-character-lift-label-card-jxylk) | diagram-build | pop, slide-in, settle | punchy | playful | a memorable acronym or framework is introduced one letter at a time |
| [landing-page-roadmap-node-reveal-zoom-jxylk](#landing-page-roadmap-node-reveal-zoom-jxylk) | device-mockup | mask-reveal, parallax-push, draw-on | measured | neutral | a product or roadmap is walked through as the credible payoff to a pitch |
| [thinking-contrast-cards-with-meditating-monkey-jxylk](#thinking-contrast-cards-with-meditating-monkey-jxylk) | split-contrast | slide-in, stagger, settle | measured | warm | two framings of the same idea are contrasted before landing a one-line takeaway |
| [kinetic-line-over-paper-storm-then-prohibition-icon-jpu2g](#kinetic-line-over-paper-storm-then-prohibition-icon-jpu2g) | kinetic-type | kinetic-type, particle, pop | frenetic | tense | a cold-open premise lands as a swirl, then a hard 'no' snaps in to name the antagonist |
| [logo-hold-then-definition-card-slide-in-jpu2g](#logo-hold-then-definition-card-slide-in-jpu2g) | quote-card | slide-in, settle | measured | neutral | a key term gets defined — a logo holds while an explainer card slides in to deliver the definition |
| [build-your-own-card-grid-scroll-to-pill-tabs-jpu2g](#build-your-own-card-grid-scroll-to-pill-tabs-jpu2g) | code-reveal | slide-in, parallax-drift, settle | measured | clinical | a catalog of options or features reveals as a scrolling card grid that lands on a tabbed selector |
| [graffiti-the-end-card-with-comment-cta-jzg7y](#graffiti-the-end-card-with-comment-cta-jzg7y) | title-card | settle, pop | measured | playful | the outro beat that closes the video and asks for engagement |
| [mascot-prop-slide-in-subscribe-pop-jzg7y](#mascot-prop-slide-in-subscribe-pop-jzg7y) | title-card | slide-in, pop, snap | punchy | playful | an outro beat that pairs a character gag with a subscribe call-to-action |
| [red-word-title-card-cut-q09xs](#red-word-title-card-cut-q09xs) | title-card | kinetic-type, snap | punchy | serious | a section transition lands a two-word claim with one word as the hook |
| [course-card-ui-zoom-into-player-q09xs](#course-card-ui-zoom-into-player-q09xs) | device-mockup | scale-bloom, settle, mask-reveal | measured | neutral | a product/app payoff zooms from an overview into one focused screen |
| [doodle-draw-on-wow-pop-zhkze](#doodle-draw-on-wow-pop-zhkze) | kinetic-type | draw-on, pop, wipe | playful | playful | a punchline lands and a reaction word needs to pop over the frame |
| [prd-title-card-lower-third-slide-zhkze](#prd-title-card-lower-third-slide-zhkze) | title-card | slide-in, settle | measured | neutral | a chapter or topic title needs to establish before the content scrolls in |
| [lightning-title-into-node-graph-xtauy](#lightning-title-into-node-graph-xtauy) | diagram-build | mask-reveal, stagger, settle | measured | serious | a connected system is introduced and its parts wire up one tier at a time |
| [pr-ui-into-diff-fill-xtauy](#pr-ui-into-diff-fill-xtauy) | code-reveal | wipe, slide-in, settle | frenetic | neutral | a change set lands and the code diff fills in as the payoff |
| [mascot-exit-document-slide-reveal-5rlhi](#mascot-exit-document-slide-reveal-5rlhi) | device-mockup | slide-in, wipe, settle | punchy | playful | a prop or document takes over the frame as the topic shifts to a concrete artifact |
| [two-tone-title-over-money-particle-rain-5rlhi](#two-tone-title-over-money-particle-rain-5rlhi) | title-card | kinetic-type, particle, pop | frenetic | playful | a punchy headline lands as the payoff over an energetic textured background |
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

### sonic-boom-waveform-to-kinetic-onomatopoeia-17j60
- Hero: `sonic-boom-waveform-to-kinetic-onomatopoeia-17j60.png` · Strip: `sonic-boom-waveform-to-kinetic-onomatopoeia-17j60-strip.png`
- Tags: motion=[draw-on, scale-bloom, kinetic-type] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: a sound or invisible force gets visualized as the concept lands
- Motion: Over a sky plate a thin neon-green horizontal waveform line draws on left-to-right, then a small green arrow/cursor tracks along it frame by frame as the shock front advances. On the payoff frame a large kinetic 'OOOOOMMMM' onomatopoeia scale-blooms in big green letters wrapped by a swelling ring, settling centered before a hard cut to a dark 3D plane render. The waveform animates steadily, then the type pops with a punchy overshoot rather than easing in slowly.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=24.2856 · eased_energy_share=0.9692 · sparsity=0 · spatial_concentration=0.1599 · mov_texture=6.1502)
- Source: https://www.youtube.com/watch?v=6MJv7A17j60 @ 0:16-0:19

### perspective-grid-timeline-build-x5qjc
- Hero: `perspective-grid-timeline-build-x5qjc.png` · Strip: `perspective-grid-timeline-build-x5qjc-strip.png`
- Tags: motion=[draw-on, stagger, slide-in] · archetype=timeline · energy=measured · mood=serious
- Use when: a deep-time sequence of events lays itself out and you orient the viewer in history
- Motion: A receding horizontal timeline drawn in vanishing-point perspective fills the lower third, then dated milestone markers ("DINOSAUR EXTINCTION", "OPENING OF THE ATLANTIC") populate along it with their planet/icon tokens and small label cards. Across the strip the markers arrive staggered from the far end toward camera, each label sliding to its anchor on the line and settling without overshoot. The grid stays fixed while content accumulates; a green "TODAY" tag holds at the near edge as the reference point. Calm, didactic accumulation rather than punchy entrances.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.1242 · eased_energy_share=0.9561 · sparsity=0.1859 · spatial_concentration=0.4196 · mov_texture=13.3104)
- Source: https://www.youtube.com/watch?v=B9vdFqX5qJc @ 0:10-0:13

### 3d-diamond-popup-callout-x5qjc
- Hero: `3d-diamond-popup-callout-x5qjc.png` · Strip: `3d-diamond-popup-callout-x5qjc-strip.png`
- Tags: motion=[pop, scale-bloom, particle] · archetype=device-mockup · energy=punchy · mood=neutral
- Use when: a hidden mechanism inside an object is revealed as the payoff of a setup
- Motion: A photoreal 3D diamond sits rotating gently on a grey pedestal against deep blue for the first four frames, holding steady. Then a green callout balloon pops up out of the gem on a hooked arrow, scale-blooming a small spinning atom/particle render above the stone ("RADIOACTIVE ELEMENTS" then "A NATURAL ATOMIC CLOCK"). The pop is a quick overshoot-and-settle that lifts the callout clear of the diamond; the underlying render keeps its slow idle spin throughout.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.1165 · eased_energy_share=0.9768 · sparsity=0.4518 · spatial_concentration=0.633 · mov_texture=7.4513)
- Source: https://www.youtube.com/watch?v=B9vdFqX5qJc @ 0:31-0:34

### element-card-particle-decay-flash-x5qjc
- Hero: `element-card-particle-decay-flash-x5qjc.png` · Strip: `element-card-particle-decay-flash-x5qjc-strip.png`
- Tags: motion=[glitch, particle, wipe] · archetype=code-reveal · energy=punchy · mood=tense
- Use when: a technical specimen or data record is examined and then transformed
- Motion: A framed periodic-table-style card ("75 / Re / RHENIUM-187") sits over a dark blueprint grid, its yellow selection box and particle field shimmering in place for two frames. A full-frame cyan flash wipes across, then the card re-resolves with the box and label re-drawing and a softer particle decay glittering inside the frame as a "RHENIUM-187" tag fades in below. Sci-fi, slightly glitchy energy: the flash is the hard transition, the particle texture gives constant low-level motion.
- Motion-metrics: energy=punchy · cadence=continuous · spatial=localized · gate=continuous · src=scan
  (flow: motion_energy=1.5271 · eased_energy_share=0 · sparsity=0.6254 · spatial_concentration=0.7476 · mov_texture=14.4022)
- Source: https://www.youtube.com/watch?v=B9vdFqX5qJc @ 0:34-0:38

### exponential-decay-curve-drawon-x5qjc
- Hero: `exponential-decay-curve-drawon-x5qjc.png` · Strip: `exponential-decay-curve-drawon-x5qjc-strip.png`
- Tags: motion=[draw-on, count-up, slide-in] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a relationship is explained by a curve and a moving readout proves the point
- Motion: An exponential decay curve draws on from the top-left down a labelled "AGE" axis, the line tracing across the strip while two floating value pills (a yellow and a cyan label, like "24%" / "34%") ride along and update their numbers. A marker dot slides down the curve to its settle point on the x-axis as the pills converge near it. Clean, restrained data-viz: the draw-on is the main motion, the count-up pills the secondary readout, no overshoot.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.9308 · eased_energy_share=1 · sparsity=0.1397 · spatial_concentration=0.506 · mov_texture=11.8793)
- Source: https://www.youtube.com/watch?v=B9vdFqX5qJc @ 0:38-0:41

### species-catalog-cards-stagger-in-grid-iapsw
- Hero: `species-catalog-cards-stagger-in-grid-iapsw.png` · Strip: `species-catalog-cards-stagger-in-grid-iapsw-strip.png`
- Tags: motion=[stagger, slide-in, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a dataset or catalog populates to back up a claim — entries accumulating into a labeled grid as evidence
- Motion: A dark-UI data panel builds left-to-right: a single creature silhouette card sits anchored at lower-left while species-ID cards (small specimen icons paired with monospaced 'SPECIES ID' codes) populate the right two-thirds of the frame. The cards arrive in a staggered march — first a vertical stack along the right edge, then the grid widens column by column under a 'KNOWN SPECIES' header that snaps in once enough entries land. Each card slides in a short distance and settles flush into its slot with no overshoot, a clean clinical accretion rather than a bounce. The cadence is steady and metered, reading as a database filling in row by row.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.167 · eased_energy_share=0.8928 · sparsity=0.4891 · spatial_concentration=0.6588 · mov_texture=14.3158)
- Source: https://www.youtube.com/watch?v=MQwZdGiaPsw @ 0:32-0:35

### kinetic-headline-over-ion-particle-render-d4ink
- Hero: `kinetic-headline-over-ion-particle-render-d4ink.png` · Strip: `kinetic-headline-over-ion-particle-render-d4ink-strip.png`
- Tags: motion=[typewriter, particle, kinetic-type] · archetype=kinetic-type · energy=punchy · mood=neutral
- Use when: a technical term is named and progressively qualified as the concept is introduced
- Motion: Across the strip a headline accumulates word by word in yellow caps — 'ELECTRIC', then '+ PROPULSION', then '+ (ION DRIVE)' — each clause snapping in on its own beat over a 3D-rendered cylindrical thruster. Beneath it a continuous yellow-and-blue particle stream pours downward through the chamber the whole time, and a lower-third caption rewrites itself in step with the headline. The render holds full-frame and steady; the motion is the staged text reveal plus the constant ion-particle flow, with no camera move.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.8629 · eased_energy_share=0.7554 · sparsity=0.437 · spatial_concentration=0.6533 · mov_texture=13.6746)
- Source: https://www.youtube.com/watch?v=NV8jFpd4INk @ 0:13-0:16

### icon-scale-bloom-over-atom-grid-fill-d4ink
- Hero: `icon-scale-bloom-over-atom-grid-fill-d4ink.png` · Strip: `icon-scale-bloom-over-atom-grid-fill-d4ink-strip.png`
- Tags: motion=[scale-bloom, pop, stagger] · archetype=diagram-build · energy=punchy · mood=tense
- Use when: a single charged concept lands as the payoff above a field of supporting units
- Motion: A radioactive/nuclear glyph blooms from a tiny dot in the first frame to a large glowing yellow disc by the last, scaling up in a few punctuated steps before settling at full size with a soft outer glow. Below it a grid of small blue atom icons fills in row by row, denser in later frames, so the field reads as building up under the symbol. Camera stays locked full-frame; the energy is all in the central icon's scale-bloom plus the staggered grid fill.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.6174 · eased_energy_share=1 · sparsity=0.0429 · spatial_concentration=0.6119 · mov_texture=11.8384)
- Source: https://www.youtube.com/watch?v=NV8jFpd4INk @ 0:27-0:29

### red-word-emphasis-pop-over-talking-head-v6l0s
- Hero: `red-word-emphasis-pop-over-talking-head-v6l0s.png` · Strip: `red-word-emphasis-pop-over-talking-head-v6l0s-strip.png`
- Tags: motion=[pop, scale-bloom] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: a single word in the narration needs to land hard as the emphasized beat
- Motion: Over a talking-head shot, a red emphasis word punches in at the caption line and grows: across the strip it goes from a small white caption to a bold red 'DO'/'DRINK THE WATER' set that scales up a notch and holds, like a one-word highlight stamped on the spoken phrase. The pop is quick with a slight scale-bloom past final size before settling; no slide, just an in-place punch keyed to the word being said. The rest of the frame is the presenter's hands held up, so all the designed motion lives in that single recolored, enlarged word.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.1855 · eased_energy_share=0.8066 · sparsity=0.2455 · spatial_concentration=0.593 · mov_texture=12.1879)
- Source: https://www.youtube.com/watch?v=OZuWmpv6l0s @ 0:03-0:08

### subscribe-cta-button-pop-lower-third-v6l0s
- Hero: `subscribe-cta-button-pop-lower-third-v6l0s.png` · Strip: `subscribe-cta-button-pop-lower-third-v6l0s-strip.png`
- Tags: motion=[pop, scale-bloom] · archetype=lower-third · energy=measured · mood=warm
- Use when: the end-card subscribe ask, dropping a CTA chip over a closing shot
- Motion: A green rounded 'SUBSCRIBE' chip and a small monospace tagline pop into the lower third over the closing live-action shot. Across the strip the lower caption first reads as plain white text, then in the later frames the green button snaps in beneath it at full saturation with a quick scale-bloom, settling without drift. It is an in-place CTA stamp rather than a slide-in: the button arrives as a unit, parks low-left, and holds while the footage continues behind it.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.8124 · eased_energy_share=0.9878 · sparsity=0.2814 · spatial_concentration=0.4602 · mov_texture=10.463)
- Source: https://www.youtube.com/watch?v=OZuWmpv6l0s @ 0:47-0:50

### single-bar-overshoot-vs-flag-row-y9m4
- Hero: `single-bar-overshoot-vs-flag-row-y9m4.png` · Strip: `single-bar-overshoot-vs-flag-row-y9m4-strip.png`
- Tags: motion=[count-up, overshoot, slide-in] · archetype=stat-hero · energy=punchy · mood=playful
- Use when: one value dwarfs a row of peers and the gap is the punchline
- Motion: The title 'AVERAGE TORNADOES PER YEAR' and a row of short country-flag bars hold static along the bottom while one tall green bar shoots up the right third of the frame. The bar grows fast and slightly past its mark, with a curved arrow sweeping up beside it and a value label popping in at the top as it settles. A 'BY A LOT!' caption lands at the lower-left to seal the comparison. The flag row stays put the whole time so the single hero bar carries all the motion.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.701 · eased_energy_share=0.9269 · sparsity=0.2014 · spatial_concentration=0.3795 · mov_texture=15.3642)
- Source: https://www.youtube.com/watch?v=ZyB1i6Y9_m4 @ 0:03-0:05

### map-annotation-dashed-region-to-heat-glow-y9m4
- Hero: `map-annotation-dashed-region-to-heat-glow-y9m4.png` · Strip: `map-annotation-dashed-region-to-heat-glow-y9m4-strip.png`
- Tags: motion=[draw-on, scale-bloom, morph] · archetype=map · energy=measured · mood=serious
- Use when: two regional forces are introduced in sequence to set up a cause
- Motion: A satellite map of the US holds while a dashed outline draws over the Gulf-into-plains region and a '1. WARM WET AIR' label fades in, stepped lower-third captions advancing underneath ('THIS FLOWS INTO THE PLAINS' then 'FROM THE GULF'). The first annotation then dims and a red heat glow blooms over the southwest as the label morphs to '2. WARM DRY AIR'. The camera stays locked; all the motion is the sequential reveal and the cool-to-hot color shift between the two labeled zones.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.7478 · eased_energy_share=0.9262 · sparsity=0.0067 · spatial_concentration=0.0413 · mov_texture=6.3335)
- Source: https://www.youtube.com/watch?v=ZyB1i6Y9_m4 @ 0:13-0:15

### typed-headline-into-stacked-timeline-list-s2uos
- Hero: `typed-headline-into-stacked-timeline-list-s2uos.png` · Strip: `typed-headline-into-stacked-timeline-list-s2uos-strip.png`
- Tags: motion=[typewriter, stagger, accordion-reflow] · archetype=timeline · energy=punchy · mood=serious
- Use when: a single named item resolves into the full ordered series it belongs to
- Motion: Reading left to right, a chunky outlined headline types in over a space B-roll plate: first a lone 'A', then 'ARTEMIS I', settling to 'ARTEMIS III' with a small sub-caption beneath. In the last two frames the single title collapses into a left-aligned stacked list — ARTEMIS I through V appear one row at a time top-to-bottom in a tight stagger, each new line nudging the block as it reflows. No overshoot; the type snaps in crisply and holds. The background footage drifts slowly behind the static text frame.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.1966 · eased_energy_share=0.9598 · sparsity=0.0244 · spatial_concentration=0.3072 · mov_texture=15.9133)
- Source: https://www.youtube.com/watch?v=fy6Kd0s2UOs @ 0:04-0:06

### lunar-render-camera-track-to-rocket-reveal-s2uos
- Hero: `lunar-render-camera-track-to-rocket-reveal-s2uos.png` · Strip: `lunar-render-camera-track-to-rocket-reveal-s2uos-strip.png`
- Tags: motion=[parallax-push, slide-in, mask-reveal] · archetype=map · energy=measured · mood=serious
- Use when: a rendered environment establishes the scene, then the hero object is revealed at the end of a move
- Motion: A 3D-rendered lunar surface holds across the first frames while a low rover/lander vehicle tracks across the foreground left-to-right, the camera pushing with it so the habitat dome behind shifts in parallax. A small caption sits low-left throughout. On the final frame the scene cuts/reveals to a tall rocket standing vertical on the surface, swapping the wide environment for the hero object. The motion is slow and deliberate — a steady traverse rather than a snap, settling on the rocket reveal.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.2196 · eased_energy_share=0.9879 · sparsity=0.0569 · spatial_concentration=0.5587 · mov_texture=10.4995)
- Source: https://www.youtube.com/watch?v=fy6Kd0s2UOs @ 0:44-0:47

### numbered-theory-diagram-build-aqzyi
- Hero: `numbered-theory-diagram-build-aqzyi.png` · Strip: `numbered-theory-diagram-build-aqzyi-strip.png`
- Tags: motion=[draw-on, stagger, kinetic-type] · archetype=diagram-build · energy=punchy · mood=serious
- Use when: an explainer enumerates a set of competing options before naming the one it will follow
- Motion: Opens off a talking-head frame and cuts into a dark stage where three colored teardrop/flow-line shapes draw on stacked vertically, each tagged by a count-up label '1.' '2.' '3.' that appears in step with its shape. The caption 'THERE ARE THREE BIG THEORIES' holds at the base while the numbered list stagger-reveals top to bottom. It then collapses to a single highlighted teardrop and a bold 'BIG FREEZE' title settling center-left, the rainbow flow lines tracing the shape's contour. Cadence is punctuated and quick, each label snapping in rather than easing.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=6.809 · eased_energy_share=0.9684 · sparsity=0.017 · spatial_concentration=0.2148 · mov_texture=9.9204)
- Source: https://www.youtube.com/watch?v=mD9386aqzyI @ 0:01-0:04

### giant-number-countup-then-page-peel-aqzyi
- Hero: `giant-number-countup-then-page-peel-aqzyi.png` · Strip: `giant-number-countup-then-page-peel-aqzyi-strip.png`
- Tags: motion=[count-up, scale-bloom, wipe] · archetype=kinetic-type · energy=frenetic · mood=playful
- Use when: a number balloons to an absurd magnitude to dramatize scale, then hands off to the next idea
- Motion: From a talking-head frame, a neon-green '100,000,' lands center, then explodes into a wall of stacked '000,000,000,...' digits that scale-bloom to fill the entire frame as the magnitude runs away. The oversized numeral is the whole image at peak. It resolves into a graph-paper sheet whose top corner page-peels/curls away like a torn pad page, wiping to the next 'AND ALL OF THESE THEORIES' beat. Energy is frenetic and comedic; the count-up is the punchline, the page-peel is the exit.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=7.4719 · eased_energy_share=0.7683 · sparsity=0.1699 · spatial_concentration=0.4127 · mov_texture=16.4025)
- Source: https://www.youtube.com/watch?v=mD9386aqzyI @ 0:46-0:50

### wordwise-caption-over-data-field-lightburst-aqzyi
- Hero: `wordwise-caption-over-data-field-lightburst-aqzyi.png` · Strip: `wordwise-caption-over-data-field-lightburst-aqzyi-strip.png`
- Tags: motion=[typewriter, mask-reveal, scale-bloom] · archetype=kinetic-type · energy=measured · mood=ominous
- Use when: narration builds toward a reveal over a moody textured backdrop and resolves into a glowing payoff
- Motion: A dense blue-violet cosmic-web data texture fills the frame as bold white captions reveal word-group by word-group along the bottom: 'SO RIGHT NOW' holds, then swaps to 'SCIENTISTS ARE STUDYING', each phrase mask-revealing in place rather than crawling. The textured field drifts subtly behind the type. It closes on a soft blue light-burst bloom that grows from a point and washes the frame, carrying 'THIS BRAND NEW DATA SET' into the glow. Measured, building cadence with a luminous settle.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.1012 · eased_energy_share=1 · sparsity=0.0588 · spatial_concentration=0.4293 · mov_texture=22.6268)
- Source: https://www.youtube.com/watch?v=mD9386aqzyI @ 0:53-0:56

### moon-name-typewriter-over-emerging-planet-ebnz4
- Hero: `moon-name-typewriter-over-emerging-planet-ebnz4.png` · Strip: `moon-name-typewriter-over-emerging-planet-ebnz4-strip.png`
- Tags: motion=[typewriter, mask-reveal, slide-in] · archetype=kinetic-type · energy=measured · mood=serious
- Use when: a single named subject is introduced and its one key fact lands underneath
- Motion: A big yellow-green all-caps label types on letter-by-letter across the strip ('E' to 'EU' to 'EUROPA'), holding a fixed left baseline while the moon itself emerges from behind Jupiter's limb and brightens frame-to-frame. As the name completes, the bottom caption swaps from the running 'AND THIS ONE' placeholder to the payoff line 'MIGHT ACTUALLY HAVE ALIEN LIFE'. Cadence is steady and unhurried — no overshoot, the type just accretes and settles, letting the reveal of the lit moon carry the energy.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.9853 · eased_energy_share=0.9601 · sparsity=0.1079 · spatial_concentration=0.4661 · mov_texture=6.9771)
- Source: https://www.youtube.com/watch?v=swr39JEbNz4 @ 0:07-0:10

### scale-comparison-labels-pop-over-celestial-collage-ebnz4
- Hero: `scale-comparison-labels-pop-over-celestial-collage-ebnz4.png` · Strip: `scale-comparison-labels-pop-over-celestial-collage-ebnz4-strip.png`
- Tags: motion=[pop, slide-in, settle] · archetype=collage · energy=punchy · mood=serious
- Use when: you cut from a presenter into a stack of compared items, each tagged as it appears
- Motion: After two talking-head frames the strip hard-cuts into a side-scrolling celestial comparison: full-frame planet/moon imagery (Ganymede, then a Mercury-scale body, then Io) slides through frame while a punchy green name label pops in over each one and a small 'NOT TO SCALE' tag sits pinned top-right. Each body's caption fills in along the bottom ('THIS ONE IS...') as it settles into place. The motion is a brisk horizontal march of labeled exhibits rather than a single eased entrance — each item lands hard and is gone by the next frame.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.3923 · eased_energy_share=0.9508 · sparsity=0.099 · spatial_concentration=0.4067 · mov_texture=10.5896)
- Source: https://www.youtube.com/watch?v=swr39JEbNz4 @ 0:00-0:06

### multi-line-chart-draw-on-climb-m7jxy
- Hero: `multi-line-chart-draw-on-climb-m7jxy.png` · Strip: `multi-line-chart-draw-on-climb-m7jxy-strip.png`
- Tags: motion=[draw-on, count-up, settle] · archetype=diagram-build · energy=measured · mood=serious
- Use when: two trends diverge and the gap between them is the point
- Motion: On a white card titled ELECTRIC CAR SALES, the axes hold static while two series draw on left-to-right: a red CHINA line climbs steepest and a blue USA line trails below it, both extending toward the right edge as the years fill in. The lines accelerate upward toward the latest year (2025) rather than rising linearly, so the divergence reads as the payoff, then the card settles to its full extent before the strip cuts to two presenters on stage.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=10.8117 · eased_energy_share=0.8954 · sparsity=0.0026 · spatial_concentration=0.0462 · mov_texture=23.5218)
- Source: https://www.youtube.com/watch?v=tOZAKMm7jxY @ 0:20-0:24

### kinetic-caption-over-product-render-to-logo-card-m7jxy
- Hero: `kinetic-caption-over-product-render-to-logo-card-m7jxy.png` · Strip: `kinetic-caption-over-product-render-to-logo-card-m7jxy-strip.png`
- Tags: motion=[kinetic-type, slide-in, wipe] · archetype=title-card · energy=measured · mood=serious
- Use when: a turn in the argument lands, then hands off to a named brand or entity
- Motion: A glossy black 3D-rendered Ferrari badge holds in soft studio light while the lower-third caption BUT THE THING IS types in beneath it in small caps. The badge stays fixed as the line completes, then the strip hard-cuts to a dark LUCID logo title card with the line TO MAKE AN ELECTRIC FERRARI, before cutting again to a talking-head of the Ferrari chief. The cadence is calm and deliberate, the text doing all the motion over a near-static hero render.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.7061 · eased_energy_share=0.8362 · sparsity=0.0963 · spatial_concentration=0.4596 · mov_texture=7.8736)
- Source: https://www.youtube.com/watch?v=tOZAKMm7jxY @ 0:38-0:42

### acronym-stack-pop-yellow-6n1k8
- Hero: `acronym-stack-pop-yellow-6n1k8.png` · Strip: `acronym-stack-pop-yellow-6n1k8-strip.png`
- Tags: motion=[pop, stagger, snap] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: an acronym or term gets spelled out and decoded word-by-word as the punchline
- Motion: Over the talking-head frame, bold lime-yellow words pop on one at a time: first a single 'COMPLETELY' snaps in mid-frame, then the full stack 'COMPLETELY / AUTOMATED / PUBLIC / TURING TEST TO TELL' builds line-by-line down the left, each word arriving with a hard snap rather than an ease. The stagger is roughly one word per frame and the type settles in place with no drift. The strip closes on a clean white card laying out branded logo lozenges, so the kinetic build hands off to a static reference card.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.4001 · eased_energy_share=0.6718 · sparsity=0.4875 · spatial_concentration=0.6901 · mov_texture=9.3935)
- Source: https://www.youtube.com/watch?v=xRYWj06N1k8 @ 0:08-0:12

### captcha-cursor-path-draw-on-6n1k8
- Hero: `captcha-cursor-path-draw-on-6n1k8.png` · Strip: `captcha-cursor-path-draw-on-6n1k8-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=device-mockup · energy=calm · mood=clinical
- Use when: you demonstrate a UI interaction and trace the path of a pointer to explain how it works
- Motion: On a pale graph-paper backdrop a reCAPTCHA 'I'm not a robot' widget sits center while an oversized cursor slides in from upper-left, hovers, and the checkbox cycles through its loading spinner. A dashed lime trail then draws on behind the cursor, tracing its path across the panel as captions wipe through underneath ('REGULAR MOUSE LEFT HERE' to 'BUT THIS BOX MOVED' to 'KIND OF LEFT HERE'). The cursor and dashed line move at a slow, measured pace and settle without overshoot, reading as a deliberate explainer diagram.
- Motion-metrics: energy=calm · cadence=continuous · spatial=localized · gate=continuous · src=scan
  (flow: motion_energy=0.232 · eased_energy_share=0 · sparsity=0.9598 · spatial_concentration=0.8996 · mov_texture=14.5916)
- Source: https://www.youtube.com/watch?v=xRYWj06N1k8 @ 0:25-0:28

### logo-wordmark-scale-down-dock-tcjw
- Hero: `logo-wordmark-scale-down-dock-tcjw.png` · Strip: `logo-wordmark-scale-down-dock-tcjw-strip.png`
- Tags: motion=[scale-bloom, settle, slide-in] · archetype=title-card · energy=punchy · mood=neutral
- Use when: a product or brand name is introduced before the segment about it begins
- Motion: The first frame shows the wordmark big and centered: a diamond sparkle icon left of 'Gemma 4' in blue, filling the lower-left quarter. By the second frame it has shrunk to roughly a third its size and docked to the upper-left as a persistent header, where it holds for the rest of the strip. The contraction is quick and eased into its resting spot rather than overshooting; once docked, supporting live-action B-roll rises from below into the now-cleared frame.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.2102 · eased_energy_share=0.9377 · sparsity=0 · spatial_concentration=0.2268 · mov_texture=3.2548)
- Source: https://www.youtube.com/watch?v=-01ZCTt-CJw @ 0:27-0:30

### title-card-bloom-flash-snap-tcjw
- Hero: `title-card-bloom-flash-snap-tcjw.png` · Strip: `title-card-bloom-flash-snap-tcjw-strip.png`
- Tags: motion=[scale-bloom, snap, glitch] · archetype=title-card · energy=punchy · mood=playful
- Use when: a recurring segment or chapter title card stamps in as a hard scene break
- Motion: A boxed monochrome title lockup ('THE CODE REPORT') sits crisp in frame one, then frames two through four blow out into a near-white bloom flash that washes the whole frame, with a thin red underline streaking beneath. The lockup re-resolves sharp by the final frames, snapping back to a clean black-and-white card. It is a fast over-exposure flash transition, not a smooth fade — bloom up hard, then snap back to legibility.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.5039 · eased_energy_share=0.4823 · sparsity=0.0238 · spatial_concentration=0.3227 · mov_texture=9.1751)
- Source: https://www.youtube.com/watch?v=-01ZCTt-CJw @ 0:52-0:55

### glitch-kinetic-type-datamosh-tcjw
- Hero: `glitch-kinetic-type-datamosh-tcjw.png` · Strip: `glitch-kinetic-type-datamosh-tcjw-strip.png`
- Tags: motion=[glitch, kinetic-type, snap] · archetype=kinetic-type · energy=frenetic · mood=tense
- Use when: an error state or breaking-point phrase needs to read as system failure
- Motion: The phrase 'OUT OF MEMORY' is shredded by heavy horizontal datamosh — RGB-split scanlines tear and smear the type across the first four frames over an orange substrate, so the words barely hold legibility before re-forming. The strip then hard-cuts to a clean two-line kinetic card ('MEMORY / BANDWIDTH') stacked centered on black. The glitch is the motion: torn slices slide and re-register horizontally, settling only at the cut. Frenetic, deliberately unstable, resolving into a calm stacked headline.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.4307 · eased_energy_share=0.5467 · sparsity=0.2349 · spatial_concentration=0.574 · mov_texture=11.7569)
- Source: https://www.youtube.com/watch?v=-01ZCTt-CJw @ 2:10-2:17

### glitch-flicker-title-card-8ctzy
- Hero: `glitch-flicker-title-card-8ctzy.png` · Strip: `glitch-flicker-title-card-8ctzy-strip.png`
- Tags: motion=[glitch, snap, scale-bloom] · archetype=title-card · energy=punchy · mood=playful
- Use when: a recurring segment ident slams in to mark a hard topic cut
- Motion: The strip cuts from a B-roll plate straight into a black card where a bold 'CODE REPORT' wordmark hits center-frame. Across the final frames the lockup pulses through a glitch/flicker treatment — the letters strobe and bloom brighter then settle, with a hard-edged invert flash rather than any easing. It reads as an instant snap-on title ident with no slide, the energy carried by the rapid contrast flicker and a faint scale bloom on the type as it locks.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.703 · eased_energy_share=0.8029 · sparsity=0.495 · spatial_concentration=0.5066 · mov_texture=14.6564)
- Source: https://www.youtube.com/watch?v=0pgCBV8CTZY @ 0:45-0:56

### ui-card-reveal-drawn-arrow-cta-8ctzy
- Hero: `ui-card-reveal-drawn-arrow-cta-8ctzy.png` · Strip: `ui-card-reveal-drawn-arrow-cta-8ctzy-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=device-mockup · energy=punchy · mood=neutral
- Use when: a product UI lands and a hand-drawn pointer flags the exact action to take
- Motion: A dark product card titled 'How urgent?' holds at right while a fire B-roll plate sits beside it through the early frames. Midway across the strip a chunky hand-drawn arrow draws on from upper-right and curves down to point straight at the card's red CTA button, settling with its tip parked on the control. The card itself stays steady — the motion is the marker-style arrow stroking in over a static UI — before the beat cuts to a second darker full-screen UI scene at the tail.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.583 · eased_energy_share=0.7006 · sparsity=0.5577 · spatial_concentration=0.7543 · mov_texture=13.5453)
- Source: https://www.youtube.com/watch?v=0pgCBV8CTZY @ 4:18-4:23

### benchmark-bar-chart-panel-slide-xmvwe
- Hero: `benchmark-bar-chart-panel-slide-xmvwe.png` · Strip: `benchmark-bar-chart-panel-slide-xmvwe-strip.png`
- Tags: motion=[slide-in, wipe, settle] · archetype=diagram-build · energy=punchy · mood=clinical
- Use when: a model or product wins a head-to-head benchmark and the comparison is the payoff
- Motion: A dark titled panel holds a Terminal-Bench leaderboard table whose horizontal bars draw outward, with the hero row ('Composer 2') filled solid orange against the muted white competitors. The whole panel then wipes leftward as a second comparison panel (Price / Speed scatter columns) slides in from the right to take its place, the table sliding partly off-frame at the seam. Movement is a firm left-to-right panel push rather than per-bar staggering; each chart settles flat with no overshoot, reading as a crisp data-viz cross-fade between two benchmark views.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=17.1967 · eased_energy_share=1 · sparsity=0 · spatial_concentration=0.0088 · mov_texture=16.157)
- Source: https://www.youtube.com/watch?v=JSuS-zXMVwE @ 1:16-1:18

### glitch-wipe-reveal-logotype-xmvwe
- Hero: `glitch-wipe-reveal-logotype-xmvwe.png` · Strip: `glitch-wipe-reveal-logotype-xmvwe-strip.png`
- Tags: motion=[glitch, wipe, snap] · archetype=title-card · energy=frenetic · mood=tense
- Use when: a hard cut or name-drop punches in and you want a aggressive transition into a title word
- Motion: A dark horizontally-banded field tears with datamosh/glitch noise that wipes left-to-right across the frame, scan-line bands jittering frame to frame. Out of the corruption a logotype snaps into place, resolving to the word 'BLACK SMITH' stacked in heavy condensed caps by the final frames. There is no easing or settle — the text arrives by abrupt glitch-snap, letterboxed top and bottom, giving a short, violent transition stinger rather than a smooth reveal.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.1491 · eased_energy_share=0.9637 · sparsity=0.123 · spatial_concentration=0.5465 · mov_texture=13.9163)
- Source: https://www.youtube.com/watch?v=JSuS-zXMVwE @ 4:18-4:20

### benchmark-bar-chart-fill-then-photo-snap-kpto
- Hero: `benchmark-bar-chart-fill-then-photo-snap-kpto.png` · Strip: `benchmark-bar-chart-fill-then-photo-snap-kpto-strip.png`
- Tags: motion=[wipe, settle, pop] · archetype=stat-hero · energy=punchy · mood=playful
- Use when: two competing numbers land side by side as the proof point
- Motion: Opens on a dark blurred horizontal wipe that clears to reveal a titled comparison card (SWE-bench Pro). The two labeled rows settle in with their filled bars and percentages already set (77.8% solid, 53.4% hatched), holding steady across the middle frames. On the final frame a cut-out photo snaps in from the lower-right to punctuate the higher score, landing without overshoot.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.5215 · eased_energy_share=0.9904 · sparsity=0.2897 · spatial_concentration=0.5193 · mov_texture=6.3018)
- Source: https://www.youtube.com/watch?v=d3Qq-rkp_to @ 0:05-0:07

### logo-title-card-glow-flicker-reveal-kpto
- Hero: `logo-title-card-glow-flicker-reveal-kpto.png` · Strip: `logo-title-card-glow-flicker-reveal-kpto-strip.png`
- Tags: motion=[scale-bloom, glitch, settle] · archetype=title-card · energy=frenetic · mood=playful
- Use when: a recurring segment ident slams in to open a new chapter
- Motion: From near-black the CODE REPORT wordmark blooms up inside a bright glowing frame, oversized and overexposed at the peak so the outline flares. Across the strip it flickers and contracts, the halo pumping a couple of times like a neon sign settling. By the final frame the glow has cooled and the boxed logo locks crisp and centered at rest.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.6906 · eased_energy_share=0.3473 · sparsity=0.0612 · spatial_concentration=0.3408 · mov_texture=8.533)
- Source: https://www.youtube.com/watch?v=d3Qq-rkp_to @ 1:08-1:11

### kinetic-headline-with-sweeping-arrow-annotation-g8zpu
- Hero: `kinetic-headline-with-sweeping-arrow-annotation-g8zpu.png` · Strip: `kinetic-headline-with-sweeping-arrow-annotation-g8zpu-strip.png`
- Tags: motion=[kinetic-type, marker-sweep, draw-on] · archetype=kinetic-type · energy=measured · mood=playful
- Use when: a headline term lands and a hand-drawn arrow ties it to a piece of evidence on screen
- Motion: A big two-line orange display headline (CLAUDE / CODE) sits locked on the left while a small red LEAK label and a curved hand-drawn arrow sweep on to the right, the arrow's tip arcing down to point at a file-tree panel. The headline holds steady across the strip; the energy is all in the annotation drawing on over a settled file list. By the final frames the arrow has fully landed and the layout settles before cutting away. Reads as a label-plus-pointer reveal rather than text that itself moves.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.8966 · eased_energy_share=0.809 · sparsity=0.6971 · spatial_concentration=0.7763 · mov_texture=10.625)
- Source: https://www.youtube.com/watch?v=mBHRPeg8zPU @ 0:22-0:27

### title-card-glitch-flash-bloom-g8zpu
- Hero: `title-card-glitch-flash-bloom-g8zpu.png` · Strip: `title-card-glitch-flash-bloom-g8zpu-strip.png`
- Tags: motion=[glitch, scale-bloom, snap] · archetype=title-card · energy=punchy · mood=tense
- Use when: a recurring section title slams in as a hard scene break between segments
- Motion: A boxed CODE REPORT title card builds from a faint wireframe outline, snaps to a bold filled lockup, then blows out into a near-white flash bloom that washes the whole frame before resolving back to the clean card. The arc is build, slam, overexpose, settle across roughly six frames, with a glitchy high-contrast flash at peak energy. A thin red baseline streak flickers under the card as it lands. Works as an aggressive title slam, not a soft fade.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.8291 · eased_energy_share=0.3902 · sparsity=0.0287 · spatial_concentration=0.3284 · mov_texture=8.4675)
- Source: https://www.youtube.com/watch?v=mBHRPeg8zPU @ 1:32-1:35

### strobe-flash-logo-title-card-dt9i
- Hero: `strobe-flash-logo-title-card-dt9i.png` · Strip: `strobe-flash-logo-title-card-dt9i-strip.png`
- Tags: motion=[glitch, scale-bloom, settle] · archetype=title-card · energy=frenetic · mood=playful
- Use when: a recurring segment ID slams in as a hard scene break
- Motion: A boxed two-line wordmark (CODE / REPORT) strobes in from near-black: early frames flicker the outline in, then a mid-strip white blowout floods the whole frame as the lockup scale-blooms past full size. A thin red underline streaks across at the peak. The flash decays and the mark settles to a crisp, flat, fully-legible state in the final frame. The whole build is hard-cut and punchy rather than eased, reading as a strobe-driven logo sting.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.47 · eased_energy_share=0.3944 · sparsity=0.0683 · spatial_concentration=0.3362 · mov_texture=8.6338)
- Source: https://www.youtube.com/watch?v=nxwkn9Dt9-I @ 0:52-0:56

### constellation-word-map-labels-scale-in-dt9i
- Hero: `constellation-word-map-labels-scale-in-dt9i.png` · Strip: `constellation-word-map-labels-scale-in-dt9i-strip.png`
- Tags: motion=[scale-bloom, parallax-drift, stagger] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: loosely-related concepts surface one after another across a connected field
- Motion: Capitalized association words (YELLOW, PIG, WATER, AIRPLANE) sit on a dark blue star-field network map and grow in staggered, not all at once: YELLOW dominates the left early, then PIG and WATER scale up large on the right as the field slowly parallax-drifts. Each label pops to an oversized weight before easing back, so the eye is pulled term-to-term. The underlying constellation of small ghost-words holds steady underneath, giving the scaled labels a layered depth.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.1747 · eased_energy_share=1 · sparsity=0.0078 · spatial_concentration=0.3018 · mov_texture=24.1093)
- Source: https://www.youtube.com/watch?v=nxwkn9Dt9-I @ 2:00-2:04

### title-lockup-bloom-flash-reveal-yohyk
- Hero: `title-lockup-bloom-flash-reveal-yohyk.png` · Strip: `title-lockup-bloom-flash-reveal-yohyk-strip.png`
- Tags: motion=[scale-bloom, pop, settle] · archetype=title-card · energy=frenetic · mood=playful
- Use when: a recurring segment-title lockup slams in to open a new section
- Motion: A boxed two-line wordmark snaps onto a black field, then mid-strip a hard white over-exposed bloom floods the whole lockup outward — the glow blows past the box edges before collapsing back. By the final frame the type re-settles crisp and legible with a thin red underline ticking in beneath. The flash is the whole gesture: instant on, blinding overshoot, fast settle to the clean card.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.8867 · eased_energy_share=0.9388 · sparsity=0.0304 · spatial_concentration=0.3223 · mov_texture=9.183)
- Source: https://www.youtube.com/watch?v=o7NYXvYohYk @ 1:13-1:16

### logo-glitch-blur-to-sharp-yohyk
- Hero: `logo-glitch-blur-to-sharp-yohyk.png` · Strip: `logo-glitch-blur-to-sharp-yohyk-strip.png`
- Tags: motion=[blur-rack, glitch, snap] · archetype=title-card · energy=measured · mood=neutral
- Use when: a brand or product logo resolves into focus as it is named
- Motion: The wordmark starts as a smeared, horizontally torn glitch over a dark motion-blurred background, the letters barely readable. Across the strip the smear racks toward focus — the torn scanline displacement settles and the glyphs harden — until the final frame lands a clean, sharp logo. It reads as a blur-rack with glitch displacement resolving to a hard snap, no bounce, just a decisive focus-pull.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.1601 · eased_energy_share=0.9761 · sparsity=0.3407 · spatial_concentration=0.5867 · mov_texture=19.7641)
- Source: https://www.youtube.com/watch?v=o7NYXvYohYk @ 4:04-4:06

### glitch-bloom-logo-badge-settle-vo2q
- Hero: `glitch-bloom-logo-badge-settle-vo2q.png` · Strip: `glitch-bloom-logo-badge-settle-vo2q-strip.png`
- Tags: motion=[glitch, scale-bloom, settle] · archetype=title-card · energy=frenetic · mood=playful
- Use when: a recurring segment badge slams in to announce a new section
- Motion: A small line-icon flickers in on black, then the CODE REPORT wordmark detonates into a blown-out, motion-blurred bloom that fills the frame for two to three frames. The overexposed glow collapses inward as the type snaps back to crisp scale, resolving into a clean two-line badge (CODE / REPORT) by the final frame. A thin red underline sweeps along the baseline as it settles. Fast, percussive, no camera move.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.5372 · eased_energy_share=0.5406 · sparsity=0.0173 · spatial_concentration=0.3209 · mov_texture=8.9381)
- Source: https://www.youtube.com/watch?v=piah4fV_o2Q @ 0:48-0:50

### paired-logo-connector-blur-rack-reveal-vo2q
- Hero: `paired-logo-connector-blur-rack-reveal-vo2q.png` · Strip: `paired-logo-connector-blur-rack-reveal-vo2q-strip.png`
- Tags: motion=[slide-in, blur-rack, settle] · archetype=collage · energy=punchy · mood=playful
- Use when: two named things get linked into a before/after or A-pipes-to-B relationship
- Motion: The PHP logo holds alone on black at frame one. The word 'script' types in beneath it, then a blue pushpin/funnel connector slides in from the left to bridge toward the right edge. Simultaneously the WordPress mark racks from a soft out-of-focus blur into sharp focus as it arrives at right. By the last frame all three elements sit settled in a clean left-to-right chain (PHP-script -> connector -> WordPress). No camera move; the reveal is carried by the slide and the focus rack.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.2874 · eased_energy_share=0.8648 · sparsity=0.4237 · spatial_concentration=0.5914 · mov_texture=5.6899)
- Source: https://www.youtube.com/watch?v=piah4fV_o2Q @ 1:40-1:43

### logo-titlecard-glow-bloom-lcrvs
- Hero: `logo-titlecard-glow-bloom-lcrvs.png` · Strip: `logo-titlecard-glow-bloom-lcrvs-strip.png`
- Tags: motion=[scale-bloom, pop, settle] · archetype=title-card · energy=punchy · mood=playful
- Use when: a segment-branding bumper punches in to announce a recurring section
- Motion: Black frame; a small boxed wordmark snaps in tiny at left, then the full 'THE CODE REPORT' lockup scales up and over-brightens into a hot white bloom that washes the whole frame at the strip's midpoint. The glow then collapses back as the outlined badge resolves crisp and centered, with a thin red underline settling beneath it. It reads as a hard pop-in chased by a bloom flash that decays to a clean held logo.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.8513 · eased_energy_share=0.3904 · sparsity=0.0246 · spatial_concentration=0.3195 · mov_texture=9.2982)
- Source: https://www.youtube.com/watch?v=vd14EElCRvs @ 1:07-1:10

### reflow-list-stack-reveal-slam-label-lcrvs
- Hero: `reflow-list-stack-reveal-slam-label-lcrvs.png` · Strip: `reflow-list-stack-reveal-slam-label-lcrvs-strip.png`
- Tags: motion=[slide-in, stagger, snap] · archetype=kinetic-type · energy=frenetic · mood=playful
- Use when: a punchline term lands while a list of API/method names stacks up as the receipt
- Motion: Opens on a green angled 'KINEMATIC TYPOGRAPHY / PRETEXT' slab label skewed over dim body text, then cuts to a right-aligned monospace stack of method names (getBoundingClientRect, clientWidth, offsetWidth, scrollHeight...) that builds top-to-bottom. A red angled 'FORCE REFLOW' slab slams in from the left mid-strip and snaps to rest beside the list while the names keep stacking. Motion is fast and punctuated, the slab labels arriving with a hard skewed snap rather than an eased glide.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=10.8796 · eased_energy_share=0.9722 · sparsity=0 · spatial_concentration=0.0248 · mov_texture=11.2418)
- Source: https://www.youtube.com/watch?v=vd14EElCRvs @ 2:28-2:30

### angled-slam-label-then-arrow-annotation-lcrvs
- Hero: `angled-slam-label-then-arrow-annotation-lcrvs.png` · Strip: `angled-slam-label-then-arrow-annotation-lcrvs-strip.png`
- Tags: motion=[snap, pop, draw-on] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: a key term slams over a screen-grab, then a hand-drawn arrow points to the one thing to watch
- Motion: A red angled 'VIRTUAL LIST' slab label snaps in over a dim chat screenshot and holds, jittering slightly in skew across frames. In the final frame it drops away and a hand-scrawled white arrow draws on toward a shrunken UI panel at right, captioned 'only render this'. The cadence is a hard label snap-and-hold followed by a quick sketch arrow that redirects the eye to the highlighted region.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.7934 · eased_energy_share=0.851 · sparsity=0.2323 · spatial_concentration=0.6133 · mov_texture=4.0998)
- Source: https://www.youtube.com/watch?v=vd14EElCRvs @ 2:05-2:07

### glitch-flare-logo-badge-snap-k0mns
- Hero: `glitch-flare-logo-badge-snap-k0mns.png` · Strip: `glitch-flare-logo-badge-snap-k0mns-strip.png`
- Tags: motion=[glitch, scale-bloom, snap] · archetype=title-card · energy=frenetic · mood=playful
- Use when: a recurring segment ident slams in to announce a new section
- Motion: An outlined wireframe box flickers in at left, then the CODE REPORT badge rattles and grows across the next frames with a hard light-bloom that blows the whole frame near-white at peak. The flare collapses and the badge settles as a clean filled lockup with a thin red baseline. Pure glitch-and-flare ident energy, no easing in or out — it punches in and locks.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=6.7282 · eased_energy_share=0.8742 · sparsity=0.0186 · spatial_concentration=0.3193 · mov_texture=9.0668)
- Source: https://www.youtube.com/watch?v=wfeiCZK0mNs @ 0:50-0:53

### icon-collage-swap-price-flip-k0mns
- Hero: `icon-collage-swap-price-flip-k0mns.png` · Strip: `icon-collage-swap-price-flip-k0mns-strip.png`
- Tags: motion=[pop, slide-in, snap] · archetype=collage · energy=punchy · mood=playful
- Use when: a value comparison lands — cheap option versus expensive option side by side
- Motion: A cluster pops on together left of frame: a red mascot, a bold $0 price, a constellation of product logos, and a Mac mini held in a hand. The cluster clears and the frame cuts to a second arrangement — a glossy iOS icon, a dark device, a $$$ tag, and a burst icon — each element snapping into its slot rather than easing. The motion is a staccato collage swap, two priced states traded fast with no settle drift.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.0288 · eased_energy_share=0.9817 · sparsity=0.0255 · spatial_concentration=0.4219 · mov_texture=9.968)
- Source: https://www.youtube.com/watch?v=wfeiCZK0mNs @ 1:41-1:44

### labeled-nodes-dashed-arc-draw-on-k0mns
- Hero: `labeled-nodes-dashed-arc-draw-on-k0mns.png` · Strip: `labeled-nodes-dashed-arc-draw-on-k0mns-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=diagram-build · energy=measured · mood=serious
- Use when: a concept gets framed as a set of named parts encircled by one binding idea
- Motion: A source screenshot holds top-left while three red-outlined oval nodes — PRIVATE DATA, UNTRUSTED CONTENT, EXTERNAL COMMUNICATION — line up across the lower band. The screenshot then drops away and a dashed blue arc sweeps in to lasso the three nodes as the words 'persistent memory' fade up beneath them, brightening from ghost-grey to solid white as the arc closes. It settles into a stable encircled-trio diagram, the loop reading as a containing boundary drawn around the parts.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.3134 · eased_energy_share=0.9297 · sparsity=0.3645 · spatial_concentration=0.3018 · mov_texture=10.8054)
- Source: https://www.youtube.com/watch?v=wfeiCZK0mNs @ 2:01-2:03

### pixel-block-logo-assemble-stagger-xlvss
- Hero: `pixel-block-logo-assemble-stagger-xlvss.png` · Strip: `pixel-block-logo-assemble-stagger-xlvss-strip.png`
- Tags: motion=[stagger, slide-in, settle] · archetype=title-card · energy=punchy · mood=playful
- Use when: a brand mark or title assembles itself piece by piece at the cold open
- Motion: Green and white square blocks drop in one cluster at a time against a near-black field, building a tetromino-like logo from the lower-left upward. Each frame adds another stacked group, so the form grows by stepped increments rather than a single move, with the blocks snapping to a grid with no overshoot. By the last two frames the field has flipped to a white card and the assembled mark settles into place with a small wordmark fading in beneath it.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.5317 · eased_energy_share=0.9398 · sparsity=0.0011 · spatial_concentration=0.3444 · mov_texture=2.8445)
- Source: https://www.youtube.com/watch?v=Q2KxTcXlvss @ 0:00-0:02

### quiz-option-select-correct-card-pop-xlvss
- Hero: `quiz-option-select-correct-card-pop-xlvss.png` · Strip: `quiz-option-select-correct-card-pop-xlvss-strip.png`
- Tags: motion=[snap, pop, mask-reveal] · archetype=checklist · energy=punchy · mood=triumphant
- Use when: a choice is committed and the answer is confirmed as the payoff
- Motion: A multiple-choice list sits with a cursor hovering the options, then the top radio button snaps to a filled selected state with its row highlighting in a tinted pill. Immediately after, the frame cuts to a full white card where a chevron logo and a bold 'Correct!' headline pop in together. The closing frame reveals a parabola-and-line function graph drawing in on an axis, so the confirmation hands off to the underlying math visual.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.7949 · eased_energy_share=0.8981 · sparsity=0.0003 · spatial_concentration=0.1886 · mov_texture=6.7062)
- Source: https://www.youtube.com/watch?v=Q2KxTcXlvss @ 6:43-6:47

### vector-triangle-rocket-path-draw-xlvss
- Hero: `vector-triangle-rocket-path-draw-xlvss.png` · Strip: `vector-triangle-rocket-path-draw-xlvss-strip.png`
- Tags: motion=[draw-on, slide-in, pop] · archetype=diagram-build · energy=measured · mood=warm
- Use when: a relationship is demonstrated by animating an object along a constructed diagram
- Motion: A titled 'Subtracting Vectors' card holds a vector triangle — labelled white arrows from a planet to a rocket to a UFO — then the explanatory chrome drops away to leave the diagram on black. A rocket flies along the resultant edge trailing an orange exhaust streak, the traversed leg recolors to red as it goes, and the motion ends on a small burst of particles as the rocket reaches the far corner. The build is steady and deliberate, the path drawing on left-to-right rather than snapping.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.4605 · eased_energy_share=0.9841 · sparsity=0.0196 · spatial_concentration=0.2887 · mov_texture=13.0843)
- Source: https://www.youtube.com/watch?v=Q2KxTcXlvss @ 6:53-6:55

### ui-slider-drag-into-bar-chart-reveal-hgp5y
- Hero: `ui-slider-drag-into-bar-chart-reveal-hgp5y.png` · Strip: `ui-slider-drag-into-bar-chart-reveal-hgp5y-strip.png`
- Tags: motion=[slide-in, snap, draw-on] · archetype=device-mockup · energy=measured · mood=clinical
- Use when: a UI interaction resolves into the data it produces — input handled, then the result chart appears
- Motion: A phone-style app card holds a 'Correlation' slider reading -1.0; across the first frames the blue handle stays pinned at the left rail while a green cursor blob hops down to the dark 'Check' button, which reshapes from a wide pill to a tighter rounded capsule as it is pressed. The card content then cuts away and the final frame snaps to a clean bar chart — five labeled bars (TX, WA, FL, CA, NY) drawing up to different heights with axis ticks, under Bar/Pie toggle tabs. Measured, deliberate cadence: one interaction beat, then the result reveal, no overshoot.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=6.2043 · eased_energy_share=0.9464 · sparsity=0.0003 · spatial_concentration=0.4226 · mov_texture=14.6492)
- Source: https://www.youtube.com/watch?v=RoW5E-HGP5Y @ 6:12-6:14

### hand-drawn-arrow-callout-label-sweep-lwfom
- Hero: `hand-drawn-arrow-callout-label-sweep-lwfom.png` · Strip: `hand-drawn-arrow-callout-label-sweep-lwfom-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=lower-third · energy=measured · mood=playful
- Use when: a meme or B-roll shot needs a term named and pointed at as the punchline lands
- Motion: Across the strip a hand-drawn curved arrow builds stroke-by-stroke from upper-right down toward the subject, and an italic underlined callout label ('Reservoir sampling') slides in along the arrow's tail, settling pinned to the lower-right corner. The arrow draws on first, the label arrives a beat behind it, and both hold without overshoot once placed. The underlying clip keeps playing live underneath, so the annotation reads as a static designed overlay laid over moving footage rather than a self-contained scene.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.0629 · eased_energy_share=0.9628 · sparsity=0.2635 · spatial_concentration=0.5834 · mov_texture=15.4719)
- Source: https://www.youtube.com/watch?v=9xnbhmlwFOM @ 1:28-1:33

### draw-on-arrow-points-to-pixel-card-ffw1w
- Hero: `draw-on-arrow-points-to-pixel-card-ffw1w.png` · Strip: `draw-on-arrow-points-to-pixel-card-ffw1w-strip.png`
- Tags: motion=[draw-on, kinetic-type] · archetype=kinetic-type · energy=measured · mood=playful
- Use when: a key term gets defined and a hand-drawn pointer ties the words to a concrete example
- Motion: A line of caption type sits in the upper-left with one word color-accented; a hand-drawn arrow curves down from it toward a pixel-art card on a starfield. Across the strip the arrow draws on stroke-by-stroke from the text toward the graphic, settling as the pointer that anchors the phrase to the example. The text holds while the arrow does the work, then a second line fades up on the right to continue the thought. Calm, deliberate cadence with no overshoot — the draw-on is the only moving element.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.7795 · eased_energy_share=0.8763 · sparsity=0.7458 · spatial_concentration=0.7589 · mov_texture=22.2493)
- Source: https://www.youtube.com/watch?v=BpIYoaFfW1w @ 3:06-3:10

### logo-build-line-to-card-to-glyph-pop-ffw1w
- Hero: `logo-build-line-to-card-to-glyph-pop-ffw1w.png` · Strip: `logo-build-line-to-card-to-glyph-pop-ffw1w-strip.png`
- Tags: motion=[draw-on, pop, scale-bloom] · archetype=title-card · energy=measured · mood=triumphant
- Use when: a brand or product logo assembles itself as the payoff at the end of a section
- Motion: On a black starfield, italic caption text reads out first, then clears. A thin purple underline draws on horizontally across center. A purple card pops in above that line with a white glyph already inside, then the whole card scale-blooms larger toward the final logo lockup. The build is sequential and staged — line, then card, then growth — each step snapping in cleanly with a small pop rather than a long ease, landing on the resolved brand mark.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.704 · eased_energy_share=0.8893 · sparsity=0.742 · spatial_concentration=0.7822 · mov_texture=9.1812)
- Source: https://www.youtube.com/watch?v=BpIYoaFfW1w @ 3:24-3:27

### ui-modal-crossfade-screen-swap-ffw1w
- Hero: `ui-modal-crossfade-screen-swap-ffw1w.png` · Strip: `ui-modal-crossfade-screen-swap-ffw1w-strip.png`
- Tags: motion=[mask-reveal, blur-rack, slide-in] · archetype=device-mockup · energy=measured · mood=neutral
- Use when: a product UI step finishes and the view transitions to the next screen in a flow
- Motion: A centered app modal ('Connect to a messaging app' with a list of integrations and a CTA button) sits crisp on a dark starfield. Across the strip the modal holds, then the whole frame racks out of focus and dims as a new lighter screen wipes in over the top from the right. The outgoing modal blurs and recedes while the incoming panel slides forward, a clean designed screen-to-screen swap rather than a hard cut. Measured pacing, single transition event.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=1.2706 · eased_energy_share=0.9455 · sparsity=0.6648 · spatial_concentration=0.675 · mov_texture=12.3154)
- Source: https://www.youtube.com/watch?v=BpIYoaFfW1w @ 3:35-3:38

### logo-particle-dissolve-wipe-iwjys
- Hero: `logo-particle-dissolve-wipe-iwjys.png` · Strip: `logo-particle-dissolve-wipe-iwjys-strip.png`
- Tags: motion=[particle, wipe, mask-reveal] · archetype=title-card · energy=punchy · mood=playful
- Use when: a sponsor or section card exits and hands off to the next scene
- Motion: Opens on a screen-recording card with a bright green DataCamp logo locked centered over the muted UI. The logo holds for the first two frames, then a field of pale-blue rounded particles erupts from frame-right and sweeps left as a mask, eating the card edge-first. By the final frame the particles have engulfed the whole frame, dissolving the logo entirely. The wipe is fast and gappy rather than a clean edge — the particle front advances irregularly, reading as an energetic dissolve transition into the next scene.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.7293 · eased_energy_share=0.8566 · sparsity=0.6346 · spatial_concentration=0.7126 · mov_texture=14.0794)
- Source: https://www.youtube.com/watch?v=E6XEtEIWJYs @ 3:49-3:55

### sdk-card-grid-parallax-pan-to-mockup-x0rro
- Hero: `sdk-card-grid-parallax-pan-to-mockup-x0rro.png` · Strip: `sdk-card-grid-parallax-pan-to-mockup-x0rro-strip.png`
- Tags: motion=[parallax-push, slide-in, settle] · archetype=collage · energy=punchy · mood=neutral
- Use when: an ecosystem of options or integrations is surveyed before zooming to one concrete product
- Motion: A grid of labeled feature cards (React SDK, iOS SDK, Android SDK, Flutter SDK, Unity, Angular, JS client) sits on a dark starfield and the camera parallax-pushes across it left-to-right, the rows sliding past as fresh cards keep entering at the right edge. The pan holds a steady, even velocity rather than overshooting, treating the whole grid as one continuous surface. On the final frame it lands on a bright device mockup of a chat UI floating against the same starfield, snapping the survey down to a single concrete product. The cards stay legible throughout; motion is the camera, not the cards.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.4195 · eased_energy_share=0.5682 · sparsity=0.1013 · spatial_concentration=0.2772 · mov_texture=12.7236)
- Source: https://www.youtube.com/watch?v=ff9JoLX0RRo @ 3:13-3:16

### ui-panel-build-then-marker-highlight-stat-ymaug
- Hero: `ui-panel-build-then-marker-highlight-stat-ymaug.png` · Strip: `ui-panel-build-then-marker-highlight-stat-ymaug-strip.png`
- Tags: motion=[mask-reveal, marker-sweep, kinetic-type] · archetype=code-reveal · energy=measured · mood=neutral
- Use when: a tooled interface fills in, then a count payoff gets underlined as the takeaway
- Motion: A dark IDE/GitHub-style panel populates left-to-right: the sidebar and content rows reveal row by row across the first two frames, settling into a full populated layout. Then the frame swings to a kinetic line where the headline figure '26 projects that matter' lands with a green marker-sweep underline drawn beneath the number. Motion is calm and deliberate — UI fills first, type and highlight resolve second, no overshoot, each element holding once settled.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.9898 · eased_energy_share=0.8675 · sparsity=0.6047 · spatial_concentration=0.6424 · mov_texture=9.0842)
- Source: https://www.youtube.com/watch?v=n5KcJQYmaug @ 3:06-3:16

### promo-card-particle-dissolve-wipe-ymaug
- Hero: `promo-card-particle-dissolve-wipe-ymaug.png` · Strip: `promo-card-particle-dissolve-wipe-ymaug-strip.png`
- Tags: motion=[particle, wipe, mask-reveal] · archetype=title-card · energy=punchy · mood=playful
- Use when: a discount or promo card clears off-screen via a textured dissolve into the next scene
- Motion: A '40% OFF' offer card holds for the first three frames while a cloud of small icy-blue rounded particles floods up from the bottom edge, building denser frame over frame. By the fourth frame the particle field has overtaken the entire panel as a full-frame mask, then thins back out toward black across the last two frames — a particle wipe that both covers the card and reveals what's behind it. The fill is fast and granular, the clear is the inverse, used as a designed scene transition rather than a settle.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.8361 · eased_energy_share=0.9004 · sparsity=0.1249 · spatial_concentration=0.3174 · mov_texture=16.5615)
- Source: https://www.youtube.com/watch?v=n5KcJQYmaug @ 3:34-3:36

### icon-cluster-bloom-over-hero-figure-673fa
- Hero: `icon-cluster-bloom-over-hero-figure-673fa.png` · Strip: `icon-cluster-bloom-over-hero-figure-673fa-strip.png`
- Tags: motion=[scale-bloom, pop, settle] · archetype=collage · energy=punchy · mood=playful
- Use when: a concept's pieces all crowd in at once to make a single overwhelming idea land
- Motion: Opening on a near-empty dark frame, a flat-illustrated bearded figure at a laptop fades up under a warm orange backlight arc, and a cluster of themed icons blooms above and around the head in a tight burst. Padlocks, chat bubbles, a shield, and orange '*' marks scale up from small to full size with a slight pop, the stack of locks growing tallest by the final frames. Everything settles into a packed symmetrical halo around the figure rather than dispersing, so the motion reads as accumulation.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.6742 · eased_energy_share=0.9601 · sparsity=0.2121 · spatial_concentration=0.4367 · mov_texture=10.8892)
- Source: https://www.youtube.com/watch?v=u_SJcg673fA @ 0:34-0:36

### particle-cloud-disperse-thin-out-673fa
- Hero: `particle-cloud-disperse-thin-out-673fa.png` · Strip: `particle-cloud-disperse-thin-out-673fa-strip.png`
- Tags: motion=[particle, parallax-drift] · archetype=title-card · energy=frenetic · mood=tense
- Use when: a dense mass breaks apart and clears the frame as a transition out of an intense moment
- Motion: A solid full-frame wall of glowing blue-white particles (with a dark smoke wash on the left) begins packed edge to edge, then thins rapidly left to right across the strip as the particles drift apart and clear toward black. Each frame is noticeably sparser than the last, the cluster dissolving from a dense field to scattered specks. The dispersal reads as a fast, energetic clearing-out transition with no settle — it keeps thinning to near-empty.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=7.0883 · eased_energy_share=0.9318 · sparsity=0.0092 · spatial_concentration=0.2682 · mov_texture=26.0248)
- Source: https://www.youtube.com/watch?v=u_SJcg673fA @ 3:44-3:46

### cell-particle-flood-wipe-kinetic-title-cugvq
- Hero: `cell-particle-flood-wipe-kinetic-title-cugvq.png` · Strip: `cell-particle-flood-wipe-kinetic-title-cugvq-strip.png`
- Tags: motion=[particle, wipe, kinetic-type] · archetype=title-card · energy=frenetic · mood=triumphant
- Use when: a defiant one-line claim lands and you hard-cut to the next section
- Motion: Opens on a black card with the kinetic title 'Coding is not dead', the words 'not dead' underlined in yellow as the emphasis tell. A dense field of cyan-outlined cells/bubbles then floods in from the bottom-left corner on a fast diagonal, swallowing the title word-by-word until it fully packs the frame in the last frames. The fill is frenetic and near-instant across the strip, reading as a particle wipe-on that buries the scene rather than a soft crossfade.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.8391 · eased_energy_share=0.926 · sparsity=0.3896 · spatial_concentration=0.3391 · mov_texture=27.7527)
- Source: https://www.youtube.com/watch?v=wbU5CWCuGvQ @ 3:26-3:28

### whiteboard-sketch-then-query-text-reveal-tkfyw
- Hero: `whiteboard-sketch-then-query-text-reveal-tkfyw.png` · Strip: `whiteboard-sketch-then-query-text-reveal-tkfyw-strip.png`
- Tags: motion=[draw-on, kinetic-type, slide-in] · archetype=diagram-build · energy=calm · mood=neutral
- Use when: a posed question or query is introduced and a hand-sketched diagram begins assembling alongside it
- Motion: Opens on two hand-drawn stick figures lower-left with an arrow gesture between them. By the second frame the camera/composition has cut up to the top band, where a sketched arrow and tree-icon glyph draw on at top-left and the line 'Hey database, show me all orders from customers in US' fades up top-right as faint ghost type. The remaining frames hold that arrangement nearly static, so the motion is a single quick draw-on plus text fade-in that settles immediately with no overshoot — a calm, punctuated whiteboard reveal.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.3297 · eased_energy_share=0.9585 · sparsity=0.7728 · spatial_concentration=0.4531 · mov_texture=3.7926)
- Source: https://www.youtube.com/watch?v=B5UBO2tKfyw @ 0:30-0:33

### character-react-over-flag-collage-build-tkfyw
- Hero: `character-react-over-flag-collage-build-tkfyw.png` · Strip: `character-react-over-flag-collage-build-tkfyw-strip.png`
- Tags: motion=[pop, settle, mask-reveal] · archetype=collage · energy=measured · mood=playful
- Use when: a lively reaction lands as a dense grid of items or logos fills a panel, then clears for the next scene
- Motion: A hand-drawn stick figure on the left swings through energetic poses (arms thrown up, then crouched mid-action) while a database/tree icon sits centered up top with an arrow pointing down into a screen panel. Inside that panel a dense collage of country flags and app icons is already filled and holds across the first four frames. In the last two frames the collage and figure clear out and a faint server-rack glyph ghosts in center-left, reading as a wipe-out transition into the next beat. Overall measured and playful — character pop plus a steady icon-grid hold resolving into a soft scene change.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.4762 · eased_energy_share=0.9768 · sparsity=0.6485 · spatial_concentration=0.5516 · mov_texture=6.7236)
- Source: https://www.youtube.com/watch?v=B5UBO2tKfyw @ 4:30-4:32

### html-code-panel-typewriter-build-n5diy
- Hero: `html-code-panel-typewriter-build-n5diy.png` · Strip: `html-code-panel-typewriter-build-n5diy-strip.png`
- Tags: motion=[typewriter, draw-on] · archetype=code-reveal · energy=calm · mood=clinical
- Use when: source code or markup assembles line by line as a concept is explained
- Motion: A dark code panel sits to the right of an otherwise static explainer layout (newspaper CLASSIFIEDS crop, 3D building render) and types out an HTML document line by line. Reading left-to-right the panel advances <!DOCTYPE html> first, then opens <html><head>, adds <title>, closes the head and opens <body>, and finally lands on a <form method="post"> line — each frame holding one more line than the last. The panel carries a slight perspective tilt that stays put; only the text grows, in a steady measured cadence with no overshoot, so the structure of the document reveals itself top-down.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.3076 · eased_energy_share=0.3019 · sparsity=0.8519 · spatial_concentration=0.834 · mov_texture=14.3961)
- Source: https://www.youtube.com/watch?v=NSfE0BN5DIY @ 4:47-4:49

### whiteboard-type-on-phrase-with-hand-drawn-figure-lkss
- Hero: `whiteboard-type-on-phrase-with-hand-drawn-figure-lkss.png` · Strip: `whiteboard-type-on-phrase-with-hand-drawn-figure-lkss-strip.png`
- Tags: motion=[typewriter, draw-on, slide-in] · archetype=kinetic-type · energy=measured · mood=playful
- Use when: a narrated phrase lands as a labelled idea while a hand-drawn character reacts to it
- Motion: Opens on an empty whiteboard. A black hand-drawn label types on left-to-right, settling first as "big misunderstanding" while a sketched stick figure draws on beneath it in a wide shrug pose. The line then extends with the trailing word "here" appended on the same typewriter cadence, no overshoot, each word snapping in place at its final position. The beat closes by cutting to a fresh icon scene where a blue webhook glyph and an "API" gear flank the figure, joined by a short red curved arrow sweeping between them.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.6125 · eased_energy_share=0.9903 · sparsity=0.3087 · spatial_concentration=0.4274 · mov_texture=10.9314)
- Source: https://www.youtube.com/watch?v=T6XyrW-LKss @ 2:10-2:12

### linked-list-node-chain-builds-s45yu
- Hero: `linked-list-node-chain-builds-s45yu.png` · Strip: `linked-list-node-chain-builds-s45yu-strip.png`
- Tags: motion=[mask-reveal, pop, draw-on] · archetype=diagram-build · energy=measured · mood=neutral
- Use when: an abstract concept resolves into its concrete structure as the payoff
- Motion: The board opens with a line of body text that wipes away left-to-right across the first frames, clearing the stage. Then a chain of rounded letter-nodes (L, I, N, K, E, D) pops in colored boxes, each linked to the next by short hand-drawn arrows, assembling the linked-list diagram in the final frame. The nodes settle in a loose two-row zigzag rather than a straight line, reading as a built chain rather than a static graphic.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.5182 · eased_energy_share=0.9919 · sparsity=0.6226 · spatial_concentration=0.6124 · mov_texture=6.1253)
- Source: https://www.youtube.com/watch?v=YeWKYVS45yU @ 0:32-0:34

### scene-scale-out-shrink-transition-s45yu
- Hero: `scene-scale-out-shrink-transition-s45yu.png` · Strip: `scene-scale-out-shrink-transition-s45yu-strip.png`
- Tags: motion=[settle, parallax-push] · archetype=title-card · energy=measured · mood=neutral
- Use when: one section closes and the frame pulls back to hand off to the next beat
- Motion: The full Heap scene — caption block, the pink illustrated figure at a screen, and a bold red 'Importance' word — holds at full size for the first frames, then scales down together toward frame center as a single group across the back half of the strip. It is a uniform zoom-out transition, not an element animation: everything recedes in lockstep, leaving a small cluster mid-frame as the scene retires.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.7123 · eased_energy_share=0.949 · sparsity=0.4576 · spatial_concentration=0.5112 · mov_texture=7.4401)
- Source: https://www.youtube.com/watch?v=YeWKYVS45yU @ 2:50-2:52

### data-structure-icon-grid-collage-s45yu
- Hero: `data-structure-icon-grid-collage-s45yu.png` · Strip: `data-structure-icon-grid-collage-s45yu-strip.png`
- Tags: motion=[mask-reveal, settle] · archetype=collage · energy=measured · mood=neutral
- Use when: a recap fans the whole topic set out at once as an overview grid
- Motion: Opens on a localized Heap detail — 'Top Node' and 'Lower Node' ovals with a magnifying-glass icon hovering the lower one. The detail and presenter fade out across the middle frames, then the final frame snaps to a full 3x3 collage of labeled doodle icons (Array, Linked List, Stack, Queue, Hash Table, Tree, Heap, Graph) laid out as an overview grid. The transition is a clean swap from one focused element to the populated index grid.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.3011 · eased_energy_share=0.9045 · sparsity=0.7982 · spatial_concentration=0.7483 · mov_texture=9.1097)
- Source: https://www.youtube.com/watch?v=YeWKYVS45yU @ 2:53-2:56

### whiteboard-logo-arrow-callout-reflow-ifoog
- Hero: `whiteboard-logo-arrow-callout-reflow-ifoog.png` · Strip: `whiteboard-logo-arrow-callout-reflow-ifoog-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=diagram-build · energy=measured · mood=playful
- Use when: a named concept is introduced and annotated with a hand-drawn callout before clearing for the next point
- Motion: A whiteboard-explainer scene anchored by a 'React' title and logo top-center. A large React atom logo sits left while a hand-drawn curved arrow draws on pointing to the callout 'It was created by facebook in 2013', with 'Completely change' plus a heart-eyes emoji and an app-icon cluster below. Reading left-to-right the React logo and app cluster shrink and exit while the curved arrow persists and the text labels reflow smaller and recenter, settling into a cleaner state — a measured, marker-style reveal-then-clear transition rather than a snappy single move.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.8261 · eased_energy_share=0.9821 · sparsity=0.6929 · spatial_concentration=0.722 · mov_texture=8.2353)
- Source: https://www.youtube.com/watch?v=rd5VilifoOg @ 0:15-0:17

### low-poly-render-camera-push-to-pip-wue78
- Hero: `low-poly-render-camera-push-to-pip-wue78.png` · Strip: `low-poly-render-camera-push-to-pip-wue78-strip.png`
- Tags: motion=[camera-orbit, parallax-push, scale-bloom] · archetype=device-mockup · energy=frenetic · mood=playful
- Use when: a 3D/game-render moment lands, then collapses into an inset to hand off to the next scene
- Motion: A low-poly rendered character sits on a banked race-track as the camera pushes and orbits in: frame 1 is a wide flat ground plane, frames 2-4 swing the horizon and bank the track hard so the curve sweeps diagonally across the frame, reading as a fast parallax push around the subject. In the last two frames the entire scene scales down and parks into a small picture-in-picture window in the upper-left over black, an abrupt full-frame-to-inset shrink that doubles as a scene-handoff transition. The camera move is loose and energetic rather than eased to a clean stop.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=7.2718 · eased_energy_share=0.9509 · sparsity=0.2045 · spatial_concentration=0.5211 · mov_texture=8.0358)
- Source: https://www.youtube.com/watch?v=0mpkIAwUe78 @ 2:38-2:43

### lesson-card-collage-with-rgb-colorwheel-wue78
- Hero: `lesson-card-collage-with-rgb-colorwheel-wue78.png` · Strip: `lesson-card-collage-with-rgb-colorwheel-wue78-strip.png`
- Tags: motion=[pop, slide-in, mask-reveal] · archetype=collage · energy=punchy · mood=playful
- Use when: a rapid montage of distinct concept cards sells a sequence of ideas, each landing with its own hero graphic
- Motion: A series of clean light-mode lesson cards cut through quickly, each pairing a headline with its own popped-in hero graphic: 'The While Loop' lands with a green rounded-diamond loop badge that pops over the card, then an isometric maze device mock fades up, then a dark terminal block with 'for count from 1 to 10' wipes in, then a 'Thinking with Graphs' node-link diagram, closing on a 'Coloring with Numbers' RGB color wheel whose R/G/B value chips count along at the bottom. Each card holds briefly then cuts; the motion is in the per-card hero pop and the cursor hovering live UI, giving a punchy walkthrough cadence rather than one continuous move.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.2814 · eased_energy_share=0.961 · sparsity=0.008 · spatial_concentration=0.2661 · mov_texture=7.3402)
- Source: https://www.youtube.com/watch?v=0mpkIAwUe78 @ 4:05-4:16

### device-mockup-zoom-with-block-code-build-wue78
- Hero: `device-mockup-zoom-with-block-code-build-wue78.png` · Strip: `device-mockup-zoom-with-block-code-build-wue78-strip.png`
- Tags: motion=[scale-bloom, slide-in, settle] · archetype=device-mockup · energy=punchy · mood=playful
- Use when: a UI/device mockup is the hero while a control panel assembles step by step beneath it
- Motion: An isometric maze 'device' mock sits centered and scale-blooms — small in the first frame under the 'The While Loop' headline, then growing to fill most of the card across the middle frames before easing back to a settled size. Underneath, a block-coding panel builds line by line: a 'repeat 2 times' loop chip appears, the count bumps from 2 to 4, and 'move forward / turn right' rows slide in below while a cursor hovers the dropdowns. The pairing reads as hero-mockup-zoom on top with a control panel assembling beneath it, settling into a stable layout.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.6102 · eased_energy_share=0.9735 · sparsity=0.0162 · spatial_concentration=0.2443 · mov_texture=9.3628)
- Source: https://www.youtube.com/watch?v=0mpkIAwUe78 @ 4:34-4:36

### code-typewriter-with-definition-lower-third-feygo
- Hero: `code-typewriter-with-definition-lower-third-feygo.png` · Strip: `code-typewriter-with-definition-lower-third-feygo-strip.png`
- Tags: motion=[typewriter, slide-in] · archetype=lower-third · energy=measured · mood=neutral
- Use when: a single term gets defined as the code is written that introduces it
- Motion: Left of frame a dark code editor types a Dockerfile line by line (a commented hint, then 'FROM') in a steady typewriter cadence, while a designed lower-third caption 'base image = starting point' sits flush to the bottom-left as a plain-language gloss. The caption holds static under the typing so the term and its definition read together. After the reveal it cuts away to a plain Docker Hub browser scroll, so only the first third of the strip carries the designed motion.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.6002 · eased_energy_share=1 · sparsity=0.0109 · spatial_concentration=0.244 · mov_texture=10.5435)
- Source: https://www.youtube.com/watch?v=DQdB7wFEygo @ 4:20-4:23

### code-line-zoom-punch-emphasis-feygo
- Hero: `code-line-zoom-punch-emphasis-feygo.png` · Strip: `code-line-zoom-punch-emphasis-feygo-strip.png`
- Tags: motion=[scale-bloom, settle] · archetype=code-reveal · energy=punchy · mood=neutral
- Use when: one command in a code block is the line that matters and needs to pop
- Motion: A clean syntax-highlighted block ('# Install app dependencies' / 'RUN npm install') sits centered, then a steady push-in scale-blooms the same two lines larger across each frame of the strip, magenta keyword and white command growing in step. The zoom is continuous rather than overshooting, settling at a held close-up that frames 'RUN npm install' as the takeaway before the next beat.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.7205 · eased_energy_share=0.986 · sparsity=0.0044 · spatial_concentration=0.3151 · mov_texture=9.3023)
- Source: https://www.youtube.com/watch?v=DQdB7wFEygo @ 4:58-5:00

### step-title-card-with-logo-build-feygo
- Hero: `step-title-card-with-logo-build-feygo.png` · Strip: `step-title-card-with-logo-build-feygo-strip.png`
- Tags: motion=[slide-in, stagger, settle] · archetype=title-card · energy=punchy · mood=playful
- Use when: a numbered step or chapter break announces the next section
- Motion: A full code editor cuts to a white title card: the blue Docker whale logo settles in at left while a two-line heading builds on the right, 'Step 5:' landing first, then 'Building the Image' dropping in beneath it in a quick stagger. The text slides up and settles with no overshoot, holding the assembled card before cutting to a terminal. It reads as a clean section-break stinger over a plain backdrop.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.8583 · eased_energy_share=0.8759 · sparsity=0.0001 · spatial_concentration=0.0765 · mov_texture=7.4098)
- Source: https://www.youtube.com/watch?v=DQdB7wFEygo @ 6:23-6:26

### logo-card-spin-flip-settle-feygo
- Hero: `logo-card-spin-flip-settle-feygo.png` · Strip: `logo-card-spin-flip-settle-feygo-strip.png`
- Tags: motion=[card-flip, snap, settle] · archetype=title-card · energy=frenetic · mood=playful
- Use when: a brand or logo is called out with a quick, energetic flourish
- Motion: A white 'docker Compose' logo card sits flat, then spins hard through the strip: it tips clockwise, flips fully upside-down at the mid-frame, swings back through, and snaps upright to a settled rest. The rotation carries real angular speed (this is the highest-energy beat in the video), reading as a single fast card-flip flourish before cutting straight to an Express code file.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=16.3818 · eased_energy_share=1 · sparsity=0.0001 · spatial_concentration=0.2833 · mov_texture=15.4261)
- Source: https://www.youtube.com/watch?v=DQdB7wFEygo @ 9:14-9:17

### but-pivot-word-with-year-compare-panel-ki7uc
- Hero: `but-pivot-word-with-year-compare-panel-ki7uc.png` · Strip: `but-pivot-word-with-year-compare-panel-ki7uc-strip.png`
- Tags: motion=[pop, snap, settle] · archetype=kinetic-type · energy=punchy · mood=tense
- Use when: a one-word pivot interrupts the momentum right before the turn ('but...')
- Motion: After a stretch of red crashing-market B-roll, the frame cuts to black and a single bold lowercase 'but' snaps in dead-center, holding with no drift. To its right a small three-column year panel (2020 / 2024 / 2025) settles into place as a quiet comparison tell beneath a 'how did this happen?' header. The cut from chaotic full-frame texture to one stark word on black is the whole move — a hard contrast beat, not a built animation.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.5578 · eased_energy_share=0.8663 · sparsity=0.0191 · spatial_concentration=0.269 · mov_texture=15.0849)
- Source: https://www.youtube.com/watch?v=M98r0fKI7uc @ 0:36-0:42

### logo-scale-bloom-soft-glow-over-code-ki7uc
- Hero: `logo-scale-bloom-soft-glow-over-code-ki7uc.png` · Strip: `logo-scale-bloom-soft-glow-over-code-ki7uc-strip.png`
- Tags: motion=[scale-bloom, pop] · archetype=device-mockup · energy=punchy · mood=playful
- Use when: a named product or brand drops in as the punchline over a working screen
- Motion: The strip holds a static dark code editor for most of its width, then a teal ChatGPT mark scale-blooms up from small into the lower-right, backed by a soft radial glow that grows with it. The logo overshoots slightly and settles large, reading as a stamp landing on top of the existing screen rather than a transition. The underlying code never moves — only the badge animates in.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.9847 · eased_energy_share=0.8049 · sparsity=0.0874 · spatial_concentration=0.4824 · mov_texture=8.3694)
- Source: https://www.youtube.com/watch?v=M98r0fKI7uc @ 3:04-3:10

### bridge-truss-diagram-build-node-by-node-ki7uc
- Hero: `bridge-truss-diagram-build-node-by-node-ki7uc.png` · Strip: `bridge-truss-diagram-build-node-by-node-ki7uc-strip.png`
- Tags: motion=[draw-on, stagger, settle] · archetype=diagram-build · energy=measured · mood=neutral
- Use when: a structure or system assembles piece by piece to show how the parts connect
- Motion: Under a 'Structure — make this bridge rigid' title, a black-node truss draws itself onto a white panel: first a low arch of a few nodes and beams, then successive frames add crossbeams and a raised apex node, the lattice thickening left-to-right as orange terrain wedges anchor each end. The build is staggered and additive — each frame commits a couple more struts and settles, so the diagram grows denser without anything re-laying-out. A clean, calm step-by-step assembly.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.924 · eased_energy_share=0.9712 · sparsity=0 · spatial_concentration=0.1847 · mov_texture=8.8339)
- Source: https://www.youtube.com/watch?v=M98r0fKI7uc @ 7:02-7:04

### agent-pipeline-node-graph-build-htrji
- Hero: `agent-pipeline-node-graph-build-htrji.png` · Strip: `agent-pipeline-node-graph-build-htrji-strip.png`
- Tags: motion=[draw-on, slide-in, parallax-push] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a multi-stage pipeline assembles node-by-node as you narrate how the parts hand off
- Motion: On a near-black canvas, labeled agent nodes ("Research Agent", "Writer Agent") reveal left-to-right, each a rounded card with a small icon and sub-node fan beneath it, linked by short connector arrows that draw on between stages. Across the strip the camera pushes/pans rightward so the next node slides into frame as the prior one settles, reading as a chain being built link by link. Easing is gentle, no overshoot — nodes simply resolve into place. The final frame cuts away entirely to live-action B-roll, so the usable motion is the diagram-assembly portion only.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=10.9907 · eased_energy_share=1 · sparsity=0.0009 · spatial_concentration=0.2992 · mov_texture=9.6295)
- Source: https://www.youtube.com/watch?v=XBuv4HHTRjI @ 6:01-6:04

### colored-block-flow-diagram-into-title-card-htrji
- Hero: `colored-block-flow-diagram-into-title-card-htrji.png` · Strip: `colored-block-flow-diagram-into-title-card-htrji-strip.png`
- Tags: motion=[draw-on, pop, wipe] · archetype=diagram-build · energy=measured · mood=neutral
- Use when: a control-flow pattern builds in colored blocks and then resolves to a clean section title
- Motion: A pastel block diagram assembles in the center — pink "LLM Block" and blue capsule nodes wired by curved arrows that loop back through a "Check Output / Exit" gate, the colored boxes popping in over a documentation backdrop. Mid-strip a labeled "Orchestrator-worker-synthesizer" stack of blocks fills in row by row. The beat ends on a hard wipe to a stark dark title card reading "How to make an agent" in large serif, the diagram giving way to the headline. Motion is steady with light pop on each block, no overshoot.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=7.4431 · eased_energy_share=0.3001 · sparsity=0.0052 · spatial_concentration=0.4128 · mov_texture=14.8513)
- Source: https://www.youtube.com/watch?v=XBuv4HHTRjI @ 7:04-7:09

### landing-hero-headline-into-ui-reveal-htrji
- Hero: `landing-hero-headline-into-ui-reveal-htrji.png` · Strip: `landing-hero-headline-into-ui-reveal-htrji-strip.png`
- Tags: motion=[scale-bloom, slide-in, settle] · archetype=title-card · energy=punchy · mood=triumphant
- Use when: a product hero headline lands first, then its supporting UI and sections reveal underneath
- Motion: Opens on a white landing-page hero — "The Platform For Building Agents" set huge with the second line in orange italic, twin "Get Started / View Docs" buttons, and a chat-bubble flow blooming in below the fold. The headline holds across the first frames while the body UI populates, then the strip transitions to a "What are agents?" section and a faint node diagram, settling finally on a dark code block. The hero type carries weight up front; supporting elements slide in and settle beneath it with calm easing and no overshoot.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.8432 · eased_energy_share=0.5255 · sparsity=0.0389 · spatial_concentration=0.3284 · mov_texture=6.1857)
- Source: https://www.youtube.com/watch?v=XBuv4HHTRjI @ 7:32-7:36

### oversized-quote-resolves-to-definition-card-utlno
- Hero: `oversized-quote-resolves-to-definition-card-utlno.png` · Strip: `oversized-quote-resolves-to-definition-card-utlno-strip.png`
- Tags: motion=[slide-in, wipe, settle] · archetype=title-card · energy=punchy · mood=playful
- Use when: a punchline term gets defined as the payoff of a setup
- Motion: Opens on oversized black serif type cropped tight against white ('a short way to say... to someone's... Oxford University Press'), held large so only a fragment reads. Across the strip the big text clears and a centered definition card swaps in on black: a 'Rizz' heading at top, a small meme thumbnail beneath it, and a three-line dictionary gloss anchored at the bottom. The card holds steady once it lands with no further drift, so the motion is a single hard cut-to-settle from oversized teaser type into the framed definition rather than a continuous tween.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=7.5372 · eased_energy_share=1 · sparsity=0 · spatial_concentration=0.2916 · mov_texture=25.5139)
- Source: https://www.youtube.com/watch?v=Z_Z_PKUTLno @ 5:07-5:10

### scrolling-caption-banner-panel-wipe-utlno
- Hero: `scrolling-caption-banner-panel-wipe-utlno.png` · Strip: `scrolling-caption-banner-panel-wipe-utlno-strip.png`
- Tags: motion=[slide-in, kinetic-type, wipe] · archetype=lower-third · energy=punchy · mood=playful
- Use when: a quoted aside or punchline scrolls across as a caption banner
- Motion: A wide gray caption banner carries bold black two-line text ('...BYTES - Oh you don't know what a sloth byte is?') that tracks steadily leftward frame to frame, sliding the same phrase across at an even, readable pace. The last frame breaks the rhythm: the banner clips off at a hard right edge and a clean white panel wipes in from the right, settling the scroll into a fresh card. The cadence is a constant-velocity horizontal scroll punctuated by a single panel wipe at the end.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=11.2689 · eased_energy_share=0.7724 · sparsity=0 · spatial_concentration=0.1683 · mov_texture=10.2645)
- Source: https://www.youtube.com/watch?v=Z_Z_PKUTLno @ 6:27-6:29

### breaking-news-banner-logo-row-pop-qqmes
- Hero: `breaking-news-banner-logo-row-pop-qqmes.png` · Strip: `breaking-news-banner-logo-row-pop-qqmes-strip.png`
- Tags: motion=[pop, stagger, settle] · archetype=title-card · energy=punchy · mood=playful
- Use when: a mock breaking-news banner stamps in to frame a topic as urgent or hyped
- Motion: A row of recognizable brand logos snaps in across the top, then the stacked headline pops on beneath it: an italic blue 'AI NEWS' kicker first, then a heavy black 'BREAKING' and a multicolor 'AI NEWS' lockup landing as a unit. The type arrives with a hard punch rather than a soft fade, the logo row reading as a quick left-to-right stagger before the headline stamps. It settles flat and centered with no drift, holding as a static banner once assembled.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=15.3948 · eased_energy_share=0.8638 · sparsity=0 · spatial_concentration=0.247 · mov_texture=13.7421)
- Source: https://www.youtube.com/watch?v=jeCDCbqqmes @ 0:31-0:34

### rounded-logo-scale-pop-overshoot-qqmes
- Hero: `rounded-logo-scale-pop-overshoot-qqmes.png` · Strip: `rounded-logo-scale-pop-overshoot-qqmes-strip.png`
- Tags: motion=[scale-bloom, overshoot, settle] · archetype=title-card · energy=punchy · mood=warm
- Use when: a brand or section logo bounces on as a cheerful interstitial stamp
- Motion: A small rounded-pill 'Sloth Bytes' logo blooms up from a compact size to a large hero scale on a clean white field, the second frame showing it noticeably overshot and oversized before it would settle back. The growth is fast and springy, reading as a single scale-up bounce centered in frame. It then hard-cuts away to a browser screen, so the kept motion is the pop-in itself.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.1532 · eased_energy_share=0.892 · sparsity=0.0531 · spatial_concentration=0.387 · mov_texture=14.5583)
- Source: https://www.youtube.com/watch?v=jeCDCbqqmes @ 6:35-6:46

### node-graph-glow-to-promo-card-6crlc
- Hero: `node-graph-glow-to-promo-card-6crlc.png` · Strip: `node-graph-glow-to-promo-card-6crlc-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=diagram-build · energy=measured · mood=neutral
- Use when: a connected-system idea resolves into a single call-to-action payoff
- Motion: Opens on a dark knowledge-graph: faint node-and-edge lines fan out from a glowing diamond hub at center-right, the connections holding steady as the focal node pulses. The strip then hard-cuts to a deep-blue promo card where 'Link in the description / Use code: sloth25 for 25% off' sits centered while 'Save hours every day' kinetic text holds above and below. The final frames layer in an 'Augmented Browsing' label and a small code/recall overlay sliding up bottom-right. Cadence is calm and stepped — graph holds, then a clean scene swap to the offer card, no overshoot.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.7193 · eased_energy_share=0.8072 · sparsity=0.2813 · spatial_concentration=0.5379 · mov_texture=6.6783)
- Source: https://www.youtube.com/watch?v=tIdWQC6Crlc @ 11:10-11:16

### feature-card-grid-then-kinetic-pullquote-6crlc
- Hero: `feature-card-grid-then-kinetic-pullquote-6crlc.png` · Strip: `feature-card-grid-then-kinetic-pullquote-6crlc-strip.png`
- Tags: motion=[stagger, slide-in, scale-bloom] · archetype=kinetic-type · energy=measured · mood=triumphant
- Use when: a product's features assemble, then a bold quote lands as the closing flourish
- Motion: Begins with a 2x3 grid of feature cards (Spaced Repetition, Automatic Knowledge Graph, Secure & Private) settled in place with icons. A 'Security And Data Protection' section title then rises and settles into center as a fresh row of three cards (Data ownership, Data portability, Privacy Focused) staggers in beneath it. The strip closes on a large pull-quote — 'Creativity is just connecting things.' — that scale-blooms up to full size and holds, with 'Used by Nerds Around the World' fading in below, then the quote shrinks back toward the corner. Easing is gentle and confident: each card steps in left-to-right, the quote overshoots slightly into its hold.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.8991 · eased_energy_share=0.9859 · sparsity=0.308 · spatial_concentration=0.2355 · mov_texture=7.2395)
- Source: https://www.youtube.com/watch?v=tIdWQC6Crlc @ 11:17-11:21

### kinetic-future-of-title-build-dzxf0
- Hero: `kinetic-future-of-title-build-dzxf0.png` · Strip: `kinetic-future-of-title-build-dzxf0-strip.png`
- Tags: motion=[kinetic-type, slide-in, settle] · archetype=title-card · energy=punchy · mood=neutral
- Use when: a section title lands to frame the next claim
- Motion: Over a dark field the phrase assembles word-by-word: a faint glyph cluster resolves first, then 'future of' snaps into legibility, and by the final frame the full 'the future of' has settled crisp and centered. Each word arrives staggered left-to-right rather than all at once, and the type slides up a touch into its resting baseline. No camera move — the build is purely in the type sharpening and sliding to rest.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.5865 · eased_energy_share=0.9658 · sparsity=0.5281 · spatial_concentration=0.7094 · mov_texture=17.5464)
- Source: https://www.youtube.com/watch?v=2AzUeddzxF0 @ 0:19-0:23

### handwritten-verdict-text-slide-settle-dzxf0
- Hero: `handwritten-verdict-text-slide-settle-dzxf0.png` · Strip: `handwritten-verdict-text-slide-settle-dzxf0-strip.png`
- Tags: motion=[slide-in, kinetic-type, settle] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: a blunt verdict or punchline lands over a quote or clip
- Motion: A source quote card sits at far left, then the strip cuts to a dark field where the handwritten-style phrase 'mostly garbage' slides in from the right and grows as it travels. Across the middle frames it scales up and slides toward center, settling slightly tilted in a casual marker hand. By the last frames it holds at full size over the underlying talking-head clip — the emphasis is all in the rightward slide-and-grow before it locks.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.1728 · eased_energy_share=0.976 · sparsity=0.2057 · spatial_concentration=0.4128 · mov_texture=12.9661)
- Source: https://www.youtube.com/watch?v=2AzUeddzxF0 @ 2:08-2:11

### green-check-list-build-then-wipe-dzxf0
- Hero: `green-check-list-build-then-wipe-dzxf0.png` · Strip: `green-check-list-build-then-wipe-dzxf0-strip.png`
- Tags: motion=[draw-on, stagger, wipe] · archetype=checklist · energy=punchy · mood=warm
- Use when: two or three supporting points tick off as the payoff
- Motion: Beside the presenter two checklist rows hold steady — a green tick draws on next to 'doesn't cost performance', then a second tick beside 'can be faster' — reading as a staggered top-to-bottom build. After the list completes it doesn't fade in place: the right frames show the green ticks and text wiping/sliding off to clear the frame, leaving only faint ghost marks. The motion is the sequential check-on followed by a clean exit wipe.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.7534 · eased_energy_share=0.9556 · sparsity=0.1683 · spatial_concentration=0.2842 · mov_texture=17.1452)
- Source: https://www.youtube.com/watch?v=2AzUeddzxF0 @ 4:18-4:21

### title-checklist-glitch-dissolve-to-icons-jeab0
- Hero: `title-checklist-glitch-dissolve-to-icons-jeab0.png` · Strip: `title-checklist-glitch-dissolve-to-icons-jeab0-strip.png`
- Tags: motion=[glitch, mask-reveal, settle] · archetype=checklist · energy=frenetic · mood=playful
- Use when: a labeled concept resolves into its concrete parts as the explanation lands
- Motion: Opens on a glowing 'VIRTUALISATION' title over a starfield with a hand-drawn checklist already settled around an orange VM icon — memory capacity, storage size, processor speed each ticked. Mid-strip the checklist and icon shatter into a vertical shredded/glitch texture that scans across the frame, then the noise clears to leave the title alone before resolving onto clean RAM and CPU icons. The transition is a hard glitch-wipe, not an ease — punchy and abrupt, with the title holding constant as the anchor.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.8666 · eased_energy_share=0.9457 · sparsity=0.3888 · spatial_concentration=0.6195 · mov_texture=21.5524)
- Source: https://www.youtube.com/watch?v=3dAAHKJEaB0 @ 0:54-0:57

### lock-hub-orbiting-labels-to-icon-set-jeab0
- Hero: `lock-hub-orbiting-labels-to-icon-set-jeab0.png` · Strip: `lock-hub-orbiting-labels-to-icon-set-jeab0-strip.png`
- Tags: motion=[pop, stagger, settle] · archetype=diagram-build · energy=frenetic · mood=neutral
- Use when: a central concept's facets are introduced one by one before the topic is named
- Motion: A gold padlock sits center with three labels — identity, permissions, resources — popping in around it on a red 'Identity and Access Management' lower strip. The cluster clears to a single person silhouette held alone for a couple frames, then a person/people/gear icon set snaps in left-to-right in a quick stagger. Each element pops in discretely rather than sliding; the lower-third label stays pinned the whole beat while the upper graphic swaps sets.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.8875 · eased_energy_share=0.934 · sparsity=0.2206 · spatial_concentration=0.4415 · mov_texture=15.3407)
- Source: https://www.youtube.com/watch?v=3dAAHKJEaB0 @ 2:34-2:37

### server-stack-dissolve-spiking-arrow-draw-jeab0
- Hero: `server-stack-dissolve-spiking-arrow-draw-jeab0.png` · Strip: `server-stack-dissolve-spiking-arrow-draw-jeab0-strip.png`
- Tags: motion=[draw-on, mask-reveal, scale-bloom] · archetype=diagram-build · energy=punchy · mood=tense
- Use when: a cost or metric spikes as the consequence of the prior point
- Motion: Starts with a balanced cluster of five white server-stack icons over a pink 'AWS Lambda' lower-third. The icons dissolve away in waves from the right — first thinning to two stacks, then to one — while a bold red zig-zag arrow draws on from the lower-right and grows, ratcheting upward across the last frames until it dominates the empty frame. The server fade-out and the arrow draw-on run as a crossfade against each other, reading as a sharp upward spike replacing the infrastructure.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.0526 · eased_energy_share=0.9421 · sparsity=0.5682 · spatial_concentration=0.7725 · mov_texture=21.0232)
- Source: https://www.youtube.com/watch?v=3dAAHKJEaB0 @ 6:37-6:40

### cash-particle-scatter-over-logo-stack-mz0rc
- Hero: `cash-particle-scatter-over-logo-stack-mz0rc.png` · Strip: `cash-particle-scatter-over-logo-stack-mz0rc-strip.png`
- Tags: motion=[particle, scale-bloom, settle] · archetype=collage · energy=frenetic · mood=playful
- Use when: a money/cost claim lands and you want the value to feel like it's raining down on a brand mark
- Motion: A dense cloud of dollar bills tumbles in as 3D particles, swirling across the full frame at high velocity through the first frames. A stacked colored block mark (red/green/blue/yellow) sits center and grows slightly as the bills churn. By the right frames the bill density thins and the storm has mostly cleared the mark, the particles settling toward the edges so the logo reads cleanly. No camera move; the motion is all foreground particle chaos resolving to a centered hold.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.209 · eased_energy_share=0.9611 · sparsity=0.1152 · spatial_concentration=0.379 · mov_texture=12.9793)
- Source: https://www.youtube.com/watch?v=5jp0H9mz0Rc @ 0:21-0:26

### logo-reveal-with-evaporative-kinetic-type-mz0rc
- Hero: `logo-reveal-with-evaporative-kinetic-type-mz0rc.png` · Strip: `logo-reveal-with-evaporative-kinetic-type-mz0rc-strip.png`
- Tags: motion=[slide-in, scale-bloom, settle] · archetype=kinetic-type · energy=punchy · mood=neutral
- Use when: a named product or spec drops in as the headline while a two-word label punches up beneath it
- Motion: The NVIDIA H100 wordmark holds at the top as the centerpiece. Beneath it the two-word label builds in sequence: EVAPORATIVE settles first, then COOLING scales up and bolds into place a beat later with a slight overshoot before settling to a crisp hold. Across the right frames the lower text wipes downward out of frame as the scene resets, leaving the clean logo. Tight, mechanical staging with no camera move.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=7.6917 · eased_energy_share=0.9409 · sparsity=0.2581 · spatial_concentration=0.5845 · mov_texture=16.0961)
- Source: https://www.youtube.com/watch?v=5jp0H9mz0Rc @ 1:34-1:36

### google-letters-assemble-then-searchbar-slide-mz0rc
- Hero: `google-letters-assemble-then-searchbar-slide-mz0rc.png` · Strip: `google-letters-assemble-then-searchbar-slide-mz0rc-strip.png`
- Tags: motion=[pop, settle, slide-in] · archetype=title-card · energy=measured · mood=neutral
- Use when: a recognizable brand/logo assembles from its colored parts and a UI element rises to complete the scene
- Motion: It opens with the four colored Google dots clustered low, then the full Google wordmark pops into the upper-center and holds steady. From the second frame on, a rounded search-bar pill rises from the bottom edge and slides upward frame by frame, climbing toward the wordmark until it settles into the lower third. Easing is smooth with a soft landing; the whole composition lives on flat black with a faint starfield, no camera move.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=8.2716 · eased_energy_share=0.9485 · sparsity=0.2234 · spatial_concentration=0.5897 · mov_texture=6.8049)
- Source: https://www.youtube.com/watch?v=5jp0H9mz0Rc @ 2:04-2:06

### handwritten-checklist-then-3d-skull-render-mz0rc
- Hero: `handwritten-checklist-then-3d-skull-render-mz0rc.png` · Strip: `handwritten-checklist-then-3d-skull-render-mz0rc-strip.png`
- Tags: motion=[draw-on, settle, scale-bloom] · archetype=checklist · energy=punchy · mood=playful
- Use when: a set of requirements or features gets ticked off one by one before the scene hard-cuts to a payoff visual
- Motion: The first frames hold a hand-drawn green checklist where four items (DBs, compute, 1TB, forks) each carry a marker check that reads as freshly drawn on. The scene then hard-cuts and a chromed 3D skull/robot render rises from behind a low city skyline, growing larger and tilting up across the remaining frames with glowing orange eyes resolving as it settles into frame. Two distinct designed beats stitched by a cut; the second has a slow scale-up push but no orbit.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.9043 · eased_energy_share=0.9637 · sparsity=0.289 · spatial_concentration=0.6414 · mov_texture=16.1593)
- Source: https://www.youtube.com/watch?v=5jp0H9mz0Rc @ 4:16-4:18

### scribble-annotated-title-swap-ffam
- Hero: `scribble-annotated-title-swap-ffam.png` · Strip: `scribble-annotated-title-swap-ffam-strip.png`
- Tags: motion=[marker-sweep, wipe, snap] · archetype=title-card · energy=punchy · mood=playful
- Use when: a phrase gets a hand-drawn aside before the idea hard-cuts to its punchline
- Motion: A two-tone left-aligned headline ('Monday / morning') sits over a portrait while a magenta handwritten 'review' scribble sweeps on above it like a marker annotation. The headline and scribble hold for a couple of frames, then the whole frame hard-cuts to a fresh two-line card ('THINK & SOLVE / PROBLEMS') in the same weight — a snap swap rather than a dissolve. No easing on the type itself; the only continuous motion is the marker stroke laying down the accent word.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=2.5988 · eased_energy_share=0.8988 · sparsity=0.636 · spatial_concentration=0.7993 · mov_texture=19.5125)
- Source: https://www.youtube.com/watch?v=6alBAr_FfaM @ 0:57-1:00

### green-streak-wipe-title-handoff-ffam
- Hero: `green-streak-wipe-title-handoff-ffam.png` · Strip: `green-streak-wipe-title-handoff-ffam-strip.png`
- Tags: motion=[wipe, glitch, snap] · archetype=title-card · energy=punchy · mood=neutral
- Use when: one labeled idea cuts to the next through a charged transition rather than a clean dissolve
- Motion: A three-line lowercase headline ('learn / a new / library') holds over a black-and-white B-roll plate, then collapses as a horizontal green streak rakes across the lower third like a scanline wipe, smearing the type into ghosted bars. Out of that streak the next two-tone card ('GENERATE / SOLUTIONS') snaps in fully formed. The transition is the designed element — a fast lateral green-line wipe with a brief glitch-smear, no overshoot or settle, the destination card arriving hard.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.6108 · eased_energy_share=0.9625 · sparsity=0.3189 · spatial_concentration=0.6653 · mov_texture=15.0121)
- Source: https://www.youtube.com/watch?v=6alBAr_FfaM @ 1:25-1:29

### ai-logo-icon-cluster-to-custom-ffam
- Hero: `ai-logo-icon-cluster-to-custom-ffam.png` · Strip: `ai-logo-icon-cluster-to-custom-ffam-strip.png`
- Tags: motion=[pop, scale-bloom, snap] · archetype=collage · energy=punchy · mood=playful
- Use when: a roster of tools or brands clusters around a subject before the takeaway word lands
- Motion: A grayscale portrait anchors the left while a cluster of saturated icon glyphs — a four-point gradient star, an orange burst, a teal logo, a slashed circle — pop in around the head, each holding crisp and bright against the desaturated plate. The icon grid stays put for a beat, then the frame snaps to a single bold 'CUSTOM' kinetic-type card that scale-blooms briefly before settling. The contrast of colorful designed icons over monochrome footage carries the motion; the word arrives as a hard payoff cut.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.4519 · eased_energy_share=0.8926 · sparsity=0.3446 · spatial_concentration=0.497 · mov_texture=18.422)
- Source: https://www.youtube.com/watch?v=6alBAr_FfaM @ 7:08-7:11

### kinetic-headline-over-retro-plate-trapq
- Hero: `kinetic-headline-over-retro-plate-trapq.png` · Strip: `kinetic-headline-over-retro-plate-trapq-strip.png`
- Tags: motion=[pop, slide-in, settle] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: a single concept word lands as a punchy on-screen label over a stylized background image
- Motion: A retro shush-woman illustration is already on the plate when the green 'STABLE' headline pops in to its right, scaling up with a small overshoot before settling. A beat later a smaller 'USER INTERFACE' subtitle slides up underneath it. The word carries the emphasis while the background image holds, so the type reads as the payoff layered over a graphic plate.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.1637 · eased_energy_share=0.9623 · sparsity=0.359 · spatial_concentration=0.5777 · mov_texture=13.3723)
- Source: https://www.youtube.com/watch?v=AZljidtrAPQ @ 1:58-2:01

### code-block-wipe-to-image-trapq
- Hero: `code-block-wipe-to-image-trapq.png` · Strip: `code-block-wipe-to-image-trapq-strip.png`
- Tags: motion=[wipe, slide-in, snap] · archetype=code-reveal · energy=punchy · mood=neutral
- Use when: a code sample hands off to its visual result via a hard scene swap
- Motion: The strip opens full-frame on a syntax-highlighted code block held steady, then a vertical seam sweeps left-to-right and a surprised retro-woman image takes over the frame in two snaps. The transition is a clean designed cut between a code-reveal scene and an image scene rather than a crossfade, so the swap reads as a hard wipe from code to consequence.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.9978 · eased_energy_share=0.9918 · sparsity=0.1651 · spatial_concentration=0.4549 · mov_texture=12.5203)
- Source: https://www.youtube.com/watch?v=AZljidtrAPQ @ 2:16-2:19

### handwritten-word-under-brand-logo-side-cutout-trapq
- Hero: `handwritten-word-under-brand-logo-side-cutout-trapq.png` · Strip: `handwritten-word-under-brand-logo-side-cutout-trapq-strip.png`
- Tags: motion=[slide-in, draw-on, settle] · archetype=title-card · energy=measured · mood=warm
- Use when: a brand or tool name is introduced as a friendly titled callout with a supporting cutout
- Motion: An orange Cloudflare cloud logo holds center while the handwritten 'integration' word draws in beneath it, the script settling as if hand-lettered. Then a black-and-white winking retro-woman cutout slides in from the right edge to fill the negative space. The logo anchors, the word and the side cutout enter in sequence and settle, giving a calm two-part title build.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.0434 · eased_energy_share=0.9637 · sparsity=0.2885 · spatial_concentration=0.5632 · mov_texture=7.9246)
- Source: https://www.youtube.com/watch?v=AZljidtrAPQ @ 3:51-3:55

### badge-collage-arrow-connect-trapq
- Hero: `badge-collage-arrow-connect-trapq.png` · Strip: `badge-collage-arrow-connect-trapq-strip.png`
- Tags: motion=[pop, draw-on, stagger] · archetype=collage · energy=frenetic · mood=playful
- Use when: two tools or icons connect to each other as the punchline of a busy collage frame
- Motion: Over a retro-woman photo collage, a purple-and-yellow V8 lightning badge pops in at lower-left while a circled 'R#' badge appears upper-right, and a small curved arrow draws on between them to link the two. The badges hold and the arrow completes the connect, then the whole collage clears to black. It is a frenetic, layered pop-and-connect rather than a clean single entrance.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.8565 · eased_energy_share=0.9782 · sparsity=0.3183 · spatial_concentration=0.5496 · mov_texture=9.5819)
- Source: https://www.youtube.com/watch?v=AZljidtrAPQ @ 7:09-7:12

### split-flap-board-to-filetree-reveal-enuju
- Hero: `split-flap-board-to-filetree-reveal-enuju.png` · Strip: `split-flap-board-to-filetree-reveal-enuju-strip.png`
- Tags: motion=[slide-in, wipe, settle] · archetype=device-mockup · energy=punchy · mood=playful
- Use when: an app or product mockup is introduced, then swapped for the underlying data or file structure behind it
- Motion: Opens on a fully-built split-flap departure-board mockup ('Vistaboard WEB APP CLONE') reading STRAVA / MORNING RUN with DIST, PACE, and TIME rows already settled. The board holds for two frames, then a hard left-edge wipe pushes it off and a dark starfield panel slides in carrying a smaller framed UI card. That card resolves into a code file-tree listing of .js filenames, with a hand-drawn arrow annotation ('clk lines') sweeping in to point at the list. The cadence is hold-then-swap: a static graphic establishes, a quick horizontal wipe transitions, and the replacement panel settles with an annotation drawn on last.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.648 · eased_energy_share=0.972 · sparsity=0.0666 · spatial_concentration=0.1749 · mov_texture=5.4915)
- Source: https://www.youtube.com/watch?v=MrCh0tEnUjU @ 1:46-1:48

### vibe-coding-highlight-wipe-to-solopreneur-enuju
- Hero: `vibe-coding-highlight-wipe-to-solopreneur-enuju.png` · Strip: `vibe-coding-highlight-wipe-to-solopreneur-enuju-strip.png`
- Tags: motion=[marker-sweep, wipe, kinetic-type] · archetype=title-card · energy=punchy · mood=playful
- Use when: a punchline label needs to land with emphasis, then hard-cut into a contrasting payoff card
- Motion: Starts on a 'vibe coding WEEKEND' title where WEEKEND sits inside a green highlight block, the eyes of the figure masked by a matching green bar. The green highlight is the held emphasis for the first two frames. Then a left-to-right wipe collapses the green block off the word as the frame cuts through a dark seam into a high-contrast black-and-white clip, and the strip resolves on a separate 'SOLOPRENEUR' title card snapping in at the right edge. Cadence is emphasis-hold, then a fast wipe transition that swaps the kinetic label for the contrasting payoff word.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.6423 · eased_energy_share=0.9807 · sparsity=0.1663 · spatial_concentration=0.6814 · mov_texture=21.3108)
- Source: https://www.youtube.com/watch?v=MrCh0tEnUjU @ 6:13-6:16

### card-dissolve-to-wordmark-logo-dmkia
- Hero: `card-dissolve-to-wordmark-logo-dmkia.png` · Strip: `card-dissolve-to-wordmark-logo-dmkia-strip.png`
- Tags: motion=[mask-reveal, blur-rack, pop] · archetype=title-card · energy=punchy · mood=playful
- Use when: a named concept resolves into its branded wordmark as the payoff
- Motion: A screenshot card (a dictionary 'word of the year' entry) holds for the first two frames, then blur-racks and dissolves across the middle frames as it hands off. In the final frames the 'vibe coding' wordmark snaps in clean, the lowercase script settling under the bold mark with a small orange swoosh accent on the first letter. The transition is a soft defocus-out into a crisp logo pop rather than a hard cut.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.4484 · eased_energy_share=0.9703 · sparsity=0.3112 · spatial_concentration=0.5013 · mov_texture=16.0333)
- Source: https://www.youtube.com/watch?v=klK3mfDMkiA @ 1:01-1:04

### year-count-up-over-wordmark-dmkia
- Hero: `year-count-up-over-wordmark-dmkia.png` · Strip: `year-count-up-over-wordmark-dmkia-strip.png`
- Tags: motion=[count-up, snap, wipe] · archetype=kinetic-type · energy=frenetic · mood=neutral
- Use when: a year or running figure spins up to its final value as a reveal
- Motion: Opens on a 'software ENGINEERING' wordmark (green-highlighted lower word) which wipes off to clear the frame. A large numeral then races a count-up sequence center-frame — 1, then 19, holding 19, then 196 — each value snapping in over the last with no easing tail, reading as a fast odometer roll toward a year. The strip closes as a black-and-white archival photo wipes in behind the final number, grounding the count-up in a historical date.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.1119 · eased_energy_share=0.9561 · sparsity=0.2373 · spatial_concentration=0.4183 · mov_texture=18.0645)
- Source: https://www.youtube.com/watch?v=klK3mfDMkiA @ 1:59-2:02

### render-skull-checklist-wipe-to-table-dmkia
- Hero: `render-skull-checklist-wipe-to-table-dmkia.png` · Strip: `render-skull-checklist-wipe-to-table-dmkia-strip.png`
- Tags: motion=[wipe, slide-in, draw-on] · archetype=checklist · energy=punchy · mood=playful
- Use when: a verdict checklist gives way to the supporting data it summarizes
- Motion: A 3D chrome skull render sits left while two hand-drawn green checkmarks anchor a 'very good use cases' / 'some decent use cases' list right; a marker underline grows beneath the lower item across the first three frames. The whole composition then wipes left as a white data table slides in from the right with green accent slivers trailing the edge, the rows landing settled on a starfield background. The cut from illustrated verdict to literal table is a hard horizontal wipe rather than a dissolve.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.3312 · eased_energy_share=0.982 · sparsity=0.0752 · spatial_concentration=0.3924 · mov_texture=21.7885)
- Source: https://www.youtube.com/watch?v=klK3mfDMkiA @ 5:06-5:09

### logo-lockup-3d-petal-bloom-unfurl-alwxs
- Hero: `logo-lockup-3d-petal-bloom-unfurl-alwxs.png` · Strip: `logo-lockup-3d-petal-bloom-unfurl-alwxs-strip.png`
- Tags: motion=[draw-on, scale-bloom, morph] · archetype=title-card · energy=measured · mood=serious
- Use when: a brand mark resolves and a designed organic form blooms in to give the title weight
- Motion: An orange asterisk star sits locked left of the white MYTHOS wordmark, both already settled and holding steady. Across the strip a white 3D petal/floral form unfurls in from the right edge, growing larger and rotating open frame by frame while the wordmark stays fixed. The bloom eases in slowly with no overshoot, scaling and morphing from a tight bud to spread petals as it drifts toward center. The brand lockup anchors the frame while the decorative render carries all the motion.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.6983 · eased_energy_share=0.9617 · sparsity=0.453 · spatial_concentration=0.547 · mov_texture=13.5837)
- Source: https://www.youtube.com/watch?v=mOGqQjAlWxs @ 4:04-4:06

### sponsor-logo-confetti-pop-ui-panel-alwxs
- Hero: `sponsor-logo-confetti-pop-ui-panel-alwxs.png` · Strip: `sponsor-logo-confetti-pop-ui-panel-alwxs-strip.png`
- Tags: motion=[pop, particle, slide-in] · archetype=title-card · energy=punchy · mood=playful
- Use when: a sponsor or product name lands as a celebratory beat before its UI is revealed
- Motion: Opens on a hand-drawn get it / build it script with a small face, then the CodeCrafters wordmark pops in centered as multicolored confetti particles scatter across the black field. The logo shifts scale and position between frames as confetti continues raining, reading as a bouncy pop-in rather than a clean settle. The tail frames slide in a teal terminal/UI mock panel with a red accent ball from the right, layering a product reveal under the celebratory particle burst.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.5147 · eased_energy_share=0.935 · sparsity=0.1498 · spatial_concentration=0.3531 · mov_texture=7.4167)
- Source: https://www.youtube.com/watch?v=mOGqQjAlWxs @ 4:56-5:02

### two-tone-title-word-build-cutout-pop-9013y
- Hero: `two-tone-title-word-build-cutout-pop-9013y.png` · Strip: `two-tone-title-word-build-cutout-pop-9013y-strip.png`
- Tags: motion=[kinetic-type, slide-in, pop] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: a named concept is introduced and the label assembles itself on screen
- Motion: Opens on a magenta/white 'METHODOLOGY KILLS THE JOY' line, then hard-cuts to building the headline 'SPEC-DRIVEN DEVELOPMENT' word by word: 'SPEC-DRIVEN' arrives first in teal-green (sliding in with a motion-blur smear on the entering word), settles, then 'DEVELOPMENT' drops in below it on the next frame. As the title locks, a person cutout pops up from the lower edge at the final frame. The two-tone color split (green keyword over white) carries the emphasis; cadence is one word per beat with no overshoot, snappy and punctuated.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.466 · eased_energy_share=0.971 · sparsity=0.2695 · spatial_concentration=0.5418 · mov_texture=11.5236)
- Source: https://www.youtube.com/watch?v=nnUMJX9013Y @ 1:00-1:04

### checklist-beside-cutout-blur-wipe-to-title-9013y
- Hero: `checklist-beside-cutout-blur-wipe-to-title-9013y.png` · Strip: `checklist-beside-cutout-blur-wipe-to-title-9013y-strip.png`
- Tags: motion=[mask-reveal, blur-rack, wipe] · archetype=checklist · energy=frenetic · mood=neutral
- Use when: a labeled list of requirements gives way to the next section header
- Motion: Holds on a 'SPECIFY' header with three checkmarked items (JOURNEYS / REQUIREMENTS / CRITERIA) stacked beside a desaturated person cutout on the left. The list reads as already settled, then a heavy horizontal motion-blur rack wipes the whole frame and resolves into the green 'PLANNING' section title. The transition is the motion event — a fast blur-smear that carries the eye from the checklist scene straight into the next header, no stagger on the list itself.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=7.0732 · eased_energy_share=0.9755 · sparsity=0.0668 · spatial_concentration=0.1984 · mov_texture=16.6336)
- Source: https://www.youtube.com/watch?v=nnUMJX9013Y @ 3:08-3:10

### annotated-curve-drawon-arrow-to-title-9013y
- Hero: `annotated-curve-drawon-arrow-to-title-9013y.png` · Strip: `annotated-curve-drawon-arrow-to-title-9013y-strip.png`
- Tags: motion=[draw-on, marker-sweep, blur-rack] · archetype=diagram-build · energy=frenetic · mood=playful
- Use when: a curve illustrates a trade-off and a hand-drawn note calls out its peak
- Motion: A glowing green hill-shaped curve sits across the frame with a hand-scrawled pink 'complexity trough' label and a curved arrow pointing down into the dip; a small person cutout anchors the lower-left. The curve and its annotation hold for the first three frames, then a fast blur-rack smears the scene away and resolves into a bold blue 'DIGITAL' title that settles, with 'BABYSITTING' appearing in white beneath it on the final frame. The hand-drawn marker arrow plus the title's two-line reveal are the designed touches; pacing is punctuated, the transition snappy with no overshoot.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.2714 · eased_energy_share=0.9588 · sparsity=0.1227 · spatial_concentration=0.4717 · mov_texture=13.4024)
- Source: https://www.youtube.com/watch?v=nnUMJX9013Y @ 7:30-7:32

### headline-card-motionblur-wipe-out-8pm
- Hero: `headline-card-motionblur-wipe-out-8pm.png` · Strip: `headline-card-motionblur-wipe-out-8pm-strip.png`
- Tags: motion=[wipe, blur-rack, mask-reveal] · archetype=quote-card · energy=punchy · mood=serious
- Use when: a headline or quote lands, holds to be read, then clears to reveal the next subject
- Motion: A rounded white card carrying a bold serif headline and a small body paragraph sits crisp at frame-left and holds steady for the first two frames so it reads. It then drags sideways with a heavy horizontal motion-blur streak across the third and fourth frames, smearing the type as it exits. By the last frames the card is gone and a vintage bespectacled figure is left behind in the black field. The settle is on the incoming subject, not the card — the card never re-sharpens, it just blurs away.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.3249 · eased_energy_share=0.9921 · sparsity=0.0479 · spatial_concentration=0.2196 · mov_texture=16.8845)
- Source: https://www.youtube.com/watch?v=s31ZpM8_p_M @ 1:45-1:47

### handwritten-keyword-popon-formula-field-8pm
- Hero: `handwritten-keyword-popon-formula-field-8pm.png` · Strip: `handwritten-keyword-popon-formula-field-8pm-strip.png`
- Tags: motion=[pop, scale-bloom, draw-on] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: a single concept word punches in to name the idea the narrator just said
- Motion: Over a dim chalk-formula field and a centered subject, the lowercase word 'output' pops on hard in white near center-frame, arriving at full size with no slide. A couple frames later a second word, 'understanding', snaps in to the upper-right in handwritten red script, slightly larger and tilted. Each word appears as a discrete punch rather than a fade, and both hold once placed — the formulas behind stay static so the new word is the only thing that moves.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.6343 · eased_energy_share=0.902 · sparsity=0.2781 · spatial_concentration=0.5433 · mov_texture=8.7277)
- Source: https://www.youtube.com/watch?v=s31ZpM8_p_M @ 2:25-2:32

### red-x-checklist-build-then-wipe-8pm
- Hero: `red-x-checklist-build-then-wipe-8pm.png` · Strip: `red-x-checklist-build-then-wipe-8pm-strip.png`
- Tags: motion=[stagger, pop, wipe] · archetype=checklist · energy=punchy · mood=serious
- Use when: two or three negatives stack up as a list before the scene clears to the payoff
- Motion: Beside a talking subject, a stacked list builds top-down — 'friction', then 'effort', then 'thinking' — each line prefixed by a red X that pops in with its word in a quick stagger. The full three-item list holds crisp for a frame or two, then the whole frame wipes hard to black across the back half of the strip, leaving only a faint figure emerging. The build is fast and punctuated; the exit is a clean blackout wipe rather than a fade.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.1524 · eased_energy_share=0.9712 · sparsity=0.2857 · spatial_concentration=0.4795 · mov_texture=8.1227)
- Source: https://www.youtube.com/watch?v=s31ZpM8_p_M @ 2:48-2:52

### logo-grid-icon-cycle-swap-t0nfu
- Hero: `logo-grid-icon-cycle-swap-t0nfu.png` · Strip: `logo-grid-icon-cycle-swap-t0nfu-strip.png`
- Tags: motion=[pop, morph, settle] · archetype=collage · energy=punchy · mood=neutral
- Use when: an ecosystem or category list lands as a tidy roster of branded tools/options at once
- Motion: A 2x5 grid of circular icon-plus-label tiles (DevOps, SecOps, GitOps, CloudOps, FinOps, DataOps, MLOps, etc.) holds its layout while the icons inside each tile cycle and swap between the strip's two states. Tiles don't slide; the motion is localized inside each cell, with icons popping/morphing in place and the labels staying pinned beneath. The grid reads as a calm settled roster with per-cell refresh rather than a global entrance, so the eye scans the whole set evenly.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.5465 · eased_energy_share=0.9219 · sparsity=0.2013 · spatial_concentration=0.2841 · mov_texture=32.8213)
- Source: https://www.youtube.com/watch?v=16Gx6Ut0NfU @ 0:18-0:29

### beveled-letterform-over-parallax-bg-zi0es
- Hero: `beveled-letterform-over-parallax-bg-zi0es.png` · Strip: `beveled-letterform-over-parallax-bg-zi0es-strip.png`
- Tags: motion=[parallax-drift, settle] · archetype=title-card · energy=measured · mood=serious
- Use when: a single brand letter or monogram opens the piece and needs to feel weighty
- Motion: A large beveled 3D 'E' letterform sits center-frame and holds while the dark library/bookshelf background drifts behind it in a slow parallax push. Across the strip the letter barely translates; the depth comes from the receding shelves sliding past, giving the static glyph a sense of mass. It settles dead-center with no overshoot — a held title beat rather than an entrance.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.54 · eased_energy_share=0.9537 · sparsity=0.0205 · spatial_concentration=0.2413 · mov_texture=12.704)
- Source: https://www.youtube.com/watch?v=6pxwe0zI0es @ 0:04-0:08

### comparison-card-grid-build-promo-callout-zi0es
- Hero: `comparison-card-grid-build-promo-callout-zi0es.png` · Strip: `comparison-card-grid-build-promo-callout-zi0es-strip.png`
- Tags: motion=[stagger, slide-in, settle] · archetype=diagram-build · energy=punchy · mood=clinical
- Use when: a sponsor or product comparison resolves into a clean card grid with a price callout
- Motion: A dark comparison layout builds top row first — labelled spec pills and logo tiles staggering in left-to-right — then the lower row of branded cards fills underneath. Across the strip the grid populates in two passes and locks to a tidy aligned matrix. A yellow '60% OFF using link below' callout underlines in at the bottom on the final beats, sweeping on after the cards have settled.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=8.2431 · eased_energy_share=0.8853 · sparsity=0.0635 · spatial_concentration=0.0995 · mov_texture=10.939)
- Source: https://www.youtube.com/watch?v=6pxwe0zI0es @ 5:04-5:08

### level-slate-bold-type-over-swirl-diagram-1dook
- Hero: `level-slate-bold-type-over-swirl-diagram-1dook.png` · Strip: `level-slate-bold-type-over-swirl-diagram-1dook-strip.png`
- Tags: motion=[kinetic-type, settle, wipe] · archetype=title-card · energy=measured · mood=serious
- Use when: a new chapter or difficulty tier opens and you want a bold slate to announce it
- Motion: Heavy condensed 'LVL 0' lettering sits center-frame while a swirling architecture diagram and a fan of radial cards drift in behind it on the left and right; the type holds steady as the dark backdrop resolves around it. After the slate settles, the frame wipes to a second card ('The Lord of the Files') with a red-panda illustration sliding up from the lower third. The cut between the two graphic scenes is a clean designed transition, not a hard jump.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.4439 · eased_energy_share=0.9266 · sparsity=0.3612 · spatial_concentration=0.6088 · mov_texture=7.2226)
- Source: https://www.youtube.com/watch?v=8hyg9K1Dook @ 3:35-3:41

### free-cta-serif-blur-rack-over-code-1dook
- Hero: `free-cta-serif-blur-rack-over-code-1dook.png` · Strip: `free-cta-serif-blur-rack-over-code-1dook-strip.png`
- Tags: motion=[blur-rack, scale-bloom, settle] · archetype=kinetic-type · energy=punchy · mood=triumphant
- Use when: a payoff word lands as the CTA — the free / now / done moment that closes a section
- Motion: A huge out-of-focus serif glyph fills the foreground and racks sharp as 'READ & WATCH for FREE' assembles line by line over a dimmed code-editor backdrop. The top line arrives first, then 'for', then 'FREE' blooms up to full scale and snaps crisp on the last frame. The defocus-to-focus rack and the upward scale give the closing word a hard, celebratory landing.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=1.3419 · eased_energy_share=0.7139 · sparsity=0.6316 · spatial_concentration=0.7299 · mov_texture=10.0696)
- Source: https://www.youtube.com/watch?v=8hyg9K1Dook @ 4:01-4:08

### esports-mascot-logo-zap-settle-9rvlc
- Hero: `esports-mascot-logo-zap-settle-9rvlc.png` · Strip: `esports-mascot-logo-zap-settle-9rvlc-strip.png`
- Tags: motion=[slide-in, settle, overshoot] · archetype=title-card · energy=punchy · mood=playful
- Use when: a brand or product name stamps in as a high-energy intro sting
- Motion: The ZEROCLAW wordmark plus its blue scorpion-claw mascot fly in from the left, smeared with directional motion-blur trails in the first frames, then snap to rest center-frame. Electric-blue energy bolts crackle around the lockup as it lands, reading like a slight overshoot-and-settle on arrival. By the final frame the logo is crisp and static against pure black, the streaks resolved into clean rim-light. Fast, gamer-intro cadence with no camera move.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.1586 · eased_energy_share=0.9137 · sparsity=0.1975 · spatial_concentration=0.2849 · mov_texture=12.7704)
- Source: https://www.youtube.com/watch?v=oAluRE9rvLc @ 0:59-1:01

### landing-page-blur-rack-resolve-9rvlc
- Hero: `landing-page-blur-rack-resolve-9rvlc.png` · Strip: `landing-page-blur-rack-resolve-9rvlc-strip.png`
- Tags: motion=[blur-rack, settle, slide-in] · archetype=device-mockup · energy=frenetic · mood=neutral
- Use when: a product or website is unveiled as the reveal payoff after a fast cut-in
- Motion: After a hard whip-cut off illustrated B-roll, a dark navy landing page rushes in under heavy directional motion blur, every text row a horizontal smear. The blur racks off top-to-bottom as the layout decelerates: logo, the teal-accented headline 'Your personal AI agent', the 'Secure. Lightweight. Yours.' subhead, and the teal CTA buttons sharpen into legibility one band at a time. It settles on a crisp, fully-composed NanoClaw hero with nav bar and a 'Why NanoClaw?' section edge appearing. The motion is a single decelerating rush, not a stagger — fast in, firm stop.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=6.0644 · eased_energy_share=0.9892 · sparsity=0.0704 · spatial_concentration=0.2078 · mov_texture=5.2966)
- Source: https://www.youtube.com/watch?v=oAluRE9rvLc @ 1:18-1:20

### tilted-annotation-words-pop-over-screen-recording-lfu0
- Hero: `tilted-annotation-words-pop-over-screen-recording-lfu0.png` · Strip: `tilted-annotation-words-pop-over-screen-recording-lfu0-strip.png`
- Tags: motion=[pop, kinetic-type, wipe] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: a spoken metric gets called out and stamped onto live footage as an annotation
- Motion: Over a running browser screen-recording, hand-lettered annotation words snap in at a jaunty tilt: 'uptime' and 'good' pop on first, then '1.2 seconds' lands rotated a few degrees off-axis, each word arriving as a hard cut-in rather than a fade. The words hold over the underlying capture, then a colored panel wipes across left-to-right to replace the screen with a flat blue location card. The cadence is punctuated and quick, with the type stamped on like a marker callout rather than eased.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.9124 · eased_energy_share=0.9496 · sparsity=0.0635 · spatial_concentration=0.3954 · mov_texture=21.0809)
- Source: https://www.youtube.com/watch?v=umyvnBlF-u0 @ 4:36-4:39

### code-editor-autocomplete-dropdown-filter-u1ns8
- Hero: `code-editor-autocomplete-dropdown-filter-u1ns8.png` · Strip: `code-editor-autocomplete-dropdown-filter-u1ns8-strip.png`
- Tags: motion=[typewriter, pop, snap] · archetype=code-reveal · energy=punchy · mood=clinical
- Use when: a code idea lands by showing the editor finishing the thought for you
- Motion: Left to right the cursor types into a JS file and an IntelliSense autocomplete panel snaps open just below the caret, its blue selection band sitting on the top row. As more characters are typed the suggestion list filters down each frame, the entries reshuffling and shrinking until only the matching members remain, then collapses to a single tooltip-style row ('console.log'). The dropdown pops in with no overshoot, holds in place, and the whole move is fast and mechanical rather than eased.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.5084 · eased_energy_share=0.5302 · sparsity=0.0071 · spatial_concentration=0.3069 · mov_texture=2.5168)
- Source: https://www.youtube.com/watch?v=vPKPxvu1Ns8 @ 4:04-4:07

### dashboard-checklist-columns-reveal-niyfy
- Hero: `dashboard-checklist-columns-reveal-niyfy.png` · Strip: `dashboard-checklist-columns-reveal-niyfy-strip.png`
- Tags: motion=[slide-in, stagger, settle] · archetype=checklist · energy=measured · mood=clinical
- Use when: a multi-column project tracker / checklist dashboard fills in as proof of a system
- Motion: A dark project-management board lays itself out across the strip: a left rail of task rows and a top progress header are present from the first frame, then card panels populate column by column left-to-right, each filled checklist card sliding up into place a beat after its neighbor. The fill is staggered rather than simultaneous, with rows settling cleanly into their grid and no overshoot. The layout holds steady once columns are populated, reading as a calm reveal of an organized workspace.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.9378 · eased_energy_share=0.9991 · sparsity=0.0015 · spatial_concentration=0.0874 · mov_texture=13.0403)
- Source: https://www.youtube.com/watch?v=7_k1SUNIyfY @ 6:13-6:16

### logo-slide-up-settle-zmea
- Hero: `logo-slide-up-settle-zmea.png` · Strip: `logo-slide-up-settle-zmea-strip.png`
- Tags: motion=[slide-in, scale-bloom, settle] · archetype=title-card · energy=measured · mood=neutral
- Use when: a brand or tool logo establishes the topic at the open
- Motion: Against a dark gridded editor backdrop, the blue VS Code logo enters from the lower-left edge tiny and partly off-frame, then slides up and to the right while scaling toward full size. Across the strip it grows steadily frame to frame and drifts toward screen center, settling upright with no visible overshoot. The motion is a single smooth eased rise rather than a multi-element stagger.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.1015 · eased_energy_share=0.9731 · sparsity=0.2531 · spatial_concentration=0.4423 · mov_texture=12.5678)
- Source: https://www.youtube.com/watch?v=9qoVvtZ_MEA @ 0:50-0:52

### token-teleport-between-targets-zmea
- Hero: `token-teleport-between-targets-zmea.png` · Strip: `token-teleport-between-targets-zmea-strip.png`
- Tags: motion=[slide-in, snap, settle] · archetype=diagram-build · energy=measured · mood=playful
- Use when: a moving token jumps between two targets to illustrate a link or jump
- Motion: Two circle targets sit at the top — a dashed-outline ring on the left and a filled ring on the right — while a dark code card reading a href="#destination">Teleport! slides up from the bottom and settles mid-frame. An orange dot starts nested in the right target, then over the strip it snaps across toward the left dashed ring as the card finishes settling, dramatizing the anchor 'jump.' Card rise is a clean eased slide; the dot relocation reads as a quick snap rather than a smooth glide.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.9441 · eased_energy_share=0.9801 · sparsity=0.3414 · spatial_concentration=0.4878 · mov_texture=6.535)
- Source: https://www.youtube.com/watch?v=9qoVvtZ_MEA @ 1:49-1:52

### code-card-reveal-list-then-button-pop-zmea
- Hero: `code-card-reveal-list-then-button-pop-zmea.png` · Strip: `code-card-reveal-list-then-button-pop-zmea-strip.png`
- Tags: motion=[slide-in, mask-reveal, pop] · archetype=code-reveal · energy=measured · mood=neutral
- Use when: code reveals incrementally and its rendered output lands as payoff
- Motion: A dark code card listing a ul of li items rises from the bottom and climbs up the frame, line by line scrolling into view as a light rendered panel (Groceries / Recipe lists) sits above it. As the card reaches the top, an orange 'Click Me' button pops in at the lower-right in the final frames. The card travel is a steady eased upward slide; the button arrives late as a small discrete pop, giving the beat a two-stage build (code reveal, then UI payoff).
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.7473 · eased_energy_share=0.8883 · sparsity=0 · spatial_concentration=0.3134 · mov_texture=5.7422)
- Source: https://www.youtube.com/watch?v=9qoVvtZ_MEA @ 2:05-2:07

### word-pop-scale-on-grid-bohy4
- Hero: `word-pop-scale-on-grid-bohy4.png` · Strip: `word-pop-scale-on-grid-bohy4-strip.png`
- Tags: motion=[pop, scale-bloom, settle] · archetype=kinetic-type · energy=measured · mood=neutral
- Use when: a short phrase lands beat-by-beat as the spoken line is emphasized
- Motion: Over a dim blueprint grid, the phrase arrives one chunk at a time: 'they were' pops in bold and oversized, then immediately settles to a smaller resting weight as the next chunk 'probably' bursts in oversized in turn. Each word scale-blooms past its final size and eases back, so the cadence reads as a series of punctuated pops rather than a continuous slide. Frames hold on the grid between hits, then cut to black.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.4198 · eased_energy_share=0.9561 · sparsity=0.1346 · spatial_concentration=0.3544 · mov_texture=12.7378)
- Source: https://www.youtube.com/watch?v=CWyFVjboHY4 @ 0:06-0:08

### fast-forward-chevron-streak-transition-bohy4
- Hero: `fast-forward-chevron-streak-transition-bohy4.png` · Strip: `fast-forward-chevron-streak-transition-bohy4-strip.png`
- Tags: motion=[scale-bloom, blur-rack, wipe] · archetype=title-card · energy=punchy · mood=playful
- Use when: a 'skip ahead / speed up' moment punctuates a section change
- Motion: A purple double-chevron fast-forward glyph sits centered on a white card and pulses larger across the first frames, then smears into a horizontal motion-blur streak as the whole card stretches and dissolves. The streak resolves into a dark teal scanline screen, so the icon's blur-out doubles as the wipe into the next scene. The move is quick and elastic, with the chevron leading the directional streak left-to-right.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.2442 · eased_energy_share=0.9521 · sparsity=0.0831 · spatial_concentration=0.3431 · mov_texture=14.3311)
- Source: https://www.youtube.com/watch?v=CWyFVjboHY4 @ 1:32-1:34

### blur-rack-keyword-with-meme-cutouts-bohy4
- Hero: `blur-rack-keyword-with-meme-cutouts-bohy4.png` · Strip: `blur-rack-keyword-with-meme-cutouts-bohy4-strip.png`
- Tags: motion=[blur-rack, slide-in, settle] · archetype=kinetic-type · energy=measured · mood=playful
- Use when: a punchline keyword resolves out of blur after a setup contrast line
- Motion: A two-line contrast sets up first ('You don't need to' / 'You just need to') with small meme image cutouts dropped beneath each line on the grid. The payoff word 'stubborness' then racks into focus from a heavy horizontal blur, sliding slightly as it sharpens and settling crisp and large. The blur-to-sharp is the whole gesture; the final frame shows the word momentarily smearing again as it exits, so it both enters and leaves on a focus rack.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.3954 · eased_energy_share=0.9627 · sparsity=0.2516 · spatial_concentration=0.4784 · mov_texture=15.0121)
- Source: https://www.youtube.com/watch?v=CWyFVjboHY4 @ 2:10-2:16

### title-card-to-code-blur-streak-cut-bohy4
- Hero: `title-card-to-code-blur-streak-cut-bohy4.png` · Strip: `title-card-to-code-blur-streak-cut-bohy4-strip.png`
- Tags: motion=[blur-rack, wipe, slide-in] · archetype=title-card · energy=punchy · mood=serious
- Use when: a named mistake or chapter title hands off into the live code that demonstrates it
- Motion: A glowing cyan title 'Not Debugging Properly' holds steady over a dark dashboard with a left sidebar list, barely moving across the first three frames. It then shears into a fast horizontal motion-blur streak that smears the whole frame sideways, and the streak resolves into a dark syntax-highlighted code editor. The blur-streak is the designed transition between the title card and the code reveal, quick and directional left-to-right.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.7582 · eased_energy_share=0.8248 · sparsity=0.6864 · spatial_concentration=0.5333 · mov_texture=5.7288)
- Source: https://www.youtube.com/watch?v=CWyFVjboHY4 @ 4:42-4:44

### grid-icon-stagger-reveal-8sa5g
- Hero: `grid-icon-stagger-reveal-8sa5g.png` · Strip: `grid-icon-stagger-reveal-8sa5g-strip.png`
- Tags: motion=[stagger, pop, slide-in] · archetype=diagram-build · energy=punchy · mood=playful
- Use when: a short list of concept tokens lands one after another as the beat enumerates them
- Motion: Over a dark blueprint grid, glyph icons enter one at a time across the strip: a broom pops in first center-left, then a 404 magnifier card slides up beside it, then an SEO cloud and a 404 scroll fill in to its right, each landing into its own grid cell. The cadence is a clear left-to-right stagger of roughly one icon per frame, each popping to rest with a small settle rather than drifting. The grid stays fixed as the substrate while the icon row accretes, then the final frame hard-cuts to a dark rounded card on white.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.8879 · eased_energy_share=0.8642 · sparsity=0.18 · spatial_concentration=0.5348 · mov_texture=14.747)
- Source: https://www.youtube.com/watch?v=E9DL3G8sA5g @ 2:59-3:04

### blur-rack-word-then-site-push-in-kkqqe
- Hero: `blur-rack-word-then-site-push-in-kkqqe.png` · Strip: `blur-rack-word-then-site-push-in-kkqqe-strip.png`
- Tags: motion=[blur-rack, parallax-push, settle] · archetype=kinetic-type · energy=punchy · mood=neutral
- Use when: a single keyword lands first, then the product it names rushes onto frame
- Motion: Opens on a faint grid, then the lowercase word 'first' resolves out of a heavy horizontal blur-rack, snapping to crisp focus across two frames. The word clears and a full website page (centered headline plus hero) drives in under a strong motion-blur zoom/parallax-push, streaking toward camera before decelerating. By the last two frames the page has settled square and legible with no residual blur. Punchy two-stage cadence: type reveal, then push-in payoff.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.6341 · eased_energy_share=1 · sparsity=0.0719 · spatial_concentration=0.3287 · mov_texture=15.1184)
- Source: https://www.youtube.com/watch?v=Ham1K2KKqqE @ 1:07-1:10

### twin-logo-drift-morph-over-editor-kkqqe
- Hero: `twin-logo-drift-morph-over-editor-kkqqe.png` · Strip: `twin-logo-drift-morph-over-editor-kkqqe-strip.png`
- Tags: motion=[morph, parallax-drift, scale-bloom] · archetype=collage · energy=frenetic · mood=playful
- Use when: two competing tools or stacks are weighed side by side before one gives way
- Motion: Against a dimmed code-editor backdrop the Python and PHP logos sit paired in the lower-left. The pair drifts and scale-blooms slightly larger frame to frame while a large dark glyph cross-fades behind them. In the final frames the PHP wordmark morphs and dissolves into a different lowercase mark, the whole cluster softening as it transitions out. Fast, loose, frenetic drift rather than a clean settle.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.0652 · eased_energy_share=0.8471 · sparsity=0.5509 · spatial_concentration=0.7011 · mov_texture=8.8614)
- Source: https://www.youtube.com/watch?v=Ham1K2KKqqE @ 2:10-2:13

### staggered-benefit-cards-around-cube-spotlight-kkqqe
- Hero: `staggered-benefit-cards-around-cube-spotlight-kkqqe.png` · Strip: `staggered-benefit-cards-around-cube-spotlight-kkqqe-strip.png`
- Tags: motion=[stagger, slide-in, marker-sweep] · archetype=diagram-build · energy=measured · mood=neutral
- Use when: a feature set assembles around a central object as the value proposition builds
- Motion: On near-black, labeled benefit cards ('Manage on the Go', 'Blockchain Explorer', 'Mass Payouts', 'High-Yield Staking', 'Zero Commission Swap', 'Earn Cashback') fade and slide into a constellation ringing a central 3D cube. The build is staggered: the early frames show only a couple of cards lit, and each successive frame adds another node while a soft spotlight sweeps across them. By the last frame the full constellation is present and the cube is the bright focal anchor. Measured, deliberate assembly.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.8279 · eased_energy_share=0.9671 · sparsity=0.7624 · spatial_concentration=0.8212 · mov_texture=9.6973)
- Source: https://www.youtube.com/watch?v=Ham1K2KKqqE @ 4:35-4:38

### tumbling-js-logo-card-overshoot-7ir3e
- Hero: `tumbling-js-logo-card-overshoot-7ir3e.png` · Strip: `tumbling-js-logo-card-overshoot-7ir3e-strip.png`
- Tags: motion=[overshoot, settle, pop] · archetype=title-card · energy=punchy · mood=playful
- Use when: a brand or language mark gets introduced as a bouncy cold-open emblem
- Motion: A bright-yellow JS logo card pops onto a dark dot-grid and wobbles in place: across the strip it tilts left then right past vertical, the angular skew exaggerating an elastic overshoot before it settles upright. The black 'JS' glyph and a hard drop-shadow track the card's rotation, reinforcing the toy-like spring. Final frames show the card de-saturating and shrinking slightly as it begins to exit.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.6263 · eased_energy_share=0.3128 · sparsity=0.132 · spatial_concentration=0.4762 · mov_texture=13.848)
- Source: https://www.youtube.com/watch?v=OOc1A_7iR3E @ 0:00-0:08

### tech-stack-spec-card-swap-7ir3e
- Hero: `tech-stack-spec-card-swap-7ir3e.png` · Strip: `tech-stack-spec-card-swap-7ir3e-strip.png`
- Tags: motion=[mask-reveal, slide-in, settle] · archetype=device-mockup · energy=measured · mood=clinical
- Use when: you swap one labeled spec or tech-stack card for the next in a comparison
- Motion: A rounded dark card reading 'Built with / [logo] / JS JavaScript Core' sits on a faint grid, then fades and dims as it clears frame. After an empty grid beat a replacement card masks in from the right reading 'Runs on / [React logo] / JS JavaScript Ecosystem', settling into the same slot. The swap is a measured crossfade-plus-slide between two identically framed spec cards rather than an in-place morph.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.1446 · eased_energy_share=0.9597 · sparsity=0.2214 · spatial_concentration=0.401 · mov_texture=12.3091)
- Source: https://www.youtube.com/watch?v=OOc1A_7iR3E @ 1:16-1:23

### nope-card-pop-to-sticky-note-7ir3e
- Hero: `nope-card-pop-to-sticky-note-7ir3e.png` · Strip: `nope-card-pop-to-sticky-note-7ir3e-strip.png`
- Tags: motion=[scale-bloom, snap, slide-in] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: a punchline word lands hard then flips to its cheeky opposite
- Motion: On a crimson field a glassy 'STRICT LANGUAGE / NOPE / CLUB' card blooms up to full scale, the white 'NOPE' snapping crisp at peak before the whole card recedes and dims to deep maroon. The scene then cuts to near-black where a small lime square and a yellow-bordered sticky note reading 'JS PARTY (ANYTHING GOES)' snap into a dashed-outline frame. Quick, punchy beats with hard scale-ups rather than soft eases.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.9423 · eased_energy_share=0.8534 · sparsity=0.1462 · spatial_concentration=0.4644 · mov_texture=2.6406)
- Source: https://www.youtube.com/watch?v=OOc1A_7iR3E @ 1:29-1:32

### flexbox-cards-redistribute-with-code-label-qwlgk
- Hero: `flexbox-cards-redistribute-with-code-label-qwlgk.png` · Strip: `flexbox-cards-redistribute-with-code-label-qwlgk-strip.png`
- Tags: motion=[slide-in, settle, morph] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a parameter change is demonstrated by re-laying-out the same elements side-by-side with the code that drives it
- Motion: Three rounded color chips (green, blue, pink) sit inside a dark rounded container next to a small code panel reading container { justify-content: "..." }. Across the strip the chips slide horizontally to new gaps as the label cycles space-between, then space-around, then space-evenly, each value spawning its own stacked row so the redistributions read as a vertical comparison. Motion is a calm horizontal ease into the new spacing with no overshoot; chips settle flush to their justified positions and the code string is the only text that swaps.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.9905 · eased_energy_share=0.9392 · sparsity=0.4904 · spatial_concentration=0.6391 · mov_texture=5.1759)
- Source: https://www.youtube.com/watch?v=Q5a5ShQwlgk @ 0:57-0:59

### axis-key-title-card-labeled-chips-qwlgk
- Hero: `axis-key-title-card-labeled-chips-qwlgk.png` · Strip: `axis-key-title-card-labeled-chips-qwlgk-strip.png`
- Tags: motion=[mask-reveal, settle] · archetype=title-card · energy=calm · mood=clinical
- Use when: a definition or mnemonic lands as the takeaway before returning to the demo
- Motion: A centered two-line key resolves on a dark field: "Here's the key: justify-content = main axis, align-items = cross-axis," with justify-content tinted gold and align-items tinted blue. Below it a rounded container holds three numbered chips spaced evenly apart. The card holds clean and still as the takeaway, then the strip cuts to blurred screen-recording frames as it dissolves back to the editor; the designed motion is the calm settle of the typographic key, not the recording behind it.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.2284 · eased_energy_share=0.934 · sparsity=0.8779 · spatial_concentration=0.7123 · mov_texture=8.5343)
- Source: https://www.youtube.com/watch?v=Q5a5ShQwlgk @ 1:22-1:24

### rgb-split-glitch-hero-transition-0iqw4
- Hero: `rgb-split-glitch-hero-transition-0iqw4.png` · Strip: `rgb-split-glitch-hero-transition-0iqw4-strip.png`
- Tags: motion=[glitch, blur-rack, snap] · archetype=title-card · energy=frenetic · mood=tense
- Use when: a hard cut into a new section that should feel disruptive, like a system glitching to a reveal
- Motion: A website hero is torn apart by heavy RGB-split datamosh: horizontal scanline tears and chromatic-aberration ghosting smear the frame edge to edge across the first frames. A distorted headline starting 'The...' churns through the noise, the channels drifting apart and snapping back. By the last frames the glitch decays and the layout begins to re-cohere into a readable purple-tinted hero. Energy is violent and continuous rather than staged.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=6.0177 · eased_energy_share=0.6283 · sparsity=0.0685 · spatial_concentration=0.438 · mov_texture=9.3453)
- Source: https://www.youtube.com/watch?v=RXKq_S0IQw4 @ 1:44-1:47

### numbered-checklist-row-reveal-0iqw4
- Hero: `numbered-checklist-row-reveal-0iqw4.png` · Strip: `numbered-checklist-row-reveal-0iqw4-strip.png`
- Tags: motion=[stagger, slide-in, settle] · archetype=checklist · energy=punchy · mood=playful
- Use when: enumerating a ranked list of items where each row should land one at a time as a payoff
- Motion: Over a dark gradient card titled '7 Game-Changing AI Tools', numbered pill rows stack and reveal top-to-bottom: row 1, then 2, 3, 4 drop in as a staggered cascade, each a rounded bar with an index number and label. The newest row carries a small accent flourish (a pointing-hand icon) before settling. The stagger step is even and quick, each row easing into its slot with no overshoot, building a clean ranked list.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.9015 · eased_energy_share=0.9442 · sparsity=0.0806 · spatial_concentration=0.39 · mov_texture=14.894)
- Source: https://www.youtube.com/watch?v=RXKq_S0IQw4 @ 2:29-2:39

### stacked-logo-scale-bloom-reveal-0iqw4
- Hero: `stacked-logo-scale-bloom-reveal-0iqw4.png` · Strip: `stacked-logo-scale-bloom-reveal-0iqw4-strip.png`
- Tags: motion=[scale-bloom, pop, settle] · archetype=title-card · energy=punchy · mood=neutral
- Use when: introducing a second product or brand alongside one already on screen, as a head-to-head pairing
- Motion: A blue MySQL wordmark with its dolphin sits anchored over a dim terminal backdrop across the whole strip. Below it the PostgreSQL elephant logo scale-blooms in from nothing, popping up to full size and settling, then its 'PostgreSQL' wordmark fades on beneath. The reveal is bottom-anchored and additive, building the two databases into a side-by-side comparison rather than swapping one for the other.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=1.842 · eased_energy_share=0.9631 · sparsity=0.6688 · spatial_concentration=0.701 · mov_texture=7.5021)
- Source: https://www.youtube.com/watch?v=RXKq_S0IQw4 @ 3:09-3:11

### code-panel-sweep-to-stat-ring-0iqw4
- Hero: `code-panel-sweep-to-stat-ring-0iqw4.png` · Strip: `code-panel-sweep-to-stat-ring-0iqw4-strip.png`
- Tags: motion=[marker-sweep, draw-on, count-up] · archetype=code-reveal · energy=punchy · mood=clinical
- Use when: a build or processing step resolves into a single metric that quantifies the payoff
- Motion: Two dark code panels hold ghosted gray code lines while a bright magenta progress bar sweeps left-to-right across the top of the right panel, frame by frame extending like a scan line consuming the work. As it completes, the layout cuts to a large purple arc/ring with a bold '9%' centered and 'UI Development Time Saved' beneath. The sweep is the engine; the stat lands as the clean resolution, the ring framing the number as the payoff.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.1037 · eased_energy_share=0.97 · sparsity=0.3714 · spatial_concentration=0.584 · mov_texture=2.8342)
- Source: https://www.youtube.com/watch?v=RXKq_S0IQw4 @ 3:50-3:53

### labeled-skill-cards-orbit-build-bs9sk
- Hero: `labeled-skill-cards-orbit-build-bs9sk.png` · Strip: `labeled-skill-cards-orbit-build-bs9sk-strip.png`
- Tags: motion=[slide-in, settle, stagger] · archetype=diagram-build · energy=measured · mood=neutral
- Use when: two or more category labels populate around a central concept as the structure is introduced
- Motion: On a deep-purple field a faint 'Web Development' label sits center, then a rounded icon tile reading 'Front End' slides down and settles top-left while a matching 'Back End' tile settles top-right. Across the strip a large circular orbit ring grows around the centered 'Web Development' wordmark, the two skill tiles holding their corners as the ring scales up underneath. The settle is gentle with no overshoot — tiles ease into place and hold, the circle drifting outward frame to frame.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=9.0439 · eased_energy_share=0.8988 · sparsity=0.05 · spatial_concentration=0.244 · mov_texture=1.3376)
- Source: https://www.youtube.com/watch?v=ee2oaTBS9Sk @ 0:27-0:32

### logo-tile-snap-wordmark-blur-rack-bs9sk
- Hero: `logo-tile-snap-wordmark-blur-rack-bs9sk.png` · Strip: `logo-tile-snap-wordmark-blur-rack-bs9sk-strip.png`
- Tags: motion=[blur-rack, snap, pop] · archetype=kinetic-type · energy=punchy · mood=neutral
- Use when: a named tool or brand lands as a beat punctuation on a dark grid
- Motion: On a black grid the frame starts near-empty (just a small yellow sliver), then a bright yellow 'JS' tile snaps in hard with no easing. Immediately a lowercase 'express' wordmark racks from heavy horizontal motion-blur toward sharp focus across the next frames — smeared and ghosted at first, fully legible by the last grid frame. The beat resolves by cutting to a solid 'Back End' title card, so the whole move reads as a quick punch-in then a focus-pull settle.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.5159 · eased_energy_share=0.8426 · sparsity=0.0653 · spatial_concentration=0.4236 · mov_texture=16.1822)
- Source: https://www.youtube.com/watch?v=ee2oaTBS9Sk @ 1:59-2:01

### sticker-card-collage-blur-in-bs9sk
- Hero: `sticker-card-collage-blur-in-bs9sk.png` · Strip: `sticker-card-collage-blur-in-bs9sk-strip.png`
- Tags: motion=[pop, blur-rack, stagger] · archetype=collage · energy=punchy · mood=playful
- Use when: a payoff list of benefits or proof items assembles under a headline
- Motion: A bold 'Helps you:' headline holds at top while two flat sticker cards — a red 'I GOT THIS!' hand and a teal 'START TO GET UNSTUCK' figure — are already locked left of center. Across the strip a third image card pops in to their right, starting as a blurred warm-orange smear and racking into a sharper photo by the final frames. The two left stickers stay fixed as anchors while only the newest card resolves, giving a staggered build-up where each item snaps then sharpens.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=1.794 · eased_energy_share=0.8167 · sparsity=0.76 · spatial_concentration=0.7947 · mov_texture=3.5854)
- Source: https://www.youtube.com/watch?v=ee2oaTBS9Sk @ 3:49-3:53

### centered-word-swap-on-grid-xutwk
- Hero: `centered-word-swap-on-grid-xutwk.png` · Strip: `centered-word-swap-on-grid-xutwk-strip.png`
- Tags: motion=[kinetic-type, snap, settle] · archetype=kinetic-type · energy=punchy · mood=neutral
- Use when: a single emphasis word lands one at a time to drive a point home
- Motion: Over a faint dark-on-dark engineering grid, one big white word holds dead-center, then snaps out and is replaced by the next: 'best' to 'best' to 'use'. Each word arrives crisp with no drift, holds briefly, and cuts to the next on the beat. The grid stays fixed behind so the only motion is the clean word-by-word swap; the strip ends cutting back into a code editor.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.5167 · eased_energy_share=0.9428 · sparsity=0.084 · spatial_concentration=0.3449 · mov_texture=12.1573)
- Source: https://www.youtube.com/watch?v=tfzGsCxutWk @ 0:22-0:25

### motion-blur-smear-word-morph-xutwk
- Hero: `motion-blur-smear-word-morph-xutwk.png` · Strip: `motion-blur-smear-word-morph-xutwk-strip.png`
- Tags: motion=[morph, blur-rack, wipe] · archetype=title-card · energy=frenetic · mood=playful
- Use when: a fast graphic transition smears between two labelled concepts
- Motion: After a live-action cut, the word 'element' is dragged across frame as a heavy horizontal motion-blur smear, the letters stretching and ghosting left-to-right through three frames until they resolve toward a 'CSS' card flanked by dashed accents. The blur is the whole transition — it streaks, doubles the glyphs, then snaps to the destination graphic. A loose, energetic whip rather than a precise reveal.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.6993 · eased_energy_share=0.7403 · sparsity=0.0892 · spatial_concentration=0.356 · mov_texture=12.4208)
- Source: https://www.youtube.com/watch?v=tfzGsCxutWk @ 0:48-0:55

### ui-card-tumble-zoom-in-xutwk
- Hero: `ui-card-tumble-zoom-in-xutwk.png` · Strip: `ui-card-tumble-zoom-in-xutwk-strip.png`
- Tags: motion=[scale-bloom, blur-rack, settle] · archetype=device-mockup · energy=punchy · mood=playful
- Use when: a UI or product panel slams into frame as the reveal of a result
- Motion: A blue rounded card carrying orange UI elements rushes up from a small strip at the bottom, scaling and rotating in with strong radial motion blur so it tumbles toward the viewer. It overshoots large and slightly tilted, the orange controls smearing, then de-rotates and shrinks to rest as a clean framed panel in the final frame. Fast bloom-in with the blur bleeding off as it settles.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.0381 · eased_energy_share=0.9831 · sparsity=0.0401 · spatial_concentration=0.2586 · mov_texture=12.3685)
- Source: https://www.youtube.com/watch?v=tfzGsCxutWk @ 2:14-2:17

### code-editor-demo-then-chrome-title-xutwk
- Hero: `code-editor-demo-then-chrome-title-xutwk.png` · Strip: `code-editor-demo-then-chrome-title-xutwk-strip.png`
- Tags: motion=[typewriter, scale-bloom, kinetic-type] · archetype=code-reveal · energy=punchy · mood=neutral
- Use when: a code example runs live before its concept name is stamped on screen
- Motion: Opens on a VS Code window with CSS @keyframes alongside a live preview where a cyan rounded square animates; the editor then dissolves through a black-to-magenta gradient bloom that rises from the bottom. Out of that, a metallic chrome 'pseudo-classes' title settles centered on the grid before cutting back to the editor. Sequences a working demo into a glossy concept-label stamp rather than one continuous move.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.8813 · eased_energy_share=0.7193 · sparsity=0.1912 · spatial_concentration=0.3548 · mov_texture=8.2672)
- Source: https://www.youtube.com/watch?v=tfzGsCxutWk @ 3:21-3:27

### equation-overlay-warp-build-1kvyq
- Hero: `equation-overlay-warp-build-1kvyq.png` · Strip: `equation-overlay-warp-build-1kvyq-strip.png`
- Tags: motion=[parallax-push, mask-reveal, kinetic-type] · archetype=kinetic-type · energy=frenetic · mood=tense
- Use when: an abstract idea or formula is being introduced and the screen builds toward a concept reveal
- Motion: A glowing blue brain sits center frame, then the camera punches forward through a light-speed warp tunnel of radial streaks (parallax-push). The warp resolves into a flat cyan plate carrying the equation '= C + 273', which then composites over a backlit silhouette head as floating physics expressions ('= C + 2/3' and scattered terms) mask in around it. Layers arrive fast and overlapping rather than staggered cleanly; the equation overlay is the settle point, holding while satellite terms keep drifting in.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.3636 · eased_energy_share=0.9672 · sparsity=0.013 · spatial_concentration=0.4093 · mov_texture=11.8658)
- Source: https://www.youtube.com/watch?v=07oOCD1kVYQ @ 0:17-0:20

### equation-swarm-into-section-title-1kvyq
- Hero: `equation-swarm-into-section-title-1kvyq.png` · Strip: `equation-swarm-into-section-title-1kvyq-strip.png`
- Tags: motion=[kinetic-type, settle, pop] · archetype=title-card · energy=frenetic · mood=serious
- Use when: a dense build resolves into a section header that names the next part of the argument
- Motion: A backlit silhouette head is swarmed by dense handwritten-style physics equations that orbit and layer across the frame, intensifying to a bright bloom mid-strip. The chaos then resolves: the equations recede and a clean right-aligned section title pops on — 'Now, the second pillar is' — with the word 'second' emphasized in orange. The motion arc is busy-to-clean: equation-swarm energy collapsing into a single settled typographic line as the payoff.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.7968 · eased_energy_share=1 · sparsity=0.0157 · spatial_concentration=0.3394 · mov_texture=12.9388)
- Source: https://www.youtube.com/watch?v=07oOCD1kVYQ @ 1:32-1:35

### kinetic-label-stack-over-3d-tunnel-nlpu
- Hero: `kinetic-label-stack-over-3d-tunnel-nlpu.png` · Strip: `kinetic-label-stack-over-3d-tunnel-nlpu-strip.png`
- Tags: motion=[kinetic-type, pop, settle] · archetype=kinetic-type · energy=punchy · mood=serious
- Use when: naming the parts of a system one label at a time as the narration introduces them
- Motion: A glowing blue 3D tunnel/cube graphic pulses full-frame for the first three frames, its core flaring brighter then easing back. As the tunnel darkens to near-black, white headline labels pop in centered: 'Computer' lands first, then grows into a stacked 'Computer and Server' as a second line is added, and finally an orange 'operated by the VPN company' caption snaps in at the same anchor. Each label appears as a hard cut-in with no slide, settling immediately; the color shift from white to orange marks the payoff phrase.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=6.3023 · eased_energy_share=0.323 · sparsity=0.0111 · spatial_concentration=0.3023 · mov_texture=7.4671)
- Source: https://www.youtube.com/watch?v=4hjssRnLP-U @ 0:45-0:50

### flame-particle-overlay-on-desktop-nlpu
- Hero: `flame-particle-overlay-on-desktop-nlpu.png` · Strip: `flame-particle-overlay-on-desktop-nlpu-strip.png`
- Tags: motion=[particle, scale-bloom, draw-on] · archetype=code-reveal · energy=frenetic · mood=tense
- Use when: dramatizing a screen or interface under threat or being consumed
- Motion: A dark desktop screen with small windows sits behind animated orange flames that lick up from the bottom edge and corners. Across the strip the fire churns and blooms unevenly frame to frame, tongues rising and curling at the left and right margins while the center stays comparatively clear so the underlying UI remains readable. The flames never resolve into a static shape; they flicker continuously with turbulent, organic motion, framing the screen rather than wiping it.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.8401 · eased_energy_share=0.9814 · sparsity=0.2467 · spatial_concentration=0.582 · mov_texture=9.1154)
- Source: https://www.youtube.com/watch?v=4hjssRnLP-U @ 6:56-7:04

### ui-panel-slide-then-perspective-scroll-push-adso
- Hero: `ui-panel-slide-then-perspective-scroll-push-adso.png` · Strip: `ui-panel-slide-then-perspective-scroll-push-adso-strip.png`
- Tags: motion=[slide-in, parallax-push, snap] · archetype=device-mockup · energy=punchy · mood=neutral
- Use when: a product UI is introduced and then its content rushes past as the camera dives in
- Motion: Against full black, a tall nav/sidebar panel ('TECH...' header over a stack of menu rows) slides up and snaps into place center-frame across the first three frames. It then pivots into a steep right-leaning perspective and the row list scroll-pushes diagonally toward the viewer, lines streaking with motion blur as the camera dives down the list. Entry is a quick slide-settle; the exit is a continuous accelerating parallax-push rather than a fixed hold.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.0872 · eased_energy_share=0.9596 · sparsity=0.0008 · spatial_concentration=0.2376 · mov_texture=7.7392)
- Source: https://www.youtube.com/watch?v=_xZbCEaD_So @ 2:48-2:51

### logo-then-typewriter-caption-4uhkm
- Hero: `logo-then-typewriter-caption-4uhkm.png` · Strip: `logo-then-typewriter-caption-4uhkm-strip.png`
- Tags: motion=[typewriter, slide-in] · archetype=kinetic-type · energy=measured · mood=neutral
- Use when: a named subject is introduced and its tagline types itself out beside the brand mark
- Motion: Frame one holds a green Manjaro logo and wordmark settled at left on a near-black field. From frame two the caption types in character by character on the right half — a single blinking cursor advances 'M', 'Ma', then jumps to the full 'Manjaro is the accessible gateway', and the last frame wraps to a second line 'to'. No easing or overshoot; the cadence is the steady mechanical tick of a typewriter reveal, text staying flush-left with the logo anchored static throughout.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.2256 · eased_energy_share=0.5108 · sparsity=0.5958 · spatial_concentration=0.7486 · mov_texture=3.0408)
- Source: https://www.youtube.com/watch?v=b2E5HV4UhKM @ 2:22-2:26

### swiss-army-icon-tools-unfold-4uhkm
- Hero: `swiss-army-icon-tools-unfold-4uhkm.png` · Strip: `swiss-army-icon-tools-unfold-4uhkm-strip.png`
- Tags: motion=[draw-on, pop, settle] · archetype=diagram-build · energy=punchy · mood=playful
- Use when: a single icon assembles part by part to dramatize a 'one thing, many capabilities' point
- Motion: Opens on an empty slate field with only a thin diagonal needle line hinting in. The red Swiss-Army-knife body snaps in with a long flat drop-shadow, then tools deploy in stages: first the blade swings open up-left, then a corkscrew and a scissor-like tool unfold downward, each new implement popping into place across successive frames until the knife is fully fanned out. The build is additive and staged rather than smoothly tweened — each tool lands as a discrete pop, the shadow lengthening to match.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.3496 · eased_energy_share=0.9851 · sparsity=0.1468 · spatial_concentration=0.5703 · mov_texture=2.9967)
- Source: https://www.youtube.com/watch?v=b2E5HV4UhKM @ 2:48-2:50

### two-option-language-pick-icon-pop-v0vw
- Hero: `two-option-language-pick-icon-pop-v0vw.png` · Strip: `two-option-language-pick-icon-pop-v0vw-strip.png`
- Tags: motion=[pop, slide-in] · archetype=kinetic-type · energy=punchy · mood=playful
- Use when: an either/or choice resolves and the second option lands as the punchline
- Motion: A left-aligned text card holds two stacked clauses, 'knowing Python or' over 'learning'. On the next frame the second option completes: the word 'JavaScript' slides in to finish the lower line, each language name carrying its own small colored emoji/icon that pops in beside it. The type is static-weight and the move is a single quick snap-in of the new word rather than a stagger, settling immediately with no overshoot, before the sequence hard-cuts away to live-action B-roll.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.8992 · eased_energy_share=0.8854 · sparsity=0.1363 · spatial_concentration=0.5892 · mov_texture=9.2092)
- Source: https://www.youtube.com/watch?v=y5F5Zx-V0Vw @ 0:12-0:15

### code-panels-reveal-with-kinetic-caption-sjsm0
- Hero: `code-panels-reveal-with-kinetic-caption-sjsm0.png` · Strip: `code-panels-reveal-with-kinetic-caption-sjsm0-strip.png`
- Tags: motion=[mask-reveal, kinetic-type, slide-in] · archetype=code-reveal · energy=punchy · mood=neutral
- Use when: a list of things-you'll-learn lands while code fills the frame and a phrase punches in word-by-word
- Motion: Across the strip the dark code/terminal panels populate left-to-right, each successive frame adding more revealed lines and a new editor panel so the frame keeps densifying rather than cutting. Over the top-right, a short caption builds as kinetic type — "You'll Learn Things Like" — with the middle word color-accented (red) so it pops out of the white run. The reveal reads as steady, punctuated additions settling into a full screen; no camera move, the motion is all content snapping in panel by panel.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.9031 · eased_energy_share=0.6712 · sparsity=0.0784 · spatial_concentration=0.5424 · mov_texture=15.4358)
- Source: https://www.youtube.com/watch?v=1HDrk9SJSM0 @ 1:44-1:52

### brain-bowl-character-lift-label-card-jxylk
- Hero: `brain-bowl-character-lift-label-card-jxylk.png` · Strip: `brain-bowl-character-lift-label-card-jxylk-strip.png`
- Tags: motion=[pop, slide-in, settle] · archetype=diagram-build · energy=punchy · mood=playful
- Use when: a memorable acronym or framework is introduced one letter at a time
- Motion: An illustrated green figure with an open brain-bowl head sits center on a flat green field. Across the strip a yellow cup pops into frame near the head, then the figure raises it in two stepped poses as if pouring something into the brain, each pose snapping in rather than tweening smoothly. The final frame cuts to a black panel where a stacked label card reads T = Think / E = Explain / C = ???, the lines settling in as a tidy left-aligned list with no further drift.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.4367 · eased_energy_share=0.8902 · sparsity=0.0377 · spatial_concentration=0.4252 · mov_texture=10.8371)
- Source: https://www.youtube.com/watch?v=FFGf5nJXylk @ 3:00-3:04

### landing-page-roadmap-node-reveal-zoom-jxylk
- Hero: `landing-page-roadmap-node-reveal-zoom-jxylk.png` · Strip: `landing-page-roadmap-node-reveal-zoom-jxylk-strip.png`
- Tags: motion=[mask-reveal, parallax-push, draw-on] · archetype=device-mockup · energy=measured · mood=neutral
- Use when: a product or roadmap is walked through as the credible payoff to a pitch
- Motion: A designed web UI fills the frame: a bold two-tone headline (The Most Structured Way to Prepare for Coding Interviews) over a connected roadmap of rounded node cards. Across the strip the view pushes and scrolls down the page so the headline drifts up and out while the roadmap diagram draws on, its colored node cards and connector lines revealing in sequence. The last frames zoom into the dark node grid with a CTA button settling at the base, a calm parallax descent rather than a hard cut.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.3253 · eased_energy_share=0.6858 · sparsity=0.0396 · spatial_concentration=0.2308 · mov_texture=15.5468)
- Source: https://www.youtube.com/watch?v=FFGf5nJXylk @ 3:16-3:19

### thinking-contrast-cards-with-meditating-monkey-jxylk
- Hero: `thinking-contrast-cards-with-meditating-monkey-jxylk.png` · Strip: `thinking-contrast-cards-with-meditating-monkey-jxylk-strip.png`
- Tags: motion=[slide-in, stagger, settle] · archetype=split-contrast · energy=measured · mood=warm
- Use when: two framings of the same idea are contrasted before landing a one-line takeaway
- Motion: Two stacked dark label bars slide in left-to-right reading What You're Thinking then How You're Thinking, staggered so the second lands after the first. The frame then opens to an illustrated monkey meditating cross-legged on a rock against an icy-blue cavern backdrop, holding a near-static calm pose while the camera barely breathes. The strip closes on a black panel with the orange-accented line Communication Is Very Important settling in as the takeaway.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.9784 · eased_energy_share=0.9702 · sparsity=0.3013 · spatial_concentration=0.6617 · mov_texture=9.4191)
- Source: https://www.youtube.com/watch?v=FFGf5nJXylk @ 6:46-6:48

### kinetic-line-over-paper-storm-then-prohibition-icon-jpu2g
- Hero: `kinetic-line-over-paper-storm-then-prohibition-icon-jpu2g.png` · Strip: `kinetic-line-over-paper-storm-then-prohibition-icon-jpu2g-strip.png`
- Tags: motion=[kinetic-type, particle, pop] · archetype=kinetic-type · energy=frenetic · mood=tense
- Use when: a cold-open premise lands as a swirl, then a hard 'no' snaps in to name the antagonist
- Motion: Center-set headline ('This is the story of a Browser') holds over a full-frame storm of tumbling white paper scraps drifting on a dark field; the line swaps to a second phrase ('For Browsing The Internet') while the particles keep churning. The strip then hard-cuts to a glowing red circle-slash prohibition icon that pops onto a glitch-textured cyan/magenta panel, scaling up with a small icon badge settling into the lower-left corner. Cadence is two beats: continuous ambient particle drift under swapping kinetic type, then a punchy icon snap.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.9818 · eased_energy_share=1 · sparsity=0.0291 · spatial_concentration=0.2289 · mov_texture=14.3021)
- Source: https://www.youtube.com/watch?v=MI1ZMFjpU2g @ 0:01-0:05

### logo-hold-then-definition-card-slide-in-jpu2g
- Hero: `logo-hold-then-definition-card-slide-in-jpu2g.png` · Strip: `logo-hold-then-definition-card-slide-in-jpu2g-strip.png`
- Tags: motion=[slide-in, settle] · archetype=quote-card · energy=measured · mood=neutral
- Use when: a key term gets defined — a logo holds while an explainer card slides in to deliver the definition
- Motion: The first four frames hold a large red Brave lion logo centered over a static blue crowd-silhouette backdrop, essentially a beat-anchoring hold. On the final frame a dark titled definition card ('What Is an Initial Coin Offering (ICO)?' plus a paragraph of body copy) slides in from the right and settles flush against the right edge. The motion is a single clean panel entrance after a long static hold — calm, no overshoot.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.0738 · eased_energy_share=0.9141 · sparsity=0.6114 · spatial_concentration=0.5029 · mov_texture=6.1674)
- Source: https://www.youtube.com/watch?v=MI1ZMFjpU2g @ 2:31-2:34

### build-your-own-card-grid-scroll-to-pill-tabs-jpu2g
- Hero: `build-your-own-card-grid-scroll-to-pill-tabs-jpu2g.png` · Strip: `build-your-own-card-grid-scroll-to-pill-tabs-jpu2g-strip.png`
- Tags: motion=[slide-in, parallax-drift, settle] · archetype=code-reveal · energy=measured · mood=clinical
- Use when: a catalog of options or features reveals as a scrolling card grid that lands on a tabbed selector
- Motion: A two-column grid of dark 'Build your own X' challenge cards (shell, Redis, grep, interpreter, Kafka, SQLite, DNS server, HTTP server) drifts upward across the strip, each card carrying a small colored language/icon glyph on its right edge. The grid pans steadily as new rows scroll into frame, then the final frame settles on a 'Language Tracks' header with a row of selectable pill tabs. Cadence is a continuous measured vertical scroll resolving into a static tabbed UI.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.3473 · eased_energy_share=0.9558 · sparsity=0.1454 · spatial_concentration=0.2839 · mov_texture=6.9034)
- Source: https://www.youtube.com/watch?v=MI1ZMFjpU2g @ 5:41-5:47

### graffiti-the-end-card-with-comment-cta-jzg7y
- Hero: `graffiti-the-end-card-with-comment-cta-jzg7y.png` · Strip: `graffiti-the-end-card-with-comment-cta-jzg7y-strip.png`
- Tags: motion=[settle, pop] · archetype=title-card · energy=measured · mood=playful
- Use when: the outro beat that closes the video and asks for engagement
- Motion: A hand-drawn graffiti 'THE END' lockup sits centered on a flat gray card and holds steady across the middle frames with almost no movement, reading as a settled title hold. The first frame layers an orange-and-white 'Sustainability Can Follow' lower-third beneath the mark, and the final frame snaps to a separate 'DROP A COMMENT' graffiti graphic with a downward arrow. The motion is a held card bookended by two punchy text pops rather than a continuous reveal.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.5957 · eased_energy_share=1 · sparsity=0.1152 · spatial_concentration=0.4046 · mov_texture=9.5786)
- Source: https://www.youtube.com/watch?v=Mw21BrJzg7Y @ 7:47-7:49

### mascot-prop-slide-in-subscribe-pop-jzg7y
- Hero: `mascot-prop-slide-in-subscribe-pop-jzg7y.png` · Strip: `mascot-prop-slide-in-subscribe-pop-jzg7y-strip.png`
- Tags: motion=[slide-in, pop, snap] · archetype=title-card · energy=punchy · mood=playful
- Use when: an outro beat that pairs a character gag with a subscribe call-to-action
- Motion: A composited stars-and-stripes character with sunglasses sits on a black field while a wooden bat prop slides in horizontally from the left, extending fully across the frame by the middle. As the prop settles into the character's hands, a red YouTube subscribe button pops in at the lower right in the final frame. The cadence is a single slide-in gesture that lands, then a hard snap to the CTA button.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.8276 · eased_energy_share=0.857 · sparsity=0.0732 · spatial_concentration=0.4655 · mov_texture=15.6633)
- Source: https://www.youtube.com/watch?v=Mw21BrJzg7Y @ 7:54-7:56

### red-word-title-card-cut-q09xs
- Hero: `red-word-title-card-cut-q09xs.png` · Strip: `red-word-title-card-cut-q09xs-strip.png`
- Tags: motion=[kinetic-type, snap] · archetype=title-card · energy=punchy · mood=serious
- Use when: a section transition lands a two-word claim with one word as the hook
- Motion: After several live-action B-roll frames, the strip hard-cuts to a black title card: a centered two-word phrase ('Global Scale') snaps in full-size with no slide, then cuts straight to a second card ('Different Era') where the second word ('Era') is set in red to carry the emphasis. There is no easing ramp visible across frames — each card is a clean hold that swaps on the cut, so the motion is the cut itself plus the red-word color accent doing the punctuation.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.6852 · eased_energy_share=0.7853 · sparsity=0.5025 · spatial_concentration=0.6421 · mov_texture=3.6303)
- Source: https://www.youtube.com/watch?v=PHU2Z9q09Xs @ 4:58-5:10

### course-card-ui-zoom-into-player-q09xs
- Hero: `course-card-ui-zoom-into-player-q09xs.png` · Strip: `course-card-ui-zoom-into-player-q09xs-strip.png`
- Tags: motion=[scale-bloom, settle, mask-reveal] · archetype=device-mockup · energy=measured · mood=neutral
- Use when: a product/app payoff zooms from an overview into one focused screen
- Motion: The strip opens on a dense dark 'Courses' catalog grid, holds on the full-page layout, then cuts to a centered 'Learn Python / Why Learn Python?' panel that scales up and settles as the focal card. The Python logo card grows from the left while a yellow accent frame builds behind it, and the final frames mask-reveal a video player with a blue play button and a caption strip. The cadence reads as an overview-to-detail push: wide grid, then a single card blooms to center and resolves into a playable mockup.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.9235 · eased_energy_share=0.7646 · sparsity=0.0575 · spatial_concentration=0.1352 · mov_texture=9.6572)
- Source: https://www.youtube.com/watch?v=PHU2Z9q09Xs @ 5:31-5:37

### doodle-draw-on-wow-pop-zhkze
- Hero: `doodle-draw-on-wow-pop-zhkze.png` · Strip: `doodle-draw-on-wow-pop-zhkze-strip.png`
- Tags: motion=[draw-on, pop, wipe] · archetype=kinetic-type · energy=playful · mood=playful
- Use when: a punchline lands and a reaction word needs to pop over the frame
- Motion: Opens on a retro iMac illustration, then wipes to a blank 'LONG DOGE CHALLENGE' web page. Across the middle frames a hand-drawn stick figure draws itself onto the empty canvas, line by line, while a bold 'WOW' word pops in at the lower right and then again top-center. The doodle stays put once drawn; the WOW words are punchy single-frame pop-ins rather than eased slides. No camera move — everything is overlaid flat on the page.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.6399 · eased_energy_share=0.7539 · sparsity=0.578 · spatial_concentration=0.6844 · mov_texture=17.1016)
- Source: https://www.youtube.com/watch?v=dghs0gzHkZE @ 0:08-0:12

### prd-title-card-lower-third-slide-zhkze
- Hero: `prd-title-card-lower-third-slide-zhkze.png` · Strip: `prd-title-card-lower-third-slide-zhkze-strip.png`
- Tags: motion=[slide-in, settle] · archetype=title-card · energy=measured · mood=neutral
- Use when: a chapter or topic title needs to establish before the content scrolls in
- Motion: Holds on a large left-aligned 'PRD for Vibe Coding' title card while a small profile/lower-third card slides up into the bottom-left and settles. After the title establishes, the frame cuts to a scrolling article document with a table-of-contents panel and a comparison block. The title-card open is the designed beat: a steady slide-and-settle of the corner card with no overshoot, calm and measured, no camera move.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.7715 · eased_energy_share=0.3182 · sparsity=0.0669 · spatial_concentration=0.3938 · mov_texture=20.233)
- Source: https://www.youtube.com/watch?v=dghs0gzHkZE @ 2:05-2:07

### lightning-title-into-node-graph-xtauy
- Hero: `lightning-title-into-node-graph-xtauy.png` · Strip: `lightning-title-into-node-graph-xtauy-strip.png`
- Tags: motion=[mask-reveal, stagger, settle] · archetype=diagram-build · energy=measured · mood=serious
- Use when: a connected system is introduced and its parts wire up one tier at a time
- Motion: Opens on a dark hero slide dominated by a glowing orange lightning bolt with a short headline and a small pill button lower-left. Across the middle of the strip the hero dissolves and a node graph builds in its place: rows of icon nodes fade up and link with thin connectors, populating roughly top-down then filling the lower rows. Each tier settles softly with no overshoot, keeping the cadence calm and deliberate rather than snappy; the bolt motif lingers faintly behind the graph as ambient glow.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.4827 · eased_energy_share=0.9473 · sparsity=0.1739 · spatial_concentration=0.428 · mov_texture=6.934)
- Source: https://www.youtube.com/watch?v=oB3czbxTAUY @ 0:44-0:46

### pr-ui-into-diff-fill-xtauy
- Hero: `pr-ui-into-diff-fill-xtauy.png` · Strip: `pr-ui-into-diff-fill-xtauy-strip.png`
- Tags: motion=[wipe, slide-in, settle] · archetype=code-reveal · energy=frenetic · mood=neutral
- Use when: a change set lands and the code diff fills in as the payoff
- Motion: Begins on a GitHub 'Open a pull request' form (left two frames), then hard-cuts to a unified diff panel that fills progressively. Across the right four frames the red/green hunks build top-to-bottom, each block of added/removed lines wiping into place so the panel grows denser frame by frame until it is packed with colored diff rows. The motion is the steady downward fill of the diff rather than any easing on individual elements; pace reads quick and punchy as the rows stack.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.629 · eased_energy_share=0.7601 · sparsity=0.0535 · spatial_concentration=0.44 · mov_texture=5.7881)
- Source: https://www.youtube.com/watch?v=oB3czbxTAUY @ 7:22-7:25

### mascot-exit-document-slide-reveal-5rlhi
- Hero: `mascot-exit-document-slide-reveal-5rlhi.png` · Strip: `mascot-exit-document-slide-reveal-5rlhi-strip.png`
- Tags: motion=[slide-in, wipe, settle] · archetype=device-mockup · energy=punchy · mood=playful
- Use when: a prop or document takes over the frame as the topic shifts to a concrete artifact
- Motion: A large blue mascot character sits center-left; across the strip it tracks leftward and wipes off-frame while a 'JOB APPLICATION FORM' page slides in from the right behind it. The form starts cropped at the right edge and slides left to settle near-center, its body text resolving from partial to fully legible. The exchange is a single linked slide — character out, document in — with the page easing to a stop rather than snapping.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=6.2452 · eased_energy_share=1 · sparsity=0.1143 · spatial_concentration=0.394 · mov_texture=14.1331)
- Source: https://www.youtube.com/watch?v=vHxw5Z5rLHI @ 2:10-2:12

### two-tone-title-over-money-particle-rain-5rlhi
- Hero: `two-tone-title-over-money-particle-rain-5rlhi.png` · Strip: `two-tone-title-over-money-particle-rain-5rlhi-strip.png`
- Tags: motion=[kinetic-type, particle, pop] · archetype=title-card · energy=frenetic · mood=playful
- Use when: a punchy headline lands as the payoff over an energetic textured background
- Motion: Centered two-tone headline 'These Side Hustles' (white + orange) holds on black while paper-money bills tumble and scatter across the full frame behind it. The cash particles rotate and fall at varying speeds frame to frame, drifting down and outward, so the type stays fixed and readable while the field churns around it. The headline pops in early and holds steady; all the motion energy lives in the particle rain.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.3311 · eased_energy_share=1 · sparsity=0.0268 · spatial_concentration=0.2253 · mov_texture=13.8471)
- Source: https://www.youtube.com/watch?v=vHxw5Z5rLHI @ 2:33-2:36

### tilting-balance-scale-compare-gra0
- Hero: `tilting-balance-scale-compare-gra0.png` · Strip: `tilting-balance-scale-compare-gra0-strip.png`
- Tags: motion=[settle, slide-in, wipe] · archetype=split-contrast · energy=measured · mood=clinical
- Use when: a beat weighs two options against each other before naming the tradeoff
- Motion: Two side-by-side seesaw diagrams hold the frame — SQL vs NoSQL cards balanced on one fulcrum, Batch vs Stream on the other, each tilted to show weight. The pair sits settled for most of the strip, then in the last two frames the whole comparison wipes out and clears toward empty as the next graphic's stacked gold cube blocks begin appearing bottom-center. Reads as a designed scene-to-scene handoff out of a balance-metaphor diagram rather than a single entrance.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.5958 · eased_energy_share=0.9338 · sparsity=0.5479 · spatial_concentration=0.4233 · mov_texture=0.5571)
- Source: https://www.youtube.com/watch?v=1nENigGr-a0 @ 0:03-0:06

### db-table-columns-stagger-build-gra0
- Hero: `db-table-columns-stagger-build-gra0.png` · Strip: `db-table-columns-stagger-build-gra0-strip.png`
- Tags: motion=[stagger, slide-in, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a structured record or schema assembles column by column as the payoff
- Motion: Starts on a near-empty dark frame, then a 'Primary' key label and a small DB glyph draw in upper-left. A gray header bar slides in from the left and the gold column blocks (product_id, first_name, age) stagger in left-to-right beneath it, each cell snapping into the table grid a beat after the last. By the final frame the full row of populated columns has settled flush under the header — a clean accumulating table-build.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.8554 · eased_energy_share=0.9013 · sparsity=0.3962 · spatial_concentration=0.5363 · mov_texture=5.6775)
- Source: https://www.youtube.com/watch?v=1nENigGr-a0 @ 0:27-0:29

### paired-device-nodes-arrow-pop-gra0
- Hero: `paired-device-nodes-arrow-pop-gra0.png` · Strip: `paired-device-nodes-arrow-pop-gra0-strip.png`
- Tags: motion=[pop, slide-in, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: two endpoints sync over a link and a transaction lands between them
- Motion: Two ATM/terminal device icons sit linked by a horizontal arrow, each labeled 'Balance: $10', holding steady through the first frames. In the back half a cash-note glyph and a small person icon pop in along the bottom edge below the link, punctuating the transaction. The node pair stays anchored while the supporting icons appear underneath — a settled two-endpoint diagram with a late accent pop.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.9102 · eased_energy_share=0.954 · sparsity=0.3238 · spatial_concentration=0.5639 · mov_texture=3.1074)
- Source: https://www.youtube.com/watch?v=1nENigGr-a0 @ 2:51-2:53

### article-ui-reveal-subscribe-lowerthird-gra0
- Hero: `article-ui-reveal-subscribe-lowerthird-gra0.png` · Strip: `article-ui-reveal-subscribe-lowerthird-gra0-strip.png`
- Tags: motion=[scale-bloom, slide-in, settle] · archetype=device-mockup · energy=measured · mood=warm
- Use when: a product or page is shown off and a subscribe prompt slides in to close the beat
- Motion: A blog/article page mockup scales up from a thin strip into a full multi-column layout, blooming into focus across the first frames. A 'blog.b...' browser chrome bar fades in at the top, then a ByteByteGo subscribe lower-third card slides up from the bottom-right corner and settles in the last two frames. Layered reveal: page mockup blooms, chrome lands, CTA card slides in last.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.7677 · eased_energy_share=0.9605 · sparsity=0.5119 · spatial_concentration=0.6131 · mov_texture=18.2168)
- Source: https://www.youtube.com/watch?v=1nENigGr-a0 @ 4:52-4:56

### graphql-flow-diagram-draw-on-r88xu
- Hero: `graphql-flow-diagram-draw-on-r88xu.png` · Strip: `graphql-flow-diagram-draw-on-r88xu-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=diagram-build · energy=calm · mood=clinical
- Use when: an architecture flows step by step from request to backing store
- Motion: A GraphQL query code box appears top-center first, then a desktop + mobile 'GraphQL client' pair fade in on the left. Arrows draw on toward a central pink server/resolver icon, then a second arrow extends right and a database cylinder strokes itself on at the far right. The build is left-to-right and additive, one node per frame with a calm settle and no overshoot — pieces hold once placed rather than bouncing.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.3704 · eased_energy_share=0.891 · sparsity=0.7716 · spatial_concentration=0.7247 · mov_texture=2.3719)
- Source: https://www.youtube.com/watch?v=2g1G8Jr88xU @ 1:39-1:42

### ai-logo-grid-row-pop-r88xu
- Hero: `ai-logo-grid-row-pop-r88xu.png` · Strip: `ai-logo-grid-row-pop-r88xu-strip.png`
- Tags: motion=[pop, stagger, settle] · archetype=collage · energy=measured · mood=neutral
- Use when: a roster of brands or options reveals as a populating grid
- Motion: On a dark rounded card, brand logos pop in row by row: DeepSeek + Flux first, then DALL-E and Gemini fill the top row, then a second row of Claude, Kling AI and Runway snaps in beneath. Each logo fades-and-pops with a small scale settle rather than sliding, and the rows stagger top-to-bottom so the grid fills as a sequence. The card glow holds steady underneath while the logos land.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.5786 · eased_energy_share=0.4843 · sparsity=0.3392 · spatial_concentration=0.4537 · mov_texture=1.9621)
- Source: https://www.youtube.com/watch?v=2g1G8Jr88xU @ 2:07-2:11

### stateful-stateless-balance-scale-build-r88xu
- Hero: `stateful-stateless-balance-scale-build-r88xu.png` · Strip: `stateful-stateless-balance-scale-build-r88xu-strip.png`
- Tags: motion=[slide-in, stagger, settle] · archetype=diagram-build · energy=calm · mood=neutral
- Use when: two approaches are weighed against each other as a tradeoff
- Motion: A balance-scale metaphor assembles left-to-right: first a single labeled gray box drops onto a tilted seesaw beam over a triangle fulcrum, then a second box and beam arm appear so two stacks face off. In the final frames stacked labels (Client / Application / Data vs Client / App) populate inside each box and the 'Stateful vs Stateless' title fades in up top. The build staggers element by element with a calm settle, the beam holding its tilt rather than rocking.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.4421 · eased_energy_share=0.9244 · sparsity=0.5272 · spatial_concentration=0.521 · mov_texture=0.4882)
- Source: https://www.youtube.com/watch?v=2g1G8Jr88xU @ 3:07-3:10

### icon-row-detection-labels-slide-in-vo7cy
- Hero: `icon-row-detection-labels-slide-in-vo7cy.png` · Strip: `icon-row-detection-labels-slide-in-vo7cy-strip.png`
- Tags: motion=[slide-in, typewriter, settle] · archetype=diagram-build · energy=punchy · mood=clinical
- Use when: a capability list builds up node-by-node as each feature is named
- Motion: A blue 'Motion Detection' runner icon already sits left of center; across the strip a second node enters from the right as a car icon framed by a red bounding box and a cyan detection cone, and its 'Vehicle Detection' caption types on letter-by-letter (Ve, Vehi, then full). A third 'Package' label begins typing in at the far right as the row extends. The reveal is a steady left-to-right node addition with each label completing on a short typewriter beat, no overshoot — elements snap into their grid slots and hold.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.9724 · eased_energy_share=0.8493 · sparsity=0.108 · spatial_concentration=0.3083 · mov_texture=3.3485)
- Source: https://www.youtube.com/watch?v=5kHpeVvO7cY @ 0:53-0:55

### pipeline-ml-node-scale-bloom-vo7cy
- Hero: `pipeline-ml-node-scale-bloom-vo7cy.png` · Strip: `pipeline-ml-node-scale-bloom-vo7cy-strip.png`
- Tags: motion=[scale-bloom, slide-in, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a processing stage lands as the centerpiece of a pipeline diagram
- Motion: A vertical flow is already wired — green 'Event Trigger' down to a 'Download Video Clip' cloud node. Across the strip a yellow ML 'brain' card blooms in upper-right, starting small and scaling up to full size as its label resolves ('ML', then 'ML Vehicle Det...'), while a connector arrow draws rightward from the download node to a small video thumbnail that fades in below it. The new node grows and settles without overshoot; the supporting arrow and thumbnail arrive a beat later, giving a measured two-stage build.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.2071 · eased_energy_share=0.9511 · sparsity=0.15 · spatial_concentration=0.4929 · mov_texture=3.2723)
- Source: https://www.youtube.com/watch?v=5kHpeVvO7cY @ 1:11-1:13

### architecture-http-arrow-draw-backend-pop-vo7cy
- Hero: `architecture-http-arrow-draw-backend-pop-vo7cy.png` · Strip: `architecture-http-arrow-draw-backend-pop-vo7cy-strip.png`
- Tags: motion=[draw-on, pop, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a request hop connects two services in a high-level architecture sketch
- Motion: A single dark camera/phone node sits left under a 'High-Level Architecture' heading and holds for the first frames. Then a horizontal connector draws on to the right, its 'HTTP Request' label appearing along the line, and a cyan 'Backend' pill pops in at the arrow's head — empty rounded rectangle first, then filling with its label. The build is sparse and deliberate: node holds, line draws across, destination pops and settles, reading as one clean request hop.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.4612 · eased_energy_share=0.9533 · sparsity=0.5916 · spatial_concentration=0.6512 · mov_texture=2.6399)
- Source: https://www.youtube.com/watch?v=5kHpeVvO7cY @ 1:56-1:58

### digit-counter-rolls-up-beside-static-icons-kphlu
- Hero: `digit-counter-rolls-up-beside-static-icons-kphlu.png` · Strip: `digit-counter-rolls-up-beside-static-icons-kphlu-strip.png`
- Tags: motion=[count-up, settle, mask-reveal] · archetype=stat-hero · energy=calm · mood=neutral
- Use when: a running tally or scale number ticks up to its landing value as the payoff
- Motion: Three brand logos and a node-cluster + globe icon hold static across the whole strip while the only motion lives in the right column: a boxed digit counter rolls up through values (empty, then 0, then 4, then 42) as a small server-stack glyph masks into view beneath it. The count is monospace and stepped rather than smooth, each digit snapping into its slot. Energy is low and the layout never moves, so the number is the entire focal beat.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.4859 · eased_energy_share=0.9832 · sparsity=0.7155 · spatial_concentration=0.7178 · mov_texture=2.4449)
- Source: https://www.youtube.com/watch?v=6u25GckPhLU @ 0:14-0:18

### code-panel-slides-from-monitor-then-red-x-stamps-kphlu
- Hero: `code-panel-slides-from-monitor-then-red-x-stamps-kphlu.png` · Strip: `code-panel-slides-from-monitor-then-red-x-stamps-kphlu-strip.png`
- Tags: motion=[slide-in, pop, overshoot] · archetype=code-reveal · energy=measured · mood=serious
- Use when: you reveal a code snippet or approach and then mark it as wrong or rejected
- Motion: A dashed connector line draws out from a small monitor/user glyph on the left and a dark code panel (a def sign_in function) slides in along it and settles on the right. Once the code is seated, a large red X scales up over it from small to oversized, overshooting well past the panel edges in the final frames so it dominates the frame. The two-stage cadence reads clearly: calm reveal of the snippet, then an emphatic rejection stamp that pops with weight.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.5834 · eased_energy_share=0.8694 · sparsity=0.765 · spatial_concentration=0.8086 · mov_texture=4.7887)
- Source: https://www.youtube.com/watch?v=6u25GckPhLU @ 1:03-1:05

### url-link-tree-draws-on-node-by-node-kphlu
- Hero: `url-link-tree-draws-on-node-by-node-kphlu.png` · Strip: `url-link-tree-draws-on-node-by-node-kphlu-strip.png`
- Tags: motion=[draw-on, stagger, slide-in] · archetype=diagram-build · energy=measured · mood=neutral
- Use when: a branching structure or graph builds out to show how something fans out from a root
- Motion: Under a 'Why Is This Hard?' header, a URL link-tree grows left-to-right: a root node box on the left connects via drawn edges to a middle column of page boxes, which in turn fan out to a right column of leaf pages. Boxes and their connecting edges appear in staggered waves rather than all at once, each new branch extending the tree outward. The build is steady and unhurried, the diagram filling more of the frame with every strip frame.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.6063 · eased_energy_share=0.8013 · sparsity=0.4699 · spatial_concentration=0.566 · mov_texture=3.079)
- Source: https://www.youtube.com/watch?v=6u25GckPhLU @ 1:26-1:30

### typeahead-suggestion-rows-stack-in-kphlu
- Hero: `typeahead-suggestion-rows-stack-in-kphlu.png` · Strip: `typeahead-suggestion-rows-stack-in-kphlu-strip.png`
- Tags: motion=[typewriter, stagger, slide-in] · archetype=kinetic-type · energy=measured · mood=neutral
- Use when: a search box or list autocompletes and suggestion rows populate beneath an input
- Motion: Under a 'Handling Politeness' header, a search input fills in character by character ('H', then 'Ho') while a stack of suggestion rows reveals beneath it one at a time (wikipedia.c, appl, and more), each row sliding in and the text within typing across frames. A second small chip appears to the right partway through. The cadence is a clean typeahead build: input types, dropdown rows stagger downward, list grows taller frame by frame.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.9971 · eased_energy_share=0.9632 · sparsity=0.2308 · spatial_concentration=0.4647 · mov_texture=6.9251)
- Source: https://www.youtube.com/watch?v=6u25GckPhLU @ 2:21-2:23

### logo-wordmark-scale-reveal-over-particle-field-9rb5i
- Hero: `logo-wordmark-scale-reveal-over-particle-field-9rb5i.png` · Strip: `logo-wordmark-scale-reveal-over-particle-field-9rb5i-strip.png`
- Tags: motion=[scale-bloom, pop, settle] · archetype=title-card · energy=measured · mood=neutral
- Use when: an opening title card brands the topic before the explainer begins
- Motion: Over a dark teal particle field, a small framed panel with the LinkedIn and Uber logos holds center while the Kafka logo and 'kafka' wordmark scale-bloom in above it, popping from small to full size and settling. The wordmark lands crisp and steady, then the final frame cuts the whole card to near-black as the scene wipes out. Camera is locked; all motion is element-level scale and reveal.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.2157 · eased_energy_share=0.725 · sparsity=0.2962 · spatial_concentration=0.4429 · mov_texture=6.9282)
- Source: https://www.youtube.com/watch?v=7_wkWQ9rB5I @ 0:00-0:06

### staggered-partition-table-build-with-cursor-labels-9rb5i
- Hero: `staggered-partition-table-build-with-cursor-labels-9rb5i.png` · Strip: `staggered-partition-table-build-with-cursor-labels-9rb5i-strip.png`
- Tags: motion=[stagger, slide-in, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a concept builds up column by column as each piece of the system is introduced
- Motion: Topic A and Topic B partition tables sit established at left, then a third Topic C column slides in from the right and settles into the row. In lockstep, a small cursor/hand icon and text labels ('Payment', then 'User click', then a third) stagger on beneath the columns one at a time, left to right, each settling before the next appears. The stagger step is roughly even, unhurried, with no overshoot — elements snap into place and hold.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.6589 · eased_energy_share=0.8571 · sparsity=0.4558 · spatial_concentration=0.4995 · mov_texture=3.829)
- Source: https://www.youtube.com/watch?v=7_wkWQ9rB5I @ 1:05-1:07

### code-panel-wipe-reveal-json-message-9rb5i
- Hero: `code-panel-wipe-reveal-json-message-9rb5i.png` · Strip: `code-panel-wipe-reveal-json-message-9rb5i-strip.png`
- Tags: motion=[wipe, mask-reveal, typewriter] · archetype=code-reveal · energy=measured · mood=clinical
- Use when: a payload or code snippet is revealed to show the concrete shape of the data
- Motion: A thin horizontal bar wipes across the empty frame, widening into a dark code panel that masks open from a sliver to a full rectangle. As the panel reveals, a JSON message ('topic', 'key': 'order-637', 'value': { 'orderId'... }) types/fades in line by line inside it. The reveal is a left-to-right horizontal wipe that resolves to a centered, settled panel; camera stays locked.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.5823 · eased_energy_share=0.9431 · sparsity=0.3977 · spatial_concentration=0.4927 · mov_texture=1.4364)
- Source: https://www.youtube.com/watch?v=7_wkWQ9rB5I @ 1:15-1:17

### sliding-panel-scene-transition-to-write-consume-9rb5i
- Hero: `sliding-panel-scene-transition-to-write-consume-9rb5i.png` · Strip: `sliding-panel-scene-transition-to-write-consume-9rb5i-strip.png`
- Tags: motion=[slide-in, wipe, settle] · archetype=diagram-build · energy=measured · mood=neutral
- Use when: the scene transitions from one diagram state into the next stage of the system
- Motion: A yellow producer bar and tall gray placeholder bars slide in from the left while the blue Consumer Group stack holds at right, the gray panels acting as a moving wipe between states. The bars resolve into the full Producers-to-Consumer-Group diagram, then the final frame reveals a large rounded write/consume panel with blue and red message blocks fading in alongside 'Write' and 'Consume' labels. Motion is a steady lateral slide that settles into the new layout; no overshoot or bounce.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.2621 · eased_energy_share=0.974 · sparsity=0.1318 · spatial_concentration=0.3431 · mov_texture=8.9274)
- Source: https://www.youtube.com/watch?v=7_wkWQ9rB5I @ 6:14-6:16

### staggered-tech-logo-intro-build-kpu7k
- Hero: `staggered-tech-logo-intro-build-kpu7k.png` · Strip: `staggered-tech-logo-intro-build-kpu7k-strip.png`
- Tags: motion=[stagger, pop, settle] · archetype=title-card · energy=measured · mood=neutral
- Use when: an intro names the topic and pops in the key tools/players one by one before the explainer starts
- Motion: On a near-black field the title 'How Key-value Stores Work?' is already set top-left; then three product icons pop in left-to-right with a short stagger step — first the blue database cylinder, then a boxed teal 'M', then a red Redis-style stack that builds from a single slab into a three-layer stack. As the row settles, the author lower-third 'Sahn Lam / Co-author of the System Design Interview book series' fades up bottom-right and a tiny shopping-cart glyph appears low-left. Each icon lands with a small pop rather than a slide; the cadence is calm and punctuated, one element per beat.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.8776 · eased_energy_share=0.9252 · sparsity=0.2967 · spatial_concentration=0.37 · mov_texture=2.5492)
- Source: https://www.youtube.com/watch?v=Dwt8R0KPu7k @ 0:01-0:05

### hash-ring-key-route-callout-kpu7k
- Hero: `hash-ring-key-route-callout-kpu7k.png` · Strip: `hash-ring-key-route-callout-kpu7k-strip.png`
- Tags: motion=[pop, draw-on, settle] · archetype=diagram-build · energy=punchy · mood=clinical
- Use when: a diagram shows one input being processed and routed to its destination on a structure
- Motion: Over a static consistent-hashing ring (server A/B/C nodes with hash labels), a JSON payload card 'user_12345_cart {...}' pops in at upper-right inside a dashed selection box, with a small hash '#' badge beneath it. A blue hash value ('760', '1000') flashes on as a callout, drawing a conceptual line from the key to its target node on the ring. The ring itself holds still while the new annotations appear and settle in one quick punctuated step — the motion is the callout landing, not the ring moving.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.5181 · eased_energy_share=0.932 · sparsity=0.1127 · spatial_concentration=0.3511 · mov_texture=3.742)
- Source: https://www.youtube.com/watch?v=Dwt8R0KPu7k @ 2:01-2:04

### cart-fill-buy-cta-outro-collage-kpu7k
- Hero: `cart-fill-buy-cta-outro-collage-kpu7k.png` · Strip: `cart-fill-buy-cta-outro-collage-kpu7k-strip.png`
- Tags: motion=[slide-in, pop, settle] · archetype=collage · energy=measured · mood=playful
- Use when: an outro chains a worked example into a product/subscribe call-to-action before the end card
- Motion: An empty wireframe shopping cart sits center-frame, then fills: product items drop into it and a small parcel/box swings in from the top on a line. A blue 'Buy' button pops in below with a pointer cursor nudging it, then a green ByteByteGo subscribe card with a 'SUBSCRIBE' button slides up from the lower-left. The sequence resolves into an Amazon wordmark over a dotted blue world map. Elements arrive one at a time in a measured chain — fill, then CTA, then brand end card — each settling before the next enters.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.6818 · eased_energy_share=0.9234 · sparsity=0.5855 · spatial_concentration=0.7127 · mov_texture=6.7591)
- Source: https://www.youtube.com/watch?v=Dwt8R0KPu7k @ 5:30-5:35

### book-cover-wipe-up-pair-kpu7k
- Hero: `book-cover-wipe-up-pair-kpu7k.png` · Strip: `book-cover-wipe-up-pair-kpu7k-strip.png`
- Tags: motion=[wipe, slide-in, settle] · archetype=card-flip · energy=frenetic · mood=triumphant
- Use when: a product or cover reveals fast as the payoff, then a second item joins it
- Motion: From an empty dark frame a tall green book cover ('Object Oriented Design Interview') wipes upward into view, growing from a thin sliver at the bottom to its full height in two or three quick frames. As it locks into place an orange second cover ('Machine Learning System Design') slides in from the right to sit beside it, pairing the two covers. The reveal is fast and saturated — a vertical mask-wipe followed by a lateral slide — settling on a two-up product shelf.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.9356 · eased_energy_share=0.8652 · sparsity=0.0886 · spatial_concentration=0.2528 · mov_texture=12.9739)
- Source: https://www.youtube.com/watch?v=Dwt8R0KPu7k @ 5:42-5:45

### typewriter-stat-into-result-chip-qaxm
- Hero: `typewriter-stat-into-result-chip-qaxm.png` · Strip: `typewriter-stat-into-result-chip-qaxm-strip.png`
- Tags: motion=[typewriter, slide-in, count-up] · archetype=stat-hero · energy=measured · mood=neutral
- Use when: a big number lands and then resolves into a concrete worked example
- Motion: The headline stat '100 million new URLs every day' and a dashed grid of link icons hold on the left as the anchor. A yellow result box slides in from the right and a string types out character by character ('h', 'ht', 'htt'...) building toward the shortened value. By the last frames the typed text resolves into two finished URL chips inside the box. The cadence is even and unhurried, one glyph per frame, no overshoot — the box settles in place and the type fills it left to right.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.4605 · eased_energy_share=0.9267 · sparsity=0.2039 · spatial_concentration=0.3718 · mov_texture=13.7842)
- Source: https://www.youtube.com/watch?v=HHUi8F_qAXM @ 0:43-0:46

### icons-feed-database-stack-count-up-qaxm
- Hero: `icons-feed-database-stack-count-up-qaxm.png` · Strip: `icons-feed-database-stack-count-up-qaxm-strip.png`
- Tags: motion=[count-up, slide-in, settle] · archetype=diagram-build · energy=measured · mood=neutral
- Use when: a running total climbs as inputs accumulate into a growing store
- Motion: A cluster of link icons on the upper right feeds via a single blue arrow into a database cylinder, with a '365 Billion URLs' caption pinned beside the icons. The cylinder count-up label steps '0 Terabytes -> 1 -> 2' as one cylinder, then jumps to a stacked grid of cylinders reading '35 Terabytes -> 36 Terabytes' in the final frames. The growth reads as discrete snaps rather than a smooth tween — the single unit multiplies into a tiled stack to dramatize scale, settling on the larger number.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.7536 · eased_energy_share=0.957 · sparsity=0.5182 · spatial_concentration=0.6006 · mov_texture=7.2638)
- Source: https://www.youtube.com/watch?v=HHUi8F_qAXM @ 1:01-1:04

### database-fan-out-to-replicas-draw-on-qaxm
- Hero: `database-fan-out-to-replicas-draw-on-qaxm.png` · Strip: `database-fan-out-to-replicas-draw-on-qaxm-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=diagram-build · energy=measured · mood=neutral
- Use when: a single node splits its load across multiple downstream copies
- Motion: A stacked-disk source on the left points through a '10,000 lookups per second' arrow into a central database cylinder, which holds steady as the anchor (a brief red read-flash glints on the cylinder in the first frame). Then three branch arrows draw outward from the cylinder one after another, each landing on a labeled 'Replica 1', 'Replica 2', 'Replica 3' cylinder that fades in at the arrowhead. The fan-out resolves top-to-bottom with even spacing and no overshoot — the arrows extend and the replicas settle into a clean tri-branch.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.0261 · eased_energy_share=0.9098 · sparsity=0.2571 · spatial_concentration=0.4344 · mov_texture=3.7498)
- Source: https://www.youtube.com/watch?v=HHUi8F_qAXM @ 5:00-5:02

### request-flow-numbered-steps-draw-on-qaxm
- Hero: `request-flow-numbered-steps-draw-on-qaxm.png` · Strip: `request-flow-numbered-steps-draw-on-qaxm-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: walking a request through an architecture left-to-right, step by numbered step
- Motion: A 'User' device card sits at far left and a connector line draws rightward carrying a 'GET https://tinyurl.com/...' label, threading through a blue Load Balancer node into a 'Web Server' node on the right. Small numbered step badges (1, 2, 3) light up in sequence along the path as each hop completes. The whole flow assembles left-to-right at a steady measured pace, nodes already placed while the connecting line and labels animate across, settling into a finished request-path diagram with no bounce.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.8973 · eased_energy_share=0.9518 · sparsity=0.1227 · spatial_concentration=0.2804 · mov_texture=5.3871)
- Source: https://www.youtube.com/watch?v=HHUi8F_qAXM @ 6:17-6:19

### branching-usecase-panels-stagger-reveal-g1xlo
- Hero: `branching-usecase-panels-stagger-reveal-g1xlo.png` · Strip: `branching-usecase-panels-stagger-reveal-g1xlo-strip.png`
- Tags: motion=[draw-on, stagger, mask-reveal] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: one parent concept fans out into three parallel use-cases, each unpacking its own detail
- Motion: A single GPU node anchored at top center draws two then three dashed connector lines down to labeled branches (Graphics Rendering, Scientific Computing, Machine Learning), left to right. As each branch lands, its supporting graphic reveals beneath it in turn: a teal pixel grid fills in, a Data/Operation/Result table populates row by row, and a neural-net inputs panel with weight arrows assembles last. The stagger is branch-by-branch with the leftmost settling first; everything eases in and holds with no overshoot, a calm clinical build.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.5276 · eased_energy_share=0.7547 · sparsity=0.789 · spatial_concentration=0.8347 · mov_texture=2.2885)
- Source: https://www.youtube.com/watch?v=MUWAbpg1xLo @ 1:26-1:28

### matrix-scale-up-grid-grow-g1xlo
- Hero: `matrix-scale-up-grid-grow-g1xlo.png` · Strip: `matrix-scale-up-grid-grow-g1xlo-strip.png`
- Tags: motion=[scale-bloom, count-up, slide-in] · archetype=diagram-build · energy=punchy · mood=neutral
- Use when: a small example explodes into a massive scaled-up version to convey order-of-magnitude growth
- Motion: A small bracketed 2x3 matrix sits at left; a curved arrow with a blue 'scale up' pill points right into an open region that grows a large rounded-square grid. The grid fills column-by-column from the top-left, cascading downward and rightward so the cell count visibly mushrooms across frames while a header counter climbs toward '1000 x 1000+'. The growth is continuous and energetic with no settle hold inside the window, the cells reading like a population that keeps multiplying.
- Motion-metrics: energy=punchy · cadence=continuous · spatial=localized · gate=continuous · src=scan
  (flow: motion_energy=1.6829 · eased_energy_share=0 · sparsity=0.6542 · spatial_concentration=0.6869 · mov_texture=12.288)
- Source: https://www.youtube.com/watch?v=MUWAbpg1xLo @ 2:37-2:39

### scalar-to-tensor-ladder-buildout-g1xlo
- Hero: `scalar-to-tensor-ladder-buildout-g1xlo.png` · Strip: `scalar-to-tensor-ladder-buildout-g1xlo-strip.png`
- Tags: motion=[slide-in, stagger, typewriter] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: stepping up a conceptual hierarchy one rung at a time, each rung a richer version of the last
- Motion: A left-to-right ladder assembles stage by stage: a blue Scalar circle (7) slides in, an arrow then a teal Vector row, an arrow then an amber Matrix grid, an arrow then a pink 3D Tensor cube, each with its dimension label (0D/1D/2D) tagged underneath. Above the row a title types out progressively, 'TE' then 'TEN' then 'TENSOR =' then 'TENSOR = HIGHER-DIMENSIONAL ARR...', synced to the rungs arriving. Each element eases in and holds, a steady measured climb with the cube as the payoff at the right edge.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.69 · eased_energy_share=0.9342 · sparsity=0.0648 · spatial_concentration=0.2308 · mov_texture=5.145)
- Source: https://www.youtube.com/watch?v=MUWAbpg1xLo @ 3:26-3:28

### labeled-product-cards-pop-in-accent-wipe-odd0
- Hero: `labeled-product-cards-pop-in-accent-wipe-odd0.png` · Strip: `labeled-product-cards-pop-in-accent-wipe-odd0-strip.png`
- Tags: motion=[pop, slide-in, wipe] · archetype=title-card · energy=measured · mood=neutral
- Use when: an intro that names the two subjects a video will compare or build
- Motion: Two rounded dark cards establish first — a WhatsApp glyph card pops in left-of-center with a small 'Designing WhatsApp' label tab, then a 'facebook' wordmark card pops in beside it with its own label tab. A teal accent bar wipes in horizontally to the right of the cards across the later frames, growing as the labels finish typing on ('Designi' -> 'Designing FB Newsle...'). The cards land flat with no overshoot; the only sustained motion is the accent bar's left-to-right wipe and the label text completing.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.0853 · eased_energy_share=0.9802 · sparsity=0.1024 · spatial_concentration=0.3075 · mov_texture=5.5748)
- Source: https://www.youtube.com/watch?v=OvufRkoD-D0 @ 0:00-0:03

### vector-presenter-scene-draw-on-build-odd0
- Hero: `vector-presenter-scene-draw-on-build-odd0.png` · Strip: `vector-presenter-scene-draw-on-build-odd0-strip.png`
- Tags: motion=[draw-on, scale-bloom, settle] · archetype=collage · energy=measured · mood=neutral
- Use when: a narrated scenario assembles its cast one element at a time
- Motion: A flat-design illustration builds in stages over a dark canvas. First a pale cloud blob plus a thin podium ledge scale-bloom up from nothing; next a seated presenter character draws in mid-frame, hand raised; then a second character in a red top plus a speech bubble pop in to the right, completing a two-person exchange. Each element enters in turn with a soft settle and no overshoot — additive draw-on rather than transform-driven, with the cloud anchoring the composition the others assemble around.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.7387 · eased_energy_share=0.9321 · sparsity=0.4676 · spatial_concentration=0.5562 · mov_texture=11.2131)
- Source: https://www.youtube.com/watch?v=OvufRkoD-D0 @ 1:54-1:56

### sequence-diagram-lifelines-arrows-draw-on-odd0
- Hero: `sequence-diagram-lifelines-arrows-draw-on-odd0.png` · Strip: `sequence-diagram-lifelines-arrows-draw-on-odd0-strip.png`
- Tags: motion=[draw-on, stagger, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a protocol or request/response flow is explained step by step
- Motion: A 'Client / Polling / Server' sequence diagram draws in: three column headers and vertical lifelines settle first, then 'New message?' request arrows and dashed 'connection closed' return arrows stagger downward row by row, ending on a 'Yes, Return new messages' beat near the bottom. The strip then cuts to a parallel 'Client / WebSocket / Server' diagram with a single persistent HTTP/upgrade arrow, contrasting the two protocols. Motion is purely additive line-and-arrow draw-on, calm and left-to-right top-to-bottom, no easing flourish.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.8176 · eased_energy_share=0.9293 · sparsity=0.3341 · spatial_concentration=0.4347 · mov_texture=9.9333)
- Source: https://www.youtube.com/watch?v=OvufRkoD-D0 @ 4:20-4:24

### diagram-cards-build-chip-rows-typein-hhpe
- Hero: `diagram-cards-build-chip-rows-typein-hhpe.png` · Strip: `diagram-cards-build-chip-rows-typein-hhpe-strip.png`
- Tags: motion=[stagger, slide-in, typewriter] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a system's components assemble one labeled node at a time as the explanation lays out the parts
- Motion: A first dark-green 'Spanner Server' card slides up into frame, then its colored chip rows (red GPS, yellow Atomic, blue NTP) fade in one below the next in a measured top-down stagger, each chip's label typewriter-extending from a truncated stub to full text. A second and third card then slide in to the right on the same baseline, repeating the chip cascade, while a satellite icon row populates across the top. The build is steady and punctuated rather than springy, with cards settling flat without overshoot.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.9418 · eased_energy_share=0.8268 · sparsity=0.4831 · spatial_concentration=0.6367 · mov_texture=7.8698)
- Source: https://www.youtube.com/watch?v=Qd9tJ3H_hPE @ 1:13-1:15

### green-particle-shatter-scene-transition-hhpe
- Hero: `green-particle-shatter-scene-transition-hhpe.png` · Strip: `green-particle-shatter-scene-transition-hhpe-strip.png`
- Tags: motion=[particle, wipe, snap] · archetype=title-card · energy=punchy · mood=neutral
- Use when: a hard cut between two graphic scenes needs a designed dissolve instead of a plain jump
- Motion: A flat green field erupts into a cloud of small particles that scatter and rise upward from the lower frame, thickening across the middle strip frames as a faint dashed ring lingers at center. The particle mass disperses and the green wipes away to reveal a dark new scene with sparse colored dots in the final frame. It is a fast, full-frame shatter-to-dissolve that snaps the cut closed rather than easing.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.0407 · eased_energy_share=1 · sparsity=0.5671 · spatial_concentration=0.7095 · mov_texture=10.4069)
- Source: https://www.youtube.com/watch?v=Qd9tJ3H_hPE @ 4:59-5:02

### time-axis-cells-fill-flow-to-logstack-hhpe
- Hero: `time-axis-cells-fill-flow-to-logstack-hhpe.png` · Strip: `time-axis-cells-fill-flow-to-logstack-hhpe-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=timeline · energy=measured · mood=clinical
- Use when: a sequence of events accumulates along a time axis and feeds into a downstream sink
- Motion: A horizontal 'Time' axis draws left-to-right and a row of numbered cells (yellow then blue) fills in along it, the run of cells extending further rightward across each strip frame. Curved arrows sweep up from the right end of the row into a stack of overlapping 'Log Events' cards that sits anchored top-right. Motion is calm and additive, cells settling flat with no overshoot while the flow arrows hold steady.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.2309 · eased_energy_share=0.8433 · sparsity=0.0569 · spatial_concentration=0.1969 · mov_texture=7.0595)
- Source: https://www.youtube.com/watch?v=Qd9tJ3H_hPE @ 9:37-9:39

### recap-topic-icon-grid-popin-collage-hhpe
- Hero: `recap-topic-icon-grid-popin-collage-hhpe.png` · Strip: `recap-topic-icon-grid-popin-collage-hhpe-strip.png`
- Tags: motion=[pop, stagger, settle] · archetype=collage · energy=punchy · mood=triumphant
- Use when: a closing recap fans out every concept covered as a labeled icon grid
- Motion: The strip opens holding two built diagrams ('Consistent Hashing' node ring and a 'Circuit Breaker' service topology) while small numbered badges blink in at the right margin. In the final frame a full grid of labeled topic tiles (CAP Theorem, Eventual Consistency, Load Balancing, Consistent Hashing, Rate Limiting, Monitoring) pops in together as a recap collage, each colored icon snapping to its cell. The reveal is a quick staggered pop that settles into a clean two-row grid.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.8347 · eased_energy_share=0.9045 · sparsity=0.0853 · spatial_concentration=0.3407 · mov_texture=12.5189)
- Source: https://www.youtube.com/watch?v=Qd9tJ3H_hPE @ 10:10-10:12

### logo-trio-connector-draw-on-bwqaa
- Hero: `logo-trio-connector-draw-on-bwqaa.png` · Strip: `logo-trio-connector-draw-on-bwqaa-strip.png`
- Tags: motion=[draw-on, settle] · archetype=title-card · energy=measured · mood=neutral
- Use when: an intro card establishes the players or sponsors before the topic begins
- Motion: Three stacked brand marks (GitHub, Stripe, AWS) hold center-frame while thin connector lines draw outward from each toward a shared point off-screen left and right. Across the strip the connectors extend progressively, frame by frame, from short stubs to full diagonals, with no overshoot — a slow, even reveal that settles into a static node graph. The logos themselves don't move; only the linework grows, giving a calm 'wiring the system together' feel under the title.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.3142 · eased_energy_share=0.9207 · sparsity=0.2446 · spatial_concentration=0.3828 · mov_texture=4.6665)
- Source: https://www.youtube.com/watch?v=YXkOdWBwqaA @ 0:02-0:05

### request-packets-flow-with-red-pulse-bwqaa
- Hero: `request-packets-flow-with-red-pulse-bwqaa.png` · Strip: `request-packets-flow-with-red-pulse-bwqaa-strip.png`
- Tags: motion=[slide-in, pop, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a request path is traced node-to-node and one stage lights up to mark a limit or rejection
- Motion: A Client -> Server -> Database row builds left to right: the Client box and its outline appear first, then small blue request packets queue and slide along the connector lines toward the Server. As they arrive a red bar pulses up on the Server stack and a red circular counter pops in above it, marking the rate-limit hit. Motion is even and unhurried, packets stepping in sequence rather than overshooting, settling into a steady state with the red indicator held. The accent color shift (neutral grays to a single red) does the dramatic work.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.7178 · eased_energy_share=0.9843 · sparsity=0.1072 · spatial_concentration=0.2343 · mov_texture=3.7626)
- Source: https://www.youtube.com/watch?v=YXkOdWBwqaA @ 2:05-2:08

### token-bucket-fill-with-checklist-bwqaa
- Hero: `token-bucket-fill-with-checklist-bwqaa.png` · Strip: `token-bucket-fill-with-checklist-bwqaa-strip.png`
- Tags: motion=[count-up, stagger, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: an algorithm or rule set is explained step by step with pass/fail outcomes
- Motion: A vertical token-bucket funnel sits center while request rows resolve below it one at a time, each stamped with a green check or a red X as the strip advances left to right. Simultaneously a bulleted rules list accretes underneath, line by line in a staggered build rather than all at once. The bucket icon and counters stay fixed; motion is the sequential appearance of outcome marks and list items, ending on a held red X that lands the 'request denied' beat. Steady, explanatory cadence with no camera move.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.1305 · eased_energy_share=0.9589 · sparsity=0.0721 · spatial_concentration=0.193 · mov_texture=7.5572)
- Source: https://www.youtube.com/watch?v=YXkOdWBwqaA @ 3:52-3:56

### sponsor-logo-icon-assemble-rykls
- Hero: `sponsor-logo-icon-assemble-rykls.png` · Strip: `sponsor-logo-icon-assemble-rykls-strip.png`
- Tags: motion=[snap, morph, settle] · archetype=title-card · energy=measured · mood=warm
- Use when: a sponsor or brand logo lands and resolves into its final mark
- Motion: On a near-black field the wordmark and a partial-ring 'C' icon fade up together; across the strip the icon's broken ring rotates and snaps shut into the finished logo while a small line-art delivery truck holds beside the word and a spinning silver coin/badge orbits in from the right then drops away. The pieces settle with a soft ease — no overshoot — and the final frame is the clean, recolored brand lockup centered on the dark backdrop.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=1.1578 · eased_energy_share=0.6558 · sparsity=0.6953 · spatial_concentration=0.8008 · mov_texture=12.3642)
- Source: https://www.youtube.com/watch?v=avjX3QrYkls @ 1:55-2:00

### transformer-layer-stack-boxes-assemble-rykls
- Hero: `transformer-layer-stack-boxes-assemble-rykls.png` · Strip: `transformer-layer-stack-boxes-assemble-rykls-strip.png`
- Tags: motion=[slide-in, stagger, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a layered architecture diagram assembles from its labeled parts
- Motion: Starts loose: scattered dashed nodes and an 'Attention' chip float near a tiny 'Neural Network' glyph, then the layout snaps to a centered build. Two red 'Attention' pills slide in on the left while a rounded container stacks dashed 'Layer n / Layer 2 / Layer 1' rows top-to-bottom; the assembled block then scales up to fill frame as input arrows draw in at the bottom and output arrows at the top. Easing is steady with no bounce — everything settles into a tidy stacked schematic.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.4809 · eased_energy_share=0.9757 · sparsity=0.0622 · spatial_concentration=0.3591 · mov_texture=6.6009)
- Source: https://www.youtube.com/watch?v=avjX3QrYkls @ 2:57-3:00

### positional-encoding-heatmap-wipe-split-rykls
- Hero: `positional-encoding-heatmap-wipe-split-rykls.png` · Strip: `positional-encoding-heatmap-wipe-split-rykls-strip.png`
- Tags: motion=[mask-reveal, wipe, morph] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a continuous data-viz field resolves, then fractures to expose its internal structure
- Motion: Opens with a labeled token-plus-position embedding diagram ('Jake + position 1', 'Learned + position 2'...) under a 'Injecting positional information' caption, then cuts to a single rounded card holding a smooth red-white-blue horizontal gradient. The gradient band drifts and re-bands subtly across the middle frames, then in the final frame the card wipes/splits into a full multi-column positional-encoding heatmap of vertical striped panels. The reveal is a clean mask transition from one smooth field into the striped matrix — measured, no jitter.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.932 · eased_energy_share=0.9778 · sparsity=0.2745 · spatial_concentration=0.5792 · mov_texture=16.5409)
- Source: https://www.youtube.com/watch?v=avjX3QrYkls @ 5:12-5:15

### qkv-attention-matrix-grid-build-rykls
- Hero: `qkv-attention-matrix-grid-build-rykls.png` · Strip: `qkv-attention-matrix-grid-build-rykls-strip.png`
- Tags: motion=[slide-in, stagger, draw-on] · archetype=diagram-build · energy=punchy · mood=clinical
- Use when: a math pipeline lays out its matrices and operators left-to-right
- Motion: First frames show a compact self-attention computation — color grids feeding a Softmax operator with a red attention-score heatmap below. The strip then transitions to a wider canvas where an 'Input tokens' grid on the left fans out into stacked weight blocks (Wq/Wk/Wv) producing colored Queries (red), Keys (green) and Values (blue) grids, with the chunky 'Softmax' arrow-block drawing in on the right. Matrices and operators slide and stack into their row positions in quick punchy steps, settling into a clean left-to-right Q/K/V pipeline.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.9109 · eased_energy_share=0.9735 · sparsity=0.0358 · spatial_concentration=0.2365 · mov_texture=5.4754)
- Source: https://www.youtube.com/watch?v=avjX3QrYkls @ 8:22-8:24

### title-card-speaker-roster-slide-in-8y3gm
- Hero: `title-card-speaker-roster-slide-in-8y3gm.png` · Strip: `title-card-speaker-roster-slide-in-8y3gm-strip.png`
- Tags: motion=[slide-in, stagger, settle] · archetype=title-card · energy=measured · mood=neutral
- Use when: a session opens and you introduce the panel — big topic title locked left while the speaker lineup is credited
- Motion: The big serif title 'Lessons from Building Cursor' is already settled bottom-left against a faint blueprint grid and holds rock-steady through the whole strip. The motion is on the right edge: a stacked roster of speaker cards (headshot + name + role) slides in from off-frame right, the topmost card landing first and the lower cards filling in behind it as the strip advances, so the panel builds top-to-bottom into a clean right-hand column. Easing is gentle with no overshoot — cards arrive and settle flush, anchored by the locked title and a small STATSIG sponsor mark up top.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.6641 · eased_energy_share=0.9637 · sparsity=0.2467 · spatial_concentration=0.6096 · mov_texture=0.6276)
- Source: https://www.youtube.com/watch?v=dUMsFQ8y3gM @ 0:00-0:02

### hub-spoke-node-graph-builds-out-abkiy
- Hero: `hub-spoke-node-graph-builds-out-abkiy.png` · Strip: `hub-spoke-node-graph-builds-out-abkiy-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: an architecture grows from a core out to its connected services
- Motion: A central hub node ('Private APIs', a blue circle) anchors frame one with one or two connector lines already drawn to a couple of service boxes. Left to right the graph fills out: more spoke nodes (Product, Catalog, User) slide into place and their connector lines draw on, each landing a beat apart so the fan of edges thickens evenly. Late in the strip a small refresh glyph blinks in at upper right, then a handshake icon and a fresh 'Partner APIs' box appear on the far right, extending the network. Everything eases to a clean settle with no overshoot; the build is steady and unhurried.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.289 · eased_energy_share=0.9215 · sparsity=0.1866 · spatial_concentration=0.3371 · mov_texture=6.4507)
- Source: https://www.youtube.com/watch?v=hltLrjabkiY @ 0:33-0:36

### brand-logo-grid-pops-in-rows-abkiy
- Hero: `brand-logo-grid-pops-in-rows-abkiy.png` · Strip: `brand-logo-grid-pops-in-rows-abkiy-strip.png`
- Tags: motion=[pop, stagger, settle] · archetype=collage · energy=punchy · mood=neutral
- Use when: a roster of tools or vendors is enumerated as a grid
- Motion: A small bordered 'API Terminologies' card holds the left edge, then the scene wipes to a dark 'LLM Teams' panel and a grid of brand logos populates. The top row pops in first (deepseek, an F-mark, DALL-E, Gemini), then the second row fills (Claude, KLING AI), and finally 'runway' snaps into the third slot, so the grid reads as a staggered top-to-bottom, left-to-right fill. Each logo pops on with a quick scale to its resting size; no overshoot, just crisp appearance and settle. The cumulative effect is a checklist-of-vendors enumeration rather than a single hero.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.6375 · eased_energy_share=0.9708 · sparsity=0.2674 · spatial_concentration=0.4406 · mov_texture=1.9997)
- Source: https://www.youtube.com/watch?v=hltLrjabkiY @ 1:29-1:33

### numbered-card-typewriter-title-icon-fill-abkiy
- Hero: `numbered-card-typewriter-title-icon-fill-abkiy.png` · Strip: `numbered-card-typewriter-title-icon-fill-abkiy-strip.png`
- Tags: motion=[typewriter, pop, settle] · archetype=card-flip · energy=measured · mood=neutral
- Use when: a numbered section header builds and names itself as a new topic opens
- Motion: Frame one is a bare panel; a small teal dot pops in at center, then a rounded card outline draws and a green numbered badge ('5') with a pill-shaped title bar slides up along the top edge. The title types in letter by letter across the strip ('API D' to 'API Docume' to 'API Document' to 'API Documentation'), a clear typewriter reveal. Beneath it tool icons fill in left to right (a Swagger glyph, then a pencil) each with its own typewriter label ('Swa' growing to 'Swagger'). The whole card eases to a settle with no bounce; it reads as a deliberate, on-brand section opener.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.7064 · eased_energy_share=0.9599 · sparsity=0.5512 · spatial_concentration=0.6244 · mov_texture=2.7974)
- Source: https://www.youtube.com/watch?v=hltLrjabkiY @ 3:32-3:34

### isometric-cube-stack-build-gmqsw
- Hero: `isometric-cube-stack-build-gmqsw.png` · Strip: `isometric-cube-stack-build-gmqsw-strip.png`
- Tags: motion=[slide-in, stagger, settle] · archetype=diagram-build · energy=measured · mood=neutral
- Use when: an abstract system is assembled piece-by-piece from primitive blocks
- Motion: Isometric 3D cubes (flat-blue with yellow side faces, some cross-hatched) enter beside a YouTube wordmark one at a time, sliding in from the upper-right and dropping into a staircase arrangement. Across the strip the count grows from one floating cube to a packed 3-wide, 2-tall masonry cluster, each new block landing a tier lower with a short settle. The cubes hold their isometric facing throughout — no rotation — so the build reads as stacking, not tumbling, and a thin pointer line draws in at the end.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.991 · eased_energy_share=0.9215 · sparsity=0.5425 · spatial_concentration=0.646 · mov_texture=4.8152)
- Source: https://www.youtube.com/watch?v=jWRW2xGMqSw @ 0:13-0:19

### chunk-bar-blocks-grow-insert-gmqsw
- Hero: `chunk-bar-blocks-grow-insert-gmqsw.png` · Strip: `chunk-bar-blocks-grow-insert-gmqsw-strip.png`
- Tags: motion=[count-up, scale-bloom, snap] · archetype=diagram-build · energy=punchy · mood=neutral
- Use when: a sequence is shown filling up unit-by-unit, with one element highlighted as inserted
- Motion: Three labeled groups of cyan vertical bars ('chunk + chunk + chunk') build left-to-right beside an upload glyph. The strip opens on a single bar, then each chunk fills its row of bars in a quick count-up; mid-sequence a few bars grow taller and a red '+' bar snaps in between groups to flag an insertion. The final frame reflows the whole row up into a tighter top line with a second row forming below, reading as a re-chunking pass — crisp, punctuated steps with little easing.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.623 · eased_energy_share=0.9576 · sparsity=0.1873 · spatial_concentration=0.526 · mov_texture=5.9898)
- Source: https://www.youtube.com/watch?v=jWRW2xGMqSw @ 1:12-1:15

### video-fanout-tree-draw-on-gmqsw
- Hero: `video-fanout-tree-draw-on-gmqsw.png` · Strip: `video-fanout-tree-draw-on-gmqsw-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=diagram-build · energy=measured · mood=neutral
- Use when: one source node branches into several derived outputs
- Motion: A central 'Video' film-strip node sits left while three 'Segment' nodes stack on the right. Across the strip the connector arrows draw outward one at a time from the source to each segment, top branch first, then middle, then bottom, with the segment tiles sliding the last few pixels into place as their arrow lands. Motion is calm and orderly — a fan-out tree assembling branch by branch, settling with no overshoot, and a small index tick appears top-right on the final frames.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.1521 · eased_energy_share=0.9342 · sparsity=0.0758 · spatial_concentration=0.3177 · mov_texture=3.5225)
- Source: https://www.youtube.com/watch?v=jWRW2xGMqSw @ 4:04-4:08

### manifest-code-panel-reveal-gmqsw
- Hero: `manifest-code-panel-reveal-gmqsw.png` · Strip: `manifest-code-panel-reveal-gmqsw-strip.png`
- Tags: motion=[wipe, mask-reveal, slide-in] · archetype=code-reveal · energy=punchy · mood=clinical
- Use when: a spec or config diagram resolves into the actual file contents
- Motion: A 'Primary Manifest' node connects via a labeled HLS stream line to a Media Manifest, with colored tokens in the inline code string lighting up across the early frames. In the last two frames a dark terminal-style 'Media Manifest File' panel wipes in from the right and reveals a column of monospace #EXT manifest lines, mask-revealing the raw file beneath the diagram. The reveal is abrupt and punchy — diagram first, then the code slab snaps into the right half.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.8924 · eased_energy_share=0.3944 · sparsity=0.1352 · spatial_concentration=0.4409 · mov_texture=3.6521)
- Source: https://www.youtube.com/watch?v=jWRW2xGMqSw @ 4:55-5:01

### radial-branch-callout-pills-reveal-p6vm
- Hero: `radial-branch-callout-pills-reveal-p6vm.png` · Strip: `radial-branch-callout-pills-reveal-p6vm-strip.png`
- Tags: motion=[draw-on, stagger, slide-in] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: one central concept fans out into its named sub-options as the payoff
- Motion: The left side (two leader DB nodes with write arrows) is already settled. A teal 'Conflict resolution strategies' node appears center-frame, then thin connector lines draw outward to the right and rounded white callout pills slide in one at a time along them — first one pill, then a second and third stacking down, until four labeled pills (Last Write Wins, Conflict-free, etc.) have populated the fan. The reveal is a left-to-right radial branch: hub first, then spokes and labels in sequence, each settling without overshoot.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.1539 · eased_energy_share=0.8717 · sparsity=0.2871 · spatial_concentration=0.3983 · mov_texture=6.6895)
- Source: https://www.youtube.com/watch?v=nBvDtj-p6VM @ 4:46-4:49

### staggered-labeled-arrows-into-node-p6vm
- Hero: `staggered-labeled-arrows-into-node-p6vm.png` · Strip: `staggered-labeled-arrows-into-node-p6vm-strip.png`
- Tags: motion=[stagger, slide-in, draw-on] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: several parallel inputs converge on one component, then hand off downstream
- Motion: An Application box sits left; three numbered 'Write to Cache' arrows (1a, 1b, 1c) draw in top-to-bottom in a tight stagger and converge on a teal Cache node that pops in once the arrows land. The frame holds, then a second-stage arrow ('Write to Storage in Batch', step 2) extends right from the Cache to a pink database cylinder that fades up. Two-stage left-to-right build: parallel fan-in first, single hand-off second, each element settling cleanly.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.9627 · eased_energy_share=0.8441 · sparsity=0.334 · spatial_concentration=0.3996 · mov_texture=4.2868)
- Source: https://www.youtube.com/watch?v=nBvDtj-p6VM @ 6:24-6:27

### icon-card-grid-pop-with-header-pills-p6vm
- Hero: `icon-card-grid-pop-with-header-pills-p6vm.png` · Strip: `icon-card-grid-pop-with-header-pills-p6vm-strip.png`
- Tags: motion=[pop, stagger, slide-in] · archetype=checklist · energy=punchy · mood=neutral
- Use when: a set of related concepts is enumerated as a recap or menu of options
- Motion: Cards pop in one at a time across a grid, each a dark rounded tile with a line-art icon and a yellow header pill (Partitioning, Database Sharding, DB Indexing, Replication...). The first row fills left-to-right, then a second row (Caching, CDN, and a final placeholder) drops in below, with a red layered-cache icon scaling up as an accent. The stagger is brisk and even — each tile snaps to place with a small settle, building a full taxonomy grid by the last frame.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.4454 · eased_energy_share=0.989 · sparsity=0.6534 · spatial_concentration=0.6797 · mov_texture=4.5281)
- Source: https://www.youtube.com/watch?v=nBvDtj-p6VM @ 7:47-7:50

### server-db-replica-fanout-with-red-accent-p6vm
- Hero: `server-db-replica-fanout-with-red-accent-p6vm.png` · Strip: `server-db-replica-fanout-with-red-accent-p6vm-strip.png`
- Tags: motion=[slide-in, draw-on, stagger] · archetype=diagram-build · energy=measured · mood=serious
- Use when: a single source scales out into multiple downstream copies
- Motion: Starts minimal: a Server node and a Database cylinder linked by an arrow. A red faceted accent block fades in on the connector, then dashed arrows draw outward from the Database to the upper-right and lower-right, each spawning a Replica cylinder that slides into place. The fan-out is sequential — first replica top, then bottom, then a third — and the red accent intensifies in the final frame as the emphasis beat. Clean left-to-right expansion from one node to a replicated fleet.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.504 · eased_energy_share=0.8899 · sparsity=0.4967 · spatial_concentration=0.5563 · mov_texture=2.1)
- Source: https://www.youtube.com/watch?v=nBvDtj-p6VM @ 8:03-8:05

### staggered-logo-grid-pop-in-xnlta
- Hero: `staggered-logo-grid-pop-in-xnlta.png` · Strip: `staggered-logo-grid-pop-in-xnlta-strip.png`
- Tags: motion=[stagger, pop, settle] · archetype=collage · energy=measured · mood=neutral
- Use when: naming the field of players an example sits among — competitor or ecosystem logos arriving as a set
- Motion: Against a flat dark panel, brand chat-app logos appear one at a time in a loose 3-by-2 grid. The first icon pops in solo, then the top row fills left-to-right (WhatsApp, Messenger, Hangouts), then the second row seeds (Discord, WeChat, iMessage) so the grid assembles row-major. Each icon arrives with a small pop and quickly settles — no overshoot wobble, just a clean discrete appearance per frame. The cadence is a steady one-icon-per-beat reveal that ends as a full, static logo cluster.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.9495 · eased_energy_share=0.9208 · sparsity=0.118 · spatial_concentration=0.2925 · mov_texture=3.5254)
- Source: https://www.youtube.com/watch?v=okrR1KXNLtA @ 0:10-0:13

### checklist-checkmarks-sequence-xnlta
- Hero: `checklist-checkmarks-sequence-xnlta.png` · Strip: `checklist-checkmarks-sequence-xnlta-strip.png`
- Tags: motion=[stagger, draw-on, settle] · archetype=checklist · energy=measured · mood=neutral
- Use when: a requirements or feature list gets confirmed item by item as the payoff
- Motion: A right-aligned list of requirement labels (1:1 chat, Delivery guarantee, Offline storage, Presence) sits static while green checkmarks draw in to their left top-to-bottom. The first check strokes on next to the top row, then the second appears against the next row a beat later, each mark drawing on quickly with a slight settle. The labels never move — only the ticks accrue downward in a steady tick-by-tick rhythm, reading as a list being validated line by line.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.8344 · eased_energy_share=0.8493 · sparsity=0.1737 · spatial_concentration=0.3979 · mov_texture=2.4422)
- Source: https://www.youtube.com/watch?v=okrR1KXNLtA @ 0:16-0:19

### routing-dataflow-highlight-sweep-xnlta
- Hero: `routing-dataflow-highlight-sweep-xnlta.png` · Strip: `routing-dataflow-highlight-sweep-xnlta-strip.png`
- Tags: motion=[marker-sweep, slide-in, settle] · archetype=diagram-build · energy=measured · mood=neutral
- Use when: tracing a path or routing decision live across an already-built system diagram
- Motion: Over a settled node graph (Alice and Bob at the edges, Chat Server A and B center, an etcd logo anchoring the top), a bright cyan-to-yellow highlight bar sweeps along the link between the two chat servers to trace a 'Bob to Server B' route. The bar lights up the connection, runs across it, and the warm yellow leading edge resolves as the path completes while a 'Presence' label slides in beneath the route. The surrounding diagram holds steady — only the energized link animates, so the eye follows the data moving server-to-server.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.1767 · eased_energy_share=0.9172 · sparsity=0.1533 · spatial_concentration=0.3226 · mov_texture=7.1773)
- Source: https://www.youtube.com/watch?v=okrR1KXNLtA @ 5:26-5:28

### endcard-book-covers-wipe-up-xnlta
- Hero: `endcard-book-covers-wipe-up-xnlta.png` · Strip: `endcard-book-covers-wipe-up-xnlta-strip.png`
- Tags: motion=[wipe, slide-in, settle] · archetype=title-card · energy=punchy · mood=warm
- Use when: an outro or CTA card resolving on screen at the very end of a piece
- Motion: From an empty dark frame a tall green book-cover panel wipes upward into view, growing from a thin sliver at the bottom to a full portrait card ('Object Oriented Design Interview'). Once it lands, a second orange book-cover card slides in beside it from the right, completing a two-up end-card layout. The wipe-up is brisk and the cards snap to their final positions with little settle — a quick, confident outro reveal rather than a slow fade.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.95 · eased_energy_share=0.8614 · sparsity=0.0694 · spatial_concentration=0.1901 · mov_texture=12.6255)
- Source: https://www.youtube.com/watch?v=okrR1KXNLtA @ 8:27-8:30

### diagram-reflow-title-typewriter-qdkqk
- Hero: `diagram-reflow-title-typewriter-qdkqk.png` · Strip: `diagram-reflow-title-typewriter-qdkqk-strip.png`
- Tags: motion=[accordion-reflow, typewriter, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: an old labeled diagram collapses to make room for the concept you're really introducing
- Motion: Three labeled icon clusters (Data Lake / Data Lakehouse / Data Warehouse) sit fully built, then the center Lakehouse node fades out and the surviving icons slide inward to close the gap as the layout reflows. In lockstep a header types in left-to-right across the strip, 'Traditional' growing one word per frame to 'Traditional Data System'. Motion is calm and measured with no overshoot; elements settle cleanly into their new spacing. Camera holds static.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.694 · eased_energy_share=0.9645 · sparsity=0.3544 · spatial_concentration=0.5558 · mov_texture=3.0264)
- Source: https://www.youtube.com/watch?v=taSmwcqdkQk @ 0:06-0:09

### banner-card-rise-over-logo-backdrop-qdkqk
- Hero: `banner-card-rise-over-logo-backdrop-qdkqk.png` · Strip: `banner-card-rise-over-logo-backdrop-qdkqk-strip.png`
- Tags: motion=[slide-in, mask-reveal, settle] · archetype=title-card · energy=measured · mood=neutral
- Use when: a named concept lands as a payoff title against a faint brand backdrop
- Motion: Over a dim oversized snowflake logo watermark, a bright cyan banner card rises from the bottom edge, growing taller frame by frame until it occupies the lower third. As it rises a top title bar wipes in and reveals 'FULLY MANAGED, UNIFIED PLATFORM' left-to-right. The card eases up and settles without bounce; the reveal is a clean mask wipe rather than a typewriter. No camera move — the backdrop logo stays fixed.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=1.0237 · eased_energy_share=0.8951 · sparsity=0.728 · spatial_concentration=0.6454 · mov_texture=19.2034)
- Source: https://www.youtube.com/watch?v=taSmwcqdkQk @ 1:41-1:44

### object-slides-then-staggered-file-grid-qdkqk
- Hero: `object-slides-then-staggered-file-grid-qdkqk.png` · Strip: `object-slides-then-staggered-file-grid-qdkqk-strip.png`
- Tags: motion=[slide-in, stagger, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a store/container fills with its contents as you enumerate what lives inside it
- Motion: A small blue object pill slides rightward along a horizontal connector line from a source icon, traveling a bit further each frame. Once it docks, a teal 'Object Storage' container card appears below and a row of file-type icons populates inside it with a left-to-right stagger — Log file, Parquet file, Txt file, JSON file landing in sequence. Each icon-plus-label settles in place with a small step delay between them; motion is measured and clean, no overshoot, camera static.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.8552 · eased_energy_share=0.8342 · sparsity=0.342 · spatial_concentration=0.5167 · mov_texture=1.5209)
- Source: https://www.youtube.com/watch?v=taSmwcqdkQk @ 2:56-2:58

### tech-logos-slide-swap-kinetic-qdkqk
- Hero: `tech-logos-slide-swap-kinetic-qdkqk.png` · Strip: `tech-logos-slide-swap-kinetic-qdkqk-strip.png`
- Tags: motion=[slide-in, kinetic-type, morph] · archetype=kinetic-type · energy=punchy · mood=neutral
- Use when: two competing tools or brands are name-dropped back to back as alternatives
- Motion: Logos animate horizontally across an empty dark frame: an Apache 'Spark' wordmark with its orange star and a 'trino' wordmark with a purple rabbit slide and swap positions left-to-right, one overtaking the other across the strip. The motion is a quick lateral slide with the marks crossfading/morphing as they pass, faster and punchier than the diagram beats. They glide to rest with no bounce; no camera move, just the lateral logo travel.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.748 · eased_energy_share=0.936 · sparsity=0.1266 · spatial_concentration=0.3072 · mov_texture=5.4962)
- Source: https://www.youtube.com/watch?v=taSmwcqdkQk @ 3:36-3:39

### labeled-icon-grid-staggered-build-lpqv4
- Hero: `labeled-icon-grid-staggered-build-lpqv4.png` · Strip: `labeled-icon-grid-staggered-build-lpqv4-strip.png`
- Tags: motion=[stagger, pop, slide-in] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a system's components are introduced one cluster at a time so the whole architecture assembles before the viewer
- Motion: Opens nearly empty with one lone icon, then a top row of yellow pill labels (Microservices, AuthN & AuthZ, Service Discovery) snaps in above its line-art icon, each badge popping a beat after the one to its left. A magenta API node settles in below, then a full second row (API Gateway, Message Queues) builds underneath in the same left-to-right cadence. The stagger step is roughly one icon per frame; elements arrive in place with no overshoot, settling crisply into a tidy two-row grid.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.5328 · eased_energy_share=0.8274 · sparsity=0.442 · spatial_concentration=0.4867 · mov_texture=6.479)
- Source: https://www.youtube.com/watch?v=uq-JpclPQV4 @ 0:09-0:15

### connector-arrow-draws-across-to-server-cluster-lpqv4
- Hero: `connector-arrow-draws-across-to-server-cluster-lpqv4.png` · Strip: `connector-arrow-draws-across-to-server-cluster-lpqv4-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: showing a request or handshake travelling from a client node across to a server, with the connection itself as the payoff
- Motion: A browser/globe client node fades and draws in on the far left first. Then a horizontal arrow labelled 'Connection Upgrade, WebSocket' extends rightward across the empty middle, drawing on toward a server cluster that resolves on the right edge as the line lands. The reveal reads strictly left-to-right: node, then connector growing across, then the destination cluster settling — a calm directional build with no bounce.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.6338 · eased_energy_share=0.8572 · sparsity=0.4788 · spatial_concentration=0.5666 · mov_texture=1.355)
- Source: https://www.youtube.com/watch?v=uq-JpclPQV4 @ 8:11-8:14

### green-endcard-panel-wipe-up-reveal-lpqv4
- Hero: `green-endcard-panel-wipe-up-reveal-lpqv4.png` · Strip: `green-endcard-panel-wipe-up-reveal-lpqv4-strip.png`
- Tags: motion=[wipe, slide-in, mask-reveal] · archetype=title-card · energy=frenetic · mood=triumphant
- Use when: a hard cut to an outro or promo panel that should arrive fast and fill the frame as the closing beat
- Motion: From a near-empty frame a tall green poster panel wipes up and outward, the fill mask climbing the frame across the first few tiles. As it lands, two interview-card thumbnails (an Object-Oriented Design card, then a second to its right) reveal inside the panel, and the wordmark types in along the bottom edge (b, by, byt). The motion is fast and high-energy — a full-frame mask-wipe that snaps the end-card into place rather than easing it.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.0386 · eased_energy_share=0.9653 · sparsity=0.0692 · spatial_concentration=0.226 · mov_texture=12.8506)
- Source: https://www.youtube.com/watch?v=uq-JpclPQV4 @ 9:04-9:07

### cyan-pipeline-banner-mask-reveal-bgbjw
- Hero: `cyan-pipeline-banner-mask-reveal-bgbjw.png` · Strip: `cyan-pipeline-banner-mask-reveal-bgbjw-strip.png`
- Tags: motion=[mask-reveal, slide-in, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a group of items gets named and wrapped under one labeled concept
- Motion: A solid cyan banner snaps in above the existing stack of command rows, then its label text wipes in left-to-right inside it ('Pi' -> 'Pip' -> full word across the strip) as if mask-revealed. The command card below holds steady while the banner does all the work, so the eye reads it as a new grouping bracket dropping over content that was already there. The banner settles flat with no overshoot; it is a clean snap-then-typewrite rather than a bounce.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.7379 · eased_energy_share=0.9644 · sparsity=0.4385 · spatial_concentration=0.5622 · mov_texture=1.2082)
- Source: https://www.youtube.com/watch?v=z_NbVtbgBJw @ 0:59-1:01

### labeled-card-slide-then-arrow-draw-to-node-bgbjw
- Hero: `labeled-card-slide-then-arrow-draw-to-node-bgbjw.png` · Strip: `labeled-card-slide-then-arrow-draw-to-node-bgbjw-strip.png`
- Tags: motion=[slide-in, draw-on, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a batched input flows into a single processing unit as the payoff of a comparison
- Motion: A cyan 'Pipelined commands' card holding three stacked command rows sits at left while a connector arrow draws on rightward toward a red isometric Redis cube labeled 'Single Threaded'. Across the strip the arrow extends from the card to the cube and the cube's label resolves, so the motion reads as source-card-established then flow-line-drawn into the destination. Easing is gentle and linear; the arrowhead lands flush at the node with no overshoot, a steady left-to-right build of one flow edge.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.6323 · eased_energy_share=0.6838 · sparsity=0.3362 · spatial_concentration=0.5073 · mov_texture=8.3162)
- Source: https://www.youtube.com/watch?v=z_NbVtbgBJw @ 1:01-1:05

### primary-replica-fanout-arrows-draw-down-bgbjw
- Hero: `primary-replica-fanout-arrows-draw-down-bgbjw.png` · Strip: `primary-replica-fanout-arrows-draw-down-bgbjw-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: one source node fans out to multiple downstream copies as a topology reveals
- Motion: Client 1 streams parallel lines into a red Redis cube topped by a small dial gauge; first a single 'Primary' pill appears beneath it, then two diverging arrows draw downward and outward to a left and right red node, which then gain 'Replica' labels. The reveal is top-down and sequential: ingest lines first, Primary established, then the fan-out arrows extend to the two replicas that settle into place. Pacing is measured with each tier landing in turn, no bounce on the arrowheads.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.0748 · eased_energy_share=0.8993 · sparsity=0.0843 · spatial_concentration=0.2902 · mov_texture=5.0062)
- Source: https://www.youtube.com/watch?v=z_NbVtbgBJw @ 5:00-5:03

### isometric-ram-sticks-render-with-label-list-bgbjw
- Hero: `isometric-ram-sticks-render-with-label-list-bgbjw.png` · Strip: `isometric-ram-sticks-render-with-label-list-bgbjw-strip.png`
- Tags: motion=[parallax-push, slide-in, draw-on] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a hardware or storage concept renders in 3D while supporting labels stack alongside
- Motion: Green isometric RAM sticks build up in 3D space, stacking from one to a thicker pile of modules as the strip advances, while three labels ('In-memory', 'Single-threaded', 'Data Structure') appear left-to-right and a vertical list of data-structure names (String, List, Hash, Set...) populates row-by-row on the right with a small cyan squiggle connector. The isometric stack reads as a parallax-pushed 3D render rather than a flat fade, and the right-side list fills top-down in a staggered cascade. Everything settles without overshoot into a labeled hardware diagram.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.5776 · eased_energy_share=0.9562 · sparsity=0.4647 · spatial_concentration=0.5379 · mov_texture=1.1495)
- Source: https://www.youtube.com/watch?v=z_NbVtbgBJw @ 8:08-8:10

### depth-scale-descent-arrow-draw-xjyio
- Hero: `depth-scale-descent-arrow-draw-xjyio.png` · Strip: `depth-scale-descent-arrow-draw-xjyio-strip.png`
- Tags: motion=[draw-on, slide-in, parallax-drift] · archetype=diagram-build · energy=measured · mood=serious
- Use when: establishing a measured descent down a scale toward a goal depth/value
- Motion: After a brief talking-head cut, a stylized descender figure drops into a deep-blue gradient column. A long green arrow draws downward through the frame as faint depth-tick labels (1,920M, 1,940M) scroll up past it, and a rocky seabed slab parallax-drifts in from the right. The bottom caption builds line by line. Motion is calm and continuous — the arrow elongates and the scale scrolls at an even rate, settling without overshoot.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.0135 · eased_energy_share=0.9924 · sparsity=0.0958 · spatial_concentration=0.4619 · mov_texture=14.0078)
- Source: https://www.youtube.com/watch?v=2AgABtxjYIo @ 0:00-0:03

### giant-eye-iris-bloom-reveal-xjyio
- Hero: `giant-eye-iris-bloom-reveal-xjyio.png` · Strip: `giant-eye-iris-bloom-reveal-xjyio-strip.png`
- Tags: motion=[mask-reveal, scale-bloom, settle] · archetype=diagram-build · energy=measured · mood=ominous
- Use when: a hidden presence or threat slowly reveals itself as the payoff to a setup line
- Motion: Against a near-black deep-sea field with drifting speck particles, the small descender figure hangs in the lower-left while a huge amber eye opens in the upper-right. The eye reveals as a thin glowing slit, then mask-reveals wider into a full lens, the dark pupil scaling and dilating to a round bloom across the last frames. The caption 'THERE'S SOMETHING ELSE' holds static below while the eye does all the work — a slow, deliberate open that settles fully dilated.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.8825 · eased_energy_share=0.5467 · sparsity=0.2195 · spatial_concentration=0.5439 · mov_texture=1.6223)
- Source: https://www.youtube.com/watch?v=2AgABtxjYIo @ 1:05-1:07

### earth-to-basketball-scale-morph-weizq
- Hero: `earth-to-basketball-scale-morph-weizq.png` · Strip: `earth-to-basketball-scale-morph-weizq-strip.png`
- Tags: motion=[scale-bloom, slide-in, settle] · archetype=diagram-build · energy=measured · mood=serious
- Use when: an abstract measurement is made tangible by mapping it onto a familiar object
- Motion: Against a starfield, a tiny Earth grows from the left and scales up into a basketball-sized sphere centered frame, easing to a settle as the lower-third caption updates word by word. Once the sphere holds at its final size, a small tennis-ball moon slides in from the right edge to establish the size comparison. The growth is a smooth scale-bloom with no overshoot; the captions punctuate each phrase so the visual lands in sync with the narration.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=1.1031 · eased_energy_share=0.9734 · sparsity=0.1734 · spatial_concentration=0.4044 · mov_texture=8.8183)
- Source: https://www.youtube.com/watch?v=Gab74WWEIZQ @ 0:03-0:10

### sphere-stack-build-then-diagonal-reflow-weizq
- Hero: `sphere-stack-build-then-diagonal-reflow-weizq.png` · Strip: `sphere-stack-build-then-diagonal-reflow-weizq-strip.png`
- Tags: motion=[stagger, accordion-reflow, count-up] · archetype=diagram-build · energy=measured · mood=serious
- Use when: a count is built up unit by unit and then re-laid-out to read as a total
- Motion: Earth spheres stack vertically one atop another in a staggered column rising out of frame, each unit added as the caption advances. Partway through, the whole column reflows into a tilted diagonal row of fifteen smaller Earths, snapping into the new layout while a '1.5 EARTHS / NOW FIFTEEN EARTHS' label resolves alongside. The stagger reads as a deliberate count-up, and the reflow is a single clean re-arrange rather than a morph.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.4034 · eased_energy_share=0.8992 · sparsity=0.0095 · spatial_concentration=0.2216 · mov_texture=5.9948)
- Source: https://www.youtube.com/watch?v=Gab74WWEIZQ @ 0:23-0:25

### elliptical-orbit-marker-sweep-distance-diagram-weizq
- Hero: `elliptical-orbit-marker-sweep-distance-diagram-weizq.png` · Strip: `elliptical-orbit-marker-sweep-distance-diagram-weizq-strip.png`
- Tags: motion=[draw-on, marker-sweep, settle] · archetype=map · energy=calm · mood=clinical
- Use when: a spatial relationship resolves into a labeled distance or comparison readout
- Motion: A faint elliptical orbit is drawn around a labeled Earth, with the Moon riding the path; a warm red marker sweeps along the arc to highlight the orbit's far stretch, tracing it rather than snapping. As the sweep completes the geometry settles into a static distance diagram — 'EARTH' and 'MOON' nodes joined by a measured line annotated '29 EARTHS'. The whole beat is unhurried: a draw-on, a single highlighting sweep, then a calm settle into the annotated readout.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.9638 · eased_energy_share=0.8737 · sparsity=0.7988 · spatial_concentration=0.868 · mov_texture=5.3327)
- Source: https://www.youtube.com/watch?v=Gab74WWEIZQ @ 0:35-0:42

### orbital-zone-diagram-label-settle-zzdk
- Hero: `orbital-zone-diagram-label-settle-zzdk.png` · Strip: `orbital-zone-diagram-label-settle-zzdk-strip.png`
- Tags: motion=[parallax-push, slide-in, settle] · archetype=diagram · energy=measured · mood=serious
- Use when: an explainer establishes a spatial system and labels each part as it settles into place
- Motion: A top-down orbital diagram sits on a starfield with colored orbit rings (yellow Mercury inner, blue Earth, orange Mars outer) around a glowing sun. Across the strip the camera slowly pushes in and the field of view shifts so the rings reframe, while planet labels (MERCURY, then EARTH, then MARS) fade and slide into position one at a time and hold. Each label settles without overshoot, a measured left-to-right reveal that ends with all three orbits and labels resolved and the lower caption swapping per frame.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=3.091 · eased_energy_share=0.9492 · sparsity=0.0328 · spatial_concentration=0.3438 · mov_texture=9.3237)
- Source: https://www.youtube.com/watch?v=Qqwn4rzZ-Dk @ 0:06-0:09

### diagram-badge-pop-to-planet-render-zzdk
- Hero: `diagram-badge-pop-to-planet-render-zzdk.png` · Strip: `diagram-badge-pop-to-planet-render-zzdk-strip.png`
- Tags: motion=[pop, scale-bloom, snap] · archetype=diagram · energy=punchy · mood=warm
- Use when: a question or callout pops onto a diagram and then hard-cuts to a hero subject that answers it
- Motion: Opens on the same orbital diagram where small rounded '+?' query badges pop onto the planet markers with a quick scale-bloom and a VE/Venus label fades up. After the third frame it snap-cuts to a full-frame cinematic 3D planet render (Venus) that holds large and lit from the side, drifting almost imperceptibly while the lower caption stays fixed. The contrast is the motion: tight punchy badge pops on the schematic, then a calm settle on the rendered hero planet.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=7.6485 · eased_energy_share=0.9236 · sparsity=0.0131 · spatial_concentration=0.2849 · mov_texture=8.2339)
- Source: https://www.youtube.com/watch?v=Qqwn4rzZ-Dk @ 0:09-0:14

### probe-line-drop-pin-annotation-blhpk
- Hero: `probe-line-drop-pin-annotation-blhpk.png` · Strip: `probe-line-drop-pin-annotation-blhpk-strip.png`
- Tags: motion=[draw-on, slide-in, typewriter] · archetype=diagram-build · energy=calm · mood=serious
- Use when: a measurement probes into a layered medium and the reading is annotated as it lands
- Motion: A thin vertical leader line draws downward from the top edge into the glowing orange stellar atmosphere, with a small round pin marker riding at its tip. As the strip advances the line lengthens and the pin settles deeper, while a small caption types in below it and a wavy gradient marker resolves on the left. The descent is steady and eased, not snappy, settling without overshoot; the molten render holds still behind so all the motion reads as the probe and its label arriving.
- Motion-metrics: energy=calm · cadence=punctuated · spatial=localized · gate=eased · src=scan
  (flow: motion_energy=0.3956 · eased_energy_share=0.9449 · sparsity=0.6714 · spatial_concentration=0.6335 · mov_texture=3.5332)
- Source: https://www.youtube.com/watch?v=VFdyFPbLHpk @ 0:10-0:14

### impactor-object-enters-on-leader-line-blhpk
- Hero: `impactor-object-enters-on-leader-line-blhpk.png` · Strip: `impactor-object-enters-on-leader-line-blhpk-strip.png`
- Tags: motion=[slide-in, scale-bloom, settle] · archetype=diagram-build · energy=measured · mood=serious
- Use when: a second object enters the frame to collide with or annotate a focal subject
- Motion: A bright white star sits centered with a leader line and green pin already anchored. A rocky brown sphere slides in from the upper right along the connector, growing and resolving surface detail as it approaches, then settles just above the star's edge while the lower-third label swaps to its name. The entry is measured and eased, the object arriving and coming to rest rather than snapping; the bloomed star core stays fixed so the incoming body carries the motion.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.141 · eased_energy_share=0.9695 · sparsity=0.1203 · spatial_concentration=0.3512 · mov_texture=7.5212)
- Source: https://www.youtube.com/watch?v=VFdyFPbLHpk @ 0:31-0:33

### moon-shatter-debris-render-zccg8
- Hero: `moon-shatter-debris-render-zccg8.png` · Strip: `moon-shatter-debris-render-zccg8-strip.png`
- Tags: motion=[particle, scale-bloom, kinetic-type] · archetype=diagram-build · energy=frenetic · mood=ominous
- Use when: a catastrophic transformation lands as the dramatic payoff of an explainer
- Motion: Opens on a cool grey cloud/atmosphere plate with the line 'THE PLANET'S SMASHED' set low, then hard-cuts to a 3D space render: a full moon hangs over a curved Earth limb against deep blue. Across the next frames the moon visibly tears apart — molten orange fractures bloom outward and a shower of debris fragments scatters down toward Earth while the 'TEAR IT TO SHREDS' caption holds. It settles on a stark black title card, 'REAL NASA SIMULATION', with two clean white spheres and 'THAT HAPPENED', the energy collapsing from chaos to a calm reveal.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=8.2904 · eased_energy_share=0.8299 · sparsity=0.0178 · spatial_concentration=0.4472 · mov_texture=9.7628)
- Source: https://www.youtube.com/watch?v=h-0YMkZccg8 @ 0:26-0:30

### orbit-rings-draw-on-earth-zccg8
- Hero: `orbit-rings-draw-on-earth-zccg8.png` · Strip: `orbit-rings-draw-on-earth-zccg8-strip.png`
- Tags: motion=[draw-on, slide-in] · archetype=map · energy=measured · mood=neutral
- Use when: an orbital or spatial relationship is set up before the reveal of where something sits
- Motion: Earth sits center-frame in space with stylized pale-blue orbital ring arcs drawn around its equator, the rings reading as concentric drawn-on bands under the caption '...EARTH JUST AROUND'. It cuts to a second graphic scene — a large detailed moon in the lower frame with a small Earth suspended above it and 'BUT TO FIND OUT WHERE' — holding nearly static as a setup card. The motion is the ring construction plus the clean scene swap between two space diagrams; it settles on the moon-and-Earth pairing before the strip returns to a talking-head subscribe overlay.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.0993 · eased_energy_share=0.9791 · sparsity=0.1026 · spatial_concentration=0.4419 · mov_texture=12.7154)
- Source: https://www.youtube.com/watch?v=h-0YMkZccg8 @ 0:45-0:49

### earth-cross-section-layer-scroll-reveal-c7awq
- Hero: `earth-cross-section-layer-scroll-reveal-c7awq.png` · Strip: `earth-cross-section-layer-scroll-reveal-c7awq-strip.png`
- Tags: motion=[parallax-push, slide-in, settle] · archetype=diagram-build · energy=punchy · mood=warm
- Use when: a layered structure is introduced top-to-bottom and each stratum is named as it arrives
- Motion: A filled cross-section of Earth scrolls downward across the first three frames: frame one holds at the surface with CRUST and MANTLE called out, frame two pushes deeper to expose the outer-core band, and frame three settles on the full stack with MANTLE / OUTER CORE / INNER CORE labels parked beside their bands. The reveal is a steady vertical parallax push rather than discrete pops, with the warm red-to-yellow gradient sliding into frame and each label settling in place once its layer arrives. No overshoot; it reads as a confident downward pan that lands cleanly.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.3882 · eased_energy_share=0.9882 · sparsity=0.3448 · spatial_concentration=0.4488 · mov_texture=10.0147)
- Source: https://www.youtube.com/watch?v=pag8Ncc7AwQ @ 0:03-0:07

### seismic-raypath-sketch-draw-on-c7awq
- Hero: `seismic-raypath-sketch-draw-on-c7awq.png` · Strip: `seismic-raypath-sketch-draw-on-c7awq-strip.png`
- Tags: motion=[draw-on, stagger, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a mechanism is explained by tracing paths through a system and a legend builds alongside
- Motion: A hand-drawn-style ray-path diagram builds in two passes: the first two frames hold a faint grey sketch of curved paths arcing through a ghosted Earth, then frames three through six ink in the full diagram — the core layers fill with labeled bands and colored seismic rays (orange, then red) draw on one set at a time. A legend in the lower third populates line by line in step with each ray color, so the strokes and their key arrive in staggered pairs. The cadence is unhurried and deliberate, every line drawing on and settling before the next, giving it a clinical chalkboard feel.
- Motion-metrics: energy=measured · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=0.9243 · eased_energy_share=0.982 · sparsity=0.5387 · spatial_concentration=0.5821 · mov_texture=18.295)
- Source: https://www.youtube.com/watch?v=pag8Ncc7AwQ @ 0:33-0:35

### measure-line-overlay-then-title-slide-hvnhy
- Hero: `measure-line-overlay-then-title-slide-hvnhy.png` · Strip: `measure-line-overlay-then-title-slide-hvnhy-strip.png`
- Tags: motion=[draw-on, slide-in, settle] · archetype=diagram-build · energy=measured · mood=clinical
- Use when: a measured quantity gets annotated on a real subject before its name lands
- Motion: Left frames draw a bright vertical measurement line up the face of a mountain with a value tag riding at the top, the line anchoring the height being called out. The composition then hard-cuts to a calm landscape where a chunky 'MAUNA LOA' label slides in and settles dead-center, holding without further movement. The annotation reads as a draw-on overlay, the title as a single decisive slide-and-settle.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.1554 · eased_energy_share=0.9494 · sparsity=0.0523 · spatial_concentration=0.369 · mov_texture=10.9643)
- Source: https://www.youtube.com/watch?v=xxbkGphvnhY @ 0:19-0:22

### twin-stat-card-count-up-compare-hvnhy
- Hero: `twin-stat-card-count-up-compare-hvnhy.png` · Strip: `twin-stat-card-count-up-compare-hvnhy-strip.png`
- Tags: motion=[count-up, pop, settle] · archetype=stat-hero · energy=punchy · mood=triumphant
- Use when: a headline number lands as the payoff and a second figure pops in to dwarf or contrast it
- Motion: A centered 'MAUNA LOA' label holds while its stat numerically rolls from 95.00 up to 95,000k and finally resolves to a formatted 95,000km tag that pops on with a small box. A second 'MAUNA KEA' card then snaps in below on a darker band with its own 42,000k figure, staging a direct A-vs-B comparison. The count-up does the work on the first number; the second card arrives as a clean pop-and-settle, no overshoot.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=4.6632 · eased_energy_share=0.9379 · sparsity=0.0079 · spatial_concentration=0.1324 · mov_texture=14.7769)
- Source: https://www.youtube.com/watch?v=xxbkGphvnhY @ 0:23-0:26

### geology-cross-section-magma-shift-hvnhy
- Hero: `geology-cross-section-magma-shift-hvnhy.png` · Strip: `geology-cross-section-magma-shift-hvnhy-strip.png`
- Tags: motion=[slide-in, morph, settle] · archetype=diagram-build · energy=measured · mood=serious
- Use when: a hidden structure or mechanism is revealed beneath the surface to explain a cause
- Motion: Opening frames show a blue-toned cross-section of a mountain with a glowing red magma seam, a caption reading 'IT'S SO HEAVY THAT ITS WEIGHT'. The scene warps to a warmer earth-tone cross-section as the red crust line shifts and deepens, the terrain sinking under load while the caption continues. A green 'SUBSCRIBE' lower-third pops into the bottom-left and holds through the back half; the geology layers carry the motion as a slow morph-and-settle.
- Motion-metrics: energy=punchy · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=2.2758 · eased_energy_share=0.9384 · sparsity=0.0345 · spatial_concentration=0.2842 · mov_texture=5.3483)
- Source: https://www.youtube.com/watch?v=xxbkGphvnhY @ 0:27-0:31

### stacked-place-label-kinetic-list-hvnhy
- Hero: `stacked-place-label-kinetic-list-hvnhy.png` · Strip: `stacked-place-label-kinetic-list-hvnhy-strip.png`
- Tags: motion=[stagger, pop, slide-in] · archetype=kinetic-type · energy=frenetic · mood=playful
- Use when: several named items are racked up in quick succession to build a ranked or growing list
- Motion: Over a flat landscape the word 'MAUNA' pops on, then completes to 'MAUNA KEA', and successive labels — 'MAUNA LOA', 'GARDNER P...' — stack in staggered, one entering as the last settles, building a vertical roster fast. The type is chunky green caps that snap into place rather than drift. The beat then cuts to a talking-head reaction with a 'SUBSCRIBE' lower-third, so the kept motion is the front-half label stacking.
- Motion-metrics: energy=frenetic · cadence=punctuated · spatial=full-frame · gate=eased · src=scan
  (flow: motion_energy=5.9871 · eased_energy_share=0.7869 · sparsity=0.0089 · spatial_concentration=0.2936 · mov_texture=13.6902)
- Source: https://www.youtube.com/watch?v=xxbkGphvnhY @ 1:07-1:10
