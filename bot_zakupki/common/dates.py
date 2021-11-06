import datetime


def sqlite_date_to_datetime(date: str) -> datetime.datetime:
    return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")


def res_date_to_datetime(date: str) -> datetime.datetime:
    return datetime.datetime.strptime(date, "%d.%m.%Y")


def format_date(current_date: datetime.datetime) -> str:
    # example: 2021-08-08

    return current_date.date().strftime("%Y-%m-%d")


def format_date_for_request(date: datetime.datetime) -> str:
    # example: 04.11.2021

    return date.date().strftime("%d.%m.%Y")


def get_current_time_for_db():
    return datetime.datetime.now().replace(microsecond=0)


def get_today_date():
    return format_date(datetime.datetime.now())


def is_working_day(date: datetime.datetime) -> bool:
    work_days = [1, 2, 3, 4, 5]
    day_number = date.date().isoweekday()
    if day_number in work_days:
        return True
    return False
