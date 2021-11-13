# type: ignore
import datetime

from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
from aiogram.dispatcher.filters.state import StatesGroup
from loguru import logger

from bot_zakupki.bot.handlers import change_query_handlers as cqh
from bot_zakupki.bot.handlers import commands
from bot_zakupki.bot.handlers import messages
from bot_zakupki.common import consts
from bot_zakupki.common import db
from bot_zakupki.common import models
from bot_zakupki.common import user_info
from bot_zakupki.common import utils


class SearchParameters(StatesGroup):
    search_string = State()
    location = State()
    min_price = State()
    max_price = State()


def register_handlers_search_query(dp: Dispatcher):
    dp.register_message_handler(
        new_query, commands=commands.ADD_NEW_QUERY, state="*"
    )
    dp.register_message_handler(
        process_search_string,
        lambda message: not message.text.startswith("/"),
        state=SearchParameters.search_string,
    )

    dp.register_message_handler(
        process_location,
        lambda message: message.text in models.CUSTOMER_PLACES.keys(),
        state=[SearchParameters.location, cqh.ChangeSearchParameters.location],
    )
    dp.register_message_handler(
        process_location_invalid,
        lambda message: message.text not in models.CUSTOMER_PLACES.keys(),
        state=[SearchParameters.location, cqh.ChangeSearchParameters.location],
    )

    dp.register_message_handler(
        process_min_price,
        state=[
            SearchParameters.min_price,
            cqh.ChangeSearchParameters.min_price,
        ],
    )

    dp.register_message_handler(
        process_max_price,
        lambda message: utils.delete_all_spaces(message.text).isdigit(),
        state=SearchParameters.max_price,
    )


async def new_query(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user_by_user_id(user_id=user_id)
    now = datetime.datetime.now().replace(microsecond=0)

    trial_period_state = user_info.get_trial_period_state(user=user, date=now)

    search_queries = db.get_all_search_queries_by_user_id(user_id=user_id)
    number_of_search_queries = len(search_queries)

    active_search_queries = db.get_all_active_search_queries_by_user_id(
        user_id=user_id, date=now
    )
    number_of_active_search_queries = len(active_search_queries)

    logger.debug(
        f"user id: {message.from_user.id}; "
        f"trial period state: {trial_period_state}; "
        f"number_of_search_queries: {number_of_search_queries}; "
        f"number_of_active_search_queries: {number_of_active_search_queries}"
    )

    # пробный период
    # нельзя добавить больше 3-х запросов
    if (
        trial_period_state == models.TrialPeriodState.TRIAL_PERIOD
        and number_of_active_search_queries
        >= consts.MAX_QUERIES_IN_TRIAL_PERIOD
    ):
        await message.answer(
            messages.CANNOT_ADD_MORE_QUERY_IN_TRIAL_PERIOD,
            reply_markup=types.ReplyKeyboardRemove(),
        )
        return

    # пробный период закончился
    # нельзя добавить больше 3 неактивных запросов
    if (
        trial_period_state == models.TrialPeriodState.TRIAL_PERIOD_IS_OVER
        and number_of_search_queries - number_of_active_search_queries
        >= consts.MAX_NONACTIVE_QUERIES
    ):
        logger.debug(
            f"number of active queries: {number_of_active_search_queries}; "
            f"number of all queries: {number_of_search_queries}"
        )
        await message.answer(
            messages.TOO_MANY_NOT_ACTIVE_QUERIES,
            reply_markup=types.ReplyKeyboardRemove(),
        )
        return

    await SearchParameters.search_string.set()

    await message.answer(
        messages.NEW_QUERY_MSG, reply_markup=types.ReplyKeyboardRemove()
    )


# ========== SEARCH STRING ==========


async def process_search_string(message: types.Message, state: FSMContext):
    await state.update_data(search_string=message.text.lower())
    await SearchParameters.location.set()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    for place in models.CUSTOMER_PLACES:
        keyboard.add(place)

    await message.answer(messages.SELECT_LOCATION, reply_markup=keyboard)


# ========== LOCATION ==========


async def process_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)

    if await state.get_state() == "ChangeSearchParameters:location":
        await cqh.ChangeSearchParameters.min_price.set()
    else:
        await SearchParameters.min_price.set()

    markup = types.ReplyKeyboardRemove()

    await message.answer(messages.SET_MINIMUM_PRICE, reply_markup=markup)


async def process_location_invalid(message: types.Message):
    await message.reply(messages.SELECT_LOCATION_INVALID)


# ========== PRICE ==========


async def process_min_price(message: types.Message, state: FSMContext):
    # проверка на валидность минимальной цены
    min_price = utils.delete_all_spaces(message.text)
    logger.debug(f"min_price: {min_price}")
    if not min_price.isdigit() or int(min_price) < 0:
        await message.reply(messages.SET_MINIMUM_PRICE_INVALID)
        return

    min_price = int(min_price)
    await state.update_data(min_price=min_price)

    if await state.get_state() == "ChangeSearchParameters:min_price":
        await cqh.ChangeSearchParameters.max_price.set()
    else:
        await SearchParameters.max_price.set()

    await message.answer(messages.SET_MAXIMUM_PRICE)


async def process_max_price(message: types.Message, state: FSMContext):
    additional_message = ""
    data = await state.get_data()
    valid, max_price = utils.check_and_process_max_price(
        message.text, data["min_price"]
    )

    if valid == models.MaxPriceValidation.NOT_A_NUMBER:
        await message.answer(messages.MAX_PRICE_NOT_A_NUMBER)
        return

    if valid == models.MaxPriceValidation.LESS_THAT_MIN_PRICE:
        await message.reply(messages.MAX_PRICE_LESS_THAN_MIN)
        return

    data["max_price"] = int(max_price)

    user_id = message.from_user.id

    query = {
        "user_id": user_id,
        "search_string": data["search_string"],
        "location": data["location"],
        "min_price": data["min_price"],
        "max_price": data["max_price"],
    }

    user = db.get_user_by_user_id(user_id=user_id)
    now = datetime.datetime.now().replace(microsecond=0)
    trial_period_state = user_info.get_trial_period_state(user=user, date=now)

    # пробный период не начался
    # добавляем дату начала и окончания пробного периода
    if (
        trial_period_state
        == models.TrialPeriodState.TRIAL_PERIOD_HAS_NOT_STARTED
    ):
        last_sub_day = now + datetime.timedelta(days=consts.TRIAL_PERIOD)

        user_data_update = {
            "trial_start_date": now,
            "trial_end_date": last_sub_day,
        }
        db.update_user_by_user_id(
            user_id=message.from_user.id, column_values=user_data_update
        )

        query["subscription_last_day"] = last_sub_day
        additional_message = f"Дата окончания пробного периода: {last_sub_day}"

    # сейчас пробный период
    # дата окончания подписки - дата окончания пробного периода
    if trial_period_state == models.TrialPeriodState.TRIAL_PERIOD:
        last_sub_day = user.trial_end_date

        query["subscription_last_day"] = last_sub_day
        additional_message = f"Дата окончания пробного периода: {last_sub_day}"

    # пробный период закончился
    if trial_period_state == models.TrialPeriodState.TRIAL_PERIOD_IS_OVER:
        additional_message = "Оплатить новый запрос можно по ссылке: link"

    db.insert_new_search_query(column_values=query)

    query_data_message = messages.query_message_formation(
        data["search_string"],
        data["location"],
        data["min_price"],
        data["max_price"],
    )

    await message.answer(query_data_message)
    await message.answer(additional_message)

    await state.finish()
