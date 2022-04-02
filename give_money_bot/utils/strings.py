from typing import List, Dict

from jinja2 import Template

from give_money_bot.db.models import Credit

ASK_FOR_DEBTORS_MESSAGE = """
{%- if negative -%}
Кому ты должен {{ value | abs }} руб?
{{ info }}
{%- else -%}
Кто тебе должен {{ value }} руб?
{{ info }}
{%- endif -%}
"""

SAVE_CREDIT_MESSAGE = """
{%- if negative -%}
Ты должен {{ value }} руб. {{ username | join(', ') }}
{%- else -%}
Тебе должен {{ value }} руб. {{ username | join(', ') }}
{%- endif -%}
{{ info }}
Сохранено
"""

ANNOUNCE_NEW_CREDIT_MESSAGE = """
{%- if negative -%}
Тебе должен {{ value }} руб.: {{ username }}
{%- else -%}
Ты должен {{ value }} руб. ему: {{ username }}
{%- endif -%}
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
{{ value }} руб. ему: {{ user[user_id] }}
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
    def ASK_FOR_DEBTORS(value: int, info: str, negative: bool = False) -> str:
        return Template(ASK_FOR_DEBTORS_MESSAGE).render(value=value, info=info, negative=negative)

    @staticmethod
    def SAVE_CREDIT(value: int, usernames: List[str], info: str, negative: bool = False) -> str:
        return Template(SAVE_CREDIT_MESSAGE).render(value=value, usernames=usernames, info=info, negative=negative)

    @staticmethod
    def ANNOUNCE_NEW_CREDIT(value: int, username: str, info: str, negative: bool = False) -> str:
        return Template(ANNOUNCE_NEW_CREDIT_MESSAGE).render(value=value, username=username, info=info,
                                                            negative=negative)

    @staticmethod
    def ANNOUNCE_RETURN_CREDIT(value: int, username: str, info: str) -> str:
        return Template(ANNOUNCE_RETURN_CREDIT_MESSAGE).render(value=value, username=username, info=info)

    @staticmethod
    def REMOVE_CREDITS_WITH(amount: int, chain: str) -> str:
        return Template(REMOVE_CREDITS_WITH_MESSAGE).render(amount=amount, chain=chain)

    @staticmethod
    def DEBTOR_CREDITS_MESSAGE(credits: List[Credit], user_credits: Dict[int, int], credits_sum: int,
                               users: Dict[int, str]) -> str:
        template = Template(DEBTOR_CREDITS_MESSAGE)
        return template.render(credits=credits, user_credits=user_credits, credits_sum=credits_sum, users=users)

    @staticmethod
    def RETURN_MESSAGE(returned_credits_sum: Dict[int, int], users: Dict[int, str]):
        template = Template(RETURN_GENERATOR_MESSAGE)
        return template.render(credits=returned_credits_sum, users=users)

    @staticmethod
    def CREDITOR_CREDITS_GENERATOR(credits: List[Credit], user_credits: Dict[int, int], credits_sum: int,
                                   users: Dict[int, str]) -> str:
        template = Template(CREDITOR_CREDITS_GENERATOR_MESSAGE)
        return template.render(credits=credits, user_credits=user_credits, credits_sum=credits_sum, users=users)
