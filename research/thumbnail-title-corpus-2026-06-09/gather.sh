#!/usr/bin/env bash
# Gather top-by-views thumbnails + titles for the thumbnail-and-title-generator
# corpus study. Cookie-authenticated yt-dlp (low bot-wall risk), resumable per
# channel. Long-form: flat-list recent candidates -> throttled full-extract view
# counts -> keep top N. Shorts: flat-list (view_count is free on the shorts tab)
# -> keep top N. Thumbnails pulled from the CDN (maxres -> hq fallback).
#
# Usage:
#   bash gather.sh                 # full run (defaults below)
#   CAND_VIDEOS=5 KEEP_VIDEOS=3 CAND_SHORTS=5 KEEP_SHORTS=3 ONLY=Shadeofcode bash gather.sh   # smoke test
set -uo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
COOKIES=(--cookies-from-browser chrome)
SLEEP="${SLEEP:-1}"
CAND_VIDEOS="${CAND_VIDEOS:-40}"   # how many recent long-form to consider
KEEP_VIDEOS="${KEEP_VIDEOS:-25}"   # how many to keep (top by views)
CAND_SHORTS="${CAND_SHORTS:-60}"   # how many recent shorts to consider
KEEP_SHORTS="${KEEP_SHORTS:-15}"   # how many to keep (top by views)
ONLY="${ONLY:-}"                   # restrict to one channel slug (for smoke tests)

# slug<TAB>handle
CHANNELS=(
  "shadeofcode	@Shadeofcode"
  "devforgehq	@devforgehq"
  "fireship	@Fireship"
  "thecodingkoalaa	@thecodingkoalaa"
  "technetiumm	@technetiumm"
  "thecodingsloth	@TheCodingSloth"
  "awesome-coding	@awesome-coding"
  "codehead01	@codehead01"
  "swagprofessorexplain	@SwagProfessorExplain"
  "latticx	@Latticx"
  "cleoabram	@CleoAbram"
)

STATUS="$ROOT/STATUS.md"
log() { echo "[$(date '+%H:%M:%S')] $*"; echo "- [$(date '+%H:%M:%S')] $*" >> "$STATUS"; }

dl_thumb() {  # id outpath
  local id="$1" out="$2"
  if curl -sfL "https://i.ytimg.com/vi/$id/maxresdefault.jpg" -o "$out" 2>/dev/null && [ -s "$out" ]; then
    local sz; sz=$(stat -f%z "$out" 2>/dev/null || echo 0)
    [ "$sz" -lt 3000 ] && curl -sfL "https://i.ytimg.com/vi/$id/hqdefault.jpg" -o "$out" 2>/dev/null
  else
    curl -sfL "https://i.ytimg.com/vi/$id/hqdefault.jpg" -o "$out" 2>/dev/null
  fi
  [ -s "$out" ] && return 0 || return 1
}

[ -f "$STATUS" ] || echo "# Gather status — thumbnail-title corpus 2026-06-09" > "$STATUS"
log "RUN start (cand_v=$CAND_VIDEOS keep_v=$KEEP_VIDEOS cand_s=$CAND_SHORTS keep_s=$KEEP_SHORTS only='${ONLY:-all}')"

for entry in "${CHANNELS[@]}"; do
  slug="${entry%%	*}"; handle="${entry##*	}"
  [ -n "$ONLY" ] && [ "$slug" != "$ONLY" ] && continue
  cdir="$ROOT/$slug"; tdir="$cdir/thumbs"; mani="$cdir/titles.jsonl"
  if [ -f "$mani" ] && [ "$(wc -l < "$mani" | tr -d ' ')" -gt 0 ]; then
    log "SKIP $slug (manifest exists, $(wc -l < "$mani" | tr -d ' ') items)"; continue
  fi
  mkdir -p "$tdir"; : > "$mani"
  log "CHANNEL $slug ($handle) — long-form"

  # ---- long-form (stream IDs; bash-3.2-safe, no mapfile) ----
  vtmp="$(mktemp)"; empties=0; ncand=0
  while IFS= read -r id; do
    [ -z "$id" ] && continue
    ncand=$((ncand+1))
    line=$(yt-dlp "${COOKIES[@]}" --no-download --sleep-requests "$SLEEP" --socket-timeout 30 \
      --print "%(view_count)s	%(duration)s	%(title)s" "https://www.youtube.com/watch?v=$id" </dev/null 2>/dev/null)
    if [ -z "$line" ]; then empties=$((empties+1)); [ "$empties" -ge 5 ] && { log "  $slug: WALL? 5 consecutive empties — stopping long-form early"; break; }; continue; fi
    empties=0
    views=$(echo "$line" | cut -f1); [ "$views" = "NA" ] && views=0
    printf "%s\t%s\t%s\n" "$id" "$views" "$line" >> "$vtmp"
  done < <(yt-dlp "${COOKIES[@]}" --flat-playlist --playlist-end "$CAND_VIDEOS" \
    --print "%(id)s" "https://www.youtube.com/$handle/videos" </dev/null 2>/dev/null)
  log "  $slug: $ncand long-form candidates extracted"
  # rank by views (col 2), keep top N
  rank=0
  while IFS=$'\t' read -r id views _v dur title; do
    rank=$((rank+1)); [ "$rank" -gt "$KEEP_VIDEOS" ] && break
    fn=$(printf "L%02d_%s_%s.jpg" "$rank" "$views" "$id")
    if dl_thumb "$id" "$tdir/$fn"; then thumb="thumbs/$fn"; else thumb=""; fi
    jq -nc --argjson rank "$rank" --arg kind "long" --arg id "$id" \
      --argjson views "${views:-0}" --arg dur "$dur" --arg title "$title" --arg thumb "$thumb" \
      '{rank:$rank,kind:$kind,id:$id,views:$views,duration:$dur,title:$title,thumb:$thumb}' >> "$mani"
  done < <(sort -t$'\t' -k2 -rn "$vtmp")
  log "  $slug: kept top $(grep -c '"kind":"long"' "$mani") long-form"
  rm -f "$vtmp"

  # ---- shorts (view_count is free on the flat shorts tab) ----
  log "CHANNEL $slug ($handle) — shorts"
  stmp="$(mktemp)"
  yt-dlp "${COOKIES[@]}" --flat-playlist --playlist-end "$CAND_SHORTS" \
    --print "%(id)s	%(view_count)s	%(title)s" "https://www.youtube.com/$handle/shorts" 2>/dev/null \
    | awk -F'\t' '{v=$2; if(v=="NA")v=0; print $1"\t"v"\t"$3}' > "$stmp"
  srank=0
  while IFS=$'\t' read -r id views title; do
    [ -z "$id" ] && continue
    srank=$((srank+1)); [ "$srank" -gt "$KEEP_SHORTS" ] && break
    fn=$(printf "S%02d_%s_%s.jpg" "$srank" "$views" "$id")
    if dl_thumb "$id" "$tdir/$fn"; then thumb="thumbs/$fn"; else thumb=""; fi
    jq -nc --argjson rank "$srank" --arg kind "short" --arg id "$id" \
      --argjson views "${views:-0}" --arg dur "" --arg title "$title" --arg thumb "$thumb" \
      '{rank:$rank,kind:$kind,id:$id,views:$views,duration:$dur,title:$title,thumb:$thumb}' >> "$mani"
  done < <(sort -t$'\t' -k2 -rn "$stmp")
  log "  $slug: kept top $(grep -c '"kind":"short"' "$mani") shorts"
  rm -f "$stmp"
  log "DONE $slug — total $(wc -l < "$mani" | tr -d ' ') items, $(ls "$tdir" | wc -l | tr -d ' ') thumbs"
done
log "RUN complete"
