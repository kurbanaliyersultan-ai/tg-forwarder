import os
import requests
import time

# Токен читается из переменной окружения BOT_TOKEN (добавляется в Railway → Variables)
TOKEN = os.environ["BOT_TOKEN"]

# После диагностики впиши сюда реальные значения из логов:
SOURCE_CHAT_ID = -1004332624949   # ID группы-источника
SOURCE_THREAD_ID = 2             # ID вкладки в группе-источнике
TARGET_CHAT_ID = -1004374638664   # ID группы-получателя (обычная группа)

API = f"https://api.telegram.org/bot{TOKEN}"

# Режим диагностики: True — скрипт только печатает ID входящих сообщений
# в логи, ничего не пересылает. Запусти, напиши сообщения в нужную вкладку
# и в группу-получатель, забери ID из логов, впиши выше, поставь False.
DIAGNOSTIC = False


def process_message(msg):
    chat_id = msg["chat"]["id"]
    thread_id = msg.get("message_thread_id")

    if DIAGNOSTIC:
        print(f"chat_id={chat_id} | thread_id={thread_id} | "
              f"chat_title={msg['chat'].get('title')} | "
              f"text={str(msg.get('text'))[:50]}")
        return

    # Фильтр: только группа-источник и только нужная вкладка
    if chat_id != SOURCE_CHAT_ID:
        return
    if thread_id != SOURCE_THREAD_ID:
        return

    r = requests.post(f"{API}/forwardMessage", json={
        "chat_id": TARGET_CHAT_ID,
        "from_chat_id": SOURCE_CHAT_ID,
        "message_id": msg["message_id"],
    }, timeout=30)

    if not r.ok:
        print(f"Ошибка пересылки: {r.status_code} {r.text}")


def main():
    offset = None
    print("Бот запущен...")
    while True:
        try:
            resp = requests.get(f"{API}/getUpdates", params={
                "timeout": 50,
                "offset": offset,
                "allowed_updates": '["message"]',
            }, timeout=60)
            updates = resp.json().get("result", [])
            for upd in updates:
                offset = upd["update_id"] + 1
                if "message" in upd:
                    process_message(upd["message"])
        except requests.exceptions.RequestException as e:
            print(f"Сетевая ошибка: {e}, повтор через 5 сек")
            time.sleep(5)


if __name__ == "__main__":
    main()
