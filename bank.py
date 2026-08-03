#!/usr/bin/env python3
"""
Банк кадров ibook - основа и для бесплатного пути, и для платного.

Смысл. В 156 сценариях года 780 планов, но РАЗНЫХ сцен там всего около сорока:
парикмахер с ножницами, маникюр крупным планом, клиент выбирает время в телефоне,
пустое кресло, довольный клиент у зеркала. Рисовать 780 кадров незачем - хватит
банка из сорока сцен в нескольких ракурсах, а ролики собираются из него.

Банк нужен обоим путям:
  бесплатный  - кадр оживляется движением камеры прямо на Mac
  платный     - тот же кадр отдаётся модели, и она его оживляет по-настоящему
В обоих случаях кадр СНАЧАЛА смотрит владелец. Поэтому промах вроде «мужчина
в песчаном поле» в ролик уже не попадёт: непринятый кадр туда просто не дойдёт.

    python bank.py рисуй            рисовать банк (долго, можно прерывать)
    python bank.py смотри           что уже нарисовано
"""
import os, sys, glob, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("PROJECT", "ibook")

import kadry as K
import risunok as Ri

BASE = os.environ.get("BANK", "/Volumes/T7/ibook/bank")
# Два типажа: «наш» и «европейский». Дробить мельче смысла нет - зритель считывает
# лицо как своё или чужое, а не по стране.
CAST = {"az": "Asian Kazakh", "eu": ""}
# Сколько ракурсов на сцену. Разные ракурсы одной сцены дают разнообразие
# в ленте, не требуя новых сцен.
RAKURS = [
    "medium shot, waist up",
    "close up on hands, shallow focus",
    "wide shot showing the whole room",
]


def prompts():
    """Описания для банка: сцена x типаж x ракурс."""
    out = {}
    for scene, d in K.SCENES.items():
        base = d["queries"][0]
        for ck, face in CAST.items():
            for i, r in enumerate(RAKURS):
                key = f"{scene}-{ck}-{i}"
                out[key] = ", ".join(x for x in (face, base, r, Ri.STYLE) if x)
    return out


def cmd_smotri():
    p = prompts()
    have = {os.path.basename(f)[:-4] for f in glob.glob(f"{BASE}/*.png")}
    print(f"нужно кадров: {len(p)}, нарисовано: {len(have & set(p))}")
    for scene in K.SCENES:
        n = sum(1 for k in p if k.startswith(scene + "-") and k in have)
        print(f"  {scene:16} {n}/{len(CAST)*len(RAKURS)}")


def cmd_risuy():
    p = prompts()
    os.makedirs(BASE, exist_ok=True)
    env = dict(os.environ)
    env.setdefault("HF_HOME", "/Volumes/T7/ibook/hf")
    env.setdefault("HUGGINGFACE_HUB_CACHE", "/Volumes/T7/ibook/hf")
    todo = [(k, v) for k, v in p.items() if not os.path.exists(f"{BASE}/{k}.png")]
    print(f"осталось нарисовать: {len(todo)} из {len(p)}", flush=True)
    for i, (k, prompt) in enumerate(todo, 1):
        out = f"{BASE}/{k}.png"
        subprocess.run([Ri.PY, "-m", Ri.MODEL, "--base-model", Ri.BASEM,
                        "--steps", Ri.STEPS, "--seed", str(abs(hash(k)) % 10 ** 6),
                        "--height", str(Ri.H), "--width", str(Ri.W),
                        "--output", out, "--prompt", prompt],
                       env=env, capture_output=True, text=True)
        print(f"  {i}/{len(todo)} {k} {'ok' if os.path.exists(out) else 'НЕ ВЫШЛО'}", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help", "помощь"): print(__doc__)
    elif a[0] in ("рисуй", "рисовать"): cmd_risuy()
    elif a[0] in ("смотри", "склад"): cmd_smotri()
    else: print("не знаю команду:", a[0]); print(__doc__)
