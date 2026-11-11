import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import db
from config import BOT_TOKEN
from handlers import router


async def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit("Не найден BOT_TOKEN. Создайте файл .env по примеру .env.example")

    logging.basicConfig(level=logging.INFO)
    await db.init_db()

    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
