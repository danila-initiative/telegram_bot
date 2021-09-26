import datetime
import sqlite3

import pytest

from bot_zakupki.common import db
from bot_zakupki.common import models


@pytest.fixture(scope='function')
def setup_db():
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    db._init_db(cursor)

    yield conn
    conn.close()


@pytest.fixture(scope='function')
def setup_db_with_data(setup_db):
    cursor = setup_db.cursor()
    query_1 = {
        "user_id": 123456,
        "search_string": "search_string_1",
        "location": "Москва",
    }
    query_2 = {
        "user_id": 78910,
        "search_string": "search_string_2",
        "location": "Питер",
    }
    query_3 = {
        "user_id": '123456',
        "search_string": "search_string_2",
        "location": "Питер",
        "deleted": 1,
    }

    queries = [query_1, query_2, query_3]
    for query in queries:
        db.insert_new_search_query(cursor, query)

    yield cursor


def test_insert_new_search_query(setup_db):
    cursor = setup_db.cursor()
    res_before = db.get_all_search_queries(cursor)
    data = {
        "user_id": 123456,
        "search_string": "search_string",
        "location": "Москва"
    }

    db.insert_new_search_query(cursor, data)
    res_after = db.get_all_search_queries(cursor)

    now = datetime.datetime.now().replace(microsecond=0)
    last_sub_day = now + datetime.timedelta(days=7)

    expected_result = models.SearchQuery(
        id=1,
        user_id='123456',
        search_string='search_string',
        location='Москва',
        min_price=0,
        max_price=None,
        created_at=now,
        subscription_last_day=last_sub_day,
        payment_last_day=now,
        deleted=bool(0)
    )

    assert res_before == []
    assert res_after == [expected_result]


def test_get_all_search_queries_by_user_id(setup_db_with_data):
    cursor = setup_db_with_data
    res = db.get_all_search_queries_by_user_id(cursor, "123456")

    assert len(res) == 2
    for row in res:
        assert row.user_id == '123456'
