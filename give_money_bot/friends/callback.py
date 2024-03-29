from enum import Enum
from typing import Any

from aiogram.filters.callback_data import CallbackData


class RequestAddNewUserAction(str, Enum):
    cancel = "cancel"
    save = "save"


class RequestAddNewUserCallback(CallbackData, prefix="reqanu"):
    action: RequestAddNewUserAction
    user_id: int = 0
