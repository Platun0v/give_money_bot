from subprocess import PIPE, Popen
from typing import List, Optional, Tuple

from aiogram import types

from give_money_bot.db.db_connector import db
from give_money_bot.db.models import Credit


def get_info(message: types.Message) -> str:
    msg: List[str] = message.text.split("\n")
    return "" if len(msg) == 1 else msg[1]


def get_credits_amount(from_user: int, to_user: int) -> Tuple[int, List[Credit]]:
    user_credits = db.get_credits_to_user_from_user(from_user=from_user, to_user=to_user)
    res_sum = 0
    for credit in user_credits:
        res_sum += credit.get_amount()
    return res_sum, user_credits


def parse_expression(value: str) -> Tuple[Optional[int], Optional[str]]:
    p = Popen("./parser", stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate(bytes(value, "utf-8"))
    if err:
        return None, err.decode("utf-8").split("\n")[0]
    return int(out), None


def parse_info_from_message(message: str) -> Tuple[str, str]:
    """
    Divide expression and info

    :param message: str - message from user
    :return: Tuple[str, str] - expression and info
    """
    digits = "0123456789()+-*/ "

    for i, char in enumerate(message):
        if char not in digits:
            return message[:i], message[i:]
    return message, ""
