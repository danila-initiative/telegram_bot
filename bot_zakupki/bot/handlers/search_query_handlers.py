from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
from aiogram.dispatcher.filters.state import StatesGroup

from bot_zakupki.bot.handlers import commands
from bot_zakupki.bot.handlers import messages
from bot_zakupki.common import models


class SearchParameters(StatesGroup):
    search_string = State()
    location = State()
    min_price = State()
    max_price = State()


def register_handlers_search_query(dp: Dispatcher):
    dp.register_message_handler(new_query, commands=commands.ADD_NEW_QUERY, state="*")
    dp.register_message_handler(callback=process_search_string, state=SearchParameters.search_string)

    dp.register_message_handler(process_location,
                                lambda message: message.text in models.CUSTOMER_PLACES.keys(),
                                state=SearchParameters.location)
    dp.register_message_handler(process_location_invalid,
                                lambda message: message.text not in models.CUSTOMER_PLACES.keys(),
                                state=SearchParameters.location)

    dp.register_message_handler(process_min_price,
                                lambda message: message.text.isdigit() and int(message.text) >= 0,
                                state=SearchParameters.min_price)
    dp.register_message_handler(process_min_price_invalid,
                                lambda message: not message.text.isdigit() or int(message.text) < 0,
                                state=SearchParameters.min_price)

    dp.register_message_handler(process_max_price,
                                lambda message: message.text.isdigit(),
                                state=SearchParameters.max_price)
    dp.register_message_handler(process_max_price_invalid,
                                lambda message: not message.text.isdigit(),
                                state=SearchParameters.max_price)


async def new_query(message: types.Message):
    await SearchParameters.search_string.set()

    await message.answer(messages.NEW_QUERY_MSG, reply_markup=types.ReplyKeyboardRemove())


async def process_search_string(message: types.Message, state: FSMContext):
    await state.update_data(search_string=message.text.lower())
    await SearchParameters.location.set()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    for place in models.CUSTOMER_PLACES:
        keyboard.add(place)

    await message.reply(messages.SELECT_LOCATION, reply_markup=keyboard)


async def process_location_invalid(message: types.Message, state: FSMContext):
    await message.reply('Неверно указан регион для поиска. Выберите регион из перечисленных ниже')


async def process_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text.lower())
    await SearchParameters.min_price.set()

    markup = types.ReplyKeyboardRemove()

    await message.answer("Теперь введите минимальную цену в рублях", reply_markup=markup)


async def process_min_price_invalid(message: types.Message, state: FSMContext):
    await message.reply('Неверно указана минимальная цена для поиска.')


async def process_min_price(message: types.Message, state: FSMContext):
    await state.update_data(min_price=int(message.text))
    await SearchParameters.max_price.set()

    await message.answer("Теперь введите максимальную цену в рублях")


async def process_max_price_invalid(message: types.Message, state: FSMContext):
    await message.reply('Максимальная цена должна быть целым числом')


async def process_max_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if int(message.text) < data["min_price"]:
        await message.reply('Максимальная цена меньше минимальной. Введите другое число')
        return

    data["max_price"] = int(message.text)

    await message.answer(f'Строка для поиска: {data["search_string"]} \n'
                         f'регион: {data["location"]} \n'
                         f'диапазон цен для поиска: от {data["min_price"]} до {data["max_price"]}')

    await state.finish()
