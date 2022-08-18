from typing import Any, Awaitable, Callable, Dict, Union, cast

from aiogram import BaseMiddleware
from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import CallbackQuery, Message
from aiogram.types.base import TelegramObject
from sqlalchemy.orm import Session, sessionmaker

from give_money_bot.db import db_connector as db


class UserMiddlewareMessage(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        event = cast(Message, event)
        data["user"] = db.get_user(data["session"], event.from_user.id)
        return await handler(event, data)


class UserMiddlewareCallbackQuery(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        event = cast(CallbackQuery, event)
        data["user"] = db.get_user(data["session"], event.from_user.id)
        return await handler(event, data)


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


class CheckUser(BaseFilter):
    async def __call__(self, message: Message, session: Session) -> Union[bool, Dict[str, Any]]:
        return message.from_user.id in db.get_user_ids(session)


class CheckAdmin(BaseFilter):
    async def __call__(self, message: Message, session: Session) -> Union[bool, Dict[str, Any]]:
        return db.get_user(session, message.from_user.id).admin
