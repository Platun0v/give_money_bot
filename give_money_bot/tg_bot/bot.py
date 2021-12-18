import os
import string
from subprocess import Popen, PIPE
from typing import Tuple, List, Optional, Dict

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from give_money_bot import config
from give_money_bot.db.db_connector import DB
from give_money_bot.db.models import Credit
from give_money_bot.tg_bot import keyboards as kb
from give_money_bot.tg_bot.keyboards import CALLBACK
from give_money_bot.tg_bot.my_state import AddState
from give_money_bot.utils.log import logger
from give_money_bot.utils.strings import Strings

logger.debug('DbPath: "{}", LogPath: "{}"', config.DB_PATH, config.LOG_PATH)

bot = Bot(
    token=config.TOKEN
)  # Works fine without proxy (18.11.2020) , proxy=config.PROXY)
dp = Dispatcher(bot, storage=MemoryStorage())
db = DB(db_path=config.DB_PATH + "db.sqlite")


def check_user(message: types.Message) -> bool:
    return message.from_user.id in config.USERS.keys()


def check_admin(message: types.Message) -> bool:
    return message.from_user.id == config.ADMIN


def get_info(message: types.Message) -> str:
    msg = message.text.split("\n")
    return "" if len(msg) == 1 else msg[1]


def get_credits_amount(from_user: int, to_user: int) -> Tuple[int, List[Credit]]:
    user_credits = db.get_credits_to_user_from_user(
        from_user=from_user, to_user=to_user
    )
    res_sum = 0
    for credit in user_credits:
        res_sum += credit.get_amount()
    return res_sum, user_credits


@dp.message_handler(check_user, commands=["start"])
async def process_start_command(message: types.Message):
    await message.answer(Strings.HELLO_MESSAGE, reply_markup=kb.main_markup)


@dp.message_handler(check_user, commands=["id"])
async def get_id(message: types.Message):
    await message.answer(f"{message.from_user.id}")


# TODO: Divide this shit into many functions
@dp.message_handler(check_admin, commands=["sqz"])
async def squeeze_credits(message: Optional[types.Message]):
    users_id = list(config.USERS.keys())
    for i, _user1 in enumerate(users_id):
        for j, _user2 in enumerate(users_id[i + 1:], i + 1):
            user1, user2 = _user1, _user2

            user1_amount, user1_lst = get_credits_amount(
                user1, user2
            )  # сколько 1 должен 2
            user2_amount, user2_lst = get_credits_amount(
                user2, user1
            )  # сколько 2 должен 1
            if (
                user1_amount == 0 or user2_amount == 0
            ):  # Не выполняем код, если первый не должен второму
                continue

            if (
                user2_amount > user1_amount
            ):  # Меняем местами 1 и 2, чтобы amount1 > amount2
                user1_amount, user2_amount = user2_amount, user1_amount
                user1, user2 = user2, user1
                user1_lst, user2_lst = user2_lst, user1_lst
            diff = user1_amount - user2_amount
            old_user2_amount = user2_amount

            logger.info(
                f"Try to squeeze of {user1}:{user2} - with amount1={user1_amount},  amount2={user2_amount}"
            )

            db.return_credits(
                list(map(lambda x: x.id, user2_lst))
            )  # Возвращаем все кредиты 2 пользователя

            user1_lst.sort(
                key=lambda x: x.get_amount()
            )  # Сортируем долги 1 по возрастанию
            it = 0
            credits_to_return = []
            while user2_amount > 0:  # Обнуляем долги 1 на сумму amount2
                if user2_amount < user1_lst[it].get_amount():
                    db.add_discount(user1_lst[it], discount=user2_amount)
                    user2_amount = 0
                else:
                    user2_amount -= user1_lst[it].get_amount()
                    credits_to_return.append(user1_lst[it].id)
                it += 1
            db.return_credits(credits_to_return)

            user1_amount, user1_lst = get_credits_amount(
                user1, user2
            )  # сколько 1 должен 2
            user2_amount, user2_lst = get_credits_amount(
                user2, user1
            )  # сколько 2 должен 1

            logger.info(
                f"Squeeze of {user1}:{user2} - amount1={user1_amount} amount2={user2_amount}"
            )
            if diff != (user1_amount - user2_amount):  # Что-то пошло не так
                logger.error(
                    f"Failed squeeze credits of {user1}:{user2} - {user1 - user2}\n{user1_lst}\n{user2_lst}"
                )
                await bot.send_message(config.ADMIN, "Error occurred")
                return

            await bot.send_message(
                user1,
                f"Были взаимоуничтожены долги на сумму {old_user2_amount} с {config.USERS[user2]}",
            )
            await bot.send_message(
                user2,
                f"Были взаимоуничтожены долги на сумму {old_user2_amount} с {config.USERS[user1]}",
            )


# ======================================= ADD CREDIT =======================================
@dp.message_handler(check_user, text="+")
async def process_callback_plus(message: types.Message):
    await message.answer(Strings.INPUT_CREDIT)
    await AddState.read_num.set()


def parse_expression(value: str) -> Tuple[Optional[int], Optional[str]]:
    p = Popen("./parser", stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate(bytes(value, "utf-8"))
    if err:
        return None, err.decode("utf-8").split("\n")[0]
    return int(out), None


def parse_info_from_message(message: str) -> Tuple[str, str]:
    for i, char in enumerate(message):
        if char not in Strings.DIGITS:
            return message[:i], message[i:]
    return message, ""


@dp.message_handler(state=AddState.read_num)
async def read_num_from_user(message: types.Message, state: FSMContext):
    await state.finish()

    value_str, info = parse_info_from_message(message.text)
    value, err = parse_expression(value_str)
    if value is None:
        await message.answer(err)
        return
    if value == 0:
        await message.answer(Strings.NEED_NON_ZERO)
        return

    await message.answer(
        Strings.ASK_FOR_DEBTORS(value, info, negative=value < 0),
        reply_markup=kb.get_keyboard_users_for_credit(
            message.from_user.id, value, set()
        ),
    )


@dp.callback_query_handler(text_contains=CALLBACK.choose_user_for_credit)
async def process_callback(call: types.CallbackQuery):
    value, users = kb.get_data_from_markup(call.message.reply_markup)
    user_id = kb.get_user_id(call.data)

    if user_id in users:
        users.remove(user_id)
    else:
        users.add(user_id)

    await call.message.edit_reply_markup(
        reply_markup=kb.get_keyboard_users_for_credit(call.from_user.id, value, users)
    )
    await call.answer()


@dp.callback_query_handler(text_contains=CALLBACK.save_credit)
async def process_callback_save(call: types.CallbackQuery):
    value, users = kb.get_data_from_markup(call.message.reply_markup)
    if not users:
        await call.answer(text=Strings.FORGOT_CHOOSE)
        return

    neg = False
    if value < 0:
        neg = True
        value = abs(value)

    user_names = list(map(lambda x: config.USERS[x], users))
    info = get_info(call.message)
    await call.message.edit_text(Strings.SAVE_CREDIT(value, user_names, info, negative=neg))

    user_id = call.from_user.id
    if neg:
        db.add_entry_2(list(users), user_id, value, info)
    else:
        db.add_entry(user_id, list(users), value, info)

    for user in users:
        try:  # Fixes not started conv with give_money_bot
            await bot.send_message(user, Strings.ANNOUNCE_NEW_CREDIT(value, config.USERS[user_id], info, neg))
        except Exception:
            pass

    await squeeze_credits(message=None)


@dp.callback_query_handler(text_contains=CALLBACK.cancel_crt_credit)
async def process_callback_cancel(call: types.CallbackQuery):
    await call.message.edit_text(Strings.CANCEL)


# ======================================= REMOVE CREDIT =======================================
@dp.message_handler(check_user, text="-")
async def process_callback_user_credits(message: types.Message):
    user_credits = db.get_user_credits(message.from_user.id)
    if not user_credits:
        await message.answer(Strings.NO_CREDITS_DEBTOR)
        return

    text = Strings.DEBTOR_CREDITS_GENERATOR()
    credits_sum = 0
    credits_sum_by_user: Dict[int, int] = {}
    for i, credit in enumerate(user_credits, 1):
        credits_sum += credit.get_amount()
        credits_sum_by_user[credit.to_id] = (
            credits_sum_by_user.get(credit.to_id, 0) + credit.get_amount()
        )
        text.add_position(i, credit.get_amount(), config.USERS[credit.to_id], credit.text_info)

    for user_id, amount in credits_sum_by_user.items():
        text.add_sum(amount, config.USERS[user_id])

    await message.answer(
        text.finish(credits_sum), reply_markup=kb.get_credits_markup(user_credits, set())
    )


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
        reply_markup=kb.get_credits_markup(db.get_user_credits(user_id), marked_credits)
    )
    await call.answer()


@dp.callback_query_handler(text_contains=CALLBACK.return_credits)
async def process_callback_return_credit(call: types.CallbackQuery):
    marked_credits = kb.get_marked_credits(call.message.reply_markup)

    if not marked_credits:
        await call.answer(Strings.FORGOT_CHOOSE)
        return

    returned_credits = []
    text = Strings.RETURN_GENERATOR()
    for credit_id in marked_credits:
        returned_credits.append(credit_id)
        credit = db.get_credit(credit_id)
        text.add_position(credit.get_amount(), config.USERS[credit.to_id], credit.text_info)

    db.return_credits(returned_credits)
    await call.message.edit_text(text.finish())

    await call.answer(text=text.finish(), show_alert=True)

    for credit_id in marked_credits:
        credit = db.get_credit(credit_id)
        markup = kb.get_check_markup(credit_id, True)
        try:
            await bot.send_message(
                credit.to_id,
                Strings.ANNOUNCE_RETURN_CREDIT(credit.get_amount(), config.USERS[credit.from_id], credit.text_info),
                reply_markup=markup
            )
        except Exception:
            pass


@dp.callback_query_handler(text_contains=CALLBACK.cancel_return_credits)
async def process_callback_credit_cancel(call: types.CallbackQuery):
    text = "\n".join(call.message.text.split("\n")[:-1])
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
        message = (
            f"{config.USERS[credit.to_id]} отметил, что ты не вернул {credit.get_amount()} руб.\n"
            f"{credit.get_text_info_new_line()}"
        )

        await bot.send_message(credit.from_id, message)


# ======================================= INFO =======================================
@dp.message_handler(check_user, text="info")
async def process_callback_credits_to_user(message: types.Message):
    credits_to_user = db.credits_to_user(message.from_user.id)

    if not credits_to_user:
        text = Strings.NO_CREDITS_CREDITOR
        await message.answer(text, reply_markup=kb.main_markup)
        return

    text = Strings.CREDITOR_CREDITS_GENERATOR()
    credits_sum = 0
    credits_sum_by_user: Dict[int, int] = {}
    for i, credit in enumerate(credits_to_user, 1):
        credits_sum += credit.get_amount()
        credits_sum_by_user[credit.from_id] = (
            credits_sum_by_user.get(credit.from_id, 0) + credit.get_amount()
        )
        text.add_position(i, credit.get_amount(), config.USERS[credit.from_id], credit.text_info)

    for user_id, amount in credits_sum_by_user.items():
        text.add_sum(amount, config.USERS[user_id])

    await message.answer(text.finish(credits_sum), reply_markup=kb.main_markup)


def main():
    logger.info("Starting bot")
    executor.start_polling(dp, skip_updates=True)
