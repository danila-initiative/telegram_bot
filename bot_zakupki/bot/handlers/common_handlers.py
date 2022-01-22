# type: ignore
import asyncio

from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from loguru import logger

from bot_zakupki.bot import common
from bot_zakupki.bot.handlers import commands
from bot_zakupki.bot.handlers import messages
from bot_zakupki.common import consts
from bot_zakupki.common import db
from bot_zakupki.common import user_info


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

    if consts.DEBUG:
        dp.register_message_handler(
            cmd_stop, commands=commands.STOP, state="*"
        )
        dp.register_message_handler(
            cmd_end_trial_period, commands=commands.END_TRIAL_PERIOD, state="*"
        )


# =====commands.START=====


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    text, reply_markup = await cmd_start_func(message)

    await message.answer(text=text, reply_markup=reply_markup)


async def cmd_start_func(
    message: types.Message,
) -> tuple[str, types.ReplyKeyboardRemove]:
    user_id = message.from_user.id

    logger.info(f'Command "/{commands.START}" was used by user {user_id}')
    user = user_info.UserInfo(user_id=user_id)
    user.create_or_mark_active()

    return messages.CMD_START_MSG, types.ReplyKeyboardRemove()


# =====commands.HELP=====


async def cmd_help(message: types.Message, state: FSMContext):
    await state.finish()
    logger.info(
        messages.command_log_formation(commands.HELP, message.from_user.id)
    )

    await message.answer(
        messages.CMD_HELP_MSG, reply_markup=types.ReplyKeyboardRemove()
    )


# =====commands.SHOW_ALL_MY_QUERIES=====


async def cmd_show_all_my_queries(message: types.Message, state: FSMContext):
    await state.finish()
    text, reply_markup = await cmd_show_all_my_queries_func(message)

    await common.send_message(
        message.bot,
        user_id=message.from_user.id,
        text=text,
        reply_markup=reply_markup,
    )


async def cmd_show_all_my_queries_func(
    message: types.Message,
) -> tuple[str, types.ReplyKeyboardRemove]:
    await asyncio.sleep(5)
    user_id = message.from_user.id
    queries = db.get_all_search_queries_by_user_id(user_id)

    user = db.get_user_by_user_id(user_id=user_id)
    subscription_last_day = user.subscription_last_day if user else None
    answer = messages.all_queries_messages_formation(
        queries=queries, subscription_last_day=subscription_last_day
    )

    return answer, types.ReplyKeyboardRemove()


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Действие отменено", reply_markup=types.ReplyKeyboardRemove()
    )


# DEBUG
async def cmd_stop(message: types.Message, state: FSMContext):
    await state.finish()
    logger.info(
        messages.command_log_formation(commands.STOP, message.from_user.id)
    )

    await cmd_stop_function(message)
    await message.answer(
        f"user {message.from_user.id} is not active",
        reply_markup=types.ReplyKeyboardRemove(),
    )


async def cmd_stop_function(
    message: types.Message,
):
    user_id = message.from_user.id
    data = {"bot_is_active": 0}
    db.update_user_by_user_id(user_id=user_id, column_values=data)


# DEBUG
async def cmd_end_trial_period(message: types.Message, state: FSMContext):
    await state.finish()
    logger.info(
        messages.command_log_formation(
            commands.END_TRIAL_PERIOD, message.from_user.id
        )
    )
    user_id = message.from_user.id

    db.imitate_trial_period_end(user_id=user_id)
