import gspread
import time
from google.oauth2.service_account import Credentials
from datetime import datetime
from config import GOOGLE_SHEET_ID, GOOGLE_KEY_FILE

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

SCORE_COLORS = {
    1:  {"red": 0.95, "green": 0.26, "blue": 0.21},
    2:  {"red": 0.96, "green": 0.42, "blue": 0.37},
    3:  {"red": 0.97, "green": 0.60, "blue": 0.55},
    4:  {"red": 0.99, "green": 0.80, "blue": 0.78},
    5:  {"red": 1.00, "green": 0.93, "blue": 0.40},
    6:  {"red": 0.85, "green": 0.96, "blue": 0.82},
    7:  {"red": 0.71, "green": 0.91, "blue": 0.66},
    8:  {"red": 0.49, "green": 0.83, "blue": 0.47},
    9:  {"red": 0.34, "green": 0.72, "blue": 0.31},
    10: {"red": 0.20, "green": 0.63, "blue": 0.17},
}

_sheet_cache = None
_existing_links = set()
_row_count = 0

def get_sheet():
    creds = Credentials.from_service_account_file(GOOGLE_KEY_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(GOOGLE_SHEET_ID).sheet1

def init_sheet():
    global _sheet_cache, _existing_links, _row_count
    if _sheet_cache is not None:
        return _sheet_cache
    ws = get_sheet()
    headers = ws.row_values(1)
    if not headers:
        ws.update(
            values=[["#", "Дата", "Должность", "Компания", "Источник",
                     "Ссылка", "Оценка", "Комментарий", "Статус", "CV", "Дата отправки"]],
            range_name="A1"
        )
    all_rows = ws.get_all_values()
    _existing_links = {row[5] for row in all_rows[1:] if len(row) > 5 and row[5]}
    _row_count = len(all_rows)
    _sheet_cache = ws
    return _sheet_cache

def add_vacancy(job: dict) -> int:
    global _existing_links, _row_count
    ws = init_sheet()
    job_link = job.get("link", "")
    if job_link and job_link in _existing_links:
        return -1
    _row_count += 1
    row_num = _row_count
    num = row_num - 1
    ws.update(
        values=[[num, datetime.now().strftime("%d.%m.%Y"),
                job.get("title", ""), job.get("company", ""),
                job.get("source", ""), job_link,
                "", "", "Новая", "", ""]],
        range_name=f"A{row_num}"
    )
    if job_link:
        _existing_links.add(job_link)
    time.sleep(1)
    return num

def color_row(row_num: int, score: int):
    ws = get_sheet()
    color = SCORE_COLORS.get(score, {"red": 1, "green": 1, "blue": 1})
    actual_row = row_num + 1
    ws.format(f"A{actual_row}:K{actual_row}", {
        "backgroundColor": color
    })
    time.sleep(0.5)

def update_score(row_num: int, score: int, comment: str):
    ws = get_sheet()
    actual_row = row_num + 1
    ws.update(values=[[score, comment]], range_name=f"G{actual_row}")
    time.sleep(0.5)
    color_row(row_num, score)

def update_status(row_num: int, status: str, cv_name: str = ""):
    ws = get_sheet()
    actual_row = row_num + 1
    ws.update(
        values=[[status, cv_name, datetime.now().strftime("%d.%m.%Y %H:%M")]],
        range_name=f"I{actual_row}"
    )
    time.sleep(0.5)

def get_new_vacancies() -> list:
    ws = get_sheet()
    rows = ws.get_all_values()
    result = []
    for i, row in enumerate(rows[1:], 2):
        if len(row) >= 9 and row[8] == "Новая":
            result.append({
                "row": i - 1,
                "num": row[0],
                "title": row[2],
                "company": row[3],
                "source": row[4],
                "link": row[5],
            })
    return result

def get_stats() -> dict:
    ws = get_sheet()
    rows = ws.get_all_values()[1:]
    total = len(rows)
    sent = sum(1 for r in rows if len(r) > 8 and r[8] == "CV отправлен")
    rejected = sum(1 for r in rows if len(r) > 8 and r[8] == "Отклонено")
    no_answer = sum(1 for r in rows if len(r) > 8 and r[8] == "Нет ответа")
    return {"total": total, "sent": sent, "rejected": rejected, "no_answer": no_answer}

def get_unanswered_vacancies() -> list:
    ws = get_sheet()
    rows = ws.get_all_values()
    result = []
    for i, row in enumerate(rows[1:], 2):
        if len(row) >= 9 and row[8] == "Отправлено":
            result.append({
                "row": i - 1,
                "num": row[0],
                "title": row[2],
                "company": row[3],
                "source": row[4],
                "link": row[5],
                "score": row[6],
            })
    return result

def get_pending_vacancies() -> list:
    ws = get_sheet()
    rows = ws.get_all_values()
    result = []
    PENDING_STATUSES = ("Viewed", "Approval", "Оценена", "Отправлено", "На рассмотрении")
    for i, row in enumerate(rows[1:], 2):
        if len(row) >= 9 and row[8] in PENDING_STATUSES:
            result.append({
                "row": i - 1,
                "num": row[0],
                "title": row[2],
                "company": row[3],
                "source": row[4],
                "link": row[5],
                "score": row[6],
            })
    return result

def get_all_vacancies() -> list:
    """
    Возвращает все вакансии из Google Sheets в виде list[dict].
    Ключи = названия колонок из строки 1.
    """
    try:
        ws = get_sheet()
        rows = ws.get_all_values()
        if not rows:
            return []
        headers = rows[0]
        result = []
        for row in rows[1:]:
            padded = row + [""] * (len(headers) - len(row))
            result.append(dict(zip(headers, padded)))
        return result
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("get_all_vacancies ошибка: %s", e)
        return []