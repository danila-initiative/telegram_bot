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


# ===============Common===============


def get_connection_cursor(
        path_to_db: str = consts.PATH_TO_DB,
):
    connection = sqlite3.connect(path_to_db)
    logger.info("Connection to SQLite DB successful")
    cursor = connection.cursor()
    logger.info("Cursor to SQLite DB successful")

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


def rows_to_user_model(rows: List[Tuple]) -> List[models.User]:
    users = []

    for row in rows:
        trial_start_date = None
        trial_end_date = None
        if row[5] is not None or row[6] is not None:
            trial_start_date = dates.sqlite_date_to_datetime(row[5])
            trial_end_date = dates.sqlite_date_to_datetime(row[6])
        user = models.User(
            id=row[0],
            user_id=row[1],
            first_bot_start_date=row[2],
            bot_start_date=row[3],
            bot_is_active=bool(row[4]),
            trial_start_date=trial_start_date,
            trial_end_date=trial_end_date,
            number_of_sending=row[7],
            number_of_active_search_queries=row[8],
            number_of_search_queries=row[9],
            downtime_notification=bool(row[10]),
        )
        users.append(user)

    return users


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
        return rows_to_user_model([row])[0]

    return None


def get_all_users(
        cursor: sqlite3.Cursor = base_cursor,
) -> Optional[List[models.User]]:
    sql = "SELECT * FROM user"
    cursor.execute(sql)
    rows = cursor.fetchall()
    if rows:
        return rows_to_user_model(rows)

    return None


# =============== search_query ===============


def rows_to_search_query_model(rows: List[Tuple]) -> List[models.SearchQuery]:
    queries = []

    for row in rows:
        search_query = models.SearchQuery(
            id=row[0],
            user_id=row[1],
            search_string=row[2],
            location=row[3],
            min_price=row[4],
            max_price=row[5],
            created_at=dates.sqlite_date_to_datetime(row[6]),
            subscription_last_day=dates.sqlite_date_to_datetime(row[7]),
            payment_last_day=dates.sqlite_date_to_datetime(row[8]),
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

    return rows_to_search_query_model(rows)


def get_all_active_search_queries_by_user_id(
        user_id: str,
        date: datetime.datetime,
        cursor: Optional[sqlite3.Cursor] = None,
) -> List[models.SearchQuery]:
    if cursor is None:
        connection, cursor = get_connection_cursor()
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


if __name__ == "__main__":
    check_db_exists()
