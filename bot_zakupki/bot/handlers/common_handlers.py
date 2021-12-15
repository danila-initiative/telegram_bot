# type: ignore

from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from loguru import logger

from bot_zakupki.bot.handlers import commands
from bot_zakupki.bot.handlers import messages
from bot_zakupki.common import consts
from bot_zakupki.common import db
from bot_zakupki.common import user_info


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=[commands.START], state="*")
    dp.register_message_handler(cmd_help, commands=[commands.HELP], state="*")
    dp.register_message_handler(
        cmd_show_all_my_queries, commands=[commands.SHOW_ALL_MY_QUERIES]
    )
    dp.register_message_handler(cmd_cancel, commands=commands.CANCEL, state="*")
    dp.register_message_handler(
        cmd_cancel, Text(equals="отмена", ignore_case=True), state="*"
    )

    if consts.DEBUG:
        dp.register_message_handler(cmd_stop, commands=commands.STOP, state="*")
        dp.register_message_handler(
            cmd_end_trial_period, commands=commands.END_TRIAL_PERIOD, state="*"
        )


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    text, reply_markup = await cmd_start_func(message)

    await message.answer(text=text, reply_markup=reply_markup)


async def cmd_start_func(message: types.Message):
    user_id = message.from_user.id

    logger.info(f'Command "/{commands.START}" was used by user {user_id}')

    user_info.create_user_or_mark_active(user_id=user_id)

    return messages.CMD_START_MSG, types.ReplyKeyboardRemove()


async def cmd_help(message: types.Message, state: FSMContext):
    await state.finish()
    logger.info(messages.command_log_formation(commands.HELP, message.from_user.id))

    await message.answer(
        messages.CMD_HELP_MSG, reply_markup=types.ReplyKeyboardRemove()
    )


async def cmd_show_all_my_queries(message: types.Message, state: FSMContext):
    await state.finish()
    queries = db.get_all_search_queries_by_user_id(message.from_user.id)
    if len(queries) == 0:
        answer = messages.THERE_IS_NO_QUERIES
    else:
        answer = messages.all_queries_messages_formation(queries=queries)

    await message.answer(answer)


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())


# DEBUG
async def cmd_stop(message: types.Message, state: FSMContext):
    await state.finish()
    logger.info(messages.command_log_formation(commands.STOP, message.from_user.id))

    user_id = message.from_user.id
    data = {"bot_is_active": 0}
    db.update_user_by_user_id(user_id=user_id, column_values=data)
    await message.answer(
        f"user {user_id} is not active",
        reply_markup=types.ReplyKeyboardRemove(),
    )


# DEBUG
async def cmd_end_trial_period(message: types.Message, state: FSMContext):
    await state.finish()
    logger.info(
        messages.command_log_formation(commands.END_TRIAL_PERIOD, message.from_user.id)
    )
    user_id = message.from_user.id

    db.imitate_trial_period_end(user_id=user_id)
