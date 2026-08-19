#!/bin/bash
# Забрать архивы трёх новых языков. Кусками, с дозаписью: прямое скачивание
# гигабайтного архива рвётся на середине, и curl -C - при этом ОБНУЛЯЕТ файл.
# Поэтому просим остаток заголовком Range и дописываем в конец сами.
set -u
BAZA=/Volumes/T7/ibook-reels/novye
VREM="$BAZA/.arhivy"; mkdir -p "$VREM"
TOKEN=$(cat "$HOME/.ibook_gh_token" 2>/dev/null || gh auth token 2>/dev/null)
[ -z "$TOKEN" ] && { echo "нет токена"; exit 1; }
REPO=resmiomar/reels-studio

while read -r L AID VSEGO; do
  [ -z "${AID:-}" ] && continue
  KUDA="$BAZA/$L"; mkdir -p "$KUDA"
  ZIP="$VREM/$AID.zip"
  [ -f "$VREM/.gotovo_$AID" ] && { echo "$L: уже распакован"; continue; }
  for k in $(seq 1 200); do
    EST=$(stat -f%z "$ZIP" 2>/dev/null || echo 0)
    [ "$EST" -ge "$VSEGO" ] && break
    SSYLKA=$(curl -s -o /dev/null -w '%{redirect_url}' -H "Authorization: Bearer $TOKEN" \
             "https://api.github.com/repos/$REPO/actions/artifacts/$AID/zip")
    [ -z "$SSYLKA" ] && { sleep 10; continue; }
    curl -s --max-time 300 --speed-time 30 --speed-limit 20000 \
         -H "Range: bytes=${EST}-" "$SSYLKA" >> "$ZIP"
    STALO=$(stat -f%z "$ZIP" 2>/dev/null || echo 0)
    echo "$L: $((STALO/1048576)) из $((VSEGO/1048576)) МБ"
    [ "$STALO" -le "$EST" ] && sleep 20
  done
  if unzip -tq "$ZIP" >/dev/null 2>&1; then
    unzip -qo "$ZIP" -d "$KUDA" && touch "$VREM/.gotovo_$AID"
    echo "$L: РАСПАКОВАН, роликов $(ls "$KUDA"/*.mp4 2>/dev/null | grep -vc '\._')"
  else
    echo "$L: архив пока неполный"
  fi
done < /tmp/uzproba/arhivy.txt
echo "=== ИТОГО ==="
for L in ru tr uk; do echo "  $L: $(ls "$BAZA/$L"/*.mp4 2>/dev/null | grep -vc '\._')"; done
