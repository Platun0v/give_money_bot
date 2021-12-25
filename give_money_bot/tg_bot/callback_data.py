import hashlib


class CallbackStrings:
    save_credit = ""
    cancel_crt_credit = ""
    choose_user_for_credit = ""

    choose_credit_for_return = ""
    return_credits = ""
    cancel_return_credits = ""

    check_return_of_credit = ""
    check_return_reject = ""
    check_return_approve = ""

    def __init__(self) -> None:
        variables = self.__class__.__dict__.keys()
        for key in variables:
            if (
                "__" not in key
                and isinstance(self.__getattribute__(key), str)
                and not self.__getattribute__(key)
            ):
                hash_value = hashlib.sha1(key.encode()).hexdigest()
                self.__setattr__(key, hash_value[:8])


CALLBACK = CallbackStrings()
