#!/usr/bin/env python3
"""
Подбор обработки голоса так, чтобы В ПАУЗАХ была тишина, а не шипение.

Владелец описал это точнее любого прибора: «после точки, когда начинается новое
слово, шипит, как старый телевизор». Это ровно то место, где наша обработка
делала хуже всего.

Старая цепочка поднимала тишину дважды. Сначала сжатие с добавкой четыре
децибела: оно тянет вверх ВСЁ, включая паузы. Потом выравнивание громкости до
минус десяти, а это очень громко, и оно тянет вверх ещё раз. Сверху ещё три
децибела вручную. Голос от этого громче почти не становился, потому что его и
так ограничивал лимитер, а вот шум между словами вырастал в разы.

Здесь мы гоняем один и тот же образец через разные цепочки и меряем ровно то,
что человек и слышит: насколько громко шипит в паузах по сравнению с голосом.

    python tishina.py            сравнить варианты
"""
import os, sys, subprocess, math, wave

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RABOTA = "/Volumes/T7/ibook-reels/tishina"
GOLOSA = "/Volumes/T7/uk-tts"

STARAYA = ("acompressor=threshold=-22dB:ratio=4:attack=5:release=120:makeup=4,"
           "loudnorm=I=-10:TP=-1.0:LRA=6,volume=3dB,"
           "alimiter=limit=0.85:level=disabled")

# Порядок здесь имеет значение. Сначала убираем то, чего в голосе быть не
# должно, и только потом делаем громко. Наоборот - значит усилить мусор.
NOVAYA = ("highpass=f=70,"                                    # гул и рокот ниже голоса
          "afftdn=nf=-45:nr=18,"                              # само шипение, по спектру
          "agate=threshold=0.008:ratio=6:attack=8:release=180,"   # в паузах тишина
          "acompressor=threshold=-20dB:ratio=3:attack=8:release=150:makeup=2,"
          "loudnorm=I=-12:TP=-1.5:LRA=7,"
          "alimiter=limit=0.9:level=disabled")

# Промежуточные варианты - чтобы понять, что именно помогло, а что лишнее.
VARIANTY = {
    "старая": STARAYA,
    "только тише": ("acompressor=threshold=-20dB:ratio=3:attack=8:release=150:makeup=2,"
                    "loudnorm=I=-12:TP=-1.5:LRA=7,alimiter=limit=0.9:level=disabled"),
    "плюс ворота": ("agate=threshold=0.008:ratio=6:attack=8:release=180,"
                    "acompressor=threshold=-20dB:ratio=3:attack=8:release=150:makeup=2,"
                    "loudnorm=I=-12:TP=-1.5:LRA=7,alimiter=limit=0.9:level=disabled"),
    "новая": NOVAYA,
}

TEKST = ("Holidays are over. School starts, work starts, and suddenly everybody wants "
         "their roots done this week. That rush either fills your calendar or buries you "
         "in missed calls. Put your booking link in your bio tonight.")


def izmerit(path):
    """Насколько громко шипит в паузах относительно голоса, в децибелах.

    Считаем по кадрам: самые тихие десять процентов - это паузы, самые громкие
    пять - это голос. Разница между ними и есть то, что слышно как шум. Чем
    число меньше (глубже минус), тем чище пауза.
    """
    import numpy as np
    with wave.open(path) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        sr = w.getframerate()
    kadr, shag = int(0.04 * sr), int(0.01 * sr)
    en = np.array([float(np.sqrt(np.mean(x[i:i + kadr] ** 2)))
                   for i in range(0, len(x) - kadr, shag)])
    if not len(en):
        return 0.0, 0.0
    tiho, gromko = np.percentile(en, 10), np.percentile(en, 95)
    fon = 20 * math.log10(max(tiho, 1e-7) / max(gromko, 1e-7))
    # Абсолютный уровень паузы: именно он и слышен в наушниках.
    abs_pauza = 20 * math.log10(max(tiho, 1e-7))
    return round(fon, 1), round(abs_pauza, 1)


def main():
    os.makedirs(RABOTA, exist_ok=True)
    syroy = os.path.join(RABOTA, "syroy.wav")
    if not os.path.exists(syroy):
        subprocess.run([os.path.join(GOLOSA, ".venv/bin/python"), "-m", "piper",
                        "-m", os.path.join(GOLOSA, "en_US-lessac-high.onnx"), "-f", syroy],
                       input=TEKST, text=True, capture_output=True)
    print(f"{'цепочка':16} {'шум в паузе':>12} {'уровень паузы':>14}")
    print("-" * 45)
    f, a = izmerit(syroy)
    print(f"{'без обработки':16} {f:>12} {a:>14}")
    for imya, cep in VARIANTY.items():
        out = os.path.join(RABOTA, imya.replace(" ", "_") + ".wav")
        subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", syroy, "-af", cep,
                        "-ar", "16000", "-ac", "1", out], check=False)
        if os.path.exists(out):
            f, a = izmerit(out)
            print(f"{imya:16} {f:>12} {a:>14}")


if __name__ == "__main__":
    main()
