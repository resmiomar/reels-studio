#!/usr/bin/env python3
"""
Забрать недостающие ролики из канала Telegram.

Зачем. Архивы GitHub весят гигабайтами, а связь у владельца четыре мегабайта
в минуту: чтобы достать тридцать семь китайских роликов, пришлось бы качать
полтора гигабайта целиком. В канале же они лежат по одному, и можно взять
ровно те, которых нет.

Как это работает. Бот не умеет читать историю канала - такого метода в API
нет вовсе. Зато умеет ПЕРЕСЛАТЬ сообщение себе, и в ответе приходит полное
описание файла вместе с именем и file_id. По имени узнаём номер ролика, по
file_id скачиваем.

Побочный след: пересланные сообщения остаются в личном чате владельца. Иначе
никак, читать канал бот по-другому не может.

    python zabrat_iz_kanala.py zh          добрать китайские
    python zabrat_iz_kanala.py zh 300      просмотреть до 300-го сообщения
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
BAZA = "/Volumes/T7/ibook-reels/novye"


def token():
    for l in open(os.path.join(HERE, ".env"), encoding="utf-8"):
        if l.startswith("BOT_TOKEN="):
            return l.split("=", 1)[1].strip().strip('"')
    sys.exit("нет BOT_TOKEN в .env")


def zapros(t, metod, **par):
    u = f"https://api.telegram.org/bot{t}/{metod}?" + urllib.parse.urlencode(par)
    try:
        with urllib.request.urlopen(u, timeout=60) as r:
            return json.load(r)
    except Exception as e:
        return {"ok": False, "description": str(e)[:80]}


def kanal(lang):
    d = json.load(open(os.path.join(HERE, "kanaly.json"), encoding="utf-8"))
    for k, v in d.items():
        if v.get("lang") == lang:
            return int(k)
    sys.exit(f"нет канала для языка {lang}")


def est_na_diske(lang):
    p = os.path.join(BAZA, lang)
    if not os.path.isdir(p):
        return set()
    out = set()
    for f in os.listdir(p):
        if f.startswith("._") or not f.endswith(".mp4"):
            continue
        m = re.match(r"(\d{3})", f)
        if m:
            out.add(int(m.group(1)))
    return out


def skachat(t, file_id, kuda):
    d = zapros(t, "getFile", file_id=file_id)
    if not d.get("ok"):
        return False
    put = d["result"]["file_path"]
    u = f"https://api.telegram.org/file/bot{t}/{put}"
    vrem = kuda + ".chast"
    try:
        with urllib.request.urlopen(u, timeout=900) as r, open(vrem, "wb") as f:
            while True:
                kus = r.read(1 << 16)
                if not kus:
                    break
                f.write(kus)
        os.replace(vrem, kuda)
        return os.path.getsize(kuda) > 100000
    except Exception:
        return False


def main():
    lang = sys.argv[1] if len(sys.argv) > 1 else "zh"
    predel = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    # Откуда начинать просмотр. Ролики в каналах лежат НЕ с начала: сперва идут
    # картинки каруселей, и в украинском видео начинаются лишь около тысячного
    # сообщения. Просматривать всё подряд - это лишние пятнадцать минут на язык,
    # по секунде за сообщение.
    nachalo = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    t = token()
    kan = kanal(lang)
    est = est_na_diske(lang)
    nado = [n for n in range(1, 157) if n not in est]
    print(f"  язык {lang}: на диске {len(est)}, не хватает {len(nado)}")
    if not nado:
        print("  всё на месте")
        return
    print(f"  ищу в канале {kan}, сообщения {nachalo}-{predel}\n")

    kuda_p = os.path.join(BAZA, lang)
    os.makedirs(kuda_p, exist_ok=True)
    vzyato = propal = 0
    for mid in range(nachalo, predel + 1):
        if not nado:
            break
        d = zapros(t, "forwardMessage", chat_id=kan, from_chat_id=kan, message_id=mid)
        # Пересылаем В ТОТ ЖЕ канал: так личный чат владельца остаётся чистым.
        # Если канал запрещает пересылку сам себе - пробуем через личный чат.
        if not d.get("ok"):
            propal += 1
            continue
        r = d["result"]
        v = r.get("video") or r.get("document") or {}
        imya = v.get("file_name", "")
        m = re.match(r"(\d{3})", imya)
        if not m or not imya.endswith(".mp4"):
            continue
        nom = int(m.group(1))
        if nom not in nado:
            continue
        cel = os.path.join(kuda_p, imya)
        if skachat(t, v["file_id"], cel):
            nado.remove(nom)
            vzyato += 1
            print(f"    {nom:03d}: забран ({vzyato}, осталось {len(nado)})", flush=True)
        time.sleep(1)

    print(f"\n  забрано {vzyato}, не найдено в канале {len(nado)}")
    if nado:
        print(f"  остались: {nado}")


if __name__ == "__main__":
    main()
