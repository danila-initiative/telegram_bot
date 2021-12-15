# import datetime
# import sqlite3
#
# import pytest
#
# from bot_zakupki.common import dates
# from bot_zakupki.common import db
# from bot_zakupki.common import models
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
#
#
# def test_insert_new_search_query(setup_db):
#     cursor = setup_db.cursor()
#     res_before = db.get_all_search_queries(cursor)
#     data = {
#         "user_id": 123456,
#         "search_string": "search_string",
#         "location": "Москва",
#     }
#
#     db.insert_new_search_query(
#         column_values=data, connection=setup_db, cursor=cursor
#     )
#     res_after = db.get_all_search_queries(cursor)
#
#     now = datetime.datetime.now().replace(microsecond=0)
#
#     expected_result = models.SearchQuery(
#         id=1,
#         user_id="123456",
#         search_string="search_string",
#         location="Москва",
#         min_price=0,
#         max_price=None,
#         created_at=now,
#         subscription_last_day=None,
#         payment_last_day=None,
#         deleted=bool(0),
#     )
#
#     assert res_before == []
#     assert res_after == [expected_result]
#
#
# def test_get_all_search_queries_by_user_id(setup_db_with_data):
#     cursor = setup_db_with_data
#     res = db.get_all_search_queries_by_user_id("123456", cursor)
#
#     assert len(res) == 3
#     for row in res:
#         assert row.user_id == "123456"
#
#
# def test_get_all_active_search_queries_by_user_id(setup_db_with_data):
#     today = "2021-07-15 10:10:00"
#     cursor = setup_db_with_data
#     res = db.get_all_active_search_queries_by_user_id(
#         "123456", dates.sqlite_date_to_datetime(today), cursor
#     )
#
#     assert len(res) == 2
#     for row in res:
#         assert row.subscription_last_day > dates.sqlite_date_to_datetime(today)
#
#
# def test_get_all_results(setup_db):
#     cursor = setup_db.cursor()
#     rows = db.get_all_results(cursor)
#     assert len(rows) == 0
#
#     date = dates.res_date_to_datetime("03.07.2021")
#
#     result = models.Result(
#         search_string="string 1",
#         number_of_purchase="12345678994",
#         publish_date=date,
#         finish_date=date,
#         price=1274812,
#         subject_of_purchase="subject",
#         link="http://dsdgsdgsdgsd.com",
#         customer="customer 1",
#     )
#
#     db.insert_results({124124: [result], 235423: [result]}, setup_db, cursor)
#     rows = db.get_all_results(cursor)
#
#     expected_results = [
#         models.Result(
#             search_string="string 1",
#             publish_date=datetime.datetime(2021, 7, 3, 0, 0),
#             finish_date=datetime.datetime(2021, 7, 3, 0, 0),
#             number_of_purchase="12345678994",
#             subject_of_purchase="subject",
#             price=1274812,
#             link="http://dsdgsdgsdgsd.com",
#             customer="customer 1",
#             location=None,
#             query_id=124124,
#         ),
#         models.Result(
#             search_string="string 1",
#             publish_date=datetime.datetime(2021, 7, 3, 0, 0),
#             finish_date=datetime.datetime(2021, 7, 3, 0, 0),
#             number_of_purchase="12345678994",
#             subject_of_purchase="subject",
#             price=1274812,
#             link="http://dsdgsdgsdgsd.com",
#             customer="customer 1",
#             location=None,
#             query_id=235423,
#         ),
#     ]
#
#     assert rows == expected_results
