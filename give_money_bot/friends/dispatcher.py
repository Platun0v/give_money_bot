from math import ceil
from typing import Dict, List, cast

from aiogram import F, Router, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage
from aiogram.types import CallbackQuery
from loguru import logger as log
from sqlalchemy.orm import Session

from give_money_bot.config import cfg
from give_money_bot.db import crud as db
from give_money_bot.db.crud import DbException
from give_money_bot.db.models import ShowTypes, User, AccountStatus
from give_money_bot.friends import keyboards as kb
from give_money_bot.friends.callback import RequestAddNewUserCallback, RequestAddNewUserAction
# from give_money_bot.friends.callback import UserEditVisibilityCallback
# from give_money_bot.friends.keyboards import EditVisibilityAction, EditVisibilityCallback
from give_money_bot.friends.states import FriendsMenuStates
from give_money_bot.friends.strings import Strings
from give_money_bot.tg_bot.bot import send_main_menu
from give_money_bot.tg_bot.strings import Strings as tg_strings
from give_money_bot.utils.misc import CheckUser, get_state_data, update_state_data, send_message


# ======================================= SETTINGS MENU =======================================
async def send_friends_menu(message: types.Message, state: FSMContext, user: User) -> None:
    await state.set_state(FriendsMenuStates.friends_menu)
    await message.answer(Strings.menu_friends_answer, reply_markup=kb.friends_menu_markup)


async def exit_friends_menu(message: types.Message, state: FSMContext, user: User) -> SendMessage:
    await state.clear()
    return await send_main_menu(message, user)


# ======================================= ADD USER =======================================
async def ask_for_new_user(message: types.Message, state: FSMContext, user: User) -> None:
    await state.set_state(FriendsMenuStates.new_user)
    await message.answer(Strings.ask_for_new_user, reply_markup=kb.cancel_markup)


async def add_new_user(message: types.Message, state: FSMContext, user: User, session: Session, bot: Bot) -> SendMessage:
    if message.contact is not None:
        if message.contact.user_id is None:
            return SendMessage(chat_id=message.chat.id, text=Strings.user_not_found)
        try:
            db.get_user(session, message.contact.user_id)
            return SendMessage(chat_id=message.chat.id, text=Strings.user_already_exists)
        except DbException:
            pass

        new_user = User(
            user_id=message.contact.user_id,
            name=f"{message.contact.first_name} {message.contact.last_name if message.contact.last_name is not None else ''}",
            tg_name=f"{message.contact.first_name} {message.contact.last_name if message.contact.last_name is not None else ''}",
            phone_number=message.contact.phone_number,
            invited_by=user.user_id,
        )
        new_user = db.add_user(session, new_user)
    elif message.forward_from is not None:
        try:
            db.get_user(session, message.forward_from.id)
            return SendMessage(chat_id=message.chat.id, text=Strings.user_already_exists)
        except DbException:
            pass

        new_user = User(
            user_id=message.forward_from.id,
            name=f"{message.forward_from.first_name} {message.forward_from.last_name if message.forward_from.last_name is not None else ''}",
            tg_name=f"{message.forward_from.first_name} {message.forward_from.last_name if message.forward_from.last_name is not None else ''}",
            tg_alias=message.forward_from.username,
            invited_by=user.user_id,
        )
        new_user = db.add_user(session, new_user)
    else:
        return SendMessage(chat_id=message.chat.id, text=Strings.ask_for_new_user)

    await state.set_state(FriendsMenuStates.friends_menu)
    await message.answer(Strings.sent_request_to_add_user, reply_markup=kb.friends_menu_markup)
    await send_message(
        bot=bot,
        chat_id=cfg.admin_id,
        text=Strings.admin_new_user_request(user, new_user),
        reply_markup=kb.admin_new_user_request_markup(new_user),
    )
    return SendMessage(chat_id=message.chat.id, text=Strings.menu_friends_answer, reply_markup=kb.friends_menu_markup)


async def accept_request_to_add_user(call: CallbackQuery, state: FSMContext, user: User, session: Session, callback_data: RequestAddNewUserCallback, bot: Bot) -> SendMessage:
    new_user = db.get_user(session, callback_data.user_id)
    new_user.account_status = AccountStatus.ACTIVE.value
    db.add_user(session, new_user)
    await send_message(bot=bot, chat_id=new_user.invited_by, text=Strings.admin_new_user_request_accepted(new_user))
    return SendMessage(chat_id=call.message.chat.id, text=Strings.menu_friends_answer)


async def reject_request_to_add_user(call: CallbackQuery, state: FSMContext, user: User, session: Session, callback_data: RequestAddNewUserCallback, bot: Bot) -> SendMessage:
    new_user = db.get_user(session, callback_data.user_id)
    new_user.account_status = AccountStatus.BANNED.value
    db.add_user(session, new_user)
    await send_message(bot=bot, chat_id=new_user.invited_by, text=Strings.admin_new_user_request_rejected(new_user))
    return SendMessage(chat_id=call.message.chat.id, text=Strings.admin_reject_answer)


async def cancel_add_new_user(message: types.Message, state: FSMContext, user: User) -> SendMessage:
    await state.set_state(FriendsMenuStates.friends_menu)
    return SendMessage(chat_id=message.chat.id, text=Strings.menu_friends_answer, reply_markup=kb.friends_menu_markup)


# ======================================= ROUTER =======================================
router = Router()
router.message.bind_filter(CheckUser)

# ======================================= SETTINGS MENU =======================================
router.message.register(send_friends_menu, F.text == tg_strings.menu_friends)
router.message.register(
    exit_friends_menu,
    FriendsMenuStates.friends_menu,
    F.text == Strings.menu_exit,
)

# ======================================= ADD USER =======================================
router.message.register(
    ask_for_new_user,
    FriendsMenuStates.friends_menu,
    F.text == Strings.menu_add_new_user,
)
router.message.register(
    cancel_add_new_user,
    FriendsMenuStates.new_user,
    F.text == Strings.cancel,
)
router.callback_query.register(
    accept_request_to_add_user,
    RequestAddNewUserCallback.filter(F.action == RequestAddNewUserAction.save),
)
router.callback_query.register(
    reject_request_to_add_user,
    RequestAddNewUserCallback.filter(F.action == RequestAddNewUserAction.cancel),
)
router.message.register(add_new_user, FriendsMenuStates.new_user)

# ======================================= EXIT =======================================
router.message.register(exit_friends_menu, FriendsMenuStates.friends_menu)  # If user sends random message, go back to menu
