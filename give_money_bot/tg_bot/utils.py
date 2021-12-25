from subprocess import Popen, PIPE
from typing import Optional, Tuple, List

from aiogram import types

from give_money_bot import config
from give_money_bot.db.db_connector import db
from give_money_bot.db.models import Credit
from give_money_bot.utils.strings import Strings


def check_user(message: types.Message) -> bool:
    return message.from_user.id in db.get_user_ids()


def check_admin(message: types.Message) -> bool:
    return db.get_user(message.from_user.id).admin


def get_info(message: types.Message) -> str:
    msg: List[str] = message.text.split("\n")
    return "" if len(msg) == 1 else msg[1]


def get_credits_amount(from_user: int, to_user: int) -> Tuple[int, List[Credit]]:
    user_credits = db.get_credits_to_user_from_user(
        from_user=from_user, to_user=to_user
    )
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
    for i, char in enumerate(message):
        if char not in Strings.DIGITS:
            return message[:i], message[i:]
    return message, ""
