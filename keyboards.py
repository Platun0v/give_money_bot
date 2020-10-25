from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, \
    InlineKeyboardButton, InlineKeyboardMarkup
from config import USERS
from aiogram.utils.callback_data import CallbackData

save_data = CallbackData("save", "value")
user_data = CallbackData("user", "id", "has_mark")
credit_data = CallbackData("credit_chose", "index", "has_mark")

button_plus = KeyboardButton("+")
button_info = KeyboardButton("info")

markup_main = ReplyKeyboardMarkup(resize_keyboard=True).row(button_plus, button_info)

inline_save = InlineKeyboardButton("Сохранить", callback_data=save_data.new(0))
inline_cancel = InlineKeyboardButton("Отмена", callback_data="cancel")

inline_credits_to_user = InlineKeyboardButton("Кто мне должен?", callback_data="credits_to_user")
inline_user_credits = InlineKeyboardButton("Кому я должен?", callback_data="user_credits")
inline_return_credit = InlineKeyboardButton("Вернуть выбранные долгы", callback_data="return_credit")

murkup_credits = InlineKeyboardMarkup()
murkup_credits.add(inline_credits_to_user)
murkup_credits.add(inline_user_credits)


def get_credits_markup(value: int, marked_credits: set):
    markup = InlineKeyboardMarkup()
    for i in range(0, value):
        text = f"{i + 1}"
        has_mark = 0
        if i in marked_credits:
            has_mark = 1
            text += "+"
        markup.add(InlineKeyboardButton(text, callback_data=credit_data.new(i, has_mark)))
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


def get_inline_markup(for_user_id: int, value: int, users: set):
    markup = InlineKeyboardMarkup()
    for id in USERS.keys():
        if id != for_user_id:
            text = USERS[id]
            has_mark = 0
            if id in users:
                text += "+"
                has_mark = 1
            markup.add(InlineKeyboardButton(text, callback_data=user_data.new(id, has_mark)))
    inline_save.callback_data = save_data.new(value)
    markup.add(inline_save)
    markup.add(inline_cancel)
    return markup


def get_data_from_markup(markup: InlineKeyboardMarkup):
    users = set()
    value = None
    for i in markup["inline_keyboard"]:
        if "save" in i[0].callback_data:
            value = int(save_data.parse(i[0].callback_data).get("value"))
        if "user" in i[0].callback_data:
            data = user_data.parse(i[0].callback_data)
            if data.get("has_mark") == "1":
                users.add(int(data.get("id")))
    return value, users


def get_value_from_markup(markup: InlineKeyboardMarkup):
    value = None
    for i in markup["inline_keyboard"]:
        if "save" in i[0].callback_data:
            value = int(save_data.parse(i[0].callback_data).get("value"))
    return value


def get_user_id(data: str):
    return int(user_data.parse(data).get("id"))
