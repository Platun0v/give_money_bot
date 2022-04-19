from typing import Any

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from give_money_bot import config
from give_money_bot.utils.log import logger
from give_money_bot.utils.misc import UserMiddleware

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(UserMiddleware())


def init_modules() -> None:
    from give_money_bot.admin import dispatcher as admin_dispatcher
    from give_money_bot.credits import dispatcher as credits_dispatcher
    from give_money_bot.settings import dispatcher as settings_dispatcher
    from give_money_bot.tg_bot import bot as tg_bot_dispatcher

    tg_bot_dispatcher.load_module()
    admin_dispatcher.load_module()
    settings_dispatcher.load_module()
    credits_dispatcher.load_module()  # Should be last for correct work

    logger.info("Modules loaded")


@dp.errors_handler()
async def on_error(update: Any, exception: Exception) -> None:
    logger.exception(exception)
    logger.error(exception)


def main() -> None:
    init_modules()
    logger.info("Starting bot")
    executor.start_polling(dp, skip_updates=True)
