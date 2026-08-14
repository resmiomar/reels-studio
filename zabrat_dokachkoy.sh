#!/bin/bash
# Скачивание С ДОКАЧКОЙ - работает на рвущемся мобильном интернете.
#
# Почему прежние попытки давали ноль. Команда gh тянет архив одним куском и на
# любом обрыве бросает его целиком, не сохраняя ни байта. На раздаче с телефона
# гигабайтный архив не доходит никогда: три захода подряд закончились нулём.
#
# Здесь по-другому. Ссылку на архив берём через API, а качаем curl-ом с ключом
# -C - : он продолжает с того места, где оборвалось, а не начинает сначала.
# Ссылка живёт около минуты, поэтому на каждой попытке берём свежую.
#
# Скрипт можно запускать сколько угодно раз: докачает недостающее и распакует.
set -u
cd /Volumes/T7/reels-saas || exit 1
BAZA=/Volumes/T7/ibook-reels/novye
VREM="$BAZA/.arhivy"
mkdir -p "$VREM"
POPYTOK=${POPYTOK:-40}
REPO=resmiomar/reels-studio

PROGONY="31767390995:kk 31767394326:kk 31767397573:en 31767400922:en \
         31767404345:de 31767408126:de 31767411322:zh 31767414816:zh"

TOKEN=$(gh auth token 2>/dev/null)
[ -z "$TOKEN" ] && { echo "нет токена GitHub"; exit 1; }

for PARA in $PROGONY; do
  ID=${PARA%%:*}; L=${PARA##*:}
  KUDA="$BAZA/$L"; mkdir -p "$KUDA"
  ZIP="$VREM/$ID.zip"
  [ -f "$VREM/.gotovo_$ID" ] && { echo "$ID ($L): уже распакован"; continue; }

  # Номер архива у прогона. Он не меняется, поэтому берём один раз.
  AID=$(curl -s -H "Authorization: Bearer $TOKEN" \
        "https://api.github.com/repos/$REPO/actions/runs/$ID/artifacts" \
        | python3 -c "import sys,json
try:
    a=json.load(sys.stdin)['artifacts']
    print(next(x['id'] for x in a if not x['expired']))
except Exception: print('')" 2>/dev/null)
  [ -z "$AID" ] && { echo "$ID ($L): архив недоступен"; continue; }

  for i in $(seq 1 "$POPYTOK"); do
    BYLO=$(stat -f%z "$ZIP" 2>/dev/null || echo 0)
    # Ссылка одноразовая и живёт около минуты - берём свежую каждый раз.
    SSYLKA=$(curl -s -o /dev/null -w '%{redirect_url}' \
             -H "Authorization: Bearer $TOKEN" \
             "https://api.github.com/repos/$REPO/actions/artifacts/$AID/zip")
    [ -z "$SSYLKA" ] && { sleep 20; continue; }
    # -C - продолжает с места обрыва, --retry сам повторяет мелкие сбои.
    curl -sL -C - --retry 5 --retry-delay 5 --speed-time 60 --speed-limit 1000 \
         -o "$ZIP" "$SSYLKA"
    STALO=$(stat -f%z "$ZIP" 2>/dev/null || echo 0)
    # Архив цел, если распаковщик не ругается на его оглавление.
    if unzip -tq "$ZIP" >/dev/null 2>&1; then
      unzip -qo "$ZIP" -d "$KUDA" && touch "$VREM/.gotovo_$ID"
      echo "$ID ($L): готов, на диске $(ls "$KUDA"/*.mp4 2>/dev/null | wc -l)"
      # Скачанный архив оставляем: места на диске много, а если распаковка
      # окажется неполной, будет из чего повторить. Убрать папку .arhivy
      # можно потом руками, когда всё сойдётся.
      break
    fi
    echo "$ID ($L): попытка $i, скачано $((STALO/1048576)) МБ (было $((BYLO/1048576)))"
    sleep 10
  done
done

echo "=== ИТОГО ==="
for L in kk en de zh; do
  echo "$L: $(ls "$BAZA/$L"/*.mp4 2>/dev/null | wc -l)"
done
du -sh "$BAZA"
