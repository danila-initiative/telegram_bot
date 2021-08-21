
PUBLISH_DATE_TO = True      # дата размещения - только предыдущий рабочий день

PUBLISH_DELTA = -1
CLOSE_DELTA = 5
TIME_ZONE = "Europe/Moscow"

RESULTS_FOLDER = "/code/results"
LOG_FILE = "/code/logs/log_"

BASE_URL = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?"
CUSTOMER_PLACES = {
    'Москва': 5277335,
    'Московская область': 5277327,
    'Дальневосточный ФО': 5277399,
    'Приволжский ФО': 5277362,
    'Северо-Западный ФО': 5277336,
    'Северо-Кавказский ФО': 9409197,
    'Сибирский ФО': 5277384,
    'Уральский ФО': 5277377,
    'Центральный ФО': 5277317,
    'Южный ФО': 6325041,
}