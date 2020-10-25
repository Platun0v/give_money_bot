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
        await state.update_data({"value": value, "users": []})
        await message.answer(f"Кто тебе должен {value} руб?", reply_markup=kb.get_inline_markup(message.from_user.id, value, set()))
    except Exception:
        await message.answer("Мне было нужно число, а ты мне что дал?")
    await state.reset_state(with_data=False)


@dp.callback_query_handler(lambda c: c.data == 'save')
async def process_callback_save(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = f"Тебе { data.get('value')} руб должен "
    for id in data.get("users"):
        text += f"{config.USERS[int(id)]}, "
    text = text[:-2]
    text += "\nСохранено"
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text)
    await state.reset_state()
    await bot.answer_callback_query(call.id, text=text, show_alert=True)


@dp.callback_query_handler(lambda c: c.data == 'cancel')
async def process_callback_cancel(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f"{data.get('value')} руб. Отмена")
    await state.reset_state()
    await bot.answer_callback_query(call.id, text="Отмена")


@dp.callback_query_handler(text_contains="user")
async def process_callback(call: types.CallbackQuery):
    markup = call.message.reply_markup

    users = set()
    value = None
    for i in markup["inline_keyboard"]:
        if "save" in i[0].callback_data:
            value = kb.save_data.parse(i[0].callback_data).get("value")
        if "user" in i[0].callback_data:
            user_data = kb.user_data.parse(i[0].callback_data)
            if user_data.get("has_mark") == "1":
                users.add(user_data.get("id"))

    user_id = kb.user_data.parse(call.data).get("id")
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
