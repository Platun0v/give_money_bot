from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, \
    InlineKeyboardButton, InlineKeyboardMarkup
from config import USERS
from aiogram.utils.callback_data import CallbackData

save_data = CallbackData("save", "value", "users")

button_plus = KeyboardButton("+")
button_info = KeyboardButton("info")

markup_main = ReplyKeyboardMarkup(resize_keyboard=True).row(button_plus, button_info)

inline_save = InlineKeyboardButton("Сохранить", callback_data=save_data.new(0, []))
inline_cancel = InlineKeyboardButton("Отмена", callback_data="cancel")


def get_inline_markup(for_user_id):
    markup = InlineKeyboardMarkup()
    for id in USERS.keys():
        if id != for_user_id:
            markup.add(InlineKeyboardButton(USERS[id], callback_data=f"{id}"))
    markup.add(inline_save)
    markup.add(inline_cancel)
    return markup

