#!/usr/bin/env bash
# headless_shot.sh -- take a full-page screenshot of a local HTML page with headless Chrome,
# then cut it into slices you can look at one at a time.
#
#   headless_shot.sh <file.html> <out.png> [width=1200] [height=3200]
#
# Use it to LOOK at a built lesson page or a box cover before you say it is done.
# Recipe notes (each one cost a failed attempt):
#   * a throwaway --user-data-dir keeps this away from the user's real Chrome
#   * --virtual-time-budget lets web fonts and scripts settle before the shot
#   * headless Chrome often does not exit after writing the file, so we wait for the file,
#     then kill ONLY the processes that use our throwaway profile
#   * a URL #fragment does NOT scroll the shot; ask for a tall window instead and slice it
#   * the tall window must be at least as tall as the page, or the bottom is cut off
#   * transparent PNGs show as white on a white page: that is expected
#
# Slices are written next to the screenshot as <out>-slice-00.png, -01.png, ... (1300 px tall).
set -euo pipefail
HTML="${1:?usage: headless_shot.sh <file.html> <out.png> [width] [height]}"
OUT="${2:?usage: headless_shot.sh <file.html> <out.png> [width] [height]}"
WIDTH="${3:-1200}"
HEIGHT="${4:-3200}"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
[ -x "$CHROME" ] || { echo "Chrome not found at: $CHROME (set CHROME=...)" >&2; exit 1; }

PROFILE="$(mktemp -d /tmp/headless-shot-profile.XXXXXX)"
ABS_HTML="$(cd "$(dirname "$HTML")" && pwd)/$(basename "$HTML")"
rm -f "$OUT"

"$CHROME" --headless=new --disable-gpu --no-first-run --no-default-browser-check \
  --user-data-dir="$PROFILE" --hide-scrollbars --virtual-time-budget=8000 \
  --window-size="$WIDTH,$HEIGHT" --screenshot="$OUT" "file://$ABS_HTML" >/dev/null 2>&1 &

for _ in $(seq 1 60); do
  if [ -s "$OUT" ]; then sleep 3; break; fi
  sleep 1
done
pkill -f "$PROFILE" 2>/dev/null || true
sleep 1
rm -rf "$PROFILE"
[ -s "$OUT" ] || { echo "no screenshot was written" >&2; exit 1; }

python3 - "$OUT" <<'EOF'
import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
out = sys.argv[1]
im = Image.open(out).convert("RGB")
w, h = im.size
step, n = 1300, 0
for y in range(0, h, step):
    im.crop((0, y, w, min(y + step, h))).save(out.replace(".png", "-slice-%02d.png" % n))
    n += 1
print("screenshot %dx%d, %d slices written next to %s" % (w, h, n, out))
EOF
