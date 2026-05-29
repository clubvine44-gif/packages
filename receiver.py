import requests
import os
import time

TOKEN = "8678852008:AAGZeO7cKJWT1vNugKy8wkuII-wotKDZe70"
SAVE_DIR = "/root/"
offset = 0

print("Приёмник запущен. Отправь файл боту в Telegram.")

while True:
    try:
        r = requests.get(
            f"https://api.telegram.org/bot{TOKEN}/getUpdates",
            params={"offset": offset, "timeout": 30},
            timeout=35
        )
        updates = r.json().get("result", [])
        for u in updates:
            offset = u["update_id"] + 1
            msg = u.get("message", {})
            doc = msg.get("document")
            if doc:
                fid = doc["file_id"]
                fn = doc["file_name"]
                fr = requests.get(
                    f"https://api.telegram.org/bot{TOKEN}/getFile",
                    params={"file_id": fid}
                )
                fp = fr.json()["result"]["file_path"]
                dl = requests.get(
                    f"https://api.telegram.org/file/bot{TOKEN}/{fp}"
                )
                with open(os.path.join(SAVE_DIR, fn), "wb") as f:
                    f.write(dl.content)
                print(f"Файл получен: {fn}")
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)
