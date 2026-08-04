#!/usr/bin/env python3
"""
Telegram-бот Reels Studio: генерация промо-Reels прямо в чате (без Mini App).
Диалог: /start -> проект -> язык -> голос -> видео приходит файлом в чат.
Работает через webhook (нужен публичный HTTPS), что дружит с бесплатными
хостингами, которые засыпают: входящий апдейт сам будит контейнер.

ENV: BOT_TOKEN (обяз.), PUBLIC_URL (обяз. для авто-регистрации webhook),
     WEBHOOK_SECRET (опц., иначе выводится из токена).
"""
import os, json, hashlib, asyncio, html

import httpx
from fastapi import APIRouter, Request, HTTPException

# локальный .env — грузим ДО core/reel_engine, они читают переменные на импорте.
# (на хостинге переменные приходят из окружения, файла там нет)
_ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_ENV_FILE):
    for _line in open(_ENV_FILE):
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

import core
import reel_engine

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
PUBLIC_URL = os.environ.get("PUBLIC_URL", "").rstrip("/")
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# секрет в URL вебхука, чтобы посторонний не мог слать нам фейковые апдейты
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET") or (
    hashlib.sha256(BOT_TOKEN.encode()).hexdigest()[:24] if BOT_TOKEN else "dev"
)

router = APIRouter()

FLAG = {"kk": "🇰🇿", "ru": "🇷🇺", "zh": "🇨🇳", "de": "🇩🇪", "it": "🇮🇹",
        "tr": "🇹🇷", "uk": "🇺🇦", "es": "🇪🇸", "fr": "🇫🇷", "uz": "🇺🇿"}
VOICE_TITLES = {"laura": "🎙 Laura", "bala": "🎙 Bala"}
PAID = ("kk", "ru")     # только эти два идут на платном клон-голосе -> спрашиваем голос

# что пользователь уже выбрал: chat_id -> {"project":..., "langs":...}
_PICK = {}


async def tg(method: str, **params):
    """Вызов Telegram Bot API."""
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f"{API}/{method}", json=params)
        return r.json()


async def send_video(chat_id: int, path: str, caption: str):
    """Отправка готового mp4 файлом (лимит ботов — 50 МБ)."""
    async with httpx.AsyncClient(timeout=300) as c:
        with open(path, "rb") as f:
            r = await c.post(
                f"{API}/sendVideo",
                data={"chat_id": str(chat_id), "caption": caption, "supports_streaming": "true"},
                files={"video": (os.path.basename(path), f, "video/mp4")},
            )
        return r.json()


def kb(rows):
    return {"inline_keyboard": rows}


def projects_kb():
    rows = [[{"text": reel_engine.PROJECTS[p]["title"]["ru"], "callback_data": f"p:{p}"}]
            for p in core.PROJECTS]
    if PUBLIC_URL:
        rows.append([{"text": "🎬 Открыть приложение", "web_app": {"url": PUBLIC_URL + "/"}}])
    return kb(rows)


async def start_generation(chat_id: int, uid: str, project: str, langs: str, voice: str):
    if not core.rate_ok(uid):
        await tg("sendMessage", chat_id=chat_id,
                 text=f"⛔️ Дневной лимит исчерпан ({core.DAILY_QUOTA} видео в сутки). Возвращайся завтра.")
        return
    n = len(core.langs_of(project)) if langs == "all" else 1
    await tg("sendMessage", chat_id=chat_id,
             text=f"⏳ Собираю роликов: {n}.\nПодбираю кадры под каждый язык, озвучиваю и монтирую.\n"
                  f"Примерно {2*n}–{4*n} минут. Пришлю файлами сюда же.")
    job_id = core.new_job(project, langs, voice, uid)
    asyncio.create_task(_deliver(chat_id, job_id, project))


async def _deliver(chat_id: int, job_id: str, project: str):
    """Ждёт завершения джоба и присылает результат в чат."""
    for _ in range(240):                      # максимум ~20 минут ожидания
        job = core.JOBS.get(job_id) or {}
        if job.get("status") != "running":
            break
        await asyncio.sleep(5)
    job = core.JOBS.get(job_id) or {}
    if job.get("status") != "done":
        err = html.escape((job.get("error") or "неизвестная ошибка")[-400:])
        await tg("sendMessage", chat_id=chat_id, parse_mode="HTML",
                 text=f"❌ Не получилось собрать видео.\n<pre>{err}</pre>")
        return
    sent = 0
    for lang in job.get("langs") or []:
        p = core.out_path(job_id, project, lang)
        if os.path.exists(p):
            # подпись НА РУССКОМ: владелец не знает этих языков, по самому видео
            # он рынок не определит и ролики перепутает
            await send_video(chat_id, p,
                             f"{FLAG.get(lang,'')} {reel_engine.MARKET.get(lang, lang)}")
            sent += 1
    await tg("sendMessage", chat_id=chat_id,
             text=f"✅ Готово, роликов: {sent}. Ещё одно: /start")


CHATS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "known_chats.json")


def _remember(chat_id):
    """Запоминаем, кому можно писать: Telegram не даёт боту начать диалог первым,
    а polling съедает апдейты, поэтому getUpdates задним числом уже ничего не покажет."""
    try:
        ids = json.load(open(CHATS_FILE)) if os.path.exists(CHATS_FILE) else []
    except Exception:
        ids = []
    if chat_id not in ids:
        ids.append(chat_id)
        json.dump(ids, open(CHATS_FILE, "w"))


async def handle_update(u: dict):
    msg = u.get("message") or {}
    cq = u.get("callback_query") or {}
    for src in (msg, cq.get("message") or {}):
        cid = (src.get("chat") or {}).get("id")
        if cid:
            _remember(cid)

    if msg.get("text", "").startswith("/start") or msg.get("text", "").startswith("/new"):
        await tg("sendMessage", chat_id=msg["chat"]["id"],
                 text="👋 Reels Studio — делаю вертикальные промо-ролики.\n\nВыбери проект:",
                 reply_markup=projects_kb())
        return

    if not cq:
        return

    chat_id = cq["message"]["chat"]["id"]
    uid = str(cq["from"]["id"])
    data = cq.get("data", "")
    await tg("answerCallbackQuery", callback_query_id=cq["id"])

    if data.startswith("p:"):
        project = data[2:]
        _PICK[chat_id] = {"project": project}
        langs = core.langs_of(project)
        rows = [[{"text": f"{FLAG.get(l,'')} {core.LANG_NAME[l]}", "callback_data": f"l:{l}"}]
                for l in langs]
        # по два языка в ряд, чтобы список из десяти не растягивался на экран
        rows = [sum(rows[i:i + 2], []) for i in range(0, len(rows), 2)]
        rows.append([{"text": f"🌍 Все языки ({len(langs)})", "callback_data": "l:all"}])
        await tg("editMessageText", chat_id=chat_id, message_id=cq["message"]["message_id"],
                 text="Язык ролика:", reply_markup=kb(rows))

    elif data.startswith("l:"):
        pick = _PICK.setdefault(chat_id, {})
        pick["langs"] = data[2:]
        project = pick.get("project")
        chosen = core.langs_of(project) if pick["langs"] == "all" else [pick["langs"]]
        # голос спрашиваем только там, где он платный и его правда слышно владельцу;
        # остальные языки озвучиваются бесплатными Edge-голосами автоматически
        if not any(l in PAID for l in chosen):
            await tg("editMessageText", chat_id=chat_id, message_id=cq["message"]["message_id"],
                     text=f"Готовлю {core.LANG_NAME.get(pick['langs'], pick['langs'])}…")
            await start_generation(chat_id, uid, project, pick["langs"], "laura")
            return
        await tg("editMessageText", chat_id=chat_id, message_id=cq["message"]["message_id"],
                 text="Голос диктора (казахский и русский):",
                 reply_markup=kb([[{"text": VOICE_TITLES[v], "callback_data": f"v:{v}"}]
                                  for v in core.VOICES]))

    elif data.startswith("v:"):
        pick = _PICK.get(chat_id, {})
        project = pick.get("project")
        if project not in reel_engine.PROJECTS:
            await tg("sendMessage", chat_id=chat_id, text="Начни заново: /start")
            return
        await start_generation(chat_id, uid, project, pick.get("langs", "all"), data[2:])


@router.post("/tg/{secret}")
async def webhook(secret: str, req: Request):
    if secret != WEBHOOK_SECRET:
        raise HTTPException(403, "bad secret")
    try:
        await handle_update(await req.json())
    except Exception as e:                    # апдейт не должен ронять вебхук — иначе Telegram зарепитит
        print("bot error:", e, flush=True)
    return {"ok": True}


async def setup():
    """Регистрирует webhook в Telegram при старте (если есть токен и публичный URL)."""
    if not BOT_TOKEN:
        print("bot: BOT_TOKEN не задан — бот выключен", flush=True)
        return
    if not PUBLIC_URL:
        print("bot: PUBLIC_URL не задан — вебхук не ставим (локальный режим: python bot.py)", flush=True)
        return
    url = f"{PUBLIC_URL}/tg/{WEBHOOK_SECRET}"
    r = await tg("setWebhook", url=url, allowed_updates=["message", "callback_query"],
                 drop_pending_updates=True)
    print("bot: setWebhook ->", r, flush=True)


async def poll():
    """Long-polling: бот работает без публичного URL — можно гонять локально, бесплатно."""
    await tg("deleteWebhook", drop_pending_updates=True)
    print("bot: polling запущен, жду сообщений…", flush=True)
    offset = 0
    while True:
        try:
            async with httpx.AsyncClient(timeout=70) as c:
                r = await c.post(f"{API}/getUpdates", json={
                    "offset": offset, "timeout": 60,
                    "allowed_updates": ["message", "callback_query"]})
                data = r.json()
            for u in data.get("result", []):
                offset = u["update_id"] + 1
                try:
                    await handle_update(u)
                except Exception as e:
                    print("bot error:", e, flush=True)
        except Exception as e:
            print("poll error:", e, flush=True)
            await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(poll())
