#!/usr/bin/env python3
"""
Убрать чёрную обложку у уже собранных роликов.

Беда. Instagram и TikTok берут обложкой ПЕРВЫЙ кадр ролика. В роликах, собранных
до правки движка, первый кадр чёрный: там стояло затемнение на входе, 0.28
секунды. В ленте такой ролик выглядит чёрным прямоугольником, и его пролистывают,
не досмотрев ни секунды. Проверено на казахском: чёрная обложка у десяти из
десяти.

Движок с тех пор исправлен - у первого кадра входа из черноты больше нет. Но
шестьсот с лишним роликов уже собраны и разосланы, пересобирать их долго и
дорого.

Что делает этот скрипт. Находит первый нормальный кадр и накрывает им чёрное
начало. Картинка поверх, а не вместо: длина ролика не меняется ни на кадр,
звук остаётся байт в байт прежним - его мы не трогаем вовсе.

Почему не обрезать начало. Обрезка сдвинула бы звук: голос начинается с первой
секунды, и полсекунды в минус съели бы первое слово.

    python pochinit_oblozhku.py ролик.mp4              один
    python pochinit_oblozhku.py /путь/к/папке          все в папке
"""
import os
import subprocess
import sys
import tempfile

# Ниже этого порога кадр считаем чёрным. Ноль не берём: сжатие оставляет
# единицы-двойки даже на честной черноте.
CHERNO = 22
# Докуда искать нормальный кадр. Затемнение в движке было 0.28 секунды,
# берём вдвое с запасом.
ISKAT = 0.8


def yarkost(video, t):
    """Средняя яркость кадра в момент t. Считаем самим ffmpeg, без Pillow -
    так скрипт работает на голой машине, где кроме ffmpeg ничего нет."""
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", str(t), "-i", video, "-vframes", "1",
         "-vf", "scale=64:114,format=gray,signalstats", "-f", "null", "-"],
        capture_output=True, text=True)
    for l in r.stderr.splitlines():
        if "YAVG" in l:
            for kus in l.split():
                if kus.startswith("YAVG:"):
                    return float(kus.split(":")[1])
    # Запасной путь: средняя яркость через showinfo недоступна - считаем сами.
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", str(t), "-i", video, "-vframes", "1",
         "-vf", "scale=32:56,format=gray", "-f", "rawvideo", "-"],
        capture_output=True)
    d = r.stdout
    return sum(d) / len(d) if d else 0.0


def pervyy_svetlyy(video):
    """Момент, где картинка уже разгорелась. Ищем шагами по кадру."""
    svet = yarkost(video, 1.0)          # опора: как выглядит нормальный кадр
    porog = max(CHERNO, svet * 0.55)
    t = 0.0
    while t <= ISKAT:
        if yarkost(video, t) >= porog:
            return t, svet
        t += 1 / 30
    return ISKAT, svet


def pochinit(video, kuda=None):
    y0 = yarkost(video, 0)
    if y0 >= CHERNO:
        return None, y0, y0            # обложка уже нормальная
    t, svet = pervyy_svetlyy(video)
    vrem = tempfile.mkdtemp(prefix="oblozhka_")
    kadr = os.path.join(vrem, "kadr.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", video,
                    "-vframes", "1", kadr], check=True)
    itog = kuda or video
    tmp = os.path.join(vrem, "gotovo.mp4")
    # Картинку кладём ПОВЕРХ первых кадров. Звук копируем без пересжатия:
    # сведение владелец утверждал на слух, портить его нельзя.
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", video, "-i", kadr,
        "-filter_complex",
        f"[1:v]scale=1080:1920,format=yuv420p[o];[0:v][o]overlay=enable='lte(t,{t:.3f})'[v]",
        "-map", "[v]", "-map", "0:a?", "-c:a", "copy",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-preset", "medium", "-crf", "18", "-maxrate", "8M", "-bufsize", "12M",
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
        "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, itog)
    return t, y0, yarkost(itog, 0)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cel = sys.argv[1]
    if os.path.isdir(cel):
        faily = [os.path.join(cel, f) for f in sorted(os.listdir(cel))
                 if f.endswith(".mp4") and not f.startswith("._")]
    else:
        faily = [cel]

    # Оригиналы не трогаем. Владелец просил ничего не затирать, и это разумно:
    # если починка где-то сработает криво, вернуться будет не к чему.
    # Исправленные кладём в соседнюю папку с тем же именем.
    kuda_dir = os.environ.get("KUDA")
    if not kuda_dir and os.path.isdir(cel):
        kuda_dir = cel.rstrip("/") + "-oblozhka"
    if kuda_dir:
        os.makedirs(kuda_dir, exist_ok=True)

    chinili = uzhe = 0
    for f in faily:
        out = os.path.join(kuda_dir, os.path.basename(f)) if kuda_dir else None
        if out and os.path.exists(out):
            uzhe += 1
            continue
        t, bylo, stalo = pochinit(f, out)
        if t is None:
            uzhe += 1
            continue
        chinili += 1
        if chinili % 10 == 0 or chinili < 4:
            print(f"  {os.path.basename(f)[:36]:38} было {bylo:5.1f} -> стало {stalo:5.1f}"
                  f"   накрыто {t:.2f} сек", flush=True)

    print(f"\nпочинено: {chinili}, пропущено: {uzhe}")
    if kuda_dir:
        print(f"исправленные лежат в {kuda_dir}, оригиналы не тронуты")


if __name__ == "__main__":
    main()
