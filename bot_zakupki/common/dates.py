import datetime


def sqlite_date_to_datetime(date: str) -> datetime.datetime:
    return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")


def sql_date_to_datetime_date(date: str) -> datetime.datetime:
    return datetime.datetime.strptime(date, "%Y-%m-%d")


def res_date_to_datetime(date: str) -> datetime.date:
    return datetime.datetime.strptime(date, "%d.%m.%Y").date()


def get_current_time_db_format(date: datetime.datetime = None) -> str:
    if date is None:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        return date.strftime("%Y-%m-%d %H:%M:%S")


def format_date(current_date: datetime.datetime) -> str:
    # example: 2021-08-08

    return current_date.date().strftime("%Y-%m-%d")


def format_date_date(current_date: datetime.date) -> str:
    # example: 2021-08-08

    return current_date.strftime("%Y-%m-%d")


def format_date_for_request(date: datetime.datetime) -> str:
    # example: 04.11.2021

    return date.date().strftime("%d.%m.%Y")


def get_date_for_request(days_delta: int) -> str:
    # example: 04.11.2021

    now = get_current_time_for_db()
    publish_date = now + datetime.timedelta(days=days_delta)

    return format_date_for_request(publish_date)


def format_date_for_msg(date: datetime.datetime) -> str:
    # example: 04.11.2021

    return date.date().strftime("%d.%m.%Y")


def get_current_time_for_db():
    return datetime.datetime.now().replace(microsecond=0)


def get_current_date():
    return datetime.datetime.now().date()


def get_now_without_ms():
    return datetime.datetime.now().replace(microsecond=0)


def get_today_date():
    # example: 2021-08-08

    return format_date(datetime.datetime.now())


def is_working_day(date: datetime.datetime) -> bool:
    work_days = [1, 2, 3, 4, 5]
    day_number = date.date().isoweekday()
    if day_number in work_days:
        return True
    return False
