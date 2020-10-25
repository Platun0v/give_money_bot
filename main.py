from typing import List

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import keyboards as kb
import config
from db_connector import DB
from my_state import AddState
from loguru import logger

bot = Bot(token=config.TOKEN, proxy=config.PROXY)
dp = Dispatcher(bot, storage=MemoryStorage())
db = DB()


@dp.message_handler(text="+", state=None)
async def process_callback_plus(message: types.Message):
    await message.answer("Введите сумму(по желанию инфу по долгу через пробел)")
    await AddState.read_num.set()


@dp.message_handler(text="info")
async def process_callback_info(message: types.Message):
    await message.answer("Что интересует?", reply_markup=kb.murkup_credits)


@dp.callback_query_handler(text_contains="user_credits")
async def process_callback_credits_to_user(call: types.CallbackQuery):
    text = "Ты должен:"
    credits = db.user_credits(call.from_user.id)
    if len(credits) == 0:
        text = "Ты никому не должен. Свободен"
    else:
        index = 1
        for credit in credits:
            text += f"\n{index}){credit.amount} руб. ему:{config.USERS[credit.to_id]}"
            if len(credit.text_info) != 0:
                text += f" за {credit.text_info}"
            text += f"\nДолг был добавлен {credit.date}"
            index += 1
        text += "\nТы можешь выбрать долги, которые ты уже вернул:"
    await call.message.edit_text(text, reply_markup=kb.get_credits_markup(len(credits), set()))
    await bot.answer_callback_query(call.id)


@dp.callback_query_handler(text_contains="credit_chose")
async def process_callback_credits_to_user(call: types.CallbackQuery):
    marked_credits = kb.get_marked_credits(call.message.reply_markup)
    credit_id = kb.get_credit_index(call.data)
    user_id = int(call.from_user.id)

    if credit_id in marked_credits:
        marked_credits.remove(credit_id)
    else:
        marked_credits.add(credit_id)

    await call.message.edit_reply_markup(
        reply_markup=kb.get_credits_markup(len(db.user_credits(user_id)), marked_credits))
    await bot.answer_callback_query(call.id)


@dp.callback_query_handler(text_contains="credits_to_user")
async def process_callback_credits_to_user(call: types.CallbackQuery):
    text = "Тебе должны:"
    credits = db.credits_to_user(call.from_user.id)
    if len(credits) == 0:
        text = "Тебе никто не должен. Можешь спать спокойно"
    else:
        index = 1
        for credit in credits:
            text += f"\n{index}){config.USERS[credit.from_id]}: {credit.amount} руб."
            if len(credit.text_info) != 0:
                text += f" за {credit.text_info}"
            text += f"\nДолг был добавлен {credit.date}"
            index += 1
    await call.message.edit_text(text)
    await bot.answer_callback_query(call.id)


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
        for user_id in users:
            text += f"{config.USERS[user_id]}, "
        text = text[:-2]
        info = get_info(call.message)
        text += "\n|" + info
        text += "\nСохранено"
        user_id = call.from_user.id
        db.add_entry(user_id, users, value, info)
        await call.message.edit_text(text)
        for user_id in users:
            await bot.send_message(user_id, f"Ты должен {value} руб. ему: {config.USERS[user_id]}\n" + info)
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

    await call.message.edit_reply_markup(reply_markup=kb.get_inline_markup(call.from_user.id, value, users))
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


def get_info(message: types.Message):
    message_text = message.text.split("|")
    text = ""
    if len(message_text) > 1:
        text += f"{message_text[1]}"
    return text


if __name__ == "__main__":
    main()
