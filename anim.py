#!/usr/bin/env python3
"""
Оживление кадра ПРЯМО НА MAC. Без интернета, без норм, без подписки.

    python anim.py <кадр.png> <выход.mp4> "что должно двигаться"

Модель LTX-Video 2B (Lightricks). Лицензия разрешает бесплатное коммерческое
использование всем, у кого годовая выручка меньше 10 млн долларов - ibook под
это подходит с запасом.

Почему именно оживление готового кадра, а не рисование видео с нуля: модель,
которой дали текст, придумывает сцену сама и может уехать куда угодно (у нас
на запрос про парикмахера с ножницами вышел мужчина в песчаном поле). Когда
кадр задан, ей остаётся только его подвигать - промахнуться нечем.
"""
import os, sys, time

import torch
from diffusers import LTXImageToVideoPipeline
from diffusers.utils import export_to_video, load_image

MODEL = os.environ.get("LTX_MODEL", "Lightricks/LTX-Video")
# Кадр держим маленьким: на 16 ГБ общей памяти большее не считается, а
# растянуть до 1080x1920 можно потом, при сборке ролика.
W = int(os.environ.get("LTX_W", "384"))
H = int(os.environ.get("LTX_H", "672"))
FPS = 24
NEG = ("worst quality, inconsistent motion, blurry, jittery, distorted, "
       "deformed hands, extra fingers, text, watermark, static")


def main():
    png, out = sys.argv[1], sys.argv[2]
    what = sys.argv[3] if len(sys.argv) > 3 else "gentle natural movement, subtle breathing"
    sec = float(os.environ.get("SEC", "3"))
    # у LTX число кадров обязано быть кратно 8 плюс один
    nf = int(sec * FPS) // 8 * 8 + 1

    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"устройство: {dev}, кадр {W}x{H}, {nf} кадров", flush=True)
    t0 = time.time()
    pipe = LTXImageToVideoPipeline.from_pretrained(MODEL, torch_dtype=torch.bfloat16)
    pipe.to(dev)
    pipe.vae.enable_tiling()          # иначе декодер один съедает всю память
    print(f"модель загружена за {time.time()-t0:.0f} сек", flush=True)

    img = load_image(png).resize((W, H))
    t1 = time.time()
    frames = pipe(image=img, prompt=what, negative_prompt=NEG,
                  width=W, height=H, num_frames=nf,
                  num_inference_steps=int(os.environ.get("STEPS", "30")),
                  generator=torch.Generator().manual_seed(42)).frames[0]
    export_to_video(frames, out, fps=FPS)
    print(f"ГОТОВО за {(time.time()-t1)/60:.1f} мин -> {out}", flush=True)


if __name__ == "__main__":
    main()
