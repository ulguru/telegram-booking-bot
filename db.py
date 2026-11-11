import aiosqlite

from config import DB_PATH


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                service TEXT NOT NULL,
                date TEXT NOT NULL,   -- YYYY-MM-DD
                time TEXT NOT NULL,   -- HH:MM
                UNIQUE (date, time)   -- на одно время только одна запись
            )
            """
        )
        await db.commit()


async def get_busy_times(date: str) -> set[str]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT time FROM bookings WHERE date = ?", (date,))
        return {row[0] for row in await cursor.fetchall()}


async def add_booking(user_id: int, name: str, phone: str, service: str, date: str, time: str) -> int | None:
    """Возвращает id записи или None, если время уже заняли."""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            cursor = await db.execute(
                "INSERT INTO bookings (user_id, name, phone, service, date, time) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, name, phone, service, date, time),
            )
        except aiosqlite.IntegrityError:
            return None
        await db.commit()
        return cursor.lastrowid


async def get_user_bookings(user_id: int, from_date: str) -> list[tuple]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, service, date, time FROM bookings WHERE user_id = ? AND date >= ? ORDER BY date, time",
            (user_id, from_date),
        )
        return await cursor.fetchall()


async def get_bookings_by_date(date: str) -> list[tuple]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT time, name, phone, service FROM bookings WHERE date = ? ORDER BY time",
            (date,),
        )
        return await cursor.fetchall()


async def delete_booking(booking_id: int, user_id: int) -> tuple | None:
    """Удаляет запись пользователя. Возвращает (service, date, time) удалённой записи."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT service, date, time FROM bookings WHERE id = ? AND user_id = ?",
            (booking_id, user_id),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        await db.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        await db.commit()
        return row
