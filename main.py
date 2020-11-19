from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from my_state import AddState
import keyboards as kb
from keyboards import CALLBACK
from db_connector import DB
import config
from log import logger


bot = Bot(token=config.TOKEN)  # Works fine without proxy (18.11.2020) , proxy=config.PROXY)
dp = Dispatcher(bot, storage=MemoryStorage())
db = DB()


def check_user(message: types.Message) -> bool:
    return message.from_user.id in config.USERS.keys()


def get_info(message: types.Message) -> str:
    msg = message.text.split("\n")
    return '' if len(msg) == 1 else msg[1]


@dp.message_handler(check_user, commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer("Привет!", reply_markup=kb.main_markup)


@dp.message_handler(check_user, commands=['id'])
async def get_id(message: types.Message):
    await message.answer(f"{message.from_user.id}")


# ======================================= ADD CREDIT =======================================
@dp.message_handler(check_user, text="+")
async def process_callback_plus(message: types.Message):
    await message.answer("Введите сумму(по желанию инфу по долгу через пробел)")
    await AddState.read_num.set()


@dp.message_handler(state=AddState.read_num)
async def read_num_from_user(message: types.Message, state: FSMContext):
    await state.finish()

    message_text = message.text.split(" ")
    try:
        value = int(message_text[0])
    except ValueError:
        await message.answer("Требуется число в начале сообщения")
        return

    text = f"Кто тебе должен {value} руб?\n" \
           f"{' '.join(message_text[1:])}"

    await message.answer(text, reply_markup=kb.get_keyboard_users_for_credit(message.from_user.id, value, set()))


@dp.callback_query_handler(text_contains=CALLBACK.choose_user_for_credit)
async def process_callback(call: types.CallbackQuery):
    value, users = kb.get_data_from_markup(call.message.reply_markup)
    user_id = kb.get_user_id(call.data)

    if user_id in users:
        users.remove(user_id)
    else:
        users.add(user_id)

    await call.message.edit_reply_markup(reply_markup=kb.get_keyboard_users_for_credit(call.from_user.id, value, users))
    await call.answer()


@dp.callback_query_handler(text_contains=CALLBACK.save_credit)
async def process_callback_save(call: types.CallbackQuery):
    value, users = kb.get_data_from_markup(call.message.reply_markup)
    if not users:
        text = "Ты забыл указать должников"
    else:
        user_names = list(map(lambda x: config.USERS[x], users))
        info = get_info(call.message)
        text = f'Тебе {value} руб должен: {", ".join(user_names)}\n' \
               f'{info}\n' \
               f'Сохранено'
        await call.message.edit_text(text)

        user_id = call.from_user.id
        db.add_entry(user_id, list(users), value, info)

        for user in users:
            try:  # Fixes not started conv with bot
                text_users = f"Ты должен {value} руб. ему: {config.USERS[user_id]}\n" \
                             f"{info}"
                await bot.send_message(user, text_users)
            except Exception:
                pass
    await call.answer(text=text, show_alert=True)


@dp.callback_query_handler(text_contains=CALLBACK.cancel_crt_credit)
async def process_callback_cancel(call: types.CallbackQuery):
    value = kb.get_amount_from_markup(call.message.reply_markup)
    await call.message.edit_text(
        f"{value} руб. {get_info(call.message)}\n"
        f"Отменено"
    )
    await call.answer(text="Отмена")


# ======================================= REMOVE CREDIT =======================================
@dp.message_handler(check_user, text='-')
async def process_callback_user_credits(message: types.Message):
    user_credits = db.user_credits(message.from_user.id)
    if not user_credits:
        text = "Ты никому не должен. Свободен"
        await message.answer(text)
    else:
        text = "Ты должен:\n"
        credits_sum = 0
        for i, credit in enumerate(user_credits, 1):
            credits_sum += credit.amount
            text += f'{i}) {credit.amount} руб. ему: {config.USERS[credit.to_id]}\n' \
                    f'{credit.get_text_info_new_line()}' \
                    f'Долг был добавлен {credit.get_date_str()}\n'
        text += f"Итого: {credits_sum} руб.\n"
        text += "Ты можешь выбрать долги, которые ты уже вернул:"
        await message.answer(text, reply_markup=kb.get_credits_markup(user_credits, set()))


@dp.callback_query_handler(text_contains=CALLBACK.choose_credit_for_return)
async def process_callback_credit_chose(call: types.CallbackQuery):
    marked_credits = kb.get_marked_credits(call.message.reply_markup)
    credit_id = kb.get_credit_id(call.data)
    user_id = int(call.from_user.id)

    if credit_id in marked_credits:
        marked_credits.remove(credit_id)
    else:
        marked_credits.add(credit_id)

    await call.message.edit_reply_markup(
        reply_markup=kb.get_credits_markup(db.user_credits(user_id), marked_credits))
    await call.answer()


@dp.callback_query_handler(text_contains=CALLBACK.return_credits)
async def process_callback_return_credit(call: types.CallbackQuery):
    marked_credits = kb.get_marked_credits(call.message.reply_markup)

    if not marked_credits:
        text = "Ты ничего не отметил"
    else:
        returned_credits = []
        text = "Ты вернул:"
        for credit_id in marked_credits:
            returned_credits.append(credit_id)
            credit = db.get_credit(credit_id)
            text = f'{credit.amount} руб. ему: {config.USERS[credit.to_id]}\n' \
                   f'{credit.get_text_info_new_line()}'

        db.return_credit(returned_credits)
        await call.message.edit_text(text)

    await call.answer(text=text, show_alert=True)

    for credit_id in marked_credits:
        credit = db.get_credit(credit_id)
        markup = kb.get_check_markup(credit_id, True)
        message = f'Тебе {config.USERS[credit.from_id]} вернул {credit.amount} руб.\n' \
                  f'{credit.get_text_info_new_line()}'
        try:
            await bot.send_message(credit.to_id, message, reply_markup=markup)
        except Exception:
            pass


@dp.callback_query_handler(text_contains=CALLBACK.cancel_return_credits)
async def process_callback_credit_cancel(call: types.CallbackQuery):
    text = '\n'.join(call.message.text.split("\n")[:-1])
    await call.message.edit_text(text)
    await call.answer()


@dp.callback_query_handler(text_contains=CALLBACK.check_return_approve)
async def process_callback_check_true(call: types.CallbackQuery):
    credit_id, value = kb.get_data_from_check(call.message.reply_markup)
    if value == "0":
        await call.message.edit_reply_markup(kb.get_check_markup(credit_id, True))
    await call.answer()


@dp.callback_query_handler(text_contains=CALLBACK.check_return_reject)
async def process_callback_check_false(call: types.CallbackQuery):
    credit_id, value = kb.get_data_from_check(call.message.reply_markup)
    if value == "1":
        await call.message.edit_reply_markup(kb.get_check_markup(credit_id, False))
    await call.answer()


@dp.callback_query_handler(text_contains=CALLBACK.check_return_of_credit)
async def process_callback_check(call: types.CallbackQuery):
    credit_id, value = kb.get_data_from_check(call.message.reply_markup)

    await call.answer()

    if value == "1":
        await call.message.delete_reply_markup()
    else:
        db.reject_return_credit(credit_id)
        text = call.message.text
        await call.message.edit_text(text + "\nОтмена")
        credit = db.get_credit(credit_id)
        message = f"{config.USERS[credit.to_id]} отметил, что ты не вернул {credit.amount} руб.\n" \
                  f"{credit.get_text_info_new_line()}"

        await bot.send_message(credit.from_id, message)


# ======================================= INFO =======================================
@dp.message_handler(check_user, text='info')
async def process_callback_credits_to_user(message: types.Message):
    credits_to_user = db.credits_to_user(message.from_user.id)

    if not credits_to_user:
        text = "Тебе никто не должен. Можешь спать спокойно"
    else:
        text = "Тебе должны:\n"
        credits_sum = 0
        for i, credit in enumerate(credits_to_user, 1):
            credits_sum += credit.amount
            text += f'{i}) {config.USERS[credit.from_id]}: {credit.amount} руб.\n' \
                    f'{credit.get_text_info_new_line()}' \
                    f'Долг был добавлен {credit.get_date_str()}\n'
        text += f'Итог: {credits_sum} руб.'

    await message.answer(text, reply_markup=kb.main_markup)


def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
