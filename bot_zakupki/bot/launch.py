# type: ignore
import asyncio
import os
import sys

from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from loguru import logger

from bot_zakupki.bot.handlers import change_query_handlers
from bot_zakupki.bot.handlers import commands
from bot_zakupki.bot.handlers import common_handlers
from bot_zakupki.bot.handlers import search_query_handlers
from bot_zakupki.bot.middlewares import AccessMiddleware
from bot_zakupki.common import consts
from bot_zakupki.common import dates

logger.remove()
if consts.DEBUG:
    logger.add(
        f"{consts.BOT_LOG_FOLDER}{dates.get_today_date()}.log", level="DEBUG"
    )
    logger.add(sys.stdout, level="DEBUG")
else:
    logger.add(
        f"{consts.BOT_LOG_FOLDER}{dates.get_today_date()}.log", level="INFO"
    )
    logger.add(sys.stdout, level="INFO")


async def set_commands(bot: Bot):
    commands_to_set = [
        types.BotCommand(
            command=commands.ADD_NEW_QUERY,
            description=commands.ADD_NEW_QUERY_DESCRIPTION,
        ),
        types.BotCommand(
            command=commands.SHOW_ALL_MY_QUERIES,
            description=commands.SHOW_ALL_MY_QUERIES_DESCRIPTION,
        ),
        types.BotCommand(
            command=commands.CHANGE_QUERY,
            description=commands.CHANGE_QUERY_DESCRIPTION,
        ),
        types.BotCommand(
            command=commands.HELP, description=commands.HELP_DESCRIPTION
        ),
    ]

    if consts.DEBUG:
        commands_to_set.append(
            types.BotCommand(
                command=commands.STOP, description=commands.STOP_DESCRIPTION
            )
        )
        commands_to_set.append(
            types.BotCommand(
                command=commands.END_TRIAL_PERIOD,
                description=commands.END_TRIAL_PERIOD_DESCRIPTION,
            )
        )

    await bot.set_my_commands(commands_to_set)


@logger.catch
async def main():
    access_ids = os.getenv("TELEGRAM_ACCESS_ID")[1:-1]
    access_ids = access_ids.split(",")
    print(f"access_ids: {access_ids}")
    api_token = os.getenv("ADMIN_TELEGRAM_API_TOKEN")

    bot = Bot(token=api_token, parse_mode="HTML")

    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    dp.middleware.setup(AccessMiddleware([int(i) for i in access_ids]))

    common_handlers.register_handlers_common(dp)
    search_query_handlers.register_handlers_search_query(dp)
    change_query_handlers.register_change_search_query(dp)

    await set_commands(bot)

    # await dp.skip_updates()
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
