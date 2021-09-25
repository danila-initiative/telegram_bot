import datetime
import sqlite3

import pytest

from bot_zakupki.common import db


@pytest.fixture(scope='function')
def setup_database():
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    db._init_db(cursor)

    yield conn
    conn.close()


def test_insertion(setup_database):
    print(datetime.datetime.now())
    # connection = setup_database
    cursor = setup_database.cursor()
    res_before = db.get_all_search_queries(cursor)
    data = {
        "user_id": 123456,
        "search_string": "search_string",
        "location": "Москва"
    }
    db.insert_one_in_search_query(cursor, data)
    res_after = db.get_all_search_queries(cursor)

    now = datetime.datetime.now()
    date_time = now.strftime("%Y-%m-%d %H:%M:%S")

    last_sub_day = now + datetime.timedelta(days=7)
    last_date = last_sub_day.strftime("%Y-%m-%d %H:%M:%S")

    assert res_before == []
    assert res_after == [(1, '123456', 'search_string',
                          'Москва', None, date_time,
                          last_date, date_time, 0)]
