#!/usr/bin/env python3
"""
Рисованные кадры для роликов ibook.

Сток даёт «примерно про то же», а рисованный кадр делается ровно по описанию из
сценария. Плюс такого снимка не существует нигде, и Instagram не может счесть его
дублем - у стока эта беда постоянная, потому что конкуренты качают те же клипы.

    python risunok.py кадр "описание сцены" kk       нарисовать один кадр
    python risunok.py ролик 32 A ru                  нарисовать все кадры недели
    python risunok.py склад                          что уже нарисовано

Картинка статичная, поэтому в ролике ей задаётся движение камеры: медленный
наезд, отъезд или проезд вбок. На трёх-четырёх секундах это неотличимо от
съёмки с рук.
"""
import os, sys, json, subprocess, hashlib, random, re

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("PROJECT", "ibook")

BASE = os.environ.get("RISUNKI", "/Volumes/T7/ibook/risunki")
INDEX = os.path.join(BASE, "index.json")
PY = os.path.expanduser("~/kadr-gen/.venv/bin/mflux-generate")
# Свободная копия FLUX.1-schnell: та же модель и та же лицензия Apache, но
# официальный склад закрыт за регистрацией, а этот открыт. Уже пожата под
# Apple Silicon - 9 ГБ вместо 25.
MODEL = os.environ.get("RIS_MODEL", "dhairyashil/FLUX.1-schnell-mflux-4bit")
BASEM = os.environ.get("RIS_BASE", "schnell")
STEPS = os.environ.get("RIS_STEPS", "4")
W, H = 576, 1024          # больше не влезает в 16 ГБ памяти

# Внешность под рынок. Ролик для Алматы с европейской моделью читается как
# чужая реклама и не продаёт.
# Внешность описываем ПОДРОБНО. От короткого «Asian Kazakh» типаж плавал:
# в одном кадре казашка, в соседнем европейка. Модели нужны приметы - возраст,
# волосы, черты лица, - иначе она берёт усреднённое лицо из обучения.
FACE = {
 "kk": "young Kazakh woman 25-30 years old, straight black hair, warm light-tan skin, Central Asian facial features",
 "ru": "young Kazakh woman 25-30 years old, straight black hair, warm light-tan skin, Central Asian facial features",
 "uz": "young Uzbek woman 25-30 years old, dark hair, warm skin tone, Central Asian facial features",
 "tr": "young Turkish woman 25-30 years old, dark wavy hair, olive skin",
 "rf": "young Slavic woman 25-30 years old, light brown hair, fair skin",
 "uk": "young Slavic woman 25-30 years old, light brown hair, fair skin",
 "zh": "young Chinese woman 25-30 years old, straight black hair",
 "en": "young woman 25-30 years old", "de": "young woman 25-30 years old",
 "it": "young woman 25-30 years old", "es": "young woman 25-30 years old",
 "fr": "young woman 25-30 years old"}
# Если в сцене мужской мастер - подставляем мужчину того же типажа
FACE_M = {k: v.replace("woman", "man").replace("Kazakh man", "Kazakh man")
          for k, v in FACE.items()}
MUZH = ("barber", "barbershop", "mens haircut", "beard", "shave", "male")
# Что дописываем к каждому описанию, чтобы кадр выглядел снятым, а не нарисованным
# Слова «no text» модель понимает плохо и часто рисует вывеску назло. Надёжнее
# описать стены и фон ПУСТЫМИ - тогда писать буквы просто негде.
STYLE = ("photorealistic, shot on 35mm film, shallow depth of field, natural light, "
         "candid documentary photography, plain clean walls, blank surfaces, "
         "no signage, no lettering, no posters")
# Чего в кадре быть не должно: киножаргон модель понимает буквально и рисует
# камеру внутри кадра
DROP = ("camera slowly", "camera pushes", "camera arcs", "camera drifts", "push in",
        "handheld", "slow motion", "static shot", "wide shot", "close up of",
        "extreme close up", "overhead shot", "no text", "no logos")


def load_index():
    return json.load(open(INDEX, encoding="utf-8")) if os.path.exists(INDEX) else {}


def save_index(ix):
    os.makedirs(BASE, exist_ok=True)
    tmp = INDEX + ".part"
    json.dump(ix, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, INDEX)


# Из описания вырезаем ТОЛЬКО операторский жаргон - точечно, внутри фразы.
# Выбрасывать кусок целиком нельзя: в нём сидит само ДЕЙСТВИЕ, ради которого
# кадр и снимается. Так у нас пропало «рука открывает расписание в телефоне» и
# «мастер работает с бровями клиента», а остались одни портреты - девушка просто
# красиво смотрит в камеру, и к тексту это не имеет отношения.
KAMERA = re.compile(
    r"\b(?:extreme\s+)?close[- ]up(?:\s+(?:of|on))?\b"
    r"|\bmedium\s+(?:close[- ]up|shot)\b|\bwide\s+shot\b|\boverhead\s+shot\b"
    r"|\bhandheld(?:\s+camera)?(?:\s+\w+ing)?\b"
    r"|\bcamera\s+(?:slowly\s+)?\w+(?:s|ing)?\b[^,]*"
    r"|\bslow\s+(?:push\s+in|motion|arc)\b|\bpush(?:es|ing)?\s+in\b"
    r"|\bstatic\s+shot\b|\bno\s+text\b|\bno\s+logos?\b|\bno\s+watermark\b",
    re.I)
# Толпа модели не даётся: головы и руки срастаются. Её убираем, действие - нет.
TOLPA = re.compile(r"\b(?:three|four|several|a\s+group\s+of|a\s+crowd\s+of)\s+\w+[^,]*"
                   r"|\bkids?\s+run\w*[^,]*", re.I)
# Экран телефона модель рисует каракулями: интерфейса ibook она не знает.
# Само действие «открывает телефон» оставляем, а вот ЧТО на экране - убираем.
EKRAN = re.compile(r"\b(?:showing|with)\s+a?\s*(?:neat\s+)?(?:schedule|calendar|"
                   r"appointments?|list)[^,]*", re.I)

GEROY = re.compile(r"\b(hairdresser|stylist|barber|colou?rist|nail (artist|technician)|"
                   r"manicurist|brow artist|lash (artist|technician)|beautician|"
                   r"cosmetologist|esthetician|makeup artist|massage therapist|masseuse|"
                   r"therapist|dentist|doctor|salon owner|apprentice|"
                   r"boy|girl|woman|man|artist|technician|she|he|her|his)\b", re.I)


def clean(prompt):
    """Готовим описание сцены для модели, СОХРАНЯЯ действие.

    Убираем только то, что модель понимает буквально и рисует внутри кадра:
    названия планов, движения камеры, толпу, содержимое экрана. Всё остальное -
    кто, что делает, где, с каким лицом - остаётся, иначе видео перестаёт
    совпадать с озвучкой.
    """
    p = KAMERA.sub("", prompt)
    p = TOLPA.sub("", p)
    p = EKRAN.sub("", p)
    p = re.sub(r"\s*,\s*(?=,)", "", p)
    p = re.sub(r"\s{2,}", " ", p)
    p = " ".join(p.split()).strip(" ,.")
    # «Same artist» без предыдущего кадра модель не понимает - называем профессию
    p = re.sub(r"^same\s+", "", p, flags=re.I)
    if not GEROY.search(p):
        kto = GEROY.search(prompt)
        p = f"{kto.group(0) if kto else 'hairdresser'} in a bright modern salon, " + p
    return p[:320]


def key_of(prompt, lang):
    return hashlib.md5(f"{FACE.get(lang,'')}|{clean(prompt)}".encode()).hexdigest()[:12]


def draw(prompt, lang="ru", seed=None, force=False):
    """Кадр по описанию. Уже нарисованное не пересчитываем: полторы минуты за кадр."""
    ix = load_index()
    k = key_of(prompt, lang)
    if not force and k in ix and os.path.exists(ix[k]["path"]):
        return ix[k]["path"]
    os.makedirs(BASE, exist_ok=True)
    out = os.path.join(BASE, f"{k}.png")
    body = clean(prompt)
    face = (FACE_M if any(m in body.lower() for m in MUZH) else FACE).get(lang, "")
    full = ", ".join(x for x in (face, body, STYLE) if x)
    env = dict(os.environ)
    env.setdefault("HF_HOME", "/Volumes/T7/ibook/hf")
    env.setdefault("HUGGINGFACE_HUB_CACHE", "/Volumes/T7/ibook/hf")
    cmd = [PY, "-m", MODEL, "--base-model", BASEM, "--steps", STEPS,
           "--seed", str(seed if seed is not None else random.randint(1, 10 ** 6)),
           "--height", str(H), "--width", str(W), "--output", out, "--prompt", full]
    subprocess.run(cmd, env=env, capture_output=True, text=True)
    if not os.path.exists(out):
        return None
    ix[k] = {"path": out, "lang": lang, "prompt": full[:200]}
    save_index(ix)
    return out


def ozhivit(png, out, sec=3.5, fps=30, move=None, plan="wide"):
    """Оживляем неподвижный кадр движением камеры.

    plan задаёт крупность: из одной картинки так получается несколько РАЗНЫХ
    планов - общий, поясной, крупный, - и ролик собирается только из своих
    кадров, без чужого стока.

    Движение держим внутри картинки. Раньше камера уезжала за край и в кадре
    оставалась голая стена без человека - самый заметный брак прошлой сборки.
    Лицо в вертикальном кадре сидит выше центра, поэтому крупные планы
    смещаем вверх, а не по геометрическому центру.
    """
    move = move or random.choice(["in", "out", "left", "right"])
    n = max(2, int(sec * fps))
    # доля картинки, попадающая в кадр, и куда смещаем окно по вертикали
    KRUP = {"wide": (1.00, 0.50), "medium": (0.78, 0.42), "close": (0.58, 0.34)}
    frac, ycen = KRUP.get(plan, KRUP["wide"])
    # исходник растягиваем ровно настолько, чтобы вырезаемое окно давало 1080x1920
    sw, sh = int(1080 / frac), int(1920 / frac)
    z0, z1 = (1.0, 1.10) if move == "in" else (1.10, 1.0) if move == "out" else (1.06, 1.06)
    zexpr = f"{z0}+({z1}-{z0})*on/{n}"
    # запас, на который можно двигать окно, не вылезая за картинку
    if move in ("left", "right"):
        d = 1 if move == "right" else -1
        xexpr = f"(iw-iw/zoom)/2+{d}*(on/{n}-0.5)*(iw-iw/zoom)*0.7"
    else:
        xexpr = "(iw-iw/zoom)/2"
    yexpr = f"(ih-ih/zoom)*{ycen}"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", png,
                    "-vf", (f"scale={sw}:{sh}:flags=lanczos,"
                            f"zoompan=z='{zexpr}':d={n}:s=1080x1920:fps={fps}"
                            f":x='{xexpr}':y='{yexpr}',unsharp=5:5:0.4"),
                    "-t", f"{sec:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "18", "-preset", "medium", out], check=False)
    return out if os.path.exists(out) else None


def cmd_kadr(prompt, lang="ru"):
    p = draw(prompt, lang)
    print("нарисовано:", p or "не вышло")


def cmd_rolik(week, slot, lang):
    os.environ.update(SOURCE="year", WEEK=str(week), SLOT=slot)
    import reel_engine as R
    card = R.year_card(lang)
    print(f"{card['title']} — кадров {len(card['shots'])}")
    for i, sh in enumerate(card["shots"]):
        p = draw(sh["prompt"], lang)
        print(f"  [{i}] {'ok' if p else 'НЕ ВЫШЛО'}  {clean(sh['prompt'])[:70]}")


def cmd_sklad():
    ix = load_index()
    print(f"нарисовано кадров: {len(ix)}")
    gb = sum(os.path.getsize(v["path"]) for v in ix.values()
             if os.path.exists(v["path"])) / 1e9
    print(f"занимают: {gb:.2f} ГБ")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help", "помощь"): print(__doc__)
    elif a[0] == "кадр": cmd_kadr(a[1], a[2] if len(a) > 2 else "ru")
    elif a[0] == "ролик": cmd_rolik(a[1], a[2], a[3] if len(a) > 3 else "ru")
    elif a[0] == "склад": cmd_sklad()
    else: print("не знаю команду:", a[0]); print(__doc__)
