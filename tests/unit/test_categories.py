import json
from pytest_mock import MockerFixture
from service import report_category_handler

def test_get_report_categories_list(mocker: MockerFixture):
    response = report_category_handler.get_report_categories_list(mocker.MagicMock(), mocker.MagicMock())

    body = json.loads(response["body"])
    assert body is not None