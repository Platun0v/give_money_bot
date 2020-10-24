from aiogram import Bot, Dispatcher, executor, types
import config
from loguru import logger

bot = Bot(token=config.TOKEN, proxy=config.PROXY)
dp = Dispatcher(bot)


@dp.message_handler()
async def echo(message: types.Message):
    await message.reply(message.text)


@logger.catch()
def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
