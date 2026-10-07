import requests
import json
import time
import asyncio
import anthropic
from datetime import datetime
from bs4 import BeautifulSoup
from config import *

SEEN_FILE = "C:\\jobagent\\seen_careers.json"

CAREER_SITES = [
    "https://jobs.zalando.com/en/jobs",
    "https://www.revolut.com/en-US/careers/",
    "https://careers.nebius.com/",
    "https://miro.com/careers/open-positions/",
    "https://job-boards.eu.greenhouse.io/jetbrains",
    "https://careers.indrive.com/",
    "https://picsart.com/careers/",
    "https://exness-careers.com/jobs/",
    "https://careers.epam.com/en/jobs/uzbekistan",
    "https://automattic.com/jobs/",
    "https://jobs.eu.lever.co/pnlfin",
    "https://about.gitlab.com/jobs/all-jobs/",
    "https://www.deel.com/careers/open-roles/",
    "https://jobs.ashbyhq.com/1password",
    "https://canonical.com/careers/all",
    "https://posthog.com/careers",
    "https://rubylabs.com/careers/",
    "https://mercuryo.io/career",
    "https://apply.workable.com/libertexgroup/",
    "https://careers.circle.com/us/en/search-results",
    "https://careers.airbnb.com/positions/",
    "https://www.apollo.io/careers",
    "https://careers.veeam.com/search-jobs",
    "https://careers.paychex.com/it/jobs",
]

KEYWORDS = [
    "senior project manager", "project manager", "lead project manager",
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

def make_job_key(job: dict, url: str) -> str:
    # Нормализуем: lowercase, убираем пробелы, берём домен сайта
    title = job.get("title", "").lower().strip()[:50]
    domain = url.split("/")[2].replace("www.", "").replace("careers.", "").replace("jobs.", "")
    return f"{domain}_{title}"

def passes_prefilter(text: str) -> bool:
    return any(kw in text.lower() for kw in KEYWORDS)

def scrape_careers(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 20]
        return "\n".join(lines[:150])
    except:
        return ""

def analyze_careers(url: str, text: str) -> list:
    if not text or len(text) < 100:
        return []
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            messages=[{"role": "user", "content": f"""Найди подходящие вакансии на странице.

КРИТЕРИИ:
{SEARCH_CRITERIA}

СТРАНИЦА: {url}

СОДЕРЖИМОЕ:
{text[:1500]}

Верни JSON ПОДХОДЯЩИХ:
[{{"title":"...","company":"...","link":"{url}","reason":"..."}}]

Если нет — верни []. Только JSON."""}]
        )
        result = message.content[0].text.strip().replace("```json", "").replace("```", "").strip()
        start = result.find("[")
        end = result.rfind("]") + 1
        if start == -1 or end == 0:
            return []
        return json.loads(result[start:end])
    except Exception as e:
        print(f"  Claude ошибка: {e}")
        return []

async def run_careers_agent():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Careers агент запущен")

    seen = load_seen()
    print(f"  Известных вакансий: {len(seen)}")

    all_good = []
    skipped_filter = 0

    for url in CAREER_SITES:
        domain = url.split("/")[2].replace("www.", "").replace("careers.", "").replace("jobs.", "")
        print(f"  Проверяю: {domain}...")

        text = scrape_careers(url)
        if not text:
            print(f"  Пропускаю (пустая страница)")
            continue

        if not passes_prefilter(text):
            skipped_filter += 1
            print(f"  Пропускаю (нет ключевых слов)")
            continue

        jobs = analyze_careers(url, text)

        new_jobs = []
        for job in jobs:
            job_key = make_job_key(job, url)
            if job_key not in seen:
                seen.add(job_key)
                new_jobs.append(job)
            else:
                print(f"  Дубликат: {job.get('title')}")

        if new_jobs:
            print(f"  Найдено новых: {len(new_jobs)}")
            all_good.extend(new_jobs)
        else:
            print(f"  Подходящих нет")

        time.sleep(1)

    save_seen(seen)

    print(f"\n  Пропущено (pre-filter): {skipped_filter}")
    print(f"  Итого новых подходящих: {len(all_good)}")
    return all_good

def job():
    return asyncio.run(run_careers_agent())

if __name__ == "__main__":
    asyncio.run(run_careers_agent())