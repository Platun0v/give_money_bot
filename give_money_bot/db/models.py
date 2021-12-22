import datetime

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from give_money_bot import config

Base = declarative_base()


class Credit(Base):
    __tablename__ = "credits"

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True,
    )
    to_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.user_id", name='fk_creditor_id'), nullable=False)  # Кому должны
    creditor = relationship("User", foreign_keys="Credit.to_id")
    from_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.user_id", name='fk_debtor_id'), nullable=False)  # Кто должен
    debtor = relationship("User", foreign_keys="Credit.from_id")
    amount = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    discount = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    date = sqlalchemy.Column(
        sqlalchemy.DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    text_info = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="")
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
            return f"{self.text_info}\n"
        return ""

    def get_amount(self) -> int:
        return self.amount - (0 if self.discount is None else self.discount)

    def __repr__(self):
        return (
            f"<Credit('{self.debtor.name}' -> '{self.creditor.name}', "
            f"amount='{self.amount}', discount='{self.discount}')>"
        )


class User(Base):
    __tablename__ = "users"
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        unique=True,
        primary_key=True
    )
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    admin = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
    # credits = relationship('Credit', primaryjoin="or_(users.user_id==credits.creditor_id, users.user_id==credits.debtor_id)", lazy='dynamic')

    def __repr__(self):
        return (
            f"<User(id='{self.user_id}', name='{self.name}', admin='{self.admin}')>"
        )
