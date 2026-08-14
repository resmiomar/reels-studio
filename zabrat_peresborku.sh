#!/bin/bash
# Забрать пересобранные ролики на внешний диск и записать, чего не хватило.
#
# Пересборка идёт БЕЗ отправки в каналы: старые ролики там остаются, новые
# ложатся на диск. Так владелец сам решает, менять ли содержимое каналов.
cd /Volumes/T7/reels-saas || exit 1
BAZA=/Volumes/T7/ibook-reels/novye
mkdir -p "$BAZA"

for id in $(gh run list --limit 8 --json databaseId --jq '.[].databaseId'); do
  L=$(gh run view "$id" --log 2>/dev/null | grep -oE "^.*язык [a-z]{2}" | head -1 | grep -oE "[a-z]{2}$")
  [ -z "$L" ] && L=raznoe
  mkdir -p "$BAZA/$L"
  echo "--- прогон $id, язык $L"
  gh run download "$id" -n roliki -D "$BAZA/$L" 2>&1 | tail -1
  echo "    на диске: $(ls "$BAZA/$L"/*.mp4 2>/dev/null | wc -l)"
done

echo "=== ИТОГО ==="
for L in kk en de zh; do
  echo "$L: $(ls "$BAZA/$L"/*.mp4 2>/dev/null | wc -l)"
done
du -sh "$BAZA"
