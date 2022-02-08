import os


RESULT_PUBLISH_DATE = "publish_date"
RESULT_FINISH_DATE = "finish_date"
RESULT_NUMBER_OF_PURCHASE = "number_of_purchase"
RESULT_SUBJECT_OF_PURCHASE = "subject_of_purchase"
RESULT_PRICE = "price"
RESULT_LINK = "link"
RESULT_CUSTOMER = "customer"
RESULT_QUERY_ID = "query_id"

USER_USER_ID = "user_id"
USER_FIRST_BOT_START_DATE = "first_bot_start_date"
USER_BOT_START_DATE = "bot_start_date"
USER_BOT_IS_ACTIVE = "bot_is_active"
USER_SUBSCRIPTION_LAST_DAY = "subscription_last_day"
USER_PAYMENT_LAST_DAY = "payment_last_day"
USER_MAX_NUMBER_OF_QUERIES = "max_number_of_queries"

# trial period
TRIAL_PERIOD_DAYS = 10
MAX_QUERIES_IN_TRIAL_PERIOD = 3
MAX_QUERIES_IN_COMMON_PERIOD = 5


PUBLISH_DELTA = -1
CLOSE_DELTA = 5

CRONS_LOG_FOLDER = "/app/logs/crons/"
BOT_LOG_FOLDER = "/app/logs/bot/"

PATH_TO_DB = "/app/db/bot.sqlite"
PATH_TO_MIGRATIONS = "bot_zakupki/storage/migrations"
TABLES_NAME = ["result", "search_query", "user"]

PATH_TO_TEST_DB = "/app/tests/db/bot_test.sqlite"

BASE_URL = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?"

DEBUG = True if os.getenv("DEBUG") == "True" else False

PRICE_TABLE = "/app/bot_zakupki/static/price.png"

RESULTS_PATH = "/app/crons/results/"
