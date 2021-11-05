# type: ignore
import datetime

from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from loguru import logger

from bot_zakupki.bot.handlers import commands
from bot_zakupki.bot.handlers import messages
from bot_zakupki.common import consts
from bot_zakupki.common import db


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(
        cmd_start, commands=[commands.START], state="*"
    )
    dp.register_message_handler(cmd_help, commands=[commands.HELP], state="*")
    dp.register_message_handler(
        cmd_show_all_my_queries, commands=[commands.SHOW_ALL_MY_QUERIES]
    )
    dp.register_message_handler(
        cmd_cancel, commands=commands.CANCEL, state="*"
    )
    dp.register_message_handler(
        cmd_cancel, Text(equals="отмена", ignore_case=True), state="*"
    )

    if consts.DEBUG:
        dp.register_message_handler(
            cmd_stop, commands=commands.STOP, state="*"
        )
        dp.register_message_handler(
            cmd_end_trial_period, commands=commands.END_TRIAL_PERIOD, state="*"
        )


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    logger.info(
        f'Command "/{commands.START}" was used by user {message.from_user.id}'
    )

    user_id = message.from_user.id
    user = db.get_user_by_user_id(user_id=user_id)
    if user is None:
        db.insert_new_user(user_id=user_id)
    elif not user.bot_is_active:
        logger.info(f"user {user_id} was not active")
        now = datetime.datetime.now().replace(microsecond=0)
        data = {"bot_start_date": now, "bot_is_active": 1}
        db.update_user_by_user_id(user_id=user_id, column_values=data)

    await message.answer(
        messages.CMD_START_MSG, reply_markup=types.ReplyKeyboardRemove()
    )


async def cmd_help(message: types.Message, state: FSMContext):
    await state.finish()
    logger.info(
        f'Command "/{commands.HELP}" was used by user {message.from_user.id}'
    )

    await message.answer(
        messages.CMD_HELP_MSG, reply_markup=types.ReplyKeyboardRemove()
    )


async def cmd_show_all_my_queries(message: types.Message, state: FSMContext):
    await state.finish()
    queries = db.get_all_search_queries_by_user_id(message.from_user.id)
    answer = messages.all_queries_messages_formation(queries=queries)

    await message.answer(answer)


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Действие отменено", reply_markup=types.ReplyKeyboardRemove()
    )


async def cmd_stop(message: types.Message, state: FSMContext):
    await state.finish()
    logger.info(
        f'Command "/{commands.STOP}" was used by user {message.from_user.id}'
    )

    user_id = message.from_user.id
    data = {"bot_is_active": 0}
    db.update_user_by_user_id(user_id=user_id, column_values=data)
    await message.answer(
        f"user {user_id} is not active",
        reply_markup=types.ReplyKeyboardRemove(),
    )


async def cmd_end_trial_period(message: types.Message, state: FSMContext):
    await state.finish()
    logger.info(
        f'Command "/{commands.END_TRIAL_PERIOD}" '
        f"was used by user {message.from_user.id}"
    )
    user_id = message.from_user.id

    db.imitate_trial_period_end(user_id=user_id)
