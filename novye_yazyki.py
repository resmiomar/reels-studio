#!/usr/bin/env python3
"""
Заготовки сценариев для испанского, французского и итальянского.

Что уже есть и что нужно. У английского года всё готово: пятьдесят две недели
по три ролика, расписанные аудитории, кадры, тайминги, теги и музыка. У трёх
южных языков - по два ролика из ста пятидесяти шести.

Главная экономия в том, что переписывать надо НЕ ВСЁ. Кадры в сценарии
написаны по-английски нарочно: они идут запросом в фотосток, и переводить их
не только не нужно, но и вредно - сток по-испански ничего не найдёт. Теги
тоже общие, они на латинице. Тайминги, аудитория и музыка от языка не зависят
вовсе.

Значит переносим костяк и пишем заново только четыре поля:

    hook      крючок в первые секунды
    vo        сам текст, который читает голос
    cta       призыв в конце
    caption   подпись к посту

Кадры переносим с одной правкой: народность в них меняется. В английском
сценарии стоит «A young barber», для Испании нужен испанский типаж, иначе в
ролике для Мадрида будут скандинавские лица.

Скрипт делает заготовку: берёт английский костяк, подставляет рынок и
оставляет четыре поля ПУСТЫМИ. Дальше их заполняет человек или языковая
модель - но заполняет осмысленно, а не машинным переводом. Владелец про это
сказал прямо: носитель видит перевод с первой строки.

    python novye_yazyki.py es          сделать заготовку испанского
    python novye_yazyki.py --счёт      сколько заполнено
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCEN = os.path.join(HERE, "scenarii")

# Типаж в кадре по рынку. Без этого сток отдаёт кого попало: в ролике для
# Севильи оказываются северяне, и местный это замечает сразу.
TIPAZH = {
    "es": ("spanish", "Spain"),
    "fr": ("french", "France"),
    "it": ("italian", "Italy"),
}
# Что меняем в английских заданиях к кадрам. Ищем национальность и место.
ZAMENA = [
    (r"\bAmerican\b", None), (r"\bAmerica\b", None),
    (r"\bUS\b", None), (r"\bNew York\b", None),
]


def kadr_pod_rynok(prompt, nar):
    """Задание к кадру под нужный рынок: народность подставляем, остальное
    оставляем как есть - кадрирование и свет проверены на других языках."""
    t = prompt
    for shablon, _ in ZAMENA:
        t = re.sub(shablon, nar, t, flags=re.I)
    # Если народности в задании нет вовсе - добавляем к первому человеку.
    if nar not in t.lower():
        t = re.sub(r"\b(a|an)\s+(young\s+)?(barber|hairdresser|woman|man|client|stylist)",
                   lambda m: f"a {m.group(2) or ''}{nar} {m.group(3)}", t, count=1, flags=re.I)
    return " ".join(t.split())


def zagotovka(lang):
    en = json.load(open(os.path.join(SCEN, "videos_en.json"), encoding="utf-8"))
    put = os.path.join(SCEN, f"videos_{lang}.json")
    est = json.load(open(put, encoding="utf-8")) if os.path.exists(put) else []
    # Уже написанное не трогаем: два ролика на язык сделаны носителем и
    # переписывать их незачем.
    gotovo = {(v["week"], v["slot"]): v for v in est}
    nar, strana = TIPAZH[lang]

    out = []
    novyh = 0
    for v in en:
        k = (v["week"], v["slot"])
        if k in gotovo:
            out.append(gotovo[k])
            continue
        novyh += 1
        out.append({
            "week": v["week"], "slot": v["slot"], "aud": v.get("aud", "master"),
            "title": v.get("title", ""),
            # Четыре поля под живой текст. Пустые нарочно: пусть лучше сценарий
            # честно ждёт автора, чем в канал уйдёт машинный перевод.
            "hook": "", "vo": "", "cta": "", "caption": "",
            "shots": [{**s, "prompt": kadr_pod_rynok(s.get("prompt", ""), nar)}
                      for s in v.get("shots", [])],
            "tags": v.get("tags", ""),
            "music": v.get("music", ""),
        })
    json.dump(out, open(put, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return len(out), novyh


def schet():
    print("  ЯЗЫК          ВСЕГО  С ТЕКСТОМ  ПУСТЫХ")
    for l in ("es", "fr", "it"):
        p = os.path.join(SCEN, f"videos_{l}.json")
        if not os.path.exists(p):
            print(f"  {l}: файла нет")
            continue
        d = json.load(open(p, encoding="utf-8"))
        s = sum(1 for v in d if v.get("vo", "").strip())
        print(f"  {l:13} {len(d):5}  {s:9}  {len(d) - s:6}")


if __name__ == "__main__":
    if "--счёт" in sys.argv or "--schet" in sys.argv:
        schet()
    else:
        for l in (sys.argv[1:] or ["es", "fr", "it"]):
            vsego, novyh = zagotovka(l)
            print(f"  {l}: всего {vsego}, добавлено заготовок {novyh}")
        print()
        schet()
