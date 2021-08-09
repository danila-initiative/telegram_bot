#!venv/bin/python
import os
import logging
import random
from aiogram import Bot, Dispatcher, executor, types
from middlewares import AccessMiddleware
from dates import GetCurrentDate
import asyncio
import datetime


# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

ACCESS_ID = os.getenv("TELEGRAM_ACCESS_ID")
ADMIN_TELEGRAM_API_TOKEN = os.getenv('ADMIN_TELEGRAM_API_TOKEN')

# Объект бота
bot = Bot(token=ADMIN_TELEGRAM_API_TOKEN)

# Диспетчер для бота
dp = Dispatcher(bot)

dp.middleware.setup(AccessMiddleware(ACCESS_ID))

# Хэндлер на команду /start
@dp.message_handler(state="*", commands="start")
async def send_welcome(message: types.Message):
    await message.answer(
        "Админский бот для сервиса подбора закупок\n\n"
        "Получать ежедневную рассылку для всех пользователей: /get_daily_newsletter\n"
        )


# Хэндлер на команду /get_daily_newsletter
@dp.message_handler(commands="get_daily_newsletter")
async def get_daily_newsletter(message: types.Message):
    isSendedToday = False
    current_date = GetCurrentDate().date()

    await message.answer(current_date)

    while True:
        if (isSendedToday == False) and (GetCurrentDate().time() > datetime.time(12, 56, 00)):
            await message.answer("Сейчас больше 12:56")
            isSendedToday = True
        else:
            await message.answer(GetCurrentDate().time())

        if GetCurrentDate().date() > current_date:
            current_date = GetCurrentDate().date()
            isSendedToday = False
        await asyncio.sleep(random.randint(10, 20))

    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
