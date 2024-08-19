from aiogram.dispatcher.filters.state import State, StatesGroup


class createPost(StatesGroup):
    text = State()
    photo = State()
    ready = State()  # Состояние для завершения


class addChannel(StatesGroup):
    name = State()
    channel_id = State()


class timePosting(StatesGroup):
    time = State()