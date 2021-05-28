from typing import Set, Tuple, List, Union, Optional

from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.callback_data import CallbackData

from give_money_bot.config import USERS
from give_money_bot.config import Emoji
from give_money_bot.db.db_connector import Credit
from give_money_bot.tg_bot.callback_data import CALLBACK

credit_amount_data = CallbackData(CALLBACK.save_credit, "value")
user_choose_data = CallbackData(CALLBACK.choose_user_for_credit, "id", "has_mark")
credit_choose_data = CallbackData(
    CALLBACK.choose_credit_for_return, "index", "has_mark"
)
check_return_data = CallbackData(CALLBACK.check_return_of_credit, "credit_id", "value")

main_markup = ReplyKeyboardMarkup(resize_keyboard=True).row(
    KeyboardButton("+"), KeyboardButton("-"), KeyboardButton("info")
)

cancel_crt_credit_inline = InlineKeyboardButton(
    "Отмена", callback_data=CALLBACK.cancel_crt_credit
)
return_credit_inline = InlineKeyboardButton(
    "Вернуть выбранные долги", callback_data=CALLBACK.return_credits
)
cancel_return_credit_inline = InlineKeyboardButton(
    "Отмена", callback_data=CALLBACK.cancel_return_credits
)


def get_check_markup(credit_id: Union[str, int], value: bool) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    if value:
        markup.add(
            InlineKeyboardButton(
                f"Все верно{Emoji.TRUE}", callback_data=CALLBACK.check_return_approve
            )
        )
        markup.add(
            InlineKeyboardButton(
                f"Это не так{Emoji.FALSE}", callback_data=CALLBACK.check_return_reject
            )
        )
        markup.add(
            InlineKeyboardButton(
                "Сохранить", callback_data=check_return_data.new(credit_id, "1")
            )
        )
    else:
        markup.add(
            InlineKeyboardButton(
                f"Все верно{Emoji.FALSE}", callback_data=CALLBACK.check_return_approve
            )
        )
        markup.add(
            InlineKeyboardButton(
                f"Это не так{Emoji.TRUE}", callback_data=CALLBACK.check_return_reject
            )
        )
        markup.add(
            InlineKeyboardButton(
                "Сохранить", callback_data=check_return_data.new(credit_id, "0")
            )
        )
    return markup


def get_data_from_check(markup: InlineKeyboardMarkup) -> Tuple[int, str]:
    data = markup["inline_keyboard"][2][0].callback_data
    parsed_data = check_return_data.parse(data)
    return int(parsed_data.get("credit_id")), parsed_data.get("value")


def get_credits_markup(
    user_credits: List[Credit], marked_credits: set
) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    for i, credit in enumerate(user_credits, 1):
        if credit.id in marked_credits:
            has_mark = 1
            text = f"{i} {Emoji.TRUE}"
        else:
            has_mark = 0
            text = f"{i} {Emoji.FALSE}"
        markup.add(
            InlineKeyboardButton(
                text, callback_data=credit_choose_data.new(credit.id, has_mark)
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
    for user_id in USERS.keys():
        if user_id != for_user_id:
            if user_id in users:
                has_mark = 1
                text = f"{USERS[user_id]}{Emoji.TRUE}"
            else:
                has_mark = 0
                text = f"{USERS[user_id]}{Emoji.FALSE}"

            markup.add(
                InlineKeyboardButton(
                    text, callback_data=user_choose_data.new(user_id, has_mark)
                )
            )
    inline_save = InlineKeyboardButton(
        "Сохранить", callback_data=credit_amount_data.new(value)
    )
    markup.add(
        inline_save,
        cancel_crt_credit_inline,
    )
    return markup


def get_data_from_markup(
    markup: InlineKeyboardMarkup,
) -> Tuple[Optional[int], Set[int]]:
    users = set()
    value = None
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
