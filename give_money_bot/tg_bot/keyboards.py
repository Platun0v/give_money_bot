from typing import Dict, Optional, Set, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from give_money_bot.tg_bot.strings import Strings

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=Strings.menu_credits),
            KeyboardButton(text=Strings.menu_debtors),
            KeyboardButton(text=Strings.menu_settings),
        ]
    ],
    resize_keyboard=True,
)
