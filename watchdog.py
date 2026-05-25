import requests
import time
from datetime import datetime
from config import WATCHDOG_TOKEN, TELEGRAM_CHAT_ID, HC_PING_URL

def send_telegram(text: str):
    try:
        requests.post(
            f"https://api.telegram.org/bot{WATCHDOG_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
            timeout=10
        )
    except Exception as e:
        print(f"Telegram ошибка: {e}")

def ping_healthchecks():
    try:
        requests.get(HC_PING_URL, timeout=10)
        print(f"  [{datetime.now().strftime('%H:%M')}] Пинг отправлен")
    except Exception as e:
        print(f"  Пинг ошибка: {e}")

send_telegram("🟢 Сервер восстановлен")
print(f"[{datetime.now().strftime('%H:%M')}] Watchdog запущен")

while True:
    ping_healthchecks()
    time.sleep(300)