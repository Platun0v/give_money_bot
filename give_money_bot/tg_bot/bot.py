from typing import Optional, Dict, List

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from give_money_bot import config
from give_money_bot.db.db_connector import db
from give_money_bot.db.models import Credit
from give_money_bot.tg_bot import keyboards as kb
from give_money_bot.tg_bot.keyboards import CALLBACK
from give_money_bot.tg_bot.utils import check_user, check_admin, get_info, get_credits_amount, parse_info_from_message, \
    parse_expression
from give_money_bot.utils.log import logger
from give_money_bot.utils.strings import Strings


bot = Bot(
    token=config.TOKEN
)  # Works fine without proxy (18.11.2020) , proxy=config.PROXY)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(check_user, commands=["start"])
async def process_start_command(message: types.Message) -> None:
    await message.answer(Strings.HELLO_MESSAGE, reply_markup=kb.main_markup)


@dp.message_handler(check_user, commands=["id"])
async def get_id(message: types.Message) -> None:
    await message.answer(f"{message.from_user.id}")


# TODO: Divide this shit into many functions
@dp.message_handler(check_admin, commands=["sqz"])
async def squeeze_credits(message: Optional[types.Message]) -> None:
    user_ids = [e.user_id for e in db.get_users()]
    for i, _user1 in enumerate(user_ids):
        for j, _user2 in enumerate(user_ids[i + 1:], i + 1):
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
                await bot.send_message(db.get_admin().user_id, "Error occurred")
                return

            await bot.send_message(
                user1,
                f"Были взаимоуничтожены долги на сумму {old_user2_amount} с {db.get_user(user2).name}",
            )
            await bot.send_message(
                user2,
                f"Были взаимоуничтожены долги на сумму {old_user2_amount} с {db.get_user(user1).name}",
            )


# ======================================= ADD CREDIT =======================================
async def read_num_from_user(message: types.Message) -> None:
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
async def process_callback(call: types.CallbackQuery) -> None:
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
async def process_callback_save(call: types.CallbackQuery) -> None:
    value, users = kb.get_data_from_markup(call.message.reply_markup)
    if not users:
        await call.answer(text=Strings.FORGOT_CHOOSE)
        return

    neg = False
    if value < 0:
        neg = True
        value = abs(value)

    info = get_info(call.message)
    await call.message.edit_text(Strings.SAVE_CREDIT(value, [e.name for e in db.get_users(users)], info, negative=neg))

    user_id = call.from_user.id
    if neg:
        db.add_entry_2(list(users), user_id, value, info)
    else:
        db.add_entry(user_id, list(users), value, info)

    for user in users:
        try:  # Fixes not started conv with give_money_bot
            await bot.send_message(user, Strings.ANNOUNCE_NEW_CREDIT(value, db.get_user(user_id).name, info, neg))
        except Exception:
            pass

    await squeeze_credits(message=None)


@dp.callback_query_handler(text_contains=CALLBACK.cancel_crt_credit)
async def process_callback_cancel(call: types.CallbackQuery) -> None:
    await call.message.edit_text(Strings.CANCEL)


# ======================================= REMOVE CREDIT =======================================
@dp.message_handler(check_user, text="-")
async def process_callback_user_credits(message: types.Message) -> None:
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
        text.add_position(i, credit.get_amount(), credit.creditor.name, credit.text_info)

    for user_id, amount in credits_sum_by_user.items():
        text.add_sum(amount, db.get_user(user_id).name)

    await message.answer(
        text.finish(credits_sum), reply_markup=kb.get_credits_markup(credits_sum_by_user, set())
    )


@dp.callback_query_handler(text_contains=CALLBACK.choose_credit_for_return)
async def process_callback_credit_chose(call: types.CallbackQuery) -> None:
    marked_users = kb.get_marked_credits(call.message.reply_markup)
    chosen_user_id = kb.get_credit_id(call.data)

    if chosen_user_id in marked_users:
        marked_users.remove(chosen_user_id)
    else:
        marked_users.add(chosen_user_id)

    credits_sum_by_user: Dict[int, int] = {}
    for credit in db.get_user_credits(int(call.from_user.id)):
        credits_sum_by_user[credit.to_id] = (
                credits_sum_by_user.get(credit.to_id, 0) + credit.get_amount()
        )

    await call.message.edit_reply_markup(
        reply_markup=kb.get_credits_markup(credits_sum_by_user, marked_users)
    )
    await call.answer()


@dp.callback_query_handler(text_contains=CALLBACK.return_credits)
async def process_callback_return_credit(call: types.CallbackQuery) -> None:
    marked_users = kb.get_marked_credits(call.message.reply_markup)

    if not marked_users:
        await call.answer(Strings.FORGOT_CHOOSE)
        return

    returned_credits: List[int] = []
    text = Strings.RETURN_GENERATOR()
    for user_id in marked_users:
        amount, credits = get_credits_amount(call.from_user.id, user_id)
        for credit in credits:
            returned_credits.append(credit.id)
        text.add_position(amount, db.get_user(user_id).name)

    await call.message.edit_text(text.finish())
    await call.answer(text=text.finish(), show_alert=True)

    for user_id in marked_users:
        amount, credits = get_credits_amount(call.from_user.id, user_id)
        info = []
        for credit in credits:
            info.append(credit.text_info)
        # markup = kb.get_check_markup(credit_id, True)
        try:
            await bot.send_message(
                user_id,
                Strings.ANNOUNCE_RETURN_CREDIT(amount, db.get_user(call.from_user.id).name, "\n".join(info)),
                # reply_markup=markup
            )
        except Exception:
            pass
    db.return_credits(returned_credits)


@dp.callback_query_handler(text_contains=CALLBACK.cancel_return_credits)
async def process_callback_credit_cancel(call: types.CallbackQuery) -> None:
    text = "\n".join(call.message.text.split("\n")[:-1])
    await call.message.edit_text(text)
    await call.answer()


@dp.callback_query_handler(text_contains=CALLBACK.check_return_approve)
async def process_callback_check_true(call: types.CallbackQuery) -> None:
    credit_id, value = kb.get_data_from_check(call.message.reply_markup)
    if value == "0":
        await call.message.edit_reply_markup(kb.get_check_markup(credit_id, True))
    await call.answer()


@dp.callback_query_handler(text_contains=CALLBACK.check_return_reject)
async def process_callback_check_false(call: types.CallbackQuery) -> None:
    credit_id, value = kb.get_data_from_check(call.message.reply_markup)
    if value == "1":
        await call.message.edit_reply_markup(kb.get_check_markup(credit_id, False))
    await call.answer()


@dp.callback_query_handler(text_contains=CALLBACK.check_return_of_credit)
async def process_callback_check(call: types.CallbackQuery) -> None:
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
            f"{credit.creditor.name} отметил, что ты не вернул {credit.get_amount()} руб.\n"
            f"{credit.get_text_info_new_line()}"
        )

        await bot.send_message(credit.from_id, message)


# ======================================= INFO =======================================
@dp.message_handler(check_user, text="info")
async def process_callback_credits_to_user(message: types.Message) -> None:
    credits_to_user = db.credits_to_user(message.from_user.id)

    if not credits_to_user:
        await message.answer(Strings.NO_CREDITS_CREDITOR, reply_markup=kb.main_markup)
        return

    text = Strings.CREDITOR_CREDITS_GENERATOR()
    credits_sum = 0
    credits_sum_by_user: Dict[int, int] = {}
    for i, credit in enumerate(credits_to_user, 1):
        credits_sum += credit.get_amount()
        credits_sum_by_user[credit.from_id] = (
                credits_sum_by_user.get(credit.from_id, 0) + credit.get_amount()
        )
        text.add_position(i, credit.get_amount(), credit.debtor.name, credit.text_info)

    for user_id, amount in credits_sum_by_user.items():
        text.add_sum(amount, db.get_user(user_id).name)

    await message.answer(text.finish(credits_sum), reply_markup=kb.main_markup)


dp.register_message_handler(read_num_from_user, check_user)


def main() -> None:
    logger.info("Starting bot")
    executor.start_polling(dp, skip_updates=True)
