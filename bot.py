#!/usr/bin/env python3
"""
Telegram-бот Reels Studio: генерация промо-Reels прямо в чате (без Mini App).
Диалог: /start -> проект -> язык -> голос -> видео приходит файлом в чат.
Работает через webhook (нужен публичный HTTPS), что дружит с бесплатными
хостингами, которые засыпают: входящий апдейт сам будит контейнер.

ENV: BOT_TOKEN (обяз.), PUBLIC_URL (обяз. для авто-регистрации webhook),
     WEBHOOK_SECRET (опц., иначе выводится из токена).
"""
import os, hashlib, asyncio, html

import httpx
from fastapi import APIRouter, Request, HTTPException

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

LANGS = [("kk", "🇰🇿 Қазақша"), ("ru", "🇷🇺 Русский"), ("both", "🇰🇿+🇷🇺 Оба")]
VOICE_TITLES = {"laura": "🎙 Laura", "bala": "🎙 Bala"}

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
    await tg("sendMessage", chat_id=chat_id,
             text="⏳ Генерирую видео…\nПодбираю стоковые кадры, озвучиваю клон-голосом и монтирую.\n"
                  "Это займёт 1–3 минуты — пришлю файлом сюда же.")
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
    titles = {"kk": "🇰🇿 Қазақша нұсқасы", "ru": "🇷🇺 Русская версия"}
    for lang in ("kk", "ru"):
        p = core.out_path(job_id, project, lang)
        if os.path.exists(p):
            await send_video(chat_id, p, f"{titles[lang]} — {project}")
    await tg("sendMessage", chat_id=chat_id, text="✅ Готово! Ещё одно — /start")


async def handle_update(u: dict):
    msg = u.get("message") or {}
    cq = u.get("callback_query") or {}

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
        _PICK[chat_id] = {"project": data[2:]}
        await tg("editMessageText", chat_id=chat_id, message_id=cq["message"]["message_id"],
                 text="Язык ролика:",
                 reply_markup=kb([[{"text": t, "callback_data": f"l:{c}"}] for c, t in LANGS]))

    elif data.startswith("l:"):
        _PICK.setdefault(chat_id, {})["langs"] = data[2:]
        await tg("editMessageText", chat_id=chat_id, message_id=cq["message"]["message_id"],
                 text="Голос диктора:",
                 reply_markup=kb([[{"text": VOICE_TITLES[v], "callback_data": f"v:{v}"}]
                                  for v in core.VOICES]))

    elif data.startswith("v:"):
        pick = _PICK.get(chat_id, {})
        project = pick.get("project")
        if project not in reel_engine.PROJECTS:
            await tg("sendMessage", chat_id=chat_id, text="Начни заново: /start")
            return
        await start_generation(chat_id, uid, project, pick.get("langs", "both"), data[2:])


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
    if not (BOT_TOKEN and PUBLIC_URL):
        print("bot: BOT_TOKEN/PUBLIC_URL не заданы — бот выключен", flush=True)
        return
    url = f"{PUBLIC_URL}/tg/{WEBHOOK_SECRET}"
    r = await tg("setWebhook", url=url, allowed_updates=["message", "callback_query"],
                 drop_pending_updates=True)
    print("bot: setWebhook ->", r, flush=True)
