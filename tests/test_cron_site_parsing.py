import datetime

import pytest

from bot_zakupki.common import consts
from bot_zakupki.common import dates
from bot_zakupki.common import db


@pytest.mark.parametrize(
    "user_ids,number_of_queries,max_num_of_queries,days_delta," "expected_len",
    (
        pytest.param(["111"], 0, 0, consts.TRIAL_PERIOD_DAYS, 0, id="1"),
        pytest.param(["222"], 1, 3, consts.TRIAL_PERIOD_DAYS, 1, id="2"),
        pytest.param(["333"], 3, 3, consts.TRIAL_PERIOD_DAYS, 3, id="3"),
        pytest.param(["444"], 3, 3, -1, 0, id="4"),
        pytest.param(["555"], 5, 1, 30, 1, id="5"),
        pytest.param(["666", "77"], 5, 1, 30, 2, id="6"),
        pytest.param(["777"], 5, 5, 30, 5, id="7"),
        pytest.param(["888"], 5, 5, -1, 0, id="8"),
    ),
)
def test_get_all_active_search_queries(
    setup_db,
    user_ids,
    number_of_queries,
    max_num_of_queries,
    days_delta,
    expected_len,
):
    # 1. Пользователь только зарегался - 0 запросов
    # 2. Пользователь на пробном периоде - 1 запрос
    # 3. Пользователь на пробном периоде - 3 запроса
    # 4. Пользователь закончил пробный период - подписку не продлил
    # 5. Активная подписка на 1 запрос, всего есть 5 запросов
    # 6. Активная подписка на 1 запрос, всего есть 5 запросов (2 пользователя)
    # 7. Активная подписка на 5 запросов, всего есть 5 запросов
    # 8. Неактивная подписка на 5 запросов, всего есть 5 запросов

    _set_db_according_data(
        user_ids, number_of_queries, max_num_of_queries, days_delta
    )

    rows = db.get_all_active_search_queries()
    assert len(rows) == expected_len


def _set_db_according_data(
    user_ids, number_of_queries, max_num_of_queries, days_delta
):
    now = dates.get_current_time_for_db()

    for user_id in user_ids:
        db.insert_new_user(user_id)
        query = {
            "user_id": user_id,
            "search_string": "search_string",
            "location": "location",
            "min_price": 0,
            "max_price": 100,
        }
        for i in reversed(range(number_of_queries)):
            delta = i if i % 2 == 1 else -i
            query["created_at"] = now + datetime.timedelta(minutes=delta)
            db.insert_new_search_query(column_values=query)

        last_sub_day = now + datetime.timedelta(days=days_delta)

        user_data_update = {
            db.USER_SUBSCRIPTION_LAST_DAY: last_sub_day,
            db.USER_MAX_NUMBER_OF_QUERIES: max_num_of_queries,
        }
        db.update_user_by_user_id(
            user_id=user_id, column_values=user_data_update
        )


def test_site_parsing(setup_db):
    pass
