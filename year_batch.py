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
import bot as B                      # подтягивает .env
import reel_engine as R
import send_batch as SB

LANG = sys.argv[1] if len(sys.argv) > 1 else "kk"
START = int(sys.argv[2]) if len(sys.argv) > 2 else 31
OUT = os.path.expanduser(f"~/Desktop/ibook-год-{R.LANGRU.get(LANG, LANG)}")
os.makedirs(OUT, exist_ok=True)
MIN_LEFT = 1500                      # запас, чтобы не оборваться на полуслове


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
    chat = SB.find_chat()
    print(f"язык {LANG}, роликов {len(jobs)}, старт с недели {START}, chat={chat}", flush=True)
    done = 0
    for w, s in jobs:
        left = quota_left()
        if left is not None and left < MIN_LEFT:
            print(f"СТОП: квота ElevenLabs кончилась ({left} знаков). Готово {done} роликов.", flush=True)
            break
        num = (w - 1) * 3 + {"A": 1, "B": 2, "C": 3}[s]
        env = dict(os.environ, PROJECT="ibook", SOURCE="year", WEEK=str(w), SLOT=s,
                   LANGS_ONLY=LANG, OUT_DIR=OUT, WORK=os.path.join(OUT, "work"))
        r = subprocess.run([sys.executable, os.path.join(HERE, "reel_engine.py")],
                           env=env, capture_output=True, text=True)
        path = os.path.join(OUT, f"{num:03d}-{R.COUNTRY.get(LANG,LANG)}-{R.LANGRU.get(LANG,LANG)}.mp4")
        if not os.path.exists(path):
            print(f"  №{num} ({w}{s}) НЕ СОБРАЛСЯ: {r.stdout[-200:]}", flush=True)
            continue
        done += 1
        print(f"  №{num} ({w}{s}) готов, всего {done}, квота {left}", flush=True)
        if chat:
            try:
                SB.send_video(chat, path, f"№{num} · 🇰🇿 {R.COUNTRY.get(LANG,LANG)} · {R.LANGRU.get(LANG,LANG)}")
            except Exception as e:
                print(f"     отправка не удалась: {str(e)[:70]}", flush=True)
    print(f"ИТОГО собрано {done} из {len(jobs)}", flush=True)


if __name__ == "__main__":
    main()
