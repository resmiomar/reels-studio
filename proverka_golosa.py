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


def mera(path, znakov):
    import numpy as np
    x, sr = chitat(path)
    dlit = len(x) / sr
    f0, en = vysota(x, sr)
    if len(f0) < 20:
        return None
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
            "темп": round(znakov / dlit, 1), "громкость": round(gromkost, 1)}


def main():
    os.makedirs(RABOTA, exist_ok=True)
    try:
        import numpy  # noqa
    except ImportError:
        sys.exit("нужен numpy: запускай через " + os.path.join(GOLOSA, ".venv/bin/python"))

    itog = {}

    # Эталон «хорошо»: голос, который владелец одобрил. Достаём из готового ролика.
    # Имя ищем через нормализацию: внешний диск хранит «й» разложенной на «и» и
    # значок сверху, и обычное сравнение строк такой файл не находит.
    import unicodedata as U
    def norm(s): return U.normalize("NFC", s)
    obrazec = sorted(f for f in glob.glob(os.path.join(ARHIV, "*.mp4"))
                     if "русский" in norm(os.path.basename(f)))
    if obrazec:
        w = os.path.join(RABOTA, "etalon_eleven.wav")
        if v_wav(obrazec[0], w):
            m = mera(w, 250)
            if m:
                itog["ЭТАЛОН ElevenLabs (одобрен)"] = m

    for lang in ("ru", "kk", "uk", "zh", "en", "de", "fr", "es"):
        w = os.path.join(RABOTA, f"{lang}.wav")
        r = sintez(lang, w)
        if not r:
            print(f"  {lang}: не синтезировался", flush=True)
            continue
        m = mera(w, len(r[1]))
        if m:
            itog[f"{NAZVANIE[lang]}"] = m
        print(f"  {NAZVANIE[lang]}: готово", flush=True)

    print()
    zag = f"{'голос':32} {'размах':>7} {'пауз':>5} {'темп':>6} {'громк':>6}"
    print(zag); print("-" * len(zag))
    for k, v in itog.items():
        print(f"{k:32} {v['размах']:>7} {v['пауз']:>5} {v['темп']:>6} {v['громкость']:>6}")
    json.dump(itog, open(os.path.join(RABOTA, "itog.json"), "w"),
              ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
