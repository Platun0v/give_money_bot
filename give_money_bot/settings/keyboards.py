from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from give_money_bot.settings.callback import EditVisibilityAction, EditVisibilityCallback
from give_money_bot.settings.states import PAGE_MAX_USERS, EditVisibilityData
from give_money_bot.settings.strings import Strings

settings_markup = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text=Strings.menu_add_new_user)],
        [KeyboardButton(text=Strings.menu_edit_friendly_name)],
        [KeyboardButton(text=Strings.menu_edit_number)],
        [KeyboardButton(text=Strings.menu_edit_visible_users)],
        [KeyboardButton(text=Strings.menu_exit)],
    ],
)


def create_edit_visibility_keyboard(data: EditVisibilityData) -> InlineKeyboardMarkup:
    markup = []

    page_start = (data.page - 1) * PAGE_MAX_USERS
    page_end = data.page * PAGE_MAX_USERS
    for user in data.users_list[page_start:page_end]:
        markup.append(
            [
                InlineKeyboardButton(
                    text=f"{data.users[user].username} {Strings.vision_emojis[data.users[user].vision]}",
                    callback_data=EditVisibilityCallback(action=EditVisibilityAction.user, user_id=user).pack(),
                )
            ]
        )
    markup.append(
        [
            InlineKeyboardButton(
                text=Strings.left_emoji, callback_data=EditVisibilityCallback(action=EditVisibilityAction.left).pack()
            ),
            InlineKeyboardButton(
                text=Strings.save, callback_data=EditVisibilityCallback(action=EditVisibilityAction.save).pack()
            ),
            InlineKeyboardButton(
                text=Strings.right_emoji, callback_data=EditVisibilityCallback(action=EditVisibilityAction.right).pack()
            ),
        ]
    )
    markup.append(
        [
            InlineKeyboardButton(
                text=Strings.cancel, callback_data=EditVisibilityCallback(action=EditVisibilityAction.cancel).pack()
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=markup)
