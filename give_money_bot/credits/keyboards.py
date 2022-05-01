from typing import Dict, Optional, Set, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from give_money_bot.db.models import User
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from give_money_bot.credits.callback_data import CALLBACK, CreditAmountData, CreditChooseData, UserChooseData
from give_money_bot.credits.strings import Strings
from give_money_bot.db import db_connector as db


def get_credits_markup(
    user_credits: Dict[int, int], marked_credits: Set[int], session: Session
) -> InlineKeyboardMarkup:
    markup = []
    for user_id, credit_sum in user_credits.items():
        if user_id in marked_credits:
            has_mark = 1
            text = f"{db.get_user(session, user_id).name} - {credit_sum} {Strings.TRUE}"
        else:
            has_mark = 0
            text = f"{db.get_user(session, user_id).name} - {credit_sum} {Strings.FALSE}"
        markup.append([
            InlineKeyboardButton(
                text=text,
                callback_data=CreditChooseData(index=user_id, has_mark=has_mark).pack(),
            )]
        )
    markup.append([InlineKeyboardButton(text=Strings.RETURN_CHOSEN_CREDITS, callback_data=CALLBACK.return_credits)])
    markup.append([InlineKeyboardButton(text=Strings.CANCEL, callback_data=CALLBACK.cancel_return_credits)])
    return InlineKeyboardMarkup(inline_keyboard=markup)


def get_marked_credits(markup: InlineKeyboardMarkup) -> Set[int]:
    marked_credits = set()
    for _ in markup.inline_keyboard:
        for elem in _:
            if CALLBACK.choose_credit_for_return in elem.callback_data:
                data = CreditChooseData.unpack(elem.callback_data)
                if data.has_mark == 1:
                    marked_credits.add(data.index)
    return marked_credits


def get_keyboard_users_for_credit(
    for_user_id: int, value: int, chosen_users: Set[int], users: Set[User], session: Session
) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    for user in users:
        if user.user_id == for_user_id:
            continue
        if user.user_id in chosen_users:
            has_mark = 1
            text = f"{user.name}{Strings.TRUE}"
        else:
            has_mark = 0
            text = f"{user.name}{Strings.FALSE}"

        markup.append([
            InlineKeyboardButton(
                text=text,
                callback_data=UserChooseData(user_id=user.user_id, has_mark=has_mark).pack(),
            )]
        )
    markup.append([InlineKeyboardButton(text=Strings.SAVE, callback_data=CreditAmountData(value=value).pack())])
    markup.append([InlineKeyboardButton(text=Strings.CANCEL, callback_data=CALLBACK.cancel_create_credit)])
    return InlineKeyboardMarkup(inline_keyboard=markup)


def get_data_from_markup(
    markup: InlineKeyboardMarkup,
) -> Tuple[int, Set[int]]:
    users = set()
    value = 0
    for _ in markup.inline_keyboard:
        for elem in _:
            if CALLBACK.save_new_credit in elem.callback_data:
                value = CreditAmountData.unpack(elem.callback_data).value
            if CALLBACK.choose_users_for_credit in elem.callback_data:
                data = UserChooseData.unpack(elem.callback_data)
                if data.has_mark == 1:
                    users.add(data.user_id)
    return value, users


def get_amount_from_markup(markup: InlineKeyboardMarkup) -> Optional[int]:
    for _ in markup.inline_keyboard:
        for elem in _:
            if CALLBACK.save_new_credit in elem.callback_data:
                return CreditAmountData.unpack(elem.callback_data).value
    return None
