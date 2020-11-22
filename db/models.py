import datetime
from typing import Optional

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

import config


Base = declarative_base()


class Credit(Base):
    __tablename__ = 'credits'

    id: int = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    to_id: int = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # Кому должны
    from_id: int = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # Кто должен
    amount: int = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    discount: Optional[int] = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    date: datetime.datetime = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.datetime.utcnow)
    text_info: str = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='')
    returned: bool = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
    return_date: Optional[datetime.datetime] = sqlalchemy.Column(sqlalchemy.DateTime)

    def get_date_str(self):
        return f"{self.date.day}.{self.date.month}.{self.date.year}"

    def get_return_date_str(self):
        return f"{self.return_date.day}.{self.return_date.month}.{self.return_date.year}"

    def get_text_info_new_line(self):
        if self.text_info:
            return f'{self.text_info}\n'
        return ''

    def get_amount(self) -> int:
        return self.amount - (0 if self.discount is None else self.discount)

    def __repr__(self):
        return f"<Credit('{config.USERS[self.from_id]}' -> '{config.USERS[self.to_id]}', amount='{self.amount}')>"
