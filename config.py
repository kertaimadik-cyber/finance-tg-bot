import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Токен Telegram-бота (получить у @BotFather)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# API-ключ для ИИ (Gemini или OpenAI — в зависимости от того, что будешь использовать)
AI_API_KEY = os.getenv("AI_API_KEY")

# Путь к файлу базы данных SQLite
DB_PATH = os.getenv("DB_PATH", "finance.db")

# Проверка, что критичные переменные заданы — падаем сразу с понятной ошибкой,
# а не где-то в середине работы бота
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден. Проверь файл .env")

if not AI_API_KEY:
    raise ValueError("AI_API_KEY не найден. Проверь файл .env")