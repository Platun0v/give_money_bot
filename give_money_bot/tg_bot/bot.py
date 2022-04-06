from typing import Optional, Dict, List, Any

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.middlewares import BaseMiddleware

from give_money_bot import config
from give_money_bot.db.db_connector import db
from give_money_bot.db.models import Credit, User
from give_money_bot.tg_bot import keyboards as kb
from give_money_bot.tg_bot.keyboards import CALLBACK
from give_money_bot.tg_bot.utils import (
    check_user,
    check_admin,
    get_info,
    get_credits_amount,
    parse_info_from_message,
    parse_expression,
)
from give_money_bot.utils.log import logger
from give_money_bot.utils.squeezer import squeeze
from give_money_bot.utils.strings import Strings


class UserMiddleware(BaseMiddleware):
    async def on_pre_process_message(
        self, message: types.Message, data: Dict[str, Any]
    ) -> None:
        data["user"] = db.get_user(message.from_user.id)

    async def on_pre_process_callback_query(
        self, callback_query: types.CallbackQuery, data: Dict[str, Any]
    ) -> None:
        data["user"] = db.get_user(callback_query.from_user.id)


bot = Bot(
    token=config.TOKEN
)  # Works fine without proxy (18.11.2020) , proxy=config.PROXY)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(UserMiddleware())


@dp.message_handler(check_user, commands=["start"])
async def process_start_command(message: types.Message, user: User) -> None:
    logger.info(f"{user.name=} started")
    await message.answer(Strings.HELLO_MESSAGE, reply_markup=kb.main_markup)


@dp.message_handler(check_user, commands=["id"])
async def get_id(message: types.Message, user: User) -> None:
    logger.info(f"{user.name=} asked for id")
    await message.answer(f"{message.from_user.id}")


@dp.message_handler(check_admin, commands=["sqz"])
async def squeeze_credits(message: Optional[types.Message], user: User) -> None:
    sqz_report = squeeze()
    logger.info(f"Squeezed {sqz_report=}")
    for e in sqz_report:
        chain = " -> ".join(map(lambda x: db.get_user(x.from_id).name, e.cycle))
        for edge in e.cycle:
            await bot.send_message(
                edge.from_id, Strings.removed_credit_chain(e.amount, chain)
            )


@dp.message_handler(check_admin, commands=["add_user"])
async def add_user(message: types.Message, user: User) -> None:
    _, user_id, name = message.text.split()
    logger.info(f"{user.name=} asked for adding user {user_id=} {name=}")
    db.add_user(user_id, name)
    await message.answer("Added user")


@dp.message_handler(check_admin, commands=["add_show_user"])
async def add_show_user(message: types.Message, user: User) -> None:
    lst = message.text.split()
    _, user_id, user_ids = lst[0], lst[1], lst[2:]
    logger.info(f"{user.name=} asked for adding show user {user_id=} {user_ids=}")
    db.add_show_users(user_id, user_ids)
    await message.answer("Added users for showing")


# ======================================= ADD CREDIT =======================================
async def read_num_from_user(message: types.Message, user: User) -> None:
    value_str, info = parse_info_from_message(message.text)
    logger.info(f"{user.name=} trying to add credit {value_str=} {info=}")
    value, err = parse_expression(value_str)
    if value is None:
        await message.answer(err)
        return
    if value == 0:
        await message.answer(Strings.NEED_NON_ZERO)
        return

    await message.answer(
        Strings.ask_for_debtors(value, info),
        reply_markup=kb.get_keyboard_users_for_credit(
            message.from_user.id, value, set()
        ),
    )
    logger.info(f"{user.name=} asked for debtors")


@dp.callback_query_handler(text_contains=CALLBACK.choose_user_for_credit)
async def process_callback(call: types.CallbackQuery, user: User) -> None:
    value, users = kb.get_data_from_markup(call.message.reply_markup)
    logger.info(f"{user.name=} chosing users for credit {call.data=}")
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
async def process_callback_save(call: types.CallbackQuery, user: User) -> None:
    value, users = kb.get_data_from_markup(call.message.reply_markup)
    logger.info(f"{user.name=} saving credit {call.data=}")
    if not users:
        await call.answer(text=Strings.FORGOT_CHOOSE)
        return

    info = get_info(call.message)
    await call.message.edit_text(
        Strings.credit_saved(value, [e.name for e in db.get_users(users)], info)
    )

    user_id = call.from_user.id
    if value < 0:
        db.add_entry_2(list(users), user_id, abs(value), info)
    else:
        db.add_entry(user_id, list(users), value, info)

    for user_ in users:
        try:  # Fixes not started conv with give_money_bot
            await bot.send_message(
                user_,
                Strings.announce_new_credit(value, user.name, info),
            )
        except Exception:
            pass
    logger.info(f"{user.name=} saved credit {value=} {users=}")
    await squeeze_credits(message=None)


@dp.callback_query_handler(text_contains=CALLBACK.cancel_crt_credit)
async def process_callback_cancel(call: types.CallbackQuery, user: User) -> None:
    logger.info(f"{user.name=} canceling credit creation")
    await call.message.edit_text(Strings.CANCEL)


# ======================================= REMOVE CREDIT =======================================
@dp.message_handler(check_user, text="-")
async def process_callback_user_credits(message: types.Message, user: User) -> None:
    user_credits = db.get_user_credits(message.from_user.id)
    logger.info(f"{user.name=} asking for credits")
    if not user_credits:
        await message.answer(Strings.NO_CREDITS_DEBTOR)
        return

    credits_sum = 0
    credits_sum_by_user: Dict[int, int] = {}
    for i, credit in enumerate(user_credits, 1):
        credits_sum += credit.get_amount()
        credits_sum_by_user[credit.to_id] = (
            credits_sum_by_user.get(credit.to_id, 0) + credit.get_amount()
        )

    await message.answer(
        Strings.debtor_credits(
            user_credits, credits_sum_by_user, credits_sum, db.get_user_ids_with_name()
        ),
        reply_markup=kb.get_credits_markup(credits_sum_by_user, set()),
    )


@dp.callback_query_handler(text_contains=CALLBACK.choose_credit_for_return)
async def process_callback_credit_chose(call: types.CallbackQuery, user: User) -> None:
    marked_users = kb.get_marked_credits(call.message.reply_markup)
    chosen_user_id = kb.get_credit_id(call.data)
    logger.info(f"{user.name=} chosing users to return credits {call.data=}")

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
async def process_callback_return_credit(call: types.CallbackQuery, user: User) -> None:
    marked_users = kb.get_marked_credits(call.message.reply_markup)
    logger.info(f"{user.name=} returning credits {call.data=}")

    if not marked_users:
        await call.answer(Strings.FORGOT_CHOOSE)
        return

    returned_credits: List[int] = []
    returned_credits_sum: Dict[int, int] = {}
    for user_id in marked_users:
        amount, credits = get_credits_amount(call.from_user.id, user_id)
        for credit in credits:
            returned_credits.append(credit.id)
        returned_credits_sum[user_id] = amount

    msg = Strings.returned_credit(returned_credits_sum, db.get_user_ids_with_name())
    await call.message.edit_text(msg)
    await call.answer(text=msg, show_alert=True)

    for user_id in marked_users:
        amount, credits = get_credits_amount(call.from_user.id, user_id)
        info = []
        for credit in credits:
            info.append(credit.text_info)
        # markup = kb.get_check_markup(credit_id, True)
        try:
            await bot.send_message(
                user_id,
                Strings.announce_returned_credit(
                    amount, db.get_user(call.from_user.id).name, "\n".join(info)
                ),
                # reply_markup=markup
            )
        except Exception:
            pass
    db.return_credits(returned_credits)
    logger.info(f"{user.name=} returned credits {returned_credits=}")


@dp.callback_query_handler(text_contains=CALLBACK.cancel_return_credits)
async def process_callback_credit_cancel(call: types.CallbackQuery, user: User) -> None:
    logger.info(f"{user.name=} canceling credit return")
    text = "\n".join(call.message.text.split("\n")[:-1])  # Remove last line
    await call.message.edit_text(text)
    await call.answer()


# ======================================= INFO =======================================
@dp.message_handler(check_user, text="info")
async def process_callback_credits_to_user(message: types.Message, user: User) -> None:
    credits_to_user = db.credits_to_user(message.from_user.id)
    logger.info(f"{user.name=} asking for credits to user")
    if not credits_to_user:
        await message.answer(Strings.NO_CREDITS_CREDITOR, reply_markup=kb.main_markup)
        return

    credits_sum = 0
    credits_sum_by_user: Dict[int, int] = {}
    for i, credit in enumerate(credits_to_user, 1):
        credits_sum += credit.get_amount()
        credits_sum_by_user[credit.from_id] = (
            credits_sum_by_user.get(credit.from_id, 0) + credit.get_amount()
        )

    await message.answer(
        Strings.creditor_credits(
            credits_to_user,
            credits_sum_by_user,
            credits_sum,
            db.get_user_ids_with_name(),
        ),
        reply_markup=kb.main_markup,
    )


dp.register_message_handler(
    read_num_from_user, check_user
)  # Добавляем последним, чтобы обрабатывать сообщение, как новый долг только, когда не прошло по остальным пунктам


def main() -> None:
    logger.info("Starting bot")
    executor.start_polling(dp, skip_updates=True)
