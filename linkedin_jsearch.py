"""
linkedin_jsearch.py — Поиск международных вакансий через JSearch API (RapidAPI)
Покрывает: LinkedIn, Indeed, Glassdoor, ZipRecruiter и другие платформы.

Документация API: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests

from config import (
    JSEARCH_API_KEY,        # добавить в config.py (см. ниже)
    TELEGRAM_TOKEN,         # реальное имя в config.py
    TELEGRAM_CHAT_ID,
)
from helpers import send_job_with_buttons   # реальное имя в helpers.py
from sheets_helper import add_vacancy       # реальное имя в sheets_helper.py

logger = logging.getLogger(__name__)

SEEN_FILE = Path("seen_international.json")

# ── Экономный режим для Free плана RapidAPI (200 req/мес) ────────────────────
# 3 запроса × 3 локации × 1 стр = 9 req/прогон × 2/день × 10 рабочих дней = 180 req
SEARCH_QUERIES = [
    "CTO Chief Technology Officer",
    "IT Director Head of IT",
    "VP Engineering Head of Engineering",
]

LOCATIONS = [
    "Uzbekistan",
    "UAE",
    "Remote",
]

JSEARCH_URL = "https://jsearch.p.rapidapi.com/search"
JSEARCH_HEADERS = {
    "X-RapidAPI-Key": JSEARCH_API_KEY,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
}

EXCLUDE_KEYWORDS = [
    "junior", "intern", "trainee", "student",
    "assistant", "support specialist", "helpdesk",
]

REQUIRED_KEYWORDS_ANY = [
    "cto", "chief technology", "it director", "head of it",
    "head of engineering", "vp engineering", "vp of engineering",
    "technology director", "director of it", "director of engineering",
]


# ── Дедупликация ──────────────────────────────────────────────────────────────

def load_seen() -> set:
    if SEEN_FILE.exists():
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_seen(seen: set) -> None:
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, ensure_ascii=False, indent=2)


def _job_id(job: dict) -> str:
    return job.get("job_id") or (
        f"{job.get('employer_name', '')}_{job.get('job_title', '')}_{job.get('job_city', '')}"
    )


# ── Поиск ─────────────────────────────────────────────────────────────────────

def search_jobs(query: str, location: str, num_pages: int = 1) -> list:
    results = []
    for page in range(1, num_pages + 1):
        params = {
            "query": f"{query} {location}",
            "page": str(page),
            "num_pages": "1",
            "date_posted": "week",
            "employment_types": "FULLTIME",
        }
        try:
            resp = requests.get(JSEARCH_URL, headers=JSEARCH_HEADERS, params=params, timeout=15)
            resp.raise_for_status()
            jobs = resp.json().get("data", [])
            results.extend(jobs)
            logger.info("JSearch '%s'+'%s' стр.%d → %d вакансий", query, location, page, len(jobs))
        except requests.RequestException as e:
            logger.error("JSearch ошибка (%s/%s): %s", query, location, e)
    return results


# ── Нормализация → формат helpers.py ─────────────────────────────────────────
# helpers.send_job_with_buttons ожидает ключи:
#   source, title, company, location, reason, link

def normalize_job(job: dict) -> dict:
    city = job.get("job_city") or ""
    country = job.get("job_country") or ""
    is_remote = job.get("job_is_remote", False)
    location_parts = [p for p in [city, country] if p]
    location_str = ", ".join(location_parts) if location_parts else "не указана"
    if is_remote:
        location_str = f"Remote ({location_str})" if location_parts else "Remote"

    salary_min = job.get("job_min_salary")
    salary_max = job.get("job_max_salary")
    currency = job.get("job_salary_currency", "")
    if salary_min and salary_max:
        salary_str = f"{int(salary_min):,}–{int(salary_max):,} {currency}"
    elif salary_min:
        salary_str = f"от {int(salary_min):,} {currency}"
    else:
        salary_str = "не указана"

    platform = job.get("job_publisher", "LinkedIn/Indeed")

    # reason — краткое обоснование для кнопки (показывается в Telegram)
    skills = job.get("job_required_skills") or []
    reason_parts = [platform]
    if salary_str != "не указана":
        reason_parts.append(f"💰 {salary_str}")
    if skills:
        reason_parts.append(", ".join(skills[:3]))
    reason = " · ".join(reason_parts)

    return {
        # ── ключи для helpers.send_job_with_buttons ──
        "source": f"JSearch ({platform})",
        "title": job.get("job_title", ""),
        "company": job.get("employer_name", ""),
        "location": location_str,
        "reason": reason,
        "link": job.get("job_apply_link") or job.get("job_google_link", ""),
        # ── ключи для sheets_helper.add_vacancy ──
        # add_vacancy берёт: title, company, source, link
    }


# ── Фильтрация ────────────────────────────────────────────────────────────────

def is_relevant(job: dict) -> bool:
    title_lower = job["title"].lower()
    if any(kw in title_lower for kw in EXCLUDE_KEYWORDS):
        return False
    if not any(kw in title_lower for kw in REQUIRED_KEYWORDS_ANY):
        logger.debug("Пропускаем (нерелевантный тайтл): %s", job["title"])
        return False
    return True


# ── Основная функция ──────────────────────────────────────────────────────────

def run_jsearch_agent() -> int:
    """Запускает поиск и отправляет новые вакансии в Telegram. Возвращает кол-во."""
    logger.info("=== JSearch Agent запущен ===")
    seen = load_seen()
    new_count = 0

    raw_jobs: dict = {}
    for query in SEARCH_QUERIES:
        for location in LOCATIONS:
            for j in search_jobs(query, location, num_pages=1):
                jid = _job_id(j)
                if jid not in raw_jobs:
                    raw_jobs[jid] = j

    logger.info("Уникальных от API: %d", len(raw_jobs))

    for jid, raw in raw_jobs.items():
        if jid in seen:
            continue

        job = normalize_job(raw)
        if not is_relevant(job):
            seen.add(jid)
            continue

        try:
            result = add_vacancy(job)
            if result != -1:  # -1 = дубликат
                new_count += 1
            seen.add(jid)

        except Exception as e:
            logger.error("Ошибка отправки вакансии %s: %s", jid, e)

    save_seen(seen)
    logger.info("=== JSearch Agent завершён. Новых: %d ===", new_count)
    return new_count


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    print(run_jsearch_agent())
