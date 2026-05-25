"""
weekly_stats.py — Еженедельная статистика по вакансиям в Telegram.
Адаптирован под реальную структуру Google Sheets:
  # | Дата | Должность | Компания | Источник | Ссылка | Оценка | Комментарий | Статус | CV | Дата отправки
"""

import logging
from collections import Counter
from datetime import datetime, timedelta

import requests

from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

try:
    from sheets_helper import get_all_vacancies
    SHEETS_AVAILABLE = True
except ImportError:
    SHEETS_AVAILABLE = False

# ── Маппинг колонок Sheets → внутренние ключи ────────────────────────────────
# Ключ Sheets         → ключ в коде
COL_STATUS  = "Статус"
COL_SOURCE  = "Источник"
COL_TITLE   = "Должность"
COL_COMPANY = "Компания"
COL_SCORE   = "Оценка"
COL_DATE    = "Дата"        # дата добавления, формат dd.mm.yyyy

STATUS_EMOJI = {
    "Новая":          "🆕",
    "Viewed":         "👁",
    "Approval":       "✅",
    "Оценена":        "🔍",
    "Отправлено":     "📨",
    "CV отправлен":   "📨",
    "Нет ответа":     "🔇",
    "Отклонено":      "❌",
}

SOURCE_NAMES = {
    "hh":       "hh.ru / hh.uz",
    "jsearch":  "LinkedIn / Indeed",
    "telegram": "Telegram",
    "careers":  "Карьерные сайты",
    "remotive": "Remotive",
    "jobicy":   "Jobicy",
}


def get_weekly_data() -> list:
    """Возвращает вакансии за последние 7 дней из Sheets."""
    if not SHEETS_AVAILABLE:
        logger.warning("sheets_helper недоступен, статистика пустая")
        return []

    week_ago = datetime.now() - timedelta(days=7)
    all_rows = get_all_vacancies()
    recent = []

    for row in all_rows:
        date_str = row.get(COL_DATE, "")
        try:
            dt = datetime.strptime(date_str, "%d.%m.%Y")
            if dt >= week_ago:
                recent.append(row)
        except ValueError:
            pass

    logger.info("Из Sheets: %d строк, за неделю: %d", len(all_rows), len(recent))
    return recent


def calculate_stats(rows: list) -> dict:
    total = len(rows)
    by_status: Counter = Counter()
    by_source: Counter = Counter()
    scores = []
    top_companies: Counter = Counter()
    sent_rows = []

    for row in rows:
        status  = row.get(COL_STATUS, "Новая").strip()
        source  = row.get(COL_SOURCE, "").strip()
        score   = row.get(COL_SCORE, "")
        company = row.get(COL_COMPANY, "").strip()

        by_status[status] += 1

        # Нормализуем источник к короткому ключу для группировки
        src_key = source.lower()
        if "hh" in src_key:
            by_source["hh"] += 1
        elif "jsearch" in src_key or "linkedin" in src_key or "indeed" in src_key:
            by_source["jsearch"] += 1
        elif "telegram" in src_key:
            by_source["telegram"] += 1
        elif "remotive" in src_key:
            by_source["remotive"] += 1
        elif "jobicy" in src_key:
            by_source["jobicy"] += 1
        else:
            by_source[source or "другое"] += 1

        try:
            scores.append(float(score))
        except (TypeError, ValueError):
            pass

        if company:
            top_companies[company] += 1

        if status in ("CV отправлен", "Отправлено"):
            sent_rows.append(row)

    avg_score = sum(scores) / len(scores) if scores else None
    sent_cnt = len(sent_rows)
    conversion = round(sent_cnt / total * 100, 1) if total > 0 else 0

    return {
        "total": total,
        "by_status": dict(by_status),
        "by_source": dict(by_source),
        "avg_score": avg_score,
        "conversion_pct": conversion,
        "sent_cnt": sent_cnt,
        "top_companies": top_companies.most_common(5),
        "sent_rows": sent_rows,
    }


def format_report(stats: dict) -> str:
    week_start = (datetime.now() - timedelta(days=7)).strftime("%d.%m")
    week_end = datetime.now().strftime("%d.%m.%Y")

    lines = [
        f"📊 *Еженедельный отчёт Mymoon*",
        f"_{week_start} – {week_end}_",
        "",
        f"🔍 *Найдено за неделю:* {stats['total']}",
        "",
    ]

    if stats["by_source"]:
        lines.append("*По источникам:*")
        for src, cnt in sorted(stats["by_source"].items(), key=lambda x: -x[1]):
            name = SOURCE_NAMES.get(src, src)
            bar = "▓" * min(cnt, 10) + "░" * max(0, 10 - min(cnt, 10))
            lines.append(f"  {bar} {cnt}  _{name}_")
        lines.append("")

    if stats["by_status"]:
        lines.append("*Воронка:*")
        # Показываем в логическом порядке
        order = ["Новая", "Viewed", "Оценена", "Approval", "Отправлено", "CV отправлен", "Нет ответа", "Отклонено"]
        shown = set()
        for s in order:
            cnt = stats["by_status"].get(s, 0)
            if cnt:
                emoji = STATUS_EMOJI.get(s, "•")
                lines.append(f"  {emoji} {s}: *{cnt}*")
                shown.add(s)
        # Прочие статусы
        for s, cnt in stats["by_status"].items():
            if s not in shown and cnt:
                lines.append(f"  • {s}: *{cnt}*")
        lines.append("")

    lines.append(f"*Конверсия:* {stats['sent_cnt']} отправлено ({stats['conversion_pct']}%)")
    lines.append("")

    if stats["avg_score"] is not None:
        score_val = stats["avg_score"]
        stars = "⭐" * round(score_val / 2)  # шкала 1-10 → 1-5 звёзд
        lines.append(f"*Средний AI-скор:* {stars} {score_val:.1f}/10")
        lines.append("")

    if stats["top_companies"]:
        lines.append("*Топ компании недели:*")
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        for i, (company, cnt) in enumerate(stats["top_companies"]):
            lines.append(f"  {medals[i] if i < 5 else '•'} {company} ({cnt})")
        lines.append("")

    if stats["sent_rows"]:
        lines.append(f"*Отправлены cover letter ({stats['sent_cnt']}):*")
        for row in stats["sent_rows"][:5]:
            title = row.get(COL_TITLE, "—")
            company = row.get(COL_COMPANY, "")
            lines.append(f"  📨 {title}" + (f" @ {company}" if company else ""))
        if stats["sent_cnt"] > 5:
            lines.append(f"  _...и ещё {stats['sent_cnt'] - 5}_")
        lines.append("")

    if stats["total"] == 0:
        lines.append("⚠️ Вакансии не найдены — проверь агентов.")
    elif stats["sent_cnt"] >= 3:
        lines.append(f"💪 Отличная неделя — {stats['sent_cnt']} отклика!")
    else:
        lines.append("📈 Агент работает. Продолжаем.")

    lines.append("")
    lines.append("_Mymoon Agent_")
    return "\n".join(lines)


def send_weekly_report(text: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Отчёт отправлен")
        return True
    except requests.RequestException as e:
        logger.error("Ошибка отправки: %s", e)
        return False


def run_weekly_stats() -> None:
    logger.info("=== Weekly Stats ===")
    rows = get_weekly_data()
    stats = calculate_stats(rows)
    report = format_report(stats)
    send_weekly_report(report)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    run_weekly_stats()
