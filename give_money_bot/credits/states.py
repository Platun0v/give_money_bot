from typing import Dict, List, Set

from aiogram.dispatcher.fsm.state import State, StatesGroup
from pydantic import BaseModel, Field, root_validator, validator

from give_money_bot.db.models import ShowTypes


class AddCreditData(BaseModel):
    amount: int
    message: str
    show_more: bool
    users: Set[int]
    message_id: int


class ReturnCreditsData(BaseModel):
    users: Set[int]
    message_id: int
