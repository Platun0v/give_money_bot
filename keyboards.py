from typing import Set, Tuple, List, Union

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, \
    InlineKeyboardButton, InlineKeyboardMarkup
from config import USERS
from config import Emoji
from db_connector import Credit
from aiogram.utils.callback_data import CallbackData

credit_amount_data = CallbackData("save", "value")
user_data = CallbackData("user", "id", "has_mark")
credit_data = CallbackData("credit_chose", "index", "has_mark")
check_data = CallbackData("check", "credit_id", "value")

main_markup = ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton("+"), KeyboardButton("info"))

credits_info_markup = InlineKeyboardMarkup()
credits_info_markup.add(InlineKeyboardButton("Кто мне должен?", callback_data="credits_to_user"))
credits_info_markup.add(InlineKeyboardButton("Кому я должен?", callback_data="user_credits"))

cancel_inline_button = InlineKeyboardButton("Отмена", callback_data="cancel")
return_credit_inline_button = InlineKeyboardButton("Вернуть выбранные долги", callback_data="return_credit")
cancel_credit_inline_button = InlineKeyboardButton("Я ничего еще не вернул", callback_data="credit_cancel")


def get_check_markup(credit_id: Union[str, int], value: bool) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    if value:
        markup.add(InlineKeyboardButton(f"Все верно{Emoji.TRUE}", callback_data="true"))
        markup.add(InlineKeyboardButton(f"Это не так{Emoji.FALSE}", callback_data="false"))
        markup.add(InlineKeyboardButton("Сохранить", callback_data=check_data.new(credit_id, "1")))
    else:
        markup.add(InlineKeyboardButton(f"Все верно{Emoji.FALSE}", callback_data="true"))
        markup.add(InlineKeyboardButton(f"Это не так{Emoji.TRUE}", callback_data="false"))
        markup.add(InlineKeyboardButton("Сохранить", callback_data=check_data.new(credit_id, "0")))
    return markup


def get_data_from_check(markup: InlineKeyboardMarkup) -> Tuple[int, str]:
    data = markup["inline_keyboard"][2][0].callback_data
    parsed_data = check_data.parse(data)
    return int(parsed_data.get("credit_id")), parsed_data.get("value")


def get_credits_markup(user_credits: List[Credit], marked_credits: set) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    for i, credit in enumerate(user_credits, 1):
        if credit.id in marked_credits:
            has_mark = 1
            text = f'{i} {Emoji.TRUE}'
        else:
            has_mark = 0
            text = f'{i} {Emoji.FALSE}'
        markup.add(InlineKeyboardButton(text, callback_data=credit_data.new(credit.id, has_mark)))
    markup.add(return_credit_inline_button)
    markup.add(cancel_credit_inline_button)
    return markup


def get_marked_credits(markup: InlineKeyboardMarkup) -> Set[int]:
    marked_credits = set()
    for _ in markup["inline_keyboard"]:
        for elem in _:
            if "credit_chose" in elem.callback_data:
                data = credit_data.parse(elem.callback_data)
                if data.get("has_mark") == "1":
                    marked_credits.add(int(data.get("index")))
    return marked_credits


def get_credit_id(data: str) -> int:
    return int(credit_data.parse(data).get("index"))


def get_keyboard_users_for_credit(for_user_id: int, value: int, users: Set[int]) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    for user_id in USERS.keys():
        if user_id != for_user_id:
            if user_id in users:
                has_mark = 1
                text = f'{USERS[user_id]}{Emoji.TRUE}'
            else:
                has_mark = 0
                text = f'{USERS[user_id]}{Emoji.FALSE}'

            markup.add(InlineKeyboardButton(text, callback_data=user_data.new(user_id, has_mark)))
    inline_save = InlineKeyboardButton("Сохранить", callback_data=credit_amount_data.new(value))
    markup.add(
        inline_save,
        cancel_inline_button,
    )
    return markup


def get_data_from_markup(markup: InlineKeyboardMarkup) -> Tuple[int, Set[int]]:
    users = set()
    value = None
    for _ in markup["inline_keyboard"]:
        for elem in _:
            if "save" in elem.callback_data:
                value = int(credit_amount_data.parse(elem.callback_data).get("value"))
            if "user" in elem.callback_data:
                data = user_data.parse(elem.callback_data)
                if data.get("has_mark") == "1":
                    users.add(int(data.get("id")))
    return value, users


def get_amount_from_markup(markup: InlineKeyboardMarkup) -> int:
    for _ in markup["inline_keyboard"]:
        for elem in _:
            if "save" in elem.callback_data:
                return int(credit_amount_data.parse(elem.callback_data).get("value"))


def get_user_id(data: str) -> int:
    return int(user_data.parse(data).get("id"))
