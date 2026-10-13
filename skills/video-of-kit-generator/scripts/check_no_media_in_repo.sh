#!/usr/bin/env bash
# Fail if rendered media (video, audio, GIF) sits inside the git repo that contains PATH.
# Videos belong in ~/Movies. Only the recipe (video.json, animation.html, build.sh,
# README.md) is allowed in media/kits/{SLUG}/.
#
# usage: check_no_media_in_repo.sh [PATH_INSIDE_REPO]
set -uo pipefail

ROOT="$(git -C "${1:-.}" rev-parse --show-toplevel 2>/dev/null)" || {
  echo "not inside a git repo: nothing to check"
  exit 0
}
cd "$ROOT"

EXT='\.(mp4|mov|m4v|webm|avi|mkv|wav|mp3|m4a|aac|gif)$'

# 1. anything under media/ on disk (tracked, untracked, or ignored)
on_disk="$(find media -type f 2>/dev/null | grep -i -E "$EXT" || true)"
# 2. anything named like a finished video anywhere in the working tree
named="$(find . -path ./.git -prune -o -path ./site -prune -o -type f -iname '*-30s*' -print 2>/dev/null \
         | grep -i -E "$EXT" || true)"
# 3. anything git tracks that looks like it came from this skill
tracked="$(git ls-files | grep -i -E -- '-30s.*'"$EXT" || true)"

bad="$(printf '%s\n%s\n%s\n' "$on_disk" "$named" "$tracked" | sed -e '/^$/d' -e 's#^\./##' | sort -u)"

if [ -n "$bad" ]; then
  echo "FAIL: rendered media found inside the repo ($ROOT):"
  echo "$bad" | sed 's/^/  /'
  echo "Move these to ~/Movies and never 'git add' them."
  exit 1
fi
echo "OK: no rendered media inside $ROOT"
