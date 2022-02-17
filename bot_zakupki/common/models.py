import dataclasses
import datetime
import os
import typing
from enum import Enum

import yaml

from bot_zakupki.common import consts
from bot_zakupki.common import dates


class Region:
    MOSCOW_MOSCOW_REGION = "Москва и Московская область"
    FAR_EASTERN_FEDERAL_DISTRICT = "Дальневосточный федеральный округ"
    VOLGA_FEDERAL_DISTRICT = "Приволжский федеральный округ"
    NORTHWESTERN_FEDERAL_DISTRICT = "Северо-Западный федеральный округ"
    NORTH_CAUCASIAN_FEDERAL_DISTRICT = "Северо-Кавказский федеральный округ"
    SIBERIAN_FEDERAL_DISTRICT = "Сибирский федеральный округ"
    URAL_FEDERAL_DISTRICT = "Уральский федеральный округ"
    CENTRAL_FEDERAL_DISTRICT = "Центральный федеральный округ"
    SOUTHERN_FEDERAL_DISTRICT = "Южный федеральный округ"


CUSTOMER_PLACES = {
    Region.MOSCOW_MOSCOW_REGION: "5277335%2C5277327",
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
    publish_date: datetime.date
    finish_date: datetime.date
    number_of_purchase: str
    subject_of_purchase: str
    price: int
    link: str
    customer: str

    @staticmethod
    def get_result_columns_name() -> tuple:
        return (
            consts.RESULT_PUBLISH_DATE,
            consts.RESULT_FINISH_DATE,
            consts.RESULT_NUMBER_OF_PURCHASE,
            consts.RESULT_SUBJECT_OF_PURCHASE,
            consts.RESULT_PRICE,
            consts.RESULT_LINK,
            consts.RESULT_CUSTOMER,
            consts.RESULT_QUERY_ID,
        )


@dataclasses.dataclass()
class ResultDB:
    unique_id: int
    query_id: int
    publish_date: datetime.date
    finish_date: datetime.date
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
            self.publish_date = dates.sql_date_to_datetime_date(publish_date)
        elif type(publish_date) == datetime.datetime:
            self.publish_date = publish_date
        if type(finish_date) == str:
            self.finish_date = dates.sql_date_to_datetime_date(finish_date)
        elif type(finish_date) == datetime.datetime:
            self.finish_date = finish_date
        self.number_of_purchase = number_of_purchase
        self.subject_of_purchase = subject_of_purchase
        self.price = price
        self.link = link
        self.customer = customer
        self.query_id = query_id

    def to_list_for_df(self) -> list:
        return [
            self.query_id,
            self.number_of_purchase,
            self.subject_of_purchase,
            self.price,
            dates.format_date_date(self.finish_date),
            self.link,
        ]


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

    def to_dict(self) -> dict:
        return {
            "searchString": self.prepare_search_string(self.search_string),
            "priceFromGeneral": str(self.min_price),
            "priceToGeneral": str(self.max_price),
            # "customerPlace": CUSTOMER_PLACES.get(self.place_name),
            "delKladrIds": CUSTOMER_PLACES.get(self.place_name),
            "publishDateFrom": self.publish_date_from,
            "publishDateTo": self.publish_date_to,
            "applSubmissionCloseDateFrom": self.close_date_from,
            "applSubmissionCloseDateTo": self.close_date_to,
        }

    @staticmethod
    def prepare_search_string(raw_string: str) -> str:
        search_list = raw_string.split()
        search_string = "+".join(search_list)

        return search_string


# ========== Config ==========
@dataclasses.dataclass()
class QueryLimitsConf:
    max_queries_in_trial_period: int
    max_queries_in_common_period: int


@dataclasses.dataclass()
class SearchParametersConf:
    base_url: str
    publish_delts: int
    close_delta: int


@dataclasses.dataclass()
class PathsConf:
    to_migrations: str
    to_price_table: str
    to_bot_logs: str
    to_cron_logs: str
    to_db: str


@dataclasses.dataclass()
class Config:
    email_support: str
    trial_period_days: int
    query_limits: QueryLimitsConf
    search_parameters: SearchParametersConf
    paths: PathsConf
    price: dict

    def __init__(self):
        with open("bot_zakupki/config.yaml", "r") as file:
            config = yaml.safe_load(file)
        self.email_support = config["email_support"]
        self.trial_period_days = config["trial_period_days"]

        query_limits = config["query_limits"]
        self.query_limits = QueryLimitsConf(
            max_queries_in_trial_period=query_limits[
                "max_queries_in_trial_period"
            ],
            max_queries_in_common_period=query_limits[
                "max_queries_in_common_period"
            ],
        )

        search_parameters = config["search_parameters"]
        self.search_parameters = SearchParametersConf(
            base_url=search_parameters["base_url"],
            publish_delts=search_parameters["base_url"],
            close_delta=search_parameters["close_delta"],
        )

        paths = config["paths"]
        self.paths = PathsConf(
            to_migrations=paths["to_migrations"],
            to_price_table=paths["to_price_table"],
            to_bot_logs=paths["to_bot_logs"],
            to_cron_logs=paths["to_cron_logs"],
            to_db=paths["to_db"],
        )
        self._correct_path_to_db(config)

        self._set_price(config)

    def _correct_path_to_db(self, config):
        test = os.getenv("TEST")
        if test in ["True", "true"]:
            paths = config["testing"]["paths"]
            self.paths.to_bot_logs = paths["to_bot_logs"]
            self.paths.to_cron_logs = paths["to_cron_logs"]
            self.paths.to_db = paths["to_db"]

    def _set_price(self, config):
        debug = os.getenv("DEBUG")
        if debug in ["False", "false"]:
            self.price = config["production"]["price"]
        else:
            self.price = config["debugging"]["price"]
