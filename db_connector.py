import json
import time
from typing import Dict, List, Optional

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


class DB:
    def __init__(self, path: str):
        self.path: str = path
        self.db: Optional[Dict[Dict[List[Credit]]]] = None

    def read_file(self):
        with open(self.path, 'r') as f:
            json.load(f)


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
