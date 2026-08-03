#!/usr/bin/env python3
"""
Прогон целого года на одном языке: рендерит ролик за роликом и сразу шлёт в Telegram.

  python year_batch.py kk [стартовая_неделя]

Порядок недель идёт ОТ ТЕКУЩЕГО СЕЗОНА и заворачивается на начало года:
31..52, потом 1..30. Так первым приходит то, что можно публиковать сегодня,
а не январь в августе.

Перед каждым роликом проверяется квота ElevenLabs: если её не хватает, прогон
останавливается сам и говорит, сколько успел, а не падает на середине.
"""
import os, sys, json, subprocess, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import subprocess as _sp, json as _json
import bot as B                      # подтягивает .env
import reel_engine as R
import send_batch as SB

LANG = sys.argv[1] if len(sys.argv) > 1 else "kk"
START = int(sys.argv[2]) if len(sys.argv) > 2 else 31
LIMIT = int(sys.argv[3]) if len(sys.argv) > 3 else 0        # сколько роликов максимум
TAG = os.environ.get("CAP_TAG", "")                          # пометка в подписи
# Пишем на внешний диск, если он подключён: на внутреннем места в обрез,
# а год роликов это несколько гигабайт.
_T7 = "/Volumes/T7/ibook/video"
OUT = (os.path.join(_T7, f"год-{R.LANGRU.get(LANG, LANG)}") if os.path.isdir("/Volumes/T7/ibook")
       else os.path.expanduser(f"~/Desktop/ibook-год-{R.LANGRU.get(LANG, LANG)}"))
os.makedirs(OUT, exist_ok=True)
MIN_LEFT = 1500                      # запас, чтобы не оборваться на полуслове

# Недели -> месяцы, как в годовом плане. Владельцу номер «№93» ничего не говорит,
# ему нужно «АВГУСТ, третий ролик» - по этому он и планирует публикации.
MONTHS = [("ЯНВАРЬ",1,4),("ФЕВРАЛЬ",5,9),("МАРТ",10,13),("АПРЕЛЬ",14,17),
          ("МАЙ",18,22),("ИЮНЬ",23,26),("ИЮЛЬ",27,30),("АВГУСТ",31,35),
          ("СЕНТЯБРЬ",36,39),("ОКТЯБРЬ",40,43),("НОЯБРЬ",44,48),("ДЕКАБРЬ",49,52)]
def month_of(week):
    for name,a,b in MONTHS:
        if a <= week <= b: return name,a,b
    return "ГОД",1,52
def month_size(a,b):
    return (b-a+1)*3


def already_good(path):
    """Готов ли ролик и цел ли он. Проверяем ДО рендера, иначе прогон после
    перезапуска начинает всё с начала: для платных языков это сожжённая квота,
    для бесплатных - потерянные часы. Битые (картинка короче звука) переделываем."""
    if not os.path.exists(path) or os.path.getsize(path) < 200_000:
        return False
    try:
        r = _sp.run(["ffprobe", "-v", "quiet", "-print_format", "json",
                     "-show_streams", path], capture_output=True, text=True)
        v = a = 0.0
        for st in _json.loads(r.stdout).get("streams", []):
            if st["codec_type"] == "video": v = float(st.get("duration") or 0)
            else: a = float(st.get("duration") or 0)
        return v > 5 and abs(a - v) < 1.5          # звук и картинка сходятся
    except Exception:
        return False


def quota_left():
    try:
        req = urllib.request.Request("https://api.elevenlabs.io/v1/user/subscription",
                                     headers={"xi-api-key": os.environ["EL_KEY"]})
        d = json.load(urllib.request.urlopen(req, timeout=30))
        return d["character_limit"] - d["character_count"]
    except Exception:
        return None


def main():
    weeks = list(range(START, 53)) + list(range(1, START))
    jobs = [(w, s) for w in weeks for s in ("A", "B", "C")]
    if LIMIT: jobs = jobs[:LIMIT]
    chat = SB.find_chat()
    print(f"язык {LANG}, роликов {len(jobs)}, старт с недели {START}, chat={chat}", flush=True)
    done = 0
    cur_month = None
    idx_in_month = 0
    # Квота нужна только платному движку. Языки на локальных моделях считаются
    # бесплатно и без лимитов - для них проверка бессмысленна и лишь тормозит прогон.
    PAID = R.VOICES.get(LANG, [("", "")])[0][0] == "eleven"
    for w, s in jobs:
        left = quota_left() if PAID else None
        if left is not None and left < MIN_LEFT:
            print(f"СТОП: квота ElevenLabs кончилась ({left} знаков). Готово {done} роликов.", flush=True)
            break
        num = (w - 1) * 3 + {"A": 1, "B": 2, "C": 3}[s]
        mname, ma, mb = month_of(w)
        if mname != cur_month:                      # объявляем начало месяца
            cur_month, idx_in_month = mname, 0
            if chat:
                try: SB.api("sendMessage", chat_id=chat,
                            text=f"🗓 {mname} — дальше идут ролики этого месяца")
                except Exception: pass
        idx_in_month += 1
        path_pre = os.path.join(OUT, f"{num:03d}-{R.COUNTRY.get(LANG,LANG)}-{R.LANGRU.get(LANG,LANG)}.mp4")
        if already_good(path_pre):
            done += 1
            print(f"  №{num} ({w}{s}) уже готов, пропускаю", flush=True)
            continue
        env = dict(os.environ, PROJECT="ibook", SOURCE="year", WEEK=str(w), SLOT=s,
                   LANGS_ONLY=LANG, OUT_DIR=OUT, WORK=os.path.join(OUT, "work"))
        r = subprocess.run([sys.executable, os.path.join(HERE, "reel_engine.py")],
                           env=env, capture_output=True, text=True)
        path = os.path.join(OUT, f"{num:03d}-{R.COUNTRY.get(LANG,LANG)}-{R.LANGRU.get(LANG,LANG)}.mp4")
        # уже собранный и целый ролик не переделываем: квота дорогая
        if not os.path.exists(path):
            print(f"  №{num} ({w}{s}) НЕ СОБРАЛСЯ: {r.stdout[-200:]}", flush=True)
            continue
        done += 1
        print(f"  №{num} ({w}{s}) готов, всего {done}" + (f", квота {left}" if PAID else ""), flush=True)
        if chat:
            try:
                cap = (f"🗓 {cur_month} · ролик {idx_in_month} из {month_size(ma,mb)}\n"
                       f"🇰🇿 {R.COUNTRY.get(LANG,LANG)} · {R.LANGRU.get(LANG,LANG)} · неделя {w}")
                if TAG: cap = f"{TAG}\n{cap}"
                SB.send_video(chat, path, cap)
            except Exception as e:
                print(f"     отправка не удалась: {str(e)[:70]}", flush=True)
    print(f"ИТОГО собрано {done} из {len(jobs)}", flush=True)


if __name__ == "__main__":
    main()
