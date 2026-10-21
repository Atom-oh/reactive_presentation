#!/usr/bin/env bash
# Usage: to-mp4.sh <cast> <out.mp4>   asciinema cast -> agg gif -> h264 mp4 (1920 폭, 무음)
set -euo pipefail
in=$1; out=$2; tmp=$(mktemp -d "${TMPDIR:-$HOME/.tmp}/rec.XXXX")
sed -E 's/\b[0-9]{12}\b/************/g' "$in" > "$tmp/r.cast"
agg --theme asciinema --font-family "Noto Sans Mono CJK KR" --font-size 26 --idle-time-limit 2 "$tmp/r.cast" "$tmp/r.gif"
ffmpeg -y -loglevel error -i "$tmp/r.gif" -movflags +faststart -pix_fmt yuv420p -vf "scale=1920:-2:flags=lanczos" -c:v libx264 -crf 20 -an "$out"
ffprobe -v error -show_entries format=duration:stream=width,height -of csv=p=0 "$out"
rm -rf "$tmp"
