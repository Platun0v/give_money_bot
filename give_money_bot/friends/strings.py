from jinja2 import Template

from give_money_bot.db.models import User
from give_money_bot.settings.states import EditVisibilityData

# EDIT_VISIBILITY_MESSAGE = """
# Страница: {{ page }} / {{ page_total }}
# """
#
NEW_USER_REQUEST = """
Пользователь {{ user.name }} хочет добавить пользователя {{ new_user.name }} в бота.
"""

NEW_USER_REQUEST_ACCEPTED = """
Админ подтвердил добавление пользователя {{ new_user.name }} в бота.
"""

NEW_USER_REQUEST_DECLINED = """
Админ отклонил добавление пользователя {{ new_user.name }} в бота.
"""


class Strings:
    cancel = "Отмена"
    save = "Сохранить"
    saved = "Сохранено"
    menu_friends_answer = "Настройки друзей"

    menu_add_new_user = "Добавить нового пользователя"
    ask_for_new_user = "Пришли мне контакт пользователя или перешли сообщение от пользователя"
    request_contact = "Отправить контакт"
    user_not_found = "Пользователь не найден"
    user_already_exists = "Пользователь уже существует"
    sent_request_to_add_user = "Запрос на добавление пользователя отправлен администратору"
    admin_accept_answer = "Пользователь подтвержден"
    admin_reject_answer = "Пользователь отклонен"

    menu_exit = "Назад"

    @staticmethod
    def admin_new_user_request(user: User, new_user: User) -> str:
        return Template(NEW_USER_REQUEST).render(user=user, new_user=new_user)

    @staticmethod
    def admin_new_user_request_accepted(new_user: User) -> str:
        return Template(NEW_USER_REQUEST_ACCEPTED).render(new_user=new_user)

    @staticmethod
    def admin_new_user_request_rejected(new_user: User) -> str:
        return Template(NEW_USER_REQUEST_DECLINED).render(new_user=new_user)

    # @staticmethod
    # def profile_message(user: User) -> str:
    #     return Template(PROFILE_MESSAGE).render(user=user)
