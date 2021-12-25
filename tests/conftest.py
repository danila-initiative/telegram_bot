import pytest
from aiogram.dispatcher import storage
from aiogram.types import Chat
from aiogram.types import Message
from aiogram.types import User

from bot_zakupki.common import db


@pytest.fixture
def clear_db():
    db.delete_all_data()


@pytest.fixture
def setup_db(clear_db):
    # if os.path.exists(consts.PATH_TO_TEST_DB):
    #     os.remove(consts.PATH_TO_TEST_DB)
    # conn = sqlite3.connect(consts.PATH_TO_TEST_DB)
    # cursor = conn.cursor()
    db.init_db()

    # yield conn
    # conn.close()


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
