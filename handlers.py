import logging

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

import database
import ai_processor

logger = logging.getLogger(__name__)
router = Router()


# ---------- Состояния ----------

class UserStates(StatesGroup):
    waiting_for_expense = State()
    waiting_for_goal = State()
    waiting_for_purchase = State()


# ---------- Клавиатуры ----------

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Меню ✅"), KeyboardButton(text="Таблица 🌐")]
    ],
    resize_keyboard=True
)

menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Узнать подробнее о боте 🧬")],
        [KeyboardButton(text="Мой траты 👀")],
        [KeyboardButton(text="Подключить банк 💳")],
        [KeyboardButton(text="Поделиться чеками 💸")],
        [KeyboardButton(text="Поделись интересным советом 📖")],
        [KeyboardButton(text="Мои цели 📊📌")],
        [KeyboardButton(text="Digital Twin 📱")],
        [KeyboardButton(text="⬅️ Назад")],
    ],
    resize_keyboard=True
)


# ---------- Вспомогательная функция: разбор траты ----------

async def process_expense_text(message: Message) -> None:
    result = await ai_processor.parse_receipt_or_expense(message.text)

    if not result or result.get("amount", 0) <= 0:
        await message.answer(
            "Не смог найти сумму траты 🤔 Попробуй написать с указанием числа, "
            "например: «Такси 1500»."
        )
        return

    await database.add_transaction(
        user_id=message.from_user.id,
        amount=result["amount"],
        category=result["category"],
        description=result["description"],
    )

    await message.answer(
        f"Записал ✅\n"
        f"Сумма: {result['amount']:.0f}\n"
        f"Категория: {result['category']}\n"
        f"Описание: {result['description']}"
    )


# ---------- /start ----------

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    name = message.from_user.first_name
    text = (
        f"Привет, {name}! Я финансовый ассистент MoneyMind! "
        f"Я помогу тебе с правильным распределением бюджета, мы вместе поставим цель 😇\n\n"
        f"Если хочешь участвовать в бета-тесте, нужно заполнить таблицу 👇"
    )
    await message.answer(text, reply_markup=main_kb)


# ---------- Навигация и Кнопки ----------

@router.message(F.text.startswith("Меню"))
async def handle_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выбери, что тебя интересует 👇", reply_markup=menu_kb)


@router.message(F.text.startswith("⬅️ Назад"))
async def handle_back(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню", reply_markup=main_kb)


@router.message(F.text.startswith("Таблица"))
async def handle_table_button(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Вот доступ к таблице для заполнения данных:\n"
        "🔗 https://forms.gle/example-placeholder\n\n"
        "(заглушка — заменим на реальную ссылку позже)"
    )


@router.message(F.text.startswith("Узнать подробнее"))
async def handle_about(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "MoneyMind — твой личный финансовый ассистент.\n\n"
        "Я анализирую траты, присланные текстом, помогаю ставить "
        "цели и подсказываю, как распоряжаться бюджетом."
    )


@router.message(F.text.startswith("Мой траты"))
async def handle_my_expenses(message: Message, state: FSMContext):
    await state.clear()
    summary = await database.get_monthly_summary(message.from_user.id)
    text = await ai_processor.generate_expense_summary_text(str(summary))
    await message.answer(text)


@router.message(F.text.startswith("Подключить банк"))
async def handle_connect_bank(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Функция автоматического получения данных банка в разработке 🛠")


@router.message(F.text.startswith("Поделиться чеками"))
async def handle_share_receipts(message: Message, state: FSMContext):
    await state.set_state(UserStates.waiting_for_expense)
    await message.answer(
        "Окей, присылай текстом свои траты (по одной или списком) — я разберу и сохраню. "
        "Когда закончишь, нажми «⬅️ Назад» или «Меню ✅»."
    )


@router.message(F.text.startswith("Поделись интересным"))
async def handle_advice(message: Message, state: FSMContext):
    await state.clear()
    summary = await database.get_monthly_summary(message.from_user.id)
    advice = await ai_processor.generate_advice(str(summary))
    await message.answer(advice)


@router.message(F.text.startswith("Мои цели"))
async def handle_goals(message: Message, state: FSMContext):
    await state.clear()
    goal = await database.get_goal(message.from_user.id)

    if goal is None:
        await message.answer(
            "У тебя пока нет активной цели. Напиши, какую цель поставить "
            "(например: «Накопить 100000 на отпуск»)."
        )
    else:
        target = f" (цель: {goal['target_amount']:.0f})" if goal.get("target_amount") else ""
        await message.answer(
            f"Твоя текущая цель: {goal['goal_text']}{target}\n\n"
            f"Хочешь изменить — просто напиши новую цель."
        )

    await state.set_state(UserStates.waiting_for_goal)


@router.message(F.text.startswith("Digital Twin"))
async def handle_digital_twin(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(UserStates.waiting_for_purchase)
    await message.answer(
        "Опиши покупку, которую планируешь (например: «Хочу купить ноутбук за 60000»), "
        "и я спрогнозирую, как это скажется на твоём бюджете."
    )


# ---------- FSM состояния ----------

@router.message(UserStates.waiting_for_expense)
async def handle_expense_state(message: Message, state: FSMContext):
    await process_expense_text(message)


@router.message(UserStates.waiting_for_goal)
async def process_goal(message: Message, state: FSMContext):
    await database.set_goal(message.from_user.id, message.text)
    await state.clear()
    await message.answer(f"Готово! Новая цель сохранена: «{message.text}» 🎯")


@router.message(UserStates.waiting_for_purchase)
async def process_digital_twin(message: Message, state: FSMContext):
    summary = await database.get_monthly_summary(message.from_user.id)
    forecast = await ai_processor.digital_twin_forecast(message.text, str(summary))
    await state.clear()
    await message.answer(forecast)


# ---------- Свободный ввод трат (ПОСЛЕДНИЙ) ----------

@router.message(F.text)
async def handle_free_text_expense(message: Message):
    await process_expense_text(message)


# =========================================================
# ВСТАВИТЬ В САМЫЙ КОНЕЦ ФАЙЛА HANDLERS.PY
# =========================================================

# Перехватывает нажатия на Inline-кнопки (гасит "часики", бот не зависает)
@router.callback_query()
async def fallback_callback(callback: CallbackQuery):
    await callback.answer("Кнопка обработана!", show_alert=False)


@router.message()
async def fallback_message(message: Message, state: FSMContext):
    current_state = await state.get_state()
    # Если пользователь просто написал сообщение (например "Обед 500") — пробуем записать как трату
    if current_state is None and message.text and not message.text.startswith("/"):
        await process_expense_text(message)
    else:
        await message.answer("Воспользуйтесь кнопками меню или введите /start", reply_markup=main_kb)
