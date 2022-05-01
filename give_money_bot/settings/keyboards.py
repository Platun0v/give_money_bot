from enum import Enum

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.callback_data import CallbackData

from give_money_bot.settings.states import EditVisibilityData, PAGE_MAX_USERS
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


class Action(str, Enum):
    user = "user"
    left = "left"
    right = "right"
    cancel = "cancel"
    save = "save"


class EditVisibilityCallback(CallbackData, prefix="editvis"):
    action: Action
    user_id: int = 0


def create_edit_visibility_keyboard(data: EditVisibilityData) -> InlineKeyboardMarkup:
    markup = []

    page_start = (data.page - 1) * PAGE_MAX_USERS
    page_end = data.page * PAGE_MAX_USERS
    for user in data.users_list[page_start:page_end]:
        markup.append([
            InlineKeyboardButton(
                text=f"{data.users[user].username} {Strings.vision_emojis[data.users[user].vision]}",
                callback_data=EditVisibilityCallback(action=Action.user, user_id=user).pack()
            )
        ])
    markup.append([
        InlineKeyboardButton(text=Strings.left_emoji, callback_data=EditVisibilityCallback(action=Action.left).pack()),
        InlineKeyboardButton(text=Strings.save, callback_data=EditVisibilityCallback(action=Action.save).pack()),
        InlineKeyboardButton(text=Strings.right_emoji, callback_data=EditVisibilityCallback(action=Action.right).pack()),
    ])
    markup.append([
        InlineKeyboardButton(text=Strings.cancel, callback_data=EditVisibilityCallback(action=Action.cancel).pack())
    ])

    return InlineKeyboardMarkup(inline_keyboard=markup)
