from dotenv import load_dotenv
import os

load_dotenv()

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY", "")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_KEY_FILE = os.getenv("GOOGLE_KEY_FILE")
ALLOWED_USERS = [int(x) for x in os.getenv("ALLOWED_USERS", "").split(",") if x]

TG_API_ID = int(os.getenv("TG_API_ID", "0"))
TG_API_HASH = os.getenv("TG_API_HASH")

WATCHDOG_TOKEN = os.getenv("WATCHDOG_TOKEN")
HC_PING_URL = os.getenv("HC_PING_URL")

PROFILE_DIR = os.getenv("PROFILE_DIR", "C:\\jobagent\\profile\\")
CV_RU = os.getenv("CV_RU", "CV_RU.docx")
CV_EN = os.getenv("CV_EN", "CV_EN.docx")

CANDIDATE_NAME_RU = os.getenv("CANDIDATE_NAME_RU")
CANDIDATE_NAME_EN = os.getenv("CANDIDATE_NAME_EN")
CANDIDATE_EMAIL = os.getenv("CANDIDATE_EMAIL")
CANDIDATE_TELEGRAM = os.getenv("CANDIDATE_TELEGRAM")
CANDIDATE_EXPERIENCE = os.getenv("CANDIDATE_EXPERIENCE")
CANDIDATE_SKILLS = os.getenv("CANDIDATE_SKILLS")
CANDIDATE_LANGUAGES = os.getenv("CANDIDATE_LANGUAGES")

SEARCH_CRITERIA = """
Я ищу работу на позиции руководителя IT.

ПОДХОДИТ если в названии есть: CTO, технический директор, IT Director,
Head of IT, Head of Engineering, VP Engineering, Deputy CTO,
руководитель IT, директор по технологиям, Chief Technology.

НЕ ПОДХОДИТ: разработчик любого уровня, тестировщик, аналитик,
менеджер по продажам, HR, маркетинг.

Фильтруй ТОЛЬКО по названию должности. Сфера компании не важна.

ГЕОГРАФИЯ: Узбекистан, Армения, Россия, ОАЭ, Европа, Казахстан, удалённо (remote).
США, Канада, Австралия — НЕ ПОДХОДИТ если не указан remote.
"""

JOB_SITES = [
    "https://hh.ru/search/vacancy?text=CTO&industry=7",
    "https://hh.ru/search/vacancy?text=IT+Director&industry=7",
    "https://hh.ru/search/vacancy?text=директор+по+IT",
    "https://hh.ru/search/vacancy?text=руководитель+IT+департамента",
    "https://hh.ru/search/vacancy?text=Head+of+IT",
    "https://hh.uz/search/vacancy?text=IT+Director",
    "https://hh.uz/search/vacancy?text=CTO",
]