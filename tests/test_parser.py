import datetime

import pytest
from requests.models import Response

from bot_zakupki.common import models
from bot_zakupki.common import parser


# logger.add(sys.stderr, format="{time} {level} {message}",
#            level="INFO")

# TODO: Дописать параметризованную проверку результатов
# TODO: добавить тест с пустой страницей выдачи
@pytest.mark.parametrize(
    'expected_result,',
    (
            pytest.param(
                models.Result(search_string='лифт', number_of_purchase='№ 0373200041521001009',
                              publish_date=datetime.datetime.strptime('07.09.2021', '%d.%m.%Y'),
                              finish_date=datetime.datetime.strptime('24.09.2021', '%d.%m.%Y'),
                              price=9175661,
                              subject_of_purchase='Выполнение работ по замене лифтового оборудования в рамках капитального ремонта в ГБУ ГЦМ',
                              link='https://zakupki.gov.ru/epz/order/notice/ea44/view/common-info.html?regNumber=0373200041521001009',
                              customer='ГОСУДАРСТВЕННОЕ КАЗЕННОЕ УЧРЕЖДЕНИЕ ГОРОДА МОСКВЫ "ДИРЕКЦИЯ ПО ОБЕСПЕЧЕНИЮ ДЕЯТЕЛЬНОСТИ ОРГАНИЗАЦИЙ ТРУДА И СОЦИАЛЬНОЙ ЗАЩИТЫ НАСЕЛЕНИЯ ГОРОДА МОСКВЫ"',
                              location='Москва'),
                id='0',
            ),
    )
)
def test_parser_page(expected_result):
    page = open("tests/static/test_parser/results.html", 'r', encoding='utf-8')
    response = Response()
    response._content = str(page.read())
    results = parser.parse_result_page(response, "лифт", "Москва")

    assert results[0] == expected_result


@pytest.mark.parametrize(
    'expected_url,search_string,min_price,max_price,place_name,publish_date_from,'
    'publish_date_to,close_date_from,close_date_to',
    (
            pytest.param('tests/static/test_parser/expected_url_1.txt',
                         'лифт',
                         10000,
                         2000000,
                         'Москва',
                         '01.09.2021',
                         '03.09.2021',
                         '08.09.2021',
                         '18.09.2021',
                         id='1',
                         ),
            pytest.param('tests/static/test_parser/expected_url_2.txt',
                         ' современная школа ',
                         10000,
                         20000000,
                         'Москва',
                         '01.09.2021',
                         '03.09.2021',
                         '08.09.2021',
                         '18.09.2021',
                         id='2',
                         ),
            pytest.param('tests/static/test_parser/expected_url_3.txt',
                         ' Эскалатор ',
                         10000,
                         20000000,
                         'Москва',
                         '01.09.2021',
                         None,
                         None,
                         None,
                         id='3',
                         ),
    )
)
def test_request_formation(expected_url, search_string, min_price, max_price, place_name, publish_date_from,
                           publish_date_to, close_date_from, close_date_to):
    params = models.RequestParameters(
        search_string=search_string,
        min_price=min_price,
        max_price=max_price,
        place_name=place_name,
        publish_date_from=publish_date_from,
        publish_date_to=publish_date_to,
        close_date_from=close_date_from,
        close_date_to=close_date_to,
    )

    url = parser.request_formation(params)

    with open(expected_url, 'r', ) as file:
        expected = file.readline()
        assert expected == url
