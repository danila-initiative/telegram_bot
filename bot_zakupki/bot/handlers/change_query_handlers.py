# type: ignore
from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State
from aiogram.dispatcher.filters.state import StatesGroup

from bot_zakupki.bot.handlers import commands
from bot_zakupki.bot.handlers import messages
from bot_zakupki.common import db
from bot_zakupki.common import models
from bot_zakupki.common import utils

user_data = {}


class ChangeSearchParameters(StatesGroup):
    search_string = State()
    location = State()
    min_price = State()
    max_price = State()


def register_change_search_query(dp: Dispatcher):
    dp.register_message_handler(
        cmd_choose_query_to_change, commands=commands.CHANGE_QUERY, state="*"
    )
    dp.register_callback_query_handler(
        callback_change_query, Text(startswith="change_query_")
    )
    dp.register_message_handler(
        callback=process_change_search_string,
        state=ChangeSearchParameters.search_string,
    )
    dp.register_message_handler(
        process_change_max_price, state=ChangeSearchParameters.max_price
    )


async def cmd_choose_query_to_change(message: types.Message, state: FSMContext):
    print(f"State: {await state.get_state()}")
    await state.finish()
    print(f"State: {await state.get_state()}")
    user_id = message.from_user.id

    # Получение всех запросов
    queries = db.get_all_search_queries_by_user_id(
        user_id=user_id,
    )

    answer = messages.all_queries_messages_formation(queries=queries)
    answer += "\n"
    answer += messages.WHICH_QUERY_CHANGE

    # Формирование клавиатуры для этих запросов
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for i in range(len(queries)):
        button = types.InlineKeyboardButton(
            text=str(i + 1), callback_data=f"change_query_{i + 1}"
        )
        buttons.append(button)

    keyboard.add(*buttons)

    await message.answer(answer, reply_markup=keyboard)


async def callback_change_query(call: types.CallbackQuery):
    await ChangeSearchParameters.search_string.set()

    user_id = call.from_user.id
    queries = db.get_all_search_queries_by_user_id(
        user_id=user_id,
    )

    number = call.data.split("_")[-1]
    user_data[user_id] = (number, queries[int(number) - 1].id)

    await call.message.answer(
        f"Введите новую ключевую строку для запроса {number}: ",
    )


# ========== SEARCH STRING ==========


async def process_change_search_string(message: types.Message, state: FSMContext):
    await state.update_data(search_string=message.text.lower())
    await ChangeSearchParameters.location.set()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    for place in models.CUSTOMER_PLACES:
        keyboard.add(place)

    await message.answer(messages.SELECT_LOCATION, reply_markup=keyboard)


async def process_change_max_price(message: types.Message, state: FSMContext):
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

    data["max_price"] = max_price

    user_id = message.from_user.id
    query_id = user_data[user_id][1]
    query_number = user_data[user_id][0]

    query = {
        "search_string": data["search_string"],
        "location": data["location"],
        "min_price": data["min_price"],
        "max_price": data["max_price"],
    }

    db.update_search_query(query_id=query_id, column_values=query)
    changed_query_data_message = messages.changed_query_message_formation(
        data["search_string"],
        data["location"],
        data["min_price"],
        data["max_price"],
        query_number,
    )

    await message.answer(changed_query_data_message)

    await state.finish()
