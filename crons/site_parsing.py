import random
import time

from bs4 import BeautifulSoup as BS
from loguru import logger

from bot_zakupki.common import consts
from bot_zakupki.common import dates
from bot_zakupki.common import db
from bot_zakupki.common import models
from bot_zakupki.common import parser


def start_parsing():
    logger.info(f"Cron task {__file__} launched.")

    site_available = _is_site_available()
    if not site_available:
        # TODO: добавить отправку сообщения в админский чат
        # TODO: Записать в таблицу, что сайт недоступен
        return

    # Получаем список всех активных запросов из базы
    active_queries = db.get_all_active_search_queries()

    publish_date = dates.get_date_for_request(days_delta=consts.PUBLISH_DELTA)

    # {query_id: List[Results]}
    results = {}
    for query in active_queries:
        # Формируем url для запроса
        url = _format_request(query=query, publish_date=publish_date)
        logger.debug(f"query_id: {query.unique_id}; url: {url}")

        page = parser.get_page_by_url(url)

        result = parser.parse_result_page(
            page=page, search_string=query.search_string
        )

        if result is None:
            logger.info(f"There is no results for query {query.unique_id} "
                        f"at {publish_date}")
            continue

        results[query.unique_id] = result

        time.sleep(random.randint(3, 10))

    db.insert_results(column_values=results)

    logger.info(f"Cron task {__file__} is finished.")


def _is_site_available():
    page = parser.get_page_by_url(consts.BASE_URL)

    if page.status_code >= 400:
        logger.error(f"Site unavailable. Status code: {page.status_code}")
        return False

    soup = BS(page.content, "html.parser")
    number_of_records = soup.find("div", class_="search-results__total")

    if number_of_records is None:
        logger.error("Probably site unavailable: Check it manually")
        raise False

    return True


def _format_request(query: models.SearchQuery, publish_date: str) -> str:
    params = models.RequestParameters(
        search_string=query.search_string,
        min_price=query.min_price,
        max_price=query.max_price,
        place_name=query.location,
        publish_date_from=publish_date,
        publish_date_to=publish_date,
    )

    return parser.request_formation(params)


if __name__ == "__main__":
    logger.remove()
    if consts.DEBUG:
        logger.add(
            f"{consts.CRONS_LOG_FOLDER}{dates.get_today_date()}.log",
            level="DEBUG",
            backtrace=True,
            diagnose=True,
        )
    else:
        logger.add(
            f"{consts.CRONS_LOG_FOLDER}{dates.get_today_date()}.log",
            level="INFO",
        )

    start_parsing()
