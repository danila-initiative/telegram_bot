import os

TEST_PERIOD = 10
PUBLISH_DELTA = -1
CLOSE_DELTA = 5

TIME_ZONE = "Europe/Moscow"

LOG_FILE = "/code/logs/log_"

PATH_TO_DB = "db/bot.sqlite"
PATH_TO_MIGRATIONS = "bot_zakupki/storage/migrations"
PATH_TO_QUERIES = "bot_zakupki/storage/queries"
TABLES_NAME = ["result", "search_query", "user"]

BASE_URL = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?"

DEBUG = os.getenv("DEBUG")
