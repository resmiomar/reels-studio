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
import os, sys, json, subprocess, hashlib, random

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
FACE = {"kk": "Asian Kazakh", "ru": "Asian Kazakh", "uz": "Asian Uzbek",
        "tr": "Turkish", "rf": "Slavic", "uk": "Slavic", "zh": "Chinese",
        "en": "", "de": "", "it": "", "es": "", "fr": ""}
# Что дописываем к каждому описанию, чтобы кадр выглядел снятым, а не нарисованным
STYLE = ("photorealistic, shot on 35mm film, shallow depth of field, natural light, "
         "candid documentary photography, no text, no logos, no watermark")
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


def clean(prompt):
    """Убираем из описания движение камеры: рисуем неподвижный кадр, движение
    добавим потом монтажом. Модель иначе пытается нарисовать сам приём."""
    p = prompt
    for d in DROP:
        p = p.replace(d, "")
    p = " ".join(p.split()).strip(" ,.")
    # описание длиннее 300 знаков модель уже не удерживает целиком
    return p[:300]


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
    full = ", ".join(x for x in (FACE.get(lang, ""), clean(prompt), STYLE) if x)
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


def ozhivit(png, out, sec=3.5, fps=30, move=None):
    """Оживляем неподвижный кадр движением камеры.

    Наезд, отъезд или проезд вбок. Держим движение медленным: заметное движение
    на статичной картинке сразу выдаёт приём, а еле уловимое читается как съёмка
    с рук. Картинку сперва растягиваем с запасом, чтобы движению было куда идти.
    """
    move = move or random.choice(["in", "out", "left", "right"])
    n = int(sec * fps)
    big = f"{W*3}x{H*3}"                      # запас на плавность масштабирования
    z = {"in": f"min(1.12,1+0.12*on/{n})", "out": f"max(1.0,1.12-0.12*on/{n})"}
    if move in z:
        expr = (f"zoompan=z='{z[move]}':d={n}:s=1080x1920:fps={fps}"
                f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'")
    else:
        d = 1 if move == "right" else -1
        expr = (f"zoompan=z='1.14':d={n}:s=1080x1920:fps={fps}"
                f":x='iw/2-(iw/zoom/2)+{d}*(on/{n}-0.5)*iw*0.06'"
                f":y='ih/2-(ih/zoom/2)'")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", png,
                    "-vf", f"scale={big},{expr},unsharp=5:5:0.5",
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
