from give_money_bot.tg_bot.utils import CallbackData


class CreditsCallbackData(CallbackData):
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
