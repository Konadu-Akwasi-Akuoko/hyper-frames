# Decision examples — the per-chunk imagery & type-role verdict bank

This is the worked-example bank for the **imagery & type-role** portion of the per-chunk
verdict — the reasoning the **`scene-design-decider` subagent** applies (Step D), and that
the director re-reads to sanity-check a returned verdict. The point is not to memorise these
scenes — it is to copy the *reasoning*: for each beat the decider walks the three-part AND gate from `visual-language.md` §2, names what to put on screen (or names the candidate weighed and rejected), and settles which font carries each role. The iron rule lives in every example: **declining imagery names the candidate it rejected** — a `text-only` verdict with no named candidate is the silent skip this whole pass exists to kill. The examples are deliberately on *other* topics (CDNs, central banking, hyperscale data centres, lighthouse keeping) so the instinct generalises to whatever sentence is in front of you, not the one video you happen to be authoring.

## The per-chunk verdict

The `scene-design-decider` returns one verdict per chunk **before** the director authors —
the same auditable discipline as Step B (quote the chunk text back so the pass can be
checked). The full verdict (SKILL.md Step D) also carries an `ARCHETYPE:` line and the
auditable `MOTION-REF:` line; this bank focuses on the two lines below — the imagery call
and the font roles:

  Imagery: box: class=<logo|glyph|photo|reaction> referent="<thing>" [emotion="<e>"] [treatment="<…>"]
           — OR —  text-only — <named candidate> weighed, rejected because <principled reason>
  Type-role: <role→font assignments for this chunk; verbatim human quote → human-voice font, never system font>

When a talking-head source is detected (Step A), a **presentation-mode** line joins the
verdict — decided **alongside** imagery and type-role, not instead of them; the policy lives
in `reference/talking-head.md` and the worked verdicts are Set C below.

A reaction box uses `emotion=` (primary) + `desc=` and omits `referent=`; the other classes use `referent=` and omit `emotion=`. `treatment=` carries image-prep presets only (grain, cutout, duotone); source/licence notes live in their own clause, never crammed into `treatment`.

## Set A — does this beat earn an image?

Six worked verdicts walking the §2 gate. Four are YES (logo / photo / reaction / glyph), two are first-class `text-only` — each naming the candidate it weighed and why it lost.

### Logo YES — a named brand that is the subject

A video on how CDNs decide where to serve your bytes from reaches the line *"When Cloudflare gets a request, it answers from whichever of its 300-odd edge cities sits closest to you."* Run the three-part AND gate from `visual-language.md` §2. Subject? Yes — the whole sentence turns on this one named operator; it isn't a vendor dropped into a list of three, it's *the* actor the beat is about. Recognisable on sight? Yes — Cloudflare ships a settled orange-cloud mark you'd clock without a caption, so it clears the "if you'd have to label it, it fails" test. Adds meaning bare type can't? Yes — the mark stamps an instant identity on the line, turning an abstract "a CDN" into *this specific company* the moment it appears, which plain text would have to spell out. All three gates hold, so this routes `class=logo`: a coloured Iconify `logos:` mark (or local `assets/icons/`), saved as a static SVG, referent the named company. The narration here is system-voice (no human is quoted), so the type stays the system font. Phrase the trigger to yourself as a beat *category* — "a named brand that is the subject of the line" — so the instinct fires on any video's hero vendor, not this one.

  Chunk: "When Cloudflare gets a request…"
  Imagery: box: class=logo referent="Cloudflare"
  Type-role: narration → system font

### Photo YES — a real place where scale is the payoff

In a video on hyperscale computing, the line lands: *"A single one of these data centers can draw as much power as a small city."* Walk the 3-part AND gate from `visual-language.md` §2. (1) Subject: the beat turns on the data center itself — the physical plant drawing city-scale power, not "power" as an abstraction. (2) Recognisable on sight: a hyperscale facility is a near-universal image — the warehouse-in-a-field aerial, endless server rows; you read "vast computing plant" without a label. (3) Adds meaning words can't: this is the photo trigger doing what type can't — the sheer scale and texture, the rows receding to a vanishing point, *sells* "as much as a city" where the phrase only asserts it. Not a logo (no mark is the subject; the brand is irrelevant — the bigness is the point) and not a glyph (a server icon would shrink the very scale that's the payoff), so it routes to `class=photo`. Source it from Wikimedia Commons and capture the licence now — a real-facility photo carries an attribution obligation that travels with the asset, and that source note belongs in its own clause, not inside `treatment`. A recognisable real place where scale is the payoff is the photo case.

  Chunk: "A single one of these data centers…"
  Imagery: box: class=photo referent="hyperscale data center interior (server rows receding to a vanishing point)" treatment="grain, cool-tint, cutout" — Wikimedia Commons source; record artist/license on data-asset-credit
  Type-role: stat phrase "as much power as a small city" → kinetic display font (emphasis sweep on "small city"); body narration → system sans

### Reaction YES — an ironic punchline, name the emotion

In a workplace-productivity-app video, the line lands: *"The app built to save you time now sends you fourteen notifications a day reminding you to use it."* This is the slot reaction imagery was made for — the humour *is* the twist, and a face pays off an irony the words only set up. Note the branch: this is **not** the referent gate of `visual-language.md` §2 ("show the thing you name") — irony has no mark to show. It's the other branch §2 names — *react for the viewer* — so the question isn't "is it recognisable on sight" but "does naming the emotion add the deadpan the prose can only imply, and hold watch-time." It does. The emotion is the primary match: this is an **eye-roll** — the "of course it does" beat — not a laugh or a shock. Then note what you do *not* add: with the face carrying the contrast, leave the line at full strength — don't divide the frame or dim a half (§2: one device, not two competing). Source is Pinterest (logged-in), treated to a cutout so it sits on the void.

  Chunk: "The app built to save you time…"
  Imagery: box: class=reaction emotion="eye-roll" desc="weary eye-roll reaction face, looking left toward the text" treatment="cutout"
           — a Pinterest-sourced eye-rolling cutout reacting for the viewer; a *laughing* face was weighed and rejected — the beat is weary irony ("of course it does"), not a belly-laugh, and the wrong emotion misreads the punchline
  Type-role: narration/punchline → display kinetic type owns the frame opposite the cutout; the payoff fragment "fourteen notifications a day" gets a colour-ignition on its word — no card

### Glyph YES vs noise — a structural glyph set earns it, a word-restating glyph doesn't

In a systems-architecture explainer on how a distributed tracing system follows a request, one beat lands on: *"Every request fans out through three tiers — an edge proxy, a service mesh, and a storage layer — and the trace stitches their timing back together."* The three tiers aren't passing nouns; they *are* the subject, and together they form a real top-to-bottom diagram: three settled infra shorthands (proxy → gateway glyph, mesh → node-graph glyph, storage → database-cylinder glyph) stacked so the eye reads one drawn object. Each passes the gate (`visual-language.md` §2): the tiers are the subject of the beat, each glyph is iconic on sight (no label needed), and the stacked arrangement adds the spatial "fans out top-to-bottom" meaning bare type can't. That's a structural glyph *set* — a small concept diagram, currentColor-tintable so it tints as one — and it earns the box. The noise version is the same impulse one step too far: had the line just said "the trace records each request" and we'd dropped a lone *request*/document glyph beside the word *request*, that glyph would only restate the noun next to it — it fails clause 3 (adds no meaning), the exact "icon next to the word it names" the gate calls out — so that version stays text-only/diagram.

  Chunk: "Every request fans out through three tiers…"
  Imagery: box: class=glyph referent="edge-proxy → service-mesh → storage stack (three stacked infra glyphs forming a top-to-bottom diagram, currentColor-tintable)"
           — the lone *request*/document glyph beside the word *request* was weighed and rejected: it only restates the noun (fails gate clause 3, adds no meaning), so it stays diagram/text-only
  Type-role: tier labels (edge proxy / service mesh / storage layer) → diagram-node label font; running narration → body font

### Text-only — an abstract idea with no settled mark, candidate named and rejected

A central-banking explainer lands on the line: *"What a central bank really sells is credibility — the belief that next year's money will buy roughly what today's does."* The beat turns on "credibility," exactly the kind of abstract the §2 gate names in its hard exclusions (alongside "trust" and "performance") — an idea with no settled mark. Run the candidate anyway so the skip is auditable: a stock handshake photo, or a balance-scales glyph. The handshake fails gate-clause (2) — you'd have to label it "credibility," it reads as generic corporate filler — and gate-clause (3): it adds nothing the word doesn't already carry, it's literal-cheesy. The scales glyph merely restates "belief/balance" beside the word, the noise case §2 warns against. So credibility stays kinetic type. This is the standing move for any beat whose subject is an abstract worth with no recognisable referent.

  Chunk: "What a central bank really sells is credibility…"
  Imagery: text-only — a stock handshake photo (and a balance-scales glyph) weighed, rejected because "credibility" is an abstract worth with no settled mark; the handshake is label-dependent and literal-cheesy, the glyph merely restates the word beside it.
  Type-role: narrated line → human-voice font throughout (it is spoken); "credibility" → emphasis (display weight, the word the line turns on); the em-dash definition → secondary weight (the narrator's gloss, still human-voice). System sans is reserved for any non-narrated chrome, of which this chunk has none.

### Text-only by rationing — the neighbour already carries it

In a video about how deep-sea cargo gets to shore, two consecutive sentences land: *"Everything funnels through the Suez Canal — one narrow ditch carrying a tenth of world trade."* then *"Miss the tide there and a ship waits a full day before it can move again."* Both name the same place, so both tempt a sprite — but ration across the pair. The first beat *turns on* the canal (its narrowness IS the point, and the satellite image of that thin blue line adds scale bare type can't), so it earns the picture; the second beat is about the *waiting*, where the canal is just the where, a noun in passing. Gate part (1) decides it: subject vs. setting. The neighbour already carries the canal, so the second beat declines — re-stamping it would be a duplicate, the "glyph that merely restates the word beside it" failure. Emit both blocks so the "already carried" claim is auditable.

  Chunk: "Everything funnels through the Suez Canal —"
  Imagery: box: class=photo referent="Suez Canal" treatment="satellite-crop"
  Type-role: "funnels" emphasis word → bold weight of the body display font; "one narrow ditch carrying a tenth of world trade" → muted body font.

  Chunk: "Miss the tide there and a ship waits a full day…"
  Imagery: text-only — a second Suez Canal photo (class=photo, referent="Suez Canal") weighed, rejected because this beat's subject is the day-long wait, not the canal; gate part (1) fails (setting, not subject) and the adjacent beat already carries the canal, so re-stamping it would be duplicate noise.
  Type-role: "a full day" emphasis phrase → bold weight of the body display font; rest → muted body font.

## Set A2 — a Motion-metrics tiebreak (Scope C) when two entries share the archetype

One worked verdict on the `MOTION-REF:` line. The point is the secondary ranking: meaning and archetype stay primary, but when two index entries plausibly fit the same beat, the objective `Motion-metrics:` line breaks the tie toward the one whose measured character matches what the beat wants.

### Two kinetic-type entries fit — measured energy/cadence/spatial breaks the tie

A video on how a build pipeline fails fast lands on: *"One bad commit, and the whole pipeline slams to a halt — red across the board, instantly."* The beat is a single hard, abrupt stop: punchy, punctuated, and tightly localized on the failing node, not a sweeping full-frame drift. The chosen archetype is `kinetic-type`, and the Quick index scan turns up two entries that both plausibly fit it — `headline-snap-in` and `manifesto-drift`. Both share the archetype, so this is the genuine tie Scope C is for: drill in and read their `Motion-metrics:` lines. `headline-snap-in` carries `energy=punchy · cadence=punctuated · spatial=localized` (src=scan); `manifesto-drift` carries `energy=calm · cadence=continuous · spatial=full-frame`. The beat wants the slam — punchy/punctuated/localized — so `headline-snap-in` wins the tiebreak on measured character, even though both names read "kinetic." Note the metric, not the human Tag, decided it: `manifesto-drift`'s human `energy=` Tag reads "assertive," but its *measured* energy is calm, and on motion character the measured value is what we trust. Had only one entry fit, meaning alone would have settled it and the metrics line would be a footnote; here it earns its keep. (If a candidate had carried no `Motion-metrics:` line at all — a clip-mode entry — it would not be penalized; we'd fall back to its human energy/mood Tags and weigh it on those.)

  Chunk: "One bad commit, and the whole pipeline slams to a halt…"
  Motion-ref: headline-snap-in — adapting the hard single-overshoot snap-and-settle on the failing node (no stagger drift); tiebreak vs. manifesto-drift resolved on Motion-metrics — headline-snap-in measures energy=punchy · cadence=punctuated · spatial=localized, which matches this beat's abrupt localized slam, where manifesto-drift measures energy=calm · cadence=continuous · spatial=full-frame

## Set B — which font carries each role?

Six worked verdicts on the type-role line. The hinge throughout is *provenance, not cadence*: only a real person's actual words (or their hand-drawn marks) earn the design's reserved human-voice font; everything the script says in its own voice stays in the system/authority font, and literal identifiers go to mono.

### Verbatim human quote → human-voice font

In a video on the history of lighthouse keeping, a scene lands on a keeper's actual words from his 1881 logbook, the night a storm took out the lamp: *"The light failed at two; I climbed and held a lantern to the glass until dawn, and no ship was lost."* This is a real person's words quoted directly, so the gate question is which font carries them. The narrator is not speaking here — a real keeper is, and `design.md` reserves Excalifont for exactly that human voice while Inter carries all narration and system text. Rendering the quote in Inter would flatten it into another reframe line and erase the fact that a person lived this; the human-voice font is what signals "someone said this," not "the video is saying this." The attribution that frames it ("Keeper's log, Skerryvore, 1881") is metadata, not the human's voice, so it drops to mono. This is the move for any verbatim human quote: the reserved human-voice font carries the words, the system font never does.

  Chunk: "The light failed at two…"
  Imagery: text-only — a scanned logbook page weighed, rejected because the beat is the keeper's *words* and a faded manuscript scan would fight the line for legibility rather than serve it
  Type-role: quote line → Excalifont (reserved human-voice font, never Inter); attribution "Keeper's log, Skerryvore, 1881" → JetBrains Mono (metadata, muted)

### Narrator paraphrase → system font

A monetary-policy explainer narrates: *When a currency loses trust, no interest rate can buy it back.* It is crisp and aphoristic and reads like something you could drop on a slide inside quotation marks. But there are no quotation marks, no attributed speaker, and no real person said these exact words — it is the script reframing its own argument in the narrator's voice. `design.md` reserves the human-voice font (Excalifont) for verbatim real-person quotes and hand-drawn annotations only; the moment a system reframe borrows that font, the video starts implying a source that doesn't exist. So the line stays in the system/authority font (Inter) that carries every other reframe and headline. The font question hinges on provenance, not cadence: quotability is not quotation, and only a real person's actual words earn the human-voice font.

  Chunk: "When a currency loses trust…"
  Imagery: text-only — a hand-scrawled annotation circling "trust" was the honest candidate, rejected because the hand-annotation register is design.md's reserved human-voice treatment, and laying it over a narrator reframe would falsely imply an external source the script doesn't have
  Type-role: narration → system/authority font (Inter); the human-voice font (Excalifont) is withheld because this is the script's own paraphrase, not a verbatim human quote — provenance, not cadence, decides the font

### Hand annotation on a diagram → human-voice font

A finance explainer freezes on a system diagram of the monetary plumbing — boxes for the central bank, commercial banks, and reserves, labeled in Inter, with the overnight rate shown in mono — and the narrator says: *"Watch what happens to this one arrow when the rate moves."* The diagram is the system speaking, so every structural label stays in the design's authority voice and the rate figure stays in the technical/mono voice — a split `design.md` already locks, and the freeze doesn't change it. But the narrator now *marks up* that diagram by hand: a circled arrow and a margin note, "this is the lever," drawn on top. A hand-drawn annotation layered on clean system content is the design's second reserved use of the human-voice font — same gate as a verbatim human quote — so the scribble takes that font precisely because it reads as a person's hand intruding on the machine's diagram.

  Chunk: "Watch what happens to this one arrow…"
  Imagery: box: class=glyph referent="monetary-plumbing diagram: central-bank / commercial-bank / reserves boxes with connecting arrows, hand-annotated"
           — literal pen-in-hand photo weighed, rejected because the annotation itself already IS the human presence; a pen prop would double the signal and clutter the diagram
  Type-role: diagram structural labels → system/authority font (Inter); overnight-rate figure → technical/mono (JetBrains Mono); hand-drawn annotation ("this is the lever") → human-voice font (Excalifont), the design's reserved hand-annotation role, never the system font

### Code token, API name, file path → mono

A devtools/CLI video on container builds narrates: *"Every rebuild starts the same way — Docker reads your `Dockerfile` top to bottom and caches each layer."* The chunk surfaces a literal filename, so before anything else the type-role gate fires: `Dockerfile` is a technical identifier, not narration, and `design.md` assigns identifiers the technical mono font — it signals "this is literal code/config you'd type, not the narrator's voice." The narration wrapped around it stays in the system/authority font, so the mono token reads as a deliberate switch into literal-code register rather than emphasis. On imagery, the Docker whale logo is the obvious candidate, but the tool is a passing reference here, not the subject of the beat (the layer-caching behavior is), so a logo box would be decorative chrome — declined; the token carries itself by font alone.

  Chunk: "Every rebuild starts the same way…"
  Imagery: text-only — box: class=logo referent="Docker whale" weighed, rejected because the tool is a passing reference, not the subject of the beat (the layer-caching behavior is); a logo box would be decorative chrome
  Type-role: code token `Dockerfile` → technical mono font; surrounding narration → system/authority font

### Product wordmark / UI label → system font

A consumer-finance explainer narrates *"By 2027, your transit pass and bank card collapse into one app, simply called Tap."* The word "Tap" is the product's wordmark, and the instinct is to make it feel special — reach for the human-voice font to give it character, or treat it like a brand logo. But this is a plain text wordmark, not a sourced logo asset (no `class=logo` mark to drop in — nothing was supplied), and `design.md` reserves the human-voice font (here Excalifont) strictly for verbatim human quotes and hand-drawn annotations. A wordmark is the system naming its own product: structural, authority text, so it takes the system font (Inter) like every other label and headline. The human-voice font would mislabel a system artifact as a person speaking. This is the beat category of a product wordmark or UI chrome label rendered as type — system font, always, unless an actual logo asset exists.

  Chunk: "By 2027, your transit pass…"
  Imagery: text-only — a `class=logo` box for a "Tap" mark was weighed, rejected because no sourced logo asset exists; a plain text wordmark is type, not a dispatchable mark
  Type-role: "Tap" wordmark → system font (Inter); surrounding narration → system font (Inter); "2027" → system font (Inter) unless it sits in a data/metadata treatment, where it takes mono (JetBrains Mono)

### Caption / metadata label → mono or muted, never a hero

A deep-sea cable documentary narrates the bandwidth a single fiber pair carries, and underneath sits a small attribution: *"Source: TeleGeography Submarine Cable Map, 2024."* That credit is metadata — a citation label, not the line the viewer reads as the point of the scene — so it takes the muted color in the technical/mono font, the role `design.md` reserves for credits and figures. The narration above it ("One cable pair moves more data than the entire 1990s internet") is the actual spoken line, so it carries the system/authority font at full foreground weight; pushing the credit to muted-mono keeps it legibly subordinate, and the muted color must never bleed onto that narration line, because muted is for labels and metadata only. The trigger here is a citation/source-credit label sitting beneath a narration line — never style the credit as a hero, and never let the narration drop to muted.

  Chunk: "One cable pair moves more data…"
  Imagery: text-only — a submarine-cable-map glyph was weighed, rejected because the map is decorative backdrop, not the subject of this beat (the bandwidth claim is), and a literal cable icon would be abstract chrome that competes with the number the line lands on
  Type-role: narration line → system font (Inter), fg weight; the source credit beneath it → mono (JetBrains Mono) in the muted color (label/metadata role, never narration)

## Set C — which presentation mode delivers this beat?

Three worked verdicts on the **presentation-mode** line — emitted **only when a talking-head
source is present** (`reference/talking-head.md`), inert on the default graphics-only
pipeline. The discipline mirrors Set A: name the mode you weighed and **rejected** and why,
and land the transition on a real transcript pause / sentence boundary — never a round number,
never mid-clause. These beats are deliberately on *other* topics so the instinct generalises;
each emits the verbatim MODE line. GRAPHICS being the majority is an *outcome* of explainer
content, not a slot to fill.

### GRAPHICS full-frame — the default, face runs hidden underneath

A talking-head explainer on how TLS handshakes work lands on: *"The client and server trade
certificates, agree on a cipher, and only then does a single byte of your data move."* The
beat is a three-step mechanism — the information lives in the *sequence*, which a staged
diagram carries far harder than a face describing it. So the graphics archetype covers the
frame and the take keeps running **hidden underneath, audio unbroken** — the majority case for
a mechanism beat. FACE full-frame was weighed and rejected: the words are *about* a process,
not *to* the viewer, so a talking head would bury the steps it's narrating; PIP was rejected
too — there's no reaction or aside to inset, the diagram wants the whole frame. The transition
lands on the sentence boundary after the *prior* line ("…that's the part most people skip.")
at 41280 ms, a clean full stop, not mid-handshake.

  MODE: graphics — transition at "skip" (41280) via crossfade

### FACE full-frame — direct address, the words are *to* the viewer

A talking-head video on burnout lands on: *"And if you've felt that creeping dread on a Sunday
night — I'm telling you, you are not broken, and you are not alone."* This is direct address:
the line is *to* the viewer, not *about* a thing, and the sincerity pays off on the creator's
face, where any graphic would feel like hiding from the moment. So the take fills the frame —
archetype and imagery are moot here. GRAPHICS full-frame was weighed and rejected: there is no
referent to show, and covering the face would mute the one beat that earns eye contact; PIP was
rejected because shrinking this line into a corner inset undercuts the intimacy it's built on.
The transition lands on the `>400ms` pause before "And if you've felt…" at 138640 ms — a
held breath the narration-map flags — so the reveal breathes rather than whip-cuts.

  MODE: face — transition at "And" (138640) via crossfade

### PIP — a quick aside beside a live graphic, face inset in the reserved zone

A talking-head explainer on inflation freezes on a line chart of CPI climbing, and the creator
adds: *"Now — full disclosure, I lived through the '08 crunch, so this one hits different for
me."* The chart is the subject and stays live and fully visible, but the aside is *personal* —
a wink to the viewer that wants the face present without surrendering the data. So the face
lifts into a **bordered, drop-shadowed inset** in the chart's reserved **lower-right** safe
zone (the archetype reflowed its axis labels left to clear it), reading as deliberate framing,
never occluding a single plotted point. FACE full-frame was weighed and rejected — it would
throw away the chart the aside is layered over; GRAPHICS full-frame was rejected because hiding
the face drops the personal-aside register entirely. The transition lands on the em-dash pause
after "Now" at 232900 ms.

  MODE: pip — transition at "Now" (232900) via push; pip-safe-zone: lower-right

## Reading these

`text-only` is a first-class verdict — but only when it names the candidate it weighed and the principled reason it lost (literal/cheesy, not the subject, abstract with no mark, already carried by a neighbour); a `text-only` with no named candidate is the silent skip this pass exists to kill. None of this is a quota: a run of YES boxes and a run of bare-text cards are equally a smell, and the gate, not a target count, decides each beat. The trigger is always the sentence in front of you, never the scene number.

The same no-quota / name-your-rejection discipline governs the **presentation-mode** verdict when a talking-head source is present (Set C): a mode call — *especially* the default GRAPHICS — is first-class only when it names the mode it weighed and rejected and why, just as `text-only` must name its declined candidate; an unjustified "graphics" is the same silent skip. An all-one-mode run (every beat graphics, or every beat face) is a smell exactly like an all-imagery run — content, not a fixed slot, decides each beat, and GRAPHICS leading is an outcome to *earn*, not a target to hit.