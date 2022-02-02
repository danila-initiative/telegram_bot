import os

# trial period
TRIAL_PERIOD_DAYS = 10
MAX_QUERIES_IN_TRIAL_PERIOD = 3
MAX_QUERIES_IN_COMMON_PERIOD = 5


PUBLISH_DELTA = -2
CLOSE_DELTA = 5

CRONS_LOG_FOLDER = "/app/logs/crons/"
BOT_LOG_FOLDER = "/app/logs/bot/"

PATH_TO_DB = "/app/db/bot.sqlite"
PATH_TO_MIGRATIONS = "bot_zakupki/storage/migrations"
TABLES_NAME = ["result", "search_query", "user"]

PATH_TO_TEST_DB = "/app/tests/db/bot_test.sqlite"

BASE_URL = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?"

DEBUG = os.getenv("DEBUG")

PRICE_TABLE = '/app/bot_zakupki/static/price.png'
