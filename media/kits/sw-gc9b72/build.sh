#!/usr/bin/env bash
# Rebuild the 30-second videos for this kit: portrait (default, YouTube Shorts) and landscape.
# The MP4s are written to ~/Movies (never into this repo). See README.md,
# PORTRAIT.md and LANDSCAPE.md.
#
#   ./build.sh                     both formats, full quality, with soundtrack
#   ./build.sh --format portrait   only the portrait video (1080x1920, 9:16)
#   ./build.sh --format landscape  only the landscape video (1920x1080, 16:9)
#   ./build.sh --preview           half-size 10 fps check of the whole pipeline (any of the above)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "$HERE" rev-parse --show-toplevel)"
exec "$REPO/skills/video-of-kit-generator/scripts/build_video.sh" "$HERE" "$@"
