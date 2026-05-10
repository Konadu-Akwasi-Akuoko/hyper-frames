# v2-quirks — eight engine landmines

Multilingual v2's sharp edges, sourced from the official models page,
help center, and the project's own first-render observations. Apply
these mitigations during annotation and tool defaults; the SKILL.md
already wires the most important ones in.

## 1. Language switching mid-generation

v2 sometimes switches accent or even language on a single proper noun if
the model thinks it's in another language ("paella", "naïve", "café",
"jalapeño", "résumé"). The audio sounds like an English narrator briefly
became Spanish/French/etc. for one word.

**Mitigation:** Pass `language_code="en"` on every call. The v2 tool's
default does this. If a specific word still slips, respell phonetically
in `script.md` and add a `<!-- TTS: jalapeño → ha-la-pen-yo -->`
comment.

## 2. No phoneme tags

v2 doesn't accept `<phoneme>` SSML. Pronunciation control is via:

- Inline phonetic respelling per `script-writer/reference/tts-gotchas.md`
- Project-level pronunciation dictionary (alias rules) — not yet wired
  into our tools; see the "Future" note in `tts-gotchas.md`.

Don't reach for SSML phonemes — they silently fail.

When you respell, look up the IPA first (Wikipedia is reliable for
proper nouns; the article on "Luis von Ahn" gives `[ˈlwis fon ˈan]`).
Don't guess from English orthography — `AHN`/`AWN`/`OHN` look
interchangeable but map to three different English vowels (`/an/`,
`/ɔn/`, `/oʊn/`). Match the IPA, then test on a 30-second slice
before committing to a full regen.

## 3. SSML break tag bounds

v2 supports `<break time="Xs"/>` up to ~3 seconds. Longer pauses fail
silently or get clamped. For longer pauses, split into multiple breaks
(`<break time="2s"/><break time="2s"/>`) or rewrite the sentence so the
pause isn't needed.

Allowed values: 0.3s, 0.5s, 0.8s, 1.5s, 2s, 3s. The skill's hard cap
forbids anything above 3s.

## 4. Style slider trap

`style` above ~0.6 produces erratic emphasis on long-form (random words
get over-stressed, prosody becomes sing-songy). The docs recommend
0.3–0.5 for natural expression; cap at 0.5 by convention.

The tool default is `0.35` — safe. Don't push it higher without first
testing on a 30-second slice.

## 5. Stability paradox

`stability` above ~0.7 produces *more* monotone delivery, not "more
stable." The slider's name is misleading: it controls how rigidly the
voice adheres to a neutral baseline, and the baseline is flat. 0.4 is
the long-form sweet spot per docs.

The tool default is `0.4` — leave it.

## 6. `use_speaker_boost` × similarity stacking

Both push toward the cloned voice. Stacking high values (similarity ≥
0.85 + speaker_boost on) amplifies any flaws in the source recording —
breath noises, room tone, microphone artifacts.

The tool defaults to `similarity_boost=0.75 + use_speaker_boost=True`.
Don't push similarity higher; if the voice doesn't sound like the
source, the source recording probably has issues that need fixing.

## 7. Concurrency limits per plan

From the official models page:

| Plan | Multilingual v2 concurrent |
|---|---|
| Free | 2 |
| Starter | 3 |
| Creator | 5 |
| Pro | 10 |
| Scale / Business | 15 |
| Enterprise | Elevated |

Single-shot + single-user means we never hit this — the tool fires one
request per render. Documented for completeness.

## 8. PVC vs IVC

Professional Voice Clones are **fully supported** on v2 (unlike v3
alpha, where PVC support is partial). If the user upgrades from an
Instant Voice Clone to a Professional Voice Clone, no skill or tool
change is needed — only the `--voice-id` flag value changes.

## 9. Initialism trap on short ALL-CAPS proper nouns

Short ALL-CAPS tokens (≤3 letters, or ≥3 consonants in a row, or any
shape that looks like an acronym to a human reader) get read
letter-by-letter. `AHN` becomes "A-H-N", `OHM` becomes "O-H-M",
`LBJ` becomes "L-B-J" (which is what you want for that one — but
not for proper nouns).

**Mitigation:** When an anchor term is a short proper noun, drop it
out of full ALL-CAPS but keep the surrounding emphasis. `LUIS VON Ahn`
works — the first/middle words carry the emphasis, the surname
renders naturally. Don't full-lowercase the whole phrase; you lose
the anchor signal entirely.

**Heuristic at annotation time:** before writing `WORD` into
`voiceover.txt`, ask "would a human reader read this as an
initialism?" If yes, demote that single word to title case and keep
the rest of the phrase ALL-CAPS.
