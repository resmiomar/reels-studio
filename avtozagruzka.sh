#!/bin/bash
# Автозагрузка роликов на внешний диск. Запускается сама, как только компьютер
# включён и T7 подключён - службой digital.ibook.zabrat.
#
# Почему кусками. Связь у владельца около 4 МБ в минуту, а архивы по гигабайту.
# Прямое скачивание рвётся на середине, и curl -C - при этом ОБНУЛЯЕТ файл -
# так мы уже теряли 68 мегабайт. Поэтому просим остаток заголовком Range и
# дописываем в конец сами.
#
# Скрипт выходит с ошибкой, пока не забрал всё. Служба перезапускает его
# именно по ненулевому выходу - так скачивание переживает и сон ноутбука,
# и обрыв связи, и выключение на ночь.
set -u
BAZA=/Volumes/T7/ibook-reels/novye
VREM="$BAZA/.arhivy"
SPISOK=/Volumes/T7/reels-saas/arhivy.txt
REPO=resmiomar/reels-studio

# Диск может быть не подключён - тогда просто выходим и ждём следующего раза.
[ -d "$BAZA" ] || { echo "T7 не подключён"; exit 1; }
mkdir -p "$VREM"

# Токен берём из файла, а не из связки ключей: служба запускается без доступа
# к связке и молча падала.
TOKEN=$(cat "$HOME/.ibook_gh_token" 2>/dev/null || gh auth token 2>/dev/null)
[ -z "$TOKEN" ] && { echo "нет токена GitHub"; exit 1; }
[ -f "$SPISOK" ] || { echo "нет списка архивов: $SPISOK"; exit 1; }

while read -r L AID VSEGO; do
  [ -z "${AID:-}" ] && continue
  KUDA="$BAZA/$L"; mkdir -p "$KUDA"
  ZIP="$VREM/$AID.zip"
  [ -f "$VREM/.gotovo_$AID" ] && continue

  for k in $(seq 1 60); do
    EST=$(stat -f%z "$ZIP" 2>/dev/null || echo 0)
    [ "$EST" -ge "$VSEGO" ] && break
    SSYLKA=$(curl -s -o /dev/null -w '%{redirect_url}' -H "Authorization: Bearer $TOKEN" \
             "https://api.github.com/repos/$REPO/actions/artifacts/$AID/zip")
    [ -z "$SSYLKA" ] && { sleep 15; continue; }
    # speed-time/speed-limit обрывают мёртвое соединение за полминуты. Без них
    # curl висел ПЯТНАДЦАТЬ минут на сокете, который не отдавал ни байта.
    curl -s --max-time 600 --speed-time 30 --speed-limit 10000 \
         -H "Range: bytes=${EST}-" "$SSYLKA" >> "$ZIP"
    STALO=$(stat -f%z "$ZIP" 2>/dev/null || echo 0)
    echo "$L: $((STALO/1048576)) из $((VSEGO/1048576)) МБ"
    [ "$STALO" -le "$EST" ] && sleep 20
  done

  if unzip -tq "$ZIP" >/dev/null 2>&1; then
    unzip -qo "$ZIP" -d "$KUDA" && touch "$VREM/.gotovo_$AID"
    echo "$L: РАСПАКОВАН, роликов $(ls "$KUDA"/*.mp4 2>/dev/null | grep -vc '\._')"
  fi
done < "$SPISOK"

# После каждого захода перекладываем свежее в чистый каталог: владелец берёт
# ролики оттуда, и ему не надо знать, какой архив уже распакован.
/Volumes/T7/reels-saas/.venv/bin/python /Volumes/T7/reels-saas/razlozhit_na_disk.py 2>&1 | tail -12

echo "=== СКОЛЬКО НА ДИСКЕ ==="
VSE=0
for L in kk ru rf uk tr uz zh en de; do
  N=$(ls "$BAZA/$L"/*.mp4 2>/dev/null | grep -vc '\._')
  echo "  $L: $N"
  VSE=$((VSE + N))
done
echo "  итого: $VSE"

# Пока не собрали весь год по восьми языкам плюс Россию - просим службу
# запустить нас снова.
[ "$VSE" -ge 1404 ] && { echo "ВСЁ ЗАБРАНО"; exit 0; }
echo "буду продолжать"
exit 1
