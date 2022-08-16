from typing import Any

import sqlalchemy
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage
from loguru import logger as log
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import SingletonThreadPool

import give_money_bot.utils.log
from give_money_bot import config
from give_money_bot.db.base import Base
from give_money_bot.utils.misc import DbSessionMiddleware, UserMiddlewareCallbackQuery, UserMiddlewareMessage

# import sentry_sdk
# sentry_sdk.init(
#     "https://3e62d55707a64ec280d22e4ec1e2d809@o1226305.ingest.sentry.io/6390884",
#     traces_sample_rate=1.0
# )


engine = sqlalchemy.create_engine(
    f"sqlite:///{config.DB_PATH + 'db.sqlite'}",
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=SingletonThreadPool,
)
Base.metadata.create_all(engine)
db_pool = sessionmaker(bind=engine)

bot = Bot(token=config.TOKEN)

dp = Dispatcher(storage=MemoryStorage())
dp.message.outer_middleware(DbSessionMiddleware(db_pool))
dp.message.middleware(UserMiddlewareMessage())
dp.callback_query.outer_middleware(DbSessionMiddleware(db_pool))
dp.callback_query.middleware(UserMiddlewareCallbackQuery())


def init_modules() -> None:
    from give_money_bot.admin.dispatcher import router as admin_router
    from give_money_bot.credits.dispatcher import router as credits_router
    from give_money_bot.settings.dispatcher import router as settings_router
    from give_money_bot.tg_bot.bot import router as tg_bot_router

    dp.include_router(tg_bot_router)
    dp.include_router(admin_router)
    dp.include_router(settings_router)
    dp.include_router(credits_router)

    log.info("Modules loaded")


@dp.errors()
async def on_error(update: Any, exception: Exception) -> None:
    log.exception(exception)
    log.error(exception)


def main() -> None:
    init_modules()
    log.info("Starting bot")
    dp.run_polling(bot)
