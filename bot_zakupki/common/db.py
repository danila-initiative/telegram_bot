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


def check_db_exists(
        cursor: sqlite3.Cursor = base_cursor):
    """Проверяет, инициализирована ли БД, если нет — инициализирует"""
    for table_name in consts.TABLES_NAME:
        cursor.execute(
            "SELECT name FROM sqlite_master "
            f"WHERE type='table' AND name='{table_name}'"
        )
        table_exists = cursor.fetchall()
        if not table_exists:
            init_db()


# ===============search_query===============


def rows_to_search_query_model(rows: List[Tuple]) -> List[models.SearchQuery]:
    result = []

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
        result.append(search_query)

    return result


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


def get_all_search_queries(cursor: sqlite3.Cursor = base_cursor) \
        -> List[models.SearchQuery]:
    sql = "SELECT * FROM search_query"
    cursor.execute(sql)
    rows = cursor.fetchall()

    return rows_to_search_query_model(rows)


def get_all_search_queries_by_user_id(
        user_id: str, cursor: Optional[sqlite3.Cursor] = None
) -> List[models.SearchQuery]:
    sql = """
        SELECT *
        FROM search_query
        WHERE user_id = ?
    """

    if cursor is None:
        connection, cursor = get_connection_cursor()
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
