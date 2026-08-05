#!/usr/bin/env python3
"""
Проверка голосов ЦИФРАМИ, а не на слух.

Владелец понимает казахский, русский и узбекский. Китайский, немецкий,
французский, испанский он проверить не может - и правильно делает, что не
верит на слово. Поэтому считаем то, что можно измерить.

Что меряем и почему именно это:

    РАЗМАХ ГОЛОСА   на сколько полутонов голос ходит вверх-вниз.
                    Живая речь гуляет, робот бубнит на одной ноте.
                    Это самая честная примета «искусственности» - она не
                    зависит от языка, поэтому годится там, где мы ни слова
                    не понимаем.

    ПАУЗЫ           сколько раз голос останавливается и на сколько.
                    Человек дышит и держит паузу по смыслу, синтез часто
                    идёт сплошным потоком или, наоборот, рвёт ровными кусками.

    ТЕМП            знаков в секунду. Слишком быстро - каша, слишком
                    медленно - усыпляет.

    ГРОМКОСТЬ       разброс громкости. У живой речи ударные слова громче,
                    у робота всё ровное.

Мерить в пустоте бессмысленно, поэтому есть две опорные точки:

    ЭТАЛОН ХОРОШО   русский ElevenLabs - тот голос, который владелец сам
                    выбрал из трёх и одобрил.
    ЭТАЛОН РОБОТ    русский Piper - тот тип звучания, про который он сказал
                    «не очень, как робот».

Каждый бесплатный голос сравниваем с этими двумя. Если цифры ближе к первому -
язык можно отдавать бесплатному голосу. Ближе ко второму - нужен платный.

    python proverka_golosa.py
"""
import os, sys, json, glob, math, subprocess, wave

HERE = os.path.dirname(os.path.abspath(__file__))
GOLOSA = "/Volumes/T7/uk-tts"
RABOTA = "/Volumes/T7/ibook-reels/proverka"
ARHIV = "/Volumes/T7/ibook-reels/kk"

# Какой голос за какой язык. Берём то, что реально лежит на диске.
GOLOS = {
    "kk": "kk_KZ-issai-high",
    "uk": "uk_UA-tetiana-high",
    "zh": "zh_CN-huayan-medium",
    "en": "en_US-libritts-high",
    "de": "de_DE-thorsten-high",
    "fr": "fr_FR-siwis-medium",
    "es": "es_MX-claude-high",
    "ru": "ru_RU-dmitri-medium",      # эталон «робот»
}
NAZVANIE = {"kk": "казахский", "uk": "украинский", "zh": "китайский",
            "en": "английский", "de": "немецкий", "fr": "французский",
            "es": "испанский", "ru": "русский (бесплатный)"}


def tekst(lang):
    """Живой кусок текста из настоящего сценария, а не выдуманная фраза."""
    f = os.path.join(HERE, "scenarii", f"videos_{lang}.json")
    d = json.load(open(f, encoding="utf-8"))
    d = d if isinstance(d, list) else d.get("videos", [])
    for v in d:
        t = (v.get("vo") or "").strip()
        if len(t) > 180:
            return t[:400]
    return (d[0].get("vo") or "")[:400] if d else ""


def sintez(lang, out):
    m = os.path.join(GOLOSA, GOLOS[lang] + ".onnx")
    if not os.path.exists(m):
        return None
    t = tekst(lang)
    if not t:
        return None
    py = os.path.join(GOLOSA, ".venv/bin/python")
    r = subprocess.run([py, "-m", "piper", "-m", m, "-f", out],
                       input=t, text=True, capture_output=True)
    return (out, t) if os.path.exists(out) and os.path.getsize(out) > 1000 else None


def v_wav(src, dst):
    """Всё приводим к одному виду: моно, 16 кГц - иначе цифры несравнимы."""
    subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", src,
                    "-ac", "1", "-ar", "16000", dst], check=False)
    return os.path.exists(dst)


def chitat(path):
    import numpy as np
    with wave.open(path) as w:
        n = w.getnframes()
        x = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
        return x, w.getframerate()


def vysota(x, sr):
    """Высота голоса по кадрам. Автокорреляция: там, где сигнал повторяется
    сам через одинаковый промежуток, этот промежуток и есть период голоса."""
    import numpy as np
    kadr, shag = int(0.04 * sr), int(0.01 * sr)
    lo, hi = int(sr / 400), int(sr / 70)          # 70-400 Гц, весь людской диапазон
    f0, energiya = [], []
    for i in range(0, len(x) - kadr, shag):
        k = x[i:i + kadr]
        e = float(np.sqrt(np.mean(k ** 2)))
        energiya.append(e)
        if e < 0.01:
            continue
        k = k - k.mean()
        a = np.correlate(k, k, "full")[kadr - 1:]
        if a[0] <= 0:
            continue
        a = a / a[0]
        seg = a[lo:hi]
        if not len(seg):
            continue
        p = int(np.argmax(seg)) + lo
        if a[p] > 0.35:                            # иначе это шум, а не голос
            f0.append(sr / p)
    return np.array(f0), np.array(energiya)


def shum(x, sr):
    """Сколько в записи лишнего шума.

    Владелец услышал в английском голосе шипение, которого я не померил, и был
    прав. Хуже того: мой прежний замер живости шум ПООЩРЯЛ. Высоту голоса я
    беру по автокорреляции, а на шумной записи она скачет как попало, и этот
    скачок засчитывался как «живая интонация». Поэтому голос с шипением вышел
    на первое место. Теперь шум меряем отдельно и живость без него не смотрим.

    ЧИСТОТА    насколько звук периодичен. Голос - это повторяющиеся колебания
               связок, шум не повторяется. Единица - чистый тон, ноль - шипение.
    ФОН        насколько громко шипит В ПАУЗАХ, когда голос молчит. Именно это
               и слышно как «грязная запись».
    """
    import numpy as np
    kadr, shag = int(0.04 * sr), int(0.01 * sr)
    lo, hi = int(sr / 400), int(sr / 70)
    piki, en = [], []
    for i in range(0, len(x) - kadr, shag):
        k = x[i:i + kadr]
        en.append(float(np.sqrt(np.mean(k ** 2))))
        if en[-1] < 0.01:
            continue
        k = k - k.mean()
        a = np.correlate(k, k, "full")[kadr - 1:]
        if a[0] <= 0:
            continue
        seg = (a / a[0])[lo:hi]
        if len(seg):
            piki.append(float(np.max(seg)))
    en = np.array(en)
    if not len(piki) or not len(en):
        return 0.0, 0.0
    # Фон: тихие кадры против громких, в децибелах. Чем ближе к нулю, тем
    # сильнее слышно шипение между словами.
    tihie = np.percentile(en, 10)
    gromkie = np.percentile(en, 95)
    fon = 20 * math.log10(max(tihie, 1e-7) / max(gromkie, 1e-7))
    return float(np.mean(piki)), fon


def mera(path, znakov):
    import numpy as np
    x, sr = chitat(path)
    dlit = len(x) / sr
    f0, en = vysota(x, sr)
    if len(f0) < 20:
        return None
    chistota, fon = shum(x, sr)
    # Разброс высоты в полутонах: язык не важен, ухо слышит именно это.
    med = float(np.median(f0))
    polutona = 12 * np.log2(np.clip(f0, 1e-6, None) / med)
    razmah = float(np.std(polutona))
    # Паузы: тишина дольше четверти секунды.
    tiho = en < (float(np.mean(en)) * 0.15)
    pauzy, tek = [], 0
    for t in tiho:
        if t:
            tek += 1
        elif tek:
            if tek * 0.01 > 0.25:
                pauzy.append(tek * 0.01)
            tek = 0
    gromkost = float(np.std(20 * np.log10(np.clip(en, 1e-6, None))))
    return {"длит": round(dlit, 1), "размах": round(razmah, 2),
            "пауз": len(pauzy), "пауза_ср": round(sum(pauzy) / len(pauzy), 2) if pauzy else 0,
            "темп": round(znakov / dlit, 1), "громкость": round(gromkost, 1),
            "чистота": round(chistota, 3), "фон": round(fon, 1)}


def main():
    os.makedirs(RABOTA, exist_ok=True)
    try:
        import numpy  # noqa
    except ImportError:
        sys.exit("нужен numpy: запускай через " + os.path.join(GOLOSA, ".venv/bin/python"))

    itog = {}

    # Две опорные точки. Берём ЧИСТЫЙ голос без музыки: в готовом ролике звук
    # сжат и выровнен обработкой, и по нему живость речи уже не измеришь.
    for imya, f in (("ЭТАЛОН ElevenLabs (одобрен)", "/Volumes/T7/ibook/golos-ru/gotov_ru_eleven.mp3"),
                    ("ЭТАЛОН робот (забракован)", "/Volumes/T7/ibook/golos-ru/gotov_ru_piper.mp3")):
        if not os.path.exists(f):
            continue
        w = os.path.join(RABOTA, os.path.basename(f) + ".wav")
        if v_wav(f, w):
            m = mera(w, len(tekst("ru")))
            if m:
                itog[imya] = m

    # Сравниваем не только «свой» голос языка, но и запасные того же языка:
    # владелец услышал шипение в английском, значит выбирать надо из нескольких.
    zapas = [x.strip() for x in os.environ.get("ZAPAS", "").split(",") if x.strip()]
    yazyki = [x.strip() for x in os.environ.get("YAZYKI", "ru,kk,uk,zh,en,de,fr,es").split(",")]
    for lang in yazyki:
        w = os.path.join(RABOTA, f"{lang}.wav")
        r = sintez(lang, w)
        if not r:
            print(f"  {lang}: не синтезировался", flush=True)
            continue
        m = mera(w, len(r[1]))
        if m:
            itog[f"{NAZVANIE.get(lang, lang)}"] = m
        print(f"  {NAZVANIE.get(lang, lang)}: готово", flush=True)

    for g in zapas:
        lang = g[:2] if g[:2] in NAZVANIE else "en"
        GOLOS["_"] = g
        NAZVANIE["_"] = g
        w = os.path.join(RABOTA, g + ".wav")
        staryy = GOLOS.get(lang)
        GOLOS[lang] = g
        r = sintez(lang, w)
        GOLOS[lang] = staryy
        if not r:
            print(f"  {g}: не синтезировался", flush=True)
            continue
        m = mera(w, len(r[1]))
        if m:
            itog[g] = m
        print(f"  {g}: готово", flush=True)

    print()
    zag = f"{'голос':30} {'чистота':>8} {'фон дБ':>7} {'размах':>7} {'темп':>6}"
    print(zag); print("-" * len(zag))
    for k, v in itog.items():
        print(f"{k:30} {v['чистота']:>8} {v['фон']:>7} {v['размах']:>7} {v['темп']:>6}")
    json.dump(itog, open(os.path.join(RABOTA, "itog.json"), "w"),
              ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
