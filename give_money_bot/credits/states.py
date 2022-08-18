from typing import Set

from pydantic import BaseModel


class AddCreditData(BaseModel):
    amount: int
    message: str
    show_more: bool
    users: Set[int]
    message_id: int


class ReturnCreditsData(BaseModel):
    users: Set[int]
    message_id: int
