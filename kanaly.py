#!/usr/bin/env python3
"""
Отправка роликов по странам: свой Telegram-канал для каждого рынка.

    python kanaly.py найди          какие каналы бот уже видит
    python kanaly.py карта          какой язык в какой канал
    python kanaly.py шли <папка>    разослать ролики по каналам

Как бот узнаёт про канал. Списка каналов Telegram боту не даёт - он видит только
те, куда его добавили. Поэтому: добавляешь бота администратором, Telegram
присылает ему событие, мы его ловим и запоминаем id и название. Один раз на канал.

Ролики уходят ФАЙЛОМ, а не видео: так Telegram не пережимает и качество остаётся
исходным. Владелец потом выкладывает их сам.
"""
import os, sys, json, glob, re

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import send_batch as SB

KARTA = os.path.join(HERE, "kanaly.json")
# По какому слову в названии канала понимаем язык. Два казахстанских канала
# различаем по слову «рус» - там ролики на русском для Казахстана.
# Порядок важен: «ibook.kz ( ru )» должен попасть в русский раньше, чем
# сработает признак «kz» и уведёт его в казахский канал.
PRIZNAK = [
    ("ru", ("kz ( ru", "kz(ru", "kz ru", "казах рус", "рус каз", "kazakhstan ru")),
    ("kk", ("қазақ", "казах", "kazakh", "kz")),
    ("rf", ("россия", "russia", "рф")),
    ("uk", ("украин", "ukrain")),
    ("uz", ("узбек", "uzbek", "o'zbek")),
    ("tr", ("турц", "turk", "türk")),
    ("zh", ("китай", "china", "中文")),
    ("en", ("english", "usa", "англ")),
    ("de", ("герман", "german", "deutsch")),
    ("it", ("итал", "ital")),
    ("es", ("испан", "spain", "españ")),
    ("fr", ("франц", "franc", "français")),
]
MESYAC = [("ЯНВАРЬ", 1, 4), ("ФЕВРАЛЬ", 5, 9), ("МАРТ", 10, 13), ("АПРЕЛЬ", 14, 17),
          ("МАЙ", 18, 22), ("ИЮНЬ", 23, 26), ("ИЮЛЬ", 27, 30), ("АВГУСТ", 31, 35),
          ("СЕНТЯБРЬ", 36, 39), ("ОКТЯБРЬ", 40, 43), ("НОЯБРЬ", 44, 48), ("ДЕКАБРЬ", 49, 52)]


def karta():
    return json.load(open(KARTA, encoding="utf-8")) if os.path.exists(KARTA) else {}


def opredelit(nazv):
    """Язык канала по его названию. Казахстанский русскоязычный проверяем первым,
    иначе слово «казах» в названии увело бы его в казахский канал."""
    n = (nazv or "").lower()
    for lang, slova in PRIZNAK:
        if any(s in n for s in slova):
            return lang
    return None


def cmd_naydi():
    d = SB.api("getUpdates", limit=100, timeout=0,
               allowed_updates=json.dumps(["my_chat_member","chat_member",
                                           "channel_post","message"]))
    k = karta()
    novyh = 0
    for u in d.get("result", []):
        for key in ("my_chat_member", "channel_post", "message"):
            v = u.get(key) or {}
            c = v.get("chat")
            f = v.get("forward_from_chat") or (v.get("forward_origin") or {}).get("chat")
            if f and f.get("type") == "channel":
                c = f
            if not c or c.get("type") not in ("channel", "supergroup", "group"):
                continue
            lang = opredelit(c.get("title"))
            if str(c["id"]) not in k:
                novyh += 1
            k[str(c["id"])] = {"nazvanie": c.get("title"), "lang": lang}
    json.dump(k, open(KARTA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if not k:
        print("Каналов не вижу. Добавь бота @ibook_videos_bot АДМИНИСТРАТОРОМ\n"
              "в каждый канал, потом запусти эту команду снова.")
        return
    print(f"каналов: {len(k)}, новых: {novyh}")
    for i, v in k.items():
        print(f"  {i}  {v['nazvanie']}  ->  {v['lang'] or 'ЯЗЫК НЕ ПОНЯЛ, впиши руками'}")


def cmd_karta():
    k = karta()
    if not k:
        print("карта пуста, запусти:  python kanaly.py найди"); return
    for i, v in sorted(k.items(), key=lambda x: x[1]["lang"] or "я"):
        print(f"  {str(v['lang']):4} {v['nazvanie']}  ({i})")


def razbor(imya):
    """Из имени файла достаём номер ролика и язык: «091-Казахстан-русский.mp4»."""
    m = re.match(r"(\d+)-([^-]+)-([^.]+)", imya)
    if not m:
        return None, None, None
    nom = int(m.group(1))
    ned = (nom - 1) // 3 + 1
    for name, a, b in MESYAC:
        if a <= ned <= b:
            return nom, name, (nom - (a - 1) * 3)
    return nom, "ГОД", nom


def cmd_shli(papka):
    import reel_engine as R
    k = karta()
    if not k:
        print("сначала:  python kanaly.py найди"); return
    po_yazyku = {}
    for i, v in k.items():
        if v.get("lang"):
            po_yazyku.setdefault(v["lang"], i)
    files = sorted(glob.glob(os.path.join(papka, "*.mp4")))
    print(f"роликов: {len(files)}")
    for f in files:
        imya = os.path.basename(f)
        nom, mes, vmes = razbor(imya)
        # язык берём из имени файла: там он записан по-русски
        lang = None
        for L, ru in R.LANGRU.items():
            if f"-{ru}." in imya:
                lang = L
                break
        chat = po_yazyku.get(lang)
        if not chat:
            print(f"  {imya}: нет канала для «{lang}», пропускаю"); continue
        card = None
        try:
            os.environ.update(SOURCE="year", WEEK=str((nom - 1) // 3 + 1),
                              SLOT="ABC"[(nom - 1) % 3])
            import importlib; importlib.reload(R)
            card = R.year_card(lang)
        except Exception:
            pass
        zag = card["title"] if card else imya
        opis = (card.get("caption") or "")[:350] if card else ""
        text = f"🗓 {mes} · ролик {vmes}\n\n{zag}\n\n{opis}"
        try:
            SB.send_file(chat, f, text, "document")
            print(f"  {imya} -> {k[chat]['nazvanie']}", flush=True)
        except Exception as e:
            print(f"  {imya}: не ушло — {str(e)[:90]}", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help", "помощь"): print(__doc__)
    elif a[0] == "найди": cmd_naydi()
    elif a[0] == "карта": cmd_karta()
    elif a[0] == "шли": cmd_shli(a[1])
    else: print("не знаю команду:", a[0]); print(__doc__)
