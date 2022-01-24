import sys

import pytest
from aiogram.dispatcher import storage
from aiogram.types import Chat
from aiogram.types import Message
from aiogram.types import User
from loguru import logger

from bot_zakupki.common import consts
from bot_zakupki.common import dates
from bot_zakupki.common import db


@pytest.fixture
def extra_logging():
    db.delete_all_data()
    logger.remove()
    if consts.DEBUG:
        logger.add(
            f"{consts.BOT_LOG_FOLDER}{dates.get_today_date()}.log",
            level="DEBUG",
        )
        logger.add(sys.stdout, level="DEBUG")
    else:
        logger.add(
            f"{consts.BOT_LOG_FOLDER}{dates.get_today_date()}.log",
            level="INFO",
        )
        logger.add(sys.stdout, level="INFO")


@pytest.fixture
def clear_db(extra_logging):
    db.delete_all_data()


@pytest.fixture
def setup_db(clear_db):
    db.init_db()


@pytest.fixture
def get_message():
    def _get_message(telegram_id: int):
        message = Message()
        message.message_id = 3139
        message.from_user = User(
            id=telegram_id,
            is_bot=False,
            first_name="Dani",
            last_name="Master",
            username="DaniMaster",
            language_code="en",
        )
        message.chat = Chat(
            id=telegram_id,
            first_name="Danila",
            last_name="Master",
            username="DanilaMaster",
            types="private",
        )
        # message.date=1639392877
        message.text = ("/start",)
        # message.entities=MessageEntity(
        #         type="bot_command",
        #         offset=0,
        #         length=6
        #     )

        return message

    return _get_message


@pytest.fixture
def get_fsm_context():
    return storage.FSMContext(
        storage=storage.BaseStorage,
        chat="chat",
        user=66666666,
    )
