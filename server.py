#!/usr/bin/env python3
"""
Полный ролик через сервер: кадры, движение, сборка, отправка в Telegram.

    python server.py ролик 31 A kk        один ролик целиком
    python server.py смета 31 A           цена, не тратя ни цента

Что где считается и почему:
    кадры      сервер   2 секунды вместо 6 минут на Mac, дешевле цента
    движение   сервер   $0.07 за клип, локально его просто нет
    голос      Mac      бесплатно, 12 языков
    монтаж     Mac      бесплатно
    отправка   Telegram бесплатно

Купленное складывается на внешний диск НАВСЕГДА. Второй раз за те же кадры и
клипы деньги не берутся: файл на месте - шаг пропускается. Это главное правило,
потому что деньги владельца ограничены.
"""
import os, sys, glob, json, time, base64, subprocess, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("PROJECT", "ibook")

BASE = os.environ.get("SRV_BASE", "/Volumes/T7/ibook/srv")
LIMIT = float(os.environ.get("LIMIT", "1.5"))
SEC = float(os.environ.get("SEC", "4"))
FLUX = "fal-ai/flux/schnell"
VIDEO = "fal-ai/bytedance/seedance/v1/lite/image-to-video"


def key():
    return open(os.path.expanduser("~/.fal/key")).read().strip()


def balans():
    try:
        r = urllib.request.Request("https://rest.alpha.fal.ai/billing/user_balance",
                                   headers={"Authorization": f"Key {key()}"})
        return float(urllib.request.urlopen(r, timeout=25).read().decode().strip())
    except Exception:
        return None


def skachat(url, dst):
    with urllib.request.urlopen(url, timeout=300) as s, open(dst + ".part", "wb") as f:
        f.write(s.read())
    os.replace(dst + ".part", dst)
    return dst


def kadr(prompt, dst):
    """Картинка на сервере. Стоит доли цента, считается пару секунд."""
    if os.path.exists(dst):
        return dst
    import fal_client
    os.environ["FAL_KEY"] = key()
    r = fal_client.subscribe(FLUX, arguments={
        "prompt": prompt, "image_size": {"width": 576, "height": 1024},
        "num_inference_steps": 4, "num_images": 1})
    return skachat(r["images"][0]["url"], dst)


DVIZH = ("natural breathing, slow head movement, blinking, subtle hand motion, "
         "hair moves gently, soft realistic light, no camera shake")


def klip(png, dst):
    """Движение из готового кадра. Формат задаём явно - иначе сервис может
    вернуть горизонтальный кадр, а деньги уже списаны."""
    if os.path.exists(dst):
        return dst
    import fal_client
    os.environ["FAL_KEY"] = key()
    with open(png, "rb") as f:
        img = "data:image/png;base64," + base64.b64encode(f.read()).decode()
    r = fal_client.subscribe(VIDEO, arguments={
        "image_url": img, "prompt": DVIZH, "resolution": "480p",
        "duration": str(int(SEC)), "aspect_ratio": "9:16", "camera_fixed": False})
    url = (r.get("video") or {}).get("url") or r.get("url")
    if not url:
        raise RuntimeError(f"сервис не вернул видео: {str(r)[:150]}")
    skachat(url, dst)
    d = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                        "-of", "csv=p=0", dst], capture_output=True, text=True).stdout.strip()
    if not d or float(d) < 0.5:
        os.remove(dst)
        raise RuntimeError("пришёл битый файл, за него не платим дважды")
    return dst


def do_1080(src, dst):
    if os.path.exists(dst):
        return dst
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src,
                    "-vf", "scale=1080:1944:flags=lanczos,crop=1080:1920,unsharp=5:5:0.6",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                    "-preset", "medium", "-an", dst], check=False)
    return dst


def opisaniya(week, slot, lang):
    os.environ.update(SOURCE="year", WEEK=str(week), SLOT=slot)
    import risunok as Ri, reel_engine as R
    card = R.year_card(lang)
    out = []
    for sh in card["shots"]:
        body = Ri.clean(sh["prompt"])
        face = (Ri.FACE_M if any(m in body.lower() for m in Ri.MUZH) else Ri.FACE).get(lang, "")
        out.append(", ".join(x for x in (face, body, Ri.STYLE) if x))
    return card, out


def cmd_smeta(week, slot, lang="kk"):
    card, pr = opisaniya(week, slot, lang)
    n = len(pr)
    kl = (480 * 864 * 24 * SEC) / 1024 / 1e6 * 1.80
    print(f"{card['title']} — планов {n}")
    print(f"  кадры    ~${0.002*n:.3f}")
    print(f"  движение ~${kl*n:.2f}")
    print(f"  ИТОГО    ~${0.002*n + kl*n:.2f}")


def cmd_rolik(week, slot, lang):
    cast = "az" if lang in ("kk", "ru", "uz", "tr") else (
        "zh" if lang == "zh" else "slav" if lang in ("rf", "uk") else "eu")
    K = f"{BASE}/kadry"; V = f"{BASE}/klipy"; U = f"{BASE}/klipoteka"
    for d in (K, V, U, f"{BASE}/video/w"):
        os.makedirs(d, exist_ok=True)
    card, pr = opisaniya(week, slot, lang)
    kl = (480 * 864 * 24 * SEC) / 1024 / 1e6 * 1.80
    nado = len([1 for i in range(len(pr))
                if not os.path.exists(f"{V}/{week}{slot}-{i}-{cast}.mp4")])
    b = balans()
    print(f"{card['title']}")
    print(f"  планов {len(pr)}, оплатить {nado}, цена ~${kl*nado:.2f}, баланс ${b}")
    if kl * nado > LIMIT + 1e-9:
        raise SystemExit(f"СТОП: ${kl*nado:.2f} выше потолка ${LIMIT:.2f}")

    for i, p in enumerate(pr):
        png = f"{K}/{week}{slot}-{i}-{cast}.png"
        mp4 = f"{V}/{week}{slot}-{i}-{cast}.mp4"
        up = f"{U}/{week}{slot}-{i}-{cast}.mp4"
        t0 = time.time()
        kadr(p, png)
        klip(png, mp4)
        do_1080(mp4, up)
        print(f"  [{i}] готов за {time.time()-t0:.0f} сек", flush=True)

    env = dict(os.environ, KLIPY=U, KADRY=K, PROJECT="ibook", SOURCE="year",
               WEEK=str(week), SLOT=slot, LANGS_ONLY=lang,
               OUT_DIR=f"{BASE}/video", WORK=f"{BASE}/video/w")
    subprocess.run([sys.executable, os.path.join(HERE, "reel_engine.py")], env=env)
    print(f"остаток на счету: ${balans()}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help", "помощь"): print(__doc__)
    elif a[0] == "смета": cmd_smeta(a[1], a[2], a[3] if len(a) > 3 else "kk")
    elif a[0] == "ролик": cmd_rolik(a[1], a[2], a[3] if len(a) > 3 else "kk")
    else: print("не знаю команду:", a[0]); print(__doc__)
