#!/usr/bin/env bash
# Tile the t_*.png test frames from render_frames.py --times into one contact sheet.
# Works for either orientation: portrait tiles are narrow (360 px), landscape tiles 640 px.
#
# usage: contact_sheet.sh FRAMES_DIR OUT.png [COLUMNS=4] [--safe]
#
#   --safe   portrait only: draw the Shorts safe box (x 40-640, y 165-1025 on the 720x1280
#            stage) in yellow on every tile. Captions, callouts, the controls and the screen
#            should sit inside it; the Shorts UI covers the bottom ~20 % and right ~12 %.
#
# Write OUT.png to the same temp/scratchpad directory as the frames, never into the repo.
set -euo pipefail

DIR=""; OUT=""; COLS=4; SAFE=0
POS=()
for a in "$@"; do
  case "$a" in
    --safe) SAFE=1 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) POS+=("$a") ;;
  esac
done
DIR="${POS[0]:-}"; OUT="${POS[1]:-}"; COLS="${POS[2]:-4}"
[ -n "$DIR" ] && [ -n "$OUT" ] || { sed -n '2,12p' "$0"; exit 2; }
command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null || { echo "missing ffmpeg/ffprobe (brew install ffmpeg)"; exit 1; }

shopt -s nullglob
FILES=("$DIR"/t_*.png)
N=${#FILES[@]}
[ "$N" -gt 0 ] || { echo "no t_*.png frames in $DIR (render with --times first)"; exit 1; }

IFS=, read -r W H < <(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "${FILES[0]}")
if [ "$H" -gt "$W" ]; then TILE_W=360; else TILE_W=640; fi
[ "$N" -lt "$COLS" ] && COLS="$N"
ROWS=$(( (N + COLS - 1) / COLS ))

VF="scale=${TILE_W}:-1"
if [ "$SAFE" = 1 ]; then
  if [ "$H" -gt "$W" ]; then
    # the box is defined on the 720x1280 stage; express it as fractions of the tile
    VF="$VF,drawbox=x=iw*40/720:y=ih*165/1280:w=iw*600/720:h=ih*860/1280:color=yellow@0.9:t=2"
  else
    echo "note: --safe applies to portrait frames only; ignored" >&2
  fi
fi
VF="$VF,tile=${COLS}x${ROWS}:padding=8:color=0x333a46"

ffmpeg -y -loglevel error -pattern_type glob -i "$DIR/t_*.png" -vf "$VF" -frames:v 1 "$OUT"
echo "$OUT  (${N} frames, ${COLS}x${ROWS}, ${W}x${H} source)"
