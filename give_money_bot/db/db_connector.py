import datetime
import typing
from typing import List, Optional, Iterable

import sqlalchemy
from sqlalchemy.orm import sessionmaker

from give_money_bot.db.models import Base, Credit, User
from give_money_bot import config


class DB:
    def __init__(self, db_path: str = "db.sqlite"):
        self.engine = sqlalchemy.create_engine(
            f"sqlite:///{db_path}",
            echo=False,
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_entry(
        self,
        to_user: int,
        from_users: List[int],
        amount: int,
        additional_info: str = "",
    ) -> None:
        for from_user in from_users:
            self.session.add(
                Credit(
                    to_id=to_user,
                    from_id=from_user,
                    amount=amount,
                    text_info=additional_info,
                    discount=0,
                )
            )
        self.session.commit()

    def add_entry_2(
        self,
        to_users: List[int],
        from_user: int,
        amount: int,
        additional_info: str = "",
    ) -> None:
        for to_user in to_users:
            self.session.add(
                Credit(
                    to_id=to_user,
                    from_id=from_user,
                    amount=amount,
                    text_info=additional_info,
                    discount=0,
                )
            )
        self.session.commit()

    def get_user_credits(self, user: int) -> List[Credit]:
        return (
            self.session.query(Credit)
            .filter(Credit.from_id == user)
            .filter(Credit.returned == False)
            .order_by(Credit.to_id)
            .order_by(Credit.date)
            .all()
        )

    def credits_to_user(self, user: int) -> List[Credit]:
        return (
            self.session.query(Credit)
            .filter(Credit.to_id == user)
            .filter(Credit.returned == False)
            .order_by(Credit.from_id)
            .order_by(Credit.date)
            .all()
        )

    def get_credits_to_user_from_user(
        self, from_user: int, to_user: int
    ) -> List[Credit]:
        return (
            self.session.query(Credit)
            .filter(Credit.to_id == to_user)
            .filter(Credit.from_id == from_user)
            .filter(Credit.returned == False)
            .all()
        )

    def return_credits(self, credit_ids: typing.Union[List[int], int, Credit]) -> None:
        if isinstance(credit_ids, int):
            credit_ids = [credit_ids]
        if isinstance(credit_ids, Credit):
            credit_ids = [credit_ids.id]

        for credit_id in credit_ids:
            credit: Credit = (
                self.session.query(Credit).filter(Credit.id == credit_id).first()
            )
            credit.returned = True
            credit.return_date = datetime.datetime.utcnow()
        self.session.commit()

    def reject_return_credit(self, credit_ids: typing.Union[List[int], int]) -> None:
        if isinstance(credit_ids, int):
            credit_ids = [credit_ids]

        for credit_id in credit_ids:
            credit: Credit = (
                self.session.query(Credit).filter(Credit.id == credit_id).first()
            )
            credit.returned = False
            credit.return_date = None
        self.session.commit()

    def get_credit(self, credit_id: int) -> Credit:
        return self.session.query(Credit).filter(Credit.id == credit_id).first()

    def get_credits(self) -> List[Credit]:
        return self.session.query(Credit).filter(Credit.returned == False).all()

    def add_discount(self, credit: typing.Union[int, Credit], discount: int) -> None:
        if isinstance(credit, int):
            credit = self.get_credit(credit)
        if credit.discount is None:
            credit.discount = 0
        credit.discount += discount
        self.session.commit()

    def get_user(self, user_id: int) -> User:
        return self.session.query(User).filter(User.user_id == user_id).first()

    def get_users(self, user_ids: Optional[Iterable[int]] = None) -> List[User]:
        if user_ids is None:
            return self.session.query(User).all()
        return self.session.query(User).filter(User.user_id.in_(user_ids)).all()

    def get_user_ids(self) -> List[int]:
        return [e.user_id for e in self.get_users()]

    def get_admin(self) -> User:
        return self.session.query(User).filter(User.admin == True).first()


db = DB(db_path=config.DB_PATH + "db.sqlite")
