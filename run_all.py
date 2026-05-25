"""
run_all.py — Запуск всех агентов Mymoon по расписанию.

Расписание:
  Пн–Пт  09:00 → полный прогон всех агентов
  Пн–Пт  15:00 → полный прогон всех агентов
  Пн     09:05 → еженедельная статистика

Источники:
  agent.py            → hh.ru / hh.uz
  linkedin_agent.py   → Remotive, Jobicy (международные, без ключа)
  linkedin_jsearch.py → LinkedIn, Indeed, Glassdoor (JSearch API)
  telegram_agent.py   → Telegram каналы
  careers_agent.py    → карьерные сайты компаний
"""

import logging
import time
from datetime import datetime

import schedule

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("mymoon.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def safe_run(name: str, func):
    """Запускает агент и логирует результат/ошибку."""
    logger.info("▶ Запуск: %s", name)
    try:
        result = func()
        logger.info("✓ %s завершён. Результат: %s", name, result)
    except Exception as e:
        logger.error("✗ %s упал с ошибкой: %s", name, e, exc_info=True)


def run_all_agents():
    """Запускает все агенты последовательно."""
    logger.info("=" * 60)
    logger.info("MYMOON AGENT — полный прогон %s", datetime.now().strftime("%d.%m.%Y %H:%M"))
    logger.info("=" * 60)

    # 1. hh.ru / hh.uz
    from agent import run_hh_agent
    safe_run("HH Agent (hh.ru/hh.uz)", run_hh_agent)

    # 2. Remotive, Jobicy (бесплатные API, без ключа)
    from linkedin_agent import run_linkedin_agent
    safe_run("LinkedIn Agent (Remotive/Jobicy)", run_linkedin_agent)

    # 3. LinkedIn, Indeed, Glassdoor через JSearch API (RapidAPI)
    from linkedin_jsearch import run_jsearch_agent
    safe_run("JSearch Agent (LinkedIn/Indeed)", run_jsearch_agent)

    # 4. Telegram каналы
    from telegram_agent import run_telegram_agent
    safe_run("Telegram Agent", run_telegram_agent)

    # 5. Карьерные сайты компаний
    from careers_agent import run_careers_agent
    safe_run("Careers Agent", run_careers_agent)

    logger.info("=" * 60)
    logger.info("Прогон завершён: %s", datetime.now().strftime("%d.%m.%Y %H:%M"))
    logger.info("=" * 60)


def run_weekly_stats_job():
    """Отправляет еженедельный отчёт (только по понедельникам)."""
    if datetime.now().weekday() == 0:
        from weekly_stats import run_weekly_stats
        safe_run("Weekly Stats", run_weekly_stats)


def setup_schedule():
    for day in [
        schedule.every().monday,
        schedule.every().tuesday,
        schedule.every().wednesday,
        schedule.every().thursday,
        schedule.every().friday,
    ]:
        day.at("09:00").do(run_all_agents)
        day.at("15:00").do(run_all_agents)

    schedule.every().monday.at("09:05").do(run_weekly_stats_job)

    logger.info(
        "Расписание настроено. Следующий запуск: %s",
        schedule.next_run().strftime("%d.%m.%Y %H:%M") if schedule.next_run() else "—",
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Mymoon Job Agent")
    parser.add_argument("--now", action="store_true", help="Запустить прогон немедленно")
    parser.add_argument("--stats", action="store_true", help="Отправить статистику сейчас")
    args = parser.parse_args()

    if args.now:
        run_all_agents()
    elif args.stats:
        from weekly_stats import run_weekly_stats
        run_weekly_stats()
    else:
        setup_schedule()
        logger.info("Планировщик запущен. Ctrl+C для остановки.")
        while True:
            schedule.run_pending()
            time.sleep(30)
