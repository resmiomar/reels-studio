#!/usr/bin/env python3
"""
Reels SaaS backend — FastAPI.
Отдаёт Telegram Mini App (static/index.html) и API для генерации промо-Reels.
Пайплайн: reel_engine.py (сток Pexels + клон-голос ElevenLabs + музыка + ffmpeg).
ENV: PEXELS_KEY, EL_KEY (обязательно), BOT_TOKEN (для валидации initData, опц.),
     PUBLIC_URL (URL сервиса, для Mini App). Голоса-клоны зашиты в reel_engine.VOICES.
"""
import os, sys, uuid, asyncio, hmac, hashlib, json, time
from urllib.parse import parse_qsl
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import reel_engine  # для списка проектов/голосов

APP_DIR = os.path.dirname(os.path.abspath(__file__))
JOBS_DIR = os.path.join(APP_DIR, "jobs")
os.makedirs(JOBS_DIR, exist_ok=True)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# доступные голоса-клоны (человеческий казах без акцента)
VOICES = {
    "laura": "xKWShjEXraJurmIX5TZM",
    "bala":  "M4jzBCMPD6005WAnM0H9",
}
PROJECTS = list(reel_engine.PROJECTS.keys())

app = FastAPI(title="Reels SaaS")
JOBS = {}  # job_id -> {status, project, langs, files, error, owner}
_SEM = asyncio.Semaphore(int(os.environ.get("MAX_CONCURRENT", "2")))  # не форк-бомбить ffmpeg
_RATE = {}  # user_id -> [timestamps за сутки]
DAILY_QUOTA = int(os.environ.get("DAILY_QUOTA", "15"))


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


def _rate_ok(uid: str) -> bool:
    """Не более DAILY_QUOTA генераций на пользователя в сутки (защита кошелька/квот)."""
    now = time.time()
    lst = [t for t in _RATE.get(uid, []) if now - t < 86400]
    if len(lst) >= DAILY_QUOTA:
        _RATE[uid] = lst
        return False
    lst.append(now)
    _RATE[uid] = lst
    return True


async def _run_job(job_id, project, langs, voice_id):
    job = JOBS[job_id]
    out_dir = os.path.join(JOBS_DIR, job_id)
    os.makedirs(out_dir, exist_ok=True)
    env = dict(os.environ)
    env.update({
        "PROJECT": project,
        "OUT_DIR": out_dir,
        "WORK": os.path.join(out_dir, "work"),   # ИЗОЛИРОВАННЫЙ скретч на job (иначе конкурентные джобы затирают друг друга)
        "VOICE_KK": f"eleven:{voice_id}",
        "VOICE_RU": f"eleven:{voice_id}",
    })
    if langs in ("kk", "ru"):
        env["LANGS_ONLY"] = langs
    try:
        async with _SEM:   # ограничение параллельных генераций
            proc = await asyncio.create_subprocess_exec(
                sys.executable, os.path.join(APP_DIR, "reel_engine.py"),
                env=env, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
            )
            out, _ = await proc.communicate()
        if proc.returncode != 0:
            job["status"] = "error"
            job["error"] = (out or b"").decode()[-800:]
            return
        files = {}
        for lang, suffix in (("kk", "KZ"), ("ru", "RU")):
            p = os.path.join(out_dir, f"{project}-STOCK-{suffix}.mp4")
            if os.path.exists(p):
                files[lang] = f"/api/file/{job_id}/{lang}"
        job["files"] = files
        job["status"] = "done" if files else "error"
        if not files:
            job["error"] = (out or b"").decode()[-800:]
    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)


@app.get("/api/config")
async def config():
    return {
        "projects": [{"id": p, "title": reel_engine.PROJECTS[p]["title"]["ru"]} for p in PROJECTS],
        "voices": list(VOICES.keys()),
    }


@app.post("/api/generate")
async def generate(req: Request):
    body = await req.json()
    uid = _auth_user(body.get("initData", ""))
    if not uid:
        raise HTTPException(401, "auth required")
    if not _rate_ok(uid):
        raise HTTPException(429, "daily limit reached")
    project = body.get("project")
    langs = body.get("langs", "both")   # kk | ru | both
    if langs not in ("kk", "ru", "both"):
        langs = "both"
    voice = body.get("voice", "laura")
    if project not in reel_engine.PROJECTS:
        raise HTTPException(400, "unknown project")
    voice_id = VOICES.get(voice, VOICES["laura"])
    job_id = uuid.uuid4().hex[:12]
    JOBS[job_id] = {"status": "running", "project": project, "langs": langs,
                    "files": {}, "error": "", "ts": time.time(), "owner": uid}
    asyncio.create_task(_run_job(job_id, project, langs, voice_id))
    return {"job_id": job_id}


@app.get("/api/status/{job_id}")
async def status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "no job")
    return job


@app.get("/api/file/{job_id}/{lang}")
async def file(job_id: str, lang: str):
    suffix = {"kk": "KZ", "ru": "RU"}.get(lang)
    job = JOBS.get(job_id)
    if not job or not suffix:
        raise HTTPException(404, "no file")
    p = os.path.join(JOBS_DIR, job_id, f"{job['project']}-STOCK-{suffix}.mp4")
    if not os.path.exists(p):
        raise HTTPException(404, "not ready")
    return FileResponse(p, media_type="video/mp4",
                        filename=f"{job['project']}-{lang}.mp4")


app.mount("/", StaticFiles(directory=os.path.join(APP_DIR, "static"), html=True), name="static")
