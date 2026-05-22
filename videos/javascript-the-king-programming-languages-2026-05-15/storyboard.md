# Storyboard — How JavaScript Quietly Conquered the World

> Sample storyboard, drafted to demonstrate the artifact's shape. It sits between
> `script.md` and composition authoring, and is the synthesis layer that turns
> narration + word-level timing + the iceberg-arc direction into a buildable,
> per-block plan. It **references** the visual system rather than restating it —
> palette/type/motion tokens belong in a `design.md` (this video doesn't have one
> yet; the Global Direction block below is the proto-design until it does).
>
> Timing is the **enriched pass**: every window and anchor below is a real
> `transcript.json` timestamp (global seconds), not a round number. At build,
> snap block boundaries to the nearest `spacing` row. Re-run the anchor resolver
> if the voiceover is recut.

---

## Global direction

- **Format:** 1920×1080, ~601s (10:01). Single audio track `audio/voiceover.mp3`. GSAP is wired in `index.html` and stays the choreography backbone — but it isn't the only tool; each beat picks its adapter / catalog item from the tooling menu (see `learnings/storyboard-template.md`).
- **Voiceover:** recorded own voice (the project default), cut in `tools/audio-editor` from `audio/raw.mp3`. The Scribe v2 `transcript.json` is timing truth — animation lands on the spoken word.
- **Style basis:** iceberg-arc subversion (per `notes.md`). Tip = "JS is for websites." Subversion = "JS is the substrate under every screen you touch." The 2014 "escape the browser" quote is the spine: stated at the hook, honored through the body, closed at the landing.
- **Core motif — the substrate.** JavaScript renders as an *underlayer* that creeps upward. A faint monospace code-rain lives in the deep background and gains density each time JS captures a new domain (browser → server → desktop → mobile → OS → the model corpus). By the climax it saturates the frame.
- **Spine — the timeline.** A horizontal time axis 1995 → 2026 runs across the mid-layer. The "camera" travels along it left-to-right; most beat-to-beat transitions are diegetic travel along this spine, not hard cuts. Year ticks (1995, 2009, 2015, 2024, 2026) are content/atmosphere, not chrome.
- **Palette (proposed → promote to `design.md`):** near-black `#000` base; single accent JS-yellow `#f7df1e`; "establishment / other languages" in desaturated slate `#5b6675`; paper-white `#f4f4f0` for quote type. Accent yellow is rationed — it only marks JavaScript itself.
- **The "escape" visual.** A browser-chrome box contains the yellow JS mark; at "escaped the browser" the mark literally breaks the box. Same escape-box primitive is reused for each subsequent domain it breaks into.
- **Project constraints (root CLAUDE.md):** no editorial chrome — no scene labels, part numbers, or running timecodes on screen. Ambient decoratives (glows, grid, ghost type, the code-rain, the timeline spine) are in scope. Multi-block from scene one. Check the registry before hand-rolling any primitive.

---

## Block plan (multi-block from scene one)

| # | Block file | Window (s) | Dur | Beat |
|---|------------|-----------|-----|------|
| 00 | `compositions/00-hook.html` | 0.0 – 29.0 | 29.0 | HOOK — the disgust quote |
| 01 | `compositions/01-origin.html` | 29.0 – 136.1 | 107.1 | Q1 — how JS came to be |
| 02 | `compositions/02-server.html` | 136.1 – 292.2 | 156.1 | Q2 — JS reaches the server |
| 03 | `compositions/03-rehook.html` | 292.2 – 315.5 | 23.3 | RE-HOOK — the quote returns |
| 04 | `compositions/04-electron.html` | 315.5 – 387.9 | 72.4 | Q3a — desktop / Electron |
| 05 | `compositions/05-react-native.html` | 387.9 – 435.5 | 47.6 | Q3b — mobile / React Native |
| 06 | `compositions/06-terror-reign.html` | 435.5 – 457.4 | 21.9 | the app roll-call |
| 07 | `compositions/07-climax-windows.html` | 457.4 – 517.9 | 60.5 | CLIMAX — Windows 11 Start menu |
| 08 | `compositions/08-flywheel.html` | 517.9 – 567.9 | 50.0 | Q4 — the LLM flywheel + SO survey |
| 09 | `compositions/09-thesis-landing.html` | 567.9 – 601.3 | 33.4 | THESIS + LANDING |

---

## Beat sheet

### 00 · HOOK — "this awful language has escaped the browser"
- **Window:** 0.0 – 29.0 · `compositions/00-hook.html`
- **Anchors:** "this awful language" @ **2.40** · "escaped the browser" @ **4.04** · "infrastructure" @ **22.12** · "how did that happen?" @ **23.96–25.44**
- **On screen:** The danbruc HN quote types onto a paper-white card over black. On "escaped the browser," the yellow JS mark inside a small browser-chrome box punches through the box edge. Cut to a cold stat line — JS "runs the world's infrastructure, 2026."
- **Camera / mood:** Static, tight, ominous. The hook holds before the spine appears.
- **Adapter:** `gsap` (quote + box choreography) · `css-animations` (the code-rain loop).
- **Catalog candidates:** `caption-highlight` / `caption-editorial-emphasis` for the quote-word treatment; `vfx-shatter` or `vfx-portal` for the escape-box break (instead of hand-rolling the mask-break); `grain-overlay` + `vignette` for global atmosphere.
- **Motion:** GSAP. Typewriter reveal of the quote (clip-path or per-word stagger keyed to the spoken words 2.40→5.04). Escape-box break = scale + rotate + mask-break on the JS mark at 4.04. "How did that happen?" pulls back to reveal the empty timeline spine at 1995.
- **Depth:** code-rain (far, sparse) · quote card (near) · no spine yet.
- **Transition out:** camera pull-back lands on the **1995** tick of the timeline spine → into block 01.
- **SFX intent:** sub-bass drone under the quote; single typewriter texture; a low *thunk* on the box-break at 4.04.
- **Blocks used:** `quote-card`, `escape-box`, `timeline-spine`.

### 01 · Q1 — "How did JavaScript come to be?"
- **Window:** 29.0 – 136.1 · `compositions/01-origin.html`
- **Anchors:** "came to be" @ **31.16** · "May 1995" @ **33.28** · "Java was too heavy" @ **38.82** · "Brendan Eich" @ **64.20** · "10 days" @ **68.00**, prototype "in 10 days" @ **71.40** · "Mocha" @ **73.88** · "LiveScript" @ **78.48** · "renamed it to JavaScript" @ **82.12** · "designed to be available" @ **127.00**
- **On screen:** Question card Q1. Spine parks at **1995**. "Java too heavy / C too low-level" shown as two heavy slate blocks that won't fit a lightweight browser slot. Eich enters; a 10-day countdown ticks. The **rename chain** Mocha → LiveScript → JavaScript morphs in place, each label stamped on its month. Close on "designed to be available, not to win" as a thesis pin.
- **Camera / mood:** Wry, brisk. Travel into the 1995 marker, settle.
- **Adapter:** `gsap`.
- **Catalog candidates:** `caption-weight-shift` for the "available ≠ win" split; a shader transition (`cross-warp-morph`) for the rename-chain morphs if the local block feels heavy.
- **Motion:** GSAP timeline. Slate blocks try-and-fail to dock (38.82). Countdown is a deterministic seek-driven counter, not `Date.now()`. Rename-chain cross-morph keyed to 73.88 / 78.48 / 82.12. "Available ≠ win" splits one word into two diverging labels at 127.00.
- **Depth:** code-rain (far) · spine (mid) · origin scene (near).
- **Transition in:** continued spine travel from hook. **Out:** spine travels forward; years blur past 1995→2009 toward block 02.
- **SFX intent:** clock tick under the 10-day countdown; a stamp/click on each rename; soft *pin* on the thesis line.
- **Blocks used:** `question-card`, `timeline-spine`, `rename-chain`, `stat-counter` (countdown), `escape-box` (browser slot).

### 02 · Q2 — "How the hell did JavaScript get to the server?"
- **Window:** 136.1 – 292.2 · `compositions/02-server.html`
- **Anchors:** "get to the server" @ **137.80** · "For 14 years, it didn't" @ **139.76** · "November 2009" @ **154.70** · "Ryan Dahl" @ **158.70** · "Berlin" @ **161.22** · "150 people" @ **162.90** · "Apache" @ **165.88** · "every request opened a new thread" @ **173.04** · "no I/O library" @ **243.44** · "thought in events" @ **252.38** · "V8" @ **259.50** · "event loop" @ **264.06** · "Node.js" @ **269.06** · "standing ovation" @ **271.86** · "first in the [conference's history]" @ **273.52** · "JavaScript had escaped the browser" @ **288.72–290.96**
- **On screen:** Question card Q2. Spine at **2009**. The "14 years" gap shown as JS pinned inside the browser box while Perl→PHP→Python→Ruby cycle through the server slot. Dahl on a small stage, "150" audience dots. Apache thread-per-request: threads stack and the server bar collapses under load. Then the contrast — other languages bolt async on (EventMachine, Twisted shown fighting their defaults) vs. JS as a clean empty I/O slate. V8 + event loop wrap into the **Node.js** mark. Standing ovation: the 150 dots rise. End on the JS mark breaking the browser box a second time — "escaped the browser."
- **Camera / mood:** The longest beat — earns a build. Tension (Apache collapse) → release (ovation). Travel down into the server layer.
- **Adapter:** `gsap` (the build); consider `three` for the event-loop ring if you want true 3D depth.
- **Catalog candidates:** `flash-through-white` on the Apache collapse; `caption-highlight` on "escaped the browser". (The load bar / 150 dots stay local blocks — `data-chart` is the wrong shape here.)
- **Motion:** GSAP. Server-load bar climbs then collapses ~173–176. Async-bolt-on libraries judder/stall on 243.44. Event-loop ring spins up around V8 at 259.50→264.06, resolving to the Node mark at 269.06. Ovation = staggered dot rise 271.86. Second escape-box break at 290.22 (rhyme with the hook's break at 4.04 — same primitive, same motion, larger scale).
- **Depth:** code-rain density steps up after Node lands · spine (mid) · server scene (near) · ovation dots (foreground).
- **Transition in:** spine travel from 01. **Out:** hold on the broken box — hard match-cut into block 03 (the quote returns).
- **SFX intent:** server-room hum bed; stacking *clicks* as threads pile; a low *crash* on collapse; sparse real-applause swell on the ovation (subtle, not a stadium); riser into the box-break.
- **Blocks used:** `question-card`, `timeline-spine`, `escape-box`, `app-logo-grid` (language logos in the server slot), `stat-counter` (150 dots / load bar).

### 03 · RE-HOOK — "And there's the line."
- **Window:** 292.2 – 315.5 · `compositions/03-rehook.html`
- **Anchors:** "And there's the line" @ **292.22–292.76** · "Hacker News commenter, 2014" @ **293.66** · "We allowed this awful…" @ **298.91** · "infiltrate our servers" @ **302.34**
- **On screen:** The exact hook quote-card returns — but now the verb "escape" and "infiltrate our servers" highlight in yellow, recontextualized. The 2014 attribution stamps under it. Close on "he was right about the escape — but didn't know what was coming next," with the spine teasing forward past 2009.
- **Camera / mood:** Snap back to the cold hook framing. The payoff of the loop. Brief, deliberate.
- **Adapter:** `gsap`.
- **Catalog candidates:** `caption-highlight` / `caption-editorial-emphasis` for the "escape"/"infiltrate" word sweep — the textbook word-timed caption use; prefer it over a hand-rolled marker. `whip-pan` for the match-cut in.
- **Motion:** GSAP. Reuse `quote-card` with a `highlight` variable; marker-sweep the "escape"/"infiltrate" words on 290→302 (consider the registry highlight/marker primitive). Attribution stamp at 295.72.
- **Depth:** quote card (near) over a now-denser code-rain.
- **Transition in:** match-cut from the broken box in 02. **Out:** "what was coming next" → forward spine travel into 04.
- **SFX intent:** reverse riser / time-rewind whoosh on the quote return; typewriter on the attribution; a held breath before "what was coming next."
- **Blocks used:** `quote-card` (reused, highlighted), `timeline-spine`.

### 04 · Q3a — Desktop / Electron
- **Window:** 315.5 – 387.9 · `compositions/04-electron.html`
- **Anchors:** "mobile and desktop. How?" @ **315.54** · "Cheng Zhao" @ **321.76** · "Atom" @ **343.00** · "Atom Shell" @ **356.34** · "Electron" @ **360.36** · "thumbs-up" @ **366.44**
- **On screen:** Question card Q3 (mobile + desktop). Spine at **2013**. Chromium + Node.js fuse into one runtime box (Atom Shell). Rename Atom Shell → **Electron** (reuse `rename-chain`). The gag: a chat app "ships a whole browser to render a thumbs-up" — a giant browser box collapses down to a single 👍.
- **Camera / mood:** Lighter, comedic timing on the thumbs-up. Travel up out of the server layer onto the desktop layer.
- **Adapter:** `gsap`.
- **Catalog candidates:** `vfx-shatter` for the browser-box → thumbs-up collapse; `macos-notification` social overlay if you want a diegetic chat-app frame around the 👍.
- **Motion:** GSAP. Two source boxes (Chromium, Node) merge at ~356. Rename morph at 360.36. Browser-box → thumbs-up scale-collapse punchline at 366.44.
- **Depth:** code-rain (mid-density now) · desktop-window mock (near).
- **Transition in:** spine travel from 03. **Out:** desktop window slides aside for the Facebook bet → 05.
- **SFX intent:** mechanical fuse/clunk on the runtime merge; UI *pop* on the thumbs-up.
- **Blocks used:** `question-card`, `timeline-spine`, `rename-chain`, `escape-box` (browser→app).

### 05 · Q3b — Mobile / React Native
- **Window:** 387.9 – 435.5 · `compositions/05-react-native.html`
- **Anchors:** "biggest mistake we've made" @ **387.90** · "Jordan Walke" @ **406.16** · "actual native widgets" @ **417.10** · "March 2015 / F8" @ **429.12** · "React Native" @ **431.26**
- **On screen:** Spine at **2015**. Zuckerberg's "biggest mistake" — the HTML5 mobile bet shown crossed-out; two native codebases (iOS + Android) split apart, "twice the cost." Walke's hackathon: one JS component tree drives **two real native widget sets** (not a webview — emphasize the native boundary crossing). Stamp "React Native, F8, March 2015."
- **Camera / mood:** The bet/reversal. Two-column split (iOS | Android) converging back to one JS source.
- **Adapter:** `three` for the device frames + `gsap` for the converge.
- **Catalog candidates:** `vfx-iphone-device` (3D device showcase) for the iOS/Android frames; a `caption-*` strike for the "biggest mistake" cross-out.
- **Motion:** GSAP. HTML5 bet strikes through at 387.90. Codebase split diverges, then a single JS tree re-converges to drive both columns at 417.10. RN stamp at 431.26.
- **Depth:** code-rain · two device frames (near).
- **Transition in:** slide from 04. **Out:** device frames multiply outward into the app roll-call → 06.
- **SFX intent:** error *buzz* on "biggest mistake"; native UI *click* when JS drives the real widgets; stamp on the RN reveal.
- **Blocks used:** `question-card` (or carry Q3 card), `timeline-spine`, `app-logo-grid` (device frames).

### 06 · The terror reign — the roll-call
- **Window:** 435.5 – 457.4 · `compositions/06-terror-reign.html`
- **Anchors:** "terror reign" @ **435.50** · VS Code @ **440.46** · Slack @ **442.40** · Discord @ **444.16** · Figma @ **444.94** · Notion @ **445.62** · 1Password @ **446.34** · Obsidian @ **446.94** · "your favorite chat app is a browser too" @ **455.20**
- **On screen:** Rapid logo grid — VS Code, Slack, Discord, Figma, Notion, 1Password, Obsidian — each snapping in *on its spoken word* (this is the densest sync moment in the video; the logos are ~0.5–0.8s apart, so timing must be exact). Each logo, on landing, briefly flips to reveal the JS/Electron mark underneath. Close: "your code editor is a browser… your chat app is a browser too."
- **Camera / mood:** Machine-gun rhythm, the build's peak density. No camera travel — let the cuts carry it.
- **Adapter:** `lottie` for the app logos (icon reveals) + `gsap` for the per-word timing.
- **Catalog candidates:** `caption-kinetic-slam` for the roll-call words; `grid-pixelate-wipe` or a Grid CSS transition for the collapse-to-point out.
- **Motion:** GSAP stagger, but **per-logo anchored** to the timestamps above (not an even stagger — the words aren't evenly spaced). Each logo: snap-in + flip-to-reveal-JS.
- **Depth:** code-rain near-saturated · logo grid (near).
- **Transition in:** frames multiply from 05. **Out:** all logos collapse toward a single point → the Windows climax wipe.
- **SFX intent:** rapid-fire stamp/*chunk* per logo, rhythmic; a final stacked hit on "browser too."
- **Blocks used:** `app-logo-grid` (the marquee use — parametrized list of {name, logo, anchor}).
- **Registry note:** check `npx hyperframes catalog --tag transition` for a clean grid-collapse wipe before hand-rolling the out-transition.

### 07 · CLIMAX — the Windows 11 Start menu
- **Window:** 457.4 – 517.9 · `compositions/07-climax-windows.html`
- **Anchors:** "2024" @ **457.40** · "Windows 11" @ **463.44** · "Start menu" @ **464.04** · "XAML" @ **469.96** · "React Native for Windows" @ **502.26** · "drawing its own menu in the language one engineer wrote in **ten days**" @ **513.80 / 514.82 / 515.50**
- **On screen:** The payoff — a pixel-faithful Windows 11 Start menu renders, looking fully native. On "not a webview… actual native UI controls described in JavaScript," the menu's "recommended" section **peels back** like a label to reveal React Native → XAML → JS underneath. Microsoft's deliberate choice (ship-fast / iterate-fast) shown as the reason. Land hard on the callback: "the most-deployed OS on the planet, drawing its own menu in the language one engineer wrote in ten days" — echo the 10-day countdown from block 01.
- **Camera / mood:** The iceberg subversion lands. Slow, confident push-in on the Start menu, then the reveal. This is the single most surprising fact in the video — give it air.
- **Adapter:** `gsap` + a shader transition for the peel.
- **Catalog candidates:** `sdf-iris` / `cross-warp-morph` / `vfx-portal` for the peel-to-reveal; `cinematic-zoom` for the push-in.
- **Motion:** The **`start-menu-peel`** reveal. Build with CSS `clip-path` + GSAP, or a registry shader transition for the peel — evaluate both. XAML/RN/JS layers stack in z at 469.96→502.26. Callback: re-mount the block 01 countdown digits briefly at 515.50 (the "ten days" rhyme is the emotional hinge — make the visual rhyme explicit).
- **Depth:** code-rain fully saturated behind · Start menu (near) · peeled reveal layers (foreground, stacked z).
- **Transition in:** collapse-to-point wipe from 06 resolves into the Start menu. **Out:** pull back; spine ticks to **2026** → flywheel.
- **SFX intent:** Windows-startup-adjacent soft chime (suggestive, not the literal trademark); a satisfying *peel/reveal* sting on the label pull; low boom on the "ten days" callback.
- **Blocks used:** `start-menu-peel` (new, parametrize the peel-to-reveal so any "looks native, is JS" reveal can reuse it), `timeline-spine`, `stat-counter` (countdown rhyme).
- **Registry note:** browse `--tag transition` / `--tag reveal` for the peel before hand-rolling.

### 08 · Q4 — the LLM flywheel + the survey
- **Window:** 517.9 – 567.9 · `compositions/08-flywheel.html`
- **Anchors:** "In 2026" @ **517.92–518.20** · "every large language model" @ **519.66** · "every npm package" @ **529.02** · "Stack Overflow" @ **531.94** · "forty-nine thousand engineers" @ **554.20** · "Sixty-six percent" @ **563.08** · "the single most-used language on the planet" @ **565.38–566.60**
- **On screen:** Spine at **2026**. The compounding loop visualized as a flywheel: GitHub repos + npm + blog posts + Stack Overflow answers → training corpus → generated code → shipped code → next corpus. The loop spins faster each cycle. Then the SO 2025 survey: **49,000** engineers count up, **66%** fills a bar, "#1 every year for over a decade." Keep the LLM claim appropriately hedged per `substrate-notes.md` ("appears to," "likely") — reflect that softening visually (dashed/uncertain edge on the corpus node), don't assert it as hard fact.
- **Camera / mood:** Accelerating, inevitable. The flywheel literally accelerates with the VO.
- **Adapter:** `waapi` for the data-driven counters + `gsap` for the flywheel ramp.
- **Catalog candidates:** `data-chart` for the SO survey (66% bar / 49,000 count) — direct fit, install it rather than building a counter; `flowchart` as the base for the compounding-loop diagram.
- **Motion:** GSAP. Flywheel rotation speed ramps across 519→554. `stat-counter` count-up to 49,000 keyed to 554.20; 66% bar fill keyed to 563.08 — both deterministic, seek-driven (no `Date.now()`/`Math.random()`).
- **Depth:** code-rain (the corpus — now the literal background subject) · flywheel diagram (near) · stat overlay (foreground).
- **Transition in:** spine travel from 07. **Out:** flywheel slows to a stop on the thesis line → 09.
- **SFX intent:** rising looped tone that accelerates with the flywheel; tick per counter increment; a clean *snap* when 66% locks.
- **Blocks used:** `question-card`, `timeline-spine`, `stat-counter` (count-up + bar), `flywheel` (new diagram block).

### 09 · THESIS + LANDING
- **Window:** 567.9 – 601.3 · `compositions/09-thesis-landing.html`
- **Anchors:** "didn't win on quality" @ **568.40–569.24** · "won on supply" @ **570.44–571.08** · "the kid Netscape hired… now writes the world" @ **572.24 / 576.04** · "the next time you open…" @ **585.96** · "Because it was already there" @ **596.30–598.02**
- **On screen:** Two words face off — **QUALITY** (slate, struck) vs **SUPPLY** (yellow, standing). The kid-in-10-days line callbacks once more. Landing: the viewer's own toolbar — code editor, password manager, the Start menu — each briefly flips to reveal JS underneath (rhymes with block 06), then resolve on the closing line over near-black: "Not because it won. Because it was already there." Code-rain settles to a calm, persistent baseline — it never fully leaves.
- **Camera / mood:** Resolve. Slow, quiet, earned. Drop the spine; return to the intimate framing of the hook to close the loop.
- **Adapter:** `gsap` + `css-animations` (code-rain settle to baseline).
- **Catalog candidates:** `caption-weight-shift` for the QUALITY-vs-SUPPLY face-off; a Dissolve CSS transition to black.
- **Motion:** GSAP. QUALITY strike-through + SUPPLY emphasis at 569/571. Toolbar flip-reveals staggered across 585→595. Final line fades up at 596.30 and holds to 599.87 (audio end), block runs to 601.3.
- **Depth:** code-rain (calm baseline) · closing type (near).
- **Transition in:** flywheel stop from 08. **Out:** fade to black on the held line.
- **SFX intent:** single clean resolving tone on "supply"; soft UI flips on the toolbar reveal; silence under the final line — let it land dry.
- **Blocks used:** `escape-box`/reveal-flip (reused on toolbar), `quote-card` (closing line styling).

---

## Reusable blocks to author (parametrized, under `compositions/`)

These are the didactic-explainer primitives this video needs as parametrized blocks
(`data-composition-variables` on the root, mounted via `data-composition-src` +
`data-variable-values`). Several recur across beats — the whole argument for making
them blocks now rather than inlining. **Some have catalog alternatives** (note under
the table); reach for those first.

| Block | Params | Used by beats |
|-------|--------|---------------|
| `timeline-spine` | year range, marker years, camera-x position | 00–02, 04–05, 07–08 (the connective tissue) |
| `quote-card` | text, attribution, highlight words, accent | 00, 03, 09 |
| `escape-box` | payload label, break-direction, scale | 00, 02, 04, 09 |
| `rename-chain` | ordered labels, per-label anchor | 01, 04 |
| `stat-counter` | mode (countdown/count-up/bar), value, label, anchor | 01, 02, 07, 08 |
| `app-logo-grid` | list of {name, logo, anchor, reveal?} | 02, 05, 06 |
| `question-card` | question text, index | 01, 02, 04, 08 |
| `start-menu-peel` | top-layer asset, revealed stack labels | 07 |
| `flywheel` | node labels, ramp curve | 08 |

**Catalog alternatives — evaluate before authoring:** `flywheel` → `flowchart`; `stat-counter` (count-up / bar) → `data-chart`; `app-logo-grid` logos → `lottie` icon reveals; `escape-box` break → `vfx-shatter` / `vfx-portal`. Author the local block only when the catalog item can't be word-anchored or styled to the design. `timeline-spine`, the `quote-card` rhyme, and `start-menu-peel` have no catalog equivalent — those stay local.

## Check the catalog first
Browse visually at https://hyperframes.heygen.com/catalog/ (or `npx hyperframes catalog`), then `npx hyperframes add <slug>` + the `hyperframes-registry` skill to wire. Strong candidates for this video:
- **Captions (word-timed):** `caption-highlight`, `caption-editorial-emphasis` (00, 03); `caption-kinetic-slam` (06); `caption-weight-shift` (01, 09).
- **Transitions:** `whip-pan` (03); `flash-through-white` (02); `grid-pixelate-wipe` (06 collapse); `sdf-iris` / `cross-warp-morph` / `vfx-portal` + `cinematic-zoom` (07 peel + push-in); a Dissolve CSS transition (09).
- **VFX:** `vfx-shatter` / `vfx-portal` (00, 04 breaks); `vfx-iphone-device` (05 device frames).
- **Data / diagram:** `data-chart` (08 survey); `flowchart` (08 loop).
- **Atmosphere:** `grain-overlay`, `vignette`, `shimmer-sweep` (global).

Hand-roll only the didactic primitives the catalog lacks (`timeline-spine`, the escape-box rhyme, `start-menu-peel`) — see Reusable blocks above.

## Open questions for the human before build
- **Logos/assets:** the roll-call (06) and device frames (05) need real logo assets in `assets/`. Confirm sourcing/licensing, or stylize as generic glyphs.
- **Windows Start menu (07):** pixel-faithful mock vs. stylized? Faithful sells the subversion harder but is more asset work.
- **LLM-flywheel hedge (08):** confirm the on-screen copy stays softened ("appears to") per `substrate-notes.md` and `fact-check.md` — the visual shouldn't over-assert the unverified compounding claim.
- **No `design.md` yet:** promote the Global Direction palette/type/motion into a real `design.md` so this storyboard can reference it instead of carrying it.
