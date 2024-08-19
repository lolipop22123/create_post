import random

from config import bot, dp, admins, db

from aiogram.dispatcher import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ContentTypes,
    MediaGroup,
    InputMediaPhoto
)

from app.keyboards import start_kb
from app.state import createPost, addChannel, timePosting


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
    user_id = call.from_user.id
    
    if user_id in admins:
        all_post = db.get_all_posts()
        
        mkp = InlineKeyboardMarkup()
        for post in all_post:
            mkp.add(InlineKeyboardButton(f"{post['id_post']}", callback_data=f"deletepost_{post['id_post']}"))
        
        await call.message.answer(
            f'Выберит пост:', 
            reply_markup=mkp
        )


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('deletepost_'))
async def process_deletepost(call: CallbackQuery):
    user_id = call.from_user.id
    id_post = call.data.split('_')[1]

    try:
        info_post = db.get_post_by_id(int(id_post))
        photo_id = info_post['photo_ids']
        text = info_post['text']
        
        mkp = InlineKeyboardMarkup()
        btn1 = InlineKeyboardButton(f'❌Удалить', callback_data=f'deletepostyes_{id_post}')
        btn2 = InlineKeyboardButton(f'👈Назад', callback_data=f'backallpost')
        mkp.add(btn1).add(btn2)
        
        if photo_id:
            # Создаем объект MediaGroup
            media = [InputMediaPhoto(photo_id) for photo_id in photo_id]

            # Добавляем описание к последнему фото
            media[-1].caption = text
            
            await bot.send_media_group(chat_id=user_id, media=media)
            await call.message.answer(
                f'<b>Выберите действие:</b>',
                reply_markup=mkp
            )
    except Exception as e:
        print(e)
        await call.message.answer(
            f'Что то пошло не так!',
            reply_markup=start_kb()
        )


# Подтверждения удаления
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('deletepostyes_'))
async def deletepostyes(call:CallbackQuery, state:FSMContext):
    post_id = call.data.split('_')[1]
        
    try:
        db.delete_post_by_id(int(post_id))
        await call.message.answer(f'Пост успешно удален✅', reply_markup=start_kb())
    except Exception as e:
        print(e)
        mkp = InlineKeyboardMarkup()
        btn1 = InlineKeyboardButton(f'Создать пост', callback_data=f'createpost')
        btn2 = InlineKeyboardButton(f'Удалить пост', callback_data=f'delatepost')
        btn3 = InlineKeyboardButton(f'Назад', callback_data=f'backmenu')
        mkp.add(btn1).add(btn2).add(btn3)
        
        await call.message.answer(f'Что то пошло не так, попробуйте еще раз!', reply_markup=mkp)


# отмена удаления поста
@dp.callback_query_handler(text = 'backallpost')
async def backallpost(call:CallbackQuery, state:FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 2)
    
    user_id = call.from_user.id
    
    if user_id in admins:
        all_post = db.get_all_posts()
        
        mkp = InlineKeyboardMarkup()
        for post in all_post:
            mkp.add(InlineKeyboardButton(f"{post['id_post']}", callback_data=f"deletepost_{post['id_post']}"))
        mkp.add(InlineKeyboardButton(f'Назад', callback_data=f'backmenu'))
        
        await call.message.answer(
            f'Выберит пост:', 
            reply_markup=mkp
        )


# Добавление каналов
@dp.callback_query_handler(text = 'addchannel')
async def addchannel(call:CallbackQuery, state:FSMContext):
    user_id = call.from_user.id
    
    if user_id in admins:
        mkp = InlineKeyboardMarkup()
        mkp.add(InlineKeyboardButton(f'❌Отмена', callback_data=f'cancelchannel'))
        
        await call.message.answer(
            f'<b>Введите айди канала или группы:</b>',
            reply_markup=mkp
        )
        
        await addChannel.channel_id.set()
    

@dp.message_handler(state = addChannel.channel_id)
async def addChannelId(m:Message, state:FSMContext):
    channel_id = m.text
    
    async with state.proxy() as data:
        data['channel_id'] = channel_id
    
    mkp = InlineKeyboardMarkup()
    mkp.add(InlineKeyboardButton(f'❌Отмена', callback_data=f'cancelchannel'))
    
    await m.answer(
        f'<b>Придумайте имя или название канала (для информации):</b>',
        reply_markup=mkp
    )
    
    await addChannel.name.set()


@dp.message_handler(state = addChannel.name)
async def addChannelNameText(m:Message, state:FSMContext):
    name_channel = m.text
    
    async with state.proxy() as data:
        channel_id = data['channel_id']
    
    try:
        db.add_channel_posting(name_channel, channel_id)
        await m.answer(
            f'Канал успешно добавлен✅',
            reply_markup=start_kb()
        )
    except Exception as e:
        print(e)
        await m.answer(f'Что то пошло не так, попробуйте еще раз!', reply_markup=start_kb())
    
    await state.finish()


# Удаление канала
@dp.callback_query_handler(text = 'deletechanel')
async def deletechanel(call:CallbackQuery):
    user_id = call.from_user.id
    
    if user_id in admins:
        all_channel_info = db.get_all_channel_postings()
        
        mkp = InlineKeyboardMarkup()
        for id, name, channle_id in all_channel_info:
            mkp.add(InlineKeyboardButton(f'{name}', callback_data=f'delid_{channle_id}'))
        mkp.add(InlineKeyboardButton(f'❌Отмена', callback_data=f'canceldelchannelid'))
        
        await call.message.answer(
            f'<b>Выберите канала для удаления:</b>',
            reply_markup=mkp
        )    
        

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('delid_'))
async def delid(call:CallbackQuery, state:FSMContext):
    channle_id = call.data.split('_')[1]
    
    try:
        db.delete_channel_posting(channle_id)
        await call.message.answer(f'Канал успешно удален!', reply_markup=start_kb())
    except Exception as e:
        print(e)
        await call.message.answer(f'Что то пошло не так, попробуйте еще раз!', reply_markup=start_kb())    


# НАстройка постинга
@dp.callback_query_handler(text = 'planposting')
async def planposting(call:CallbackQuery):
    user_id = call.from_user.id
    
    if user_id in admins:
        mkp = InlineKeyboardMarkup()
        btn1 = InlineKeyboardButton(f'⚙️Настроить постинг', callback_data=f'settingsposting')
        btn2 = InlineKeyboardButton(f'👈Назад', callback_data=f'backmenu')
        mkp.add(btn1).add(btn2)
        
        await call.message.answer(f'Выберите действие:', reply_markup=mkp)
        

@dp.callback_query_handler(text = 'settingsposting')        
async def settingsposting(call:CallbackQuery):
    all_post = db.get_all_posts()
        
    mkp = InlineKeyboardMarkup()
    for post in all_post:
        mkp.add(InlineKeyboardButton(f"{post['id_post']}", callback_data=f"postngsett_{post['id_post']}"))
    mkp.add(InlineKeyboardButton(f'Отмена', callback_data=f'backmenu'))

    await call.message.answer(
        f'Выберите пост:',
        reply_markup=mkp
    )
    

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('postngsett_'))
async def postingsettings(call:CallbackQuery, state:FSMContext):
    id_post = call.data.split('_')[1]
    
    async with state.proxy() as data:
        data['id_post'] = id_post
    
    keyboard = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton('Пн', callback_data='day_Pn')
    btn2 = InlineKeyboardButton('Вт', callback_data='day_Vt')
    btn3 = InlineKeyboardButton('Ср', callback_data='day_Sr')
    btn4 = InlineKeyboardButton('Чт', callback_data='day_Cht')
    btn5 = InlineKeyboardButton('Пт', callback_data='day_Pt')
    btn6 = InlineKeyboardButton('Сб', callback_data='day_Sb')
    btn7 = InlineKeyboardButton('Вс', callback_data='day_Vs')
    btn8 = InlineKeyboardButton(f'Пропустить', callback_data=f'day_skipday')
    keyboard.add(btn1, btn2).add(btn3, btn4).add(btn5, btn6, btn7).add(btn8)

    await call.message.answer(
        f'Выберите день недели:',
        reply_markup=keyboard
    )

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('day_'))
async def dayselect(call:CallbackQuery, state:FSMContext):
    day = call.data.split('_')[1]
    
    async with state.proxy() as data:
        data['day'] = day
    
    
    mkp = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(f'Отмена', callback_data=f'cancel')
    btn2 = InlineKeyboardButton(f'Пропустить', callback_data=f'sckiptime')
    mkp.add(btn1, btn2)
    
    await call.message.answer(
        f'Введите вермя постинга (10:00, 20:10):',
        reply_markup=mkp
    )
    
    await timePosting.time.set()


@dp.message_handler(state = timePosting.time)
async def timePostingTime(m:Message, state:FSMContext):
    time_posting = m.text
    
    async with state.proxy() as data:
        day = data['day'] 
        id_post = data['id_post']
    
    
# Отмена действия при удаление
@dp.callback_query_handler(text = 'canceldelchannelid')
async def canceldelchannelid(call:CallbackQuery, state:FSMContext):
    await call.message.delete()
    await call.message.answer(f'Вы отменили действия!', reply_markup=start_kb())
    await state.finish()


# Отмена добавления канала
@dp.callback_query_handler(text = 'cancelchannel', state = addChannel.name)
@dp.callback_query_handler(text = 'cancelchannel', state = addChannel.channel_id)
async def cancelChannel(call:CallbackQuery, state:FSMContext):
    await call.message.delete()
    await call.message.answer(f'Вы отменили добавление канала!', reply_markup=start_kb())
    await state.finish()


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