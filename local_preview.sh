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
cp -a "$SRC/upload_cache.json" "$TMP/" 2>/dev/null || true
cd "$TMP"
find content -name "*.md" -exec sed -i 's|../../static/images/|/images/|g' {} +
source .venv/bin/activate
python optimize_fonts.py
python upload_img.py
python sync_data.py
python sync_css.py
sed -i 's|^base_url = "https://kaixinol\.github\.io/"|base_url = "/"|' config.toml
zola build
wget -O public/js/lightense.min.js https://cdn.jsdelivr.net/npm/@kaesinol/lightense-images@latest/dist/lightense.min.js
sed -E -i 's/::selection\s*\{[^}]*\}//g' public/main.css
python -m http.server -d public --bind localhost 8000


