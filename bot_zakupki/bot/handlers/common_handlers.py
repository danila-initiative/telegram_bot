# type: ignore
import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from loguru import logger

from bot_zakupki.bot.handlers import commands
from bot_zakupki.bot.handlers import messages
from bot_zakupki.common import dates
from bot_zakupki.common import db


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(
        cmd_start, commands=[commands.START, "/help"], state="*"
    )
    dp.register_message_handler(cmd_stop, commands=commands.STOP, state="*")
    dp.register_message_handler(
        cmd_show_all_my_queries, commands=[commands.SHOW_ALL_MY_QUERIES]
    )
    dp.register_message_handler(
        cmd_cancel, commands=commands.CANCEL, state="*"
    )
    dp.register_message_handler(
        cmd_cancel, Text(equals="отмена", ignore_case=True), state="*"
    )


async def cmd_start(message: types.Message, state: FSMContext):
    logger.info(f"{__name__} is working")

    user_id = message.from_user.id
    user = db.get_user_by_user_id(user_id=user_id)
    if user is None:
        db.insert_new_user(user_id=user_id)
    elif not user.bot_is_active:
        logger.info(f"user {user_id} was not active")
        now = datetime.datetime.now().replace(microsecond=0)
        data = {"bot_start_date": now, "bot_is_active": 1}
        db.update_user_by_user_id(user_id=user_id, column_values=data)

    await state.finish()
    await message.answer(
        messages.CMD_START_MSG, reply_markup=types.ReplyKeyboardRemove()
    )


async def cmd_stop(message: types.Message):
    logger.info(f"{__name__} is working")

    user_id = message.from_user.id
    data = {"bot_is_active": 0}
    db.update_user_by_user_id(user_id=user_id, column_values=data)
    await message.answer(
        f"user {user_id} is not active",
        reply_markup=types.ReplyKeyboardRemove(),
    )


async def cmd_show_all_my_queries(message: types.Message):
    now = datetime.datetime.now().replace(microsecond=0)
    queries = db.get_all_active_search_queries_by_user_id(
        message.from_user.id, now
    )
    answer = ""
    if not queries:
        answer = "У тебя сейчас нет активных запросов"

    for i, query in enumerate(queries):
        tmp = (
            f"<b>{i + 1}</b>. 🔍 Ключевая строка: {query.search_string}\n"
            f"    🌏 Регион: {query.location}\n"
            f"    💰 Цена: от {query.min_price} до {query.max_price} рублей\n"
            f"    🗓️ Окончание подписки: "
            f"{dates.format_date(query.subscription_last_day)}\n"
            f"\n"
        )
        answer += tmp

    await message.answer(answer)


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Действие отменено", reply_markup=types.ReplyKeyboardRemove()
    )
