import re
import pandas as pd
import requests
from bs4 import BeautifulSoup as BS
from loguru import logger
from pandas.core.frame import DataFrame
from requests import Response

import consts


def RequestFormation(key_word: str,
                     min_price: int,
                     max_price: int,
                     publish_date_from: str,
                     location: str,
                     close_date = None) -> str:

    location_id = consts.CUSTOMER_PLACES[location]

    search_string = re.sub(" +", " ", key_word)
    search_string = search_string.strip()
    search_string = "+".join(search_string.split(" "))

    params = [
        ("searchString", search_string),
        ("morphology", "on"),
        ("search-filter", "Дате+размещения"),
        ("pageNumber", "1"),
        ("sortDirection", "false"),
        ("recordsPerPage", "_20"),
        ("showLotsInfoHidden", "false"),
        ("sortBy", "UPDATE_DATE"),
        ("fz44", "on"),
        ("fz223", "on"),
        ("ppRf615", "on"),
        ("af", "on"),
        ("priceFromGeneral", str(min_price * 10**6)),
        ("priceToGeneral", str(max_price * 10**6)),
        ("currencyIdGeneral", "-1"),
        ("publishDateFrom", publish_date_from),
        ("customerPlace", str(location_id))
    ]

    if consts.PUBLISH_DATE_TO:
        params.append(("publishDateTo", publish_date_from))

    if close_date != None:
        params.append(("applSubmissionCloseDateFrom", close_date))

    params_combined = "&".join(map(lambda x: x[0]+"="+x[1], params))

    return consts.BASE_URL + params_combined

def GetPageByURL(url: str) -> Response:
    page = requests.get(url, headers={'User-Agent': 'Custom'})
    return page

def ParseResultPage(page: Response, key_word: str) -> DataFrame:
    """Return all results with key words in purchase subject"""

    soup = BS(page.content, 'html.parser')

    # soup = BS(page, 'html.parser')          # если работаешь с локальным файлом

    number_of_records = soup.find("div", class_="search-results__total")
    number_of_records = number_of_records.text.strip().split(" ")[0]
    
    if number_of_records == 0:
        return pd.DataFrame()

    results = {
        "Номер закупки" : [],
        "Объект закупки" : [],
        "Начальная цена" : [],
        "Дата окончания подачи заявок" : [],
        "Ссылка на закупку" : []
    }

    records = soup.find_all("div", class_="search-registry-entry-block box-shadow-search-input")
    for i in records:
        subject = i.find("div", class_="registry-entry__body-value").text.strip()
        subject_lower = subject.lower()
        
        key_words = key_word.lower().split(" ")

# Доп фильтрация полученных результатов по полю "Объект закупок"
        if len(key_words) < 3:    
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
                logger.warning(f"Key word \"{key_word}\" not in subject \"{subject}\"")
                continue


        results["Объект закупки"].append(subject)

        number = i.find("div", class_="registry-entry__header-mid__number")
        results["Номер закупки"].append(number.text.strip())

        price = i.find("div", class_="price-block__value").text.strip()
        results["Начальная цена"].append(price)

        close_date = i.find_all("div", class_="data-block__value")
        close_date = close_date[-1].text.strip()
        results["Дата окончания подачи заявок"].append(close_date)

        link = number.find("a")["href"]
        addition = "https://zakupki.gov.ru"
        if link.startswith("/epz"):
            link = addition + link

        results["Ссылка на закупку"].append(link)

    columns = [
        "Номер закупки",
        "Объект закупки",
        "Начальная цена",
        "Дата окончания подачи заявок",
        "Ссылка на закупку"
    ]

    df = pd.DataFrame(results, columns=columns)

    return df


def SaveDfToExel(df: DataFrame, file_name: str):
    writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1') 

    workbook  = writer.book
    worksheet = writer.sheets['Sheet1']
    wrap_format = workbook.add_format({'text_wrap': True})

    center_format = workbook.add_format({ 'align': 'center', 'valign': 'vcenter'})
    v_center_format = workbook.add_format({'valign': 'vcenter'})
    link_format = workbook.add_format({'font_color': 'blue', 'underline': True, 'valign': 'vcenter'})
    
    worksheet.set_column('A:A', 25, v_center_format)
    worksheet.set_column('B:B', 50, wrap_format)
    worksheet.set_column('C:C', 25, center_format)
    worksheet.set_column('D:D', 30, center_format)
    worksheet.set_column('E:E', 100, link_format)

    writer.save()


if __name__ == "__main__":
    # page = requests.get(r"https://zakupki.gov.ru/epz/order/extendedsearch/results.html?searchString=%D0%BB%D0%B8%D1%84%D1%82&morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&pageNumber=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&sortBy=UPDATE_DATE&fz44=on&fz223=on&af=on&priceFromGeneral=10000000&priceToGeneral=15000000&currencyIdGeneral=-1",
    #                     headers={'User-Agent': 'Custom'})
    # df = ParseResultPage(page)

    # если работаешь с локальным файлом
    # page = open("zakup.html", "r", encoding="utf8")
    # df = ParseResultPage(page)

    # SaveDataFrameToXlsx(df, "results/test.xlsx")
    pass
