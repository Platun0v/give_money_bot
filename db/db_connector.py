import typing
from typing import Dict, List, Optional, Set
import datetime

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from .models import Base, Credit


class DB:
    def __init__(self, db_path: str = "db.sqlite"):
        self.engine = sqlalchemy.create_engine(f'sqlite:///{db_path}', echo=False,
                                               connect_args={'check_same_thread': False})
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_entry(self, to_user: int, from_users: List[int], amount: int, additional_info: str = ""):
        for from_user in from_users:
            self.session.add(Credit(to_id=to_user, from_id=from_user, amount=amount, text_info=additional_info))
        self.session.commit()

    def user_credits(self, user: int) -> List[Credit]:
        return self.session.query(Credit).filter(Credit.from_id == user).filter(Credit.returned == False).all()

    def credits_to_user(self, user: int) -> List[Credit]:
        return self.session.query(Credit).filter(Credit.to_id == user).filter(Credit.returned == False).all()

    def return_credit(self, credit_ids: typing.Union[List[int], int]):
        if isinstance(credit_ids, int):
            credit_ids = [credit_ids]

        for credit_id in credit_ids:
            credit: Credit = self.session.query(Credit).filter(Credit.id == credit_id).first()
            credit.returned = True
            credit.return_date = datetime.datetime.utcnow()
        self.session.commit()

    def reject_return_credit(self, credit_ids: typing.Union[List[int], int]):
        if isinstance(credit_ids, int):
            credit_ids = [credit_ids]

        for credit_id in credit_ids:
            credit: Credit = self.session.query(Credit).filter(Credit.id == credit_id).first()
            credit.returned = False
            credit.return_date = None
        self.session.commit()

    def get_credit(self, credit_id: int) -> Credit:
        return self.session.query(Credit).filter(Credit.id == credit_id).first()