import os
import sqlite3
from sqlite3 import Error
from typing import Dict, List

from loguru import logger

from bot_zakupki.common import consts


def create_connection(path):
    conn = None
    try:
        conn = sqlite3.connect(path)
        logger.info("Connection to SQLite DB successful")
    except Error as e:
        logger.exception(f"The error '{e}' occurred")
    return conn


def insert_one_in_search_query(cursor: sqlite3.Cursor, column_values: Dict):
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join("?" * len(column_values.keys()))
    cursor.executemany(
        f"INSERT INTO search_query "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    # conn.commit()


def get_all_search_queries(cursor: sqlite3.Cursor) -> List[Dict]:
    sql = "SELECT * FROM search_query"
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows


# def delete(table: str, row_id: int) -> None:
#     row_id = int(row_id)
#     cursor.execute(f"delete from {table} where id={row_id}")
#     conn.commit()
#
#
# def get_cursor():
#     return cursor


def _init_db(cursor: sqlite3.Cursor, path_to_migrations: str = consts.PATH_TO_MIGRATIONS):
    """Инициализирует БД"""
    migrations = os.listdir(path_to_migrations)
    migrations = [os.path.join(path_to_migrations, mig) for mig in migrations]
    logger.info(f"migrations: {migrations}")
    for migration in migrations:
        with open(migration, "r") as f:
            sql = f.read()
        cursor.executescript(sql)
        # connection.commit()


def check_db_exists(path_to_db: str = consts.PATH_TO_DB):
    """Проверяет, инициализирована ли БД, если нет — инициализирует"""
    connection = create_connection(path_to_db)
    cursor = connection.cursor()

    for table_name in consts.TABLES_NAME:
        cursor.execute("SELECT name FROM sqlite_master "
                       f"WHERE type='table' AND name='{table_name}'")
        table_exists = cursor.fetchall()
        if not table_exists:
            _init_db(cursor)


check_db_exists()
