import math

import pytest

from give_money_bot.credits.utils import parse_expression


def test_test():
    assert 3 == 1 + 2


@pytest.mark.parametrize("expression", [
    "1 + 2",
    "(1 + 2)",
    "-(1 * 2)",
    "- (1 * 2)",
    "- (-1 * 2)",
    "-+123",
    "-5+4",
    "-(+(-(5)))",
])
def test_parser(expression):
    assert parse_expression(expression)[0] == eval(expression)


@pytest.mark.parametrize("expression_float", [
    "180 / 3 +1200/3",
    "5 + (4 / (3 - (1 * 4)))",
])
def test_parser_float(expression_float):
    assert math.floor(parse_expression(expression_float)[0]) == math.floor(eval(expression_float))


@pytest.mark.parametrize("expression_error", [
    "((1)",
    "1/0",
    "",
    "1 - * 5"
])
def test_parser_on_error1(expression_error):
    assert parse_expression(expression_error)[1] is not None

# TODO: Тесты Warning, о которых пишется, что они не прошли, но общее прохождение тестов считается успешным
