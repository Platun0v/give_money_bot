from typing import Any, Dict

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from give_money_bot.db.db_connector import db


class UserMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: Dict[str, Any]) -> None:
        data["user"] = db.get_user(message.from_user.id)

    async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data: Dict[str, Any]) -> None:
        data["user"] = db.get_user(callback_query.from_user.id)
