# 🌙 Mymoon Agent — Автоматический поиск работы

Персональный AI-агент для автоматического поиска вакансий Senior Project Manager и Program Manager с оценкой вакансий, генерацией cover letter и управлением через Telegram.

---

## Архитектура

```
┌─────────────────────────────────────────────────────┐
│                    run_all.py                        │
│              (Пн–Пт, 09:00 и 15:00)                 │
└──────────┬──────────┬──────────┬────────────────────┘
           │          │          │           │
     agent.py  linkedin_  telegram_  careers_
     (hh.ru/  jsearch.py  agent.py   agent.py
      hh.uz)  (JSearch    (Telethon) (прямые
              API)                   сайты)
           │          │          │           │
           └──────────┴──────────┴───────────┘
                              │
                    analyzer_agent.py
                  (оценка по профилю + AI)
                              │
                    ┌─────────┴──────────┐
                    │    bot_server.py    │
                    │  Telegram бот с    │
                    │ кнопками ✅/❌     │
                    │ + cover letter AI  │
                    └─────────┬──────────┘
                              │
               ┌──────────────┴───────────────┐
               │                              │
       sheets_helper.py               weekly_stats.py
       (Google Sheets лог)          (еженедельная сводка)
```

---

## Статусы вакансий

```
Новая → Viewed → Approval → Sent / Rejected
```

| Статус    | Описание                                      |
|-----------|-----------------------------------------------|
| Новая     | Найдена агентом, ещё не просмотрена           |
| Viewed    | Открыта в боте, ожидает решения               |
| Approval  | Одобрена (✅), ожидает отправки cover letter  |
| Sent      | Cover letter отправлен                         |
| Rejected  | Отклонена (❌)                                |

---

## Файлы проекта

| Файл                  | Назначение                                         |
|-----------------------|----------------------------------------------------|
| `agent.py`            | Парсер hh.ru и hh.uz                              |
| `linkedin_jsearch.py` | Поиск через JSearch API (LinkedIn, Indeed и др.)  |
| `telegram_agent.py`   | Парсер Telegram каналов (Telethon)                |
| `careers_agent.py`    | Прямой парсинг карьерных сайтов компаний          |
| `run_all.py`          | Запуск всех агентов по расписанию                 |
| `analyzer_agent.py`   | AI-оценка вакансий по профилю (резюме в `profile/`)|
| `bot_server.py`       | Telegram бот: кнопки, cover letter, команды       |
| `weekly_stats.py`     | Еженедельная статистика в Telegram                |
| `watchdog.py`         | Ping healthchecks.io каждые 5 минут               |
| `sheets_helper.py`    | Логирование в Google Sheets                        |
| `helpers.py`          | Отправка вакансий с inline-кнопками в TG          |
| `config.py`           | Загрузка конфигурации из `.env`                   |

---

## Дедупликация

Просмотренные вакансии хранятся в JSON-файлах (не в репозитории):

- `seen_hh.json` — hh.ru / hh.uz
- `seen_telegram.json` — Telegram каналы  
- `seen_international.json` — JSearch API
- `seen_careers.json` — карьерные сайты

---

## Установка

### 1. Клонировать репозиторий

```bash
git clone https://github.com/YOUR_USERNAME/mymoon-agent.git
cd mymoon-agent
```

### 2. Создать виртуальное окружение

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Настроить конфигурацию

```bash
cp .env.example .env
# Заполнить .env своими ключами
```

### 5. Добавить резюме в папку profile/

```
profile/
  resume_ru.pdf      # Резюме на русском
  resume_en.pdf      # Резюме на английском
  profile.md         # Краткий профиль для AI-оценки
```

### 6. Запустить бота

```bash
# Только Telegram бот (приём ответов)
python bot_server.py

# Все агенты по расписанию + бот
python run_all.py
```

---

## Настройка расписания (Windows Task Scheduler)

Альтернатива встроенному scheduler в `run_all.py`:

```
Задание 1: python C:\jobagent\run_all.py
Триггер: Пн–Пт 09:00 и 15:00
```

---

## Мониторинг

- **healthchecks.io** — watchdog пингует каждые 5 минут
- **Watchdog бот** — отдельный Telegram бот с алертами при падении

---

## Требования

- Python 3.11+
- Telegram Bot Token ([@BotFather](https://t.me/BotFather))
- RapidAPI ключ для [JSearch](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)
- Anthropic API ключ (для генерации cover letter)
- Google Service Account (для Sheets интеграции)
- Telethon API credentials (для TG каналов)

---

## Лицензия

Personal use only. Not for redistribution.
