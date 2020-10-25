import json
import time
import os
from typing import Dict, List, Optional, Set
import datetime

import config

blocker: bool = False


def read_json(path) -> Dict[str, Dict[str, List]]:
    with open(path, "r") as f:
        return json.load(f)


def read_json_int_keys(path) -> Dict[int, Dict[int, List]]:
    obj = read_json(path)
    new_obj = {}
    for key1 in obj.keys():
        new_obj[int(key1)] = {}
        for key2 in obj[key1].keys():
            new_obj[int(key1)][int(key2)] = obj[key1][key2]
    return new_obj


def write_json(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f)


def date_to_string(date: datetime.date) -> Optional[str]:
    if date is None:
        return None
    return f'{date.day}:{date.month}:{date.year}'


def date_from_string(date: str) -> datetime.date:
    date = date.split(':')
    return datetime.date(year=int(date[2]), month=int(date[1]), day=int(date[0]))


class Credit:
    def __init__(self, amount: int, date: str = None, text_info: str = "", returned: bool = False,
                 return_date: str = None):
        self.amount: int = amount

        if date is None:  # Date format: dd.mm.yyyy
            self.date: datetime.date = datetime.date.today()
        else:
            self.date: datetime.date = date_from_string(date)

        self.text_info: str = text_info
        self.returned: bool = returned

        if return_date is None:  # Date format: dd.mm.yyyy
            self.return_date: Optional[datetime.date] = None
        else:
            self.return_date: datetime.date = date_from_string(return_date)

    @classmethod
    def from_json(cls, _json) -> "Credit":
        return Credit(_json["amount"], _json["date"], _json["text_info"], _json["returned"], _json["return_date"])

    def to_json(self):
        return {"amount": self.amount, "date": date_to_string(self.date), "text_info": self.text_info,
                "returned": self.returned, "return_date": date_to_string(self.return_date)}


class DB:
    def __init__(self, path: str = "db.json"):
        self.path: str = path

    def read_db(self) -> Dict[int, Dict[int, List[Credit]]]:
        db_object = self.check_file()

        for user in db_object.keys():
            for inner_user in db_object[user].keys():
                for i in range(len(db_object[user][inner_user])):
                    db_object[user][inner_user][i] = Credit.from_json(db_object[user][inner_user][i])

        return db_object

    def write_db(self, db: Dict[int, Dict[int, List[Credit]]]):
        db_object = {}
        for user in db.keys():
            db_object[user] = {}
            for inner_user in db[user].keys():
                db_object[user][inner_user] = []
                for i in range(len(db[user][inner_user])):
                    db_object[user][inner_user].append(db[user][inner_user][i].to_json())

        write_json(db_object, self.path)

    def check_file(self) -> Dict[int, Dict[int, List]]:
        if not os.path.exists(self.path):
            write_json(self.create_db_object_frame(), self.path)

        db_object: Dict[int, Dict[int, List]] = read_json_int_keys(self.path)

        # TODO: Processing new users
        # db_keys = set(db_object.keys())
        # users = set(config.USERS.keys())
        # if db_keys != users:
        #     new_users = users - db_keys

        return db_object

    def add_entry(self, to_user: int, from_users: List[int], entry: Credit):
        db = self.read_db()
        for user in from_users:
            db[to_user][user].append(entry)
        self.write_db(db)

    @staticmethod  # Изначально есть дикт диктов с пустым массивом
    def create_db_object_frame() -> Dict[int, Dict[int, List]]:
        ids: Set[int] = set(config.USERS.keys())
        db_object = {}
        for user in ids:
            db_object[user] = {}
            for inner_user in ids - {user}:
                db_object[user][inner_user] = []

        return db_object
