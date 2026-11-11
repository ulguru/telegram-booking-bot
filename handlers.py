from datetime import date, timedelta

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

import db
import keyboards as kb
from config import ADMIN_ID, CONTACTS, SERVICES

router = Router()


class Booking(StatesGroup):
    service = State()
    date = State()
    time = State()
    name = State()
    phone = State()
    confirm = State()


# ---------- Главное меню ----------

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Я помогу записаться в студию маникюра.\nВыберите действие в меню ниже.",
        reply_markup=kb.main_menu,
    )


@router.message(F.text == kb.BTN_PRICES)
async def prices(message: Message):
    lines = [f"• {title} — {price} ₽ ({minutes} мин)" for title, price, minutes in SERVICES.values()]
    await message.answer("💅 <b>Услуги и цены</b>\n\n" + "\n".join(lines))


@router.message(F.text == kb.BTN_CONTACTS)
async def contacts(message: Message):
    await message.answer(CONTACTS)


# ---------- Запись ----------

@router.message(F.text == kb.BTN_BOOK)
async def book_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Booking.service)
    await message.answer("Выберите услугу:", reply_markup=kb.services_kb())


@router.callback_query(F.data == "cancel")
async def cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("Запись отменена.")
    await call.answer()


@router.callback_query(Booking.service, F.data.startswith("service:"))
async def choose_service(call: CallbackQuery, state: FSMContext):
    code = call.data.split(":")[1]
    await state.update_data(service=code)
    await state.set_state(Booking.date)
    await call.message.edit_text(
        f"Услуга: <b>{SERVICES[code][0]}</b>\n\nВыберите дату:", reply_markup=kb.dates_kb()
    )
    await call.answer()


@router.callback_query(F.data == "back:service")
async def back_to_service(call: CallbackQuery, state: FSMContext):
    await state.set_state(Booking.service)
    await call.message.edit_text("Выберите услугу:", reply_markup=kb.services_kb())
    await call.answer()


async def show_times(call: CallbackQuery, state: FSMContext, day: str):
    markup = kb.times_kb(day, await db.get_busy_times(day))
    if markup is None:
        await call.answer("На этот день свободного времени нет 😔", show_alert=True)
        return
    await state.update_data(date=day)
    await state.set_state(Booking.time)
    await call.message.edit_text(f"Дата: <b>{kb.format_date(day)}</b>\n\nВыберите время:", reply_markup=markup)
    await call.answer()


@router.callback_query(Booking.date, F.data.startswith("date:"))
async def choose_date(call: CallbackQuery, state: FSMContext):
    await show_times(call, state, call.data.split(":", 1)[1])


@router.callback_query(F.data == "back:date")
async def back_to_date(call: CallbackQuery, state: FSMContext):
    await state.set_state(Booking.date)
    await call.message.edit_text("Выберите дату:", reply_markup=kb.dates_kb())
    await call.answer()


@router.callback_query(Booking.time, F.data.startswith("time:"))
async def choose_time(call: CallbackQuery, state: FSMContext):
    await state.update_data(time=call.data.split(":", 1)[1])
    await state.set_state(Booking.name)
    await call.message.edit_text("Как вас зовут?")
    await call.answer()


@router.message(Booking.name, F.text)
async def enter_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip()[:50])
    await state.set_state(Booking.phone)
    await message.answer(
        "Отправьте номер телефона кнопкой ниже или напишите его сообщением:",
        reply_markup=kb.phone_keyboard,
    )


@router.message(Booking.phone, F.contact | F.text)
async def enter_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text.strip()
    digits = "".join(ch for ch in phone if ch.isdigit())
    if not 10 <= len(digits) <= 15:
        await message.answer("Похоже, номер неверный. Попробуйте ещё раз, например: +79001234567")
        return
    await state.update_data(phone=phone)
    await state.set_state(Booking.confirm)
    data = await state.get_data()
    title, price, _ = SERVICES[data["service"]]
    await message.answer("Почти готово!", reply_markup=kb.main_menu)
    await message.answer(
        "Проверьте данные:\n\n"
        f"💅 {title} — {price} ₽\n"
        f"📅 {kb.format_date(data['date'])}, {data['time']}\n"
        f"👤 {data['name']}\n"
        f"📞 {phone}",
        reply_markup=kb.confirm_kb(),
    )


@router.callback_query(Booking.confirm, F.data == "confirm")
async def confirm(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    booking_id = await db.add_booking(
        call.from_user.id, data["name"], data["phone"], data["service"], data["date"], data["time"]
    )
    if booking_id is None:
        # кто-то успел занять это время, пока человек вводил данные
        await state.set_state(Booking.date)
        await call.message.edit_text(
            "Ой, это время только что заняли 😔 Выберите другую дату:", reply_markup=kb.dates_kb()
        )
        await call.answer()
        return

    await state.clear()
    when = f"{kb.format_date(data['date'])}, {data['time']}"
    title = SERVICES[data["service"]][0]
    await call.message.edit_text(f"✅ Вы записаны!\n\n💅 {title}\n📅 {when}\n\nЖдём вас!")
    await call.answer()

    if ADMIN_ID:
        await bot.send_message(
            ADMIN_ID,
            f"🆕 <b>Новая запись #{booking_id}</b>\n\n"
            f"💅 {title}\n📅 {when}\n👤 {data['name']}\n📞 {data['phone']}",
        )


# ---------- Мои записи ----------

@router.message(F.text == kb.BTN_MY)
async def my_bookings(message: Message):
    bookings = await db.get_user_bookings(message.from_user.id, date.today().isoformat())
    if not bookings:
        await message.answer("У вас пока нет записей.")
        return
    lines = [f"• {SERVICES[s][0]} — {kb.format_date(d)}, {t}" for _, s, d, t in bookings]
    await message.answer("📋 <b>Ваши записи:</b>\n\n" + "\n".join(lines), reply_markup=kb.my_bookings_kb(bookings))


@router.callback_query(F.data.startswith("del:"))
async def delete_booking(call: CallbackQuery, bot: Bot):
    row = await db.delete_booking(int(call.data.split(":")[1]), call.from_user.id)
    if row is None:
        await call.answer("Запись не найдена", show_alert=True)
        return
    service, day, t = row
    await call.message.edit_text(f"Запись на {kb.format_date(day)}, {t} отменена.")
    await call.answer()
    if ADMIN_ID:
        await bot.send_message(
            ADMIN_ID, f"❌ Клиент отменил запись: {SERVICES[service][0]}, {kb.format_date(day)}, {t}"
        )


# ---------- Для мастера ----------

@router.message(Command("today", "tomorrow"), F.from_user.id == ADMIN_ID)
async def admin_schedule(message: Message):
    offset = 1 if message.text.startswith("/tomorrow") else 0
    day = (date.today() + timedelta(days=offset)).isoformat()
    bookings = await db.get_bookings_by_date(day)
    if not bookings:
        await message.answer(f"На {kb.format_date(day)} записей нет.")
        return
    lines = [f"<b>{t}</b> — {SERVICES[s][0]}, {name}, {phone}" for t, name, phone, s in bookings]
    await message.answer(f"📅 <b>{kb.format_date(day)}</b>\n\n" + "\n".join(lines))
