import pytest

from bot_zakupki.bot.handlers import common_handlers
from bot_zakupki.common import db


@pytest.mark.asyncio
async def test_cmd_start_func(setup_db, get_message):
    cursor = setup_db.cursor()
    text, reply_markup = await common_handlers.cmd_start_func(get_message(11111))
    print(f'text: {text}')
    users = db.get_all_users(cursor=cursor)
    print(f'Users: {users}')

    assert False