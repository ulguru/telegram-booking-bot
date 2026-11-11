import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
# Telegram ID мастера/администратора — ему приходят уведомления о новых записях
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DB_PATH = os.getenv("DB_PATH", "bookings.db")

# Услуги: код -> (название, цена в рублях, длительность в минутах)
SERVICES = {
    "manicure": ("Маникюр", 1500, 60),
    "manicure_cover": ("Маникюр + покрытие", 2500, 90),
    "pedicure": ("Педикюр", 2000, 90),
    "design": ("Дизайн ногтей", 500, 30),
}

# Рабочие часы и шаг записи
WORK_START = 10  # с 10:00
WORK_END = 20  # до 20:00
SLOT_MINUTES = 60
DAYS_AHEAD = 7  # на сколько дней вперёд можно записаться
DAYS_OFF = {6}  # выходные: 0 = понедельник, 6 = воскресенье

CONTACTS = (
    "📍 Санкт-Петербург, Кронверкский пр., 49\n"
    "📞 +7 (900) 000-00-00\n"
    "🕙 Пн–Сб, 10:00–20:00"
)
