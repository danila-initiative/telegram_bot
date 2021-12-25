import pytest

from bot_zakupki.bot.handlers import search_query_handlers


@pytest.mark.parametrize(
    "input_string,expected_output",
    (
        pytest.param(
            "   всякие   пробелы    ",
            "всякие пробелы",
            id="1",
        ),
        pytest.param(
            '   "пробелы" % и №/странные   ^$символы?   ',
            "пробелы и странные символы",
            id="2",
        ),
        pytest.param(
            "нефтепродукты (Бензин АИ-95) г.Челяба",
            "нефтепродукты бензин аи 95 г.челяба",
            id="3",
        ),
    ),
)
@pytest.mark.asyncio
async def test_search_string_filter(
    setup_db, get_message, input_string, expected_output
):
    search_string = await search_query_handlers._search_string_filter(input_string)
    assert search_string == expected_output
