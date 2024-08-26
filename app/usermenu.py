import os
import re
import random
import asyncio

from config import bot, dp, admins, db

from telethon import TelegramClient, events
from dotenv import load_dotenv

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
from app.state import createPost, addChannel, timePosting, reposting, CreateSession
# from app.functions import parspost

load_dotenv()


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
    mkp.add(InlineKeyboardButton(f'Готово', callback_data=f'readyphoto')).add(InlineKeyboardButton(f'Отмена', callback_data=f'cancelphoto')).add(InlineKeyboardButton(f'Пропустить', callback_data=f'skipphoto'))
    
    await m.answer(
        f'Вставть фото:',
        reply_markup=mkp
    )
    
    await createPost.photo.set()


@dp.callback_query_handler(text = 'skipphoto', state = createPost.photo)
async def sckipPhoto(call:CallbackQuery, state:FSMContext):
    id_post = random.randint(100000, 999999)
    
    async with state.proxy() as data:
        photo_text = data['text_post']
    
    photo_ids = []
    
    try:
        db.create_post(id_post, photo_text, photo_ids)
        await call.message.answer(f'Пост добавлен в БД!', reply_markup=start_kb())
    except Exception as e:
        print(e)
        await call.message.answer(
            f'Что то пошло не так',
            reply_markup=start_kb()
        )
    # Завершаем состояние
    await state.finish()


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
        btn2 = InlineKeyboardButton(f'🔴Удаление постинга', callback_data=f'daleteposting')
        btn3 = InlineKeyboardButton(f'👈Назад', callback_data=f'backmenu')
        mkp.add(btn1).add(btn2).add(btn3)
        
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
async def postingsettings(call: CallbackQuery, state: FSMContext):
    id_post = call.data.split('_')[1]
    
    async with state.proxy() as data:
        data['id_post'] = id_post
        data['selected_days'] = []  # Инициализация списка выбранных дней
    
    keyboard = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton('Пн', callback_data='day_Pn')
    btn2 = InlineKeyboardButton('Вт', callback_data='day_Vt')
    btn3 = InlineKeyboardButton('Ср', callback_data='day_Sr')
    btn4 = InlineKeyboardButton('Чт', callback_data='day_Cht')
    btn5 = InlineKeyboardButton('Пт', callback_data='day_Pt')
    btn6 = InlineKeyboardButton('Сб', callback_data='day_Sb')
    btn7 = InlineKeyboardButton('Вс', callback_data='day_Vs')
    btn8 = InlineKeyboardButton(f'✅', callback_data=f'day_finish')
    btn9 = InlineKeyboardButton(f'🔻Пропустить', callback_data=f'skipdata')
    keyboard.add(btn1, btn2).add(btn3, btn4).add(btn5, btn6, btn7).add(btn8).add(btn9)

    await call.message.answer(
        f'Выберите дни недели для постинга:',
        reply_markup=keyboard
    )
    
@dp.callback_query_handler(text = 'skipdata')
async def skipdata(call:CallbackQuery, state:FSMContext):
    await call.message.delete()
    await call.message.answer('Введите время постинга (например, 10:00, 20:10):')
    
    await timePosting.time.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('day_'))
async def dayselect(call: CallbackQuery, state: FSMContext):
    day = call.data.split('_')[1]
    
    async with state.proxy() as data:
        if day == 'finish':
            selected_days = ', '.join(data['selected_days'])
            mkp = InlineKeyboardMarkup()
            btn1 = InlineKeyboardButton(f'🔻Пропустить', callback_data=f'skiptime')
            mkp.add(btn1)
            
            await call.message.answer(
                f'Вы выбрали следующие дни: {selected_days}\nВведите время постинга (например, 10:00, 20:10):',
                reply_markup=mkp
            )
            await timePosting.time.set()
        else:
            if day not in data['selected_days']:
                data['selected_days'].append(day)
            await call.answer(f'{day} добавлен.')


@dp.callback_query_handler(text = 'skiptime', state = timePosting.time)
async def timePostingSckip(call:CallbackQuery, state:FSMContext):
    await call.message.delete()
    
    time_posting = []
    async with state.proxy() as data:
        day =  data['selected_days']
        id_post = data['id_post']
        data['time_posting'] = time_posting

    new_list_day = []
    for i in day:
        if i == 'Pn':
            i = 'Понедельник'
        elif i == 'Vt':
            i = 'Вторник'
        elif i == 'Sr':
            i = 'Среда'
        elif i == 'Cht':
            i = 'Четверг'
        elif i == 'Pt':
            i = 'Пятница'
        elif i == 'Sb':
            i = 'Суббота'
        elif i == 'Vs':
            i = 'Воскресенье'
        else:
            pass
        
        new_list_day.append(i)

    channle_posting = db.get_all_channel_postings()
    
    mkp = InlineKeyboardMarkup()
    for id, name, id_channel in channle_posting:
        mkp.add(InlineKeyboardButton(f'{name}', callback_data=f'chanpost_{id_channel}'))
    mkp.add(InlineKeyboardButton(f'✅', callback_data=f'chanpost_finish'), InlineKeyboardButton(f'❌', callback_data=f'cancel'))

    await call.message.answer(
        f'Выберите каналы для постинга:',
        reply_markup=mkp
    )
    

@dp.message_handler(state = timePosting.time)
async def timePostingTime(m:Message, state:FSMContext):
    time_posting = m.text
    
    async with state.proxy() as data:
        day =  data['selected_days']
        id_post = data['id_post']
        data['time_posting'] = time_posting
    
    new_list_day = []
    for i in day:
        if i == 'Pn':
            i = 'Понедельник'
        elif i == 'Vt':
            i = 'Вторник'
        elif i == 'Sr':
            i = 'Среда'
        elif i == 'Cht':
            i = 'Четверг'
        elif i == 'Pt':
            i = 'Пятница'
        elif i == 'Sb':
            i = 'Суббота'
        elif i == 'Vs':
            i = 'Воскресенье'
        else:
            pass
        
        new_list_day.append(i)

    channle_posting = db.get_all_channel_postings()
    
    mkp = InlineKeyboardMarkup()
    for id, name, id_channel in channle_posting:
        mkp.add(InlineKeyboardButton(f'{name}', callback_data=f'chanpost_{id_channel}'))
    mkp.add(InlineKeyboardButton(f'✅', callback_data=f'chanpost_finish'), InlineKeyboardButton(f'❌', callback_data=f'cancel'))

    await m.answer(
        f'Выберите каналы для постинга:',
        reply_markup=mkp
    )


# Обработчик выбора каналов
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('chanpost_'), state = timePosting.time)
async def postset(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data == 'chanpost_finish':
            # Передача управления обработчику завершения
            await finish_channel_selection(call, state)
        else:
            channel_id = call.data.split('_')[1]
            selected_channels = data.get('selected_channels', [])
            if channel_id not in selected_channels:
                selected_channels.append(channel_id)
                data['selected_channels'] = selected_channels
            await call.answer(f'Канал с ID {channel_id} добавлен.')


# Обработчик завершения выбора каналов
async def finish_channel_selection(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    async with state.proxy() as data:
        selected_channels = data.get('selected_channels', [])
        day = data['selected_days']
        id_post = data['id_post']
        time_posting = data['time_posting']
    
    try:
        # Пример функции добавления в базу данных
        db.add_plan_posting(id_post, time_posting, selected_channels, day)
        await call.message.answer(
            f'Данные успешно добавлены✅',
            reply_markup=start_kb()  # Возвращение к стартовой клавиатуре
        )
    except Exception as e:
        print(e)
        await call.message.answer(
            f'Что-то пошло не так, попробуйте еще раз!',
            reply_markup=start_kb()  # Возвращение к стартовой клавиатуре
        )

    # Завершение состояния FSM
    await state.finish()


# Удалаение постинга
@dp.callback_query_handler(text = 'daleteposting')
async def daleteposting(call:CallbackQuery,state:FSMContext):
    user_id = call.from_user.id
    
    if user_id in admins:
        all_plan = db.get_all_plan_postings()
        dict_text = {}
        
        mkp = InlineKeyboardMarkup()
        for id, id_post, time, channel_id, days in all_plan:
            text_post = db.get_post_text(id_post)
            dict_text[id_post] = text_post
        
        if not dict_text:  # Проверяем, есть ли посты
            mkp = InlineKeyboardMarkup()
            btn1 = InlineKeyboardButton(f'⚙️Настроить постинг', callback_data=f'settingsposting')
            btn2 = InlineKeyboardButton(f'🔴Удаление постинга', callback_data=f'daleteposting')
            btn3 = InlineKeyboardButton(f'👈Назад', callback_data=f'backmenu')
            mkp.add(btn1).add(btn2).add(btn3)
            await call.message.answer("Нет доступных постов для отображения.", reply_markup=mkp)
            return
        
        async with state.proxy() as data:
            data['dict_text'] = dict_text
            data['current_index'] = 0
            data['post_ids'] = list(dict_text.keys())
        
        # Отправляем первый пост
        await send_post_message(call.message, state)
    

async def send_post_message(message: Message, state: FSMContext):
    async with state.proxy() as data:
        current_index = data['current_index']
        post_ids = data['post_ids']
        dict_text = data['dict_text']
        current_post_id = post_ids[current_index]
        current_text = dict_text[current_post_id]

        # Создаем клавиатуру с кнопками
        keyboard = InlineKeyboardMarkup()
        if current_index > 0:
            keyboard.add(InlineKeyboardButton('⬅️', callback_data='prev_post'))
        if current_index < len(post_ids) - 1:
            keyboard.add(InlineKeyboardButton('➡️', callback_data='next_post'))
        keyboard.add(InlineKeyboardButton('🗑️', callback_data=f'delete_post_{current_post_id}'))
        keyboard.add(InlineKeyboardButton(f'🔙', callback_data=f'backsettingsposting'))

        # Отправляем сообщение с текстом и кнопками
        await message.answer(current_text, reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data.startswith('delete_post_'), state='*')
async def delete_post(call: CallbackQuery, state: FSMContext):
    post_id = int(call.data.split('_')[2])  
    print(post_id)
    try:
        db.delete_plan_posting(post_id)
        print(f'CONFIRM')
        # Обновляем состояние и удаляем пост из списка
        async with state.proxy() as data:
            data['post_ids'].remove(post_id)
            if data['current_index'] >= len(data['post_ids']):
                data['current_index'] -= 1

        # Обновляем сообщение с новым постом
        await send_post_message(call.message, state)
    except Exception as e:
        print(e)
        await call.message.answer(
            f'Что-то пошло не так, попробуйте еще раз!',
            reply_markup=start_kb()  # Возвращение к стартовой клавиатуре
        )
        await state.finish()
    
    
@dp.callback_query_handler(lambda c: c.data in ['prev_post', 'next_post'], state='*')
async def navigate_posts(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data == 'prev_post':
            data['current_index'] -= 1
        elif call.data == 'next_post':
            data['current_index'] += 1

    # Обновляем сообщение с новым постом
    await send_post_message(call.message, state)


# Обработка персылки
@dp.callback_query_handler(text = 'replaceMessage')
async def replaceMessage(call:CallbackQuery):
    user_id = call.from_user.id
    
    if user_id in admins:
        mkp = InlineKeyboardMarkup()
        btn1 = InlineKeyboardButton(f'➕Добавление пары', callback_data=f'addpara')
        btn2 = InlineKeyboardButton(f'➖Удаление пары', callback_data=f'removepara')
        btn3 = InlineKeyboardButton(f'🔘Запуск', callback_data=f'readypara')
        btn4 = InlineKeyboardButton(f'🔴Остановка', callback_data=f'cancelpara')
        btn5 = InlineKeyboardButton(f'👈Назад', callback_data=f'backmenu')
        mkp.add(btn1).add(btn2).add(btn3, btn4).add(btn5)
        
        await call.message.answer(
            f'Выберите действие:', 
            reply_markup=mkp
        )
        

@dp.callback_query_handler(text = 'readypara')
async def readypara(call:CallbackQuery, state:FSMContext):
    user_id = call.from_user.id
    
    if user_id in admins:
        all_para = db.get_all_repostings()
        print(all_para)
        
        mkp = InlineKeyboardMarkup()
        for _, name, copy_id, post_id in all_para:
            mkp.add(InlineKeyboardButton(f'{name}', callback_data=f'startpara|{copy_id}|{post_id}'))
        mkp.add(InlineKeyboardButton(f'👈Назад', callback_data=f'backreplacemessage'))
        
        await call.message.answer(
            f'Сделайте свой выбор:',
            reply_markup=mkp
        )


@dp.callback_query_handler(lambda c: c.data.startswith('startpara|'))
async def startpara(call:CallbackQuery, state:FSMContext):
    copy_id = call.data.split('|')[1]
    posting_id = call.data.split('|')[2]
    
    mkp = InlineKeyboardMarkup()
    mkp.add(InlineKeyboardButton(f'✅Запустить', callback_data=f'readygood'), InlineKeyboardButton(f'⭕️Отмена', callback_data=f'cancelready'))

    async with state.proxy() as data:
        data['copy_id'] = copy_id
        data['posting_id'] = posting_id
    
    await call.message.answer(
        f'C {copy_id} в {posting_id}\n\nЗапустить?',
        reply_markup=mkp
    )


# Заппуск
# Глобальный список для хранения задач
tasks = []

async def parspost(api_id, api_hash, channel_username, my_channel):
    async with TelegramClient('session_name', api_id, api_hash) as client:
        @client.on(events.NewMessage(chats=channel_username))
        async def handler(event):
            message = event.message.message
            media = event.message.media
            
            print(message)
            print(media)
            
            # Отправка текста
            if message:
                await client.send_message(my_channel, message)
            
            # Отправка медиа (например, фото)
            if media:
                await client.send_file(my_channel, media, caption=message if message else None)

        # Работа в режиме ожидания новых сообщений
        await client.run_until_disconnected()


async def start_parspost(api_id, api_hash, channel_username, my_channel):
    # Создаем задачу и добавляем ее в список
    task = asyncio.create_task(parspost(api_id, api_hash, channel_username, my_channel))
    tasks.append(task)
    return task


@dp.callback_query_handler(text = 'readygood')
async def readygood(call:CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        copy_id = data['copy_id']
        posting_id = data['posting_id']
    
    # Запускаем `parspost` в фоне
    task = await start_parspost(os.getenv('api_id'), os.getenv('api_hash'), copy_id, int(posting_id))
    
    # Проверяем, запущена ли задача
    if task:
        await call.message.answer("Парсинг сообщений запущен!", reply_markup=start_kb())
    else:
        await call.message.answer("Не удалось запустить парсинг сообщений.")
        
    await state.finish()


# список задач
@dp.callback_query_handler(text = 'cancelpara')
async def cancelpara(call:CallbackQuery, state:FSMContext):
    if tasks:
        mkp = InlineKeyboardMarkup()
        tasks_info = []
        
        for i, task in enumerate(tasks, 1):
            task_status = "Выполняется" if not task.done() else "Завершена"
            tasks_info.append(f"Задача {i}: {task_status}")
            # Добавляем кнопку для каждой задачи
            mkp.add(InlineKeyboardButton(f'Удалить Задачу {i}', callback_data=f'delete_task_{i}'))
        
        tasks_text = "\n".join(tasks_info)
        await call.message.answer(f"Список задач:\n\n{tasks_text}", reply_markup=mkp)
    else:
        await call.message.answer("Нет запущенных задач.")


# обработчик для удаления задачи
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('delete_task_'))
async def delete_task(call: CallbackQuery):
    # Извлекаем номер задачи из callback_data
    task_number = int(re.search(r'delete_task_(\d+)', call.data).group(1))
    
    # Проверяем, существует ли задача с таким номером
    if 1 <= task_number <= len(tasks):
        task = tasks[task_number - 1]
        
        if not task.done():
            task.cancel()  # Отменяем задачу
            tasks.pop(task_number - 1)  # Удаляем задачу из списка
            
            await call.message.answer(f"Задача {task_number} была удалена и остановлена.")
        else:
            await call.message.answer(f"Задача {task_number} уже завершена.")
    else:
        await call.message.answer(f"Задача {task_number} не найдена.")


# отмена запуска репостинга
@dp.callback_query_handler(text = 'cancelready')
async def cancelready(call:CallbackQuery, state:FSMContext):
    await call.message.delete()
    user_id = call.from_user.id
    
    if user_id in admins:
        all_para = db.get_all_repostings()
        print(all_para)
        
        mkp = InlineKeyboardMarkup()
        for _, name, copy_id, post_id in all_para:
            mkp.add(InlineKeyboardButton(f'{name}', callback_data=f'startpara_{copy_id}_{post_id}'))
        mkp.add(InlineKeyboardButton(f'👈Назад', callback_data=f'backreplacemessage'))
        
        await call.message.answer(
            f'Сделайте свой выбор:',
            reply_markup=mkp
        )

        
# Назад к выбору настройки пары
@dp.callback_query_handler(text = 'backreplacemessage')
async def backreplacemessage(call:CallbackQuery, state:FSMContext):
    await call.message.delete()
    user_id = call.from_user.id
    
    if user_id in admins:
        mkp = InlineKeyboardMarkup()
        btn1 = InlineKeyboardButton(f'➕Добавление пары', callback_data=f'addpara')
        btn2 = InlineKeyboardButton(f'➖Удаление пары', callback_data=f'removepara')
        btn3 = InlineKeyboardButton(f'🔘Запуск', callback_data=f'readypara')
        btn4 = InlineKeyboardButton(f'🔴Остановка', callback_data=f'cancelpara')
        btn5 = InlineKeyboardButton(f'👈Назад', callback_data=f'backmenu')
        mkp.add(btn1).add(btn2).add(btn3, btn4).add(btn5)
        
        await call.message.answer(
            f'Выберите действие:', 
            reply_markup=mkp
        )

      
# Добавление пары
@dp.callback_query_handler(text = 'addpara')
async def addpara(call:CallbackQuery):
    mkp = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(f'Отмена', callback_data=f'canceladd')
    mkp.add(btn1)
    
    await call.message.answer(f'Введите username канала откуда брать посты:', reply_markup=mkp)

    await reposting.idCopy.set()
    

@dp.message_handler(state = reposting.idCopy)
async def repostingIdCopyText(m:Message, state:FSMContext):
    copy_id = m.text
    
    async with state.proxy() as data:
        data['copy_id'] = copy_id
    
    mkp = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(f'Отмена', callback_data=f'canceladd')
    mkp.add(btn1)
    
    await m.answer(f'Введит айди канал куда отправлять пост:', reply_markup=mkp)
    
    await reposting.idPosting.set()
    

@dp.message_handler(state = reposting.idPosting)
async def repostingIdPostingText(m:Message, state:FSMContext):
    posting_id = m.text
    
    async with state.proxy() as data:
        data['posting_id'] = posting_id
        
    mkp = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(f'Отмена', callback_data=f'canceladd')
    mkp.add(btn1)
    
    await m.answer(
        f'Придумайте имя для пары:',
        reply_markup=mkp
    )
    
    await reposting.name.set()


@dp.message_handler(state = reposting.name)
async def nameTextRepost(m:Message, state:FSMContext):
    name = m.text
    
    async with state.proxy() as data:
        copy_id = data['copy_id'] 
        posting_id = data['posting_id']
    
    try:
        db.add_reposting(name, copy_id, posting_id)
        await m.answer(f'Данные успешно записаны в БД✅', reply_markup=start_kb())
    except Exception as e:
        print(e)
        await m.answer(f'Что то пошло не так🤷\nПопробуйте еще раз!', reply_markup=start_kb())
    
    await state.finish()


# Загрузка сессии
@dp.callback_query_handler(text = 'createsession')
async def createsession(call:CallbackQuery, state:FSMContext):
    await call.message.delete()
    
    mkp = InlineKeyboardMarkup()
    mkp.add(InlineKeyboardButton(f'❌Отмена', callback_data=f'canceladdsession'))
    
    await call.message.answer(f'Вставть вашу сессию, файл:', reply_markup=mkp)

    await CreateSession.waiting_for_file.set()
    

@dp.message_handler(content_types=['document'], state = CreateSession.waiting_for_file)
async def fileSession(message:Message, state:FSMContext):
    file_id = message.document.file_id
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path
    
    # Получаем имя файла
    file_name = message.document.file_name

    # Указываем путь для сохранения
    save_path = os.path.join(os.getcwd(), file_name)

    # Загружаем файл
    await bot.download_file(file_path, save_path)
    
    await message.answer(f"Файл сессии '{file_name}' успешно загружен и сохранен в корневую директорию проекта.")

    await state.finish()


# Отмена загрузки сессии
@dp.callback_query_handler(text = 'canceladdsession', state = CreateSession.waiting_for_file)
async def CreateSessionCancel(call:CallbackQuery, state:FSMContext):
    await call.message.delete()
    await call.message.answer(f'Вы отменили действия!', reply_markup=start_kb())
    await state.finish()


# Отмена добавления
@dp.callback_query_handler(text = 'canceladd', state=reposting.name)
@dp.callback_query_handler(text = 'canceladd', state=reposting.idCopy)
@dp.callback_query_handler(text = 'canceladd', state=reposting.idPosting)
async def repostingCopyId(call:CallbackQuery, state:FSMContext):
    await call.message.delete()
    
    user_id = call.from_user.id
        
    if user_id in admins:
        await call.message.answer(
            f'Добро пожаловать в бота!',
            reply_markup=start_kb()
        )
    
    await state.finish()


# Возврат к настройке постинга
@dp.callback_query_handler(text = 'backsettingsposting')
async def backsettingsposting(call:CallbackQuery, state:FSMContext):
    await call.message.delete()
    
    mkp = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(f'⚙️Настроить постинг', callback_data=f'settingsposting')
    btn2 = InlineKeyboardButton(f'🔴Удаление постинга', callback_data=f'daleteposting')
    btn3 = InlineKeyboardButton(f'👈Назад', callback_data=f'backmenu')
    mkp.add(btn1).add(btn2).add(btn3)
    
    await call.message.answer(f'Выберите действие:', reply_markup=mkp)
    
    await state.finish()
    
    
# отмена выбора постинга
@dp.callback_query_handler(text = 'cancel', state=timePosting.time)
async def timePostingCanel(call:CallbackQuery, state:FSMContext):
    await call.message.delete()
    await call.message.answer(f'Вы отменили действия!', reply_markup=start_kb())
    await state.finish()
    
    
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