from typing import Dict, List
from loguru import logger

import sqlite3
from sqlite3 import Error

from bot_zakupki.common import consts

# TODO: вроде хороший коннекшн. Заменить print на логирование и использовать в других функциях
# и вроде даже путь не нужен


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        logger.info("Connection to SQLite DB successful")
    except Error as e:
        logger.exception(f"The error '{e}' occurred")
    return connection


# with open('scheduling.sql', 'r') as sql_file:
#     sql_script = sql_file.read()
#
# storage = sqlite3.connect('scheduling.storage')
# cursor = storage.cursor()
# cursor.executescript(sql_script)
# storage.commit()
# storage.close()

conn = sqlite3.connect('/app/db/zakupki.db')
cursor = conn.cursor()


def insert(table_name: str, column_values: Dict):
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join("?" * len(column_values.keys()))
    cursor.executemany(
        f"INSERT INTO {table_name} "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    conn.commit()


def fetchall(table: str, columns: List[str]) -> List[Dict]:
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table}")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


def delete(table: str, row_id: int) -> None:
    row_id = int(row_id)
    cursor.execute(f"delete from {table} where id={row_id}")
    conn.commit()


def get_cursor():
    return cursor


def _init_db():
    """Инициализирует БД"""
    with open("./bot_zakupki/storage/migrations/createdb.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def check_db_exists():
    """Проверяет, инициализирована ли БД, если нет — инициализирует"""
    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE type='table' AND name='results'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()


check_db_exists()
new_queries = {
    "user_id": 123,
    "search_string": "one"
}

insert("search_query", new_queries)
res = fetchall("search_query", ["id", "user_id", "search_string", "created_at"])
print(res)
