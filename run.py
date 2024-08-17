import start
import asyncio
import datetime

from app import usermenu

from config import dp, bot

from aiogram.utils import executor
from aiogram.types import BotCommand



async def setup_bot_commands():
    bot_commands = [
        BotCommand(command="/start", description="Start bot")
    ]
    await bot.set_my_commands(bot_commands)


async def start_bot(dp):
    await setup_bot_commands()
    

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=lambda _: start_bot(dp))