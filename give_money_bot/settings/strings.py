from jinja2 import Template

from give_money_bot.db.models import User
from give_money_bot.settings.states import EditVisibilityData

EDIT_VISIBILITY_MESSAGE = """
Страница: {{ page }} / {{ page_total }}
"""

PROFILE_MESSAGE = """
Пользователь: {{ user.name }}
Номер: {{ user.phone_number }}
"""


class Strings:
    cancel = "Отмена"
    save = "Сохранить"
    saved = "Сохранено"
    menu_settings_answer = "Настройки"

    menu_add_new_user = "Добавить нового пользователя"
    ask_for_new_user = "Пришли алиас нового пользователя"
    new_user_added = "Пользователь добавлен"

    menu_edit_friendly_name = "Изменить имя пользователя"
    ask_for_new_friendly_name = "Пришли новое имя пользователя"

    menu_edit_number = "Изменить номер"
    ask_for_new_number = "Напиши мне номер, на который тебе надо возвращать долг. Так же можешь уточнить банк, на который надо отправлять деньги"

    menu_edit_visible_users = "Изменить видимость пользователей"

    left_emoji = "◀️"
    right_emoji = "▶️"
    vision_emojis = ["🟢", "🟡", "🔴"]

    edit_visibility_description = (
        "Здесь ты можешь изменить уровень видимости тобой других пользователей при добавлении долгов:\n"
        f"{vision_emojis[0]} - означает, что ты всегда будешь видеть этого пользователя\n"
        f"{vision_emojis[1]} - означает, что ты будешь видеть этого пользователя только после нажатия дополнительной кнопки \"Больше\"(Не реализовано)\n"
        f"{vision_emojis[2]} - означает, что ты никогда не будешь видеть данного пользователя\n"
    )
    menu_exit = "Назад"

    @staticmethod
    def edit_visibility_message(data: EditVisibilityData) -> str:
        return Template(EDIT_VISIBILITY_MESSAGE).render(page=data.page, page_total=data.pages_total)

    @staticmethod
    def profile_message(user: User) -> str:
        return Template(PROFILE_MESSAGE).render(user=user)
