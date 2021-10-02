from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from bot_zakupki.bot.handlers import commands
from bot_zakupki.bot.handlers import messages


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=[commands.START, '/help'], state="*")
    dp.register_message_handler(cmd_cancel, commands=commands.CANCEL, state="*")
    dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(messages.CMD_START_MSG, reply_markup=types.ReplyKeyboardRemove())


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())
