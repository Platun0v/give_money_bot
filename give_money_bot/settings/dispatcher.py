from math import ceil
from typing import Dict, List, cast

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage
from aiogram.types import CallbackQuery
from loguru import logger as log
from sqlalchemy.orm import Session

from give_money_bot.db import db_connector as db
from give_money_bot.db.models import ShowTypes, User
from give_money_bot.settings import keyboards as kb
from give_money_bot.settings.keyboards import EditVisibilityAction, EditVisibilityCallback
from give_money_bot.settings.states import PAGE_MAX_USERS, EditVisibilityData, EditVisibilityUser, SettingsStates
from give_money_bot.settings.strings import Strings
from give_money_bot.tg_bot.bot import send_main_menu
from give_money_bot.tg_bot.strings import Strings as tg_strings
from give_money_bot.utils.misc import CheckUser, get_state_data, update_state_data


# ======================================= SETTINGS MENU =======================================
async def send_settings_menu(message: types.Message, state: FSMContext, user: User) -> None:
    await state.set_state(SettingsStates.settings)
    await message.answer(Strings.profile_message(user))
    await message.answer(Strings.menu_settings_answer, reply_markup=kb.settings_markup)


async def exit_settings_menu(message: types.Message, state: FSMContext, user: User) -> SendMessage:
    await state.clear()
    return await send_main_menu(message, user)


# ======================================= ADD USER =======================================
async def ask_for_new_user(message: types.Message, state: FSMContext, user: User) -> None:
    await state.set_state(SettingsStates.new_user)
    await message.answer(Strings.ask_for_new_user, reply_markup=types.ReplyKeyboardRemove())


async def add_new_user(message: types.Message, state: FSMContext, user: User) -> None:
    await state.set_state(SettingsStates.settings)
    await message.answer(Strings.new_user_added, reply_markup=kb.settings_markup)


# ======================================= EDIT NUMBER =======================================
async def ask_for_new_number(message: types.Message, state: FSMContext, user: User) -> None:
    await state.set_state(SettingsStates.edit_number)
    await message.answer(Strings.ask_for_new_number, reply_markup=types.ReplyKeyboardRemove())


async def save_new_number(message: types.Message, state: FSMContext, user: User, session: Session) -> None:
    if message.text is not None:
        db.change_phone(session, user, message.text)
    else:
        await message.answer(Strings.number_not_found)
        return

    await state.set_state(SettingsStates.settings)
    await message.answer(Strings.saved, reply_markup=kb.settings_markup)


# ======================================= EDIT USER VISIBILITY =======================================
async def edit_user_visibility(message: types.Message, session: Session, state: FSMContext, user: User) -> None:
    await state.set_state(SettingsStates.edit_visibility)

    users = db.get_all_users_without_current_user(session, user.user_id)
    user_visions = db.get_user_visions(session, user.user_id)
    edit_visibility_users: Dict[int, EditVisibilityUser] = {}
    users_list: List[int] = []
    for user_e in users:
        edit_visibility_users[user_e.user_id] = EditVisibilityUser(username=user_e.name, vision=ShowTypes.NEVER)
        users_list.append(user_e.user_id)
    for user_vision in user_visions:
        edit_visibility_users[user_vision.show_user_id].vision = cast(ShowTypes, user_vision.show_type)

    pages = ceil(len(edit_visibility_users) / PAGE_MAX_USERS)
    edit_visibility_data = EditVisibilityData(
        users=edit_visibility_users, users_list=users_list, page=1, pages_total=pages
    )

    await update_state_data(state, SettingsStates.edit_visibility, edit_visibility_data)
    await message.answer(Strings.edit_visibility_description)
    await message.answer(
        text=Strings.edit_visibility_message(edit_visibility_data),
        reply_markup=kb.create_edit_visibility_keyboard(edit_visibility_data),
    )


async def edit_user_visibility_user_click(
    call: CallbackQuery, state: FSMContext, callback_data: EditVisibilityCallback
) -> None:
    edit_visibility_data = await get_state_data(state, SettingsStates.edit_visibility, EditVisibilityData)
    if edit_visibility_data is None:
        log.error("edit_user_visibility_user_click: edit_visibility_data is None")
        return

    edit_visibility_data.users[callback_data.user_id].vision = cast(
        ShowTypes, (edit_visibility_data.users[callback_data.user_id].vision + 1) % 3
    )

    await update_state_data(state, SettingsStates.edit_visibility, edit_visibility_data)
    await call.message.edit_text(
        text=Strings.edit_visibility_message(edit_visibility_data),
        reply_markup=kb.create_edit_visibility_keyboard(edit_visibility_data),
    )
    await call.answer()


async def edit_user_visibility_left_click(call: CallbackQuery, state: FSMContext) -> None:
    edit_visibility_data = await get_state_data(state, SettingsStates.edit_visibility, EditVisibilityData)
    if edit_visibility_data is None:
        log.error("edit_user_visibility_left_click: edit_visibility_data is None")
        return

    edit_visibility_data.page = edit_visibility_data.page - 1
    if edit_visibility_data.page == 0:
        edit_visibility_data.page = edit_visibility_data.pages_total

    await update_state_data(state, SettingsStates.edit_visibility, edit_visibility_data)
    await call.message.edit_text(
        text=Strings.edit_visibility_message(edit_visibility_data),
        reply_markup=kb.create_edit_visibility_keyboard(edit_visibility_data),
    )
    await call.answer()


async def edit_user_visibility_right_click(call: CallbackQuery, state: FSMContext) -> None:
    edit_visibility_data = await get_state_data(state, SettingsStates.edit_visibility, EditVisibilityData)
    if edit_visibility_data is None:
        log.error("edit_user_visibility_right_click: edit_visibility_data is None")
        return

    edit_visibility_data.page = edit_visibility_data.page + 1
    if edit_visibility_data.page > edit_visibility_data.pages_total:
        edit_visibility_data.page = 1

    await update_state_data(state, SettingsStates.edit_visibility, edit_visibility_data)
    await call.message.edit_text(
        text=Strings.edit_visibility_message(edit_visibility_data),
        reply_markup=kb.create_edit_visibility_keyboard(edit_visibility_data),
    )
    await call.answer()


async def edit_user_visibility_cancel_click(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SettingsStates.settings)
    await update_state_data(state, SettingsStates.edit_visibility, None)
    await call.message.edit_text(text=Strings.cancel)


async def edit_user_visibility_save_click(call: CallbackQuery, user: User, session: Session, state: FSMContext) -> None:
    edit_visibility_data = await get_state_data(state, SettingsStates.edit_visibility, EditVisibilityData)

    for user_id in edit_visibility_data.users_list:
        db.update_user_vision(
            session,
            user_id=user.user_id,
            show_user_id=user_id,
            show_type=edit_visibility_data.users[user_id].vision,
        )

    await state.set_state(SettingsStates.settings)
    await update_state_data(state, SettingsStates.edit_visibility, None)
    await call.message.edit_text(text=Strings.saved)


# ======================================= ROUTER =======================================
router = Router()
router.message.bind_filter(CheckUser)

# ======================================= SETTINGS MENU =======================================
router.message.register(send_settings_menu, F.text == tg_strings.menu_settings)
router.message.register(
    exit_settings_menu,
    SettingsStates.settings,
    F.text == Strings.menu_exit,
)

# ======================================= ADD USER =======================================
router.message.register(
    ask_for_new_user,
    SettingsStates.settings,
    F.text == Strings.menu_add_new_user,
)
router.message.register(add_new_user, SettingsStates.new_user)

# ======================================= EDIT USER VISIBILITY =======================================
router.message.register(edit_user_visibility, SettingsStates.settings, F.text == Strings.menu_edit_visible_users)
router.callback_query.register(
    edit_user_visibility_user_click,
    EditVisibilityCallback.filter(F.action == EditVisibilityAction.user),
)
router.callback_query.register(
    edit_user_visibility_right_click,
    EditVisibilityCallback.filter(F.action == EditVisibilityAction.right),
)
router.callback_query.register(
    edit_user_visibility_left_click,
    EditVisibilityCallback.filter(F.action == EditVisibilityAction.left),
)
router.callback_query.register(
    edit_user_visibility_cancel_click,
    EditVisibilityCallback.filter(F.action == EditVisibilityAction.cancel),
)
router.callback_query.register(
    edit_user_visibility_save_click,
    EditVisibilityCallback.filter(F.action == EditVisibilityAction.save),
)

# ======================================= EDIT NUMBER =======================================
router.message.register(ask_for_new_number, SettingsStates.settings, F.text == Strings.menu_edit_number)
router.message.register(save_new_number, SettingsStates.edit_number)

# ======================================= EXIT =======================================
router.message.register(exit_settings_menu, SettingsStates.settings)  # If user sends random message, go back to menu
