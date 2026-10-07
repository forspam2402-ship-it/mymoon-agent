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
Я ищу работу на позициях Senior Project Manager и Program Manager.

ПОДХОДИТ, если название должности соответствует одной из этих ролей или её
прямому эквиваленту: Senior Project Manager, Project Manager, Lead Project
Manager, Program Manager, Programme Manager, Senior Program Manager,
Senior Programme Manager, Project Director, Program Director, Programme
Director, руководитель проектов, старший/ведущий менеджер проектов,
менеджер проектов, руководитель программы/программ, менеджер программы/
программ, директор проектов/программы/программ.

НЕ ПОДХОДИТ: IT-директор, CTO/CIO, руководитель разработки/инженерии,
Product Manager, координатор проектов, ассистент, стажёр и junior-позиции.

Оценивай соответствие по названию должности; если в объявлении есть описание,
учитывай обязанности и требуемый уровень опыта. Сфера компании не важна.

ГЕОГРАФИЯ: Узбекистан, Армения, Россия, ОАЭ, Европа, Казахстан, удалённо (remote).
США, Канада, Австралия — НЕ ПОДХОДИТ если не указан remote.
"""

JOB_SITES = [
    "https://hh.ru/search/vacancy?text=Senior+Project+Manager",
    "https://hh.ru/search/vacancy?text=Project+Manager",
    "https://hh.ru/search/vacancy?text=Program+Manager",
    "https://hh.ru/search/vacancy?text=Programme+Manager",
    "https://hh.ru/search/vacancy?text=%D1%80%D1%83%D0%BA%D0%BE%D0%B2%D0%BE%D0%B4%D0%B8%D1%82%D0%B5%D0%BB%D1%8C+%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%BE%D0%B2",
    "https://hh.ru/search/vacancy?text=%D1%80%D1%83%D0%BA%D0%BE%D0%B2%D0%BE%D0%B4%D0%B8%D1%82%D0%B5%D0%BB%D1%8C+%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D1%8B",
    "https://hh.uz/search/vacancy?text=Senior+Project+Manager",
    "https://hh.uz/search/vacancy?text=Program+Manager",
    "https://hh.uz/search/vacancy?text=%D1%80%D1%83%D0%BA%D0%BE%D0%B2%D0%BE%D0%B4%D0%B8%D1%82%D0%B5%D0%BB%D1%8C+%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%BE%D0%B2",
    "https://hh.uz/search/vacancy?text=%D1%80%D1%83%D0%BA%D0%BE%D0%B2%D0%BE%D0%B4%D0%B8%D1%82%D0%B5%D0%BB%D1%8C+%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D1%8B",
]