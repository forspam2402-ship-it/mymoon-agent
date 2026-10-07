import anthropic
import json
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import asyncio
from config import *

SEEN_FILE = "C:\\jobagent\\seen_hh.json"

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
    try:
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(list(seen), f, ensure_ascii=False)
    except Exception as e:
        print(f"  Ошибка сохранения seen: {e}")

def passes_prefilter(title: str) -> bool:
    return any(kw in title.lower() for kw in KEYWORDS)

def scrape_hh(url: str, seen: set) -> list:
    jobs = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "lxml")
        cards = soup.find_all("div", {"data-qa": "vacancy-serp__vacancy"})
        for card in cards[:20]:
            try:
                title_el = card.find("a", {"data-qa": "serp-item__title"})
                company_el = card.find("a", {"data-qa": "vacancy-serp__vacancy-employer"})
                salary_el = card.find("span", {"data-qa": "vacancy-serp__vacancy-compensation"})
                title = title_el.get_text(strip=True) if title_el else ""
                if not title:
                    continue
                company = company_el.get_text(strip=True) if company_el else "Нет компании"
                salary = salary_el.get_text(strip=True) if salary_el else "Не указана"
                link = title_el.get("href", "").split("?")[0] if title_el else ""
                job_id = link if link else title
                if job_id in seen:
                    continue
                if not passes_prefilter(title):
                    seen.add(job_id)
                    continue
                jobs.append({
                    "id": job_id,
                    "title": title,
                    "company": company,
                    "salary": salary,
                    "link": link,
                    "source": "hh.ru/hh.uz"
                })
            except:
                continue
    except Exception as e:
        print(f"  Ошибка при парсинге {url}: {e}")
    return jobs

def analyze_with_claude(jobs: list) -> list:
    if not jobs:
        return []
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    all_good = []
    for i in range(0, len(jobs), 15):
        batch = jobs[i:i+15]
        jobs_text = json.dumps(batch, ensure_ascii=False, indent=2)
        try:
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1000,
                messages=[{"role": "user", "content": f"""Проанализируй вакансии и найди подходящие.

КРИТЕРИИ:
{SEARCH_CRITERIA}

ВАКАНСИИ:
{jobs_text}

Верни JSON ПОДХОДЯЩИХ:
[{{"title":"...","company":"...","salary":"...","link":"...","reason":"..."}}]

Если нет — верни []. Только JSON."""}]
            )
            result = message.content[0].text.strip()
            result = result.replace("```json", "").replace("```", "").strip()
            start = result.find("[")
            end = result.rfind("]") + 1
            if start == -1 or end == 0:
                continue
            result = result[start:end]
            parsed = json.loads(result)
            all_good.extend(parsed)
            print(f"  Батч {i//15+1}: найдено {len(parsed)}")
        except Exception as e:
            print(f"  Батч {i//15+1} ошибка: {e}")
            continue
    return all_good

async def run_agent():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Агент запущен")

    seen = load_seen()
    print(f"  Известных вакансий: {len(seen)}")

    all_jobs = []
    for url in JOB_SITES:
        print(f"  Обхожу: {url[:60]}...")
        jobs = scrape_hh(url, seen)
        all_jobs.extend(jobs)
        print(f"  Прошло фильтр: {len(jobs)}")

    if not all_jobs:
        print("  Новых вакансий нет")
        save_seen(seen)
        return []

    print(f"  Передаю в Claude: {len(all_jobs)} вакансий...")
    good_jobs = analyze_with_claude(all_jobs)
    print(f"  Подходящих: {len(good_jobs)}")

    for job in all_jobs:
        seen.add(job['id'])
    save_seen(seen)

    return good_jobs

def job():
    return asyncio.run(run_agent())

if __name__ == "__main__":
    asyncio.run(run_agent())