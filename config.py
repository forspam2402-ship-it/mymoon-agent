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
Я ищу работу на позициях Senior Project Manager и Program Manager. Профиль:
senior Program/Project Manager в технологических проектах и программах.
Подтверждённый опыт включает управление SaaS-платформой с бюджетом $2 млн,
6 кросс-функциональными командами численностью 50+ FTE, портфелем проектов,
поставкой в срок и в бюджете, стейкхолдерами, рисками, изменениями,
зависимостями, вендорами и бизнес-результатами.

ПОДХОДЯТ вакансии Senior Project Manager, Program/Programme Manager,
Senior Program/Programme Manager, Lead Project Manager, Project/Program
Director, Technical/IT Project Manager, Delivery Manager, руководитель
программ/проектов, старший/ведущий/технический менеджер проектов.
При оценке учитывай масштаб программы, несколько потоков/команд,
технологическую поставку, бюджеты, сроки, управление стейкхолдерами,
рисками, изменениями и зависимостями. Приоритетны технологические домены:
SaaS, Fintech, EdTech, Healthcare, Telecom, Automotive, AI/ML и Industry 4.0.

НЕ ПОДХОДИТ: IT-директор, CTO/CIO, руководитель разработки/инженерии,
Product Manager, Scrum Master без ответственности за delivery, координатор
проектов, ассистент, стажёр и junior-позиции.

Не отбирай вакансию только по совпадению ключевого слова: сверяй название,
обязанности и старшинство роли. Не считай кандидата IT-директором или CTO.
Не приписывай кандидату опыт, которого нет в резюме.

ГЕОГРАФИЯ: Узбекистан, Армения, Россия, ОАЭ, Европа, Казахстан, удалённо (remote).
США, Канада, Австралия — НЕ ПОДХОДИТ если не указан remote.
"""

JOB_SITES = [
    "https://hh.ru/search/vacancy?text=Senior+Project+Manager",
    "https://hh.ru/search/vacancy?text=Project+Manager",
    "https://hh.ru/search/vacancy?text=Program+Manager",
    "https://hh.ru/search/vacancy?text=Programme+Manager",
    "https://hh.ru/search/vacancy?text=Technical+Project+Manager",
    "https://hh.ru/search/vacancy?text=Delivery+Manager",
    "https://hh.ru/search/vacancy?text=%D1%80%D1%83%D0%BA%D0%BE%D0%B2%D0%BE%D0%B4%D0%B8%D1%82%D0%B5%D0%BB%D1%8C+%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%BE%D0%B2",
    "https://hh.ru/search/vacancy?text=%D1%80%D1%83%D0%BA%D0%BE%D0%B2%D0%BE%D0%B4%D0%B8%D1%82%D0%B5%D0%BB%D1%8C+%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D1%8B",
    "https://hh.uz/search/vacancy?text=Senior+Project+Manager",
    "https://hh.uz/search/vacancy?text=Program+Manager",
    "https://hh.uz/search/vacancy?text=Technical+Project+Manager",
    "https://hh.uz/search/vacancy?text=Delivery+Manager",
    "https://hh.uz/search/vacancy?text=%D1%80%D1%83%D0%BA%D0%BE%D0%B2%D0%BE%D0%B4%D0%B8%D1%82%D0%B5%D0%BB%D1%8C+%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%BE%D0%B2",
    "https://hh.uz/search/vacancy?text=%D1%80%D1%83%D0%BA%D0%BE%D0%B2%D0%BE%D0%B4%D0%B8%D1%82%D0%B5%D0%BB%D1%8C+%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D1%8B",
]