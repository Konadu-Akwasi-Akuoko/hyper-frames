#!/usr/bin/env bash
# Bake audio/music-bed.wav from curated tracks in audio/layer_a/ (+ optional audio/layer_b/).
#
# USAGE (from this video folder):
#   1. Drop one or more instrumental tracks into  audio/layer_a/   (the main bed)
#   2. (optional) Drop darker/tenser tracks into  audio/layer_b/   (used for the back half)
#   3. ./bake-music-bed.sh
#
# Result: audio/music-bed.wav at ~-28 LUFS, fitted to the voiceover length, with a
# 2s crossfade at the layer boundary. Then add the mount in index.html (see MUSIC-README.md)
# and tune data-volume in compositions/music.html.
set -euo pipefail
cd "$(dirname "$0")"

VO="audio/voiceover.mp3"
OUT="audio/music-bed.wav"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Layer boundary: where layer_a hands off to layer_b. Default = terror-reign turn (~385s).
BOUNDARY="${BOUNDARY:-385}"
XF=2          # crossfade seconds
FADE_IN=1.5
FADE_OUT=4

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VO")
DUR=${DUR%.*}
echo "voiceover duration: ${DUR}s   boundary: ${BOUNDARY}s"

# Collect files (sorted) from a layer dir into a newline list.
layer_files() { find "audio/$1" -type f \( -iname '*.wav' -o -iname '*.mp3' -o -iname '*.flac' -o -iname '*.m4a' \) | sort; }

# Build one continuous, length-fitted, loudness-normalized layer.
#   $1 = layer dir name   $2 = target seconds   $3 = output path
build_layer() {
  local dir="$1" target="$2" out="$3"
  mapfile -t files < <(layer_files "$dir")
  [ "${#files[@]}" -eq 0 ] && return 1
  # concat (re-encode to a common format first so concat is safe across mp3/wav)
  local parts=() i=0
  for f in "${files[@]}"; do
    ffmpeg -nostdin -v error -y -i "$f" -ar 48000 -ac 2 -c:a pcm_s16le "$TMP/${dir}_$i.wav"
    parts+=("$TMP/${dir}_$i.wav"); i=$((i+1))
  done
  printf "file '%s'\n" "${parts[@]}" > "$TMP/${dir}.txt"
  ffmpeg -nostdin -v error -y -f concat -safe 0 -i "$TMP/${dir}.txt" -c copy "$TMP/${dir}_cat.wav"
  # loop the concatenated set enough to exceed target, then trim + loudnorm
  ffmpeg -nostdin -v error -y -stream_loop 50 -i "$TMP/${dir}_cat.wav" \
    -t "$target" -af "loudnorm=I=-28:LRA=11:TP=-2" -ar 48000 -ac 2 -c:a pcm_s16le "$out"
  echo "built $dir -> $out (${target}s)"
}

HAVE_A=0; HAVE_B=0
[ -n "$(layer_files layer_a)" ] && HAVE_A=1
[ -n "$(layer_files layer_b)" ] && HAVE_B=1

if [ "$HAVE_A" -eq 0 ]; then
  echo "ERROR: drop at least one track into audio/layer_a/ first." >&2; exit 1
fi

if [ "$HAVE_B" -eq 1 ]; then
  build_layer layer_a "$((BOUNDARY + XF))" "$TMP/A.wav"
  build_layer layer_b "$((DUR - BOUNDARY + XF))" "$TMP/B.wav"
  ffmpeg -nostdin -v error -y -i "$TMP/A.wav" -i "$TMP/B.wav" \
    -filter_complex "[0][1]acrossfade=d=${XF}:c1=qsin:c2=qsin,\
afade=t=in:st=0:d=${FADE_IN},afade=t=out:st=$((DUR - ${FADE_OUT%.*})):d=${FADE_OUT},\
alimiter=limit=0.85" -ar 48000 -ac 2 -c:a pcm_s16le "$OUT"
else
  build_layer layer_a "$DUR" "$TMP/A.wav"
  ffmpeg -nostdin -v error -y -i "$TMP/A.wav" \
    -af "afade=t=in:st=0:d=${FADE_IN},afade=t=out:st=$((DUR - ${FADE_OUT%.*})):d=${FADE_OUT},alimiter=limit=0.85" \
    -ar 48000 -ac 2 -c:a pcm_s16le "$OUT"
fi

echo "---"
echo "wrote $OUT"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT" | xargs printf "bed duration: %ss\n"
echo "loudness check:"; ffmpeg -nostdin -v error -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | tail -6 || true

# Emit compositions/music.html (mirrors compositions/sfx.html shape).
cat > compositions/music.html <<'HTML'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  </head>
  <body>
    <template id="music-layer-template">
      <div data-composition-id="music-layer" data-width="1920" data-height="1080">
        <audio
          id="music-bed"
          class="clip"
          data-start="0"
          data-duration="530.617"
          data-volume="0.13"
          data-track-index="10"
          src="../audio/music-bed.wav"
        ></audio>
        <script>
          (() => {
            window.__timelines = window.__timelines || {};
            window.__timelines["music-layer"] = gsap.timeline({ paused: true });
          })();
        </script>
      </div>
    </template>
  </body>
</html>
HTML
echo "wrote compositions/music.html (volume 0.13 — tune 0.10..0.20)"
echo ""
echo "FINAL STEP — paste this block into index.html, just above the sfx-layer mount:"
cat <<'SNIP'
      <!-- music-layer: baked bed (audio/music-bed.wav) -->
      <div
        id="music-layer"
        data-composition-id="music-layer"
        data-composition-src="compositions/music.html"
        data-start="0"
        data-duration="530.617"
        data-track-index="10"
      ></div>
SNIP
echo "Then reload the preview tab. Run 'npx hyperframes lint' to confirm clean."
