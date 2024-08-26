import re
from telethon import TelegramClient, events
from telethon import functions, types

api_id = 27687393
api_hash = '0f60be04554c8e66559401dba06e313a'
channel_username = 'asdsad1dasq2'   
my_channel = -1002104942315  # Используйте ID канала или группы
client = TelegramClient('session_name', api_id, api_hash)


@client.on(events.NewMessage(chats=channel_username))
async def handler(event):
    try:
        message = event.message.message
        media = event.message.media
            
        print(media)
        print(f"Received message: {message}")        
        # Отправка сообщения в другой канал
        # Отправка текста
        # if message:
        #     await client.send_message(my_channel, message)
        
        # # Отправка медиа (например, фото)
        # if media:
        #     await client.send_file(my_channel, media, caption=message if message else None)
    except Exception as e:
        print(f"Error: {e}")

async def main():
    try:
        await client.start()
        print('Программа запущена!')
        await client.run_until_disconnected()
    except Exception as e:
        print(f"Error starting the client: {e}")

# Запуск клиента
with client:
    client.loop.run_until_complete(main())
