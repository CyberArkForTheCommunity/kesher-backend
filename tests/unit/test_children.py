import json
from pytest_mock import MockerFixture
from service import children_handler

def test_get_child_reports(mocker: MockerFixture):
    child_id = '217345691'

    response = children_handler.get_child_reports({"pathParameters": {"child_id": child_id}}, mocker.MagicMock())

    daily_reports = json.loads(response["body"])['daily_reports']
    assert daily_reports[0]['value']