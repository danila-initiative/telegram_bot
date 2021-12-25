import asyncio
import datetime

import pytest
from aiogram import types

from bot_zakupki.bot.handlers import common_handlers
from bot_zakupki.bot.handlers import messages
from bot_zakupki.common import db

TELEGRAM_ID_1 = 11111
SLEEP_TIME = 2
TEST_QUERY_1 = {
    "user_id": TELEGRAM_ID_1,
    "search_string": "test search string",
    "location": "test location",
    "min_price": 0,
    "max_price": 100000,
}


@pytest.mark.asyncio
async def test_cmd_start_func(setup_db, get_message):
    now = datetime.datetime.now().replace(microsecond=0)

    # запускаем бота первый раз
    text, reply_markup = await common_handlers.cmd_start_func(
        get_message(TELEGRAM_ID_1)
    )
    assert text == messages.CMD_START_MSG
    assert reply_markup == types.ReplyKeyboardRemove()
    user_new = db.get_all_users()[0]

    # останавливаем бота
    await common_handlers.cmd_stop_function(get_message(TELEGRAM_ID_1))
    user_stopped = db.get_all_users()[0]

    # перезапускаем бота
    await asyncio.sleep(SLEEP_TIME)
    text, reply_markup = await common_handlers.cmd_start_func(
        get_message(TELEGRAM_ID_1)
    )
    user_restarted = db.get_all_users()[0]
    assert text == messages.CMD_START_MSG
    assert reply_markup == types.ReplyKeyboardRemove()

    assert user_new.first_bot_start_date == now
    assert user_stopped.first_bot_start_date == now
    assert user_restarted.first_bot_start_date == now

    assert user_new.bot_start_date == now
    assert user_stopped.bot_start_date == now
    assert user_restarted.bot_start_date > now

    assert user_new.unique_id == 1
    assert user_stopped.unique_id == 1
    assert user_restarted.unique_id == 1

    assert user_new.user_id == str(TELEGRAM_ID_1)
    assert user_stopped.user_id == str(TELEGRAM_ID_1)
    assert user_restarted.user_id == str(TELEGRAM_ID_1)

    assert user_new.bot_is_active
    assert user_stopped.bot_is_active is False
    assert user_restarted.bot_is_active


@pytest.mark.asyncio
async def test_show_all_my_queries(setup_db, get_message):
    # Нет запросов
    text, reply_markup = await common_handlers.cmd_show_all_my_queries_func(
        get_message(TELEGRAM_ID_1)
    )
    assert (
        text
        == """У вас еще нет поисковых запросов 🙂. 
Добавить запрос для поиска закупок можно командой /add_new_query

    🗓️ Подписка неактивна"""
    )
    assert reply_markup == types.ReplyKeyboardRemove()

    # Добавляем один запрос
    db.insert_new_search_query(column_values=TEST_QUERY_1)

    text, reply_markup = await common_handlers.cmd_show_all_my_queries_func(
        get_message(TELEGRAM_ID_1)
    )
    assert (
        text
        == """<b>1</b>. 🔍 Ключевая строка: test search string
    🌏 Регион: test location
    💰 Цена: от 0 до  100 000  рублей

    🗓️ Подписка неактивна"""
    )

    # Добавляем пользователя с активной подпиской
    db.insert_new_user(str(TELEGRAM_ID_1))
    last_sub_day = datetime.datetime(2023, 12, 19, 16, 21, 12)
    user_data_update = {
        db.USER_SUBSCRIPTION_LAST_DAY: last_sub_day,
    }
    db.update_user_by_user_id(
        user_id=str(TELEGRAM_ID_1), column_values=user_data_update
    )

    text, reply_markup = await common_handlers.cmd_show_all_my_queries_func(
        get_message(TELEGRAM_ID_1)
    )
    assert (
        text
        == """<b>1</b>. 🔍 Ключевая строка: test search string
    🌏 Регион: test location
    💰 Цена: от 0 до  100 000  рублей

    🗓️ Окончание подписки: 19.12.2023
"""
    )
