#!/usr/bin/env python3
"""
Общее ядро генерации: очередь джобов + запуск reel_engine.
Используют оба фронта — Mini App (app.py) и Telegram-бот (bot.py).
"""
import os, sys, uuid, asyncio, time

import reel_engine

APP_DIR = os.path.dirname(os.path.abspath(__file__))
JOBS_DIR = os.path.join(APP_DIR, "jobs")
os.makedirs(JOBS_DIR, exist_ok=True)

# доступные голоса-клоны (человеческий казах без акцента)
VOICES = {
    "laura": "xKWShjEXraJurmIX5TZM",
    "bala":  "M4jzBCMPD6005WAnM0H9",
}
PROJECTS = list(reel_engine.PROJECTS.keys())

JOBS = {}   # job_id -> {status, project, langs, files, error, owner}
_SEM = asyncio.Semaphore(int(os.environ.get("MAX_CONCURRENT", "2")))  # не форк-бомбить ffmpeg
_RATE = {}  # user_id -> [timestamps за сутки]
DAILY_QUOTA = int(os.environ.get("DAILY_QUOTA", "15"))

SUFFIX = {"kk": "KZ", "ru": "RU"}


def rate_ok(uid: str) -> bool:
    """Не более DAILY_QUOTA генераций на пользователя в сутки (защита кошелька/квот)."""
    now = time.time()
    lst = [t for t in _RATE.get(uid, []) if now - t < 86400]
    if len(lst) >= DAILY_QUOTA:
        _RATE[uid] = lst
        return False
    lst.append(now)
    _RATE[uid] = lst
    return True


def out_path(job_id: str, project: str, lang: str) -> str:
    return os.path.join(JOBS_DIR, job_id, f"{project}-STOCK-{SUFFIX[lang]}.mp4")


def new_job(project: str, langs: str, voice: str, owner: str) -> str:
    """Регистрирует джоб и запускает его в фоне. Возвращает job_id."""
    job_id = uuid.uuid4().hex[:12]
    JOBS[job_id] = {"status": "running", "project": project, "langs": langs,
                    "files": {}, "error": "", "ts": time.time(), "owner": owner}
    asyncio.create_task(run_job(job_id, project, langs, VOICES.get(voice, VOICES["laura"])))
    return job_id


async def run_job(job_id, project, langs, voice_id):
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
        log = (out or b"").decode()[-800:]
        if proc.returncode != 0:
            job["status"] = "error"
            job["error"] = log
            return
        files = {}
        for lang in ("kk", "ru"):
            if os.path.exists(out_path(job_id, project, lang)):
                files[lang] = f"/api/file/{job_id}/{lang}"
        job["files"] = files
        job["status"] = "done" if files else "error"
        if not files:
            job["error"] = log
    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)
