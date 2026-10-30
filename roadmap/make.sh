#!/bin/bash
# Turns roadmap.html into roadmap.png and roadmap-dark.png with Google Chrome (Mac).
cd "$(dirname "$0")"
C="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
URL="file://$PWD/roadmap.html"
H=$("$C" --headless=new --hide-scrollbars --window-size=1080,2000 --virtual-time-budget=3000 --dump-dom "$URL" 2>/dev/null | grep -o 'data-h="[0-9]*"' | grep -o '[0-9]*')
[ -n "$H" ] || { echo "Could not measure the page"; exit 1; }
for v in "roadmap.png|" "roadmap-dark.png|#dark"; do
  "$C" --headless=new --hide-scrollbars --force-device-scale-factor=2 --window-size=1080,$H \
    --virtual-time-budget=3000 --screenshot="$PWD/${v%%|*}" "$URL${v##*|}" 2>/dev/null
done
echo "Done: 2160 × $((H * 2)) pixels"
