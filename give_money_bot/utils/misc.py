from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import (
    UNSET,
    ForceReply,
    InlineKeyboardMarkup,
    Message,
    MessageEntity,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from loguru import logger as log
from pydantic import BaseModel
from sqlalchemy.orm import Session

from give_money_bot.db import crud as db


class CheckUser(BaseFilter):
    async def __call__(self, message: Message, session: Session) -> Union[bool, Dict[str, Any]]:
        return message.from_user.id in db.get_user_ids(session)


class CheckAdmin(BaseFilter):
    async def __call__(self, message: Message, session: Session) -> Union[bool, Dict[str, Any]]:
        if not db.check_user_exists(session, message.from_user.id):
            return False
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
        await ctx.update_data({state.state: None})
    else:
        await ctx.update_data({state.state: data.json()})


async def send_message(
    bot: Bot,
    chat_id: Union[int, str],
    text: str,
    parse_mode: Optional[str] = UNSET,
    entities: Optional[List[MessageEntity]] = None,
    disable_web_page_preview: Optional[bool] = None,
    disable_notification: Optional[bool] = None,
    protect_content: Optional[bool] = None,
    reply_to_message_id: Optional[int] = None,
    allow_sending_without_reply: Optional[bool] = None,
    reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]] = None,
) -> None:
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            entities=entities,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=reply_markup,
        )
    except TelegramBadRequest:
        log.warning(f"Cant send message to {chat_id}")
    except Exception as e:
        log.error(f"{e=}")
