from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from give_money_bot.db.models import User
from give_money_bot.friends.callback import RequestAddNewUserCallback, RequestAddNewUserAction
from give_money_bot.friends.strings import Strings

friends_menu_markup = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text=Strings.menu_add_new_user)],
        [KeyboardButton(text=Strings.menu_exit)],
    ],
)

cancel_markup = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text=Strings.cancel)],
    ]
)


def admin_new_user_request_markup(new_user: User) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=Strings.save,
                    callback_data=RequestAddNewUserCallback(
                        action=RequestAddNewUserAction.save,
                        user_id=new_user.user_id,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text=Strings.cancel,
                    callback_data=RequestAddNewUserCallback(
                        action=RequestAddNewUserAction.cancel,
                        user_id=new_user.user_id,
                    ).pack(),
                ),
            ],
        ],
    )
