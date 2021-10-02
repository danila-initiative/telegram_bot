"""Аутентификация — пропускаем сообщения только от определенного id"""
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware


class AccessMiddleware(BaseMiddleware):
    def __init__(self, access_ids: int):
        self.access_ids = access_ids
        super().__init__()

    async def on_process_message(self, message: types.Message, _):
        if int(message.from_user.id) != self.access_ids:
            await message.answer("Access Denied")
            raise CancelHandler()
