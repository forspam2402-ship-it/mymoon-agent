import asyncio
import json
import anthropic
from datetime import datetime
from telethon import TelegramClient
from config import *

TG_API_ID = 38460534
TG_API_HASH = "890b84ecde1c1c8bc5bd30bbc3c48e3c"
SESSION_NAME = "C:\\jobagent\\tg_session"
SEEN_FILE = "C:\\jobagent\\seen_telegram.json"

CHANNELS = [
    "revacancy", "Getitrussia", "jobGeeks", "rfoundersjobs", "geekjobs",
    "hh_vacancy_development", "it_vakansii_jobs", "budujobs", "progjob",
    "devs_it", "yojob", "zarubezhom_jobs", "Remoteit", "Relocats",
    "choicy_work", "hiddengurus", "youritjobuae", "it_vacancy_relocation",
    "jobs_abroad", "relocaty_jobs", "IT_REMOTE_PROJECTS", "myjobit",
    "productconsult", "forproducts", "product_jobs", "blackproduct",
    "productvacancy", "productjobgo", "hireproproduct", "jobstobefound",
    "tophr", "hr_recrute", "HRlead", "rff_channel", "itrecruitergroup",
    "hr_only", "hrdigital", "hr_breakfast_emergency", "hrbreakfast",
]

KEYWORDS = [
    "senior project manager", "project manager", "technical project manager",
    "it project manager", "lead project manager", "delivery manager",
    "project delivery manager",
    "program manager", "programme manager", "senior program manager",
    "senior programme manager", "project director", "program director",
    "programme director", "руководитель проектов", "менеджер проектов",
    "старший менеджер проектов", "ведущий менеджер проектов",
    "руководитель программы", "руководитель программ", "менеджер программы",
    "менеджер программ", "директор проектов", "директор программы",
    "директор программ",
]

def load_seen() -> set:
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()

def save_seen(seen: set):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, ensure_ascii=False)

def passes_prefilter(text: str) -> bool:
    return any(kw in text.lower() for kw in KEYWORDS)

async def fullscan():
    print(f"[{datetime.now().strftime('%H:%M')}] Полный скан Telegram (limit=100)")

    seen = load_seen()
    print(f"  Известных постов до скана: {len(seen)}")

    posts = []
    skipped_seen = 0
    skipped_filter = 0

    client = TelegramClient(SESSION_NAME, TG_API_ID, TG_API_HASH)
    await client.start()

    for channel_name in CHANNELS:
        try:
            print(f"  Читаю: @{channel_name}...")
            channel = await client.get_entity(channel_name)
            messages = await client.get_messages(channel, limit=100)
            for msg in messages:
                if not msg.text or len(msg.text) < 50:
                    continue
                msg_id = f"{channel_name}_{msg.id}"
                if msg_id in seen:
                    skipped_seen += 1
                    continue
                if not passes_prefilter(msg.text):
                    skipped_filter += 1
                    seen.add(msg_id)
                    continue
                posts.append({
                    "id": msg_id,
                    "channel": channel_name,
                    "text": msg.text[:500],
                    "link": f"https://t.me/{channel_name}/{msg.id}"
                })
        except Exception as e:
            print(f"  Ошибка {channel_name}: {e}")

    await client.disconnect()

    print(f"\n  Пропущено (уже видели): {skipped_seen}")
    print(f"  Пропущено (pre-filter): {skipped_filter}")
    print(f"  Передаю в Claude: {len(posts)} постов")

    if not posts:
        print("  Новых релевантных постов нет")
        save_seen(seen)
        return

    # Анализ через Claude
    client_ai = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    all_good = []

    for i in range(0, len(posts), 10):
        batch = posts[i:i+10]
        try:
            message = client_ai.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1000,
                messages=[{"role": "user", "content": f"""Проанализируй посты из Telegram.

КРИТЕРИИ:
{SEARCH_CRITERIA}

ПОСТЫ:
{json.dumps(batch, ensure_ascii=False, indent=2)}

Верни JSON ПОДХОДЯЩИХ:
[{{"title":"...","company":"...","channel":"...","link":"...","reason":"..."}}]

Если нет — верни []. Только JSON."""}]
            )
            result = message.content[0].text.strip().replace("```json", "").replace("```", "").strip()
            start = result.find("[")
            end = result.rfind("]") + 1
            if start != -1 and end > 0:
                parsed = json.loads(result[start:end])
                all_good.extend(parsed)
                print(f"  Батч {i//10+1}: найдено {len(parsed)}")
        except Exception as e:
            print(f"  Батч {i//10+1} ошибка: {e}")

    for post in posts:
        seen.add(post["id"])
    save_seen(seen)

    print(f"\n  Итого найдено вакансий: {len(all_good)}")
    print(f"  Известных постов после скана: {len(seen)}")

    # Сохраняем результаты для аналитика
    with open("C:\\jobagent\\fullscan_results.json", "w", encoding="utf-8") as f:
        json.dump(all_good, f, ensure_ascii=False, indent=2)
    print("  Результаты сохранены в fullscan_results.json")
    print("  Запусти аналитик: python analyzer_agent.py")

asyncio.run(fullscan())