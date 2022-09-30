from typing import Dict, List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.orm import Session

from give_money_bot.credits.callback import (
    AddCreditAction,
    AddCreditCallback,
    ChooseUserAddCreditCallback,
    ChooseUserReturnCreditsCallback,
    RemoveCreditAction,
    RemoveCreditCallback,
    ReturnCreditsAction,
    ReturnCreditsCallback,
)
from give_money_bot.credits.states import AddCreditData, ReturnCreditsData
from give_money_bot.credits.strings import Strings
from give_money_bot.db import crud as db
from give_money_bot.db.models import User


def get_credits_markup(
    user_credits: Dict[int, int], return_credit_data: ReturnCreditsData, session: Session
) -> InlineKeyboardMarkup:
    markup = []
    for user_id, credit_sum in user_credits.items():
        if user_id in return_credit_data.users:
            text = f"{db.get_user(session, user_id).name} - {credit_sum} {Strings.TRUE}"
        else:
            text = f"{db.get_user(session, user_id).name} - {credit_sum} {Strings.FALSE}"

        markup.append(
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=ChooseUserReturnCreditsCallback(user_id=user_id).pack(),
                )
            ]
        )
    markup.append(
        [
            InlineKeyboardButton(
                text=Strings.RETURN_CHOSEN_CREDITS,
                callback_data=ReturnCreditsCallback(action=ReturnCreditsAction.save).pack(),
            )
        ]
    )
    markup.append(
        [
            InlineKeyboardButton(
                text=Strings.CANCEL, callback_data=ReturnCreditsCallback(action=ReturnCreditsAction.cancel).pack()
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=markup)


def get_keyboard_add_credit(for_user_id: int, add_credit_data: AddCreditData, session: Session) -> InlineKeyboardMarkup:
    markup = []

    users: List[User]
    if add_credit_data.show_more:
        users = db.get_users_with_show_more(session, for_user_id)
    else:
        users = db.get_users_with_show_always(session, for_user_id)

    for user in users:
        if user.user_id == for_user_id:
            continue
        if user.user_id in add_credit_data.users:
            text = f"{user.name}{Strings.TRUE}"
        else:
            text = f"{user.name}{Strings.FALSE}"

        markup.append(
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=ChooseUserAddCreditCallback(user_id=user.user_id).pack(),
                )
            ]
        )
    if add_credit_data.show_more:  # if we DONT need to show more users, add button with show more text
        markup.append(
            [
                InlineKeyboardButton(
                    text=Strings.CANCEL_SHOW_MORE_USERS,
                    callback_data=AddCreditCallback(action=AddCreditAction.show_more).pack(),
                )
            ]
        )
    else:
        markup.append(
            [
                InlineKeyboardButton(
                    text=Strings.SHOW_MORE_USERS,
                    callback_data=AddCreditCallback(action=AddCreditAction.show_more).pack(),
                )
            ]
        )

    markup.append(
        [InlineKeyboardButton(text=Strings.SAVE, callback_data=AddCreditCallback(action=AddCreditAction.save).pack())]
    )
    markup.append(
        [
            InlineKeyboardButton(
                text=Strings.CANCEL, callback_data=AddCreditCallback(action=AddCreditAction.cancel).pack()
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=markup)


def kb_rm_credit() -> InlineKeyboardMarkup:
    markup = [
        [
            InlineKeyboardButton(
                text=Strings.CANCEL, callback_data=RemoveCreditCallback(action=RemoveCreditAction.cancel).pack()
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=markup)
