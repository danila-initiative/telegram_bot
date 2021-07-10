#!venv/bin/python
import os
import logging
import time
from aiogram import Bot, Dispatcher, executor, types
from middlewares import AccessMiddleware

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

ACCESS_ID = os.getenv("TELEGRAM_ACCESS_ID")
ADMIN_TELEGRAM_API_TOKEN = os.environ['ADMIN_TELEGRAM_API_TOKEN']

# Объект бота
bot = Bot(token = ADMIN_TELEGRAM_API_TOKEN)
# Диспетчер для бота
dp = Dispatcher(bot)

dp.middleware.setup(AccessMiddleware(ACCESS_ID))

# Хэндлер на команду /start
@dp.message_handler(commands="start")
async def cmd_test1(message: types.Message):
    # for i in range(5):
    #     await message.answer(f"Message {i}")
    #     time.sleep(3)
    
        await message.answer("Сегодняшняя статистика: /today\n")

if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)