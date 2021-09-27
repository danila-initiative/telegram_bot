import datetime

from bot_zakupki.common import consts


def sqlite_date_to_datetime(date: str) -> datetime.datetime:
    return datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')


def res_date_to_datetime(date: str) -> datetime.datetime:
    return datetime.datetime.strptime(date, '%d.%m.%Y')


def get_date_with_delta_for_request(publish_delta=consts.PUBLISH_DELTA) -> str:
    # return first working day with shift from today
    # today: 07.08.2021
    # return: 06.08.2021

    today = get_current_date()

    pub_delta = datetime.timedelta(days=publish_delta)
    pub_day = today + pub_delta
    while not is_working_day(pub_day):
        pub_day = pub_day + datetime.timedelta(days=-1)

    return pub_day.date().strftime("%d.%m.%Y")


def get_current_date() -> datetime.datetime:
    # example: 2021-07-09 19:20:22.657220+03:00

    return datetime.datetime.now(tz=datetime.timezone.utc)


def format_date(current_date: datetime.datetime) -> str:
    # example: 2021-08-08

    return current_date.date().strftime("%Y-%m-%d")


def is_working_day(date: datetime.datetime) -> bool:
    work_days = [1, 2, 3, 4, 5]
    day_number = date.date().isoweekday()
    if day_number in work_days:
        return True
    return False
