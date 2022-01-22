import random
import time

from loguru import logger

from bot_zakupki.common import consts
from bot_zakupki.common import dates
from bot_zakupki.common import db
from bot_zakupki.common import models
from bot_zakupki.common import parser


def start_parsing():
    logger.info(f"Cron task {__file__} launched.")
    # Получаем список всех активных запросов из базы
    active_queries = db.get_all_active_search_queries()

    publish_date = dates.get_date_for_request(days_delta=consts.PUBLISH_DELTA)

    # {query_id: List[Results]}
    results = {}
    for query in active_queries:

        # Формируем url для запроса
        params = models.RequestParameters(
            search_string=query.search_string,
            min_price=query.min_price,
            max_price=query.max_price,
            place_name=query.location,
            publish_date_from=publish_date,
            publish_date_to=publish_date,
        )

        url = parser.request_formation(params)

        logger.debug(f"query_id: {query.unique_id}; url: {url}")
        page = parser.get_page_by_url(url)
        result = parser.parse_result_page(
            page=page, search_string=query.search_string
        )

        if result is None:
            continue

        results[query.unique_id] = result

        time.sleep(random.randint(3, 10))

    db.insert_results(column_values=results)


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
