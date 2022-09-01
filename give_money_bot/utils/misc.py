from typing import Any, Awaitable, Callable, Dict, Optional, Type, TypeVar, Union

from aiogram import BaseMiddleware
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message
from aiogram.types.base import TelegramObject
from loguru import logger as log
from pydantic import BaseModel
from sqlalchemy.orm import Session, sessionmaker

from give_money_bot.db import db_connector as db
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
            data["user"] = db.get_user(data["session"], event.from_user.id)
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


class CheckUser(BaseFilter):
    async def __call__(self, message: Message, session: Session) -> Union[bool, Dict[str, Any]]:
        return message.from_user.id in db.get_user_ids(session)


class CheckAdmin(BaseFilter):
    async def __call__(self, message: Message, session: Session) -> Union[bool, Dict[str, Any]]:
        return db.get_user(session, message.from_user.id).admin


T = TypeVar("T", bound=BaseModel)


async def get_state_data(ctx: FSMContext, state: State, model: Type[T]) -> Optional[T]:
    if state.state is None:  # Always true
        raise RuntimeError("State is not found")

    state_data = await ctx.get_data()
    data = state_data.get(state.state)
    if data is None:
        log.debug(f"State {state.state} is not found")
        return None

    return model.parse_raw(data)


async def update_state_data(ctx: FSMContext, state: State, data: Optional[T] = None) -> None:
    if state.state is None:
        raise RuntimeError("State is not found")
    if data is None:
        await ctx.set_data({state.state: None})
    else:
        await ctx.update_data({state.state: data.json()})
