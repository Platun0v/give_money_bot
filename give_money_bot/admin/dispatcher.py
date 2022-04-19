from aiogram import types

from give_money_bot import dp
from give_money_bot.db.db_connector import db
from give_money_bot.db.models import User
from give_money_bot.tg_bot.utils import check_admin
from give_money_bot.utils.log import logger


async def add_user(message: types.Message, user: User) -> None:
    _, user_id, name = message.text.split()
    logger.info(f"{user.name=} asked for adding user {user_id=} {name=}")
    db.add_user(user_id, name)
    await message.answer("Added user")


async def add_show_user(message: types.Message, user: User) -> None:
    lst = message.text.split()
    _, user_id, user_ids = lst[0], lst[1], lst[2:]
    logger.info(f"{user.name=} asked for adding show user {user_id=} {user_ids=}")
    db.add_show_users(user_id, user_ids)
    await message.answer("Added users for showing")


def load_module() -> None:
    dp.register_message_handler(add_user, check_admin, commands=["add_user"])
    dp.register_message_handler(add_show_user, check_admin, commands=["add_show_user"])
