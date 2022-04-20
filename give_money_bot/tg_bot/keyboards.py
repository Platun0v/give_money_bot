from typing import Dict, Optional, Set, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from give_money_bot.tg_bot.strings import Strings

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(
    KeyboardButton(Strings.menu_credits),
    KeyboardButton(Strings.menu_debtors),
    KeyboardButton(Strings.menu_settings),
)
