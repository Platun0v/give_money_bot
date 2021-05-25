import datetime
from typing import Optional

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

from give_money_bot import config

Base = declarative_base()


class Credit(Base):
    __tablename__ = 'credits'

    id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    to_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # Кому должны
    from_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # Кто должен
    amount = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    discount = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.datetime.utcnow)
    text_info = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='')
    returned = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
    return_date = sqlalchemy.Column(sqlalchemy.DateTime)

    def get_date_str(self):
        return f"{self.date.day}.{self.date.month}.{self.date.year}"

    def get_return_date_str(self) -> str:
        if self.return_date:
            return f"{self.return_date.day}.{self.return_date.month}.{self.return_date.year}"
        return ""

    def get_text_info_new_line(self) -> str:
        if self.text_info:
            return f'{self.text_info}\n'
        return ''

    def get_amount(self) -> int:
        return self.amount - (0 if self.discount is None else self.discount)

    def __repr__(self):
        return f"<Credit('{config.USERS[self.from_id]}' -> '{config.USERS[self.to_id]}', " \
               f"amount='{self.amount}', discount='{self.discount}')>"
