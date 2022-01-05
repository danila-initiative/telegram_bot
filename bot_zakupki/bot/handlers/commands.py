from dataclasses import dataclass

# Common commands
START = "start"
START_DESCRIPTION = "Старт"

HELP = "help"
HELP_DESCRIPTION = "Информация о боте"

CANCEL = "cancel"

UPDATE_SUBSCRIPTION = "update_subscription"
UPDATE_SUBSCRIPTION_DESCRIPTION = "Управление подпиской"


# Query commands
ADD_NEW_QUERY = "add_new_query"
ADD_NEW_QUERY_DESCRIPTION = "Добавить параметры для запроса"

SHOW_ALL_MY_QUERIES = "show_all_my_queries"
SHOW_ALL_MY_QUERIES_DESCRIPTION = "Показать все мои запросы"

CHANGE_QUERY = "change_query"
CHANGE_QUERY_DESCRIPTION = "Изменить мои запросы"

DELETE_QUERY = "delete_query"
DELETE_QUERY_DESCRIPTION = "Удалить запрос"


# DEBUGGING
STOP = "stop"
STOP_DESCRIPTION = "[DEBUG] Имитация деактивации бота"

END_TRIAL_PERIOD = "end_trial_period"
END_TRIAL_PERIOD_DESCRIPTION = "[DEBUG] Имитация окончания пробного периода"


@dataclass
class Command:
    name: str
    description: str


# commands to display in bot interface
BOT_COMMANDS = [
    Command(SHOW_ALL_MY_QUERIES, SHOW_ALL_MY_QUERIES_DESCRIPTION),
    Command(ADD_NEW_QUERY, ADD_NEW_QUERY_DESCRIPTION),
    Command(CHANGE_QUERY, CHANGE_QUERY_DESCRIPTION),
    Command(DELETE_QUERY, DELETE_QUERY_DESCRIPTION),
    Command(UPDATE_SUBSCRIPTION, UPDATE_SUBSCRIPTION_DESCRIPTION),
    Command(HELP, HELP_DESCRIPTION),
]

DEBUG_COMMANDS = [
    Command(STOP, STOP_DESCRIPTION),
    Command(END_TRIAL_PERIOD, END_TRIAL_PERIOD_DESCRIPTION),
]
