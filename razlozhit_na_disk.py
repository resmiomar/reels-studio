#!/usr/bin/env python3
"""
Разложить готовые ролики в отдельный каталог на внешнем диске.

Зачем отдельно. Рабочая папка novye/ вперемешку: там и архивы, и временные
файлы, и папки -oblozhka с исправленными копиями, и логи. Владельцу нужен
каталог, куда можно зайти и сразу увидеть год по рынкам, не разбираясь, что
из этого черновик.

Правило простое: если у ролика есть починенная обложка - берём её, иначе
исходный. Так в каталоге оказывается ЛУЧШАЯ версия каждого ролика, и не надо
помнить, где какая.

Оригиналы остаются на месте. Каталог - это копия, а не переезд: если что-то
разложится не так, чинить будем копию.

    python razlozhit_na_disk.py            разложить всё готовое
    python razlozhit_na_disk.py kk ru      только эти языки
"""
import os
import shutil
import sys

OTKUDA = "/Volumes/T7/ibook-reels/novye"
KUDA = "/Volumes/T7/ibook-ГОД-ВИДЕО"

# Как назвать папку рынка. Имя должно читаться без пояснений: владелец этих
# языков не знает и по содержимому ролика рынок не определит.
RYNKI = {
    "kk": "01-Казахстан-казахский",
    "ru": "02-Казахстан-русский",
    "rf": "03-Россия-русский",
    "uz": "04-Узбекистан-узбекский",
    "tr": "05-Турция-турецкий",
    "uk": "06-Украина-украинский",
    "en": "07-США-английский",
    "de": "08-Германия-немецкий",
    "zh": "09-Китай-китайский",
}


def rolik_luchshiy(lang, imya):
    """Путь к лучшей версии ролика: с починенной обложкой, если она есть."""
    pochinen = os.path.join(OTKUDA, f"{lang}-oblozhka", imya)
    if os.path.exists(pochinen) and os.path.getsize(pochinen) > 100000:
        return pochinen, "обложка починена"
    return os.path.join(OTKUDA, lang, imya), "как собрано"


def razlozhit(lang):
    papka = os.path.join(OTKUDA, lang)
    if not os.path.isdir(papka):
        return 0, 0
    kuda = os.path.join(KUDA, RYNKI.get(lang, lang))
    os.makedirs(kuda, exist_ok=True)
    skopirovano = pochineno = 0
    for imya in sorted(os.listdir(papka)):
        if imya.startswith("._") or not imya.endswith(".mp4"):
            continue
        istochnik, otkuda = rolik_luchshiy(lang, imya)
        cel = os.path.join(kuda, imya)
        # Уже лежит и того же размера - не перекладываем заново.
        if os.path.exists(cel) and os.path.getsize(cel) == os.path.getsize(istochnik):
            skopirovano += 1
            continue
        shutil.copy2(istochnik, cel)
        skopirovano += 1
        if otkuda == "обложка починена":
            pochineno += 1
    return skopirovano, pochineno


def main():
    yazyki = sys.argv[1:] or list(RYNKI)
    os.makedirs(KUDA, exist_ok=True)
    vsego = vsego_poch = 0
    print(f"РАСКЛАДЫВАЮ В {KUDA}\n")
    for l in yazyki:
        n, p = razlozhit(l)
        if not n:
            continue
        vsego += n
        vsego_poch += p
        print(f"  {RYNKI.get(l, l):28} {n:3} роликов"
              + (f", из них с починенной обложкой {p}" if p else ""))
    print(f"\n  всего разложено: {vsego}")
    print(f"  с починенной обложкой: {vsego_poch}")

    # Записка рядом: через месяц никто не вспомнит, что тут к чему.
    with open(os.path.join(KUDA, "ЧТО ЗДЕСЬ.txt"), "w", encoding="utf-8") as f:
        f.write(
            "ГОД ВИДЕО ДЛЯ ibook\n"
            "\n"
            "Каждая папка - один рынок. Внутри 156 роликов на год,\n"
            "по три в неделю. Имя файла начинается с номера: 001 идёт\n"
            "первой неделей января, 156 - последней неделей декабря.\n"
            "\n"
            "Ролики уже готовы к загрузке: 1080x1920, 30 кадров,\n"
            "звук выровнен по громкости, обложка не чёрная.\n"
            "\n"
            "Это КОПИЯ. Рабочие файлы лежат в ibook-reels/novye,\n"
            "трогать их не нужно.\n")
    print(f"  записка: {os.path.join(KUDA, 'ЧТО ЗДЕСЬ.txt')}")


if __name__ == "__main__":
    main()
