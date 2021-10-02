import asyncio
import os

from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot_zakupki.bot.handlers import commands
from bot_zakupki.bot.handlers import common_handlers
from bot_zakupki.bot.handlers import search_query_handlers
from bot_zakupki.bot.middlewares import AccessMiddleware


async def set_commands(bot: Bot):
    commands_to_set = [
        types.BotCommand(command=commands.START, description='типа старт'),
        types.BotCommand(command=commands.ADD_NEW_QUERY, description=commands.ADD_NEW_QUERY_DESCRIPTION),
        types.BotCommand(command="/cancel", description="Отменить текущее действие")
    ]
    await bot.set_my_commands(commands_to_set)


async def main():
    access_id = os.getenv("TELEGRAM_ACCESS_ID")
    api_token = os.getenv('ADMIN_TELEGRAM_API_TOKEN')

    bot = Bot(token=api_token)

    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    dp.middleware.setup(AccessMiddleware(int(access_id)))

    common_handlers.register_handlers_common(dp)
    search_query_handlers.register_handlers_search_query(dp)

    await set_commands(bot)

    # await dp.skip_updates()
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
