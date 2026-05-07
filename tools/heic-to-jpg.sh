#!/usr/bin/env bash
# heic-to-jpg.sh — batch-convert HEIC → JPG for the test toolchain.
# Bash equivalent of tools/heic-to-jpg.ps1; same args, same behaviour.
#
# Requires: ImageMagick + libheif
#   Ubuntu:  sudo apt-get install imagemagick libheif1
#   macOS:   brew install imagemagick libheif
#
# Usage:
#   ./tools/heic-to-jpg.sh <source-dir> <dest-dir> [maxwidth=1800] [quality=82]
set -euo pipefail
SRC="${1:?usage: $0 <source-dir> <dest-dir> [maxwidth] [quality]}"
DST="${2:?usage: $0 <source-dir> <dest-dir> [maxwidth] [quality]}"
MAX="${3:-1800}"
Q="${4:-82}"

command -v convert >/dev/null 2>&1 || {
  echo "[FAIL] ImageMagick 'convert' is not on PATH." >&2
  echo "       Ubuntu: sudo apt-get install imagemagick libheif1" >&2
  echo "       macOS:  brew install imagemagick libheif" >&2
  exit 1
}
[[ -d "$SRC" ]] || { echo "[FAIL] source folder not found: $SRC" >&2; exit 1; }
mkdir -p "$DST"

CONV=0; SKIP=0; FAIL=0
shopt -s nullglob
for f in "$SRC"/*.HEIC "$SRC"/*.heic; do
  base="$(basename "$f")"
  name="${base%.*}"
  out="$DST/$name.jpg"
  if [[ -f "$out" ]]; then SKIP=$((SKIP+1)); continue; fi
  if convert "$f" -resize "${MAX}x${MAX}>" -quality "$Q" "$out" 2>/dev/null; then
    CONV=$((CONV+1))
    sz=$(du -k "$out" | cut -f1)
    echo "[OK] $base -> $name.jpg  ${sz} KB"
  else
    FAIL=$((FAIL+1))
    echo "[FAIL] $base" >&2
  fi
done
echo
echo "[heic-to-jpg] converted=$CONV  skipped=$SKIP  failed=$FAIL"
[[ $FAIL -eq 0 ]]
