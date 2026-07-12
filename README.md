# Reels Studio — SaaS (Telegram Mini App)

Генерация вертикальных промо-Reels (9:16) для проектов через Telegram Mini App.
Кадры — бесплатный сток Pexels, голос — клон пользователя в ElevenLabs (казах без акцента),
музыка + монтаж — ffmpeg. Версии на казахском и русском, разные кадры.

## Как работает
1. Пользователь открывает Mini App из бота (кнопка-меню).
2. Выбирает продукт (Qujat/ibook/…), язык, голос → «Сгенерировать».
3. Backend запускает `reel_engine.py`, возвращает готовые .mp4 → показ + скачивание в приложении.

## Локальный запуск
```bash
cd ~/reels-saas
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PEXELS_KEY=...   EL_KEY=sk_...
uvicorn app:app --reload --port 8000
# открыть http://localhost:8000
```
Нужен установленный **ffmpeg** (`brew install ffmpeg`).

## Деплой на Railway
1. `railway init` в этой папке (или через дашборд, GitHub-репо).
2. Переменные окружения:
   - `PEXELS_KEY` — ключ Pexels
   - `EL_KEY` — ключ ElevenLabs (Creator, с клонами Laura/Bala)
   - `BOT_TOKEN` — токен бота. **ОБЯЗАТЕЛЬНО на проде**: без него `/api/generate` работает в открытом dev-режиме (uid='dev') — любой сможет тратить ваши кредиты. С BOT_TOKEN запросы валидируются по подписи Telegram и привязываются к user_id.
   - `DAILY_QUOTA` — лимит генераций на пользователя в сутки (по умолчанию 15)
   - `MAX_CONCURRENT` — сколько роликов рендерить параллельно (по умолчанию 2)
   - `PUBLIC_URL` — публичный URL сервиса (Railway выдаёт)
3. ffmpeg ставится автоматически (`nixpacks.toml`).
4. Деплой → получите URL вида `https://xxx.up.railway.app`.

## Подключить к боту (без кода — через BotFather)
1. `@BotFather` → `/newbot` (или существующий бот).
2. `/setmenubutton` → выбрать бота → ввести URL Mini App (Railway URL) → название кнопки, напр. «🎬 Сделать видео».
3. Теперь в боте внизу кнопка открывает Mini App.
   (Либо `/setdomain` для Web App при inline-кнопках.)

## Голоса (клоны в ElevenLabs)
`app.py → VOICES`: `laura`, `bala` (voice_id клонов). Добавить новые — склонировать в
ElevenLabs и вписать voice_id.

## Проекты и кадры
`reel_engine.py → PROJECTS`: тема + сценарий + запросы стока на каждый проект.
ВАЖНО: кадры строго по теме (бухгалтерия ≠ трейдинг-графики). Добавить проект — новый ключ в PROJECTS.

## Безопасность (уже сделано после ревью)
- ✅ Валидация Telegram initData + привязка job к user_id (при заданном BOT_TOKEN).
- ✅ Дневная квота на пользователя (`DAILY_QUOTA`) — защита кредитов/квот от слива.
- ✅ Семафор параллельных генераций (`MAX_CONCURRENT`) — не форк-бомбить ffmpeg.
- ✅ Изолированный per-job WORK-скретч — конкурентные джобы не затирают друг друга.
- `/api/status` и `/api/file` защищены неугадываемым job_id (capability-URL, 48 бит).

## TODO (дальнейшее продакшен-упрочнение)
- Очередь задач (Redis/RQ) + персистентный JOBS вместо in-memory (теряется при рестарте).
- Хранилище результатов (S3/диск) + чистка старых job/файлов (сейчас растут в jobs/).
- Проверка владельца (initData) и на /api/status,/api/file, не только capability-URL.
- Учёт расхода кредитов ElevenLabs/Pexels + fail-closed при исчерпании бюджета.
- Оплата/тарифы (Telegram Stars или Kaspi).
