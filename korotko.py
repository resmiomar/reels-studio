#!/usr/bin/env python3
"""
Короткая версия озвучки: 25 секунд вместо сорока.

Сорок секунд в ленте не досматривают. Reels живёт по правилу: зацепил за первые
три секунды - смотрят дальше, не зацепил - пролистнули. Причём алгоритм смотрит
на ДОСМОТР: ролик на 25 секунд, который досмотрели, поднимается выше сорока-
секундного, который бросили на середине.

Строение короткого ролика:

    0-3 сек    БОЛЬ     одна фраза, узнаваемая до дрожи
    3-8 сек    ХУЖЕ     во что эта боль обходится
    8-18 сек   РЕШЕНИЕ  что делает ibook, конкретно
    18-25 сек  ПРЕДЛОЖЕНИЕ и куда идти

Из исходного текста берём первую фразу (там боль), фразу про ibook (там решение)
и предложение с цифрами. Остальное - развитие мысли, в коротком формате оно
только тянет время.

    python korotko.py 31 A ru        показать длинную и короткую версии
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("PROJECT", "ibook")

# Сколько знаков влезает в 25 секунд. Замерено на живой озвучке: около
# 14-15 знаков в секунду и у ElevenLabs, и у локальных голосов.
ZNAKOV = int(os.environ.get("KOR_ZNAKOV", "360"))
CIFRY = re.compile(r"\d|бесплатн|тегін|бепул|ücretsiz|免费|комисси|тенге|месяц|ай\b", re.I)


def frazy(t):
    return [f.strip() for f in re.split(r"(?<=[.!?])\s+", (t or "").strip()) if f.strip()]


def korotkiy(card, lang, cta):
    """Собираем короткую озвучку: боль, решение, предложение."""
    ff = frazy(card.get("vo", ""))
    if not ff:
        return ""
    bol = ff[0]                                   # первая фраза всегда боль
    # решение - первая фраза, где назван продукт
    resh = next((f for f in ff[1:] if re.search(r"ibook|айбук|aybuk|爱布克", f, re.I)), "")
    # предложение - фраза с цифрами или словом «бесплатно»
    predl = next((f for f in reversed(ff) if CIFRY.search(f) and f not in (bol, resh)), "")

    out = [x for x in (bol, resh, predl) if x]
    # если ещё осталось место - добавляем усиление боли, оно держит внимание
    if sum(len(x) for x in out) < ZNAKOV - 60 and len(ff) > 1:
        huzhe = next((f for f in ff[1:] if f not in out), "")
        if huzhe:
            out.insert(1, huzhe)
    t = " ".join(out)
    # призыв обязателен, но короткий: длинный съедает секунды впустую
    if cta:
        k = frazy(cta)[0]
        if k and k not in t:
            t = f"{t} {k}"
    return t


def dlya(week, slot, lang):
    os.environ.update(SOURCE="year", WEEK=str(week), SLOT=slot)
    import reel_engine as R
    import importlib; importlib.reload(R)
    card = R.year_card(lang)
    cta = R.cta_line(lang, card.get("aud", "master"))
    return card, korotkiy(card, lang, cta)


if __name__ == "__main__":
    w, s = sys.argv[1], sys.argv[2]
    lang = sys.argv[3] if len(sys.argv) > 3 else "ru"
    card, kor = dlya(w, s, lang)
    dl = card["vo"]
    print(f"{card['title']}\n")
    print(f"БЫЛО  {len(dl)} знаков ≈ {len(dl)/14.5:.0f} сек")
    print(f"  {dl}\n")
    print(f"СТАЛО {len(kor)} знаков ≈ {len(kor)/14.5:.0f} сек")
    print(f"  {kor}")
