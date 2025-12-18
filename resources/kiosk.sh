#!/usr/bin/env bash
set -e

# attendre que l'API soit prête
until curl -fsS http://127.0.0.1:8787/ >/dev/null; do
  sleep 0.5
done

# éviter doublons chromium
pkill -u user -f "/usr/bin/chromium.*chromium-kiosk" 2>/dev/null || true

# cacher le curseur
unclutter -idle 0.1 -root &

exec /usr/bin/chromium \
  --kiosk \
  --noerrdialogs \
  --disable-infobars \
  --disable-translate \
  --disable-features=TranslateUI \
  --lang=en-US \
  --incognito \
  --overscroll-history-navigation=0 \
  --check-for-update-interval=31536000 \
  --disable-features=TranslateUI \
  --user-data-dir=/home/user/.config/chromium-kiosk \
  --disk-cache-dir=/tmp/chromecache \
  --disk-cache-size=1 \
  http://127.0.0.1:8787/