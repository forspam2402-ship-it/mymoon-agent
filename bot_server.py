import logging
import json
import os
import anthropic
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from helpers import get_pending_job, remove_pending_job
from config import (TELEGRAM_TOKEN, ALLOWED_USERS, ANTHROPIC_KEY,
                    CANDIDATE_NAME_RU, CANDIDATE_NAME_EN, CANDIDATE_EMAIL,
                    CANDIDATE_TELEGRAM, CANDIDATE_EXPERIENCE,
                    CANDIDATE_SKILLS, CANDIDATE_LANGUAGES, CV_RU, CV_EN)

APPROVED_FILE = "C:\\jobagent\\approved_jobs.json"
logging.basicConfig(level=logging.INFO)

def load_approved() -> list:
    if os.path.exists(APPROVED_FILE):
        with open(APPROVED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_approved(data: list):
    with open(APPROVED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_allowed(user_id: int) -> bool:
    return user_id in ALLOWED_USERS

def get_cv_advice(job: dict) -> str:
    link = job.get("link", "").lower()
    title = job.get("title", "").lower()
    if any(x in link for x in ["hh.ru", "hh.uz"]):
        return CV_RU
    elif any(x in link for x in ["linkedin", "remotive", "jobicy", "jsearch"]):
        return CV_EN
    elif any(x in title for x in ["ташкент", "узбекистан", "москва", "россия"]):
        return CV_RU
    else:
        return CV_EN

def generate_cover_letter(job: dict) -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    try:
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": f"""Определи язык вакансии и напиши сопроводительное письмо на том же языке.

Вакансия: {job.get('title')}
Компания: {job.get('company')}
Источник: {job.get('source')}

Кандидат: {CANDIDATE_NAME_RU} / {CANDIDATE_NAME_EN}
Email: {CANDIDATE_EMAIL}
Telegram: {CANDIDATE_TELEGRAM}
Опыт: {CANDIDATE_EXPERIENCE}
Навыки: {CANDIDATE_SKILLS}
Языки: {CANDIDATE_LANGUAGES}

Правила:
- Для вакансий Senior Project Manager или Program Manager подчёркивай только
  подтверждённый профилем опыт управления проектами и программами.
- Не выдумывай проекты, масштабы, результаты, навыки или достижения кандидата.
- Если вакансия на русском — пиши на русском
- Если на английском — пиши на английском
- Максимум 3 абзаца, кратко и по делу
- Никакого Markdown, без # и ---
- НЕ указывай язык вакансии в начале письма
- Для русского письма: CBS = АБС
- Контакты в конце: {CANDIDATE_EMAIL} / Telegram: {CANDIDATE_TELEGRAM}
- Подпись: {CANDIDATE_NAME_RU} (если RU) или {CANDIDATE_NAME_EN} (если EN)"""}]
        )
        letter = msg.content[0].text
        letter = letter.replace("`", "'")
        return letter
    except Exception as e:
        return f"Ошибка генерации: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        await update.message.reply_text("Доступ запрещён.")
        return
    await update.message.reply_text("Mymoon Agent активен!\n\n/stats — статистика")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return
    approved = load_approved()
    total = len(approved)
    today = sum(1 for j in approved
                if j.get("approved_at", "").startswith(datetime.now().strftime("%Y-%m-%d")))
    await update.message.reply_text(f"Одобрено всего: {total}\nСегодня: {today}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_allowed(user_id):
        await query.answer("Доступ запрещён.")
        return
    await query.answer()
    data = query.data

    if data.startswith("approve_"):
        job_id = data.replace("approve_", "")
        job = get_pending_job(job_id)
        if not job:
            await query.edit_message_text("Вакансия не найдена или уже обработана.")
            return

        job["approved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        approved = load_approved()
        approved.append(job)
        save_approved(approved)

        row = job.get("sheet_row") or job.get("row")
        if row:
            try:
                from sheets_helper import update_status
                update_status(row, "Sent")
            except Exception as e:
                print(f"  Sheets ошибка: {e}")

        remove_pending_job(job_id)
        await query.edit_message_text("✅ Одобрено! Генерирую письмо...")

        letter = generate_cover_letter(job)

        keyboard = [[
            InlineKeyboardButton("🔗 Открыть вакансию", url=job.get("link", "https://hh.ru"))
        ]]

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"```\n{letter}\n```",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("skip_"):
        job_id = data.replace("skip_", "")
        job = get_pending_job(job_id)
        title = job.get("title", "Вакансия") if job else "Вакансия"
        row = job.get("sheet_row") or job.get("row") if job else None
        if row:
            try:
                from sheets_helper import update_status
                update_status(row, "Rejected")
            except Exception as e:
                print(f"  Sheets ошибка: {e}")
        remove_pending_job(job_id)
        await query.edit_message_text(f"❌ Отклонено: {title}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Mymoon Bot запущен. Ожидаю нажатий...")
    app.run_polling()

if __name__ == "__main__":
    main()