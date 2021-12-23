from typing import List


class MessageGenerator:
    message = ""

    def add(self, text: str) -> None:
        self.message += text


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
        if negative:
            return f"Кому ты должен {abs(value)} руб?\n{info}"
        return f"Кто тебе должен {value} руб?\n{info}"

    @staticmethod
    def SAVE_CREDIT(value: int, usernames: List[str], info: str, negative: bool = False) -> str:
        if negative:
            text = f'Ты должен {value} руб: {", ".join(usernames)}\n'
        else:
            text = f'Тебе должен {value} руб: {", ".join(usernames)}\n'
        return text + f"{info}\n" + "Сохранено"

    @staticmethod
    def ANNOUNCE_NEW_CREDIT(value: int, username: str, info: str, negative: bool = False) -> str:
        if negative:
            text = f"Тебе должен {value} руб.: {username}\n"
        else:
            text = f"Ты должен {value} руб. ему: {username}\n"
        return text + info

    @staticmethod
    def ANNOUNCE_RETURN_CREDIT(value: int, username: str, info: str) -> str:
        return (
                f"Тебе {username} вернул {value} руб.\n" +
                (f"{info}\n" if info else "")
        )

    class DEBTOR_CREDITS_GENERATOR(MessageGenerator):
        def __init__(self) -> None:
            self.message += "Ты должен:\n"
            self.flag = True

        def add_position(self, i: int, value: int, username: str, info: str) -> None:
            self.add(
                f"{i}) {value} руб. ему: {username}\n" +
                (f"{info}\n" if info else "")
            )

        def add_sum(self, amount: int, username: str) -> None:
            if self.flag:
                self.add(Strings.DIVIDER)
                self.flag = False
            self.add(f"Ты должен {username} - {amount} руб.\n")

        def finish(self, credits_sum: int) -> str:
            self.add(f"Итого: {credits_sum} руб.\n")
            self.add("Ты можешь выбрать долги, которые ты уже вернул:")
            return self.message

    class RETURN_GENERATOR(MessageGenerator):
        def __init__(self) -> None:
            self.message += "Ты вернул:\n"

        def add_position(self, value: int, username: str) -> None:
            self.add(
                f"{value} руб. ему: {username}\n"
            )

        def finish(self) -> str:
            return self.message

    class CREDITOR_CREDITS_GENERATOR(MessageGenerator):
        def __init__(self) -> None:
            self.add("Тебе должны:\n")
            self.flag = True

        def add_position(self, i: int, value: int, username: str, info: str) -> None:
            self.add(
                f"{i}) {username}: {value} руб.\n" +
                (f"{info}\n" if info else "")
            )

        def add_sum(self, amount: int, username: str) -> None:
            if self.flag:
                self.add(Strings.DIVIDER)
                self.flag = False
            self.add(f"{username} тебе должен - {amount} руб.\n")

        def finish(self, credits_sum: int) -> str:
            self.add(f"Итог: {credits_sum} руб.")
            return self.message
