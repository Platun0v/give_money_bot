import datetime
from enum import IntEnum

import sqlalchemy
from sqlalchemy.orm import relationship

from give_money_bot.db.base import Base


class Credit(Base):
    __tablename__ = "credits"

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True,
        index=True,
    )
    to_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("users.user_id", name="fk_creditor_id"),
        nullable=False,
        index=True,
    )  # Кому должны
    creditor = relationship(
        "User",
        foreign_keys="Credit.to_id",
    )
    from_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("users.user_id", name="fk_debtor_id"),
        nullable=False,
        index=True,
    )  # Кто должен
    debtor = relationship("User", foreign_keys="Credit.from_id")

    amount = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    discount = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.datetime.utcnow)
    text_info = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="")
    returned = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False, index=True)
    return_date = sqlalchemy.Column(sqlalchemy.DateTime)

    # def get_date_str(self) -> str:
    #     return f"{self.date.day}.{self.date.month}.{self.date.year}"
    #
    # def get_return_date_str(self) -> str:
    #     if self.return_date:
    #         return f"{self.return_date.day}.{self.return_date.month}.{self.return_date.year}"
    #     return ""
    #
    # def get_text_info_new_line(self) -> str:
    #     if self.text_info:
    #         return f"{self.text_info}\n"
    #     return ""

    def get_amount(self) -> int:
        return self.amount - (0 if self.discount is None else self.discount)

    def __repr__(self) -> str:
        return (
            f"<Credit('{self.debtor.name}' -> '{self.creditor.name}', "
            f"amount='{self.amount}', discount='{self.discount}')>"
        )


class User(Base):
    __tablename__ = "users"
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, unique=True, primary_key=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    admin = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)

    substituted_user_id = sqlalchemy.Column(sqlalchemy.Integer, default=None)

    phone_number = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="")
    note = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="")
    tg_alias = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="", index=True)
    tg_name = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="")

    def __repr__(self) -> str:
        return f"<User(id='{self.user_id}', name='{self.name}', admin='{self.admin}')>"


class UserVision(Base):
    __tablename__ = "user_vision"
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("users.user_id"), primary_key=True, nullable=False, index=True
    )
    user = relationship("User", foreign_keys="UserVision.user_id")

    show_user_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("users.user_id"), primary_key=True, nullable=False, index=True
    )
    show_user = relationship("User", foreign_keys="UserVision.show_user_id")

    show_type = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=2, index=True)

    user_pair_idx = sqlalchemy.Index("user_pair_idx", user_id, show_user_id, unique=True)

    def __repr__(self) -> str:
        return f"<UserVision(user='{self.user}', show_user='{self.show_user}', show_type='{self.show_type}')>"


class ShowTypes(IntEnum):
    ALWAYS = 0
    ADDITIONAL = 1
    NEVER = 2
