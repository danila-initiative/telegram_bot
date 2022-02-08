# type: ignore
# import pandas as pd
from typing import Optional

import requests
from bs4 import BeautifulSoup as BS
from loguru import logger
# from pandas.core.frame import DataFrame
from requests import Response

from bot_zakupki.bot.handlers import messages
from bot_zakupki.common import dates
from bot_zakupki.common import models


class SiteUnavailable(Exception):
    pass


@logger.catch
def request_formation(custom_params: models.RequestParameters) -> str:
    params = {
        "morphology": "on",
        "search-filter": "Дате+размещения",
        "pageNumber": "1",
        "sortDirection": "false",
        "recordsPerPage": "_50",
        "showLotsInfoHidden": "false",
        "sortBy": "UPDATE_DATE",
        "fz44": "on",
        "fz223": "on",
        "ppRf615": "on",
        "af": "on",
        "currencyIdGeneral": "-1",
    }

    custom_params = custom_params.to_dict()

    if custom_params[
        "searchString"
    ] == models.RequestParameters.prepare_search_string(
        messages.I_M_FEELING_LUCKY
    ):
        custom_params.pop("searchString")
        params["recordsPerPage"] = "_20"

    for key, value in custom_params.items():
        if value is not None:
            params[key] = value

    params_: list = []
    for key, value in params.items():
        params_.append(key + "=" + value)
    params_combined = "&".join(params_)

    config = models.Config()

    return config.search_parameters.base_url + params_combined


@logger.catch
def get_page_by_url(url: str) -> Response:
    page = requests.get(url, headers={"User-Agent": "Custom"})
    return page


@logger.catch
def parse_result_page(
    page: Response, search_string
) -> Optional[list[models.Result]]:
    """Return all results with key words in purchase subject"""
    results = list()

    soup = BS(page.content, "html.parser")

    number_of_records = soup.find("div", class_="search-results__total")

    if number_of_records is None:
        return

    number_of_records = number_of_records.text.strip().split(" ")[0]

    number_tmp = ""
    for i in number_of_records:
        if i.isnumeric():
            number_tmp += i

    number_of_records = int(number_tmp)

    if number_of_records == 0:
        return

    records = soup.find_all(
        "div", class_="search-registry-entry-block box-shadow-search-input"
    )
    for i in records:
        subject_of_purchase = i.find(
            "div", class_="registry-entry__body-value"
        ).text.strip()

        subject_of_purchase = subject_of_purchase.split()
        subject_of_purchase = " ".join(subject_of_purchase)

        subject_lower = subject_of_purchase.lower()

        key_words = search_string.lower().split(" ")

        # Доп фильтрация полученных результатов по полю "Объект закупок"
        if len(key_words) < 2:
            key_words_in_subject = True
            for k in range(len(key_words)):
                tmp_word = ""
                for j in key_words[k]:
                    if j.isalpha():
                        tmp_word += j
                key_words[k] = tmp_word

            for word in key_words:
                if word not in subject_lower:
                    key_words_in_subject = False

            if not key_words_in_subject:
                logger.info(
                    f'Key word "{search_string}" '
                    f'not in subject "{subject_of_purchase}"'
                )
                continue

        number = i.find("div", class_="registry-entry__header-mid__number")
        number_of_purchase = number.text.strip()
        price = i.find("div", class_="price-block__value").text.strip()
        price = price.split(",")
        new_price = ""
        for letter in price[0]:
            if letter.isdigit():
                new_price += letter

        customer = i.find(
            "div", class_="registry-entry__body-href"
        ).text.strip()
        customer = customer.split()
        customer = " ".join(customer)

        all_dates = i.find_all("div", class_="data-block__value")
        finish_date = all_dates[-1].text.strip()
        publish_date = all_dates[0].text.strip()

        link = number.find("a")["href"]
        addition = "https://zakupki.gov.ru"
        if link.startswith("/epz"):
            link = addition + link

        results.append(
            models.Result(
                publish_date=dates.res_date_to_datetime(publish_date),
                finish_date=dates.res_date_to_datetime(finish_date),
                number_of_purchase=number_of_purchase,
                subject_of_purchase=subject_of_purchase,
                price=int(new_price),
                link=link,
                customer=customer,
            )
        )

    return results
