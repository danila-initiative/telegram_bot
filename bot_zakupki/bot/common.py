# type: ignore
import asyncio
import os
import typing

from aiogram import Bot
from aiogram.utils import exceptions
from loguru import logger

from bot_zakupki.bot import bot_service


async def send_message(
    bot: Bot,
    user_id: int,
    text: str,
    reply_markup: typing.Any = None,
    disable_notification: bool = False,
) -> bool:
    """
    Safe messages sender
    :param bot:
    :param user_id:
    :param text:
    :param reply_markup:
    :param disable_notification:
    :return:
    """
    try:
        await bot.send_message(
            user_id,
            text,
            reply_markup=reply_markup,
            disable_notification=disable_notification,
        )
    except exceptions.BotBlocked:
        logger.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        logger.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        logger.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. "
            f"Sleep {e.timeout} seconds."
        )
        await asyncio.sleep(e.timeout)
        return await send_message(bot, user_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        logger.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        logger.exception(f"Target [ID:{user_id}]: failed")
    else:
        logger.info(f"Target [ID:{user_id}]: success")
        return True
    return False


async def send_message_to_admin_bot(
    text: str, reply_markup: typing.Any = None
):
    admins_ids = os.getenv("TELEGRAM_ACCESS_ID")[1:-1].split(",")[:1]
    api_token = os.getenv("ADMIN_TELEGRAM_API_TOKEN")

    bot_instance = bot_service.BotService(
        api_token=api_token, admins_ids=admins_ids
    )
    for admins_id in admins_ids:
        await send_message(
            bot=bot_instance.bot, user_id=int(admins_id), text=text
        )
