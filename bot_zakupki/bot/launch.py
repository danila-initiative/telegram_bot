# type: ignore
import asyncio
import os
import sys

from loguru import logger

from bot_zakupki.bot import bot_service as b_serv
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


@logger.catch
async def main():
    admins_ids = os.getenv("TELEGRAM_ACCESS_ID")[1:-1].split(",")
    api_token = os.getenv("ADMIN_TELEGRAM_API_TOKEN")

    bot_service = b_serv.BotService(api_token=api_token, admins_ids=admins_ids)
    await bot_service.run()


if __name__ == "__main__":
    asyncio.run(main())
