from typing import Set

from aiogram.fsm.state import State, StatesGroup
from pydantic import BaseModel


class CreditStates(StatesGroup):
    add_credit = State()
    return_credit = State()


class AddCreditData(BaseModel):
    amount: int
    message: str
    show_more: bool
    users: Set[int]
    message_id: int


class ReturnCreditsData(BaseModel):
    users: Set[int]
    message_id: int
