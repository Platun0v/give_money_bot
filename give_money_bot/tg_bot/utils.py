import hashlib

from aiogram import types

from give_money_bot.db.db_connector import db


def check_user(message: types.Message) -> bool:
    return message.from_user.id in db.get_user_ids()


def check_admin(message: types.Message) -> bool:
    return db.get_user(message.from_user.id).admin


class CallbackData:
    def __init__(self) -> None:
        variables = self.__class__.__dict__.keys()
        for key in variables:
            if "__" not in key and isinstance(self.__getattribute__(key), str) and not self.__getattribute__(key):
                hash_value = hashlib.sha1(key.encode()).hexdigest()
                self.__setattr__(key, hash_value[:8])
