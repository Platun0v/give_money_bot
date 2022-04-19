from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from give_money_bot.settings.strings import Strings

settings_markup = (
    ReplyKeyboardMarkup(resize_keyboard=True)
    .row(KeyboardButton(Strings.menu_add_new_user))
    .row(KeyboardButton(Strings.menu_edit_friendly_name))
    .row(KeyboardButton(Strings.menu_edit_visible_users))
    .row(KeyboardButton(Strings.menu_exit))
)
