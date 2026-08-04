#!/bin/bash
# Что реально ушло в канал, а что застряло. Девять прогонов слали файлы
# одновременно, Telegram ответил 429 «слишком часто» - часть роликов не дошла.
# Логи держим на диске, чтобы не тянуть их с сервера каждый раз.
cd /Volumes/T7/reels-saas || exit 1
D=/Volumes/T7/ibook-reels/logi
mkdir -p "$D"
for id in 30832145614 30832139966 30832134805 30832129031 30832122271 \
          30832115952 30832110555 30832105289 30832099719 30877174890; do
  [ -s "$D/$id.log" ] || gh run view "$id" --log > "$D/$id.log" 2>&1
  echo "$id готов"
done
grep -ho "[0-9]\{3\}-[^ ]*\.mp4 -> " "$D"/*.log | sed 's/ -> //' | sort -u > "$D/ushli.txt"
grep -ho "[0-9]\{3\}-[^ ]*\.mp4: не ушло" "$D"/*.log | sed 's/: не ушло//' | sort -u > "$D/zastryali.txt"
echo "ушло:      $(wc -l < "$D/ushli.txt")"
echo "застряло:  $(wc -l < "$D/zastryali.txt")"
