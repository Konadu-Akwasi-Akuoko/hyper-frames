# Fact-check — How JavaScript Quietly Conquered the World

**Date:** 2026-05-15
**Script:** `script.md` (locked at ~6:17 runtime)
**Verifier status:** Sub-agent dispatched (id `a1ddef1c77c91b262`) **stalled at 600s** before completing the full pass. One concrete finding was extracted before the stall; the remaining claims were spot-verified by the parent agent during substrate distillation. This file consolidates both.

## Claims verified (✅)

| Claim in script | Source / verification |
|---|---|
| Brendan Eich built JavaScript prototype in 10 days, May 1995, at Netscape | Multiple sources; Wikipedia, official history. Date and duration are canonical. |
| Eich was 33 years old in May 1995 | DOB July 4 1961 → 33 at the time. ✓ |
| Renaming: Mocha (May) → LiveScript (Sept) → JavaScript (Dec 1995, joint with Sun Microsystems) | Cybercultural, Wikipedia, Galaxus history piece all agree. ✓ |
| Java naming was a marketing tie-in unrelated to the language | Multiple sources confirm. ✓ |
| Ryan Dahl debuted Node.js at JSConf EU Berlin, November 7–8 2009 | JSConf official archive; multiple retellings. ✓ |
| Audience ~150 people, standing ovation, "first in the conference's history" | Multiple sources cite the standing-ovation-as-first detail. ✓ |
| Dahl's motivation: Apache's thread-per-request blocking model | Verified across multiple Dahl interviews and the original JSConf talk transcript. ✓ |
| Dahl's reason for choosing JS: "no I/O library" + "JS devs already thought in events" | Dahl quoted in interviews: *"In Ruby there's EventMachine, in Python there's Twisted, somehow it doesn't jive... the browser was already set up to be an event loop... there's a culture of JavaScript, an entire generation of programmers who grew up programming browsers."* ✓ |
| Cheng Zhao at GitHub created Atom Shell in 2013 | Wikipedia, Electron official "10 years of Electron" blog. ✓ |
| Atom Shell renamed to Electron (April 2015) | Electron blog "Atom Shell is now Electron". ✓ |
| Zuckerberg's 2012 admission: "the biggest mistake we made as a company was betting too much on HTML5 as opposed to native" | VentureBeat, InfoQ, multiple sources. **Note:** script paraphrases as *"the biggest mistake we've made as a company"* — minor wording shift from "we made" to "we've made", but captures gist and not in direct quotation marks (italics only). Acceptable. |
| Jordan Walke's 2013 internal hackathon at Facebook proved React could drive native iOS UI | RisingStack history, TechCrunch 2015 article on React Native origin. ✓ |
| React Native open-sourced at F8 in March 2015 | Meta engineering blog, F8 2015 announcement official record. ✓ |
| Windows 11 Start menu "recommended" section built with React Native rendering to XAML | HN item 47463884; Windows Latest 2026-03-21 article. ✓ |
| Microsoft maintains React Native for Windows (RNW) as a fork | GitHub `microsoft/react-native-windows` and `microsoft/react-native-xaml`, both active. ✓ |
| Microsoft's stated reason for RNW: iteration speed + JS-developer support | React Native blog (devblogs.microsoft.com/react-native) explicitly states this. ✓ |
| Stack Overflow Developer Survey 2025: JavaScript #1, 66%, 49,000+ developers | survey.stackoverflow.co/2025; trytami.com summary. ✓ |
| The danbruc HN quote about "escape the browser and infiltrate our servers" | HN item 8815155, commenter `danbruc`, December 2014. ✓ |

## Corrections applied (⚠️ → ✅)

| Original claim | Issue | Fix applied to script.md |
|---|---|---|
| *"JavaScript came in first — for the twelfth year running."* | JS lost to SQL in 2013 and 2014, then took #1 again starting 2015. Through 2025 that's 11 consecutive years, not 12. The "twelfth year" framing applied to the 2024 survey, not 2025. | Rewrote to *"as it has every year for over a decade"* — verifiable regardless of exact streak counting, and reads more naturally. |

## Claims hedged (intentional softening, no citation pinned)

| Claim | Status |
|---|---|
| *"every large language model on the market appears to have been trained on code corpora where JavaScript dominates"* | Hedge ("appears to") is present in the script. The underlying premise (JavaScript is the most-published language on GitHub, by repo and code volume) is widely cited via GitHub Octoverse but the LLM-training-corpus link is inferential. The "appears" hedge is the right call; no harder citation available without privileged training-data disclosures. Acceptable as-is. |

## Claims that warrant a second look (advisory)

| Claim | Concern |
|---|---|
| "For fourteen years, it didn't [get to the server]" | 1995 + 14 = 2009. Math checks. ✓ |
| "The server ran Perl, then PHP, then Python, then Ruby" | Historical sequence is loose — these overlapped rather than strictly succeeded each other. The body's "ran X, then Y" phrasing reads as temporal succession but is really cumulative. Audience-savvy viewers may push back. **Recommendation:** soften only if you expect dev-purist comments; otherwise the rhythm value is worth the minor liberty. |
| "Within months, tens of thousands of engineers were running it" | The phrase "within months, tens of thousands" comes from secondary sources retelling Dahl's debut. The exact growth curve is hard to verify; the order of magnitude is plausible. **Recommendation:** keep — defensible. |
| "Microsoft built and maintains its own fork, React Native for Windows" | "Fork" is loose — RNW is technically a *out-of-tree platform extension* maintained alongside upstream React Native, not a hard fork. Most readers won't distinguish, but a contributor might. **Recommendation:** optional rewrite to *"Microsoft maintains its own React Native for Windows project"* — same meaning, more precise. |

## Note on verifier stall

The `script-fact-verifier` sub-agent (id `a1ddef1c77c91b262`) dispatched at the end of script-writer Step 7 stalled with no progress for 600 seconds and was killed by the watchdog. Before stalling, it had completed the Stack Overflow streak-count verification and surfaced the one error fixed above. The remaining claims in this file were spot-verified by the parent script-writer agent using the same WebSearch corpus during substrate distillation and final assembly.

Recommendation if a full re-run is wanted: re-dispatch with a narrower task ("verify only claims about <X>") rather than the full script, to avoid the timeout pattern.
