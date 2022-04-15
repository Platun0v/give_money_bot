from typing import Dict, List

from jinja2 import Template

from give_money_bot.db.models import Credit

ASK_FOR_DEBTORS_MESSAGE = """
{%- if value < 0 -%}
Кому ты должен {{ value | abs }} руб?
{{ info }}
{%- else -%}
Кто тебе должен {{ value }} руб?
{{ info }}
{%- endif -%}
"""

SAVE_CREDIT_MESSAGE = """
{%- if value < 0 -%}
Ты должен {{ value | abs }} руб. {{ username | join(', ') }}
{%- else -%}
Тебе должен {{ value }} руб. {{ username | join(', ') }}
{%- endif -%}
{{ info }}
Сохранено
"""

ANNOUNCE_NEW_CREDIT_MESSAGE = """
{%- if value < 0 -%}
Тебе должен {{ value | abs }} руб.: {{ username }}
{%- else -%}
Ты должен {{ value }} руб. ему: {{ username }}
{%- endif %}
{{ info }}
"""

ANNOUNCE_RETURN_CREDIT_MESSAGE = """
Тебе {{ username }} вернул {{ value }} руб.
{%- if info -%}
{{ info }}
{%- endif -%}
"""

REMOVE_CREDITS_WITH_MESSAGE = """ 
Была уничтожена цепочка долгов на сумму {{ amount }} руб.:
{{ chain }}
"""

DEBTOR_CREDITS_MESSAGE = """
Ты должен:
{%- for credit in credits %}
{{ loop.index }}) {{ credit.get_amount() }} руб. ему {{ credit.creditor.name }}
{%- if credit.text_info %}
{{ credit.text_info }}
{%- endif -%}
{% endfor %}
====================
{%- for user, value in user_credits.items() %}
Ты должен {{ users[user] }} - {{ value }} руб.
{%- endfor %}
Итого: {{ credits_sum }} руб.
Ты можешь выбрать долги, которые ты уже вернул:
"""

RETURN_GENERATOR_MESSAGE = """
Ты вернул:
{%- for user_id, value in credits.items() %}
{{ value }} руб. ему: {{ users[user_id] }}
{% endfor -%}
"""

CREDITOR_CREDITS_GENERATOR_MESSAGE = """
Тебе должны:
{%- for credit in credits %}
{{ loop.index }}) {{ credit.debtor.name }}: {{ credit.get_amount() }} руб.
{%- if credit.text_info %}
{{ credit.text_info }}
{%- endif -%}
{% endfor %}
====================
{%- for user, value in user_credits.items() %}
{{ users[user] }} тебе должен - {{ value }} руб.
{%- endfor %}
Итог: {{ credits_sum }} руб.
"""


class Strings:
    DIGITS = "0123456789()+-*/ "
    DIVIDER = "================\n"

    HELLO_MESSAGE = "Привет!"

    INPUT_CREDIT = "Введите сумму(по желанию инфу по долгу через пробел)"
    NEED_NON_ZERO = "Требуется ненулевое значение"

    FORGOT_CHOOSE = "Ты ничего не выбрал"
    CANCEL = "Отмена"
    SAVE = "Сохранить"

    NO_CREDITS_CREDITOR = "Тебе никто не должен. Можешь спать спокойно"
    NO_CREDITS_DEBTOR = "Ты никому не должен. Свободен"

    @staticmethod
    def ask_for_debtors(value: int, info: str) -> str:
        """
        Создает сообщение, в котором спрашивается, для кого новый долг

        Parameters:
            value: сумма долга
            info: информация о долге
        """
        return Template(ASK_FOR_DEBTORS_MESSAGE).render(value=value, info=info)

    @staticmethod
    def credit_saved(value: int, usernames: List[str], info: str) -> str:
        """
        Создает сообщение, с информацией о созданном долге

        Parameters:
            value: сумма долга
            usernames: имена пользователей
            info: информация о долге
        """
        return Template(SAVE_CREDIT_MESSAGE).render(value=value, usernames=usernames, info=info)

    @staticmethod
    def announce_new_credit(value: int, username: str, info: str) -> str:
        """
        Создает сообщение, которое сообщает пользователю о новом долге для него

        Parameters:
            value: сумма долга
            username: имя пользователя
            info: информация о долге
        """
        return Template(ANNOUNCE_NEW_CREDIT_MESSAGE).render(value=value, username=username, info=info)

    @staticmethod
    def announce_returned_credit(value: int, username: str, info: str) -> str:
        """
        Создает сообщение, в котором сообщается, что пользователю вернули долг

        Parameters:
            value: сумма долга
            username: имя пользователя
            info: информация о долге
        """
        return Template(ANNOUNCE_RETURN_CREDIT_MESSAGE).render(value=value, username=username, info=info)

    @staticmethod
    def removed_credit_chain(amount: int, chain: str) -> str:
        """
        Создает сообщение, в котором сообщается об уничтоженной цепочке долгов

        Parameters:
            amount: сумма долга
            chain: цепочка пользователей
        """
        return Template(REMOVE_CREDITS_WITH_MESSAGE).render(amount=amount, chain=chain)

    @staticmethod
    def debtor_credits(
        credits: List[Credit],
        user_credits: Dict[int, int],
        credits_sum: int,
        users: Dict[int, str],
    ) -> str:
        """
        Создает сообщение, в котором сообщается информация о нынешних задолжностях

        Parameters:
            credits: список с долгами
            user_credits: Dict[user_id: credit_amount] сумма долгов для каждого пользователя
            credits_sum: итоговая сумма долгов
            users: Dict[user_id: username] сопоставление user_id и имени пользователя
        """
        template = Template(DEBTOR_CREDITS_MESSAGE)
        return template.render(
            credits=credits,
            user_credits=user_credits,
            credits_sum=credits_sum,
            users=users,
        )

    @staticmethod
    def returned_credit(returned_credits_sum: Dict[int, int], users: Dict[int, str]) -> str:
        """
        Создает сообщение, с информацией о возвращенных долгах

        Parameters:
            returned_credits_sum: Dict[user_id: credit_amount] сумма долгов для каждого пользователя
            users: Dict[user_id: username] сопоставление user_id и имени пользователя
        """
        template = Template(RETURN_GENERATOR_MESSAGE)
        return template.render(credits=returned_credits_sum, users=users)

    @staticmethod
    def creditor_credits(
        credits: List[Credit],
        user_credits: Dict[int, int],
        credits_sum: int,
        users: Dict[int, str],
    ) -> str:
        """
        Создает сообщение, в котором сообщается о людях, которые тебе должны

        Parameters:
            credits: список с долгами
            user_credits: Dict[user_id: credit_amount] сумма долгов для каждого пользователя
            credits_sum: итоговая сумма долгов
            users: Dict[user_id: username] сопоставление user_id и имени пользователя
        """
        template = Template(CREDITOR_CREDITS_GENERATOR_MESSAGE)
        return template.render(
            credits=credits,
            user_credits=user_credits,
            credits_sum=credits_sum,
            users=users,
        )
