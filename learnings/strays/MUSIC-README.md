# Music bed — finish in ~2 minutes

The SFX pass and animation pass are **done and wired**. The music bed is the one
piece I could not complete autonomously: every quality music source is gated
behind **your** account —

- **Envato / AudioJungle** (`app.envato.com/music`) requires login. I'm not
  permitted to enter passwords or log into accounts on your behalf.
- **Pixabay Music** lets you browse, but downloading without a logged-in session
  stalls (Chrome holds the file pending an in-window confirmation).
- The local `sound-effects/` library is **SFX only** — no actual music. Faking a
  bed from rumble loops would risk an ominous hum under the lighter early acts, so
  I deliberately did not.

So I built the rest of the pipeline. Here's the whole finish:

## Steps

1. **Get tracks** (any one source):
   - Envato Elements → search e.g. *"documentary underscore"*, *"ambient tech"*,
     *"cinematic tension"* (your call — taste is yours).
   - Or **ElevenLabs Music** (you already have an ElevenLabs account — your VO uses
     it): generate one ~4-5 min instrumental, or two (a driving one + a darker one).
2. **Drop them in:**
   - `audio/layer_a/` — the main bed (driving / curious / momentum).
   - `audio/layer_b/` — *(optional)* a darker/tenser track for the back half.
     If you skip layer_b, the script loops layer_a top-to-tail.
3. **Bake:** from this folder run

   ```bash
   ./bake-music-bed.sh
   ```

   It loudness-normalizes each layer to ~−28 LUFS, fits them to the 530.6s
   voiceover, crossfades layer_a→layer_b at **385s** (the "terror reign" turn —
   override with `BOUNDARY=250 ./bake-music-bed.sh` to switch at the Node.js
   ovation instead), adds fades + a limiter, and writes `audio/music-bed.wav`.
   It also writes `compositions/music.html` for you.
4. **Mount it:** paste this just above the `sfx-layer` mount in `index.html`
   (the script prints it too):

   ```html
      <!-- music-layer: baked bed (audio/music-bed.wav) -->
      <div
        id="music-layer"
        data-composition-id="music-layer"
        data-composition-src="compositions/music.html"
        data-start="0"
        data-duration="530.617"
        data-track-index="10"
      ></div>
   ```
5. **Reload** the preview tab. `npx hyperframes lint` should stay clean.

## Tuning

- Volume lives in `compositions/music.html` → `data-volume` (starts at **0.13**).
  Sensible range **0.10 – 0.20**, step 0.02. If you can't hear VO consonants
  clearly, it's too loud.
- The energy arc to aim for (from `sound-design-playbook.md`): curious/light
  through the birth + naming acts, lift into the **Node.js ovation (~252s)**, go
  dark/tense through the **terror reign (~385-460s)**, and resolve warm on the
  **verdict + landing (~505-526s)**. Consider letting the bed **drop to near
  silence ~1s before "won on supply" (~507s)** and again before the final
  "because it was already there (~525s)" — the two earned silences.

The music sits at `track-index=10`, **below** SFX (19-29), exactly like the
prior `how-does-captchas-work` video.
