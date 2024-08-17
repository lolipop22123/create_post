import random

from config import bot, dp, admins

from aiogram.dispatcher import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from app.keyboards import start_kb
from app.state import createPost


@dp.callback_query_handler(text = 'settingspost')
async def settingspost(call:CallbackQuery):
    user_id = call.from_user.id
    
    if user_id in admins:
        mkp = InlineKeyboardMarkup()
        btn1 = InlineKeyboardButton(f'Создать пост', callback_data=f'createpost')
        btn2 = InlineKeyboardButton(f'Удалить пост', callback_data=f'delatepost')
        btn3 = InlineKeyboardButton(f'Назад', callback_data=f'backmenu')
        mkp.add(btn1).add(btn2).add(btn3)
        
        await call.message.answer(
            f'<b>Выберите действие:</b>',
            reply_markup=mkp
        )
    else:
        await call.message.answer(
            f'У вас нет доступа в бота!'
        )


#Созать пост 
@dp.callback_query_handler(text = 'createpost')
async def createpost(call:CallbackQuery):
    user_id = call.from_user.id
    
    if user_id in admins:
        mkp = InlineKeyboardMarkup()
        mkp.add(InlineKeyboardButton(f'Отмена', callback_data=f'cancel_create'))
        await call.message.answer(
            f'Введите текст поста:'
        )

        await createPost.text.set()


@dp.message_handler(state = createPost.text)
async def newTextPost(m:Message, state:FSMContext):
    text_post = m.text
    
    
# Удалить пост
  
# Меню
@dp.callback_query_handler(text = 'backmenu')
async def backmenu(call:CallbackQuery, state:FSMContext):
    user_id = call.from_user.id
    
    await call.message.delete()
    
    if user_id in admins:
        await call.message.answer(
            f'Добро пожаловать в бота!',
            reply_markup=start_kb()
        )
    
    await state.finish()


# Отмена создания поста
@dp.callback_query_handler(text = 'cancel_create', state = createPost.text)
async def cancel_create_post(call:CallbackQuery, state:FSMContext):
    await call.message.delete()
    
    user_id = call.from_user.id
    
    if user_id in admins:
        mkp = InlineKeyboardMarkup()
        btn1 = InlineKeyboardButton(f'Создать пост', callback_data=f'createpost')
        btn2 = InlineKeyboardButton(f'Удалить пост', callback_data=f'delatepost')
        btn3 = InlineKeyboardButton(f'Назад', callback_data=f'backmenu')
        mkp.add(btn1).add(btn2).add(btn3)
        
        await call.message.answer(
            f'<b>Выберите действие:</b>',
            reply_markup=mkp
        )
    else:
        await call.message.answer(
            f'У вас нет доступа в бота!'
        )
    
    await state.finish()