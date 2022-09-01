from asyncio import sleep

from aiogram import Bot, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from loguru import logger as log
from sqlalchemy.orm import Session

from give_money_bot.db import db_connector as db
from give_money_bot.db.models import User
from give_money_bot.tg_bot.keyboards import main_keyboard
from give_money_bot.utils.misc import CheckAdmin


async def add_user(message: types.Message, user: User, session: Session) -> None:
    _, user_id, name = message.text.split()
    log.info(f"{user.name=} asked for adding user {user_id=} {name=}")
    db.add_user(session, int(user_id), name)
    await message.answer("Added user")


async def add_show_user(message: types.Message, user: User, session: Session) -> None:
    pass
    # lst = message.text.split()
    # _, user_id, user_ids = lst[0], lst[1], lst[2:]
    # logger.info(f"{user.name=} asked for adding show user {user_id=} {user_ids=}")
    # db.add_show_users(session, int(user_id), list(map(int, user_ids)))
    # await message.answer("Added users for showing")


async def substitute_user(message: types.Message, user: User, session: Session, state: FSMContext) -> None:
    _, substitute_with_user = message.text.split()
    substitute_user_id = int(substitute_with_user)

    log.info(f"{user.name=} asked for substitute user {substitute_with_user}")

    await state.clear()
    db.substitute_user(session, message.from_user.id, substitute_user_id)
    await message.answer(f"Substituted with {substitute_with_user}")


async def clear_substitution(message: types.Message, user: User, session: Session, state: FSMContext) -> None:
    log.info(f"{user.name=} asked for clearing substitution")
    await state.clear()
    db.clear_substitute(session, message.from_user.id)
    await message.answer("Cleared substitution")


async def send_message_to_users(
    bot: Bot, message: types.Message, session: Session, state: FSMContext, user: User
) -> None:
    send_message = ""
    if message.text is not None:
        send_message = message.text[len("/send ") :]

    users = db.get_users(session)
    for user_ in users:
        try:
            await bot.send_message(
                chat_id=user_.user_id, text=send_message, disable_notification=True, reply_markup=main_keyboard
            )
            st_key = StorageKey(bot_id=bot.id, chat_id=user_.user_id, user_id=user_.user_id)
            state.key = st_key
            await state.set_state(None)
            await sleep(0.05)
        except TelegramBadRequest:
            log.warning(f"Cant send message to {user_.name=}")
        except Exception as e:
            log.error(f"{e=}")


router = Router()
router.message.bind_filter(CheckAdmin)

router.message.register(add_user, Command(commands="add_user"))
router.message.register(add_show_user, Command(commands="add_show_user"))
router.message.register(send_message_to_users, Command(commands="send"))
router.message.register(substitute_user, Command(commands="substitute"))
router.message.register(clear_substitution, Command(commands="clear_substitution"))
