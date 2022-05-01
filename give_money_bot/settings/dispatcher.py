from aiogram import Router, types
from aiogram.dispatcher.fsm.context import FSMContext

from give_money_bot.db.models import User
from give_money_bot.settings import keyboards as kb
from give_money_bot.settings.states import SettingsStates
from give_money_bot.tg_bot.bot import send_main_menu
from give_money_bot.tg_bot.strings import Strings as tg_strings

from ..utils.misc import CheckUser
from .strings import Strings


async def send_settings_menu(message: types.Message, state: FSMContext, user: User) -> None:
    await state.set_state(SettingsStates.settings)
    await message.answer(Strings.menu_settings_answer, reply_markup=kb.settings_markup)


async def ask_for_new_user(message: types.Message, state: FSMContext, user: User) -> None:
    await state.set_state(SettingsStates.new_user)
    await message.answer(Strings.ask_for_new_user, reply_markup=types.ReplyKeyboardRemove())


async def add_new_user(message: types.Message, state: FSMContext, user: User) -> None:
    await state.set_state(SettingsStates.settings)
    await message.answer(Strings.new_user_added, reply_markup=kb.settings_markup)


async def exit_settings_menu(message: types.Message, state: FSMContext, user: User) -> None:
    await state.clear()
    await send_main_menu(message, user)


router = Router()
router.message.bind_filter(CheckUser)

router.message.register(send_settings_menu, text=tg_strings.menu_settings)
router.message.register(
    exit_settings_menu,
    SettingsStates.settings,
    text=Strings.menu_exit,
)
router.message.register(
    ask_for_new_user,
    SettingsStates.settings,
    text=Strings.menu_add_new_user,
)
router.message.register(add_new_user, state=SettingsStates.new_user)
