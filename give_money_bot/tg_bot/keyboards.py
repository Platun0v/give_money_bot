from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

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
