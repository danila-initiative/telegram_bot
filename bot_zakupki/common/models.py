import dataclasses
import datetime
import typing
from enum import Enum

from bot_zakupki.common import dates


class Region:
    MOSCOW = "Москва"
    MOSCOW_REGION = "Московская область"
    FAR_EASTERN_FEDERAL_DISTRICT = "Дальневосточный федеральный округ"
    VOLGA_FEDERAL_DISTRICT = "Приволжский федеральный округ"
    NORTHWESTERN_FEDERAL_DISTRICT = "Северо-Западный федеральный округ"
    NORTH_CAUCASIAN_FEDERAL_DISTRICT = "Северо-Кавказский федеральный округ"
    SIBERIAN_FEDERAL_DISTRICT = "Сибирский федеральный округ"
    URAL_FEDERAL_DISTRICT = "Уральский федеральный округ"
    CENTRAL_FEDERAL_DISTRICT = "Центральный федеральный округ"
    SOUTHERN_FEDERAL_DISTRICT = "Южный федеральный округ"


CUSTOMER_PLACES = {
    Region.MOSCOW: "5277335",
    Region.MOSCOW_REGION: "5277327",
    Region.FAR_EASTERN_FEDERAL_DISTRICT: "5277399",
    Region.VOLGA_FEDERAL_DISTRICT: "5277362",
    Region.NORTHWESTERN_FEDERAL_DISTRICT: "5277336",
    Region.NORTH_CAUCASIAN_FEDERAL_DISTRICT: "9409197",
    Region.SIBERIAN_FEDERAL_DISTRICT: "5277384",
    Region.URAL_FEDERAL_DISTRICT: "5277377",
    Region.CENTRAL_FEDERAL_DISTRICT: "5277317",
    Region.SOUTHERN_FEDERAL_DISTRICT: "6325041",
}


@dataclasses.dataclass()
class User:
    unique_id: int
    user_id: str
    first_bot_start_date: datetime.datetime
    bot_start_date: datetime.datetime
    bot_is_active: bool
    max_number_of_queries: int
    subscription_last_day: typing.Optional[datetime.datetime] = None
    payment_last_day: typing.Optional[datetime.datetime] = None

    def __init__(
        self,
        unique_id: int,
        user_id: str,
        first_bot_start_date: str,
        bot_start_date: str,
        bot_is_active: int,
        max_number_of_queries: int,
        subscription_last_day: typing.Optional[str],
        payment_last_day: typing.Optional[str],
    ):
        self.unique_id = unique_id
        self.user_id = user_id
        self.first_bot_start_date = dates.sqlite_date_to_datetime(
            first_bot_start_date
        )
        self.bot_start_date = dates.sqlite_date_to_datetime(bot_start_date)
        self.bot_is_active = bool(bot_is_active)
        if subscription_last_day:
            self.subscription_last_day = dates.sqlite_date_to_datetime(
                subscription_last_day
            )
        if payment_last_day:
            self.payment_last_day = dates.sqlite_date_to_datetime(
                payment_last_day
            )
        self.max_number_of_queries = max_number_of_queries


@dataclasses.dataclass()
class SearchQuery:
    unique_id: int
    user_id: str
    search_string: str
    location: str
    min_price: int
    max_price: int
    created_at: datetime.datetime

    def __init__(
        self,
        unique_id: int,
        user_id: str,
        search_string: str,
        location: str,
        min_price: int,
        max_price: int,
        created_at: typing.Union[str, datetime.datetime],
    ):
        self.unique_id = unique_id
        self.user_id = user_id
        self.search_string = search_string
        self.location = location
        self.min_price = min_price
        self.max_price = max_price
        if type(created_at) == str:
            self.created_at = dates.sqlite_date_to_datetime(created_at)
        elif type(created_at) == datetime.datetime:
            self.created_at = created_at


class TrialPeriodState(str, Enum):
    HAS_NOT_STARTED = "trial_period_has_not_started"
    TRIAL_PERIOD = "trial_period"
    IS_OVER = "trial_period_is_over"


class MaxPriceValidation(str, Enum):
    NOT_A_NUMBER = "not_a_number"
    LESS_THAT_MIN_PRICE = "less_than_min_price"
    VALID = "valid"


@dataclasses.dataclass(frozen=True)
class Result:
    search_string: str
    number_of_purchase: str
    publish_date: datetime.datetime
    finish_date: datetime.datetime
    price: int
    subject_of_purchase: str
    link: str
    customer: str
    location: typing.Union[str, None] = None

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

    @staticmethod
    def get_result_columns_name() -> tuple:
        return (
            "search_string",
            "number_of_purchase",
            "publish_date",
            "finish_date",
            "price",
            "subject_of_purchase",
            "link",
            "customer",
            "location",
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
