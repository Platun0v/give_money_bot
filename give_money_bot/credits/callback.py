from enum import Enum
from typing import Any

from aiogram.filters.callback_data import CallbackData


class AddCreditAction(str, Enum):
    save = "save"
    cancel = "cncl"
    show_more = "shwm"
    choose_user = "chse"
    reverse = "rvrs"


class AddCreditCallback(CallbackData, prefix="addcrd"):
    action: AddCreditAction

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(prefix=cls.__prefix__, **kwargs)


class ChooseUserAddCreditCallback(AddCreditCallback):
    action = AddCreditAction.choose_user
    user_id: int = 0


class RemoveCreditAction(str, Enum):
    cancel = "cncl"


class RemoveCreditCallback(CallbackData, prefix="rmcrd"):
    action: RemoveCreditAction


class ReturnCreditsAction(str, Enum):
    save = "save"
    cancel = "cncl"
    choose_user = "chse"


class ReturnCreditsCallback(CallbackData, prefix="retcrd"):
    action: ReturnCreditsAction

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(prefix=cls.__prefix__, **kwargs)


class ChooseUserReturnCreditsCallback(ReturnCreditsCallback):
    action = ReturnCreditsAction.choose_user
    user_id: int = 0
