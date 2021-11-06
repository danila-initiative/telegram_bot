import os

TRIAL_PERIOD = 10

MAX_QUERIES_IN_TRIAL_PERIOD = 3
MAX_NONACTIVE_QUERIES = 3

PUBLISH_DELTA = -1
CLOSE_DELTA = 5

CRONS_LOG_FOLDER = "/app/logs/crons/"
BOT_LOG_FOLDER = "/app/logs/bot/"

PATH_TO_DB = "/app/db/bot.sqlite"
PATH_TO_MIGRATIONS = "bot_zakupki/storage/migrations"
TABLES_NAME = ["result", "search_query", "user"]

BASE_URL = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?"

DEBUG = os.getenv("DEBUG")
