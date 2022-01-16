import datetime
from typing import List
from typing import Optional

from bot_zakupki.bot.handlers import commands
from bot_zakupki.common import consts
from bot_zakupki.common import dates
from bot_zakupki.common import db
from bot_zakupki.common import models
from bot_zakupki.common import utils

SEARCH_STRING = "Ключевая строка"
REGION = "Регион"

CMD_START_MSG = (
    "Здравствуйте) Мы поможем вам найти подходящие для вас закупки 😎"
    "\n\n"
    "Каждый будний день, в 8 утра, мы будем присылать список "
    "подходящих для вас закупок. "
    "\n"
    "Для поиска нужно заполнить всего 3 параметра при помощи команды "
    f"/{commands.ADD_NEW_QUERY}"
    "\n\n"
    "Пробные период длится 2 недели. "
    "В пробный период можно сделать максимум 3 бесплатных запроса."
    "\n\n"
    f"Подробнее о работе бота - /{commands.HELP}\n"
)

CMD_HELP_MSG = (
    "<b>Как это работает?</b>\n"
    "Каждый будний день, в 8 утра, мы будем присылать список подходящих "
    "для вас закупок.\n"
    "\n"
    "<b>Пробный период</b>\n"
    "Пробный период длится 2 недели. "
    "В пробный период максимальное количество запросов равно 3. "
    "То есть, каждый будний день мы будем присылать вам подходящие закупки "
    "по 3-м разным запросам.\n"
    "\n"
    "<b>Описание команд</b>\n"
    f"/{commands.ADD_NEW_QUERY} - добавление нового поискового запроса\n"
    f"/{commands.SHOW_ALL_MY_QUERIES} - отображение время ваших активных и "
    "неактивных запросов\n"
    f"/{commands.CHANGE_QUERY} - при помощи этой команды можно изменить "
    "какой-нибудь запрос\n"
    f"/{commands.HELP} - покажет это сообщение еще раз 😊\n"
    "\n"
    "<b>Как с нами связаться?</b>\n "
    "По любым вопросам о работе бота можете писать нам на почту "
    "zakupki_info@gmail.com"
)

CMD_HELP_SUBSCRIPTION_MSG = "Небольшая справка о работе бота"

# ========== SEARCH_QUERY_HANDLERS ==========


class CannotAddMoreQueries:
    TRIAL_PERIOD_LIMIT = (
        "Максимальное количество поисковых запросов "
        f"в пробный период равно {consts.MAX_QUERIES_IN_TRIAL_PERIOD}."
    )
    COMMON_PERIOD_LIMIT = (
        "К сожалению, нельзя добавить больше, "
        f"чем {consts.MAX_QUERIES_IN_COMMON_PERIOD} поисковых запросов."
    )


I_M_FEELING_LUCKY = "Мне повезёт"

SEARCH_STRING_MSG = (
    "Для начала, введите <b>ключевое слово или словосочетание</b>, "
    "по которому мы будем искать вам закупки.\n"
    "Слова лучше использовать в единственном числе и именительном падеже, "
    "иногда даже без окончаний.\n"
    "\n"
    "Например:\n"
    "- <b>телефон</b>, а не телефоны\n"
    "- <b>шоколад торт</b>, а не шоколадные торты\n"
    "\n"
    "Если предмет закупки вам не столь важен, то нажмите на кнопку "
    f'"<b>{I_M_FEELING_LUCKY}</b>" и мы будем присылать по 20 закупок в'
    f" день, подходящих по остальным параметрам: цене и региону поставки.\n"
    "\n"
    "Итак, введите ключевое слово или словосочетание:\n"
)

NEW_QUERY_MSG = (
    "Параметры для поиска вы сможете изменить в любой момент при помощи "
    f"команды /{commands.CHANGE_QUERY}. Так что не бойтесь ошибиться 🙂\n"
    "\n" + SEARCH_STRING_MSG
)

CHANGE_QUERY_MSG = SEARCH_STRING_MSG

# ===LOCATION===
SELECT_LOCATION = "Теперь, выберите регион для поставки:"
SELECT_LOCATION_INVALID = (
    "Неверно указан регион. Выберите регион из перечисленных ниже"
)

# ===PRICE===
SET_MIN_PRICE = (
    "Укажите минимальную цену закупки в рублях.\n"
    "Например: <b>0</b> или <b>100 000</b>"
)

SET_MIN_PRICE_INVALID = (
    "Неверно указана минимальная цена. "
    "Минимальная цена должна быть целым, неотрицательным числом.\n"
    "Попробуйте ещё раз:"
)

SET_MAX_PRICE = (
    "И наконец максимальную цену в рублях.\n" "Например: <b>10 000 000</b>"
)

SET_MAX_PRICE_NOT_A_NUMBER = (
    "Максимальная цена должна быть целым числом.\nПопробуйте ещё раз:"
)
SET_MAX_PRICE_LESS_THAN_MIN = (
    "Максимальная цена должна быть больше минимальной. "
    "Введите число побольше 🙂"
)


def trial_last_day_msg_formation(last_sub_day: datetime.datetime):
    date = dates.format_date_for_msg(last_sub_day)
    return f"Дата окончания пробного периода: {date}"


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

    min_price_str = utils.format_price_for_message(min_price)
    max_price_str = utils.format_price_for_message(max_price)

    answer = (
        f"🔍 {SEARCH_STRING}: <b>{search_string}</b>\n"
        f"{delimiter}"
        f"🌏 {REGION}: {location}\n"
        f"{delimiter}"
        f"💰 Цена: от {min_price_str} до {max_price_str} рублей"
    )

    return answer


# ==========change_query==========
WHICH_QUERY_DELETE = "Какой запрос хотите удалить?"
WHICH_QUERY_CHANGE = "Какой запрос хотите изменить?"
UPDATED_QUERY = "Обновленные параметры для запроса"


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


# ==========show_all_my_queries==========


THERE_IS_NO_QUERIES = (
    f"У вас еще нет поисковых запросов 🙂. \n"
    f"Добавить запрос для поиска закупок можно "
    f"командой /{commands.ADD_NEW_QUERY}\n"
)


def all_queries_messages_formation(
    queries: List[models.SearchQuery],
    subscription_last_day: Optional[datetime.datetime],
) -> str:
    answer = ""
    if not queries:
        answer = THERE_IS_NO_QUERIES

    for i, query in enumerate(queries):
        min_price = utils.format_price_for_message(query.min_price)
        max_price = utils.format_price_for_message(query.max_price)
        tmp = (
            f"<b>{i + 1}</b>. 🔍 {SEARCH_STRING}: {query.search_string}\n"
            f"    🌏 {REGION}: {query.location}\n"
            f"    💰 Цена: от {min_price} до {max_price} рублей\n"
        )

        answer += tmp

    now = dates.get_current_time_for_db()
    if subscription_last_day and now < subscription_last_day:
        subscription_msg = (
            f"    🗓️ Окончание подписки: "
            f"{dates.format_date_for_msg(subscription_last_day)}\n"
        )
    else:
        subscription_msg = "    🗓️ Подписка неактивна"

    answer += "\n"
    answer += subscription_msg

    return answer


def command_log_formation(command: str, user_id: int):
    return f"Command `{command}` was used by user {user_id}"


# ==========SUBSCRIPTION==========


def subscription_message_formation(user_id: str):
    now = dates.get_current_time_for_db()

    user = db.get_user_by_user_id(user_id=user_id)
    subscription_last_day = user.subscription_last_day if user else None
    max_number_of_queries = user.max_number_of_queries if user else None

    if subscription_last_day is None or subscription_last_day < now:
        subscription_msg = "🗓️ Подписка неактивна"
    else:
        postfix = "запрос"
        if max_number_of_queries == 5:
            postfix = "запросов"
        subscription_msg = (
            f"🗓️ Текущая подписка: активна до "
            f"{dates.format_date_for_msg(subscription_last_day)}"
            f" - {max_number_of_queries} {postfix}"
        )

    return subscription_msg


def after_subscription_message_formation(user_id: str):
    user = db.get_user_by_user_id(user_id=user_id)
    subscription_last_day = user.subscription_last_day if user else None
    max_number_of_queries = user.max_number_of_queries if user else None

    if subscription_last_day is None or max_number_of_queries is None:
        raise

    postfix = "запрос"
    if max_number_of_queries == 5:
        postfix = "запросов"

    subscription_msg = (
        f"🗓️ Текущая подписка: активна до "
        f"{dates.format_date_for_msg(subscription_last_day)}"
        f" - {max_number_of_queries} {postfix}"
    )

    return subscription_msg
