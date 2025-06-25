import aiosqlite


async def initialize_database():
    # Подключаемся к базе данных (если база данных не существует, она будет создана)
    async with aiosqlite.connect("bot.db") as db:
        # Создаем таблицу users, если она не существует
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                phone_number TEXT,
                time TEXT
            )
        """)
        # Сохраняем изменения
        await db.commit()


async def add_user(telegram_id: int, username: str, phone_number: str, time: str):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("""
            INSERT INTO users (telegram_id, username, first_name)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO NOTHING
        """, (telegram_id, username, phone_number, time))
        await db.commit()


async def get_user_by_id(telegram_id: int):
    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        row = await cursor.fetchone()

        if row is None:
            return None

        # Преобразуем результат в словарь
        user = {
            "telegram_id": row[0],
            "username": row[1],
            "phone_number": row[2],
            "time": (row[3])
        }
        return user