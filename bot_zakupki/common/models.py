import dataclasses
import datetime
import typing
from enum import Enum

from bot_zakupki.common import dates

RESULT_PUBLISH_DATE = "publish_date"
RESULT_FINISH_DATE = "finish_date"
RESULT_NUMBER_OF_PURCHASE = "number_of_purchase"
RESULT_SUBJECT_OF_PURCHASE = "subject_of_purchase"
RESULT_PRICE = "price"
RESULT_LINK = "link"
RESULT_CUSTOMER = "customer"
RESULT_QUERY_ID = "query_id"


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


class TrialPeriodState(str, Enum):
    HAS_NOT_STARTED = "trial_period_has_not_started"
    TRIAL_PERIOD = "trial_period"
    IS_OVER = "trial_period_is_over"


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
    last_updated_at: datetime.datetime

    def __init__(
        self,
        unique_id: int,
        user_id: str,
        search_string: str,
        location: str,
        min_price: int,
        max_price: int,
        created_at: typing.Union[str, datetime.datetime],
        last_updated_at: typing.Union[str, datetime.datetime],
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
        if type(last_updated_at) == str:
            self.last_updated_at = dates.sqlite_date_to_datetime(
                last_updated_at
            )
        elif type(last_updated_at) == datetime.datetime:
            self.last_updated_at = last_updated_at


class MaxPriceValidation(str, Enum):
    NOT_A_NUMBER = "not_a_number"
    LESS_THAT_MIN_PRICE = "less_than_min_price"
    VALID = "valid"


@dataclasses.dataclass()
class Result:
    publish_date: datetime.datetime
    finish_date: datetime.datetime
    number_of_purchase: str
    subject_of_purchase: str
    price: int
    link: str
    customer: str

    @staticmethod
    def get_result_columns_name() -> tuple:
        return (
            RESULT_PUBLISH_DATE,
            RESULT_FINISH_DATE,
            RESULT_NUMBER_OF_PURCHASE,
            RESULT_SUBJECT_OF_PURCHASE,
            RESULT_PRICE,
            RESULT_LINK,
            RESULT_CUSTOMER,
            RESULT_QUERY_ID,
        )


@dataclasses.dataclass()
class ResultDB:
    unique_id: int
    query_id: int
    publish_date: datetime.datetime
    finish_date: datetime.datetime
    number_of_purchase: str
    subject_of_purchase: str
    price: int
    link: str
    customer: typing.Optional[str]

    def __init__(
        self,
        unique_id: int,
        publish_date: typing.Union[str, datetime.datetime],
        finish_date: typing.Union[str, datetime.datetime],
        number_of_purchase: str,
        subject_of_purchase: str,
        price: int,
        link: str,
        customer: str,
        query_id: int,
    ):
        self.unique_id = unique_id
        if type(publish_date) == str:
            self.publish_date = dates.sqlite_date_to_datetime(publish_date)
        elif type(publish_date) == datetime.datetime:
            self.publish_date = publish_date
        if type(finish_date) == str:
            self.finish_date = dates.sqlite_date_to_datetime(finish_date)
        elif type(finish_date) == datetime.datetime:
            self.finish_date = finish_date
        self.number_of_purchase = number_of_purchase
        self.subject_of_purchase = subject_of_purchase
        self.price = price
        self.link = link
        self.customer = customer
        self.query_id = query_id


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
            ("searchString", self.prepare_search_string(self.search_string)),
            ("priceFromGeneral", str(self.min_price)),
            ("priceToGeneral", str(self.max_price)),
            ("customerPlace", CUSTOMER_PLACES.get(self.place_name)),
            ("publishDateFrom", self.publish_date_from),
            ("publishDateTo", self.publish_date_to),
            ("applSubmissionCloseDateFrom", self.close_date_from),
            ("applSubmissionCloseDateTo", self.close_date_to),
        ]

    @staticmethod
    def prepare_search_string(raw_string: str) -> str:
        search_list = raw_string.split()
        search_string = "+".join(search_list)

        return search_string
