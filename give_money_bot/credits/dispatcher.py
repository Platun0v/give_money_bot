from typing import Dict, List, Optional

from aiogram import Router, types
from sqlalchemy.orm import Session

from give_money_bot import bot, dp
from give_money_bot.credits import keyboards as kb
from give_money_bot.credits.callback_data import CALLBACK
from give_money_bot.credits.keyboards import CreditChooseData, UserChooseData
from give_money_bot.credits.squeezer import squeeze
from give_money_bot.credits.strings import Strings
from give_money_bot.credits.utils import get_credits_amount, get_info, parse_expression, parse_info_from_message
from give_money_bot.db import db_connector as db
from give_money_bot.db.models import User
from give_money_bot.tg_bot.keyboards import main_keyboard
from give_money_bot.tg_bot.strings import Strings as tg_strings
from give_money_bot.utils.log import logger
from give_money_bot.utils.misc import CheckUser


async def prc_squeeze_credits(message: Optional[types.Message], session: Session, user: User) -> None:
    sqz_report = squeeze(session)
    logger.info(f"Squeezed {sqz_report=}")
    for e in sqz_report:
        chain = " -> ".join(map(lambda x: db.get_user(session, x.from_id).name, e.cycle))
        for edge in e.cycle:
            await bot.send_message(edge.from_id, Strings.removed_credit_chain(e.amount, chain))


# ======================================= ADD CREDIT =======================================
async def read_num_from_user(message: types.Message, user: User, session: Session) -> None:
    logger.info(f"{message.text=}")
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
            message.from_user.id, value, set(), db.get_users_with_show_always(session, User.user_id), session
        ),
    )
    logger.info(f"{user.name=} asked for debtors")


async def prc_callback_choose_users_for_credit(
    call: types.CallbackQuery, callback_data: UserChooseData, user: User, session: Session
) -> None:
    value, users = kb.get_data_from_markup(call.message.reply_markup)
    logger.info(f"{user.name=} chosing users for credit {call.data=}")
    user_id = callback_data.user_id

    if user_id in users:
        users.remove(user_id)
    else:
        users.add(user_id)

    await call.message.edit_reply_markup(
        reply_markup=kb.get_keyboard_users_for_credit(
            call.from_user.id, value, users, db.get_users_with_show_always(User.user_id), session
        )
    )
    await call.answer()


async def prc_callback_save_new_credit(call: types.CallbackQuery, user: User, session: Session) -> None:
    value, users = kb.get_data_from_markup(call.message.reply_markup)
    logger.info(f"{user.name=} saving credit {call.data=}")
    if not users:
        await call.answer(text=Strings.FORGOT_CHOOSE)
        return

    info = get_info(call.message)
    await call.message.edit_text(Strings.credit_saved(value, [e.name for e in db.get_users(session, users)], info))

    user_id = call.from_user.id
    if value < 0:
        db.add_entry_2(session, list(users), user_id, abs(value), info)
    else:
        db.add_entry(session, user_id, list(users), value, info)

    for user_ in users:
        try:  # Fixes not started conv with give_money_bot
            await bot.send_message(
                user_,
                Strings.announce_new_credit(value, user.name, info),
            )
        except Exception:
            pass
    logger.info(f"{user.name=} saved credit {value=} {users=}")
    await prc_squeeze_credits(session=session, message=None, user=user)


async def prc_callback_cancel_create_credit(call: types.CallbackQuery, user: User) -> None:
    logger.info(f"{user.name=} canceling credit creation")
    await call.message.edit_text(Strings.CANCEL)


# ======================================= REMOVE CREDIT =======================================
async def prc_user_credits(message: types.Message, user: User, session: Session) -> None:
    user_credits = db.get_user_credits(session, message.from_user.id)
    logger.info(f"{user.name=} asking for credits")
    if not user_credits:
        await message.answer(Strings.NO_CREDITS_DEBTOR)
        return

    credits_sum = 0
    credits_sum_by_user: Dict[int, int] = {}
    for i, credit in enumerate(user_credits, 1):
        credits_sum += credit.get_amount()
        credits_sum_by_user[credit.to_id] = credits_sum_by_user.get(credit.to_id, 0) + credit.get_amount()

    await message.answer(
        Strings.debtor_credits(user_credits, credits_sum_by_user, credits_sum, db.get_user_ids_with_name(session)),
        reply_markup=kb.get_credits_markup(credits_sum_by_user, set(), session),
    )


async def prc_callback_choose_credit_for_return(
    call: types.CallbackQuery, callback_data: CreditChooseData, user: User, session: Session
) -> None:
    marked_users = kb.get_marked_credits(call.message.reply_markup)
    chosen_user_id = callback_data.index
    logger.info(f"{user.name=} chosing users to return credits {call.data=}")

    if chosen_user_id in marked_users:
        marked_users.remove(chosen_user_id)
    else:
        marked_users.add(chosen_user_id)

    credits_sum_by_user: Dict[int, int] = {}
    for credit in db.get_user_credits(session, call.from_user.id):
        credits_sum_by_user[credit.to_id] = credits_sum_by_user.get(credit.to_id, 0) + credit.get_amount()

    await call.message.edit_reply_markup(reply_markup=kb.get_credits_markup(credits_sum_by_user, marked_users, session))
    await call.answer()


async def prc_callback_return_credits(call: types.CallbackQuery, user: User, session: Session) -> None:
    marked_users = kb.get_marked_credits(call.message.reply_markup)
    logger.info(f"{user.name=} returning credits {call.data=}")

    if not marked_users:
        await call.answer(Strings.FORGOT_CHOOSE)
        return

    returned_credits: List[int] = []
    returned_credits_sum: Dict[int, int] = {}

    for user_id in marked_users:
        amount, credits = get_credits_amount(call.from_user.id, user_id, session)
        for credit in credits:
            returned_credits.append(credit.id)
        returned_credits_sum[user_id] = amount

    msg = Strings.returned_credit(returned_credits_sum, db.get_user_ids_with_name(session))
    await call.message.edit_text(msg)
    await call.answer(text=msg, show_alert=True)

    for user_id in marked_users:
        amount, credits = get_credits_amount(call.from_user.id, user_id, session)
        info = []
        for credit in credits:
            info.append(credit.text_info)
        # markup = kb.get_check_markup(credit_id, True)
        try:
            await bot.send_message(
                user_id,
                Strings.announce_returned_credit(amount, db.get_user(session, call.from_user.id).name, "\n".join(info)),
                # reply_markup=markup
            )
        except Exception:
            pass
    db.return_credits(session, returned_credits)
    logger.info(f"{user.name=} returned credits {returned_credits=}")


async def prc_callback_cancel_return_credit(call: types.CallbackQuery, user: User) -> None:
    logger.info(f"{user.name=} canceling credit return")
    text = "\n".join(call.message.text.split("\n")[:-1])  # Remove last line
    await call.message.edit_text(text)
    await call.answer()


# ======================================= INFO =======================================
async def prc_user_debtors(message: types.Message, user: User, session: Session) -> None:
    credits_to_user = db.credits_to_user(session, message.from_user.id)
    logger.info(f"{user.name=} asking for credits to user")
    if not credits_to_user:
        await message.answer(Strings.NO_CREDITS_CREDITOR, reply_markup=main_keyboard)
        return

    credits_sum = 0
    credits_sum_by_user: Dict[int, int] = {}
    for i, credit in enumerate(credits_to_user, 1):
        credits_sum += credit.get_amount()
        credits_sum_by_user[credit.from_id] = credits_sum_by_user.get(credit.from_id, 0) + credit.get_amount()

    await message.answer(
        Strings.creditor_credits(
            credits_to_user,
            credits_sum_by_user,
            credits_sum,
            db.get_user_ids_with_name(session),
        ),
        reply_markup=main_keyboard,
    )


router = Router()
router.message.bind_filter(CheckUser)

# router.message.register(prc_squeeze_credits, commands=["sqz"])

router.callback_query.register(
    prc_callback_choose_users_for_credit,
    UserChooseData.filter(),
    # text_contains=CALLBACK.choose_users_for_credit,
)
router.callback_query.register(prc_callback_save_new_credit, text_contains=CALLBACK.save_new_credit)
router.callback_query.register(prc_callback_cancel_create_credit, text_contains=CALLBACK.cancel_create_credit)

router.message.register(prc_user_credits, text=tg_strings.menu_credits)
router.callback_query.register(
    prc_callback_choose_credit_for_return,
    CreditChooseData.filter(),
    # text_contains=CALLBACK.choose_credit_for_return,
)
router.callback_query.register(
    prc_callback_return_credits,
    text_contains=CALLBACK.return_credits,
)
router.callback_query.register(prc_callback_cancel_return_credit, text_contains=CALLBACK.cancel_return_credits)

router.message.register(prc_user_debtors, text=tg_strings.menu_debtors)

router.message.register(
    read_num_from_user
)  # Добавляем последним, чтобы обрабатывать сообщение, как новый долг только, когда не прошло по остальным пунктам
