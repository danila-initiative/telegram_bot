import datetime
import os
import sqlite3
from dataclasses import astuple
from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional

from loguru import logger

from bot_zakupki.common import consts
from bot_zakupki.common import dates
from bot_zakupki.common import models


# ===============Common===============
@dataclass
class DBService:
    connection: sqlite3.Connection
    cursor: sqlite3.Cursor


def get_connection_cursor():
    config = models.Config()
    # logger.info(f"path_to_DB: {config.paths.to_db}")
    connection = sqlite3.connect(config.paths.to_db)
    cursor = connection.cursor()

    return DBService(connection=connection, cursor=cursor)


def init_db():
    db_service: DBService = get_connection_cursor()
    config = models.Config()
    """Инициализирует БД"""
    migrations = os.listdir(config.paths.to_migrations)
    migrations = [
        os.path.join(config.paths.to_migrations, mig) for mig in migrations
    ]
    logger.info(f"migrations: {migrations}")
    for migration in migrations:
        with open(migration, "r") as f:
            sql = f.read()
        db_service.cursor.executescript(sql)
        db_service.connection.commit()


def check_db_exists():
    db_service: DBService = get_connection_cursor()
    """Проверяет, инициализирована ли БД, если нет — инициализирует"""
    for table_name in consts.TABLES_NAME:
        db_service.cursor.execute(
            "SELECT name FROM sqlite_master "
            f"WHERE type='table' AND name='{table_name}'"
        )
        table_exists = db_service.cursor.fetchall()
        if not table_exists:
            init_db()


# for tests
def delete_all_data():
    db_service: DBService = get_connection_cursor()
    for table_name in consts.TABLES_NAME:
        db_service.cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
    db_service.connection.commit()


# =============== user ===============


def insert_new_user(
    user_id: str,
):
    db_service: DBService = get_connection_cursor()
    db_service.cursor.execute(
        f"INSERT INTO user" f"(user_id) " f"VALUES ({user_id})",
    )
    db_service.connection.commit()


def update_user_by_user_id(
    user_id: str,
    column_values: Dict,
):
    db_service: DBService = get_connection_cursor()
    columns = " = ? ,".join(column_values.keys())
    columns += " = ?"

    values = tuple(column_values.values())
    db_service.cursor.execute(
        f"UPDATE user " f"SET {columns} " f"WHERE user_id = {user_id}", values
    )
    db_service.connection.commit()


def get_user_by_user_id(
    user_id: str,
) -> Optional[models.User]:
    db_service: DBService = get_connection_cursor()
    sql = """
            SELECT *
            FROM user
            WHERE user_id = ?
        """

    db_service.cursor.execute(sql, (user_id,))
    row = db_service.cursor.fetchone()

    db_service.connection.commit()

    if row is not None:
        user = models.User(*row)
        return user

    return None


def get_all_users() -> Optional[List[models.User]]:
    db_service: DBService = get_connection_cursor()
    sql = "SELECT * FROM user"
    db_service.cursor.execute(sql)
    rows = db_service.cursor.fetchall()

    db_service.connection.commit()

    if rows:
        return [models.User(*row) for row in rows]

    return None


# FOR DEBUGGING
def imitate_trial_period_end(
    user_id: str,
):
    db_service: DBService = get_connection_cursor()
    date = datetime.datetime.now().replace(microsecond=0) - datetime.timedelta(
        days=1
    )
    logger.debug(f"New {consts.USER_SUBSCRIPTION_LAST_DAY}: {date}")
    db_service.cursor.execute(
        f"UPDATE user SET {consts.USER_SUBSCRIPTION_LAST_DAY} = ? "
        f"WHERE {consts.USER_USER_ID} = {user_id}",
        (date,),
    )
    db_service.connection.commit()


# =============== search_query ===============


def insert_new_search_query(
    column_values: Dict,
):
    db_service: DBService = get_connection_cursor()
    columns = ", ".join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join("?" * len(column_values.keys()))
    db_service.cursor.executemany(
        f"INSERT INTO search_query "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values,
    )
    db_service.connection.commit()


def update_search_query(
    query_id: int,
    column_values: Dict,
):
    db_service: DBService = get_connection_cursor()
    columns = " = ? ,".join(column_values.keys())
    columns += " = ?"

    values = tuple(column_values.values())
    db_service.cursor.execute(
        f"UPDATE search_query SET {columns} WHERE id = {query_id}", values
    )
    db_service.connection.commit()


def get_all_active_search_queries() -> List[models.SearchQuery]:
    db_service: DBService = get_connection_cursor()
    date = dates.get_current_time_for_db()
    sql = """
        SELECT user.max_number_of_queries, search_query.*
        FROM user
        INNER JOIN search_query
        ON user.user_id = search_query.user_id
        WHERE user.subscription_last_day >= ?
        ORDER BY search_query.user_id, search_query.created_at
    """
    db_service.cursor.execute(sql, (date,))
    rows = db_service.cursor.fetchall()

    current_user_id = ""
    current_query_number = 1

    result = []

    for row in rows:
        max_number = row[0]
        query = models.SearchQuery(*row[1:])
        if query.user_id != current_user_id:
            current_user_id = query.user_id
            current_query_number = 1
        if current_query_number <= max_number:
            result.append(query)

        current_query_number += 1

    db_service.connection.commit()

    return result


def get_all_search_queries_by_user_id(
    user_id: str,
) -> List[models.SearchQuery]:
    db_service: DBService = get_connection_cursor()
    sql = """
        SELECT *
        FROM search_query
        WHERE user_id = ?
        ORDER BY created_at ASC
    """

    db_service.cursor.execute(sql, (user_id,))
    rows = db_service.cursor.fetchall()

    db_service.connection.commit()

    return [models.SearchQuery(*row) for row in rows]


def get_all_search_queries() -> List[models.SearchQuery]:
    db_service: DBService = get_connection_cursor()
    sql = "SELECT * FROM search_query"
    db_service.cursor.execute(sql)
    rows = db_service.cursor.fetchall()

    db_service.connection.commit()

    return [models.SearchQuery(*row) for row in rows]


def delete_search_query(query_id: int):
    db_service: DBService = get_connection_cursor()
    sql = """
            DELETE
            FROM search_query
            WHERE id = ?
        """

    db_service.cursor.execute(sql, (query_id,))

    db_service.connection.commit()
    db_service.connection.close()


def get_search_query_search_string(query_ids):
    db_service: DBService = get_connection_cursor()
    sql = """
            SELECT id, search_string
            FROM search_query
            WHERE id in (?);
        """
    query_ids = ",".join(query_ids)
    db_service.cursor.execute(sql, (query_ids,))
    rows = db_service.cursor.fetchall()

    db_service.connection.commit()

    return rows


# =============== results ===============


def insert_results(
    column_values: Dict[int, List[models.Result]],
):
    db_service: DBService = get_connection_cursor()

    columns = models.Result.get_result_columns_name()
    placeholders = ", ".join("?" * len(columns))

    values: list = []
    for query_id, result in column_values.items():
        if not result:
            continue
        tmp = [(*astuple(res), query_id) for res in result]
        values.extend(tmp)

    db_service.cursor.executemany(
        f"INSERT INTO result" f"{columns} " f"VALUES ({placeholders})",
        values,
    )

    db_service.connection.commit()


def get_all_results():
    db_service: DBService = get_connection_cursor()
    sql = """SELECT * FROM result"""
    db_service.cursor.execute(sql)
    rows = db_service.cursor.fetchall()

    db_service.connection.commit()

    return [models.ResultDB(*row) for row in rows]


def get_all_results_since(date: datetime.date):
    db_service: DBService = get_connection_cursor()
    sql = """
        SELECT * FROM result
        WHERE publish_date >= ?
    """

    db_service.cursor.execute(sql, (date,))
    rows = db_service.cursor.fetchall()

    db_service.connection.commit()
    return [models.ResultDB(*row) for row in rows]


if __name__ == "__main__":
    check_db_exists()
