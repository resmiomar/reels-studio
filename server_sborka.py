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

# По расписанию язык не задан - берём по дню недели, чтобы за неделю прошли все.
PO_DNYAM = {0: "kk", 1: "ru", 2: "uk", 3: "zh", 4: "en", 5: "de", 6: "fr"}
import datetime
YAZYK = os.environ.get("YAZYK") or PO_DNYAM[datetime.datetime.utcnow().weekday()]
# «god» - весь год, от текущего месяца и по кругу: сначала то, что можно
# публиковать сегодня, а не январь в августе.
_N = os.environ.get("NEDELI", "31 32 33 34 35").strip()
NEDELI = ([str(w) for w in list(range(31, 53)) + list(range(1, 31))]
          if _N in ("god", "год", "all") else _N.split())
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


def papka_golosa():
    """Где лежит готовая озвучка этого языка.

    Архив распаковывается под своим именем («golos-kk-eleven»), а не под тем,
    что ждал код («golos-kk»). Из-за этого движок не находил готовые дорожки
    и лез синтезировать голос, которого на сервере нет. Ищем по началу имени.
    """
    for d in sorted(glob.glob(os.path.join(ASSETS, f"golos-{YAZYK}*"))):
        if os.path.isdir(d):
            return d
    return os.path.join(ASSETS, f"golos-{YAZYK}")


def nomer(week, slot):
    """Сквозной номер ролика: неделя 31, слот A - это ролик 91."""
    return (int(week) - 1) * 3 + "ABC".index(slot) + 1


# Пересборка: собрать заново то, что уже в канале, и НЕ слать повторно.
# Нужна, когда поменялся звук: старые ролики остаются на месте, новые ложатся
# на диск, и владелец сам решает, менять ли содержимое каналов.
PERESBORKA = os.environ.get("PERESBORKA") == "1"
NE_SLAT = os.environ.get("NE_SLAT") == "1"


def uzhe_otpravlen(week, slot):
    """Проверка ДО сборки, а не после отправки.

    Ночной запуск каждую неделю брал одни и те же августовские недели и
    собирал их заново. Для казахского это просто потерянное время, а для
    русского - сгоревшая платная озвучка: пятнадцать роликов съели квоту,
    хотя они уже лежали в канале.
    """
    if PERESBORKA:
        return False
    try:
        return nomer(week, slot) in json.load(
            open(os.path.join(HERE, "otpravleno.json"), encoding="utf-8")).get(YAZYK, [])
    except Exception:
        return False


def sobrat(week, slot):
    if uzhe_otpravlen(week, slot):
        print(f"  {week}{slot}: ролик {nomer(week, slot)} уже в канале, не собираю", flush=True)
        return False
    env = dict(os.environ)
    env.update(PROJECT="ibook", SOURCE="year", WEEK=str(week), SLOT=slot,
               LANGS_ONLY=YAZYK, KOROTKO="1",
               OUT_DIR=OUT, WORK=os.path.join(OUT, "w"),
               KADRY=os.path.join(ASSETS, "kadry"),
               KLIPY=os.path.join(ASSETS, "klipoteka"),
               GOLOS=papka_golosa())
    # На сервере нет тяжёлой локальной модели голоса (9 ГБ) - её туда не затащить.
    # Русский идёт на ElevenLabs: владелец выбрал этот голос из трёх, и это
    # обычный запрос по сети, серверу он по силам.
    if YAZYK in ("ru", "rf"):
        # Голос сменился не по прихоти. Прежний id жил на старом аккаунте, тот
        # слетел с подписки, и клон вместе с ним: API отвечает 404 «нет такого
        # голоса». Владелец оплатил новый аккаунт, голос там пересоздан заново.
        # Проверять это надо ДО прогона: с мёртвым id падают все сто пятьдесят
        # шесть роликов подряд, а узнаём мы об этом через пять часов.
        env["VOICE_" + YAZYK.upper()] = "eleven:fYbY1GfdF8gzmhPxjfDp"
    # Языки, которым нужна только локальная тяжёлая модель, на сервере не берём:
    # лучше честно пропустить, чем собрать пятнадцать пустых роликов.
    #
    # Узбекский из этого списка ушёл. Он был здесь, пока говорил дообученным
    # Chatterbox: тот весит гигабайты и на сервер не влезал. Владелец эту
    # озвучку забраковал - язык он понимает и слышал обрубки и сбитые ударения.
    # Теперь узбекский говорит нейроголосом Microsoft: модель не качается
    # вовсе, синтез идёт по сети, серверу это по силам как и любой запрос.
    if YAZYK in ("tr", "it") and not os.path.isdir(os.path.expanduser("~/uz-tts")):
        print(f"  {week}{slot}: язык {YAZYK} на сервере не собирается, нужен Mac", flush=True)
        return False
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
    # Прогон ограничен шестью часами. Ролик собирается три-четыре минуты, значит
    # за раз влезает около сотни. Останавливаемся заранее и досылаем что успели,
    # иначе GitHub оборвёт на середине и пропадёт всё.
    import time as _t
    start = _t.time()
    for w in NEDELI:
        for s in ("A", "B", "C"):
            if _t.time() - start > 5.2 * 3600:
                print(f"близко к пределу времени, останавливаюсь на {w}{s}", flush=True)
                break
            if sobrat(w, s):
                n += 1
        else:
            continue
        break
    print(f"собрано роликов: {n}")
    # Отправляем сразу из сервера: тогда владельцу вообще ничего делать не надо.
    if NE_SLAT:
        print("пересборка: в каналы не отправляю, ролики лежат в артефакте")
    elif os.environ.get("TG_TOKEN"):
        os.environ["BOT_TOKEN"] = os.environ["TG_TOKEN"]
        try:
            import kanaly
            kanaly.cmd_shli(OUT)
        except Exception as e:
            print("отправка не удалась:", str(e)[:150])


if __name__ == "__main__":
    main()
