"""Аутентификация — пропускаем сообщения только от определенного id"""
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware


class AccessMiddleware(BaseMiddleware):
    def __init__(self, access_ids: str):
        access_ids = access_ids.split(',')
        self.access_id = [int(x) for x in access_ids]
        super().__init__()

    async def on_process_message(self, message: types.Message, _):
        if int(message.from_user.id) not in self.access_id:
            await message.answer("Access Denied")
            raise CancelHandler()