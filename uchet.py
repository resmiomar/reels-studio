#!/usr/bin/env python3
"""
Учёт отправленного: складываем, а не затираем.

Три потока английского года отработали идеально: сто пятьдесят шесть роликов,
все ушли в канал, ноль ошибок. А в списке отправленного осталась пятьдесят
одна запись. Причина - каждый поток начинал с одного и того же пустого списка,
дописывал СВОИ номера и клал файл поверх чужого. Кто закончил последним, тот и
переписал остальных.

Если это не чинить, следующий запуск решит, что ста пяти роликов нет, соберёт
их заново и отправит в канал по второму разу.

Здесь список объединяется с тем, что уже лежит на сервере, а не подменяется.

    python uchet.py en 1-156        отметить отправленными
    python uchet.py                 показать, что где
"""
import os, sys, json, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
FAYL = os.path.join(HERE, "otpravleno.json")


def razbor(spisok):
    """«1-156 4 7» превращаем в набор номеров."""
    nomera = set()
    for kus in spisok.replace(",", " ").split():
        if "-" in kus:
            a, b = kus.split("-", 1)
            nomera.update(range(int(a), int(b) + 1))
        else:
            nomera.add(int(kus))
    return nomera


def s_servera():
    """То, что лежит в ветке main прямо сейчас. Свой файл мог отстать."""
    r = subprocess.run(["git", "show", "origin/main:otpravleno.json"],
                       cwd=HERE, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {}


def slozhit(lang, nomera):
    subprocess.run(["git", "fetch", "-q", "origin", "main"], cwd=HERE, check=False)
    d = s_servera()
    svoy = json.load(open(FAYL, encoding="utf-8")) if os.path.exists(FAYL) else {}
    for k, v in svoy.items():
        d[k] = sorted(set(d.get(k, [])) | set(v))
    d[lang] = sorted(set(d.get(lang, [])) | set(nomera))
    json.dump(d, open(FAYL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return d


def slit(chuzhoy):
    """Влить в текущий список то, что записал другой поток (или мы сами до push)."""
    d = json.load(open(FAYL, encoding="utf-8")) if os.path.exists(FAYL) else {}
    m = json.load(open(chuzhoy, encoding="utf-8"))
    for k, v in m.items():
        d[k] = sorted(set(d.get(k, [])) | set(v))
    json.dump(d, open(FAYL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return d


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "slit":
        d = slit(sys.argv[2])
        print("после слияния:", {k: len(v) for k, v in d.items()})
        return
    if len(sys.argv) < 3:
        d = json.load(open(FAYL, encoding="utf-8")) if os.path.exists(FAYL) else {}
        for k, v in sorted(d.items()):
            print(f"  {k}: {len(v)} из 156")
        return
    lang = sys.argv[1]
    d = slozhit(lang, razbor(" ".join(sys.argv[2:])))
    print(f"{lang}: теперь {len(d[lang])} из 156")
    for k, v in sorted(d.items()):
        print(f"  {k}: {len(v)}")


if __name__ == "__main__":
    main()
