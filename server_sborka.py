#!/usr/bin/env python3
"""
Сборка роликов НА СЕРВЕРЕ. Компьютер владельца при этом выключен.

Работает внутри GitHub Actions: бесплатно, 2000 минут в месяц, а ролик собирается
около трёх минут - это больше шестисот роликов в месяц.

Почему это вообще стало возможно. Раньше сборка держалась за Mac, потому что
голос считался локальными моделями на девять гигабайт. Теперь для двух главных
языков локальные модели не нужны:

    русский    ElevenLabs по сети - обычный запрос, считает их сервер
    казахский  готовые mp3, вытащенные из прошлогодних роликов

Значит на сервере нужны только ffmpeg, python и материалы. Материалы лежат в
релизе репозитория: туда влезает до двух гигабайт на файл, и это бесплатно.

Переменные окружения задаёт GitHub:
    YAZYK   какой язык собирать
    NEDELI  какие недели, через пробел
    TG_TOKEN  токен бота для отправки в каналы
"""
import os, sys, glob, json, subprocess, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

YAZYK = os.environ.get("YAZYK", "kk")
NEDELI = os.environ.get("NEDELI", "31 32 33 34 35").split()
OUT = os.path.join(HERE, "out")
ASSETS = os.path.join(HERE, "assets")


def raspakovat():
    """Материалы приходят архивами из релиза - распаковываем то, что есть."""
    for z in sorted(glob.glob(f"{ASSETS}/*.zip")) + sorted(glob.glob(f"{ASSETS}/*.tar.gz")):
        print("распаковываю", os.path.basename(z), flush=True)
        if z.endswith(".zip"):
            subprocess.run(["unzip", "-q", "-o", z, "-d", ASSETS], check=False)
        else:
            subprocess.run(["tar", "xzf", z, "-C", ASSETS], check=False)


def sobrat(week, slot):
    env = dict(os.environ)
    env.update(PROJECT="ibook", SOURCE="year", WEEK=str(week), SLOT=slot,
               LANGS_ONLY=YAZYK, KOROTKO="1",
               OUT_DIR=OUT, WORK=os.path.join(OUT, "w"),
               KADRY=os.path.join(ASSETS, "kadry"),
               KLIPY=os.path.join(ASSETS, "klipoteka"),
               GOLOS=os.path.join(ASSETS, f"golos-{YAZYK}"))
    r = subprocess.run([sys.executable, os.path.join(HERE, "reel_engine.py")],
                       env=env, capture_output=True, text=True)
    line = [l for l in r.stdout.splitlines() if "DONE" in l or "ERR" in l]
    if line:
        print(f"  {week}{slot}: {line[0]}", flush=True)
    else:
        # Первые серверные прогоны молчали: ошибка уходила в stderr, а я его не
        # печатал и видел пустоту. Теперь показываем оба потока.
        print(f"  {week}{slot}: НЕ СОБРАЛСЯ\n     stdout: {r.stdout[-300:]}\n"
              f"     stderr: {r.stderr[-500:]}", flush=True)
    return bool(line and "DONE" in line[0])


def main():
    os.makedirs(os.path.join(OUT, "w"), exist_ok=True)
    raspakovat()
    print(f"язык {YAZYK}, недели {' '.join(NEDELI)}", flush=True)
    n = 0
    for w in NEDELI:
        for s in ("A", "B", "C"):
            if sobrat(w, s):
                n += 1
    print(f"собрано роликов: {n}")
    # Отправляем сразу из сервера: тогда владельцу вообще ничего делать не надо.
    if os.environ.get("TG_TOKEN"):
        os.environ["BOT_TOKEN"] = os.environ["TG_TOKEN"]
        try:
            import kanaly
            kanaly.cmd_shli(OUT)
        except Exception as e:
            print("отправка не удалась:", str(e)[:150])


if __name__ == "__main__":
    main()
