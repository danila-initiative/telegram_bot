#!venv/bin/python
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, executor
from aiogram.types import InputFile
from dotenv import load_dotenv
from loguru import logger

from bot_common import send_message, send_document

import consts
from dates import FormatDate, GetCurrentDate

load_dotenv()

ACCESS_ID = os.environ.get("TELEGRAM_ACCESS_ID")
ADMIN_TELEGRAM_API_TOKEN = os.environ.get('ADMIN_TELEGRAM_API_TOKEN')

# Объект бота
bot = Bot(token=ADMIN_TELEGRAM_API_TOKEN)

# Диспетчер для бота
dp = Dispatcher(bot)

@logger.catch
async def broadcaster(user_id):
    folder = f"{consts.RESULTS_FOLDER}/{FormatDate(GetCurrentDate())}"
    files = os.listdir(folder)

    await send_message(bot, user_id, f"Сегодня {FormatDate(GetCurrentDate())} создано {len(files)} документов")
    
    for file in files:
        file_name = folder + "/" + file
        await send_document(bot, user_id, file_name)
        break

    log_file = f"{consts.LOG_FILE}{FormatDate(GetCurrentDate())}.log"
    await send_document(bot, user_id, log_file)


if __name__ == "__main__":
    logger.add(consts.LOG_FILE + "{time:YYYY-MM-DD}.log", format="{time} {level} {message}", 
                level="INFO")
    logger.info(f"=====Script {Path(__file__).name} launched=====")
    # Запуск бота
    # for account in [70365850, 405503153]:
    for user_id in [70365850]:
        logger.info(f"=====Start sending files to user {user_id}=====")
        executor.start(dp, broadcaster(user_id))
