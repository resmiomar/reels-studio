#!/usr/bin/env python3
"""
Reels SaaS backend — FastAPI.
Два фронта поверх одного движка (core.py -> reel_engine.py):
  1) Telegram-бот (bot.py) — генерация прямо в чате;
  2) Telegram Mini App (static/index.html) + JSON API.
ENV: PEXELS_KEY, EL_KEY (обязательно), BOT_TOKEN (бот + валидация initData),
     PUBLIC_URL (публичный HTTPS-адрес сервиса).
"""
import os, hmac, hashlib, json
from urllib.parse import parse_qsl
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import bot          # первым: подхватывает локальный .env до чтения переменных в core
import core
import reel_engine

APP_DIR = os.path.dirname(os.path.abspath(__file__))
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.setup()          # регистрируем webhook Telegram при старте
    yield


app = FastAPI(title="Reels Studio", lifespan=lifespan)
app.include_router(bot.router)


def _auth_user(init_data: str):
    """Валидирует Telegram WebApp initData -> возвращает telegram user_id (str) или None.
    Без BOT_TOKEN -> 'dev' (открытый локальный режим; на проде BOT_TOKEN обязателен)."""
    if not BOT_TOKEN:
        return "dev"
    try:
        pairs = dict(parse_qsl(init_data, keep_blank_values=True))
        got = pairs.pop("hash", "")
        check = "\n".join(f"{k}={pairs[k]}" for k in sorted(pairs))
        secret = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        calc = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(calc, got):
            return None
        user = json.loads(pairs.get("user", "{}"))
        return str(user.get("id") or "") or None
    except Exception:
        return None


@app.get("/api/config")
async def config():
    return {
        "projects": [{"id": p, "title": reel_engine.PROJECTS[p]["title"]["ru"]} for p in core.PROJECTS],
        "voices": list(core.VOICES.keys()),
    }


@app.get("/api/health")
async def health():
    """Пинг для аптайм-мониторов (не даёт бесплатному хостингу уснуть)."""
    return {"ok": True, "jobs": len(core.JOBS)}


@app.post("/api/generate")
async def generate(req: Request):
    body = await req.json()
    uid = _auth_user(body.get("initData") or body.get("init_data") or "")
    if not uid:
        raise HTTPException(401, "auth required")
    if not core.rate_ok(uid):
        raise HTTPException(429, "daily limit reached")
    project = body.get("project")
    if project not in reel_engine.PROJECTS:
        raise HTTPException(400, "unknown project")
    langs = body.get("langs", "both")   # kk | ru | both
    if isinstance(langs, list):
        langs = langs[0] if len(langs) == 1 else "both"
    if langs not in ("kk", "ru", "both"):
        langs = "both"
    return {"job_id": core.new_job(project, langs, body.get("voice", "laura"), uid)}


@app.get("/api/status/{job_id}")
async def status(job_id: str):
    job = core.JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "no job")
    return job


@app.get("/api/file/{job_id}/{lang}")
async def file(job_id: str, lang: str):
    job = core.JOBS.get(job_id)
    if not job or lang not in core.SUFFIX:
        raise HTTPException(404, "no file")
    p = core.out_path(job_id, job["project"], lang)
    if not os.path.exists(p):
        raise HTTPException(404, "not ready")
    return FileResponse(p, media_type="video/mp4", filename=f"{job['project']}-{lang}.mp4")


app.mount("/", StaticFiles(directory=os.path.join(APP_DIR, "static"), html=True), name="static")
