from typing import Set, Tuple, List, Union, Optional, Dict

from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.callback_data import CallbackData

from give_money_bot.config import Emoji
from give_money_bot.db.db_connector import Credit, User, db
from give_money_bot.tg_bot.callback_data import CALLBACK
from give_money_bot.utils.strings import Strings

credit_amount_data = CallbackData(CALLBACK.save_credit, "value")
user_choose_data = CallbackData(CALLBACK.choose_user_for_credit, "id", "has_mark")
credit_choose_data = CallbackData(
    CALLBACK.choose_credit_for_return, "index", "has_mark"
)

main_markup = ReplyKeyboardMarkup(resize_keyboard=True).row(
    KeyboardButton("-"), KeyboardButton("info")
)

cancel_crt_credit_inline = InlineKeyboardButton(
    Strings.CANCEL, callback_data=CALLBACK.cancel_crt_credit
)
return_credit_inline = InlineKeyboardButton(
    "Вернуть выбранные долги", callback_data=CALLBACK.return_credits
)
cancel_return_credit_inline = InlineKeyboardButton(
    Strings.CANCEL, callback_data=CALLBACK.cancel_return_credits
)


def get_credits_markup(
    user_credits: Dict[int, int], marked_credits: Set[int]
) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    for user_id, credit_sum in user_credits.items():
        if user_id in marked_credits:
            has_mark = 1
            text = f"{db.get_user(user_id).name} - {credit_sum} {Emoji.TRUE}"
        else:
            has_mark = 0
            text = f"{db.get_user(user_id).name} - {credit_sum} {Emoji.FALSE}"
        markup.add(
            InlineKeyboardButton(
                text, callback_data=credit_choose_data.new(user_id, has_mark)
            )
        )
    markup.add(return_credit_inline)
    markup.add(cancel_return_credit_inline)
    return markup


def get_marked_credits(markup: InlineKeyboardMarkup) -> Set[int]:
    marked_credits = set()
    for _ in markup["inline_keyboard"]:
        for elem in _:
            if CALLBACK.choose_credit_for_return in elem.callback_data:
                data = credit_choose_data.parse(elem.callback_data)
                if data.get("has_mark") == "1":
                    marked_credits.add(int(data.get("index")))
    return marked_credits


def get_credit_id(data: str) -> int:
    return int(credit_choose_data.parse(data).get("index"))


def get_keyboard_users_for_credit(
    for_user_id: int, value: int, users: Set[int]
) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    for user in db.get_show_user(for_user_id):
        if user.user_id == for_user_id:
            continue
        if user.user_id in users:
            has_mark = 1
            text = f"{user.name}{Emoji.TRUE}"
        else:
            has_mark = 0
            text = f"{user.name}{Emoji.FALSE}"

        markup.add(
            InlineKeyboardButton(
                text, callback_data=user_choose_data.new(user.user_id, has_mark)
            )
        )
    inline_save = InlineKeyboardButton(
        Strings.SAVE, callback_data=credit_amount_data.new(value)
    )
    markup.add(
        inline_save,
        cancel_crt_credit_inline,
    )
    return markup


def get_data_from_markup(
    markup: InlineKeyboardMarkup,
) -> Tuple[int, Set[int]]:
    users = set()
    value = 0
    for _ in markup["inline_keyboard"]:
        for elem in _:
            if CALLBACK.save_credit in elem.callback_data:
                value = int(credit_amount_data.parse(elem.callback_data).get("value"))
            if CALLBACK.choose_user_for_credit in elem.callback_data:
                data = user_choose_data.parse(elem.callback_data)
                if data.get("has_mark") == "1":
                    users.add(int(data.get("id")))
    return value, users


def get_amount_from_markup(markup: InlineKeyboardMarkup) -> Optional[int]:
    for _ in markup["inline_keyboard"]:
        for elem in _:
            if CALLBACK.save_credit in elem.callback_data:
                return int(credit_amount_data.parse(elem.callback_data).get("value"))
    return None


def get_user_id(data: str) -> int:
    return int(user_choose_data.parse(data).get("id"))
