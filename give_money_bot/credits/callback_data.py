from aiogram.dispatcher.filters.callback_data import CallbackData

from give_money_bot.tg_bot.utils import CallbackData as MyCallbackData


class CreditsCallbackData(MyCallbackData):
    save_new_credit = ""
    cancel_create_credit = ""
    choose_users_for_credit = ""

    choose_credit_for_return = ""
    return_credits = ""
    cancel_return_credits = ""

    check_return_of_credit = ""
    check_return_reject = ""
    check_return_approve = ""

    def __init__(self) -> None:
        super(CreditsCallbackData, self).__init__()


CALLBACK = CreditsCallbackData()


class CreditAmountData(CallbackData, prefix=CALLBACK.save_new_credit):
    value: int


class UserChooseData(CallbackData, prefix=CALLBACK.choose_users_for_credit):
    user_id: int
    has_mark: int


class CreditChooseData(CallbackData, prefix=CALLBACK.choose_credit_for_return):
    index: int
    has_mark: int
