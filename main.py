from typing import List

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import keyboards as kb
import config
from my_state import AddState
from loguru import logger

bot = Bot(token=config.TOKEN, proxy=config.PROXY)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(text="+", state=None)
async def process_callback_plus(message: types.Message):
    await message.answer("Введите сумму")
    await AddState.read_num.set()


@dp.message_handler(text="info")
async def process_callback_info(message: types.Message):
    await message.answer("plus!", reply_markup=kb.markup_test)


@dp.message_handler(state=AddState.read_num)
async def read_num_from_user(message: types.Message, state: FSMContext):
    try:
        value = int(message.text)
        await message.answer(f"Кто тебе должен {value} руб?",
                             reply_markup=kb.get_inline_markup(message.from_user.id, value, set()))
    except Exception:
        await message.answer("Мне было нужно число, а ты мне что дал?")
    await state.finish()


@dp.callback_query_handler(text_contains="save")
async def process_callback_save(call: types.CallbackQuery):
    value, users = kb.get_data_from_markup(call.message.reply_markup)

    text = ""
    if len(users) == 0:
        text = "Ты забыл указать должников"
    else:
        text = f"Тебе {value} руб должен "
        for id in users:
            text += f"{config.USERS[int(id)]}, "
        text = text[:-2]
        text += "\nСохранено"
        await call.message.edit_text(text)

    await bot.answer_callback_query(call.id, text=text, show_alert=True)


@dp.callback_query_handler(text_contains="cancel")
async def process_callback_cancel(call: types.CallbackQuery):
    value = kb.get_value_from_markup(call.message.reply_markup)
    await call.message.edit_text(f"{value} руб. Отмена")
    await bot.answer_callback_query(call.id, text="Отмена")


@dp.callback_query_handler(text_contains="user")
async def process_callback(call: types.CallbackQuery):
    value, users = kb.get_data_from_markup(call.message.reply_markup)
    user_id = kb.get_user_id(call.data)

    if user_id in users:
        users.remove(user_id)
    else:
        users.add(user_id)

    text = f"Тебе {value} руб должен "
    for id in users:
        text += f"{config.USERS[int(id)]}, "
    text += "..."

    await call.message.edit_text(text=text, reply_markup=kb.get_inline_markup(call.from_user.id, value, users))
    await bot.answer_callback_query(call.id)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer("Привет!", reply_markup=kb.markup_main)


@dp.message_handler(commands=['id'])
async def get_id(message: types.Message):
    await message.answer(f"{message.from_user.id}")


@logger.catch()
def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
