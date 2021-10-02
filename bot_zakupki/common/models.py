import dataclasses
import datetime
import re
import typing

CUSTOMER_PLACES = {
    'Москва': '5277335',
    'Московская область': '5277327',
    'Дальневосточный федеральный округ': '5277399',
    'Приволжский федеральный округ': '5277362',
    'Северо-Западный федеральный округ': '5277336',
    'Северо-Кавказский федеральный округ': '9409197',
    'Сибирский федеральный округ': '5277384',
    'Уральский федеральный округ': '5277377',
    'Центральный федеральный округ': '5277317',
    'Южный федеральный округ': '6325041',
}


@dataclasses.dataclass(frozen=True)
class SearchQuery:
    id: int
    user_id: str
    search_string: str
    location: str
    min_price: int
    max_price: typing.Optional[int]
    created_at: datetime.datetime
    subscription_last_day: datetime.datetime
    payment_last_day: datetime.datetime
    deleted: bool


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
    min_price: int  # 100000
    max_price: int  # 500000
    place_name: str  # Москва
    publish_date_from: typing.Optional[str]  # 06.08.2021
    publish_date_to: typing.Optional[str]  # 07.08.2021
    close_date_from: typing.Optional[str]  # 08.08.2021
    close_date_to: typing.Optional[str]  # 09.08.2021

    def to_list(self):
        return [
            ('searchString', prepare_search_string(self.search_string)),
            ('priceFromGeneral', str(self.min_price)),
            ('priceToGeneral', str(self.max_price)),
            ('customerPlace', CUSTOMER_PLACES.get(self.place_name)),
            ('publishDateFrom', self.publish_date_from),
            ('publishDateTo', self.publish_date_to),
            ('applSubmissionCloseDateFrom', self.close_date_from),
            ('applSubmissionCloseDateTo', self.close_date_to),
        ]


def prepare_search_string(raw_string: str) -> str:
    search_string = re.sub(" +", " ", raw_string)
    search_string = search_string.strip()
    search_string = "+".join(search_string.split(" "))

    return search_string
