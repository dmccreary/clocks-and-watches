#!/usr/bin/env bash
# Rebuild the 30-second video for this kit.
# The MP4 is written to ~/Movies (never into this repo). See README.md.
#
#   ./build.sh            full quality, 1920x1080 @ 30 fps with soundtrack
#   ./build.sh --preview  half-size 10 fps check of the whole pipeline
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "$HERE" rev-parse --show-toplevel)"
exec "$REPO/skills/video-of-kit-generator/scripts/build_video.sh" "$HERE" "$@"
