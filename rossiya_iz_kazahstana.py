#!/usr/bin/env python3
"""
Российская версия ролика из казахстанской: звук тот же, кадры другие.

Владелец решил не озвучивать Россию заново. Причина простая: озвучка стоит
знаков подписки и времени, а голос и текст для обеих стран годятся одни и те
же. Разными делаем только кадры - иначе Instagram сочтёт ролики дублями и
прижмёт охват обоим.

Писать новый монтаж не пришлось. В движке уже есть готовый ход: если рядом
лежит папка с озвучкой, он берёт дорожку оттуда вместо синтеза. Мы этим
пользовались для казахского, когда голоса на сервере не было. Здесь тот же
приём, только дорожки не из старых роликов, а снятые с казахстанских.

Что делает скрипт:

    1  берёт готовый казахстанский ролик
    2  снимает с него звук БЕЗ пересжатия - сведение уже утверждено владельцем
    3  кладёт в assets/golos-rf/ под именем, которое движок ищет: NNN-rf.mp3

Дальше обычный прогон на языке rf. Движок увидит дорожку, синтез пропустит,
а кадры наберёт заново по российским запросам к стоку - они в сценарии свои.

Про цену. Шестьдесят два казахстанских ролика называют семь тысяч тенге.
В России это чужая валюта и чужая цена. Владелец знает и принял: время
дороже. Скрипт печатает их номера, чтобы заменить потом только их, а не
пересматривать все сто пятьдесят шесть.

    python rossiya_iz_kazahstana.py                весь готовый Казахстан
    python rossiya_iz_kazahstana.py 91 92 93       только эти номера
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Откуда берём казахстанские ролики и куда кладём снятые дорожки.
KZ = os.environ.get("KZ_DIR", "/Volumes/T7/ibook-reels/novye/ru")
GOLOS = os.environ.get("GOLOS_RF", os.path.join(HERE, "assets", "golos-rf"))
CENA = re.compile(r"тенге|₸")


def dlina(put):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", put], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def snyat_zvuk(video, kuda):
    """Снять дорожку и привести к mp3: движок ждёт именно его.

    Пересжатие тут неизбежно - в ролике звук в aac, а искомое имя с .mp3.
    Берём высокий битрейт, чтобы утверждённое сведение не пострадало.
    """
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vn",
                    "-c:a", "libmp3lame", "-q:a", "0", kuda], check=True)
    return dlina(kuda)


def nomera_na_diske():
    if not os.path.isdir(KZ):
        return []
    out = []
    for f in sorted(os.listdir(KZ)):
        if f.startswith("._") or not f.endswith(".mp4"):
            continue
        m = re.match(r"(\d{3})-", f)
        if m:
            out.append(int(m.group(1)))
    return out


def main():
    hochu = [int(x) for x in sys.argv[1:]] or nomera_na_diske()
    if not hochu:
        sys.exit(f"в {KZ} нет готовых казахстанских роликов")
    os.makedirs(GOLOS, exist_ok=True)

    scen = json.load(open(os.path.join(HERE, "scenarii", "videos_ru.json"),
                          encoding="utf-8"))
    sdelano, s_cenoy, propal = [], [], []
    for n in hochu:
        ishod = os.path.join(KZ, f"{n:03d}-Казахстан-русский.mp4")
        if not os.path.exists(ishod):
            propal.append(n)
            continue
        kuda = os.path.join(GOLOS, f"{n:03d}-rf.mp3")
        d = snyat_zvuk(ishod, kuda)
        if d < 3:
            propal.append(n)
            continue
        if n <= len(scen) and CENA.search(scen[n - 1].get("vo", "")):
            s_cenoy.append(n)
        sdelano.append(n)
        if len(sdelano) % 20 == 0:
            print(f"  снято дорожек: {len(sdelano)}", flush=True)

    print(f"\nснято дорожек: {len(sdelano)}")
    if propal:
        print(f"не нашлось роликов: {len(propal)} -> {propal[:12]}")
    print(f"лежат в {GOLOS}")

    if s_cenoy:
        print(f"\nВ {len(s_cenoy)} роликах звучит цена в тенге - для России это")
        print("чужая валюта. Номера, чтобы заменить их позже:")
        print("  " + " ".join(f"{n:03d}" for n in sorted(s_cenoy)))

    print("\nДальше: обычный прогон на языке rf. Движок увидит эти дорожки,")
    print("синтез пропустит, кадры наберёт заново по российским запросам.")


if __name__ == "__main__":
    main()
