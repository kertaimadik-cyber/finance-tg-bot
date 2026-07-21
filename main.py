import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
import database
from handlers import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main() -> None:
    # Создаём таблицы в БД, если их ещё нет (transactions, goals)
    await database.init_db()
    logger.info("База данных инициализирована")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Подключаем весь роутер с хендлерами из handlers.py
    dp.include_router(router)

    # На всякий случай сбрасываем старые апдейты, накопившиеся,
    # пока бот не работал (актуально при перезапусках)
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Бот MoneyMind запущен, начинаю polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен вручную")