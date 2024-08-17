from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)


def start_kb():
    mkp = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton(f'Управление постами', callback_data=f'settingspost')
    btn2 = InlineKeyboardButton(f'Запланировать постинг', callback_data=f'planposting')
    btn3 = InlineKeyboardButton(f'Добавить канал', callback_data=f'addchannel')
    mkp.add(btn1).add(btn2).add(btn3)
    
    return mkp