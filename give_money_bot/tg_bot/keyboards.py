from typing import Dict, Optional, Set, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from give_money_bot.config import Emoji

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(
    KeyboardButton("-"),
    KeyboardButton("info"),
    KeyboardButton(Emoji.SETTINGS),
)
