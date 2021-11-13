import dataclasses
import datetime
import typing
from enum import Enum

CUSTOMER_PLACES = {
    "Москва": "5277335",
    "Московская область": "5277327",
    "Дальневосточный федеральный округ": "5277399",
    "Приволжский федеральный округ": "5277362",
    "Северо-Западный федеральный округ": "5277336",
    "Северо-Кавказский федеральный округ": "9409197",
    "Сибирский федеральный округ": "5277384",
    "Уральский федеральный округ": "5277377",
    "Центральный федеральный округ": "5277317",
    "Южный федеральный округ": "6325041",
}


@dataclasses.dataclass(frozen=True)
class User:
    id: int
    user_id: str
    first_bot_start_date: datetime.datetime
    bot_start_date: datetime.datetime
    bot_is_active: bool
    trial_start_date: typing.Optional[datetime.datetime]
    trial_end_date: typing.Optional[datetime.datetime]
    number_of_sending: int
    downtime_notification: bool


@dataclasses.dataclass(frozen=True)
class SearchQuery:
    id: int
    user_id: str
    search_string: str
    location: str
    created_at: datetime.datetime
    subscription_last_day: typing.Optional[datetime.datetime]
    payment_last_day: typing.Optional[datetime.datetime]
    deleted: bool
    min_price: typing.Optional[int]
    max_price: typing.Optional[int]


class TrialPeriodState(str, Enum):
    TRIAL_PERIOD_HAS_NOT_STARTED = "trial_period_has_not_started"
    TRIAL_PERIOD = "trial_period"
    TRIAL_PERIOD_IS_OVER = "trial_period_is_over"


class MaxPriceValidation(str, Enum):
    NOT_A_NUMBER = "not_a_number"
    LESS_THAT_MIN_PRICE = "less_than_min_price"
    VALID = "valid"


@dataclasses.dataclass(frozen=True)
class Result:
    search_string: str
    publish_date: datetime.datetime
    finish_date: datetime.datetime
    number_of_purchase: str
    subject_of_purchase: str
    price: int
    link: str
    customer: str
    location: typing.Union[str, None] = None
    query_id: typing.Union[int, None] = None

    def to_tuple(self):
        return (
            self.search_string,
            self.number_of_purchase,
            self.publish_date,
            self.finish_date,
            self.price,
            self.subject_of_purchase,
            self.link,
            self.customer,
            self.location,
        )


@dataclasses.dataclass()
class RequestParameters:
    search_string: str  # современная школа
    place_name: str  # Москва
    publish_date_from: typing.Optional[str]  # 06.08.2021
    publish_date_to: typing.Optional[str]  # 07.08.2021
    close_date_from: typing.Optional[str] = None  # 08.08.2021
    close_date_to: typing.Optional[str] = None  # 09.08.2021
    min_price: typing.Optional[int] = None  # 100000
    max_price: typing.Optional[int] = None  # 500000

    def to_list(self) -> list:
        return [
            ("searchString", prepare_search_string(self.search_string)),
            ("priceFromGeneral", str(self.min_price)),
            ("priceToGeneral", str(self.max_price)),
            ("customerPlace", CUSTOMER_PLACES.get(self.place_name)),
            ("publishDateFrom", self.publish_date_from),
            ("publishDateTo", self.publish_date_to),
            ("applSubmissionCloseDateFrom", self.close_date_from),
            ("applSubmissionCloseDateTo", self.close_date_to),
        ]


def prepare_search_string(raw_string: str) -> str:
    search_list = raw_string.split()
    search_string = "+".join(search_list)

    return search_string
