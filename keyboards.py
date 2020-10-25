from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, \
    InlineKeyboardButton, InlineKeyboardMarkup
from config import USERS
from aiogram.utils.callback_data import CallbackData

save_data = CallbackData("save", "value")
user_data = CallbackData("user", "id", "has_mark")

button_plus = KeyboardButton("+")
button_info = KeyboardButton("info")

markup_main = ReplyKeyboardMarkup(resize_keyboard=True).row(button_plus, button_info)

inline_save = InlineKeyboardButton("Сохранить", callback_data=save_data.new(0))
inline_cancel = InlineKeyboardButton("Отмена", callback_data="cancel")


def get_inline_markup(for_user_id, value, users: set):
    markup = InlineKeyboardMarkup()
    for id in USERS.keys():
        if id != for_user_id:
            text = USERS[id]
            has_mark = 0
            if str(id) in users:
                text += "+"
                has_mark = 1
            print(text)
            markup.add(InlineKeyboardButton(text, callback_data=user_data.new(id, has_mark)))
    inline_save.callback_data = save_data.new(value)
    markup.add(inline_save)
    markup.add(inline_cancel)
    return markup

