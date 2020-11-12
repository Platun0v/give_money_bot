from typing import Set, Tuple

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, \
    InlineKeyboardButton, InlineKeyboardMarkup
from config import USERS
from config import Emoji
from aiogram.utils.callback_data import CallbackData

credit_amount_data = CallbackData("save", "value")
user_data = CallbackData("user", "id", "has_mark")
credit_data = CallbackData("credit_chose", "index", "has_mark")
check_data = CallbackData("check", "credit_id", "value")

button_plus = KeyboardButton("+")
button_info = KeyboardButton("info")

markup_main = ReplyKeyboardMarkup(resize_keyboard=True).row(button_plus, button_info)

cancel_inline_button = InlineKeyboardButton("Отмена", callback_data="cancel")

inline_credits_to_user = InlineKeyboardButton("Кто мне должен?", callback_data="credits_to_user")
inline_user_credits = InlineKeyboardButton("Кому я должен?", callback_data="user_credits")
inline_return_credit = InlineKeyboardButton("Вернуть выбранные долги", callback_data="return_credit")
incline_credit_cancel = InlineKeyboardButton("Я ничего еще не вернул", callback_data="credit_cancel")

markup_credits = InlineKeyboardMarkup()
markup_credits.add(inline_credits_to_user)
markup_credits.add(inline_user_credits)


# Done
def get_check_markup(credit_id: int, value: bool) -> InlineKeyboardMarkup:
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


def get_data_from_check(markup: InlineKeyboardMarkup):
    data = markup["inline_keyboard"][2][0].callback_data
    parsed_data = check_data.parse(data)
    return parsed_data.get("credit_id"), parsed_data.get("value")


def get_credits_markup(value: int, marked_credits: set):
    markup = InlineKeyboardMarkup()
    for i in range(0, value):
        text = f"{i + 1}"
        has_mark = 0
        if i in marked_credits:
            has_mark = 1
            text += Emoji.TRUE
        else:
            text += Emoji.FALSE
        markup.add(InlineKeyboardButton(text, callback_data=credit_data.new(i, has_mark)))
    markup.add(inline_return_credit)
    markup.add(incline_credit_cancel)
    return markup


def get_marked_credits(markup: InlineKeyboardMarkup):
    marked_credits = set()
    for i in markup["inline_keyboard"]:
        if "credit_chose" in i[0].callback_data:
            data = credit_data.parse(i[0].callback_data)
            if data.get("has_mark") == "1":
                marked_credits.add(int(data.get("index")))
    return marked_credits


def get_credit_index(data: str):
    return int(credit_data.parse(data).get("index"))


# Done
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


# Done
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


# Done
def get_amount_from_markup(markup: InlineKeyboardMarkup) -> int:
    for _ in markup["inline_keyboard"]:
        for elem in _:
            if "save" in elem.callback_data:
                return int(credit_amount_data.parse(elem.callback_data).get("value"))


# Done
def get_user_id(data: str) -> int:
    return int(user_data.parse(data).get("id"))
