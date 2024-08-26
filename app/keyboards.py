from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)


def start_kb():
    mkp = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton(f'♻️Управление постами', callback_data=f'settingspost')
    btn2 = InlineKeyboardButton(f'⌛️Запланировать постинг', callback_data=f'planposting')
    btn3 = InlineKeyboardButton(f'➕Добавить канал', callback_data=f'addchannel')
    btn4 = InlineKeyboardButton(f'➖Удаление канала', callback_data=f'deletechanel')
    btn5 = InlineKeyboardButton(f'📨Пересылка', callback_data=f'replaceMessage')
    btn6 = InlineKeyboardButton(f'🔗Создать сессию', callback_data=f'createsession')
    mkp.add(btn1).add(btn2).add(btn3).add(btn4).add(btn5, btn6)
    
    return mkp