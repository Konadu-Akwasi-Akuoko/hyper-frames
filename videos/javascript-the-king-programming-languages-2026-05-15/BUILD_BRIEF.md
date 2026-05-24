# BUILD_BRIEF — JS: The King of Programming Languages

> **For sequential subagents building this video.** Read before writing any HTML.
> Every word-level timestamp comes from `transcript.json` (Scribe v2 format).

## Goal

Every beat (5-15s) of narration must have a strong visual metaphor — a diagram,
a diagram-like UI, a code snippet, a counter, a chart — not just text fading in.
The bar is scene-01 Movement A (browser-to-server escape + 2026 to 2014 timeline).
That level of visual specificity must hold throughout the video.

"Every sentence has an animation" means: for every paragraph of narration,
identify WHAT IT SHOWS (not just what it says) and build that visual. Text-only
movements are not acceptable.

## Autonomous mode

The user is sleeping. Do NOT ask questions. Make all design decisions from this
brief, the design.md, and the established patterns. When genuinely ambiguous, pick
the richer visual.

---

## Scene table

Each scene is a sub-composition mounted in `index.html` at the specified
`data-start` and `data-duration`. All data-track-index values are 1
(substrate is 0, audio is 9).

| # | File | data-start | data-duration | Content |
|---|------|-----------|---------------|---------|
| 1 | scene-01-hook.html | 0 | 24.4 | Hook [EXISTS, B+C improved] |
| 2 | scene-02-birth.html | 24.4 | 57.6 | Birth: Netscape 1995, Brendan Eich, 10 days, Mocha |
| 3 | scene-03-name-game.html | 82.0 | 48.0 | Name game + designed to be available |
| 4 | scene-04-server-question.html | 130.0 | 20.68 | Server question + "for 14 years it didn't" |
| 5 | scene-05-ryan-dahl.html | 150.68 | 56.32 | Ryan Dahl on stage, Apache choking, chose JS |
| 6 | scene-06-node.html | 207.0 | 50.0 | EventMachine/Twisted fail, JS no I/O, V8+event loop, Node.js, ovation |
| 7 | scene-07-escape.html | 257.0 | 38.0 | Within months, centre divs, "JS had escaped", HN callback |
| 8 | scene-08-electron.html | 295.0 | 45.0 | Cheng Zhao, Atom Shell to Electron, browser-inside-app |
| 9 | scene-09-react-native.html | 340.0 | 45.0 | Facebook's bet, Zuckerberg quote, Jordan Walke, React Native |
| 10 | scene-10-terror-reign.html | 385.0 | 77.0 | Terror reign: VS Code/Slack/Discord, Windows 11, React Native for Windows |
| 11 | scene-11-verdict.html | 462.0 | 53.0 | In 2026: LLM training, Stack Overflow 66%, quality vs supply |
| 12 | scene-12-landing.html | 515.0 | 15.617 | Landing: the next time you open your code editor |

All scenes share `data-track-index="1"` and `style="position:absolute;inset:0;z-index:1"`.
The substrate (track 0) and voiceover audio (track 9) persist at their own tracks.

---

## Narration beats per scene

### Scene 2 — Birth (24.4-82s)

Key word timestamps (global audio time):
- 24.40s "Let's" / 24.68s "answer" — chapter question begins
- 28.10s "be?" — chapter question ends
- 30.98s "In" / 31.12s "May" / 31.56s "1995"
- ~38-50s: Java was too heavy, C unthinkable, needed something any intern could write
- 62.06s "Brendan" / 62.52s "Eich" — engineer card appears
- ~65s: "gave him a deadline, 10 days"
- 71.76s "Mocha." — first name
- ~75s: "By September 1995, called LiveScript"
- ~79s: "By December same year, renamed to JavaScript"
- 81.20-81.84s "JavaScript." — scene ends

Beat plan:
1. (24.4-31s) Chapter question — "How did JavaScript come to be?" — animated JS logo
2. (31-62s) May 1995 Netscape context — diagram: Java (heavy block) vs JS (light dot), the gap Netscape needed to fill
3. (62-71.76s) Brendan Eich profile + 10-day countdown timer ticking down
4. (71.76-82s) The naming parade — "Mocha" strikethrough, "LiveScript" strikethrough, "JavaScript" confirmed

### Scene 3 — Name Game + Available (82-130s)

Key word timestamps:
- 82.72s "At" / 85.0s "aliases" — "more aliases than your bashrc file"
- 86s: bashrc code snippet visual
- ~93-110s: "nothing to do with Java — marketing move" / "slapping AI on your startup today"
- 111.28s "So with time" / 113.92s "Mocha." — narrator self-corrects: Mocha... no... LiveScript... sorry... JavaScript
- 116.00s "Hey," / 116.42s "guys." / 117.74s "JavaScript." — the correction lands
- 119.58s "JavaScript wasn't" / 122.10s "win."
- 123.24s "It" / 124.40s "available,"
- 127.52s "Those" / 129.02s "things." — scene ends

Beat plan:
1. (82-93s) Terminal window: bash aliases cycling through the JS name history
2. (93-111s) Java != JavaScript — split panel: Java coffee cup vs JS logo, NO connection. Then the AI-startup parallel.
3. (111-120s) Animated text correction sequence — the narrator's stumble shown as on-screen text edits
4. (120-130s) Split card: DESIGNED TO WIN (empty) vs DESIGNED TO BE AVAILABLE (full)

### Scene 4 — Server Question (130-150.68s)

Key word timestamps:
- 130.16s "guys," / 132.72s "how" / 133.16s "hell" / 135.02s "server?"
- 136.38s "For" / 136.54s "14" / 137.18s "years," / 138.07s "didn't."
- 139.84s "Perl," / 141.08s "PHP," / 142.36s "Python," / 143.52s "Ruby."
- 144.48s "JavaScript" / 146.90s "browser," / 149.70s "there."

Beat plan:
1. (130-136s) Confrontational headline: "How the HELL did JavaScript get to the server?"
2. (136-150.68s) Server rack diagram — Perl, PHP, Python, Ruby as residents. JS icon locked outside with a "browser only" label.

### Scene 5 — Ryan Dahl (150.68-207s)

Key word timestamps:
- 150.68s "But" / 151.31s "November" / 151.70s "2009,"
- 155.30s "Ryan" / 155.62s "Dahl," / 156.50s "walked" / 157.34s "stage" / 157.84s "Berlin"
- 159.62s "150" / 160.98s "people."
- 162.42s "Apache" / 163.16s "choke"
- ~167s: Every request opened a new thread
- ~170s: Every thread ate memory
- ~173s: Server collapsed
- ~177s: wanted something that didn't block
- 178.58s "JavaScript" — "And he chose JavaScript"
- ~183s: ten-day-old language replacing battle-tested Apache
- ~193s: switched stacks as fast as abandoning a JS framework

Beat plan:
1. (150.68-160s) JSConf EU Berlin 2009 — stage diagram, a lone speaker figure, "150 people" as chair icons
2. (160-178s) Apache choking — connection counter spinning up, thread bars filling, memory bar hitting red, server crash
3. (178-207s) The surprising choice — JS badge vs Apache logo. The "10-day-old language" annotation. The JS-framework-abandonment aside.

### Scene 6 — Node.js Birth (207-257s)

Key word timestamps:
- 207.40s "Ruby" / 208.40s "Event" / 208.86s "Machine."
- 209.94s "Python" / 210.70s "Twisted."
- ~213s: "second a normal blocking call slipped in, the whole thing stalled"
- 222.24s: "JavaScript" / 223.56s-224.36s "no I/O library"
- ~225s: "No legacy, no defaults to fight"
- 232.49-233.53s "thought in events" — JS devs already had the mental model
- ~240s: "He took V8, the JS engine powering Google Chrome"
- ~244s: "wrapped it in an event loop"
- ~246s: "turned it into a server runtime"
- 248.22s "called" / 249.10s "Node.js."
- 251.98s "standing" / 252.32s "ovation," / 255.22s "history."

Beat plan:
1. (207-222s) Ruby EventMachine and Python Twisted shown as "bolt-ons" — a blocking call crashing each
2. (222-240s) Clean slate — JS = blank canvas with no I/O. Contrast with other languages' tangle. "JS devs already thought in events."
3. (240-252s) Assembly diagram: V8 engine icon + event loop ring + arrow = Node.js
4. (252-257s) Standing ovation — silhouettes rising, "first in conference history" caption

### Scene 7 — The Escape Confirmed (257-295s)

Key word timestamps:
- 256.0s "Within" / 256.74s "months,"
- ~258-261s: tens of thousands of engineers
- ~261-264s: "the people who centre divs for a living got to touch a database"
- 267.06s "JavaScript" / 268.60s "escaped" / 269.80s "browser."
- 270.62s "And" / 271.0s "there's" — the callback
- 273.5s "Hacker News commenter" / 274.14s "2014"
- ~277s: "We allowed this awful language to escape the browser and infiltrate our servers"
- 284.26s "right about the escape."
- ~287s: "But he didn't know what was coming next."
- 290.82s "went" / 291.42s "mobile" / 292.20s "desktop." / 292.94s "How?"

Beat plan:
1. (257-267s) Engineer counter spinning up. Then the "centre divs" joke: CSS code → SQL query side by side.
2. (267-270s) "JavaScript had escaped the browser." — full-screen payoff, JS-yellow.
3. (270-288s) HN card callback — quote reappears. "escape" lights green (he was right), "what was coming next" glows cyan.
4. (288-295s) Chapter hook slide: "JavaScript... went to mobile and desktop. How?"

### Scene 8 — Electron (295-340s)

Key word timestamps:
- 293.98s "In" / 294.12s "2013," / 296.16s "GitHub" / 297.52s "Chen" / 297.90s "Zhou"
- 298.96s "wrapped" — Chromium + Node.js
- 305.36s "Atom," — the hackable editor
- ~311s: "Atom's pitch: customizable in the same language as its users"
- 318.64s "Atom" / 322.68s "Electron."
- ~325s: GitHub renamed it Electron
- ~327s: "messaging app ships an entire browser to render a thumbs-up"
- ~333s: "torching memory like it was free"

Beat plan:
1. (295-308s) 2013 GitHub: Cheng Zhao profile card. Chromium + Node.js logos combining.
2. (308-322s) Atom editor wireframe with "hackable in JS" pitch. "Atom had to ship with a browser inside it."
3. (322-340s) Atom Shell to Electron rename. Absurdity panel: thumbs-up emoji inside browser chrome inside app window. Memory usage: 800MB for a chat message.

### Scene 9 — React Native (340-385s)

Key word timestamps:
- 337.74s "2012," / 339.28s "Zuckerberg"
- 343.34s "biggest" / 343.80s "mistake"
- ~346s: scrapped HTML5, rebuilt native — iOS AND Android
- ~350s: two codebases, twice the cost
- 357.72s "Jordan" / 358.60s "Walke"
- ~360s: internal hackathon
- ~363s: React component model driving real native UI on iOS
- ~367s: not a webview — actual native widgets
- 377.75s "March" / 378.77s "2015"
- 379.97s "React" / 381.23s "Native."

Beat plan:
1. (340-357s) Zuckerberg quote card ("the biggest mistake we've made as a company"). Then: 2-column split — iOS codebase | Android codebase = 2x cost.
2. (357-379s) Jordan Walke hackathon: a component tree morphing into phone wireframe native controls.
3. (379-385s) React Native announcement: F8 2015. One JS codebase arrow splitting to iOS + Android.

### Scene 10 — Terror Reign (385-462s)

Key word timestamps:
- 381.93s "And that was the beginning of a terror reign"
- 385.49s "JavaScript" / 387.49s "dominant"
- ~390s "VS Code is Electron. Slack is Electron."
- ~395s "Discord, Figma, Notion, 1Password, Obsidian — all Electron."
- ~400s "Your code editor is a browser."
- ~402s "Your password manager is a browser."
- 405.25s "Now" / 406.07s "2024,"
- 412.13s "Windows 11 Start" / 413.49s "menu"
- ~418s: built with React Native
- ~425s: "not a webview — actual native UI controls, described in JavaScript"
- 447.45s "React Native for Windows,"
- 460.01s "wrote" / 460.69s "10" / 460.93s "days."

Beat plan:
1. (385-392s) "Terror reign" title — JS at center, radiation lines.
2. (392-405s) App hall of fame — VS Code, Slack, Discord, Figma, Notion, 1Password, Obsidian — each with "Electron" badge. Then: the browser-inside-each-app reveal.
3. (405-430s) Windows 11 moment — Start menu wireframe drawn in JS-yellow lines. React Native label.
4. (430-462s) React Native for Windows + the 10-days callback: Brendan Eich's "10 days" now writes the Windows Start menu.

### Scene 11 — Verdict (462-515s)

Key word timestamps:
- 461.83s "In" / 462.07s "2026,"
- ~463-467s: every LLM trained on code where JS dominates
- 475.83s "Stack" / 476.37s "Overflow's"
- ~477-481s: 49,000 engineers, JS came in first, every year for a decade
- ~484s: "Sixty-six percent."
- ~488s: "The single most-used language on the planet."
- 505.55s "JavaScript didn't" / 507.42s "quality,"
- 508.11s "won" / 509.31s "supply."
- 509.95s "The kid" / 512.67s "days" / 513.71s "writes" / 514.37s "world."

Beat plan:
1. (462-476s) LLM flywheel diagram: JS dominates training data, loops back as most-generated, most-shipped, next training corpus.
2. (476-493s) Stack Overflow bar chart — JS extends to 66%, year-over-year streak counter.
3. (493-510s) QUALITY vs SUPPLY split — the thesis as visual contrast.
4. (510-515s) Brendan Eich callback — 10 days, now writes the world.

### Scene 12 — Landing (515-530.617s)

Key word timestamps:
- 515.18s "The next time you open"
- 516.15s "code editor,"
- 517.29s "password manager,"
- 518.95s "Start" (menu of Windows)
- ~521s "remember you're running JavaScript"
- ~523s "Not because it won. Because it was already there."
- 525.63s "because" / 527.10s "there"

Beat plan:
1. (515-522s) App icons appear on the spoken words: code editor, password manager, Start button — each lit JS-yellow.
2. (522-530.617s) "Not because it won. Because it was already there." — JS logo centered, warm glow expanding. Fade to black. FINAL SCENE — exit animations are allowed here only.

---

## Code patterns (must be consistent throughout)

### Composition file structure
Every scene is a full HTML document. Sub-compositions are NOT wrapped in a
`<template>` element — that hides content. The `data-composition-id` is on a
`<div>` directly inside `<body>`. Register the GSAP timeline in the `<script>` at
the bottom of that div:

```
window.__timelines = window.__timelines || {};
const tl = gsap.timeline({ paused: true });
/* tweens */
window.__timelines["scene-NN-slug"] = tl;
```

### Movement crossfade pattern
```js
// Correct crossfade: mvA fades out, mvB fades in, same timestamp
tl.to("#mvA", { opacity: 0, duration: 0.5, ease: "power2.inOut" }, T_AB);
tl.fromTo("#mvB", { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "power2.inOut" }, T_AB);
// DO NOT follow tl.to({opacity:0}) with tl.set({visibility:"hidden"}) on the SAME element
// within ~0.1s — lint 0.6.39+ flags this as overlapping_gsap_tweens.
```

### Dynamic content creation (security hook is active)
A pre-commit hook blocks any pattern that looks like `el.prop = untrustedString`.
Build dynamic elements with `document.createElement` + `.textContent`:

```js
const el = document.createElement("span");
el.className = "tl-tick";
el.textContent = String(year);
parent.appendChild(el);
```

Never assign HTML markup strings to `.textContent` or any DOM property for
constructing child elements.

### Lint-known gotchas
1. `repeat: -1` is banned — use `repeat: Math.ceil(duration / cycle)`.
2. `data-layout-allow-overflow` must mark each overflowing container AND ancestors
   up the chain until inspect stops flagging. Does not bubble automatically.
3. `Math.random()` and `Date.now()` are banned (non-deterministic).
4. Do NOT build timelines inside async, setTimeout, or Promises.
5. `xPercent: -50` for GSAP-centered elements; CSS `transform: translateX(-50%)`
   conflicts with GSAP's transform tracking.

### Palette discipline
```
--accent: #f7df1e   ONLY for JavaScript logos/marks/the-word-JavaScript on emphasis beats
--danger: #ff6b5d   problem state, bad outcomes, crash/fail visuals
--ok:     #7dd87d   resolved state, success, good outcomes
--accent-2: #67e8f9 secondary callouts, vector points, timeline accents
```

### Sizing
- Headlines: 96-140px / weight 700-900
- Body narration: 56-72px / weight 500-600
- Labels/metadata: 24-32px / weight 400-500 / color `--muted`
- Data values: 28-36px / JetBrains Mono / `font-variant-numeric: tabular-nums`

### No exit animations rule
Exit tweens are FORBIDDEN except in scene-12 (final scene). Crossfades handle
scene exits. Within a scene, the movement-level crossfade handles element exits.
Do NOT add `tl.to({opacity:0, y:-40})` on individual elements before a crossfade.

---

## index.html mounting template

After a scene passes `npm run check`, mount it in `index.html`:

```html
<!-- Scene N — title. Starts Xs, duration Ys. -->
<div
  id="scene-NN"
  data-composition-id="scene-NN-slug"
  data-composition-src="compositions/scene-NN-slug.html"
  data-start="X"
  data-duration="Y"
  data-track-index="1"
  data-width="1920"
  data-height="1080"
  style="position: absolute; inset: 0; z-index: 1"
></div>
```

## Commit after each scene

```bash
git add compositions/scene-NN-*.html index.html
git commit -m "feat(js-king): scene N — title"
```

One scene = one commit. Do not batch.

---

## Current state at brief creation

- scene-01-hook.html: EXISTS, passes check. Movement B+C need visual enrichment.
- substrate.html: EXISTS, passes check.
- scenes 2-12: do not exist yet.

Build order: fix scene-01 Movement B+C first, then build scenes 2-12 in order.
