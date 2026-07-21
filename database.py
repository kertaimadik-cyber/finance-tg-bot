import aiosqlite
from config import DB_PATH


async def init_db() -> None:
    """
    Создаёт таблицы transactions и goals, если они ещё не существуют.
    Вызывается один раз при старте бота (в main.py).
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                user_id INTEGER PRIMARY KEY,
                goal_text TEXT NOT NULL,
                target_amount REAL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.commit()


async def add_transaction(
    user_id: int,
    amount: float,
    category: str,
    description: str
) -> None:
    """
    Добавляет одну запись о транзакции в базу данных.
    Вызывается из handlers.py после того, как ai_processor.py вернул JSON.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO transactions (user_id, amount, category, description)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, amount, category, description)
        )
        await db.commit()


async def get_monthly_summary(user_id: int) -> dict[str, float]:
    """
    Возвращает траты пользователя за текущий месяц, сгруппированные по категориям.
    Формат: {"Еда": 50000.0, "Такси": 3200.0, ...}
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT category, SUM(amount)
            FROM transactions
            WHERE user_id = ?
              AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
            GROUP BY category
            """,
            (user_id,)
        )
        rows = await cursor.fetchall()
    return {category: amount for category, amount in rows}


async def set_goal(user_id: int, goal_text: str, target_amount: float | None = None) -> None:
    """Создаёт или обновляет финансовую цель пользователя (одна активная цель на юзера)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO goals (user_id, goal_text, target_amount, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                goal_text = excluded.goal_text,
                target_amount = excluded.target_amount,
                updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, goal_text, target_amount)
        )
        await db.commit()


async def get_goal(user_id: int) -> dict | None:
    """Возвращает текущую цель пользователя или None, если цель не задана."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT goal_text, target_amount FROM goals WHERE user_id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()
    if row is None:
        return None
    return {"goal_text": row[0], "target_amount": row[1]}