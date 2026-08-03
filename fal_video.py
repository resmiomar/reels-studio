#!/usr/bin/env python3
"""
Оживление наших кадров через платный сервис (fal.ai). Оплата за использование,
подписки нет: деньги уходят только за то, что реально посчитано.

    python fal_video.py проба <кадр.png>        одна сцена на двух моделях, сравнить
    python fal_video.py банк <папка_кадров>     оживить весь банк
    python fal_video.py смета <папка_кадров>    посчитать цену, ничего не тратя

Оживляем ГОТОВЫЙ кадр, а не просим выдумать сцену. Так человек в кадре один и
тот же во всех планах, и сцена гарантированно совпадает со сценарием - модель
ничего не придумывает. Выдумывание с нуля мы уже пробовали: на запрос про
парикмахера с ножницами пришёл мужчина в песчаном поле.

Разрешение берём 480p и растягиваем до 1080x1920 при сборке. Платить за 1080p,
чтобы потом всё равно пережимать, смысла нет - разница в цене восьмикратная.
"""
import os, sys, json, time, glob, urllib.request, base64

KEY_FILE = os.path.expanduser("~/.fal/key")
OUT = os.environ.get("FAL_OUT", "/Volumes/T7/ibook/fal")
SEC = float(os.environ.get("SEC", "4"))

# Цена за секунду по опубликованным тарифам. Проверяем по факту первым запуском:
# счёт всегда важнее прайс-листа.
MODELS = {
    "seedance": {"id": "fal-ai/bytedance/seedance/v1/lite/image-to-video",
                 "cena": 0.04, "opis": "Seedance, 1 место по движению"},
    "wan":      {"id": "fal-ai/wan-25-preview/image-to-video",
                 "cena": 0.05, "opis": "Wan 2.5, запасной"},
}


def key():
    if not os.path.exists(KEY_FILE):
        raise SystemExit(f"нет ключа. Создай его на fal.ai и сохрани:\n"
                         f"  mkdir -p ~/.fal && printf '%s' 'КЛЮЧ' > {KEY_FILE} && chmod 600 {KEY_FILE}")
    return open(KEY_FILE).read().strip()


def zapros(model, png, prompt):
    """Отправляем кадр и ждём готовое видео."""
    import fal_client
    os.environ["FAL_KEY"] = key()
    with open(png, "rb") as f:
        data = "data:image/png;base64," + base64.b64encode(f.read()).decode()
    r = fal_client.subscribe(MODELS[model]["id"], arguments={
        "image_url": data, "prompt": prompt,
        "resolution": os.environ.get("RES", "480p"),
        "duration": str(int(SEC)),
    })
    url = (r.get("video") or {}).get("url") or r.get("url")
    if not url:
        raise RuntimeError(f"сервис не вернул видео: {str(r)[:200]}")
    return url


def skachat(url, dst):
    with urllib.request.urlopen(url, timeout=300) as r, open(dst + ".part", "wb") as f:
        f.write(r.read())
    os.replace(dst + ".part", dst)
    return dst


DVIZH = ("natural breathing, slow head movement, blinking, subtle hand motion, "
         "hair moves gently, soft realistic light, no camera shake")


def cmd_proba(png):
    """Один кадр на обеих моделях - чтобы выбрать не по обзорам, а по глазам."""
    os.makedirs(OUT, exist_ok=True)
    for m in MODELS:
        dst = f"{OUT}/proba-{m}.mp4"
        t0 = time.time()
        try:
            skachat(zapros(m, png, DVIZH), dst)
            print(f"  {m:9} готов за {time.time()-t0:.0f} сек, "
                  f"примерно ${MODELS[m]['cena']*SEC:.2f} -> {dst}", flush=True)
        except Exception as e:
            print(f"  {m:9} не вышло: {str(e)[:160]}", flush=True)


def cmd_smeta(papka):
    """Сколько будет стоить, БЕЗ единой траты."""
    kadry = sorted(glob.glob(f"{papka}/*.png"))
    print(f"кадров: {len(kadry)}, по {SEC:.0f} сек каждый")
    for m, d in MODELS.items():
        print(f"  {m:9} {len(kadry)*SEC*d['cena']:7.2f} $   ({d['opis']})")


def cmd_bank(papka):
    model = os.environ.get("MODEL", "seedance")
    kadry = sorted(glob.glob(f"{papka}/*.png"))
    os.makedirs(OUT, exist_ok=True)
    itogo = 0.0
    for i, png in enumerate(kadry, 1):
        dst = f"{OUT}/{os.path.basename(png)[:-4]}.mp4"
        if os.path.exists(dst):
            continue
        try:
            skachat(zapros(model, png, DVIZH), dst)
            itogo += MODELS[model]["cena"] * SEC
            print(f"  {i}/{len(kadry)} {os.path.basename(dst)}  потрачено ~${itogo:.2f}", flush=True)
        except Exception as e:
            print(f"  {i}/{len(kadry)} не вышло: {str(e)[:120]}", flush=True)
    print(f"итого примерно ${itogo:.2f}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help", "помощь"): print(__doc__)
    elif a[0] == "проба": cmd_proba(a[1])
    elif a[0] == "смета": cmd_smeta(a[1])
    elif a[0] == "банк": cmd_bank(a[1])
    else: print("не знаю команду:", a[0]); print(__doc__)
