import datetime

from bot_zakupki.common import db
from bot_zakupki.common import models


#
#
# @pytest.fixture(scope="function")
# def setup_db():
#     conn = sqlite3.connect(":memory:")
#     cursor = conn.cursor()
#     db.init_db(connection=conn, cursor=cursor)
#
#     yield conn
#     conn.close()
#
#
# # ========== user ==========
#
#
# def test_get_insert_update_user_by_user_id(setup_db):
#     cursor = setup_db.cursor()
#     result = db.get_user_by_user_id("1111", cursor=cursor)
#     assert result is None
#
#     results = db.get_all_users(cursor=cursor)
#     assert results is None
#
#     # insert users
#     user_ids = ["1111", "2222", "3333"]
#     for user_id in user_ids:
#         db.insert_new_user(user_id=user_id, connection=setup_db, cursor=cursor)
#     results = db.get_all_users(cursor=cursor)
#     assert len(results) == 3
#
#     user_2222 = db.get_user_by_user_id("2222", cursor=cursor)
#     assert user_2222.user_id == "2222"
#     assert user_2222.id == 2
#     assert user_2222.bot_is_active
#
#     # update
#     new_data = {"bot_is_active": 0}
#     db.update_user_by_user_id(
#         user_id="2222",
#         column_values=new_data,
#         connection=setup_db,
#         cursor=cursor,
#     )
#     user_2222 = db.get_user_by_user_id("2222", cursor=cursor)
#     assert user_2222.user_id == "2222"
#     assert user_2222.id == 2
#     assert not user_2222.bot_is_active
#
#
# # ========== search_query ==========
#
#
# @pytest.fixture(scope="function")
# def setup_db_with_data(setup_db):
#     cursor = setup_db.cursor()
#     query_1 = {
#         "user_id": 123456,
#         "search_string": "search_string_1",
#         "location": "Москва",
#         "subscription_last_day": "2021-07-20 10:10:00",
#     }
#     query_2 = {
#         "user_id": 78910,
#         "search_string": "search_string_2",
#         "location": "Питер",
#         "subscription_last_day": "2021-07-25 10:10:00",
#     }
#     query_3 = {
#         "user_id": 123456,
#         "search_string": "search_string_2",
#         "location": "Питер",
#         "deleted": 1,
#         "subscription_last_day": "2021-07-30 10:10:00",
#     }
#     query_4 = {
#         "user_id": 123456,
#         "search_string": "search_string_1",
#         "location": "Москва",
#         "subscription_last_day": "2021-07-10 10:10:00",
#     }
#
#     queries = [query_1, query_2, query_3, query_4]
#     for query in queries:
#         db.insert_new_search_query(
#             column_values=query, connection=setup_db, cursor=cursor
#         )
#
#     yield cursor


def test_insert_new_search_query(setup_db):
    res_before = db.get_all_search_queries()
    data = {
        "user_id": 123456,
        "search_string": "search_string",
        "location": "Москва",
        "min_price": 0,
        "max_price": 100000,
    }

    db.insert_new_search_query(column_values=data)
    res_after = db.get_all_search_queries()

    now = datetime.datetime.now().replace(microsecond=0)

    expected_result = models.SearchQuery(
        unique_id=1,
        user_id="123456",
        search_string="search_string",
        location="Москва",
        min_price=0,
        max_price=100000,
        created_at=now,
        last_updated_at=now,
    )

    assert res_before == []
    assert res_after == [expected_result]


def test_insert_get_all_results(setup_db):
    rows = db.get_all_results()
    assert len(rows) == 0

    result_2 = {
        1: [
            models.Result(
                publish_date=datetime.datetime(2022, 1, 28).date(),
                finish_date=datetime.datetime(2022, 2, 4, 0, 0).date(),
                number_of_purchase="№ 0348100089422000001",
                subject_of_purchase="Оказание услуг по очистке скатной",
                price=269694,
                link="https://zakupki.gov.ru/epz/order/notice/zk20",
                customer="ГОСУДАРСТВЕННОЕ УЧРЕЖДЕНИЕ",
            ),
            models.Result(
                publish_date=datetime.datetime(2022, 1, 28).date(),
                finish_date=datetime.datetime(2022, 2, 4, 0, 0).date(),
                number_of_purchase="№ 0348100089422000001",
                subject_of_purchase="Оказание услуг по очистке скатной",
                price=269694,
                link="https://zakupki.gov.ru/epz/order/notice/zk20",
                customer="ГОСУДАРСТВЕННОЕ УЧРЕЖДЕНИЕ",
            ),
        ]
    }

    db.insert_results(result_2)
    rows = db.get_all_results()

    expected_results = [
        models.ResultDB(
            unique_id=1,
            publish_date=datetime.datetime(2022, 1, 28),
            finish_date=datetime.datetime(2022, 2, 4, 0, 0),
            number_of_purchase="№ 0348100089422000001",
            subject_of_purchase="Оказание услуг по очистке скатной",
            price=269694,
            link="https://zakupki.gov.ru/epz/order/notice/zk20",
            customer="ГОСУДАРСТВЕННОЕ УЧРЕЖДЕНИЕ",
            query_id=1,
        ),
        models.ResultDB(
            unique_id=2,
            publish_date=datetime.datetime(2022, 1, 28),
            finish_date=datetime.datetime(2022, 2, 4, 0, 0),
            number_of_purchase="№ 0348100089422000001",
            subject_of_purchase="Оказание услуг по очистке скатной",
            price=269694,
            link="https://zakupki.gov.ru/epz/order/notice/zk20",
            customer="ГОСУДАРСТВЕННОЕ УЧРЕЖДЕНИЕ",
            query_id=1,
        ),
    ]

    assert rows == expected_results
