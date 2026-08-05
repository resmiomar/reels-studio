#!/usr/bin/env python3
"""
Поиск ЖЕНСКОГО немецкого голоса среди 236 дикторов модели mls.

Владелец попросил женский, если найдётся хороший. У Piper из немецких женских
есть только три, и все записаны на низком качестве. Остаётся модель mls: там
236 дикторов, и среди них женские точно есть.

Ровно на такой модели я и обжёгся на английском: взял наугад голос из сборника
аудиокниг и получил шипение. Разница в том, что теперь голос можно измерить, а
не брать вслепую.

Что считаем по каждому диктору:

    ВЫСОТА    средняя частота голоса. Женский обычно 165-255 Гц, мужской
              85-155. Так отбираем женские, не слушая все 236.
    ЧИСТОТА   насколько звук периодичен, а не шипит.
    ЖИВОСТЬ   размах интонации в полутонах.
    ШУМ       насколько тихо в паузах ПОСЛЕ нашей чистки.

Сравниваем с двумя опорами: платный голос, который владелец одобрил (чистота
0.597, живость 4.20), и лучший немецкий на сегодня (0.697 и 4.38).

    python nemki.py            перебрать дикторов
"""
import os, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
GOLOSA = "/Volumes/T7/uk-tts"
RABOTA = "/Volumes/T7/ibook-reels/nemki"
MODEL = os.path.join(GOLOSA, "de_DE-mls-medium.onnx")
CHISTKA = ("highpass=f=70,afftdn=nf=-35:nr=40,"
           "agate=threshold=0.03:range=0.0002:ratio=9:attack=4:release=70:knee=3")
TEKST = ("Der Sommer ist vorbei und plötzlich wollen alle einen Termin. "
         "In ibook buchen deine Kundinnen selbst, Tag und Nacht.")
SKOLKO = int(os.environ.get("SKOLKO", "40"))
OTKUDA = int(os.environ.get("OTKUDA", "0"))


def odin(spk):
    syr = os.path.join(RABOTA, f"s{spk}.wav")
    chist = os.path.join(RABOTA, f"c{spk}.wav")
    if not os.path.exists(chist):
        subprocess.run([os.path.join(GOLOSA, ".venv/bin/python"), "-m", "piper",
                        "-m", MODEL, "-s", str(spk), "-f", syr],
                       input=TEKST, text=True, capture_output=True)
        if not os.path.exists(syr):
            return None
        subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", syr, "-af", CHISTKA,
                        "-ar", "16000", "-ac", "1", chist], check=False)
    if not os.path.exists(chist):
        return None
    import proverka_golosa as P
    import numpy as np
    m = P.mera(chist, 120)
    if not m:
        return None
    x, sr = P.chitat(chist)
    f0, _ = P.vysota(x, sr)
    if len(f0) < 20:
        return None
    return {"диктор": spk, "высота": int(np.median(f0)), **m}


def main():
    os.makedirs(RABOTA, exist_ok=True)
    vse = []
    for spk in range(OTKUDA, OTKUDA + SKOLKO):
        r = odin(spk)
        if r:
            vse.append(r)
        print(f"  диктор {spk}: {'высота ' + str(r['высота']) + ' Гц' if r else 'не вышло'}",
              flush=True)
    # Женские отбираем по высоте голоса, мужские просто не показываем.
    zhen = [r for r in vse if r["высота"] >= 160]
    zhen.sort(key=lambda r: (-r["чистота"], -r["размах"]))
    print(f"\nиз {len(vse)} проверенных женских: {len(zhen)}\n")
    print(f"{'диктор':>7} {'высота':>7} {'чистота':>8} {'живость':>8} {'шум':>7}")
    print("-" * 42)
    for r in zhen[:10]:
        print(f"{r['диктор']:>7} {r['высота']:>7} {r['чистота']:>8} {r['размах']:>8} {r['фон']:>7}")
    print("\nдля сравнения:")
    print("  платный одобренный      чистота 0.597  живость 4.20")
    print("  лучший немецкий мужской чистота 0.697  живость 4.38")


if __name__ == "__main__":
    main()
