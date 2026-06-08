from typing import List, Tuple

import sympy
from aiogram import types
from sqlalchemy.orm import Session

from give_money_bot.db import crud as db
from give_money_bot.db.models import Credit


def get_info(message: types.Message) -> str:
    msg: List[str] = message.text.split("\n")
    return "" if len(msg) == 1 else msg[1]


def get_credits_amount(from_user: int, to_user: int, session: Session) -> Tuple[int, List[Credit]]:
    user_credits = db.get_credits_to_user_from_user(session, from_user=from_user, to_user=to_user)
    res_sum = 0
    for credit in user_credits:
        res_sum += credit.get_amount()
    return res_sum, user_credits


def parse_expression(value: str) -> Tuple[int, None] | Tuple[int, str]:
    # Parse using sympy
    try:
        return int(sympy.sympify(value)), None
    except Exception as e:
        return 0, str(e)


def parse_info_from_message(message: str) -> Tuple[str, str]:
    """
    Divide expression and info

    :param message: Message from user
    :return: Expression and info
    """
    digits = "0123456789()+-*/ .%"

    for i, char in enumerate(message):
        if char not in digits:
            return message[:i], message[i:]
    return message, ""
