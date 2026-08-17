#!/usr/bin/env python3
"""
Подключение нового аккаунта ElevenLabs и выбор голоса.

Зачем. Прежний аккаунт слетел с Creator на бесплатный уровень, и вместе с ним
отвалился клонированный голос Laura-KZ: клоны на бесплатном тарифе запрещены,
API отвечает 401. Владелец купил подписку на новом аккаунте.

Ключ берём ИЗ ФАЙЛА, а не из переписки: в чате он остался бы навсегда.

    python novyy_klyuch.py                 что за тариф и сколько знаков
    python novyy_klyuch.py голоса          какие голоса доступны
    python novyy_klyuch.py проба <id>      сказать фразу этим голосом
"""
import json, os, sys, urllib.request, urllib.error

FAYL = os.path.expanduser("~/.elevenlabs_key")
API = "https://api.elevenlabs.io/v1"
FRAZA = ("Зарплату не платят два месяца? Трудовой кодекс, статья сто тринадцать. "
         "QALQAN разберёт вашу ситуацию за минуту.")


def klyuch():
    if not os.path.exists(FAYL):
        sys.exit(f"нет файла с ключом: {FAYL}\n"
                 f"сохрани его так:\n"
                 f"  printf '%s' 'КЛЮЧ' > {FAYL} && chmod 600 {FAYL}")
    k = open(FAYL).read().strip()
    if not k:
        sys.exit("файл с ключом пустой")
    return k


def zapros(put, k):
    r = urllib.request.Request(f"{API}/{put}", headers={"xi-api-key": k})
    return json.load(urllib.request.urlopen(r, timeout=30))


def podpiska(k):
    d = zapros("user/subscription", k)
    o = d.get("character_limit", 0) - d.get("character_count", 0)
    print(f"тариф:      {d.get('tier')}")
    print(f"статус:     {d.get('status')}")
    print(f"лимит:      {d.get('character_limit')}")
    print(f"осталось:   {o}")
    # Клонированные голоса доступны только на платных тарифах. Именно на этом
    # прежний аккаунт и встал: квота была, а голос не отвечал.
    print(f"клоны голоса: {'доступны' if d.get('can_use_instant_voice_cloning') else 'НЕТ, тариф не тот'}")
    print(f"роликов хватит примерно на: {o // 215}")
    return d


def golosa(k):
    d = zapros("voices", k)
    print(f"{'категория':12} {'имя':22} id")
    for v in d.get("voices", []):
        print(f"{v.get('category',''):12} {v.get('name',''):22} {v.get('voice_id')}")


def proba(k, vid):
    telo = json.dumps({"text": FRAZA, "model_id": "eleven_multilingual_v2"}).encode()
    r = urllib.request.Request(f"{API}/text-to-speech/{vid}", data=telo,
                               headers={"xi-api-key": k, "Content-Type": "application/json"})
    try:
        out = f"/Volumes/T7/ibook-reels/proba_{vid}.mp3"
        with urllib.request.urlopen(r, timeout=120) as o, open(out, "wb") as f:
            f.write(o.read())
        print("готово:", out)
    except urllib.error.HTTPError as e:
        print(f"не вышло, код {e.code}: {e.read()[:200].decode(errors='ignore')}")


if __name__ == "__main__":
    k = klyuch()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "тариф"
    if cmd == "голоса":
        golosa(k)
    elif cmd == "проба":
        proba(k, sys.argv[2])
    else:
        podpiska(k)
