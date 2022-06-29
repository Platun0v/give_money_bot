from enum import Enum

from aiogram.dispatcher.filters.callback_data import CallbackData


class EditVisibilityAction(str, Enum):
    user = "user"
    left = "left"
    right = "right"
    cancel = "cancel"
    save = "save"


class EditVisibilityCallback(CallbackData, prefix="editvis"):
    action: EditVisibilityAction
    user_id: int = 0
