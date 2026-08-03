#!/usr/bin/env python3
"""
Оживление наших кадров через fal.ai. Оплата за использование, подписки нет.

    python fal_video.py баланс                  сколько денег на счету
    python fal_video.py смета <папка>           цена, НЕ ТРАТЯ ни цента
    python fal_video.py один <кадр.png>         ОДИН клип, самый дешёвый шаг
    python fal_video.py банк <папка>            оживить набор кадров
    python fal_video.py траты                   что уже потрачено

Деньги владельца ограничены, поэтому здесь всё построено вокруг одного правила:
НИ ОДНОГО ЛИШНЕГО ЗАПУСКА.

  1. Перед стартом считаем цену и сверяем с потолком (LIMIT, по умолчанию $1).
  2. Проверяем баланс - при нуле не дёргаем сервис впустую.
  3. Готовое не пересчитываем: файл на месте - пропускаем.
  4. Каждая трата пишется в расходную книгу, итог всегда виден.
  5. Пустой или битый ответ не считаем успехом и не удаляем кадр из очереди.

Оживляем ГОТОВЫЙ кадр, а не просим выдумать сцену: человек тогда один и тот же
во всех планах, а сцена гарантированно по сценарию.
Разрешение 480p - при сборке всё равно растягиваем до 1080x1920, а 1080p стоит
в пять раз дороже.
"""
import os, sys, json, time, glob, base64, subprocess, urllib.request

KEY_FILE = os.path.expanduser("~/.fal/key")
OUT = os.environ.get("FAL_OUT", "/Volumes/T7/ibook/fal")
KNIGA = os.path.join(OUT, "traty.json")          # расходная книга
SEC = float(os.environ.get("SEC", "4"))
LIMIT = float(os.environ.get("LIMIT", "1.0"))    # потолок на один запуск, $
W, H, FPS = 480, 864, 24                         # вертикально, 480p

MODELS = {
    "seedance": "fal-ai/bytedance/seedance/v1/lite/image-to-video",
    "wan": "fal-ai/wan-25-preview/image-to-video",
}
# Seedance берёт деньги за видео-токены, а не за секунды:
#   токены = ширина x высота x кадров/сек x длительность / 1024
#   1 000 000 токенов = $1.80
# Проверено на их примере: 720p 5 сек = $0.19 при обещанных $0.18.
def cena(sec=SEC, w=W, h=H, fps=FPS):
    return (w * h * fps * sec) / 1024 / 1e6 * 1.80


def key():
    if not os.path.exists(KEY_FILE):
        raise SystemExit("нет ключа fal.ai")
    return open(KEY_FILE).read().strip()


def balans():
    req = urllib.request.Request("https://rest.alpha.fal.ai/billing/user_balance",
                                 headers={"Authorization": f"Key {key()}"})
    try:
        return float(urllib.request.urlopen(req, timeout=25).read().decode().strip())
    except Exception:
        return None


def kniga_add(model, png, summa):
    os.makedirs(OUT, exist_ok=True)
    d = json.load(open(KNIGA)) if os.path.exists(KNIGA) else []
    d.append({"kadr": os.path.basename(png), "model": model, "usd": round(summa, 4)})
    json.dump(d, open(KNIGA, "w"), ensure_ascii=False, indent=1)
    return sum(x["usd"] for x in d)


def video_celiy(p):
    """Битый ответ бывает: файл есть, а видео в нём нет. Такое за успех не считаем."""
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries",
                        "format=duration", "-of", "csv=p=0", p],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip()) > 0.5
    except ValueError:
        return False


DVIZH = ("natural breathing, slow head movement, blinking, subtle hand motion, "
         "hair moves gently, soft realistic light, no camera shake")


def odin(model, png, dst):
    import fal_client
    os.environ["FAL_KEY"] = key()
    with open(png, "rb") as f:
        img = "data:image/png;base64," + base64.b64encode(f.read()).decode()
    # aspect_ratio задаём ЯВНО: по умолчанию сервис ставит auto и может отдать
    # горизонтальный кадр - для ленты это брак, а деньги уже списаны.
    r = fal_client.subscribe(MODELS[model], arguments={
        "image_url": img, "prompt": DVIZH,
        "resolution": "480p", "duration": str(int(SEC)),
        "aspect_ratio": "9:16",
        "camera_fixed": False,          # пусть камера живёт, а не стоит колом
    })
    url = (r.get("video") or {}).get("url") or r.get("url")
    if not url:
        raise RuntimeError(f"сервис не вернул видео: {str(r)[:180]}")
    with urllib.request.urlopen(url, timeout=300) as s, open(dst + ".part", "wb") as f:
        f.write(s.read())
    os.replace(dst + ".part", dst)
    if not video_celiy(dst):
        raise RuntimeError("пришёл битый файл")
    return dst


def proverka(n):
    """Что-либо запускаем только если это по деньгам и по потолку."""
    nado = cena() * n
    b = balans()
    print(f"  клипов: {n}, цена ~${nado:.2f}, потолок ${LIMIT:.2f}, баланс ${b if b is not None else '?'}")
    if nado > LIMIT + 1e-9:
        raise SystemExit(f"СТОП: ${nado:.2f} больше потолка ${LIMIT:.2f}. "
                         f"Подними его осознанно: LIMIT={nado:.2f} ...")
    if b is not None and b < nado:
        raise SystemExit(f"СТОП: на счету ${b:.2f}, нужно ${nado:.2f}. Пополни баланс.")


def cmd_balans():
    b = balans()
    print(f"баланс: ${b:.2f}" if b is not None else "баланс узнать не вышло")


def cmd_smeta(papka):
    n = len(glob.glob(f"{papka}/*.png"))
    print(f"кадров: {n}, по {SEC:.0f} сек, 480p")
    print(f"  один клип   ${cena():.3f}")
    print(f"  всего       ${cena()*n:.2f}")


def cmd_traty():
    if not os.path.exists(KNIGA):
        print("трат ещё не было"); return
    d = json.load(open(KNIGA))
    print(f"клипов оплачено: {len(d)}, итого ${sum(x['usd'] for x in d):.2f}")


def cmd_odin(png):
    model = os.environ.get("MODEL", "seedance")
    os.makedirs(OUT, exist_ok=True)
    dst = f"{OUT}/{model}-{os.path.basename(png)[:-4]}.mp4"
    if os.path.exists(dst):
        print("уже есть, не плачу заново:", dst); return
    proverka(1)
    t0 = time.time()
    odin(model, png, dst)
    itogo = kniga_add(model, png, cena())
    print(f"готов за {time.time()-t0:.0f} сек -> {dst}")
    print(f"списано ~${cena():.3f}, всего потрачено ~${itogo:.2f}")


def cmd_bank(papka):
    model = os.environ.get("MODEL", "seedance")
    kadry = [p for p in sorted(glob.glob(f"{papka}/*.png"))
             if not os.path.exists(f"{OUT}/{model}-{os.path.basename(p)[:-4]}.mp4")]
    if not kadry:
        print("всё уже оживлено, платить не за что"); return
    proverka(len(kadry))
    os.makedirs(OUT, exist_ok=True)
    itogo = 0
    for i, png in enumerate(kadry, 1):
        dst = f"{OUT}/{model}-{os.path.basename(png)[:-4]}.mp4"
        try:
            odin(model, png, dst)
            itogo = kniga_add(model, png, cena())
            print(f"  {i}/{len(kadry)} {os.path.basename(dst)}  всего ~${itogo:.2f}", flush=True)
        except Exception as e:
            print(f"  {i}/{len(kadry)} НЕ ВЫШЛО: {str(e)[:130]}", flush=True)
    print(f"итого потрачено ~${itogo:.2f}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help", "помощь"): print(__doc__)
    elif a[0] == "баланс": cmd_balans()
    elif a[0] == "смета": cmd_smeta(a[1])
    elif a[0] == "один": cmd_odin(a[1])
    elif a[0] == "банк": cmd_bank(a[1])
    elif a[0] == "траты": cmd_traty()
    else: print("не знаю команду:", a[0]); print(__doc__)
