import asyncio
from typing import Any, Tuple

import sentry_sdk
import sqlalchemy
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from aiohttp.web import _run_app
from loguru import logger as log
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import SingletonThreadPool

from give_money_bot.admin.dispatcher import router as admin_router
from give_money_bot.config import cfg
from give_money_bot.credits.dispatcher import router as credits_router
from give_money_bot.settings.dispatcher import router as settings_router
from give_money_bot.tg_bot.bot import router as tg_bot_router
from give_money_bot.utils.log import init_logger
from give_money_bot.utils.misc import DbSessionMiddleware, SubstituteUserMiddleware, UserMiddleware
from give_money_bot.utils.prometheus_middleware import PrometheusMiddleware, metrics


def init_sentry() -> None:
    sentry_sdk.init(
        dsn=cfg.sentry_dsn,
        traces_sample_rate=cfg.sentry_traces_sample_rate,
        environment=cfg.environment,
    )


def init_db() -> sessionmaker:
    engine = sqlalchemy.create_engine(
        f"sqlite:///{cfg.db_path + 'db.sqlite'}",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=SingletonThreadPool,
    )

    db_pool = sessionmaker(bind=engine)
    return db_pool


def init_bot(db_pool: sessionmaker) -> Tuple[Bot, Dispatcher]:
    bot = Bot(token=cfg.telegram_token)

    dp = Dispatcher(storage=MemoryStorage())

    dp.message.outer_middleware(DbSessionMiddleware(db_pool))
    dp.message.middleware(UserMiddleware())
    dp.message.middleware(SubstituteUserMiddleware())
    dp.message.middleware(PrometheusMiddleware())

    dp.callback_query.outer_middleware(DbSessionMiddleware(db_pool))
    dp.callback_query.middleware(UserMiddleware())
    dp.callback_query.middleware(SubstituteUserMiddleware())
    dp.callback_query.middleware(PrometheusMiddleware())

    init_modules(dp)

    return bot, dp


def init_modules(dp: Dispatcher) -> None:
    dp.include_router(tg_bot_router)
    dp.include_router(admin_router)
    dp.include_router(settings_router)
    dp.include_router(credits_router)

    log.info("Modules loaded")


async def on_error(update: Any, exception: Exception, bot: Bot) -> None:
    await bot.send_message(chat_id=cfg.admin_id, text=f"Error occurred: {exception}")
    log.exception(exception)
    log.error(exception)


def init_web_server() -> web.Application:
    app = web.Application()
    app.add_routes([web.get('/metrics', metrics)])

    return app


def main() -> None:
    init_sentry()
    init_logger()

    db_pool = init_db()
    bot, dp = init_bot(db_pool)
    dp.errors.register(on_error)

    app = init_web_server()

    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling(bot))
    loop.create_task(_run_app(app, port=cfg.prometheus_port))

    log.info("Starting bot")
    loop.run_forever()
    log.info("Bot stopped")
