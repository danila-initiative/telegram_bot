# type: ignore
import typing

import pandas as pd

from bot_zakupki.common import models


def format_price_for_message(price: int) -> str:
    str_price = str(price)
    if len(str_price) <= 3:
        return str_price

    rest = len(str_price) % 3

    new_price = str_price[0:rest]
    i = rest
    while i <= len(str_price):
        new_price += " "
        last_index = min(len(str_price), i + 3)
        new_price += str_price[i:last_index]
        i += 3

    return new_price


def check_and_process_max_price(
    max_price: str, min_price: int
) -> typing.Tuple[models.MaxPriceValidation, typing.Optional[int]]:
    max_price = delete_all_spaces(max_price)

    if max_price.startswith("-") and max_price[1:].isdigit():
        return models.MaxPriceValidation.LESS_THAT_MIN_PRICE, None

    if not max_price.isdigit():
        return models.MaxPriceValidation.NOT_A_NUMBER, None

    if int(max_price) <= min_price:
        return models.MaxPriceValidation.LESS_THAT_MIN_PRICE, None

    if int(max_price) >= 1000000000000:
        return models.MaxPriceValidation.VALID, 1000000000000

    return models.MaxPriceValidation.VALID, int(max_price)


def delete_all_spaces(string: str) -> str:
    return "".join(string.split())


def delete_all_extra_spaces(string: str) -> str:
    return " ".join(string.split())


def convert_results_to_df(
    results: list[models.ResultDB],
) -> pd.DataFrame:
    data = [result.to_list_for_df() for result in results]
    columns = [
        "query_id",
        "Номер закупки",
        "Предмет закупки",
        "Начальная цена",
        "Дата окончания подачи заявок",
        "Ссылка",
    ]
    df = pd.DataFrame(data, columns=columns)

    return df


def save_df_to_excel(df: pd.DataFrame, file_name: str):
    writer = pd.ExcelWriter(file_name, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name="Sheet1")

    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    wrap_format = workbook.add_format({"text_wrap": True})

    center_format = workbook.add_format(
        {"align": "center", "valign": "vcenter"}
    )
    v_center_format = workbook.add_format({"valign": "vcenter"})
    link_format = workbook.add_format(
        {"font_color": "blue", "underline": True, "valign": "vcenter"}
    )

    worksheet.set_column("A:A", 25, v_center_format)
    worksheet.set_column("B:B", 50, wrap_format)
    worksheet.set_column("C:C", 25, center_format)
    worksheet.set_column("D:D", 30, center_format)
    worksheet.set_column("E:E", 100, link_format)

    writer.save()


if __name__ == "__main__":
    print(models.Config())
