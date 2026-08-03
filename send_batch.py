#!/usr/bin/env python3
"""
Отправляет готовые ролики в Telegram владельцу с ПОНЯТНОЙ РУССКОЙ подписью,
чтобы он не путал рынки: языков он не знает, по картинке их не различить.

  python send_batch.py <папка-с-mp4>

Chat id берём из первого входящего апдейта (владелец должен один раз нажать
/start у бота: Telegram не даёт боту писать первым).
"""
import os, sys, json, glob, re, time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bot as B          # подтягивает .env и BOT_TOKEN
import reel_engine as R

API = f"https://api.telegram.org/bot{B.BOT_TOKEN}"
CODE2LANG = {v: k for k, v in R.LANG_CODE.items()}   # KZ -> kk


def api(method, **params):
    req = urllib.request.Request(f"{API}/{method}",
                                 data=json.dumps(params).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))


def find_chat():
    """Кому слать. getUpdates тут бесполезен: бот работает polling-ом и уже
    съел апдейты, поэтому берём chat_id из файла, куда его пишет сам бот."""
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "known_chats.json")
    try:
        ids = json.load(open(f))
        return ids[-1] if ids else None
    except Exception:
        return None


def send_file(chat_id, path, caption, kind="video", **extra):
    """multipart вручную: тянуть зависимости ради одной отправки незачем.
    kind: video | audio | document — метод и имя поля выводятся из него."""
    meth = {"video": "sendVideo", "audio": "sendAudio",
            "photo": "sendPhoto", "document": "sendDocument"}[kind]
    mime = {"video": "video/mp4", "audio": "audio/mpeg",
            "photo": "image/png", "document": "application/octet-stream"}[kind]
    b = b"----ibook" + str(time.time()).encode()
    body = b""
    fields = [("chat_id", str(chat_id)), ("caption", caption)]
    if kind == "video": fields.append(("supports_streaming", "true"))
    fields += [(k, str(v)) for k, v in extra.items()]
    for k, v in fields:
        body += (b"--" + b + b"\r\nContent-Disposition: form-data; name=\"" + k.encode()
                 + b"\"\r\n\r\n" + v.encode() + b"\r\n")
    body += (b"--" + b + b"\r\nContent-Disposition: form-data; name=\"" + kind.encode()
             + b"\"; filename=\"" + os.path.basename(path).encode()
             + b"\"\r\nContent-Type: " + mime.encode() + b"\r\n\r\n"
             + open(path, "rb").read() + b"\r\n--" + b + b"--\r\n")
    req = urllib.request.Request(f"{API}/{meth}", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={b.decode()}"})
    return json.load(urllib.request.urlopen(req, timeout=300))


def send_video(chat_id, path, caption):
    return send_file(chat_id, path, caption, "video")


def send_photo(chat_id, path, caption):
    return send_file(chat_id, path, caption, "photo")


def send_audio(chat_id, path, caption, title=""):
    return send_file(chat_id, path, caption, "audio", **({"title": title} if title else {}))


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else "."
    # Порядок отправки: сначала домашний рынок, потом СНГ, потом остальное.
    ORDER = ["Казахстан", "Россия", "Узбекистан", "Украина", "Турция",
             "Китай", "США", "Германия", "Италия", "Испания", "Франция"]
    def rank(path):
        n = os.path.basename(path)
        for i, c in enumerate(ORDER):
            if f"-{c}-" in n:
                return (i, n)
        return (len(ORDER), n)
    files = sorted(glob.glob(os.path.join(d, "*.mp4")), key=rank)
    if not files:
        print("нет mp4 в", d); return
    chat = find_chat()
    if not chat:
        print("Не знаю, кому слать: открой @ibook_videos_bot и нажми /start, потом запусти снова.")
        return
    print(f"chat_id={chat}, роликов {len(files)}")
    FLAGS = {"Казахстан": "🇰🇿", "Россия": "🇷🇺", "Украина": "🇺🇦", "Узбекистан": "🇺🇿",
             "Турция": "🇹🇷", "Китай": "🇨🇳", "США": "🇺🇸", "Германия": "🇩🇪",
             "Италия": "🇮🇹", "Испания": "🇪🇸", "Франция": "🇫🇷"}
    for f in files:
        name = os.path.basename(f)[:-4]
        m = re.match(r"(\d+)-([^-]+)-(.+)$", name)   # 001-Италия-итальянский
        if m:
            num, country, lang = m.groups()
            cap = f"№{int(num)} · {FLAGS.get(country,'🎬')} для страны: {country} · язык: {lang}"
        else:
            cap = name
        try:
            send_video(chat, f, cap)
            print("  отправлено:", name)
        except Exception as e:
            print("  ОШИБКА:", name, str(e)[:80])


if __name__ == "__main__":
    main()
