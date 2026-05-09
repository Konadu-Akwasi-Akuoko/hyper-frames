# voice-settings — the recommended recipe

The project default voice settings tuple for v2:

```
stability=0.4
similarity_boost=0.75
style=0.35
use_speaker_boost=True
language_code="en"
```

These are wired into `tools/voiceover-elevenlabs-v2/` as flag defaults
and used uniformly across every render. The docs explicitly forbid
varying them per beat for related content; treat them as fixed.

## Per-knob rationale

### stability=0.4

The docs say 0.35–0.4 is the long-form sweet spot. Above ~0.7,
delivery becomes paradoxically monotone (the slider's name is
misleading; see `v2-quirks.md` §5). Below 0.3, prosody becomes erratic
and pronunciation gets unstable.

### similarity_boost=0.75

ElevenLabs' own default. Pushing higher amplifies source-recording
flaws when stacked with `use_speaker_boost=True`. Lower values let v2
drift away from the cloned voice over a long render.

### style=0.35

The docs recommend 0.3–0.5 for natural expression. v3's audio tags
play this role inline; v2 has only this single slider. Above ~0.6,
emphasis becomes erratic on long-form (sing-songy random stresses).

### use_speaker_boost=True

ElevenLabs' own default. Adds a small CPU cost per request but
materially helps the voice stay recognizable across a long render.

### language_code="en"

Mitigates v2's tendency to switch accent on individual proper nouns it
thinks belong to another language (`v2-quirks.md` §1). Without this,
the same script may pronounce "paella" with a Spanish accent, then
revert to English for the next sentence.

## When to tune

Default to never. The docs forbid per-beat variance. If a render comes
back consistently flat or consistently overwrought across an entire
script (not just one passage), consider tuning, but:

1. **Test on a 30-second slice first.** Re-rendering a full 5-min script
   to test a tuning change burns ~150 credits per attempt. A
   30-second slice burns ~15.
2. **A/B against the default.** Render the same slice with the default
   settings and the candidate settings. Compare side-by-side.
3. **Change one knob at a time.** If you change `stability` and `style`
   in the same test, you can't tell which knob did what.
4. **Never tune per-beat.** Even if it sounds tempting. The docs say
   "identical parameter settings… across related content." Render seams
   become audible if you don't.

## When the recipe stops working

If a render sounds wrong despite default settings, the issue is almost
never the voice settings. In order of likelihood:

1. **Source script issue** — re-read the affected passage aloud. Does
   it have a TTS-hostile construction (long parenthetical, weird
   number, homograph)? Fix the prose; see `script-writer/reference/tts-gotchas.md`.
2. **Voice issue** — is the voice clone good for long-form? Some IVCs
   sound great for 10 seconds and degrade over a minute. Try a
   different voice on the same script.
3. **Language drift** — did v2 accent-switch on a specific word?
   Mitigation in `v2-quirks.md` §1.
4. **Then** consider voice settings.
