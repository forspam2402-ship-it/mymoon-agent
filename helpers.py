import json
import uuid
import os
import asyncio
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, ALLOWED_USERS

PENDING_FILE = "C:\\jobagent\\pending_jobs.json"

def load_pending() -> dict:
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_pending(data: dict):
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_pending_job(job: dict) -> str:
    job_id = str(uuid.uuid4())[:8]
    data = load_pending()
    data[job_id] = job
    save_pending(data)
    return job_id

def get_pending_job(job_id: str) -> dict:
    data = load_pending()
    return data.get(job_id, {})

def remove_pending_job(job_id: str):
    data = load_pending()
    if job_id in data:
        del data[job_id]
        save_pending(data)

async def send_job_with_buttons(job: dict):
    job_id = add_pending_job(job)

    keyboard = [[
        InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{job_id}"),
        InlineKeyboardButton("❌ Пропустить", callback_data=f"skip_{job_id}"),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"""🎯 {job.get('source', 'Вакансия')}

{job.get('title', '')}
Компания: {job.get('company', '')}
Локация: {job.get('location', '')}
Почему подходит: {job.get('reason', '')}

Ссылка: {job.get('link', '')}"""

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=text,
        reply_markup=reply_markup
    )