#!/usr/bin/env python3
"""
Интонация для узбекского. Ведём КАЖДУЮ фразу отдельно, а не текст одним куском.

Почему так. Владелец прислал образец живого блогера и сказал главное: «нету
эмоций как робот, точку не умеет читать». Замер это подтвердил числом: у
блогера разброс тона 57 Гц, у нашего голоса 29 - ровно вдвое меньше. Живой
человек внутри одной реплики то роняет голос, то поднимает; синтез читает
всё на одной высоте, и получается диктор с вокзала.

Движок Microsoft не принимает разметку интонации внутри текста. Зато он
принимает высоту и темп НА ЗАПРОС. Значит режем текст на фразы, каждую
синтезируем со своей высотой, темпом и громкостью, потом склеиваем. Это и
есть интонация: она рождается из перепада между фразами.

Роли фраз в нашем ролике всегда одни и те же, порядок задан сценарием:

    БОЛЬ      вопрос в лоб. Выше и быстрее: так задают неудобный вопрос.
    УЗНАВАНИЕ «это про тебя». Ниже и медленнее, доверительно.
    РЕШЕНИЕ   что даёт ibook. Ровно и уверенно, это опора.
    ВЫГОДЫ    перечисление. Слегка вверх с каждым пунктом, иначе список усыпляет.
    ПРИЗЫВ    последняя фраза. Выше и громче всего, это точка удара.

Паузы между фразами тоже разные. После вопроса пауза длиннее: вопрос должен
повиснуть. Внутри перечисления - короче, иначе список рассыпается.

    python intonaciya.py "текст" out.mp3 uz-UZ-SardorNeural
"""
import asyncio, os, re, subprocess, sys, tempfile

# Высота, темп, громкость и пауза ПОСЛЕ фразы. Подобрано по образцу владельца:
# цель - разброс тона около 57 Гц вместо наших 29.
ROLI = [
    ("боль",      "+18Hz", "+16%", "+8%",  0.34),
    ("узнавание", "-8Hz",  "+2%",  "+0%",  0.26),
    ("решение",   "+0Hz",  "+10%", "+4%",  0.20),
    ("выгоды",    "+6Hz",  "+14%", "+4%",  0.14),
    ("призыв",    "+20Hz", "+8%",  "+12%", 0.00),
]


def frazy(text):
    """Разбить на фразы по знакам конца. Точка - это и есть команда на паузу."""
    ch = [c.strip() for c in re.split(r"(?<=[.!?])\s+", text.strip()) if c.strip()]
    return ch


def rasstavit(ch):
    """Раздать фразам роли. Первая - боль, последняя - призыв, между ними
    середина растягивается на оставшиеся роли пропорционально длине текста."""
    n = len(ch)
    if n == 1:
        return [(ch[0], ROLI[4])]
    if n == 2:
        return [(ch[0], ROLI[0]), (ch[1], ROLI[4])]
    out = [(ch[0], ROLI[0])]
    seredina = ch[1:-1]
    # Середину делим на узнавание, решение и выгоды. Выгод обычно больше всего:
    # это перечисление возможностей, оно и занимает основную часть ролика.
    for i, f in enumerate(seredina):
        doli = i / max(1, len(seredina) - 1)
        rol = ROLI[1] if doli < 0.2 else ROLI[2] if doli < 0.45 else ROLI[3]
        out.append((f, rol))
    out.append((ch[-1], ROLI[4]))
    return out


async def _skazat(text, golos, ton, tempo, gromkost, put):
    import edge_tts
    c = edge_tts.Communicate(text, golos, rate=tempo, pitch=ton, volume=gromkost)
    with open(put, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])


def ozvuchit(text, put, golos="uz-UZ-SardorNeural"):
    """Собрать озвучку по фразам, с разной подачей и паузами между ними."""
    plan = rasstavit(frazy(text))
    vrem = tempfile.mkdtemp(prefix="inton_")
    kuski = []
    for i, (fraza, (imya, ton, tempo, gromkost, pauza)) in enumerate(plan):
        k = os.path.join(vrem, f"{i:03d}.mp3")
        asyncio.run(_skazat(fraza, golos, ton, tempo, gromkost, k))
        kuski.append(k)
        if pauza > 0:
            t = os.path.join(vrem, f"{i:03d}_p.mp3")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                            f"anullsrc=r=24000:cl=mono", "-t", str(pauza),
                            "-q:a", "9", t], check=True)
            kuski.append(t)
    spisok = os.path.join(vrem, "spisok.txt")
    with open(spisok, "w") as f:
        for k in kuski:
            f.write(f"file '{k}'\n")
    # Склейка через concat: куски от одного движка, пересжимать их незачем.
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0",
                    "-i", spisok, "-c", "copy", put], check=True)
    return len(plan)


if __name__ == "__main__":
    t = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "inton.mp3"
    g = sys.argv[3] if len(sys.argv) > 3 else "uz-UZ-SardorNeural"
    print(f"фраз: {ozvuchit(t, out, g)} -> {out}")
