from typing import List

from bot_zakupki.bot.handlers import commands
from bot_zakupki.common import dates
from bot_zakupki.common import models

CMD_START_MSG = (
    f"Здравствуйте) Мы поможем вам найти подходящие для вас закупки 😎\n"
    f"\n"
    f"Каждый будний день, в 8 утра, мы будем присылать список подходящих для вас закупок. "
    f"\n"
    f"Для этого, необходимо заполнить несколько параметров для поиска при помощи "
    f"команды /{commands.ADD_NEW_QUERY}\n"
    f"\n"
    f"У вас будет пробный период в течение 2-х недель.\n"
    f"\n"
    f"Подробнее о работе бота можно узнать при помощи команды /{commands.HELP}\n "
)

CMD_HELP_MSG = (
    f"<b>Как это работает?</b>\n"
    f"Каждый будний день, в 8 утра, мы будем присылать список подходящих для вас закупок.\n"
    f"\n"
    f"<b>Пробный период</b>\n"
    f"Пробный период длится 2 недели."
    f"В пробный период, максимальное количество запросов равно 3."
    f"То есть, каждый будний день мы будем присылать вам подходящие закупки по 3-м разным запросам.\n"
    f"\n"
    f"<b>Описание команд </b>\n"
    f"/{commands.ADD_NEW_QUERY} - добавление нового поискового запроса\n"
    f"/{commands.SHOW_ALL_MY_QUERIES} - отображение время ваших активных и неактивных запросов\n"
    f"/{commands.CHANGE_QUERY} - при помощи этой команды можно изменить какой-нибудь запрос\n"
    f"/{commands.HELP} - покажет это сообщение еще раз 😊\n"
    f"\n"
    f"<b>Как с нами связаться?</b>\n "
    f"По любым вопросам о работе бота можете писать нам на почту zakupki_info@gmail.com"
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

SELECT_LOCATION = "Теперь выбери регион для запроса: "

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

NO_QUERIES = "У тебя пока нет никаких запросов"

SEARCH_STRING = "Ключевая строка"
REGION = "Регион"

WHICH_QUERY_CHANGE = "Какой запрос хотите изменить?"

UPDATED_QUERY = "Обновленные параметры для запроса"


# формирование сообщения после КА с заданием данных
def query_message_formation(
        search_string: str,
        location: str,
        min_price: int,
        max_price: int,
        with_n: bool = True,
) -> str:
    delimiter = ""
    if with_n:
        delimiter = "\n"
    answer = (
        f"🔍 {SEARCH_STRING}: <b>{search_string}</b>\n"
        f"{delimiter}"
        f"🌏 {REGION}: {location}\n"
        f"{delimiter}"
        f"💰 Цена: от {min_price} до {max_price} рублей"
    )

    return answer


def changed_query_message_formation(
        search_string: str,
        location: str,
        min_price: int,
        max_price: int,
        query_number: str,
) -> str:
    answer = f"{UPDATED_QUERY} <b>{query_number}.\n</b>" f"\n"
    query = query_message_formation(
        search_string, location, min_price, max_price, False
    )

    return answer + query


def all_queries_messages_formation(queries: List[models.SearchQuery]) -> str:
    answer = ""
    if not queries:
        answer = NO_QUERIES

    for i, query in enumerate(queries):
        tmp = (
            f"<b>{i + 1}</b>. 🔍 {SEARCH_STRING}: {query.search_string}\n"
            f"    🌏 {REGION}: {query.location}\n"
            f"    💰 Цена: от {query.min_price} до {query.max_price} рублей\n"
        )

        subscription_msg = ""
        subscription_last_day = query.subscription_last_day
        now = dates.get_current_time_for_db()
        if subscription_last_day is not None and now < subscription_last_day:
            subscription_msg = (
                f"    🗓️ Окончание подписки: "
                f"{dates.format_date(query.subscription_last_day)}\n"
            )
        else:
            subscription_msg = f"    🗓️ Подписка неактивна" f"\n"

        tmp += subscription_msg
        tmp += "\n"

        answer += tmp

    return answer
