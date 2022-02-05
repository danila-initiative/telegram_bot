import datetime
from pathlib import Path

from loguru import logger

from bot_zakupki.common import consts
from bot_zakupki.common import dates
from bot_zakupki.common import db
from bot_zakupki.common import utils


def start_converting():
    publish_since = _get_date_for_results()

    results = db.get_all_results_since(publish_since)

    if not results:
        logger.warning(f"There is no results today {dates.get_today_date()}")
        # TODO: send message in admin chat/bot
        return

    df = utils.convert_results_to_df(results)

    query_ids = df['query_id'].unique().tolist()
    id_string_dict = _get_query_id_search_string_dict(query_ids)

    _create_folders_for_today_results(query_ids=query_ids)

    # группируем результаты по запросам
    dfs = [x for _, x in df.groupby(df['query_id'])]

    for query_df in dfs:
        full_file_path = _file_path_formation(
            query_id=query_df.iloc[0, 0],
            results_number=query_df.shape[0],
            search_string=id_string_dict[query_df.iloc[0, 0]])

        utils.save_df_to_excel(query_df.iloc[:, 1:], full_file_path)


def _file_path_formation(query_id: str, results_number: int, search_string: str):
    common_path = f"{consts.RESULTS_PATH}/{dates.get_today_date()}/{query_id}/"
    date = dates.get_today_date()
    file_name = f"{date}_[{results_number}]_{search_string}.xlsx"

    return common_path + file_name


def _get_query_id_search_string_dict(query_ids: list[int]):
    query_ids_str = [str(id) for id in query_ids]

    search_strings = db.get_search_query_search_string(
        ", ".join(query_ids_str))

    id_string_dict = {}
    for string in search_strings:
        id_string_dict[string[0]] = string[1]

    return id_string_dict


# с какой даты присылать результаты
# либо за вчера, либо с пятницы, если рассылка в понедельник
def _get_date_for_results() -> datetime.date:
    now = dates.get_current_date()
    delta = consts.PUBLISH_DELTA
    if now.isoweekday() == 1:
        delta = 3

    return now + datetime.timedelta(days=delta)


def _create_folders_for_today_results(query_ids):
    common_part = f"{consts.RESULTS_PATH}/{dates.get_today_date()}/"
    path_parts = []
    for query_id in query_ids:
        path_parts.append(common_part + f"{query_id}")

    for path in path_parts:
        Path(path).mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    logger.remove()
    if consts.DEBUG:
        logger.add(
            f"{consts.CRONS_LOG_FOLDER}{dates.get_today_date()}.log",
            level="DEBUG",
            backtrace=True,
            diagnose=True,
        )
    else:
        logger.add(
            f"{consts.CRONS_LOG_FOLDER}{dates.get_today_date()}.log",
            level="INFO",
        )

    start_converting()
