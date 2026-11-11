# Бот записи к мастеру

Telegram-бот для онлайн-записи клиентов в студию маникюра (легко адаптируется под барбершоп, массаж, репетитора и т.п.).

## Возможности
- Выбор услуги, даты и свободного времени через inline-кнопки
- Занятое время автоматически скрывается, двойная запись на один слот невозможна
- Отправка номера телефона одной кнопкой
- «Мои записи» — просмотр и отмена своих записей
- Уведомления мастеру о новых записях и отменах
- Команды мастера: `/today`, `/tomorrow` — расписание на день
- Услуги, цены, рабочие часы и выходные настраиваются в `config.py`

## Скриншоты

| Выбор услуги | Выбор даты | Выбор времени |
|:---:|:---:|:---:|
| <img src="screenshots/1-services.webp" width="280"> | <img src="screenshots/2-dates.webp" width="280"> | <img src="screenshots/3-time.png" width="280"> |

| Подтверждение | Запись создана + уведомление мастеру |
|:---:|:---:|
| <img src="screenshots/4-confirm.webp" width="280"> | <img src="screenshots/5-booked.png" width="200"> |

| Мои записи | Отмена записи |
|:---:|:---:|
| <img src="screenshots/6-my-bookings.webp" width="380"> | <img src="screenshots/7-cancelled.png" width="380"> |

## Стек
Python 3.11+, aiogram 3 (FSM), SQLite (aiosqlite)

## Запуск
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # вписать BOT_TOKEN и ADMIN_ID
python bot.py
```
