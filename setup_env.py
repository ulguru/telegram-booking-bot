"""Записывает BOT_TOKEN и ADMIN_ID в файл .env (токен при вводе не отображается)."""
from getpass import getpass

token = getpass("Вставьте токен от @BotFather (символы не будут видны) и нажмите Enter: ").strip()
admin_id = input("Ваш Telegram ID от @userinfobot: ").strip()

if ":" not in token:
    raise SystemExit("Похоже, это не токен — он выглядит как 1234567890:AAH... Запустите скрипт ещё раз.")
if not admin_id.isdigit():
    raise SystemExit("ID должен состоять только из цифр. Запустите скрипт ещё раз.")

with open(".env", "w") as f:
    f.write(f"BOT_TOKEN={token}\nADMIN_ID={admin_id}\n")

print("✅ Готово! Теперь запустите бота: .venv/bin/python bot.py")
