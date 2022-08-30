from typing import Dict, List, Optional

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from loguru import logger as log
from sqlalchemy.orm import Session

from give_money_bot.credits import keyboards as kb
from give_money_bot.credits.callback import (
    AddCreditAction,
    AddCreditCallback,
    ReturnCreditsAction,
    ReturnCreditsCallback,
)
from give_money_bot.credits.squeezer import squeeze
from give_money_bot.credits.states import AddCreditData, CreditStates, ReturnCreditsData
from give_money_bot.credits.strings import Strings
from give_money_bot.credits.utils import get_credits_amount, parse_expression, parse_info_from_message
from give_money_bot.db import db_connector as db
from give_money_bot.db.models import User
from give_money_bot.tg_bot.keyboards import main_keyboard
from give_money_bot.tg_bot.strings import Strings as tg_strings
from give_money_bot.utils.misc import CheckUser, get_state_data, update_state_data


async def prc_squeeze_credits(message: Optional[types.Message], bot: Bot, session: Session, user: User) -> None:
    sqz_report = squeeze(session)
    log.info(f"Squeezed {sqz_report=}")
    for e in sqz_report:
        chain = " -> ".join(map(lambda x: db.get_user(session, x.from_id).name, e.cycle))
        for edge in e.cycle:
            try:
                await bot.send_message(edge.from_id, Strings.removed_credit_chain(e.amount, chain))
            except Exception:
                log.error(f"Cant send message to {db.get_user(session, edge.from_id).name=}")


# ======================================= ADD CREDIT =======================================
async def read_num_from_user(message: types.Message, bot: Bot, state: FSMContext, user: User, session: Session) -> None:
    add_credit_data = await get_state_data(state, CreditStates.add_credit, AddCreditData)
    if add_credit_data is not None:  # If we already have some data, cancel prev add credit
        await update_state_data(state, CreditStates.add_credit, None)
        await bot.edit_message_text(
            chat_id=message.chat.id, message_id=add_credit_data.message_id, text=Strings.CANCEL, reply_markup=None
        )

    log.info(f"{message.text=}")
    value_str, info = "", ""
    if message.text is not None:
        value_str, info = parse_info_from_message(message.text)

    log.info(f"{user.name=} trying to add credit {value_str=} {info=}")
    value, err = parse_expression(value_str)
    if err is not None:
        await message.answer(err, reply_markup=main_keyboard)
        return
    if value == 0:
        await message.answer(Strings.NEED_NON_ZERO)
        return

    add_credit_data = AddCreditData(
        amount=value, message=info, users=set(), show_more=False, message_id=message.message_id
    )

    msg = await message.answer(
        Strings.ask_for_debtors(value, info),
        reply_markup=kb.get_keyboard_add_credit(message.from_user.id, add_credit_data, session),
    )

    add_credit_data.message_id = msg.message_id  # We need message_id of sent message
    await update_state_data(state, CreditStates.add_credit, add_credit_data)

    log.info(f"{user.name=} asked for debtors")


async def prc_callback_choose_users_for_credit(
    call: types.CallbackQuery, callback_data: AddCreditCallback, user: User, session: Session, state: FSMContext
) -> None:
    add_credit_data = await get_state_data(state, CreditStates.add_credit, AddCreditData)
    if add_credit_data is None:
        log.error(f"{user.name=} trying to add credit without data")
        return
    if add_credit_data.message_id != call.message.message_id:
        return

    log.info(f"{user.name=} chosing users for credit {db.get_user(session, callback_data.user_id).name=}")

    if callback_data.user_id in add_credit_data.users:
        add_credit_data.users.remove(callback_data.user_id)
    else:
        add_credit_data.users.add(callback_data.user_id)

    await update_state_data(state, CreditStates.add_credit, add_credit_data)

    await call.message.edit_reply_markup(
        reply_markup=kb.get_keyboard_add_credit(call.from_user.id, add_credit_data, session)
    )
    await call.answer()


async def prc_callback_show_more_users(
    call: types.CallbackQuery, callback_data: AddCreditCallback, user: User, session: Session, state: FSMContext
) -> None:
    add_credit_data = await get_state_data(state, CreditStates.add_credit, AddCreditData)
    if add_credit_data is None:
        log.error(f"{user.name=} trying to add credit without data")
        return
    if add_credit_data.message_id != call.message.message_id:
        return

    add_credit_data.show_more = not add_credit_data.show_more

    await update_state_data(state, CreditStates.add_credit, add_credit_data)

    await call.message.edit_reply_markup(
        reply_markup=kb.get_keyboard_add_credit(call.from_user.id, add_credit_data, session)
    )
    await call.answer()


async def prc_callback_save_new_credit(
    call: types.CallbackQuery, bot: Bot, user: User, session: Session, state: FSMContext
) -> None:
    add_credit_data = await get_state_data(state, CreditStates.add_credit, AddCreditData)
    if add_credit_data is None:
        log.error(f"{user.name=} trying to add credit without data")
        return
    if add_credit_data.message_id != call.message.message_id:
        return

    users = add_credit_data.users
    if not add_credit_data.show_more:  # If we dont show more users, we need to remove additional users
        users = users & set(map(lambda x: x.user_id, db.get_users_with_show_always(session, user.user_id)))

    log.info(f"{user.name=} saving credit {add_credit_data=}")
    if not users:
        await call.answer(text=Strings.FORGOT_CHOOSE)
        return

    await call.message.edit_text(
        Strings.credit_saved(
            add_credit_data.amount, [e.name for e in db.get_users(session, users)], add_credit_data.message
        )
    )

    user_id = call.from_user.id
    if add_credit_data.amount < 0:
        db.add_entry_2(session, list(users), user_id, abs(add_credit_data.amount), add_credit_data.message)
    else:
        db.add_entry(session, user_id, list(users), add_credit_data.amount, add_credit_data.message)

    for user_ in users:
        try:  # Fixes not started conv with give_money_bot
            await bot.send_message(
                user_,
                Strings.announce_new_credit(add_credit_data.amount, user.name, add_credit_data.message),
            )
        except Exception:
            pass

    await update_state_data(state, CreditStates.add_credit)
    log.info(f"{user.name=} saved credit {add_credit_data.amount=} {users=}")
    await prc_squeeze_credits(bot=bot, session=session, message=None, user=user)


async def prc_callback_cancel_create_credit(call: types.CallbackQuery, bot: Bot, user: User, state: FSMContext) -> None:
    log.info(f"{user.name=} canceling credit creation")
    await update_state_data(state, CreditStates.add_credit)
    await call.message.edit_text(Strings.CANCEL)
    await bot.send_message(user.user_id, "Menu", reply_markup=main_keyboard)


# ======================================= RETURN CREDITS =======================================
async def prc_user_credits(message: types.Message, bot: Bot, user: User, session: Session, state: FSMContext) -> None:
    user_credits = db.get_user_credits(session, message.from_user.id)
    log.info(f"{user.name=} asking for credits")
    if not user_credits:
        await message.answer(Strings.NO_CREDITS_DEBTOR)
        return

    state_data = await state.get_data()
    return_credits_json: Optional[str] = state_data.get("return_credits")

    if return_credits_json is not None:  # If we already have some data, cancel prev add credit
        return_credit_data: ReturnCreditsData = ReturnCreditsData.parse_raw(return_credits_json)
        await update_state_data(state, CreditStates.return_credit)
        await bot.edit_message_text(
            text=Strings.CANCEL, chat_id=message.chat.id, message_id=return_credit_data.message_id, reply_markup=None
        )

    credits_sum = 0
    credits_sum_by_user: Dict[int, int] = {}
    for i, credit in enumerate(user_credits, 1):
        credits_sum += credit.get_amount()
        credits_sum_by_user[credit.to_id] = credits_sum_by_user.get(credit.to_id, 0) + credit.get_amount()

    return_credits_data = ReturnCreditsData(users=set(), message_id=0)

    msg = await message.answer(
        Strings.debtor_credits(user_credits, credits_sum_by_user, credits_sum, db.get_user_ids_with_users(session)),
        reply_markup=kb.get_credits_markup(credits_sum_by_user, return_credits_data, session),
    )

    return_credits_data.message_id = msg.message_id
    await update_state_data(state, CreditStates.return_credit, return_credits_data)


async def prc_callback_choose_credit_for_return(
    call: types.CallbackQuery, callback_data: ReturnCreditsCallback, user: User, session: Session, state: FSMContext
) -> None:
    return_credits_data = await get_state_data(state, CreditStates.return_credit, ReturnCreditsData)
    if return_credits_data is None:
        log.error(f"{user.name=} trying to return credits without data")
        return
    if return_credits_data.message_id != call.message.message_id:
        return

    chosen_user_id = callback_data.user_id
    log.info(f"{user.name=} chosing users to return credits {chosen_user_id=}")

    if chosen_user_id in return_credits_data.users:
        return_credits_data.users.remove(chosen_user_id)
    else:
        return_credits_data.users.add(chosen_user_id)

    await update_state_data(state, CreditStates.return_credit, return_credits_data)

    credits_sum_by_user: Dict[int, int] = {}
    for credit in db.get_user_credits(session, call.from_user.id):
        credits_sum_by_user[credit.to_id] = credits_sum_by_user.get(credit.to_id, 0) + credit.get_amount()

    await call.message.edit_reply_markup(
        reply_markup=kb.get_credits_markup(credits_sum_by_user, return_credits_data, session)
    )
    await call.answer()


async def prc_callback_return_credits(
    call: types.CallbackQuery, bot: Bot, user: User, session: Session, state: FSMContext
) -> None:
    return_credits_data = await get_state_data(state, CreditStates.return_credit, ReturnCreditsData)
    if return_credits_data is None:
        log.error(f"{user.name=} trying to return credits without any data")
        return
    if return_credits_data.message_id != call.message.message_id:
        return

    log.info(f"{user.name=} returning credits {return_credits_data=}")

    if not return_credits_data.users:
        await call.answer(Strings.FORGOT_CHOOSE)
        return

    returned_credits: List[int] = []
    returned_credits_sum: Dict[int, int] = {}

    for user_id in return_credits_data.users:
        amount, credits = get_credits_amount(call.from_user.id, user_id, session)
        for credit in credits:
            returned_credits.append(credit.id)
        returned_credits_sum[user_id] = amount

    msg = Strings.returned_credit(returned_credits_sum, db.get_user_ids_with_name(session))
    await call.message.edit_text(msg)
    await call.answer(text=msg, show_alert=True)

    for user_id in return_credits_data.users:
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
    log.info(f"{user.name=} returned credits {returned_credits=}")


async def prc_callback_cancel_return_credit(call: types.CallbackQuery, user: User, state: FSMContext) -> None:
    await update_state_data(state, CreditStates.return_credit)
    log.info(f"{user.name=} canceling credit return")
    text = "\n".join(call.message.text.split("\n")[:-1])  # Remove last line
    await call.message.edit_text(text)
    await call.answer()


# ======================================= INFO =======================================
async def prc_user_debtors(message: types.Message, user: User, session: Session) -> None:
    credits_to_user = db.credits_to_user(session, message.from_user.id)
    log.info(f"{user.name=} asking for credits to user")
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

# ======================================= ADD CREDIT =======================================
router.callback_query.register(
    prc_callback_choose_users_for_credit,
    AddCreditCallback.filter(F.action == AddCreditAction.choose_user),
)
router.callback_query.register(
    prc_callback_show_more_users, AddCreditCallback.filter(F.action == AddCreditAction.show_more)
)
router.callback_query.register(prc_callback_save_new_credit, AddCreditCallback.filter(F.action == AddCreditAction.save))
router.callback_query.register(
    prc_callback_cancel_create_credit, AddCreditCallback.filter(F.action == AddCreditAction.cancel)
)

# ======================================= RETURN CREDITS =======================================
router.message.register(prc_user_credits, F.text == tg_strings.menu_credits)
router.callback_query.register(
    prc_callback_choose_credit_for_return,
    ReturnCreditsCallback.filter(F.action == ReturnCreditsAction.choose_user),
)
router.callback_query.register(
    prc_callback_return_credits,
    ReturnCreditsCallback.filter(F.action == ReturnCreditsAction.save),
)
router.callback_query.register(
    prc_callback_cancel_return_credit, ReturnCreditsCallback.filter(F.action == ReturnCreditsAction.cancel)
)

# ======================================= INFO =======================================
router.message.register(prc_user_debtors, F.text == tg_strings.menu_debtors)

# ======================================= ADD CREDIT =======================================
router.message.register(
    read_num_from_user, state=None
)  # Добавляем последним, чтобы обрабатывать сообщение, как новый долг только, когда не прошло по остальным пунктам
