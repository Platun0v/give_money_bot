from enum import Enum

from aiogram.filters.callback_data import CallbackData


class AddCreditAction(str, Enum):
    save = "save"
    cancel = "cncl"
    show_more = "shwm"
    choose_user = "chse"


class AddCreditCallback(CallbackData, prefix="addcrd"):
    action: AddCreditAction
    user_id: int = 0


class ReturnCreditsAction(str, Enum):
    save = "save"
    cancel = "cncl"
    choose_user = "chse"


class ReturnCreditsCallback(CallbackData, prefix="retcrd"):
    action: ReturnCreditsAction
    user_id: int = 0
