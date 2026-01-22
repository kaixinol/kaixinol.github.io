#!/bin/sh
set -eu
SRC="$(pwd)"
TMP="/tmp/zola-work"
rm -rf "$TMP"
mkdir -p "$TMP"
cd "$SRC"
if [ -d .venv ]; then
  ln -s "$SRC/.venv" "$TMP/.venv"
fi
rsync -a \
  --exclude 'content' \
  --exclude '.venv' \
  "$SRC/" "$TMP/"
cp -a "$SRC/content" "$TMP/content"
cd "$TMP"
find content -name "*.md" -exec sed -i 's|../../static/images/|/images/|g' {} +
source .venv/bin/activate
python optimize_fonts.py
python upload_img.py
python sync_data.py
zola serve --drafts


