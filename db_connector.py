import json
import time
import os
from typing import Dict, List, Optional

import config

blocker: bool = False


class Credit:
    def __init__(self, amount: int, date: str, text_info: str, returned: bool, return_date: str):
        wait_blocker()
        block_file()

        self.amount: int = amount
        self.date: str = date
        self.text_info: str = text_info
        self.returned: bool = returned
        self.return_date: str = return_date

    @classmethod
    def from_json(cls, _json) -> "Credit":
        return Credit(_json["amount"], _json["date"], _json["text_info"], _json["returned"], _json["return_date"])

    def to_json(self):
        return {"amount": self.amount, "date": self.date, "text_info": self.text_info, "returned": self.returned, "return_date": self.return_date}


class DB:
    def __init__(self, path: str):
        self.path: str = path
        self.db: Optional[Dict[int, Dict[int, List[Credit]]]] = None

    def read_file(self):
        db_object = self.check_file()

        for user in db_object.keys():
            for inner_user in db_object[user].keys():
                for i in range(len(db_object[user][inner_user])):
                    db_object[user][inner_user][i] = Credit.from_json(db_object[user][inner_user][i])

        self.db = db_object

    def check_file(self) -> Dict[int, Dict[int, List]]:
        if not os.path.exists(self.path):
            write_json(self.create_db_object_frame(), self.path)

        db_object: Dict[int, Dict[int, List]] = read_json(self.path)

        # TODO: Processing new users
        # db_keys = set(db_object.keys())
        # users = set(config.USERS.keys())
        # if db_keys != users:
        #     new_users = users - db_keys

        return db_object

    @staticmethod  # Изначально есть дикт диктов с пустым массивом
    def create_db_object_frame() -> Dict[int, Dict[int, List]]:
        ids = set(config.USERS.keys())
        db_object = {}
        for user in ids:
            db_object[user] = {}
            for inner_user in ids - user:
                db_object[user][inner_user] = []

        return db_object


def read_json(path):
    with open(path, "r") as f:
        return json.load(f)


def write_json(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f)


def block_file():
    global blocker
    blocker = True


def unblock_file():
    global blocker
    blocker = False


def wait_blocker():
    global blocker
    while blocker:
        time.sleep(0.05)


def block(fun):
    def wrapped(*args, **kwargs):
        wait_blocker()
        block_file()
        result = fun(*args, **kwargs)
        unblock_file()
        return result
    return wrapped