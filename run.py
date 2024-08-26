import start
import asyncio

from app import usermenu

from config import dp, bot, db

from aiogram.utils import executor
from aiogram.types import BotCommand, InputMediaPhoto
from datetime import datetime, timedelta


async def check_posting():
    while True:
        all_posting_post = db.get_all_plan_postings()
        print(all_posting_post)
        
        days_map = {
            'Pn' : 'Monday',
            'Vt' : 'Tuesday',
            'Sr' : 'Wednesday',
            'Cht' : 'Thursday',
            'Pt' : 'Friday',
            'Sb' : 'Saturday',
            'Vs' : 'Sunday'
        }
        
        # Текущее время
        now = datetime.now()

        # Получаем текущий день недели и время
        day_of_week = now.strftime("%A") 
        current_time = now.strftime("%H:%M:%S")         
        print(f'DAY: {day_of_week}\nTIME: {current_time}')
        
        for id, post_id, time, id_channel, days in all_posting_post:
            flag_days = bool(days)  # Проверка наличия дней
            flag_time = bool(time and time != '{}')  # Проверка наличия времени и того, что оно не равно '{}'
            
            # print(f'FLAG TIME: {flag_time}\nFLAG DAYS: {flag_days}')
            # print(f'-------------------------------')
            
            if flag_time and flag_days:
                # Логика, если есть и время, и дни
                print(f'POST ID: {post_id}')
            
                # Преобразуем дни в полные названия
                full_day_names = [days_map[day] for day in days]

                # Преобразуем время из строки в объект datetime
                target_time = datetime.strptime(time, "%H:%M")
                time_difference = timedelta(minutes=10)  # Погрешность 10 минут
                
                # Проверка совпадения по дню недели и времени
                if day_of_week in full_day_names and target_time <= now <= (target_time + time_difference):
                    print(f'Совпадение по дню недели и времени для POST ID: {post_id}')
                    
                    for id_channel_one in id_channel:
                        if not db.is_post_sent_today(post_id, id_channel_one):
                            # Получение инфы о посте
                            post_info = db.get_post_by_id(post_id)
                            if 'photo_ids' in post_info and post_info['photo_ids']:
                                # Если есть фото
                                media = [InputMediaPhoto(media=photo_id) for photo_id in post_info['photo_ids']]
                                
                                # Добавляем текст к первой фотографии
                                media[0].caption = post_info['text']
                                
                                await bot.send_media_group(chat_id=id_channel_one, media=media)
                                # Запись в базу данных
                                db.add_sent_post(post_id, id_channel_one)
                            else:
                                # Если фото нет
                                await bot.send_message(chat_id=id_channel_one, text=post_info['text'])
                                # Запись в базу данных
                                db.add_sent_post(post_id, id_channel_one)
                        else:
                            print("Сообщение уже отправлялось сегодня.")
                else:
                    print("Совпадение по времени и дню недели не найдено.")
            elif not flag_time and flag_days:
                print(f'POST ID: {post_id}')
                full_day_names = [days_map[day] for day in days]
                
                if day_of_week in full_day_names:
                    print(f'Совпадение по дню недели для POST ID: {post_id}')
                    for id_channel_one in id_channel:
                        if not db.is_post_sent_today(post_id, id_channel_one):
                            # Проверка времени: отправка сообщения с 10:00 до 10:10
                            target_time = datetime.strptime("10:00:00", "%H:%M:%S")
                            time_difference = timedelta(minutes=5)
                            
                            if target_time <= now <= (target_time + time_difference):
                                print(f'Отправка сообщения в 10:00 с погрешностью 10 минут для POST ID: {post_id}')
                                
                                # Получение инфы о посте
                                post_info = db.get_post_by_id(post_id)
                                if 'photo_ids' in post_info and post_info['photo_ids']:
                                    # Если есть фото
                                    media = [InputMediaPhoto(media=photo_id) for photo_id in post_info['photo_ids']]
                                    
                                    # Добавляем текст к первой фотографии
                                    media[0].caption = post_info['text']
                                    
                                    await bot.send_media_group(chat_id=id_channel, media=media)
                                    # Запись в базу данных
                                    db.add_sent_post(post_id, id_channel)
                                else:
                                    # Если фото нет
                                    await bot.send_message(chat_id=id_channel, text=post_info['text'])
                                    # Запись в базу данных
                                    db.add_sent_post(post_id, id_channel)
                        else:
                            print("Сообщение уже отправлялось сегодня.")
                        # Ваш код для отправки сообщения
                print(f'----------\n')
            elif flag_time and not flag_days:
                print(f'POST ID: {post_id}')
            
                target_time = datetime.strptime(time, "%H:%M")  # Преобразуем время из строки в объект datetime
                time_difference = timedelta(minutes=10)  # Погрешность 10 минут
                
                # Проверка времени: отправка сообщения в указанное время с погрешностью 10 минут
                if target_time <= now <= (target_time + time_difference):
                    print(f'Отправка сообщения по времени для POST ID: {post_id}')
                    
                    for id_channel_one in id_channel:
                        if not db.is_post_sent_today(post_id, id_channel_one):
                            # Получение инфы о посте
                            post_info = db.get_post_by_id(post_id)
                            if 'photo_ids' in post_info and post_info['photo_ids']:
                                # Если есть фото
                                media = [InputMediaPhoto(media=photo_id) for photo_id in post_info['photo_ids']]
                                
                                # Добавляем текст к первой фотографии
                                media[0].caption = post_info['text']
                                
                                await bot.send_media_group(chat_id=id_channel_one, media=media)
                                # Запись в базу данных
                                db.add_sent_post(post_id, id_channel_one)
                            else:
                                # Если фото нет
                                await bot.send_message(chat_id=id_channel_one, text=post_info['text'])
                                # Запись в базу данных
                                db.add_sent_post(post_id, id_channel_one)
                        else:
                            print("Сообщение уже отправлялось сегодня.")
                else:
                    print("Время не подошло.")
            
        
        # Пауза между проверками, чтобы не нагружать процессор
        await asyncio.sleep(20)


async def setup_bot_commands():
    bot_commands = [
        BotCommand(command="/start", description="Start bot")
    ]
    await bot.set_my_commands(bot_commands)


async def start_bot(dp):
    await setup_bot_commands()
    
    # Запуск работы функции постинга 
    asyncio.create_task(check_posting())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=lambda _: start_bot(dp))