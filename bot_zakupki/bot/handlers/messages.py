from bot_zakupki.bot.handlers import commands

CMD_START_MSG = (
    f"Привет) Мы поможем тебе найти подходящие закупки 😎\n"
    f"\n"
    f"Для этого, необходимо заполнить несколько параметров для поиска. "
    f"Сделать это можно при помощи "
    f"команды /{commands.ADD_NEW_QUERY}\n "
    f"\n"
    f"У тебя будет тестовый период в течение 4-х недель."
    f"В течение тестового периода, каждый будний день, 8 утра, "
    f"тебе будут приходить подходящие для тебя закупки.\n"
)

# ========== SEARCH_QUERY_HANDLERS ==========
NEW_QUERY_MSG = (
    "Параметры для поиска ты сможешь изменить в любой момент, "
    "так что не бойся ошибиться 🙂\n"
    "\n"
    "Для начала, введи <b>ключевое слово или словосочетание</b>, "
    "по которому мы будем искать тебе закупки.\n"
    "Слова лучше использовать в единственном числе и именительном падеже, "
    "иногда даже без окончаний.\n"
    "\n"
    "Например:\n"
    "- <b>телефон</b>, а не телефоны\n"
    "- <b>шоколад торт</b>, а не шоколадные торты\n"
    "\n"
    "Итак, введи ключевое слово или словосочетание:\n"
)

SELECT_LOCATION = "Теперь выбери регион для закупки:"

SELECT_LOCATION_INVALID = (
    "Неверно указан регион для поиска. Выберите регион из перечисленных ниже"
)

SET_MINIMUM_PRICE = "Теперь нужно указать минимальную цену в рублях:"

SET_MINIMUM_PRICE_INVALID = (
    "Неверно указана минимальная цена. "
    "Минимальная цена должна быть целым, неотрицательным числом.\n"
    "Попробуй ещё раз:"
)

SET_MAXIMUM_PRICE = "И наконец максимальную цену в рублях:"

SET_MAX_PRICE_INVALID = (
    "Неверно указана максимальная цена. "
    "Максимальная цена должна быть целым, неотрицательным числом.\n"
    "Попробуй ещё раз:"
)

SET_MAX_PRICE_LESS_THAN_MIN = (
    "Максимальная цена меньше минимальной. Введи число побольше 🙂"
)

CANNOT_ADD_MORE_QUERY_IN_TRIAL_PERIOD = (
    "Максимальное количество поисковых запросов в пробный период равно 3."
)

TOO_MANY_NOT_ACTIVE_QUERIES = (
    "Слишком много неактивных запросов. "
    "Измените или удалите текущие неактивные запросы."
)


def query_message_formation(
        search_string: str, location: str, min_price: int, max_price: int
) -> str:
    answer = (
        f"🔍 Ключевая строка: <b>{search_string}</b>\n"
        f"\n"
        f"🌏 Регион: {location}\n"
        f"\n"
        f"💰 Цена: от {min_price} до {max_price} рублей"
    )

    return answer
