#!/usr/bin/env bash
# Build one labeled contact sheet per channel: each thumbnail scaled + captioned
# with "rank · views", tiled 5 per row. montage aborts on this Mac (missing font),
# so we tile with +append (rows) then -append (stack).
set -uo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
COLS=5
CW=300; CH=169

for d in "$ROOT"/*/; do
  d="${d%/}"; slug="$(basename "$d")"
  tdir="$d/thumbs"; [ -d "$tdir" ] || continue
  tmp="$(mktemp -d)"
  # ordered file list: long-form (L*) by rank, then shorts (S*) by rank
  cells=()
  for f in $(ls "$tdir"/L*.jpg 2>/dev/null | sort) $(ls "$tdir"/S*.jpg 2>/dev/null | sort); do
    base="$(basename "$f" .jpg)"            # e.g. L01_14390_BErlQ_HBsZg
    rank="${base%%_*}"                       # L01
    rest="${base#*_}"; views="${rest%%_*}"   # 14390
    label="$rank · ${views} views"
    cell="$tmp/$(printf '%03d' "${#cells[@]}").png"
    magick "$f" -resize ${CW}x${CH}^ -gravity center -extent ${CW}x${CH} \
      -gravity South -background '#000000cc' -splice 0x20 \
      -gravity South -pointsize 15 -fill '#FFFFFF' -annotate +0+2 "$label" "$cell" 2>/dev/null \
      || magick "$f" -resize ${CW}x${CH} "$cell"
    cells+=("$cell")
  done
  n=${#cells[@]}; [ "$n" -eq 0 ] && { echo "$slug: no thumbs"; rm -rf "$tmp"; continue; }
  # rows of COLS
  rowfiles=(); i=0; r=0
  while [ "$i" -lt "$n" ]; do
    row=(); j=0
    while [ "$j" -lt "$COLS" ] && [ "$i" -lt "$n" ]; do row+=("${cells[$i]}"); i=$((i+1)); j=$((j+1)); done
    rf="$tmp/row_$(printf '%02d' $r).png"
    magick "${row[@]}" +append -background black "$rf" 2>/dev/null
    rowfiles+=("$rf"); r=$((r+1))
  done
  magick "${rowfiles[@]}" -append -background black "$d/_contact.png" 2>/dev/null
  echo "$slug: $n cells -> _contact.png ($(magick identify -format '%wx%h' "$d/_contact.png" 2>/dev/null))"
  rm -rf "$tmp"
done
