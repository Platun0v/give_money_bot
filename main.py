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
    await message.answer("Введите сумму(по желанию инфу по долгу через пробел)")
    await AddState.read_num.set()


@dp.message_handler(text="info")
async def process_callback_info(message: types.Message):
    await message.answer("plus!")


@dp.message_handler(state=AddState.read_num)
async def read_num_from_user(message: types.Message, state: FSMContext):
    message_text = message.text.split(" ")
    value = None
    try:
        value = int(message_text[0])
    except Exception:
        await message.answer("Мне было нужно число, а ты мне что дал?")
        await state.finish()
        return

    text = f"Кто тебе должен {value} руб?"
    if len(message_text) > 1:
        text += "\n|"
        for i in range(1, len(message_text)):
            text += f"{message_text[i]} "

    await message.answer(text, reply_markup=kb.get_inline_markup(message.from_user.id, value, set()))
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
        info = get_info(call.message)
        text += info
        text += "\nСохранено"
        await call.message.edit_text(text)
        for user_id in users:
            await bot.send_message(int(user_id), f"Ты должен {value} руб. ему: "
                                                 f"{config.USERS[call.from_user.id] + info}")
    await bot.answer_callback_query(call.id, text=text, show_alert=True)


@dp.callback_query_handler(text_contains="cancel")
async def process_callback_cancel(call: types.CallbackQuery):
    value = kb.get_value_from_markup(call.message.reply_markup)
    await call.message.edit_text(f"{value} руб.{get_info(call.message)}\nОтмена")
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

    text += get_info(call.message)

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


def get_info(message):
    message_text = message.text.split("|")
    text = ""
    if len(message_text) > 1:
        text += f"\n|{message_text[1]}"
    return text


if __name__ == "__main__":
    main()
