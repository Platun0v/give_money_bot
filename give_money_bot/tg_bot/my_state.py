from aiogram.dispatcher.filters.state import StatesGroup, State


class AddState(StatesGroup):
    read_num = State()
