from datetime import datetime, timedelta
from typing import NamedTuple

from dateutil import tz

import consts


class RequestDates(NamedTuple):
    publish_date: str
    close_date: str

def GetRequestDates(publish_delta=consts.PUBLISH_DELTA,
                    close_delta=consts.CLOSE_DELTA) -> RequestDates:

    today = GetCurrentDate()

    pub_delta = timedelta(days=publish_delta)
    pub_day = today + pub_delta
    while not IsWorkDayToday(pub_day):
        pub_day = pub_day + timedelta(days=-1)

    close_delta = timedelta(days=close_delta)
    close_day = today + close_delta
    while not IsWorkDayToday(close_day):
        close_day = close_day + timedelta(days=1)

    return RequestDates(publish_date=FormatDateForURL(pub_day),
                        close_date=FormatDateForURL(close_day))


def GetCurrentDate(time_zone=consts.TIME_ZONE) -> datetime:
    # example: 2021-07-09 19:20:22.657220+03:00

    current_tz = tz.gettz(time_zone)
    return datetime.now(tz=current_tz)


def FormatDate(current_date: datetime):
    # example: 2021-08-08

    return current_date.date().strftime("%Y-%m-%d")

def FormatDateForURL(current_date: datetime):
    # example: 06.08.2021

    return current_date.date().strftime("%d.%m.%Y")


def IsWorkDayToday(date: datetime) -> bool:
    work_days = [1, 2, 3, 4, 5]
    day_number = date.date().isoweekday()
    if day_number in work_days:
        return True
    return False


if __name__ == "__main__":
    pass
    # Список названий всех таймзон
    # zonenames = list(get_zonefile_instance().zones)
