#!/usr/bin/env python3
"""
Российская версия ролика из казахстанской: звук тот же, кадры другие.

Владелец решил не озвучивать Россию заново. Причина простая: озвучка стоит
знаков подписки и времени, а голос и текст для обеих стран годятся одни и те
же. Разными делаем только кадры - иначе Instagram сочтёт ролики дублями и
прижмёт охват обоим.

Что берём из готового казахстанского ролика:

    звук целиком   голос, музыка, сведение - всё уже утверждено владельцем
    длину          новый ролик обязан совпасть до кадра, иначе звук разъедется

Что делаем заново:

    кадры          другие клипы из стока, ни один не повторяется
    субтитры       текст тот же, но рисуются заново под новую картинку

Про цену. Шестьдесят два казахстанских ролика называют семь тысяч тенге.
В России это чужая валюта и чужая цена. Владелец знает и принял: время
дороже. Скрипт помечает такие ролики в отчёте, чтобы их можно было заменить
позже, не пересматривая все сто пятьдесят шесть.

    python rossiya_iz_kazahstana.py 001            один ролик
    python rossiya_iz_kazahstana.py все            весь готовый Казахстан
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KZ = os.environ.get("KZ_DIR", "/Volumes/T7/ibook-reels/novye/ru")
OUT = os.environ.get("RF_DIR", "/Volumes/T7/ibook-reels/novye/rf")
CENA = re.compile(r"тенге|₸")


def dlina(put):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", put], capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def zvuk_iz(video, kuda):
    """Забрать звуковую дорожку как есть, без пересжатия: она уже утверждена."""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vn",
                    "-c:a", "copy", kuda], check=True)
    return dlina(kuda)


def kadry_dlya(nomer, skolko, ispolzovano):
    """Клипы под российскую версию. Берём ДРУГИЕ запросы к стоку, чтобы
    картинка не совпала с казахстанской: там были свои, здесь свои."""
    import reel_engine as dv
    zaprosy = [
        "russian woman using smartphone indoors",
        "beauty salon interior modern bright",
        "hairdresser working with client closeup",
        "woman scrolling phone calendar app",
        "happy client leaving salon smiling",
        "manicure master hands working",
        "young woman booking appointment online",
        "barber shop chair empty morning",
    ]
    out = []
    for i in range(skolko):
        q = zaprosy[(nomer + i) % len(zaprosy)]
        cid, link = dv.find_clip(q, ispolzovano)
        if link:
            out.append((q, link))
    return out


def otchet(sdelano, s_cenoy):
    print(f"\nсобрано роликов: {len(sdelano)}")
    if s_cenoy:
        print(f"\nВНИМАНИЕ: в {len(s_cenoy)} роликах звучит цена в тенге.")
        print("Для России это чужая валюта. Номера, чтобы заменить позже:")
        print("  " + " ".join(f"{n:03d}" for n in sorted(s_cenoy)))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    os.makedirs(OUT, exist_ok=True)
    scen = json.load(open(os.path.join(HERE, "scenarii", "videos_ru.json"),
                          encoding="utf-8"))

    if sys.argv[1] == "все":
        nomera = []
        for f in sorted(os.listdir(KZ)):
            m = re.match(r"(\d{3})-", f)
            if m and f.endswith(".mp4") and not f.startswith("._"):
                nomera.append(int(m.group(1)))
    else:
        nomera = [int(sys.argv[1])]

    sdelano, s_cenoy = [], []
    for n in nomera:
        ishod = os.path.join(KZ, f"{n:03d}-Казахстан-русский.mp4")
        if not os.path.exists(ishod):
            print(f"  {n:03d}: казахстанского ролика нет, пропускаю")
            continue
        if n <= len(scen) and CENA.search(scen[n - 1].get("vo", "")):
            s_cenoy.append(n)
        zv = os.path.join(OUT, f"{n:03d}-zvuk.m4a")
        d = zvuk_iz(ishod, zv)
        print(f"  {n:03d}: звук снят, {d:.1f} сек")
        sdelano.append(n)

    otchet(sdelano, s_cenoy)
    print(f"\nЗвуковые дорожки лежат в {OUT}")
    print("Дальше их подхватит движок и наложит на другие кадры.")


if __name__ == "__main__":
    main()
