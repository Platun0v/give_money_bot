from aiogram import types
from aiogram.dispatcher import FSMContext

from give_money_bot import dp
from give_money_bot.config import Emoji
from give_money_bot.db.models import User
from give_money_bot.settings import keyboards as kb
from give_money_bot.settings.states import SettingsStates
from give_money_bot.tg_bot.bot import send_main_menu
from give_money_bot.tg_bot.utils import check_user

from .strings import Strings


async def send_settings_menu(message: types.Message, user: User) -> None:
    await SettingsStates.settings.set()
    await message.answer(Strings.menu_settings_answer, reply_markup=kb.settings_markup)


async def ask_for_new_user(message: types.Message, state: FSMContext, user: User) -> None:
    await state.set_state(SettingsStates.new_user)
    await message.answer(Strings.ask_for_new_user, reply_markup=types.ReplyKeyboardRemove())


async def add_new_user(message: types.Message, state: FSMContext, user: User) -> None:
    await state.set_state(SettingsStates.settings)
    await message.answer(Strings.new_user_added, reply_markup=kb.settings_markup)


async def exit_settings_menu(message: types.Message, state: FSMContext, user: User) -> None:
    await state.finish()
    await send_main_menu(message, user)


def load_module() -> None:
    dp.register_message_handler(send_settings_menu, check_user, text=Emoji.SETTINGS)
    dp.register_message_handler(
        exit_settings_menu,
        check_user,
        state=SettingsStates.settings,
        text=Strings.menu_exit,
    )
    dp.register_message_handler(
        ask_for_new_user,
        check_user,
        state=SettingsStates.settings,
        text=Strings.menu_add_new_user,
    )
    dp.register_message_handler(add_new_user, check_user, state=SettingsStates.new_user)
