from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from bot_zakupki.bot.handlers import commands
from bot_zakupki.bot.handlers import messages


def register_handlers_subscription(dp: Dispatcher):
    dp.register_message_handler(
        cmd_update_subscription,
        commands=commands.UPDATE_SUBSCRIPTION,
        state="*",
    )
    dp.register_callback_query_handler(
        callback_update_subscription, Text(startswith="update_subscription_")
    )


async def cmd_update_subscription(message: types.Message, state: FSMContext):
    await state.finish()

    answer = messages.UPDATE_SUBSCRIPTION_MSG

    days = [30, 90, 180]
    queries = [1, 5]

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for day in days:
        for query in queries:
            if query == 1:
                postfix = "запрос"
            else:
                postfix = "запросов"
            button = types.InlineKeyboardButton(
                text=f"{day} дней - {query} {postfix}",
                callback_data=f"update_subscription_{day}_{query}"
            )
            buttons.append(button)

    keyboard.add(*buttons)

    await message.answer(answer, reply_markup=keyboard)


async def callback_update_subscription(call: types.CallbackQuery):
    params = call.data.split("_")
    days = params[-2]
    query_numbers = params[-1]

    await call.message.answer(f"Дней {days}, запросов {query_numbers}")
