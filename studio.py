#!/usr/bin/env python3
"""
ibook Studio - собственный генератор промо-роликов. Свой, локальный, без подписок.

    python studio.py языки                 что умеем и чем считаем
    python studio.py ролик kk 31 A         один ролик
    python studio.py неделя 31             все языки одной недели
    python studio.py год uz                весь год на языке (уходит в Telegram сам)
    python studio.py проверь <папка>       контроль качества готовых роликов

Что внутри и сколько стоит:
    кадры      Pexels               бесплатно
    монтаж     ffmpeg на твоём Mac  бесплатно
    голос      Chatterbox локально  бесплатно, кроме казахского
    казахский  ElevenLabs           единственная платная часть

Переключатели:
    ENGINE=local    вообще всё на локальный движок, даже казахский
    ENGINE=eleven   вернуть всё на платный (быстро, но тратит квоту)
"""
import os, sys, subprocess, json, glob

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def sh(cmd, env=None):
    return subprocess.run(cmd, env={**os.environ, **(env or {})}, cwd=HERE)


def cmd_yazyki():
    sys.path.insert(0, HERE)
    os.environ.setdefault("PROJECT", "ibook")
    import reel_engine as R
    free = [l for l in R.VOICES if R.VOICES[l][0][0] == "chatterbox"]
    paid = [l for l in R.VOICES if R.VOICES[l][0][0] == "eleven"]
    plan = {os.path.basename(f)[7:-5]: len(json.load(open(f, encoding="utf-8")))
            for f in glob.glob(os.path.join(os.path.expanduser("~/ibook-video"), "videos_*.json"))}
    print(f"{'язык':6}{'страна':13}{'сценариев':>11}  движок")
    print("-" * 52)
    for l in R.LANG_CODE:
        n = plan.get(l, 0)
        eng = "локально, бесплатно" if l in free else "ElevenLabs, платно"
        mark = "✔" if n >= 156 else ("~" if n else "нет")
        print(f"{l:6}{R.COUNTRY.get(l,''):13}{f'{mark} {n}':>11}  {eng}")
    print(f"\n  бесплатных языков: {len(free)} | платных: {len(paid)}")


def cmd_rolik(lang, week, slot):
    env = dict(PROJECT="ibook", SOURCE="year", WEEK=str(week), SLOT=slot,
               LANGS_ONLY=lang, OUT_DIR=os.environ.get("OUT_DIR", "/Volumes/T7/ibook/video/odinochnye"))
    os.makedirs(env["OUT_DIR"], exist_ok=True)
    sh([PY, os.path.join(HERE, "reel_engine.py")], env)


def cmd_nedelya(week):
    langs = ",".join(["kk", "ru", "uz", "uk", "en", "rf", "tr", "zh", "de", "it", "es", "fr"])
    out = os.environ.get("OUT_DIR", f"/Volumes/T7/ibook/video/nedelya-{week}")
    os.makedirs(out, exist_ok=True)
    for slot in ("A", "B", "C"):
        sh([PY, os.path.join(HERE, "reel_engine.py")],
           dict(PROJECT="ibook", SOURCE="year", WEEK=str(week), SLOT=slot,
                LANGS_ONLY=langs, OUT_DIR=out))


def cmd_god(lang, start="31"):
    sh([PY, os.path.join(HERE, "year_batch.py"), lang, start])


def cmd_proverь(folder):
    """Контроль: замирание картинки и повторяющиеся первые кадры. Оба бага были
    настоящими и незаметны на глаз - проверяем измерением, а не просмотром."""
    import hashlib, collections
    files = sorted(glob.glob(os.path.join(folder, "*.mp4")))
    if not files:
        print("нет роликов в", folder); return
    os.makedirs("/tmp/qc", exist_ok=True)
    froze, h = 0, collections.defaultdict(list)
    for f in files:
        r = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json",
                            "-show_streams", f], capture_output=True, text=True)
        v = a = 0.0
        for st in json.loads(r.stdout).get("streams", []):
            if st["codec_type"] == "video": v = float(st.get("duration") or 0)
            else: a = float(st.get("duration") or 0)
        if a - v > 1.0: froze += 1
        out = "/tmp/qc/" + os.path.basename(f)[:6] + ".jpg"
        subprocess.run(["ffmpeg", "-y", "-i", f, "-ss", "0.4", "-frames:v", "1", out],
                       capture_output=True)
        if os.path.exists(out):
            h[hashlib.md5(open(out, "rb").read()).hexdigest()].append(os.path.basename(f))
    dup = sum(len(g) for g in h.values() if len(g) > 1)
    print(f"  роликов:              {len(files)}")
    print(f"  замирают:             {froze}   {'✔' if not froze else '✗ ПЕРЕДЕЛАТЬ'}")
    print(f"  разных первых кадров: {len(h)} из {len(files)}")
    print(f"  повторов начала:      {dup}   {'✔' if not dup else '✗ Instagram сочтёт дублем'}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help", "помощь"):
        print(__doc__)
    elif a[0] == "языки":
        cmd_yazyki()
    elif a[0] == "ролик":
        cmd_rolik(a[1], a[2], a[3])
    elif a[0] == "неделя":
        cmd_nedelya(a[1])
    elif a[0] == "год":
        cmd_god(a[1], a[2] if len(a) > 2 else "31")
    elif a[0] in ("проверь", "проверка"):
        cmd_proverь(a[1])
    else:
        print("не знаю команду:", a[0]); print(__doc__)
