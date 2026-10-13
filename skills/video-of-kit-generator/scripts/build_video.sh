#!/usr/bin/env bash
# Build the 30-second kit video from a recipe folder (media/kits/{SLUG}).
#
#   frames  (headless Chromium, temp dir)  ->  silent.mp4
#   soundtrack.wav (numpy synth, temp dir) ->  mux  ->  ~/Movies/{name}.mp4
#
# The recipe folder is only READ. Videos are written to ~/Movies (or $VIDEO_OUT_DIR),
# and the script refuses to write inside any git repository.
#
# usage: build_video.sh RECIPE_DIR [--preview] [--keep] [--work-dir DIR]
#   --preview    half-size, 10 fps, fast encode: checks the pipeline in about a minute
#   --keep       keep the temp frames/audio (printed at the end)
#   --work-dir   use DIR for intermediates (kept after the run)
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RECIPE=""
PREVIEW=0
KEEP=0
WORK=""
OWN_WORK=1

while [ $# -gt 0 ]; do
  case "$1" in
    --preview) PREVIEW=1 ;;
    --keep) KEEP=1 ;;
    --work-dir) WORK="$2"; OWN_WORK=0; shift ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    *) RECIPE="$1" ;;
  esac
  shift
done
[ -n "$RECIPE" ] || { echo "usage: build_video.sh RECIPE_DIR [--preview] [--keep] [--work-dir DIR]"; exit 2; }
RECIPE="$(cd "$RECIPE" && pwd)"
CFG="$RECIPE/video.json"
[ -f "$CFG" ] || { echo "missing $CFG"; exit 2; }

cfg() {  # cfg KEY.PATH DEFAULT
  python3 -I - "$CFG" "$1" "${2:-}" <<'PY'
import json, sys
v = json.load(open(sys.argv[1]))
for k in sys.argv[2].split("."):
    v = v.get(k) if isinstance(v, dict) else None
print(sys.argv[3] if v is None else v)
PY
}

# ---------- preflight ----------
for tool in ffmpeg ffprobe; do
  command -v "$tool" >/dev/null || { echo "missing $tool (brew install ffmpeg)"; exit 1; }
done
python3 -I -c "import playwright, numpy" 2>/dev/null || {
  echo "python3 needs playwright and numpy:  pip install playwright numpy && playwright install chromium"
  exit 1
}

SLUG="$(cfg slug)"
ANIM="$(cfg animation animation.html)"
DUR="$(cfg duration 30)"
FPS="$(cfg fps 30)"
SCALE="$(cfg scale 1.5)"
W="$(cfg width 1280)"
H="$(cfg height 720)"
NAME="$(cfg output.name "${SLUG}-30s")"
[ -f "$RECIPE/$ANIM" ] || { echo "missing animation page: $RECIPE/$ANIM"; exit 2; }

OUT_DIR="${VIDEO_OUT_DIR:-$HOME/Movies}"
mkdir -p "$OUT_DIR"
OUT_DIR="$(cd "$OUT_DIR" && pwd)"
if git -C "$OUT_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "REFUSING: $OUT_DIR is inside a git repository. Videos belong in ~/Movies."
  exit 1
fi

if [ -z "$WORK" ]; then
  WORK="$(mktemp -d "${TMPDIR:-/tmp}/kit-video.XXXXXX")"
fi
mkdir -p "$WORK"
REPO="$(git -C "$RECIPE" rev-parse --show-toplevel 2>/dev/null || true)"
if [ -n "$REPO" ]; then
  case "$WORK/" in
    "$REPO"/*) echo "REFUSING: work dir $WORK is inside the repo $REPO"; exit 1 ;;
  esac
fi

X264=(-preset slow -crf 16)
if [ "$PREVIEW" = 1 ]; then
  SCALE=0.5; FPS=10; NAME="${NAME}-preview"; X264=(-preset veryfast -crf 26)
fi

echo "== $SLUG: ${DUR}s @ ${FPS}fps, ${W}x${H} x${SCALE} -> $OUT_DIR/$NAME.mp4"
echo "== work dir: $WORK"

# ---------- 1. frames ----------
python3 -I "$HERE/render_frames.py" "$RECIPE/$ANIM" --out "$WORK/frames" \
  --fps "$FPS" --secs "$DUR" --scale "$SCALE" --width "$W" --height "$H"

# ---------- 2. silent video ----------
ffmpeg -y -loglevel error -framerate "$FPS" -i "$WORK/frames/f_%04d.png" \
  -c:v libx264 "${X264[@]}" -pix_fmt yuv420p -movflags +faststart "$WORK/silent.mp4"

# ---------- 3. soundtrack ----------
python3 -I "$HERE/make_soundtrack.py" "$CFG" "$WORK/soundtrack.wav"

# ---------- 4. mux and deliver ----------
ffmpeg -y -loglevel error -i "$WORK/silent.mp4" -i "$WORK/soundtrack.wav" \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "$WORK/final.mp4"
cp "$WORK/final.mp4" "$OUT_DIR/$NAME.mp4"
cp "$WORK/silent.mp4" "$OUT_DIR/$NAME-silent.mp4"

# ---------- 5. verify ----------
GOT="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT_DIR/$NAME.mp4")"
SUMMARY="$(ffmpeg -hide_banner -nostats -i "$OUT_DIR/$NAME.mp4" -vn \
  -af "ebur128=peak=true:framelog=quiet" -f null - 2>&1 | sed -n '/Summary/,$p')"
LUFS="$(echo "$SUMMARY" | awk '/I:/ {print $2; exit}')"
PEAK="$(echo "$SUMMARY" | awk '/Peak:/ {print $2; exit}')"
SIZE="$(du -h "$OUT_DIR/$NAME.mp4" | cut -f1)"

echo
echo "video   : $OUT_DIR/$NAME.mp4  ($SIZE)"
echo "silent  : $OUT_DIR/$NAME-silent.mp4"
echo "duration: $GOT s (expected $DUR)"
echo "loudness: $LUFS LUFS, true peak $PEAK dBFS"
python3 -I - "$GOT" "$DUR" "$LUFS" "$PEAK" <<'PY'
import sys
got, dur, lufs, peak = map(float, sys.argv[1:5])
warn = []
if abs(got - dur) > 0.1: warn.append(f"duration {got:.2f}s is not {dur:.0f}s")
if lufs > -11: warn.append("soundtrack is hot (> -11 LUFS): lower music.peak")
if lufs < -20: warn.append("soundtrack is quiet (< -20 LUFS): raise music.peak or limiter_drive")
if peak > -0.1: warn.append("true peak above -0.1 dBFS: lower music.peak")
print("quality : " + ("OK" if not warn else "; ".join(warn)))
PY

# ---------- 6. repo hygiene ----------
"$HERE/check_no_media_in_repo.sh" "$RECIPE" || echo "WARNING: rendered media is inside the repo (see above)"

if [ "$KEEP" = 1 ] || [ "$OWN_WORK" = 0 ]; then
  echo "kept    : $WORK"
else
  rm -rf "$WORK"
fi
