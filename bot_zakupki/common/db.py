import datetime
import os
import sqlite3
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from loguru import logger

from bot_zakupki.common import consts
from bot_zakupki.common import dates
from bot_zakupki.common import models

USER_USER_ID = "user_id"
USER_FIRST_BOT_START_DATE = "first_bot_start_date"
USER_BOT_START_DATE = "bot_start_date"
USER_BOT_IS_ACTIVE = "bot_is_active"
USER_SUBSCRIPTION_LAST_DAY = "subscription_last_day"
USER_PAYMENT_LAST_DAY = "payment_last_day"


# ===============Common===============


def get_connection_cursor(
    path_to_db: str = consts.PATH_TO_DB,
):
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    logger.info("Connection and Cursor to SQLite DB successful")

    return connection, cursor


base_con, base_cursor = get_connection_cursor()


def init_db(
    connection: sqlite3.Connection = base_con,
    cursor: sqlite3.Cursor = base_cursor,
    path_to_migrations: str = consts.PATH_TO_MIGRATIONS,
):
    """Инициализирует БД"""
    migrations = os.listdir(path_to_migrations)
    migrations = [os.path.join(path_to_migrations, mig) for mig in migrations]
    logger.info(f"migrations: {migrations}")
    for migration in migrations:
        with open(migration, "r") as f:
            sql = f.read()
        cursor.executescript(sql)
        connection.commit()


def check_db_exists(cursor: sqlite3.Cursor = base_cursor):
    """Проверяет, инициализирована ли БД, если нет — инициализирует"""
    for table_name in consts.TABLES_NAME:
        cursor.execute(
            "SELECT name FROM sqlite_master "
            f"WHERE type='table' AND name='{table_name}'"
        )
        table_exists = cursor.fetchall()
        if not table_exists:
            init_db()


# =============== user ===============


def insert_new_user(
    user_id: str,
    connection: sqlite3.Connection = base_con,
    cursor: sqlite3.Cursor = base_cursor,
):
    cursor.execute(
        f"INSERT INTO user" f"(user_id) " f"VALUES ({user_id})",
    )
    connection.commit()


def update_user_by_user_id(
    user_id: str,
    column_values: Dict,
    connection: sqlite3.Connection = base_con,
    cursor: sqlite3.Cursor = base_cursor,
):
    columns = " = ? ,".join(column_values.keys())
    columns += " = ?"

    values = tuple(column_values.values())
    cursor.execute(
        f"UPDATE user " f"SET {columns} " f"WHERE user_id = {user_id}", values
    )
    connection.commit()


def get_user_by_user_id(
    user_id: str,
    cursor: sqlite3.Cursor = base_cursor,
) -> Optional[models.User]:
    sql = """
            SELECT *
            FROM user
            WHERE user_id = ?
        """

    cursor.execute(sql, (user_id,))
    row = cursor.fetchone()
    if row is not None:
        user = models.User(*row)
        return user

    return None


def get_all_users(
    cursor: sqlite3.Cursor = base_cursor,
) -> Optional[List[models.User]]:
    sql = "SELECT * FROM user"
    cursor.execute(sql)
    rows = cursor.fetchall()
    if rows:
        return [models.User(row) for row in rows]

    return None


# FOR DEBUGGING
def imitate_trial_period_end(
    user_id: str,
    cursor: sqlite3.Cursor = base_cursor,
    connection: sqlite3.Connection = base_con,
):
    date = datetime.datetime.now().replace(microsecond=0)
    logger.debug(f"New trial end date: {date}")
    cursor.execute(
        f"UPDATE user SET trial_end_date = ? WHERE user_id = {user_id}",
        (date,),
    )
    connection.commit()


# =============== search_query ===============


def rows_to_search_query_model(rows: List[Tuple]) -> List[models.SearchQuery]:
    queries = []

    for row in rows:
        subscription_last_day = None
        payment_last_day = None
        if row[7] is not None:
            subscription_last_day = dates.sqlite_date_to_datetime(row[7])
        if row[8] is not None:
            payment_last_day = dates.sqlite_date_to_datetime(row[8])

        search_query = models.SearchQuery(
            id=row[0],
            user_id=row[1],
            search_string=row[2],
            location=row[3],
            min_price=row[4],
            max_price=row[5],
            created_at=dates.sqlite_date_to_datetime(row[6]),
            subscription_last_day=subscription_last_day,
            payment_last_day=payment_last_day,
            deleted=bool(row[9]),
        )
        queries.append(search_query)

    return queries


def insert_new_search_query(
    column_values: Dict,
    connection: sqlite3.Connection = base_con,
    cursor: sqlite3.Cursor = base_cursor,
):
    columns = ", ".join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join("?" * len(column_values.keys()))
    cursor.executemany(
        f"INSERT INTO search_query "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values,
    )
    connection.commit()


def update_search_query(
    query_id: int,
    column_values: Dict,
    connection: sqlite3.Connection = base_con,
    cursor: sqlite3.Cursor = base_cursor,
):
    columns = " = ? ,".join(column_values.keys())
    columns += " = ?"

    values = tuple(column_values.values())
    cursor.execute(
        f"UPDATE search_query SET {columns} WHERE id = {query_id}", values
    )
    connection.commit()


def get_all_search_queries(
    cursor: sqlite3.Cursor = base_cursor,
) -> List[models.SearchQuery]:
    sql = "SELECT * FROM search_query"
    cursor.execute(sql)
    rows = cursor.fetchall()

    return rows_to_search_query_model(rows)


def get_all_search_queries_by_user_id(
    user_id: str,
    cursor: sqlite3.Cursor = base_cursor,
) -> List[models.SearchQuery]:
    sql = """
        SELECT *
        FROM search_query
        WHERE user_id = ?
    """

    cursor.execute(sql, (user_id,))
    rows = cursor.fetchall()

    return [models.SearchQuery(*row) for row in rows]


def get_all_active_search_queries(
    date: datetime.datetime,
    cursor: Optional[sqlite3.Cursor] = base_cursor,
) -> List[models.SearchQuery]:
    sql = """
            SELECT *
            FROM search_query
            WHERE subscription_last_day > ?"""
    cursor.execute(sql, (str(date),))
    rows = cursor.fetchall()

    return rows_to_search_query_model(rows)


def get_all_active_search_queries_by_user_id(
    user_id: str,
    date: datetime.datetime,
    cursor: Optional[sqlite3.Cursor] = base_cursor,
) -> List[models.SearchQuery]:
    logger.info(f"{date}: {str(date)}")
    sql = """
            SELECT *
            FROM search_query
            WHERE user_id = ?
            AND (subscription_last_day > ?)
        """
    cursor.execute(sql, (user_id, str(date)))
    rows = cursor.fetchall()

    return rows_to_search_query_model(rows)


# =============== results ===============


def rows_to_result_model(rows: List[tuple]) -> List[models.Result]:
    results = []

    for row in rows:
        print(f"row: {row}")
        result = models.Result(
            search_string=row[1],
            publish_date=dates.sqlite_date_to_datetime(row[2]),
            finish_date=dates.sqlite_date_to_datetime(row[3]),
            number_of_purchase=row[4],
            subject_of_purchase=row[5],
            price=row[6],
            link=row[7],
            customer=row[8],
            location=row[9],
            query_id=row[10],
        )
        results.append(result)

    return results


# Атрибуты класса Result и query_id
def get_result_columns_name() -> tuple:
    return (
        "search_string",
        "number_of_purchase",
        "publish_date",
        "finish_date",
        "price",
        "subject_of_purchase",
        "link",
        "customer",
        "location",
        "query_id",
    )


def insert_results(
    column_values: Dict[int, List[models.Result]],
    connection: sqlite3.Connection = base_con,
    cursor: sqlite3.Cursor = base_cursor,
):
    columns = get_result_columns_name()
    placeholders = ", ".join("?" * len(columns))

    values = []
    for query_id, result in column_values.items():
        if not result:
            continue
        tmp = [(*res.to_tuple(), query_id) for res in result]
        values.append(*tmp)

    cursor.executemany(
        f"INSERT INTO result" f"{columns} " f"VALUES ({placeholders})",
        values,
    )

    connection.commit()


def get_all_results(cursor: Optional[sqlite3.Cursor] = base_cursor):
    sql = """SELECT * FROM result"""
    cursor.execute(sql)
    rows = cursor.fetchall()

    return rows_to_result_model(rows)


if __name__ == "__main__":
    check_db_exists()
