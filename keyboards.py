from datetime import date, datetime, timedelta

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import DAYS_AHEAD, DAYS_OFF, SERVICES, SLOT_MINUTES, WORK_END, WORK_START

WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

BTN_BOOK = "📝 Записаться"
BTN_MY = "📋 Мои записи"
BTN_PRICES = "💅 Услуги и цены"
BTN_CONTACTS = "📍 Контакты"

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_BOOK)],
        [KeyboardButton(text=BTN_MY), KeyboardButton(text=BTN_PRICES)],
        [KeyboardButton(text=BTN_CONTACTS)],
    ],
    resize_keyboard=True,
)

phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📱 Отправить номер", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True,
)


def format_date(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{WEEKDAYS[d.weekday()]}, {d:%d.%m}"


def services_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for code, (title, price, _) in SERVICES.items():
        kb.button(text=f"{title} — {price} ₽", callback_data=f"service:{code}")
    kb.button(text="✖️ Отмена", callback_data="cancel")
    kb.adjust(1)
    return kb.as_markup()


def dates_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    today = date.today()
    for i in range(DAYS_AHEAD):
        d = today + timedelta(days=i)
        if d.weekday() in DAYS_OFF:
            continue
        kb.button(text=format_date(d.isoformat()), callback_data=f"date:{d.isoformat()}")
    kb.button(text="⬅️ Назад", callback_data="back:service")
    kb.adjust(3)
    return kb.as_markup()


def times_kb(day: str, busy: set[str]) -> InlineKeyboardMarkup | None:
    """Свободные слоты на день. None — если свободных нет."""
    kb = InlineKeyboardBuilder()
    now = datetime.now()
    slot = datetime.combine(date.fromisoformat(day), datetime.min.time()).replace(hour=WORK_START)
    end = slot.replace(hour=WORK_END)
    count = 0
    while slot < end:
        t = slot.strftime("%H:%M")
        if t not in busy and slot > now:
            kb.button(text=t, callback_data=f"time:{t}")
            count += 1
        slot += timedelta(minutes=SLOT_MINUTES)
    if count == 0:
        return None
    kb.adjust(4)
    kb.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="back:date"))
    return kb.as_markup()


def confirm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data="confirm")
    kb.button(text="✖️ Отмена", callback_data="cancel")
    return kb.as_markup()


def my_bookings_kb(bookings: list[tuple]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for booking_id, _, day, t in bookings:
        kb.button(text=f"❌ Отменить {format_date(day)} {t}", callback_data=f"del:{booking_id}")
    kb.adjust(1)
    return kb.as_markup()
