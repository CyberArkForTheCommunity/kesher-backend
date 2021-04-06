import json
from pytest_mock import MockerFixture
from service.dtos.kesher_dto import KesherDto
from service import children_handler

from tests.unit.test_utils import random_string


def test_get_child_reports(mocker: MockerFixture):
    child_id = '217345691'

    response = children_handler.get_child_reports({"pathParameters": {"child_id": child_id}}, mocker.MagicMock())

    daily_reports = json.loads(response["body"])['daily_reports']
    assert daily_reports[0]['value']

