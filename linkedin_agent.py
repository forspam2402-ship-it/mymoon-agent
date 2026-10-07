import requests
import json
import asyncio
import anthropic
from datetime import datetime
from config import *

SEEN_FILE = "C:\\jobagent\\seen_international.json"

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

def passes_prefilter(title: str) -> bool:
    return any(kw in title.lower() for kw in KEYWORDS)

def fetch_remotive(seen: set) -> list:
    jobs = []
    categories = ["management", "finance"]
    for cat in categories:
        try:
            r = requests.get(
                f"https://remotive.com/api/remote-jobs?category={cat}&limit=50",
                timeout=15
            )
            data = r.json()
            for job in data.get("jobs", []):
                job_id = str(job.get("id", ""))
                if job_id in seen:
                    continue
                title = job.get("title", "")
                if not passes_prefilter(title):
                    seen.add(job_id)
                    continue
                jobs.append({
                    "id": job_id,
                    "title": title,
                    "company": job.get("company_name", ""),
                    "location": job.get("candidate_required_location", "Remote"),
                    "link": job.get("url", ""),
                    "source": "Remotive"
                })
        except Exception as e:
            print(f"  Remotive ошибка: {e}")
    return jobs

def fetch_jobicy(seen: set) -> list:
    jobs = []
    try:
        r = requests.get(
            "https://jobicy.com/api/v2/remote-jobs?count=50&tag=management",
            timeout=15
        )
        data = r.json()
        for job in data.get("jobs", []):
            job_id = str(job.get("id", ""))
            if job_id in seen:
                continue
            title = job.get("jobTitle", "")
            if not passes_prefilter(title):
                seen.add(job_id)
                continue
            jobs.append({
                "id": job_id,
                "title": title,
                "company": job.get("companyName", ""),
                "location": job.get("jobGeo", "Remote"),
                "link": job.get("url", ""),
                "source": "Jobicy"
            })
    except Exception as e:
        print(f"  Jobicy ошибка: {e}")
    return jobs

def analyze_jobs(jobs: list) -> list:
    if not jobs:
        return []
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    all_good = []
    for i in range(0, len(jobs), 15):
        batch = jobs[i:i+15]
        try:
            msg = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1000,
                messages=[{"role": "user", "content": f"""Проанализируй вакансии.

КРИТЕРИИ:
{SEARCH_CRITERIA}

ВАКАНСИИ:
{json.dumps(batch, ensure_ascii=False, indent=2)}

Верни JSON ПОДХОДЯЩИХ:
[{{"title":"...","company":"...","location":"...","link":"...","source":"...","reason":"..."}}]

Если нет — верни []. Только JSON."""}]
            )
            result = msg.content[0].text.strip().replace("```json", "").replace("```", "").strip()
            start = result.find("[")
            end = result.rfind("]") + 1
            if start == -1 or end == 0:
                continue
            all_good.extend(json.loads(result[start:end]))
            print(f"  Батч {i//15+1}: найдено {len(all_good)}")
        except Exception as e:
            print(f"  Батч ошибка: {e}")
    return all_good

async def run_agent():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] International агент запущен")

    seen = load_seen()
    print(f"  Известных вакансий: {len(seen)}")

    all_jobs = []

    print("  Загружаю Remotive...")
    jobs = fetch_remotive(seen)
    all_jobs.extend(jobs)
    print(f"  После фильтра: {len(jobs)}")

    print("  Загружаю Jobicy...")
    jobs = fetch_jobicy(seen)
    all_jobs.extend(jobs)
    print(f"  После фильтра: {len(jobs)}")

    if not all_jobs:
        print("  Новых релевантных вакансий нет")
        save_seen(seen)
        return []

    print(f"  Передаю в Claude: {len(all_jobs)} вакансий...")
    good = analyze_jobs(all_jobs)
    print(f"  Подходящих: {len(good)}")

    for j in all_jobs:
        seen.add(j["id"])
    save_seen(seen)

    return good

def job():
    return asyncio.run(run_agent())

if __name__ == "__main__":
    asyncio.run(run_agent())