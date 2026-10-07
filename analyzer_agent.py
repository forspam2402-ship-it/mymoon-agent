import json
import asyncio
import sys
import anthropic
import telegram
from datetime import datetime
from config import *
from sheets_helper import get_new_vacancies, get_pending_vacancies, update_score, update_status, init_sheet
from helpers import send_job_with_buttons

def load_profile() -> str:
    import os
    profile_text = ""
    for filename in os.listdir(PROFILE_DIR):
        path = os.path.join(PROFILE_DIR, filename)
        try:
            if filename.endswith(".docx"):
                import docx
                doc = docx.Document(path)
                text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                profile_text += f"\n=== {filename} ===\n{text[:1500]}\n"
            elif filename.endswith(".pdf") and "photo" not in filename:
                import fitz
                doc = fitz.open(path)
                text = "".join([page.get_text() for page in doc])
                profile_text += f"\n=== {filename} ===\n{text[:1500]}\n"
        except Exception as e:
            print(f"  Ошибка загрузки {filename}: {e}")
            continue
    return profile_text[:8000]

def analyze_match(job: dict, profile: str) -> tuple:
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": f"""Оцени насколько вакансия подходит кандидату на позиции Senior Project Manager или Program Manager.

ПРОФИЛЬ:
{profile[:4000]}

ВАКАНСИЯ:
Должность: {job.get('title')}
Компания: {job.get('company')}
Источник: {job.get('source')}

Оцени релевантность опыта кандидата в управлении проектами и программами,
включая ответственность, масштаб и требуемый уровень роли. Не приписывай
кандидату опыт или достижения, которых нет в профиле.

Верни JSON:
{{"score": 1-10, "comment": "1 предложение почему подходит или нет"}}

Только JSON."""}]
        )
        result = message.content[0].text.strip()
        result = result.replace("```json", "").replace("```", "").strip()
        start = result.find("{")
        end = result.rfind("}") + 1
        data = json.loads(result[start:end])
        return data.get("score", 5), data.get("comment", "")
    except Exception as e:
        return 5, f"Ошибка: {e}"

async def run_analyzer():
    if datetime.now().weekday() >= 5:
        print("Выходной день.")
        sys.exit(0)

    print(f"[{datetime.now().strftime('%H:%M')}] Аналитик запущен")
    init_sheet()

    profile = load_profile()
    if not profile:
        print("  ОШИБКА: профиль пустой, проверь папку profile\\")
        return
    print(f"  Профиль загружен: {len(profile)} символов")

    # Новые вакансии
    vacancies = get_new_vacancies()
    print(f"  Новых вакансий: {len(vacancies)}")

    approved = 0
    for vac in vacancies:
        score, comment = analyze_match(vac, profile)
        update_score(vac['row'], score, comment)
        update_status(vac['row'], "Viewed")
        print(f"  [{vac['num']}] {vac['title']} — {score}/10")
        if score >= 5:
            vac['score'] = score
            vac['reason'] = comment
            for attempt in range(3):
                try:
                    await send_job_with_buttons(vac)
                    break
                except Exception as e:
                    print(f"  Telegram ошибка (попытка {attempt + 1}): {e}")
                    await asyncio.sleep(5)
            update_status(vac['row'], "Approval")
            approved += 1
            await asyncio.sleep(2)

    # Повторная отправка — только Approval (уже одобренные ранее)
    pending = get_pending_vacancies()
    print(f"  Ожидают решения: {len(pending)}")

    for vac in pending:
        score = int(vac.get('score', 0)) if vac.get('score') else 0
        if score < 5:
            update_status(vac['row'], "Viewed")  # оставляем как Viewed, не трогаем
            continue
        vac['reason'] = f"Повтор — оценка {score}/10"
        for attempt in range(3):
            try:
                await send_job_with_buttons(vac)
                break
            except Exception as e:
                print(f"  Telegram ошибка (попытка {attempt + 1}): {e}")
                await asyncio.sleep(5)
        update_status(vac['row'], "Approval")

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=(
            f"Аналитик завершил работу.\n"
            f"Новых проверено: {len(vacancies)}\n"
            f"Отправлено на решение: {approved + len(pending)}"
        )
    )
    print(f"  Готово. Отправлено в Telegram: {approved + len(pending)}")

asyncio.run(run_analyzer())