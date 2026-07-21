import logging
import re

logger = logging.getLogger(__name__)


async def generate_advice(user_context: str = "") -> str:
    """Заглушка совета."""
    return (
        "💡 **Финансовый совет:**\n"
        "Старайся откладывать не менее 10-15% от каждого дохода сразу на накопительный счет. "
        "Это поможет создать финансовую подушку безопасности без сильного стресса для бюджета!"
    )


async def digital_twin_forecast(user_query: str, expenses_summary: str) -> str:
    """Заглушка Digital Twin."""
    return (
        "🤖 **Digital Twin Прогноз:**\n"
        f"Анализ запроса: «{user_query}»\n\n"
        "Эта покупка незначительно повлияет на твой текущий бюджет. "
        "Рекомендуем совершить её, если сумма не превышает свободный остаток за месяц."
    )


async def generate_expense_summary_text(summary: str) -> str:
    """Заглушка сводки трат."""
    return (
        "📊 **Ваша аналитика трат:**\n\n"
        f"{summary}\n\n"
        "💡 *Совет:* Держи расходы под контролем и не забудь обновить цели!"
    )


async def parse_receipt_or_expense(text: str) -> dict:
    """Простой парсер без ИИ (извлекает первое число из текста)."""
    # Ищем первое попавшееся число в сообщении (целое или с точкой/запятой)
    match = re.search(r'(\d+[\.,]?\d*)', text)
    if match:
        try:
            amount = float(match.group(1).replace(',', '.'))
            # Убираем найденное число из описания
            description = text.replace(match.group(1), '').strip()
            if not description:
                description = "Покупка"
            return {
                "amount": amount,
                "category": "Общие расходы",
                "description": description
            }
        except ValueError:
            pass

    return {"amount": 0.0, "category": "Другое", "description": text}