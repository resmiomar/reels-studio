#!/bin/bash
# Забрать собранные ролики с сервера на внешний диск.
# Сборка идёт на GitHub, готовые файлы лежат там семь дней - потом пропадут.
# Поэтому качаем всё к себе на T7 и дальше живём с диска.
cd /Volumes/T7/reels-saas || exit 1
KUDA=/Volumes/T7/ibook-reels/kk
mkdir -p "$KUDA"
for id in 30832145614 30832139966 30832134805 30832129031 30832122271 \
          30832115952 30832110555 30832105289 30832099719 30877174890; do
  echo "--- прогон $id"
  gh run download "$id" -n roliki -D "$KUDA" 2>&1 | tail -1
  echo "    роликов на диске: $(ls "$KUDA"/*.mp4 2>/dev/null | wc -l)"
done
echo "ГОТОВО: $(ls "$KUDA"/*.mp4 2>/dev/null | wc -l) роликов"
