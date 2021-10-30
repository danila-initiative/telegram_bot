import dataclasses
import datetime
import typing

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
    number_of_active_search_queries: int
    number_of_search_queries: int
    downtime_notification: bool


@dataclasses.dataclass(frozen=True)
class SearchQuery:
    id: int
    user_id: str
    search_string: str
    location: str
    created_at: datetime.datetime
    subscription_last_day: datetime.datetime
    payment_last_day: datetime.datetime
    deleted: bool
    min_price: typing.Optional[int] = None
    max_price: typing.Optional[int] = None


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
    location: str


@dataclasses.dataclass()
class RequestParameters:
    search_string: str  # современная школа
    place_name: str  # Москва
    publish_date_from: typing.Optional[str]  # 06.08.2021
    publish_date_to: typing.Optional[str]  # 07.08.2021
    close_date_from: typing.Optional[str]  # 08.08.2021
    close_date_to: typing.Optional[str]  # 09.08.2021
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
