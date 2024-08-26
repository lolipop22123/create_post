import re
import asyncio

from telethon import TelegramClient, events


async def parspost(api_id, api_hash, channel_username, my_channel):
    # Инициализируем асинхронный клиент
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
    
    
# async def start_parspost(api_id, api_hash, channel_username, my_channel):
#     # Создаем задачу и добавляем ее в список
#     task = asyncio.create_task(parspost(api_id, api_hash, channel_username, my_channel))
#     tasks.append(task)
#     return task