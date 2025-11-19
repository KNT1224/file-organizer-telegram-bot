import os
import shutil
import time
import json
import requests

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("❌ Telegram Error:", e)

def create_folder_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def organize_files(config):
    watch_folder = config["watch_folder"]
    dest_map = config["destination_folders"]

    bot_token = config.get("telegram_bot_token")
    chat_id = config.get("telegram_chat_id")

    for filename in os.listdir(watch_folder):
        file_path = os.path.join(watch_folder, filename)

        if os.path.isdir(file_path):
            continue

        extension = filename.split(".")[-1].lower()

        moved = False
        for category, ext_list in dest_map.items():
            if extension in ext_list:
                dest_folder = os.path.join(watch_folder, category)
                create_folder_if_not_exists(dest_folder)

                new_path = os.path.join(dest_folder, filename)
                shutil.move(file_path, new_path)

                print(f"Moved: {filename} → {category}")

                if bot_token and chat_id:
                    send_telegram_message(
                        bot_token,
                        chat_id,
                        f"📁 Moved *{filename}* → `{category}`"
                    )
                moved = True
                break

        if not moved:
            other_folder = os.path.join(watch_folder, "Others")
            create_folder_if_not_exists(other_folder)

            new_path = os.path.join(other_folder, filename)
            shutil.move(file_path, new_path)

            print(f"Moved: {filename} → Others")

            if bot_token and chat_id:
                send_telegram_message(
                    bot_token,
                    chat_id,
                    f"📁 Moved *{filename}* → `Others`"
                )

def main():
    config = load_config()
    interval = config["scan_interval_seconds"]

    print("🚀 File Organizer with Telegram Started…")
    print(f"Watching: {config['watch_folder']}\n")

    while True:
        organize_files(config)
        print("✔ Scan complete. Waiting…\n")
        time.sleep(interval)

if __name__ == "__main__":
    main()
