import datetime
from pathlib import Path

from loguru import logger

from bot_zakupki.common import consts
from bot_zakupki.common import dates
from bot_zakupki.common import db
from bot_zakupki.common import utils


def start_saving():
    now = dates.get_current_date()
    delta = consts.PUBLISH_DELTA
    if now.isoweekday() == 1:
        delta = 3

    publish_since = now + datetime.timedelta(days=delta)

    results = db.get_all_results_since(publish_since)

    if not results:
        logger.warning(f"There is no results today {dates.get_today_date()}")

    df = utils.convert_results_to_df(results)

    _create_folders_for_today_results(query_ids=df['query_id'].unique())

    df1 = [x for _, x in df.groupby(df['query_id'])]
    for x in df1:
        common_part = f"{consts.RESULTS_PATH}/{dates.get_today_date()}/"
        # TODO: сформировать имя файла: дата_количество закупок_ключевое слово
        path = common_part + f"{x.iloc[0, 0]}" + "/1.xlsx"
        utils.save_df_to_excel(x.iloc[:, 1:], path)


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

    start_saving()
