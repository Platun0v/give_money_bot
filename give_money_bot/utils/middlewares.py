from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from aiogram.types.base import TelegramObject
from sqlalchemy.orm import Session, sessionmaker

from give_money_bot.db import crud as db
from give_money_bot.db.models import User


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: sessionmaker):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        with self.session_pool() as session:
            data["session"] = session
            return await handler(event, data)


class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, (Message, CallbackQuery)):
            if db.check_user_exists(data["session"], event.from_user.id):
                data["user"] = db.get_user(data["session"], event.from_user.id)
            else:
                return None
        return await handler(event, data)


class SubstituteUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, (Message, CallbackQuery)):
            session: Session = data["session"]
            user: User = data["user"]
            if user.substituted_user_id is not None:
                data["user"] = db.get_user(session, user.substituted_user_id)

        return await handler(event, data)
