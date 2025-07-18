from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
import asyncio
import sqlite3
import datetime
import logging
import os
from auto_booker import SlotBooker
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Bot token from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN', '7016462249:AAEceONPlwLRA-RiaTYeq54znDiV8yMpTCw')

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Visa categories and subcategories
VISA_CATEGORIES = {
    "C": {
        "name": "Краткосрочная (C)",
        "subcategories": {
            "C01": "Туризм",
            "C02": "Деловая",
            "C03": "Гостевая",
            "C04": "Транзит",
            "C05": "Лечение",
            "C06": "Учёба",
            "C07": "Спорт",
            "C08": "Культура",
            "C09": "Официальная",
            "C10": "Водитель",
            "C11": "Член семьи гражданина ЕС",
            "C12": "Другое"
        }
    },
    "D": {
        "name": "Долгосрочная (D)",
        "subcategories": {
            "D01": "Работа",
            "D02": "Учёба",
            "D03": "Воссоединение семьи",
            "D04": "Бизнес",
            "D05": "Другое"
        }
    }
}

CITIES = [
    ("minsk", "Минск"),
    ("brest", "Брест"),
    ("grodno", "Гродно"),
    ("vitebsk", "Витебск"),
    ("gomel", "Гомель"),
    ("mogilev", "Могилёв")
]


# States
class Registration(StatesGroup):
    waiting_for_fullname = State()
    waiting_for_gender = State()
    waiting_for_passport = State()
    waiting_for_passport_date = State()
    waiting_for_phone = State()


class SettingsFSM(StatesGroup):
    waiting_for_city = State()
    waiting_for_category = State()
    waiting_for_subcategory = State()


# Database initialization
def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                fullname TEXT,
                gender TEXT,
                passport TEXT,
                passport_date TEXT,
                email TEXT,
                phone TEXT,
                city TEXT,
                category TEXT,
                subcategory TEXT,
                is_monitoring BOOLEAN DEFAULT FALSE,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add missing columns if they don't exist
        try:
            conn.execute('ALTER TABLE users ADD COLUMN category TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            conn.execute('ALTER TABLE users ADD COLUMN subcategory TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                slots_checked INTEGER DEFAULT 0,
                active_users INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')


# Keyboards
def main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📝 Регистрация", callback_data="register"),
        InlineKeyboardButton(text="⚙ Настройки", callback_data="settings")
    )
    builder.row(
        InlineKeyboardButton(text="🎯 Начать поиск", callback_data="start_monitoring"),
        InlineKeyboardButton(text="⏹ Остановить", callback_data="stop_monitoring")
    )
    return builder.as_markup()


def back_button():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅ Назад", callback_data="back"))
    return builder.as_markup()

@dp.callback_query(F.data == "settings")
async def settings_start(callback: types.CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    for code, data in VISA_CATEGORIES.items():
        builder.row(InlineKeyboardButton(text=data["name"], callback_data=f"category_{code}"))

    await callback.message.edit_text("Выберите категорию визы:", reply_markup=builder.as_markup())
    await state.set_state(SettingsFSM.waiting_for_category)
    await callback.answer()


@dp.callback_query(F.data.startswith("category_"), SettingsFSM.waiting_for_category)
async def process_category(callback: types.CallbackQuery, state: FSMContext):
    category_code = callback.data.replace("category_", "")
    await state.update_data(category=category_code)

    subcategories = VISA_CATEGORIES[category_code]["subcategories"]
    builder = InlineKeyboardBuilder()
    for sub_code, sub_name in subcategories.items():
        builder.row(InlineKeyboardButton(text=sub_name, callback_data=f"subcategory_{sub_code}"))

    await callback.message.edit_text("Выберите подкатегорию визы:", reply_markup=builder.as_markup())
    await state.set_state(SettingsFSM.waiting_for_subcategory)
    await callback.answer()


@dp.callback_query(F.data.startswith("subcategory_"), SettingsFSM.waiting_for_subcategory)
async def process_subcategory(callback: types.CallbackQuery, state: FSMContext):
    subcategory_code = callback.data.replace("subcategory_", "")
    user_data = await state.get_data()

    save_user_data(
        user_id=callback.from_user.id,
        category=user_data.get("category"),
        subcategory=subcategory_code
    )

    await state.clear()
    await callback.message.edit_text("✅ Настройки обновлены!", reply_markup=main_menu())
    await callback.answer()


# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Database functions
def update_metrics(slots=0, users=0):
    with sqlite3.connect('database.db') as conn:
        conn.execute('''
            INSERT INTO metrics (slots_checked, active_users, last_updated)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT DO UPDATE SET
                slots_checked = slots_checked + ?,
                active_users = active_users + ?,
                last_updated = datetime('now')
        ''', (slots, users, slots, users))
        conn.commit()


def save_user_data(user_id: int, **kwargs):
    with sqlite3.connect('database.db') as conn:
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join(['?'] * len(kwargs))
        values = list(kwargs.values())

        conn.execute(
            f'''
            INSERT INTO users (user_id, {columns}, last_active)
            VALUES (?, {placeholders}, datetime('now'))
            ON CONFLICT(user_id) DO UPDATE SET
                {', '.join([f"{k} = ?" for k in kwargs.keys()])},
                last_active = datetime('now')
            ''',
            [user_id] + values + values
        )
        conn.commit()


# Handlers
@dp.message(CommandStart())
async def start(message: types.Message):
    save_user_data(
        user_id=message.from_user.id,
        username=message.from_user.username
    )
    update_metrics(users=1)
    await message.answer(
        "🤖 VFS Booking Bot - Мониторинг свободных слотов",
        reply_markup=main_menu()
    )


@dp.callback_query(F.data == "back")
async def go_back(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=main_menu()
    )
    await callback.answer()


# Registration handlers
@dp.callback_query(F.data == "register")
async def register_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите ваше имя и фамилию (как в паспорте):")
    await state.set_state(Registration.waiting_for_fullname)
    await callback.answer()

@dp.message(Registration.waiting_for_fullname)
async def process_fullname(message: types.Message, state: FSMContext):
    await state.update_data(fullname=message.text)
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Мужской", callback_data="gender_male"),
        InlineKeyboardButton(text="Женский", callback_data="gender_female")
    )
    await message.answer("Выберите пол:", reply_markup=builder.as_markup())
    await state.set_state(Registration.waiting_for_gender)


@dp.callback_query(F.data.startswith("gender_"), Registration.waiting_for_gender)
async def process_gender(callback: types.CallbackQuery, state: FSMContext):
    gender = "Мужской" if callback.data == "gender_male" else "Женский"
    await state.update_data(gender=gender)
    await callback.message.edit_text("Введите номер паспорта:")
    await state.set_state(Registration.waiting_for_passport)
    await callback.answer()

@dp.message(Registration.waiting_for_passport)
async def process_passport(message: types.Message, state: FSMContext):
    await state.update_data(passport=message.text)
    await message.answer("Введите дату выдачи паспорта (в формате ДД.ММ.ГГГГ):")
    await state.set_state(Registration.waiting_for_passport_date)


@dp.message(Registration.waiting_for_passport_date)
async def process_passport_date(message: types.Message, state: FSMContext):
    await state.update_data(passport_date=message.text)
    await message.answer("Введите номер телефона:")
    await state.set_state(Registration.waiting_for_phone)


@dp.message(Registration.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)

    # Спрашиваем город проживания
    builder = InlineKeyboardBuilder()
    for city_code, city_name in CITIES:
        builder.row(InlineKeyboardButton(text=city_name, callback_data=f"reg_city_{city_code}"))

    await message.answer("Выберите город проживания:", reply_markup=builder.as_markup())


@dp.callback_query(F.data.startswith("reg_city_"))
async def process_city(callback: types.CallbackQuery, state: FSMContext):
    city_code = callback.data.replace("reg_city_", "")
    city_name = dict(CITIES).get(city_code, "Неизвестно")
    await state.update_data(city=city_name)

    # Сохраняем все данные в БД, email берем из .env
    user_data = await state.get_data()
    save_user_data(
        user_id=callback.from_user.id,
        fullname=user_data.get("fullname"),
        gender=user_data.get("gender"),
        passport=user_data.get("passport"),
        passport_date=user_data.get("passport_date"),
        email=os.getenv('YOUR_EMAIL', ''),
        phone=user_data.get("phone"),
        city=user_data.get("city")
    )

    await state.clear()
    await callback.message.edit_text("✅ Регистрация завершена!", reply_markup=main_menu())
    await callback.answer()


# ... (other registration handlers similar to above)

# Monitoring functions
active_monitorings = {}


async def monitoring_task(user_id: int):
    try:
        while True:
            # Here would be your actual monitoring logic
            logger.info(f"Checking slots for user {user_id}")
            await asyncio.sleep(300)  # Check every 5 minutes
    except asyncio.CancelledError:
        logger.info(f"Monitoring stopped for user {user_id}")
    except Exception as e:
        logger.error(f"Monitoring error for user {user_id}: {e}")


@dp.callback_query(F.data == "start_monitoring")
async def start_monitoring(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if user_id in active_monitorings:
        await callback.answer("Мониторинг уже запущен!")
        return

    save_user_data(user_id=user_id, is_monitoring=True)
    active_monitorings[user_id] = asyncio.create_task(monitoring_task(user_id))

    await callback.message.edit_text(
        "🔍 Мониторинг запущен! Я сообщу, когда появятся свободные слоты.",
        reply_markup=main_menu()
    )
    await callback.answer()


@dp.callback_query(F.data == "stop_monitoring")
async def stop_monitoring(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if user_id not in active_monitorings:
        await callback.answer("Мониторинг не был запущен!")
        return

    active_monitorings[user_id].cancel()
    del active_monitorings[user_id]
    save_user_data(user_id=user_id, is_monitoring=False)

    await callback.message.edit_text(
        "⏹ Мониторинг остановлен.",
        reply_markup=main_menu()
    )
    await callback.answer()


# Startup
async def on_startup():
    init_db()
    logger.info("Bot started")


async def on_shutdown():
    for task in active_monitorings.values():
        task.cancel()
    logger.info("Bot stopped")


@dp.message(lambda message: message.text == "🔍 Проверить слоты")
async def check_slots_handler(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")

    try:
        page = ChromiumPage()
        booker = SlotBooker(page)

        if booker.check_and_book_slots():
            await message.answer("✅ Слот успешно забронирован!")
        else:
            await message.answer("❌ Свободных слотов не найдено")

    except Exception as e:
        logger.error(f"Ошибка при бронировании: {str(e)}")
        await message.answer("⚠ Произошла ошибка при попытке бронирования")

    finally:
        if 'page' in locals():
            page.quit()


async def main():
    await on_startup()
    await dp.start_polling(bot)
    await on_shutdown()


if __name__ == "__main__":
    asyncio.run(main())