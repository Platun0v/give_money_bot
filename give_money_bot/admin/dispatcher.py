from aiogram import Router, types
from sqlalchemy.orm import Session

from give_money_bot import bot
from give_money_bot.db import db_connector as db
from give_money_bot.db.models import User
from give_money_bot.utils.log import logger
from give_money_bot.utils.misc import CheckAdmin


async def add_user(message: types.Message, user: User, session: Session) -> None:
    _, user_id, name = message.text.split()
    logger.info(f"{user.name=} asked for adding user {user_id=} {name=}")
    db.add_user(session, int(user_id), name)
    await message.answer("Added user")


async def add_show_user(message: types.Message, user: User, session: Session) -> None:
    pass
    # lst = message.text.split()
    # _, user_id, user_ids = lst[0], lst[1], lst[2:]
    # logger.info(f"{user.name=} asked for adding show user {user_id=} {user_ids=}")
    # db.add_show_users(session, int(user_id), list(map(int, user_ids)))
    # await message.answer("Added users for showing")


async def send_message_to_users(message: types.Message, session: Session, user: User) -> None:
    send_message = message.text[len("/send "):]
    users = db.get_users(session)
    for user_ in users:
        try:
            await bot.send_message(user_.user_id, send_message)
        except Exception as e:
            logger.error(f"{e=}")


router = Router()
router.message.bind_filter(CheckAdmin)

router.message.register(add_user, commands=["add_user"])
router.message.register(add_show_user, commands=["add_show_user"])
router.message.register(send_message_to_users, commands=["send"])
