import time
from asyncio import sleep

from aiogram import Bot, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from loguru import logger as log
from sqlalchemy.orm import Session

from give_money_bot.db import db_connector as db
from give_money_bot.db.db_connector import DbException
from give_money_bot.db.models import User
from give_money_bot.tg_bot.keyboards import main_keyboard
from give_money_bot.utils.misc import CheckAdmin


async def add_user(message: types.Message, user: User, session: Session, bot: Bot) -> None:
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


async def prc_substitute_user(message: types.Message, user: User, session: Session, state: FSMContext) -> None:
    lst = message.text.split()
    if len(lst) < 2:
        await message.answer("Wrong format")
        return

    substitute_with_user = " ".join(lst[1:])
    if substitute_with_user.isdigit():
        substitute_user_id = int(substitute_with_user)
        try:
            substitute_user = db.get_user(session, substitute_user_id)
        except DbException:
            await message.answer("User not found")
            return
    else:
        substitute_user_none = db.find_user_by_str(session, substitute_with_user)
        if substitute_user_none is None:
            await message.answer("User not found")
            return
        substitute_user = substitute_user_none

    log.info(f"{user.name=} asked for substitute user {substitute_with_user}")

    await state.clear()
    db.substitute_user(session, message.from_user.id, substitute_user.user_id)
    await message.answer(f"Substituted with {substitute_user}")


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


async def bot_commands(message: types.Message, user: User, session: Session, state: FSMContext) -> None:
    await message.answer(
        "Commands:\n"
        "/add_user <user_id> <name> - add user to db\n"
        "/substitute <user_id> - substitute user with user_id\n"
        "/clear_substitution - clear substitution\n"
        "/send <message> - send message to all users\n"
    )


router = Router()
router.message.bind_filter(CheckAdmin)

router.message.register(add_user, Command(commands="add_user"))
router.message.register(add_show_user, Command(commands="add_show_user"))
router.message.register(send_message_to_users, Command(commands="send"))
router.message.register(prc_substitute_user, Command(commands="substitute"))
router.message.register(clear_substitution, Command(commands="clear_substitution"))
router.message.register(bot_commands, Command(commands="cmds"))
