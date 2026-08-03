#!/usr/bin/env python3
"""
Сборка ПОДРОБНОГО задания для модели. Главный вывод дня: беда была не в модели,
а в том, что мы ей говорили.

Сценарии писались для живого оператора: «камера медленно наезжает через плечо,
мама нетерпеливо ждёт, дети бегают». Человек это снимет. Модель читает буквально:
рисует камеру в кадре, срастает головы, и картинка перестаёт совпадать с текстом.

Здесь задание собирается по ЖЁСТКОЙ структуре, по-английски, одним абзацем:

    КТО      возраст, внешность под рынок, профессия
    ЧТО ДЕЛАЕТ  одно понятное действие, без второго одновременного
    ГДЕ      место и предметы, которые должны попасть в кадр
    ЛИЦО     что выражает - это связывает картинку со смыслом фразы
    СВЕТ     время суток и характер света
    СЪЁМКА   плёнка, глубина резкости - чтобы вышло фото, а не рисунок
    НЕЛЬЗЯ   текст, вывески, второй человек, камера в кадре

Порядок не случайный: модель сильнее держит то, что стоит в начале, поэтому
человек и его действие идут первыми, а стиль - в конце.

    python promt.py 32 A kk        показать задания для всех кадров недели
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("PROJECT", "ibook")

# КТО в кадре, подробно. От короткого «Asian Kazakh» типаж плавал: в одном кадре
# казашка, в соседнем европейка - модели нужны приметы, а не название народа.
KTO = {
 "kk": "a 27-year-old Kazakh woman with straight black hair and warm light-tan skin, Central Asian features",
 "ru": "a 27-year-old Kazakh woman with straight black hair and warm light-tan skin, Central Asian features",
 "uz": "a 27-year-old Uzbek woman with dark hair and warm skin tone, Central Asian features",
 "tr": "a 27-year-old Turkish woman with dark wavy hair and olive skin",
 "rf": "a 27-year-old Slavic woman with light brown hair and fair skin",
 "uk": "a 27-year-old Slavic woman with light brown hair and fair skin",
 "zh": "a 27-year-old Chinese woman with straight black hair",
}
KTO_DEF = "a 27-year-old woman"
MUZH = ("barber", "barbershop", "mens haircut", "beard", "shave")

# Операторский жаргон: модель рисует его буквально, вплоть до камеры в кадре.
JARGON = re.compile(
    r"\b(?:extreme\s+)?close[- ]up(?:\s+(?:of|on))?\b"
    r"|\b(?:medium|wide|overhead|static)\s+(?:close[- ]up|shot)\b"
    r"|\bhandheld(?:\s+camera)?(?:\s+\w+ing)?\b"
    r"|\bcamera\s+\w+[^,]*|\bslow\s+(?:push\s+in|motion|arc)\b"
    r"|\bpush(?:es|ing)?\s+in\b|\bno\s+(?:text|logos?|watermark)\b", re.I)
# Толпа и второй человек: на них у модели срастаются головы и руки.
TOLPA = re.compile(r"\b(?:three|four|several|a\s+group\s+of|a\s+crowd\s+of)\s+\w+[^,]*"
                   r"|\bkids?\s+run\w*[^,]*|\banother\s+\w+[^,]*", re.I)
# Что на экране телефона - не рисуем: интерфейс ibook модель не знает и даёт кашу.
EKRAN = re.compile(r"\b(?:showing|with)\s+a?\s*(?:neat\s+)?"
                   r"(?:schedule|calendar|appointments?|list|messages?)[^,]*", re.I)

SEMKA = ("photorealistic candid documentary photo, shot on 35mm film, "
         "shallow depth of field, natural light, realistic skin texture")
# Что модель ломает чаще всего - руки и экраны. Запрет пишем ПОДРОБНО и в конце:
# короткое «no text» она пропускает мимо, а перечисление держит.
NELZYA = ("anatomically correct hands with exactly five fingers, "
          "no extra fingers, no fused fingers, no deformed hands, "
          "no text, no letters, no numbers, no signage, no posters, no watermark, "
          "single person in focus")
# Телефон разворачиваем экраном ОТ камеры. Интерфейс ibook модель не знает и
# рисует кашу из значков - в рекламе приложения это худшее, что может быть.
TELEFON = ("phone held with the screen turned away from the camera, "
           "screen not visible")
# Где руки не нужны по смыслу - убираем их из кадра совсем. Меньше рук -
# меньше шансов получить шесть пальцев.
BEZ_RUK = "hands out of frame, framed from the shoulders up"


def dejstvie(prompt):
    """Оставляем действие, убираем то, на чём модель ломается."""
    p = JARGON.sub("", prompt)
    p = TOLPA.sub("", p)
    p = EKRAN.sub("", p)
    p = re.sub(r"^same\s+", "", p.strip(), flags=re.I)
    p = re.sub(r"\s*,\s*(?=,)", "", p)
    return " ".join(p.split()).strip(" ,.")


def zadanie(shot, lang):
    """Одно задание для модели: кто, что делает, где, с каким лицом, при каком свете."""
    body = dejstvie(shot.get("prompt", ""))
    kto = KTO.get(lang, KTO_DEF)
    if any(m in body.lower() for m in MUZH):
        kto = kto.replace("woman", "man")
    # Заменяем безличные «she/artist/stylist» в начале на подробное описание,
    # иначе модель берёт усреднённое лицо из обучения.
    body = re.sub(r"^(?:the\s+)?(?:brow|lash|nail)?\s*(?:artist|stylist|hairdresser|"
                  r"technician|she|he|woman|man)\b", "", body, flags=re.I).strip(" ,")
    dop = []
    if re.search(r"\bphone|smartphone\b", body, re.I):
        dop.append(TELEFON)
    # Руки нужны, только когда они и есть действие: работает, листает, держит.
    if not re.search(r"\bhand|holding|flipping|working|opening|typing|cutting|"
                     r"scissors|tweezers|brush\b", body, re.I):
        dop.append(BEZ_RUK)
    return ", ".join([kto, body] + dop + [SEMKA, NELZYA])


def dlya_nedeli(week, slot, lang):
    os.environ.update(SOURCE="year", WEEK=str(week), SLOT=slot)
    import reel_engine as R
    card = R.year_card(lang)
    return card, [zadanie(sh, lang) for sh in card["shots"]]


if __name__ == "__main__":
    w, s = sys.argv[1], sys.argv[2]
    lang = sys.argv[3] if len(sys.argv) > 3 else "kk"
    card, zz = dlya_nedeli(w, s, lang)
    print(f"{card['title']}\n")
    for i, (sh, z) in enumerate(zip(card["shots"], zz)):
        print(f"[{i}] {sh['sec']} сек · на экране: {sh.get('screen','')}")
        print(f"    {z}\n")
