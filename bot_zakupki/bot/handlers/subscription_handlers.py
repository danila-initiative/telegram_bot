# type: ignore
import datetime
import os

from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types.message import ContentTypes
from loguru import logger

from bot_zakupki.bot.handlers import commands
from bot_zakupki.bot.handlers import messages
from bot_zakupki.common import consts
from bot_zakupki.common import dates
from bot_zakupki.common import db
from bot_zakupki.common import models

PAYMENTS_PROVIDER_TOKEN = os.getenv("PAYMENTS_PROVIDER_TOKEN")

# prices = {
#     "30": {
#         "1": 99900,
#         "5": 499900,
#     },
#     "90": {
#         "1": 499900,
#         "5": 1249900,
#     },
#     "180": {
#         "1": 899900,
#         "5": 2149900,
#     },
# }


def get_price(
    days_number: str, queries_number: str
) -> list[types.LabeledPrice]:
    config = models.Config()
    bot_prices = [
        types.LabeledPrice(
            label=f"Подписка на {days_number} дней и {queries_number} запросов",
            amount=config.price[int(days_number)][int(queries_number)],
        ),
    ]
    return bot_prices


def register_handlers_subscription(dp: Dispatcher):
    dp.register_message_handler(
        cmd_update_subscription,
        commands=commands.UPDATE_SUBSCRIPTION,
        state="*",
    )
    dp.register_callback_query_handler(
        callback_update_subscription, Text(startswith="update_subscription_")
    )
    dp.register_pre_checkout_query_handler(
        checkout,
        lambda query: True,
    )
    dp.register_message_handler(
        got_payment, content_types=ContentTypes.SUCCESSFUL_PAYMENT
    )


async def cmd_update_subscription(message: types.Message, state: FSMContext):
    await state.finish()

    logger.info(
        messages.command_log_formation(commands.UPDATE_SUBSCRIPTION,
                                       message.from_user.id)
    )

    answer = messages.subscription_message_formation(message.from_user.id)

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
                callback_data=f"update_subscription_{day}_{query}",
            )
            buttons.append(button)

    keyboard.add(*buttons)

    media = types.MediaGroup()
    media.attach_photo(
        types.InputFile("/app/bot_zakupki/static/price.png"),
    )

    await message.answer(answer)
    await message.answer_media_group(media=media)
    await message.answer("Добавить подписку:", reply_markup=keyboard)


async def callback_update_subscription(call: types.CallbackQuery):
    params = call.data.split("_")
    days = params[-2]
    query_numbers = params[-1]

    logger.info(f"user: {call.from_user.id}; pressed button: days {days}, "
                f"query numbers: {query_numbers}")

    if query_numbers == 1:
        postfix = "запрос"
    else:
        postfix = "запросов"

    await call.message.bot.send_invoice(
        call.message.chat.id,
        title="Оплата подписки",
        description=f"Подписка на {days} дней, {query_numbers} {postfix}",
        payload=f"{days},{query_numbers}",
        provider_token=PAYMENTS_PROVIDER_TOKEN,
        currency="RUB",
        prices=get_price(days, query_numbers),
        start_parameter="time-machine-example",
        # provider_data={
        #     "receipt": {
        #         "customer": {
        #             "full_name": "Иванов Иван Иванович",
        #             "phone": "79000000000",
        #             "email": "forspam@vivaldi.net",
        #         },
        #         "items": [
        #             {
        #                 "description": f"Подписка на {days} дней,
        #                 {query_numbers} {postfix}",
        #                 "quantity": "1.00",
        #                 "amount": {
        #                     "value": str(prices[days][query_numbers]//100),
        #                     "currency": "RUB"
        #                 },
        #                 "vat_code": "2",
        #                 "payment_mode": "full_prepayment",
        #                 "payment_subject": "commodity"
        #         }]
        #     }
        # }
    )


async def checkout(pre_checkout_query: types.PreCheckoutQuery):
    logger.info(f"{pre_checkout_query.as_json()}")

    await pre_checkout_query.bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True,
        error_message="Aliens tried to steal your card's CVV,"
        " but we successfully protected your credentials,"
        " try to pay again in a few minutes, we need a small rest.",
    )


# Если платеж прошел успешно
async def got_payment(message: types.Message):
    logger.info(f"user: {message.from_user.id}; "
                f"successful_payment: {message.successful_payment}")

    payload = message.successful_payment.invoice_payload
    payload = payload.split(",")
    days = payload[0]
    query_numbers = payload[1]

    now = dates.get_current_time_for_db()

    user_id = message.from_user.id
    user = db.get_user_by_user_id(user_id)

    subscription_last_day = user.subscription_last_day if user else None

    if subscription_last_day is None or subscription_last_day < now:
        new_last_sub_day = now + datetime.timedelta(days=int(days))
    else:
        new_last_sub_day = subscription_last_day + datetime.timedelta(
            days=int(days)
        )

    user_data_update = {
        consts.USER_SUBSCRIPTION_LAST_DAY: new_last_sub_day,
        consts.USER_PAYMENT_LAST_DAY: now,
        consts.USER_MAX_NUMBER_OF_QUERIES: int(query_numbers),
    }
    db.update_user_by_user_id(user_id=user_id, column_values=user_data_update)

    await message.bot.send_message(
        message.chat.id, messages.after_subscription_message_formation(user_id)
    )
