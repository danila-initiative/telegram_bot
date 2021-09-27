# import pandas as pd
import requests
from bs4 import BeautifulSoup as BS
from loguru import logger
# from pandas.core.frame import DataFrame
from requests import Response

from bot_zakupki.common import consts
from bot_zakupki.common import models


@logger.catch
def request_formation(custom_params: models.RequestParameters) -> str:
    basic_params = [
        ("morphology", "on"),
        ("search-filter", "Дате+размещения"),
        ("pageNumber", "1"),
        ("sortDirection", "false"),
        ("recordsPerPage", "_50"),
        ("showLotsInfoHidden", "false"),
        ("sortBy", "UPDATE_DATE"),
        ("fz44", "on"),
        ("fz223", "on"),
        ("ppRf615", "on"),
        ("af", "on"),
        ("currencyIdGeneral", "-1"),
    ]

    custom_params = custom_params.to_list()
    filtered_custom_param = []
    for param in custom_params:
        if param[1] is not None:
            filtered_custom_param.append(param)

    parameters = basic_params + filtered_custom_param
    params_combined = "&".join(map(lambda x: x[0] + "=" + x[1], parameters))

    logger.info(f"created url: {consts.BASE_URL + params_combined}")

    return consts.BASE_URL + params_combined


@logger.catch
def get_page_by_url(url: str) -> Response:
    page = requests.get(url, headers={'User-Agent': 'Custom'})
    return page


@logger.catch
def parse_result_page(page: Response, search_string,
                      location: str) \
        -> list[models.Result]:
    """Return all results with key words in purchase subject"""
    results = []

    soup = BS(page.content, 'html.parser')

    number_of_records = soup.find("div", class_="search-results__total")
    number_of_records = number_of_records.text.strip().split(" ")[0]

    if number_of_records == 0:
        return results

    records = soup.find_all(
        "div", class_="search-registry-entry-block box-shadow-search-input")
    for i in records:
        subject_of_purchase = i.find(
            "div", class_="registry-entry__body-value").text.strip()
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
                    f"Key word \"{search_string}\" "
                    f"not in subject \"{subject_of_purchase}\"")
                continue

        number = i.find("div", class_="registry-entry__header-mid__number")
        number_of_purchase = number.text.strip()
        price = i.find("div", class_="price-block__value").text.strip()

        customer = i.find("div",
                          class_="registry-entry__body-href").text.strip()
        customer = customer.replace("\n", "")

        all_dates = i.find_all("div", class_="data-block__value")
        finish_date = all_dates[-1].text.strip()
        publish_date = all_dates[0].text.strip()

        link = number.find("a")["href"]
        addition = "https://zakupki.gov.ru"
        if link.startswith("/epz"):
            link = addition + link

        results.append(models.Result(
            search_string=search_string,
            number_of_purchase=number_of_purchase,
            publish_date=publish_date,
            finish_date=finish_date,
            price=price,
            subject_of_purchase=subject_of_purchase,
            link=link,
            customer=customer,
            location=location,
        )
        )

    return results

# def SaveDfToExel(df: DataFrame, file_name: str):
#     writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
#     df.to_excel(writer, index=False, sheet_name='Sheet1')
#
#     workbook = writer.book
#     worksheet = writer.sheets['Sheet1']
#     wrap_format = workbook.add_format({'text_wrap': True})
#
#     center_format = workbook.add_format(
#         {'align': 'center', 'valign': 'vcenter'})
#     v_center_format = workbook.add_format({'valign': 'vcenter'})
#     link_format = workbook.add_format(
#         {'font_color': 'blue', 'underline': True, 'valign': 'vcenter'})
#
#     worksheet.set_column('A:A', 25, v_center_format)
#     worksheet.set_column('B:B', 50, wrap_format)
#     worksheet.set_column('C:C', 25, center_format)
#     worksheet.set_column('D:D', 30, center_format)
#     worksheet.set_column('E:E', 100, link_format)
#
#     writer.save()
