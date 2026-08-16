#!/bin/bash
# Скачивание КУСКАМИ, с честной докачкой. Работает на рвущемся интернете.
#
# История трёх неудач:
#   1. gh run download    - тянет архив одним куском, на обрыве теряет всё.
#   2. gh с повторами     - то же самое, просто чаще. Ноль байт за три захода.
#   3. curl -C - --retry  - ключ --retry при внутреннем повторе ОБНУЛЯЕТ файл.
#      Наблюдалось прямо: архив дорос до 68 МБ и откатился до 15.
#
# Здесь докачка сделана вручную и не может обнулиться:
#   - смотрим, сколько байт уже лежит;
#   - просим ровно остаток, через заголовок диапазона;
#   - ДОПИСЫВАЕМ в конец файла, а не перезаписываем его.
#
# Хранилище это позволяет: на пробу диапазона отвечает кодом 206.
# Ссылка живёт около минуты, поэтому берём свежую на каждый круг.
set -u
cd /Volumes/T7/reels-saas || exit 1
BAZA=/Volumes/T7/ibook-reels/novye
VREM="$BAZA/.arhivy"
mkdir -p "$VREM"
KRUGOV=${KRUGOV:-400}
REPO=resmiomar/reels-studio

# Очередь по НУЖДЕ, а не по алфавиту. Казахский на диске уже лежит весь,
# сто пятьдесят шесть штук, а английского, китайского и немецкого нет вовсе:
# они существуют только в каналах. Поэтому качаем сперва недостающее.
PROGONY="31767397573:en 31767400922:en 31767411322:zh 31767414816:zh \
         31767404345:de 31767408126:de 31767390995:kk 31767394326:kk"

TOKEN=$(gh auth token 2>/dev/null)
[ -z "$TOKEN" ] && { echo "нет токена GitHub"; exit 1; }

for PARA in $PROGONY; do
  ID=${PARA%%:*}; L=${PARA##*:}
  KUDA="$BAZA/$L"; mkdir -p "$KUDA"
  ZIP="$VREM/$ID.zip"
  [ -f "$VREM/.gotovo_$ID" ] && { echo "$ID ($L): уже распакован"; continue; }

  AID=$(curl -s -H "Authorization: Bearer $TOKEN" \
        "https://api.github.com/repos/$REPO/actions/runs/$ID/artifacts" \
        | python3 -c "import sys,json
try:
    a=json.load(sys.stdin)['artifacts']
    print(next(x['id'] for x in a if not x['expired']))
except Exception: print('')" 2>/dev/null)
  [ -z "$AID" ] && { echo "$ID ($L): архив недоступен"; continue; }

  VSEGO=0
  for k in $(seq 1 "$KRUGOV"); do
    SKACHANO=$(stat -f%z "$ZIP" 2>/dev/null || echo 0)
    [ "$VSEGO" -gt 0 ] && [ "$SKACHANO" -ge "$VSEGO" ] && break

    SSYLKA=$(curl -s -o /dev/null -w '%{redirect_url}' \
             -H "Authorization: Bearer $TOKEN" \
             "https://api.github.com/repos/$REPO/actions/artifacts/$AID/zip")
    [ -z "$SSYLKA" ] && { sleep 15; continue; }

    if [ "$VSEGO" -eq 0 ]; then
      VSEGO=$(curl -sI "$SSYLKA" | awk '/[Cc]ontent-[Ll]ength/{gsub(/\r/,"");print $2}' | head -1)
      [ -z "$VSEGO" ] && VSEGO=0
      echo "$ID ($L): всего $((VSEGO/1048576)) МБ"
    fi

    # Просим остаток и ДОПИСЫВАЕМ. Обнулить файл этот вызов не может.
    # --speed-time/--speed-limit обрывают мёртвое соединение за полминуты.
    # Без них curl честно висел ПЯТНАДЦАТЬ минут на соединении, которое не
    # отдавало ни байта, и круги стояли на месте. Лучше быстро оборвать и
    # взять свежую ссылку: она всё равно одноразовая.
    curl -s --max-time 300 --speed-time 30 --speed-limit 10000 \
         -H "Range: bytes=${SKACHANO}-" "$SSYLKA" >> "$ZIP"
    STALO=$(stat -f%z "$ZIP" 2>/dev/null || echo 0)
    echo "$ID ($L): круг $k, $((STALO/1048576)) из $((VSEGO/1048576)) МБ"

    # Если за круг не прибавилось ни байта - переждём подольше.
    [ "$STALO" -le "$SKACHANO" ] && sleep 30
  done

  if unzip -tq "$ZIP" >/dev/null 2>&1; then
    unzip -qo "$ZIP" -d "$KUDA" && touch "$VREM/.gotovo_$ID"
    echo "$ID ($L): РАСПАКОВАН, на диске $(ls "$KUDA"/*.mp4 2>/dev/null | wc -l)"
  else
    echo "$ID ($L): архив пока неполный, вернусь к нему следующим запуском"
  fi
done

echo "=== ИТОГО ==="
for L in kk en de zh; do
  echo "$L: $(ls "$BAZA/$L"/*.mp4 2>/dev/null | wc -l)"
done
du -sh "$BAZA"
