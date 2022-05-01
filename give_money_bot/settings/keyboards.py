from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from give_money_bot.settings.strings import Strings

settings_markup = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text=Strings.menu_add_new_user)],
        [KeyboardButton(text=Strings.menu_edit_friendly_name)],
        [KeyboardButton(text=Strings.menu_edit_visible_users)],
        [KeyboardButton(text=Strings.menu_exit)],
    ],
)
