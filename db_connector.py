import json
import time
import os
from typing import Dict, List, Optional, Set
import datetime

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import config

Base = declarative_base()


class Credit(Base):
    __tablename__ = 'credits'

    id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    to_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # Кому должны
    from_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # Кто должен
    amount = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.datetime.utcnow)
    text_info = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='')
    returned = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
    return_date = sqlalchemy.Column(sqlalchemy.DateTime)

    # def __repr__(self):
    #     return f"<ShortUrl(name='{self.name}', url='{self.url}')>"


class DB:
    def __init__(self, db_path: str = "db.sqlite"):
        self.engine = sqlalchemy.create_engine(f'sqlite:///{db_path}', echo=True)
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
