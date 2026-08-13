#!/bin/bash
# Забрать немецкий и китайский год на внешний диск.
#
# На GitHub готовые ролики лежат семь дней и стираются. Этим уже пятый день,
# поэтому копию надо снять сейчас: иначе они останутся только в Telegram, а
# оттуда их доставать поштучно.
cd /Volumes/T7/reels-saas || exit 1

zabrat () {
  KUDA="/Volumes/T7/ibook-reels/$1"
  mkdir -p "$KUDA"
  shift
  for id in "$@"; do
    echo "--- прогон $id"
    gh run download "$id" -n roliki -D "$KUDA" 2>&1 | tail -1
    echo "    на диске: $(ls "$KUDA"/*.mp4 2>/dev/null | wc -l)"
  done
}

# Немецкий: три потока года плюс пробный запуск на 36-ю неделю.
zabrat de 31039850038 31039857030 31039864273 31038596757
# Китайский: три потока года.
zabrat zh 31057368876 31057373718 31057378911

echo "=== ИТОГО ==="
echo "немецких:  $(ls /Volumes/T7/ibook-reels/de/*.mp4 2>/dev/null | wc -l)"
echo "китайских: $(ls /Volumes/T7/ibook-reels/zh/*.mp4 2>/dev/null | wc -l)"
du -sh /Volumes/T7/ibook-reels
