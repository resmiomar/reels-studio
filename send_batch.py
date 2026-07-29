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
    """Ищем, кому слать. Без нажатого /start Telegram не позволит написать первым."""
    d = api("getUpdates", limit=20)
    for u in reversed(d.get("result", [])):
        m = u.get("message") or (u.get("callback_query") or {}).get("message") or {}
        cid = (m.get("chat") or {}).get("id")
        if cid:
            return cid
    return None


def send_video(chat_id, path, caption):
    """multipart вручную: тянуть зависимости ради одной отправки незачем."""
    b = b"----ibook" + str(time.time()).encode()
    body = b""
    for k, v in (("chat_id", str(chat_id)), ("caption", caption), ("supports_streaming", "true")):
        body += (b"--" + b + b"\r\nContent-Disposition: form-data; name=\"" + k.encode()
                 + b"\"\r\n\r\n" + v.encode() + b"\r\n")
    body += (b"--" + b + b"\r\nContent-Disposition: form-data; name=\"video\"; filename=\""
             + os.path.basename(path).encode() + b"\"\r\nContent-Type: video/mp4\r\n\r\n"
             + open(path, "rb").read() + b"\r\n--" + b + b"--\r\n")
    req = urllib.request.Request(f"{API}/sendVideo", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={b.decode()}"})
    return json.load(urllib.request.urlopen(req, timeout=300))


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else "."
    files = sorted(glob.glob(os.path.join(d, "*.mp4")))
    if not files:
        print("нет mp4 в", d); return
    chat = find_chat()
    if not chat:
        print("Не знаю, кому слать: открой @ibook_videos_bot и нажми /start, потом запусти снова.")
        return
    print(f"chat_id={chat}, роликов {len(files)}")
    for f in files:
        m = re.search(r"-([A-Z]{2})\.mp4$", f)
        lang = CODE2LANG.get(m.group(1)) if m else None
        cap = f"{R.MARKET.get(lang, os.path.basename(f))}" if lang else os.path.basename(f)
        flag = {"kk": "🇰🇿", "ru": "🇰🇿", "rf": "🇷🇺", "uk": "🇺🇦", "uz": "🇺🇿",
                "tr": "🇹🇷", "zh": "🇨🇳", "en": "🇺🇸"}.get(lang, "🎬")
        try:
            send_video(chat, f, f"{flag} {cap}")
            print("  отправлено:", os.path.basename(f), "|", cap)
        except Exception as e:
            print("  ОШИБКА:", os.path.basename(f), str(e)[:80])


if __name__ == "__main__":
    main()
