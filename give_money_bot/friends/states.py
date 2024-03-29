from typing import Dict, List

from aiogram.fsm.state import State, StatesGroup
from pydantic import BaseModel

from give_money_bot.db.models import ShowTypes


class FriendsMenuStates(StatesGroup):
    friends_menu = State()
    new_user = State()


# class EditVisibilityUser(BaseModel):
#     username: str
#     vision: ShowTypes
#
#
# PAGE_MAX_USERS = 6
#
#
# class EditVisibilityData(BaseModel):
#     users: Dict[int, EditVisibilityUser]
#     users_list: List[int]
#     page: int
#     pages_total: int
