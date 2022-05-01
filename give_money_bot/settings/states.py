from aiogram.dispatcher.fsm.state import State, StatesGroup


class SettingsStates(StatesGroup):
    settings = State()
    new_user = State()
