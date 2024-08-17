import os 

from aiogram import types, Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
BOT_NICKNAME = os.getenv('BOT_NICKNAME')
admins = [6956440009]

bot = Bot(token = TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp =Dispatcher(bot, storage = storage)
dp.middleware.setup(LoggingMiddleware())

#DB
# db = DB('calendar', 'postgres', '1111', 'localhost')