from math import ceil
from typing import Dict, List, cast

from aiogram import F, Router, types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.orm import Session

from give_money_bot.db import db_connector as db
from give_money_bot.db.models import ShowTypes, User
from give_money_bot.settings import keyboards as kb
from give_money_bot.settings.keyboards import Action, EditVisibilityCallback
from give_money_bot.settings.states import (
    PAGE_MAX_USERS,
    EditVisibilityData,
    EditVisibilityUser,
    SettingsStates,
)
from give_money_bot.settings.strings import Strings
from give_money_bot.tg_bot.bot import send_main_menu
from give_money_bot.tg_bot.strings import Strings as tg_strings
from give_money_bot.utils.misc import CheckUser


async def send_settings_menu(
    message: types.Message, state: FSMContext, user: User
) -> None:
    await state.set_state(SettingsStates.settings)
    await message.answer(Strings.menu_settings_answer, reply_markup=kb.settings_markup)


async def ask_for_new_user(
    message: types.Message, state: FSMContext, user: User
) -> None:
    await state.set_state(SettingsStates.new_user)
    await message.answer(
        Strings.ask_for_new_user, reply_markup=types.ReplyKeyboardRemove()
    )


async def add_new_user(message: types.Message, state: FSMContext, user: User) -> None:
    await state.set_state(SettingsStates.settings)
    await message.answer(Strings.new_user_added, reply_markup=kb.settings_markup)


async def exit_settings_menu(
    message: types.Message, state: FSMContext, user: User
) -> None:
    await state.clear()
    await send_main_menu(message, user)


async def edit_user_visibility(
    message: types.Message, session: Session, state: FSMContext, user: User
) -> None:
    await state.set_state(SettingsStates.edit_visibility)

    users = db.get_all_users_without_current_user(session, user.user_id)
    user_visions = db.get_user_visions(session, user.user_id)
    edit_visibility_users: Dict[int, EditVisibilityUser] = {}
    users_list: List[int] = []
    for user_e in users:
        edit_visibility_users[user_e.user_id] = EditVisibilityUser(
            username=user_e.name, vision=ShowTypes.NEVER
        )
        users_list.append(user_e.user_id)
    for user_vision in user_visions:
        edit_visibility_users[user_vision.show_user_id].vision = cast(
            ShowTypes, user_vision.show_type
        )

    pages = ceil(len(edit_visibility_users) / PAGE_MAX_USERS)
    edit_visibility_data = EditVisibilityData(
        users=edit_visibility_users, users_list=users_list, page=1, pages_total=pages
    )

    await state.update_data(edit_visibility=edit_visibility_data.json())
    await message.answer(Strings.edit_visibility_description)
    await message.answer(
        text=Strings.edit_visibility_message(edit_visibility_data),
        reply_markup=kb.create_edit_visibility_keyboard(edit_visibility_data),
    )


async def edit_user_visibility_user_click(
    call: CallbackQuery, state: FSMContext, callback_data: EditVisibilityCallback
) -> None:
    state_data = await state.get_data()
    edit_visibility_data: EditVisibilityData = EditVisibilityData.parse_raw(
        state_data.get("edit_visibility")
    )

    edit_visibility_data.users[callback_data.user_id].vision = cast(
        ShowTypes, (edit_visibility_data.users[callback_data.user_id].vision + 1) % 3
    )

    await state.update_data(edit_visibility=edit_visibility_data.json())
    await call.message.edit_text(
        text=Strings.edit_visibility_message(edit_visibility_data),
        reply_markup=kb.create_edit_visibility_keyboard(edit_visibility_data),
    )
    await call.answer()


async def edit_user_visibility_left_click(
    call: CallbackQuery, state: FSMContext
) -> None:
    state_data = await state.get_data()
    edit_visibility_data: EditVisibilityData = EditVisibilityData.parse_raw(
        state_data.get("edit_visibility")
    )

    edit_visibility_data.page = edit_visibility_data.page - 1
    if edit_visibility_data.page == 0:
        edit_visibility_data.page = edit_visibility_data.pages_total

    await state.update_data(edit_visibility=edit_visibility_data.json())
    await call.message.edit_text(
        text=Strings.edit_visibility_message(edit_visibility_data),
        reply_markup=kb.create_edit_visibility_keyboard(edit_visibility_data),
    )
    await call.answer()


async def edit_user_visibility_right_click(
    call: CallbackQuery, state: FSMContext
) -> None:
    state_data = await state.get_data()
    edit_visibility_data: EditVisibilityData = EditVisibilityData.parse_raw(
        state_data.get("edit_visibility")
    )

    edit_visibility_data.page = edit_visibility_data.page + 1
    if edit_visibility_data.page > edit_visibility_data.pages_total:
        edit_visibility_data.page = 1

    await state.update_data(edit_visibility=edit_visibility_data.json())
    await call.message.edit_text(
        text=Strings.edit_visibility_message(edit_visibility_data),
        reply_markup=kb.create_edit_visibility_keyboard(edit_visibility_data),
    )
    await call.answer()


async def edit_user_visibility_cancel_click(
    call: CallbackQuery, state: FSMContext
) -> None:
    await state.set_state(SettingsStates.settings)
    await state.update_data(edit_visibility=None)
    await call.message.edit_text(text=Strings.cancel)


async def edit_user_visibility_save_click(
    call: CallbackQuery, session: Session, state: FSMContext
) -> None:
    state_data = await state.get_data()
    edit_visibility_data: EditVisibilityData = EditVisibilityData.parse_raw(
        state_data.get("edit_visibility")
    )

    for user in edit_visibility_data.users_list:
        db.update_user_vision(
            session,
            user_id=call.from_user.id,
            show_user_id=user,
            show_type=edit_visibility_data.users[user].vision,
        )

    await state.set_state(SettingsStates.settings)
    await state.update_data(edit_visibility=None)
    await call.message.edit_text(text=Strings.saved)


router = Router()
router.message.bind_filter(CheckUser)

router.message.register(send_settings_menu, text=tg_strings.menu_settings)
router.message.register(
    exit_settings_menu,
    SettingsStates.settings,
    text=Strings.menu_exit,
)
router.message.register(
    ask_for_new_user,
    SettingsStates.settings,
    text=Strings.menu_add_new_user,
)
router.message.register(add_new_user, SettingsStates.new_user)
router.message.register(
    edit_user_visibility, SettingsStates.settings, text=Strings.menu_edit_visible_users
)
router.callback_query.register(
    edit_user_visibility_user_click,
    EditVisibilityCallback.filter(F.action == Action.user),
)
router.callback_query.register(
    edit_user_visibility_right_click,
    EditVisibilityCallback.filter(F.action == Action.right),
)
router.callback_query.register(
    edit_user_visibility_left_click,
    EditVisibilityCallback.filter(F.action == Action.left),
)
router.callback_query.register(
    edit_user_visibility_cancel_click,
    EditVisibilityCallback.filter(F.action == Action.cancel),
)
router.callback_query.register(
    edit_user_visibility_save_click,
    EditVisibilityCallback.filter(F.action == Action.save),
)
