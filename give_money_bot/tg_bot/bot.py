from aiogram import types

from give_money_bot import dp
from give_money_bot.db.models import User
from give_money_bot.tg_bot import keyboards as kb
from give_money_bot.tg_bot.strings import Strings
from give_money_bot.tg_bot.utils import check_user
from give_money_bot.utils.log import logger


async def prc_start_command(message: types.Message, user: User) -> None:
    logger.info(f"{user.name=} started")
    await message.answer(Strings.HELLO_MESSAGE)
    await send_main_menu(message, user)


async def send_main_menu(message: types.Message, user: User) -> None:
    await message.answer(Strings.MAIN_MENU, reply_markup=kb.main_keyboard)


async def prc_get_id(message: types.Message, user: User) -> None:
    logger.info(f"{user.name=} asked for id")
    await message.answer(f"{message.from_user.id}")


def load_module() -> None:
    dp.register_message_handler(prc_start_command, check_user, commands=["start"])
    dp.register_message_handler(prc_get_id, check_user, commands=["id"])
