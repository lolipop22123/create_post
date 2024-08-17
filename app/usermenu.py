import random

from config import bot, dp, admins, db

from aiogram.dispatcher import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ContentTypes
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
    
    async with state.proxy() as data:
        data['text_post'] = text_post
        
    mkp = InlineKeyboardMarkup()
    mkp.add(InlineKeyboardButton(f'Готово', callback_data=f'readyphoto')).add(InlineKeyboardButton(f'Отмена', callback_data=f'cancelphoto'))
    
    await m.answer(
        f'Вставть фото:',
        reply_markup=mkp
    )
    
    await createPost.photo.set()

@dp.message_handler(state=createPost.photo, content_types=ContentTypes.PHOTO)
async def handle_photo(message: Message, state: FSMContext):
    # Получаем ID фото
    photo_id = message.photo[-1].file_id
    
    # Получаем текущее состояние и список ID фото
    async with state.proxy() as data:
        if 'photo_ids' not in data:
            data['photo_ids'] = []
        data['photo_ids'].append(photo_id)
        
    mkp = InlineKeyboardMarkup()
    mkp.add(InlineKeyboardButton(f'Готово', callback_data=f'readyphoto')).add(InlineKeyboardButton(f'Отмена', callback_data=f'cancelphoto'))
    
    
    # Запрашиваем следующее фото
    await message.answer('Вставьте еще фото или нажмите "Готово", если закончите.', reply_markup=mkp)


@dp.callback_query_handler(text='readyphoto', state=createPost.photo)
async def finish_photos(call: Message, state: FSMContext):
    id_post = random.randint(100000, 999999)
    
    async with state.proxy() as data:
        photo_ids = data.get('photo_ids', [])
        photo_text = data['text_post']
   
    try:
        db.create_post(id_post, photo_text, photo_ids)
        await call.message.answer(f'Фото загружены. Пост добавлен в БД!', reply_markup=start_kb())
    except Exception as e:
        print(e)
        await call.message.answer(
            f'Что то пошло не так',
            reply_markup=start_kb()
        )
    # Завершаем состояние
    await state.finish()


# Удалить пост
@dp.callback_query_handler(text = 'delatepost')
async def delatepost(call:CallbackQuery):
    


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