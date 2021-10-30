# type: ignore
import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
from aiogram.dispatcher.filters.state import StatesGroup

from bot_zakupki.bot.handlers import commands
from bot_zakupki.bot.handlers import messages
from bot_zakupki.common import consts
from bot_zakupki.common import db
from bot_zakupki.common import models


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
        callback=process_search_string, state=SearchParameters.search_string
    )

    dp.register_message_handler(
        process_location,
        lambda message: message.text in models.CUSTOMER_PLACES.keys(),
        state=SearchParameters.location,
    )
    dp.register_message_handler(
        process_location_invalid,
        lambda message: message.text not in models.CUSTOMER_PLACES.keys(),
        state=SearchParameters.location,
    )

    dp.register_message_handler(
        process_min_price,
        lambda message: message.text.isdigit() and int(message.text) >= 0,
        state=SearchParameters.min_price,
    )
    dp.register_message_handler(
        process_min_price_invalid,
        lambda message: not message.text.isdigit() or int(message.text) < 0,
        state=SearchParameters.min_price,
    )

    dp.register_message_handler(
        process_max_price,
        lambda message: message.text.isdigit(),
        state=SearchParameters.max_price,
    )
    dp.register_message_handler(
        process_max_price_invalid,
        lambda message: not message.text.isdigit(),
        state=SearchParameters.max_price,
    )


async def new_query(message: types.Message):
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
    await SearchParameters.min_price.set()

    markup = types.ReplyKeyboardRemove()

    await message.answer(messages.SET_MINIMUM_PRICE, reply_markup=markup)


async def process_location_invalid(message: types.Message):
    await message.reply(messages.SELECT_LOCATION_INVALID)


# ========== PRICE ==========


async def process_min_price(message: types.Message, state: FSMContext):
    await state.update_data(min_price=int(message.text))
    await SearchParameters.max_price.set()

    await message.answer(messages.SET_MAXIMUM_PRICE)


async def process_min_price_invalid(message: types.Message):
    await message.reply(messages.SET_MINIMUM_PRICE_INVALID)


async def process_max_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if int(message.text) < data["min_price"]:
        await message.reply(messages.SET_MAX_PRICE_LESS_THAN_MIN)
        return

    data["max_price"] = int(message.text)

    now = datetime.datetime.now().replace(microsecond=0)
    last_sub_day = now + datetime.timedelta(days=consts.TEST_PERIOD)

    query = {
        "user_id": message.from_user.id,
        "search_string": data["search_string"],
        "location": data["location"],
        "min_price": data["min_price"],
        "max_price": data["max_price"],
        "subscription_last_day": last_sub_day,
    }
    db.insert_new_search_query(column_values=query)

    query_data_message = messages.query_message_formation(
        data["search_string"],
        data["location"],
        data["min_price"],
        data["max_price"],
    )

    await message.answer(query_data_message)

    await state.finish()


async def process_max_price_invalid(message: types.Message):
    await message.reply(messages.SET_MAX_PRICE_INVALID)
