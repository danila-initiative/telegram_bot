import typing

from bot_zakupki.common import models


def format_price_for_message(price: int) -> str:
    str_price = str(price)
    if len(str_price) <= 3:
        return str_price

    rest = len(str_price) % 3

    new_price = str_price[0:rest]
    i = rest
    while i <= len(str_price):
        new_price += " "
        last_index = min(len(str_price), i + 3)
        new_price += str_price[i:last_index]
        i += 3

    return new_price


def check_and_process_max_price(
    max_price: str, min_price: int
) -> typing.Tuple[models.MaxPriceValidation, typing.Union[None, int]]:
    max_price = delete_all_spaces(max_price)

    if not max_price.isdigit():
        return models.MaxPriceValidation.NOT_A_NUMBER, None

    if int(max_price) <= min_price:
        return models.MaxPriceValidation.LESS_THAT_MIN_PRICE, None

    if int(max_price) >= 1000000000000:
        return models.MaxPriceValidation.VALID, 1000000000000

    return models.MaxPriceValidation.VALID, int(max_price)


def delete_all_spaces(string: str) -> str:
    return "".join(string.split())


def delete_all_extra_spaces(string: str) -> str:
    return " ".join(string.split())
