from enum import Enum
from typing import Any

from aiogram.filters.callback_data import CallbackData


class EditVisibilityAction(str, Enum):
    user = "user"
    left = "left"
    right = "right"
    cancel = "cancel"
    save = "save"


class EditVisibilityCallback(CallbackData, prefix="editvis"):
    action: EditVisibilityAction

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(prefix=cls.__prefix__, **kwargs)


class UserEditVisibilityCallback(EditVisibilityCallback):
    action = EditVisibilityAction.user
    user_id: int = 0
