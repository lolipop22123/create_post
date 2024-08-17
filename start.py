from config import bot, dp, admins

from aiogram.dispatcher import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from app.keyboards import start_kb


@dp.message_handler(commands=['start'])
async def start_cmd(m:Message):
    user_id = m.from_user.id
    
    if user_id in admins:
        await m.answer(
            f'Добро пожаловать в бота!',
            reply_markup=start_kb()
        )
