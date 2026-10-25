#!/usr/bin/env bash
# Build the 30-second kit video, in two formats, from a recipe folder (media/kits/{SLUG}).
#
#   soundtrack.wav (numpy synth, temp dir) -- made once, shared by both formats
#   per format:  frames (headless Chromium) -> silent.mp4 -> mux with soundtrack
#                -> ~/Movies/{name}{suffix}.mp4  and  {name}{suffix}-silent.mp4
#
# Formats come from video.json "formats":
#   portrait   720x1280 x1.5 -> 1080x1920  9:16, YouTube Shorts   (the default; no suffix)
#   landscape 1280x720  x1.5 -> 1920x1080  16:9, YouTube / site   (suffix "-landscape")
# A recipe without a "formats" block builds one landscape video, as before.
#
# The recipe folder is only READ. Videos are written to ~/Movies (or $VIDEO_OUT_DIR),
# and the script refuses to write inside any git repository.
#
# usage: build_video.sh RECIPE_DIR [--format NAME|all] [--preview] [--keep] [--work-dir DIR]
#   --format     build only this format (portrait | landscape); default: all formats
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
FORMAT_SEL="all"

while [ $# -gt 0 ]; do
  case "$1" in
    --preview) PREVIEW=1 ;;
    --keep) KEEP=1 ;;
    --format) FORMAT_SEL="${2:?--format needs a name (portrait, landscape or all)}"; shift ;;
    --work-dir) WORK="$2"; OWN_WORK=0; shift ;;
    -h|--help) sed -n '2,25p' "$0"; exit 0 ;;
    *) RECIPE="$1" ;;
  esac
  shift
done
[ -n "$RECIPE" ] || { echo "usage: build_video.sh RECIPE_DIR [--format NAME|all] [--preview] [--keep] [--work-dir DIR]"; exit 2; }
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
DUR="$(cfg duration 30)"
FPS="$(cfg fps 30)"
NAME="$(cfg output.name "${SLUG}-30s")"

# one line per format: name|width|height|scale|suffix|animation|default
FORMAT_LIST="$(python3 -I - "$CFG" "$FORMAT_SEL" <<'PY'
import json, sys
cfg = json.load(open(sys.argv[1]))
sel = sys.argv[2]
fm = cfg.get("formats")
if not fm:   # legacy recipe: a single landscape video with no suffix
    fm = {"landscape": {"width": cfg.get("width", 1280), "height": cfg.get("height", 720),
                        "scale": cfg.get("scale", 1.5), "suffix": ""}}
names = list(fm) if sel == "all" else [sel]
for n in names:
    if n not in fm:
        sys.exit(f"unknown format '{n}': video.json defines {', '.join(fm)}")
    f = fm[n]
    anim = f.get("animation", cfg.get("animation", "animation.html"))
    print("|".join(str(x) for x in (n, f["width"], f["height"], f.get("scale", 1.5),
                                    f.get("suffix", ""), anim, "1" if f.get("default") else "0")))
PY
)"

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
BASE="$NAME"
if [ "$PREVIEW" = 1 ]; then
  FPS=10; BASE="${NAME}-preview"; X264=(-preset veryfast -crf 26)
fi

echo "== $SLUG: ${DUR}s @ ${FPS}fps, formats: $(echo "$FORMAT_LIST" | cut -d'|' -f1 | paste -sd' ' -)"
echo "== work dir: $WORK"

# ---------- 1. soundtrack (shared by every format) ----------
python3 -I "$HERE/make_soundtrack.py" "$CFG" "$WORK/soundtrack.wav"

SUMMARY_LINES=()
WARNINGS=0

# ---------- 2. one pass per format ----------
while IFS='|' read -r FNAME FW FH FSCALE FSUFFIX FANIM FDEFAULT; do
  [ -n "$FNAME" ] || continue
  [ -f "$RECIPE/$FANIM" ] || { echo "missing animation page for $FNAME: $RECIPE/$FANIM"; exit 2; }

  SCALE="$FSCALE"
  [ "$PREVIEW" = 1 ] && SCALE=0.5
  OUT="$BASE$FSUFFIX"
  FW_DIR="$WORK/$FNAME"
  mkdir -p "$FW_DIR"
  TAG=""; [ "$FDEFAULT" = 1 ] && TAG=" (default)"

  echo
  echo "== $FNAME$TAG: ${FW}x${FH} x${SCALE} -> $OUT_DIR/$OUT.mp4"

  # frames
  python3 -I "$HERE/render_frames.py" "$RECIPE/$FANIM" --out "$FW_DIR/frames" --format "$FNAME" \
    --fps "$FPS" --secs "$DUR" --scale "$SCALE" --width "$FW" --height "$FH"

  # silent video
  ffmpeg -nostdin -y -loglevel error -framerate "$FPS" -i "$FW_DIR/frames/f_%04d.png" \
    -c:v libx264 "${X264[@]}" -pix_fmt yuv420p -movflags +faststart "$FW_DIR/silent.mp4"

  # mux picture and sound, deliver
  ffmpeg -nostdin -y -loglevel error -i "$FW_DIR/silent.mp4" -i "$WORK/soundtrack.wav" \
    -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "$FW_DIR/final.mp4"
  cp "$FW_DIR/final.mp4" "$OUT_DIR/$OUT.mp4"
  cp "$FW_DIR/silent.mp4" "$OUT_DIR/$OUT-silent.mp4"

  # verify
  GOT="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT_DIR/$OUT.mp4")"
  RES="$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$OUT_DIR/$OUT.mp4")"
  LOUD="$(ffmpeg -nostdin -hide_banner -nostats -i "$OUT_DIR/$OUT.mp4" -vn \
    -af "ebur128=peak=true:framelog=quiet" -f null - 2>&1 | sed -n '/Summary/,$p')"
  LUFS="$(echo "$LOUD" | awk '/I:/ {print $2; exit}')"
  PEAK="$(echo "$LOUD" | awk '/Peak:/ {print $2; exit}')"
  SIZE="$(du -h "$OUT_DIR/$OUT.mp4" | cut -f1)"

  VERDICT="$(python3 -I - "$GOT" "$DUR" "$LUFS" "$PEAK" "$RES" "$FNAME" "$FW" "$FH" "$SCALE" <<'PY'
import sys
got, dur, lufs, peak = map(float, sys.argv[1:5])
res, fmt = sys.argv[5], sys.argv[6]
fw, fh, sc = float(sys.argv[7]), float(sys.argv[8]), float(sys.argv[9])
w, h = map(int, res.split("x"))
warn = []
if abs(got - dur) > 0.1: warn.append(f"duration {got:.2f}s is not {dur:.0f}s")
if lufs > -11: warn.append("soundtrack is hot (> -11 LUFS): lower music.peak")
if lufs < -20: warn.append("soundtrack is quiet (< -20 LUFS): raise music.peak or limiter_drive")
if peak > -0.1: warn.append("true peak above -0.1 dBFS: lower music.peak")
if (w, h) != (round(fw * sc), round(fh * sc)):
    warn.append(f"frame is {w}x{h}, expected {round(fw*sc)}x{round(fh*sc)}")
if fmt == "portrait" and h * 9 != w * 16:
    warn.append(f"portrait frame {w}x{h} is not 9:16 (YouTube will not treat it as a Short)")
if fmt == "landscape" and w * 9 != h * 16:
    warn.append(f"landscape frame {w}x{h} is not 16:9")
print("OK" if not warn else "; ".join(warn))
PY
)"
  [ "$VERDICT" = "OK" ] || WARNINGS=1

  echo "video   : $OUT_DIR/$OUT.mp4  ($SIZE)"
  echo "silent  : $OUT_DIR/$OUT-silent.mp4"
  echo "frame   : $RES   duration: $GOT s (expected $DUR)"
  echo "loudness: $LUFS LUFS, true peak $PEAK dBFS"
  echo "quality : $VERDICT"
  SUMMARY_LINES+=("$FNAME$TAG|$RES|$SIZE|$OUT_DIR/$OUT.mp4")
done <<< "$FORMAT_LIST"

# ---------- 3. summary ----------
echo
echo "== built:"
for L in "${SUMMARY_LINES[@]}"; do
  IFS='|' read -r A B C D <<< "$L"
  printf '   %-20s %-10s %-6s %s\n' "$A" "$B" "$C" "$D"
done
[ "$WARNINGS" = 0 ] || echo "== WARNING: at least one quality check above did not pass"

# ---------- 4. repo hygiene ----------
"$HERE/check_no_media_in_repo.sh" "$RECIPE" || echo "WARNING: rendered media is inside the repo (see above)"

if [ "$KEEP" = 1 ] || [ "$OWN_WORK" = 0 ]; then
  echo "kept    : $WORK"
else
  rm -rf "$WORK"
fi
