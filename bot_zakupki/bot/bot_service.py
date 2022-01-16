# type: ignore
import sqlite3
from dataclasses import dataclass

from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot_zakupki.bot import middlewares
from bot_zakupki.bot.handlers import change_query_handlers
from bot_zakupki.bot.handlers import commands
from bot_zakupki.bot.handlers import common_handlers
from bot_zakupki.bot.handlers import search_query_handlers
from bot_zakupki.bot.handlers import subscription_handlers
from bot_zakupki.common import consts


class DBService:
    connection: sqlite3.Connection
    cursor: sqlite3.Cursor


@dataclass
class BotService:
    def __init__(self, api_token: str, admins_ids: list[str]):
        self.api_token: str = api_token
        self.admins_ids: list[str] = admins_ids
        self.storage = MemoryStorage()
        self.bot = Bot(token=api_token, parse_mode="HTML")
        self.dp = Dispatcher(self.bot, storage=self.storage)
        self._middleware_setup()
        self._register_handlers()

    async def run(self):
        await self._set_commands()
        await self.dp.start_polling()

    def _register_handlers(self):
        common_handlers.register_handlers_common(self.dp)
        search_query_handlers.register_handlers_search_query(self.dp)
        change_query_handlers.register_change_search_query(self.dp)
        subscription_handlers.register_handlers_subscription(self.dp)

    def _middleware_setup(self):
        self.dp.middleware.setup(
            middlewares.AccessMiddleware([int(i) for i in self.admins_ids])
        )

    async def _set_commands(self):
        commands_to_set = [
            types.BotCommand(command.name, command.description)
            for command in commands.BOT_COMMANDS
        ]

        if consts.DEBUG:
            [
                commands_to_set.append(
                    types.BotCommand(command.name, command.description)
                )
                for command in commands.DEBUG_COMMANDS
            ]

        await self.bot.set_my_commands(commands_to_set)
