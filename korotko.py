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
# Сколько знаков произносится за секунду. Замерено на живой озвучке каждого
# языка. Китайский выбивается сильно: иероглиф несёт целое слово, поэтому
# знаков в секунду втрое меньше. С общей меркой в 360 знаков китайский ролик
# вышел бы на 32-38 секунд вместо двадцати, и его бы никто не досмотрел.
SKOROST = {"zh": 5.8, "ja": 6.5, "ko": 7.5,
           "ru": 14.5, "rf": 14.5, "kk": 15.2, "uk": 13.9, "uz": 14.5, "tr": 15.5,
           "en": 17.7, "de": 17.4, "fr": 17.8, "es": 15.5, "it": 15.5}
SEKUND = float(os.environ.get("KOR_SEKUND", "22"))


def znakov_dlya(lang):
    """Бюджет знаков под нужную длительность, по скорости речи языка."""
    if os.environ.get("KOR_ZNAKOV"):
        return ZNAKOV
    return int(SEKUND * SKOROST.get(lang, 14.5))
# Как узнать фразу-предложение. Раньше здесь были только русские, казахские и
# турецкие слова, а «\d» ловило цифры. Английские сценарии пишут «thirty days
# free» словами и «no commission» - ни одно из этого не совпадало, предложение
# выпадало, и ролик схлопывался до десяти секунд вместо двадцати пяти. Слова
# добавлены для всех языков, на которых мы работаем.
CIFRY = re.compile(
    r"\d"
    r"|бесплатн|тегін|бепул|комисси|тенге|месяц|ай\b"                    # рус, каз
    r"|free|commission|month|days|trial|cancel anytime|no fee"           # англ
    r"|kostenlos|Provision|Monat|Tage|jederzeit"                         # нем
    r"|gratuit|commission|mois|jours"                                    # фр
    r"|gratis|comisión|mes\b|días"                                       # исп
    r"|gratuito|commissione|mese|giorni"                                 # ит
    r"|ücretsiz|komisyon|\bay\b|gün"                                     # тур
    r"|免费|佣金|个月|天"                                                  # кит
    r"|безкоштовн|комісі|місяц|днів"                                     # укр
    r"|bepul|komissiya|oy\b|kun",                                        # узб
    re.I)


def frazy(t):
    return [f.strip() for f in re.split(r"(?<=[.!?])\s+", (t or "").strip()) if f.strip()]


def korotkiy(card, lang, cta):
    """Собираем короткую озвучку: боль, решение, предложение."""
    predel = znakov_dlya(lang)
    ff = frazy(card.get("vo", ""))
    if not ff:
        return ""
    bol = ff[0]                                   # первая фраза всегда боль
    # решение - первая фраза, где назван продукт
    resh = next((f for f in ff[1:] if re.search(r"ibook|айбук|aybuk|爱布克", f, re.I)), "")
    # предложение - фраза с цифрами или словом «бесплатно»
    predl = next((f for f in reversed(ff) if CIFRY.search(f) and f not in (bol, resh)), "")

    out = [x for x in (bol, resh, predl) if x]
    # Добираем текст до полного хронометража.
    #
    # Раньше добавлялась ровно ОДНА фраза, и этого хватало только там, где
    # предложения длинные. В английском они короткие: три куска давали сто
    # пятьдесят знаков, то есть десять секунд вместо двадцати пяти. Ролик
    # обрывался, не успев ничего продать.
    #
    # Теперь добираем по одной фразе в исходном порядке, пока есть место.
    # Порядок важен: мысль должна разворачиваться так, как её написали.
    mesto = predel - 20 - (len(cta.split(".")[0]) if cta else 0)
    for f in ff[1:]:
        if f in out:
            continue
        # Не влезла одна длинная фраза - пробуем следующую, а не бросаем добор.
        # С «break» тридцать один английский ролик так и оставался коротким:
        # место было, но первая же длинная фраза закрывала цикл.
        if sum(len(x) for x in out) + len(f) + 1 > mesto:
            continue
        out.insert(len(out) - 1 if predl and out[-1] == predl else len(out), f)
    # Если даже обязательные три фразы не влезают - режем середину.
    #
    # В китайском иероглиф несёт целое слово, и одна фраза там весит как три
    # европейских. Боль, решение и предложение вместе давали 190 знаков при
    # бюджете 127, и ролик выходил на 32 секунды. Первую фразу и предложение
    # трогать нельзя: это крючок и продажа. Значит убираем то, что между ними,
    # начиная с самого длинного.
    while len(out) > 2 and sum(len(x) for x in out) > mesto:
        seredina = out[1:-1]
        if not seredina:
            break
        out.remove(max(seredina, key=len))
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
