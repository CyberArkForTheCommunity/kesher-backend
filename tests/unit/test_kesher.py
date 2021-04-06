import json
from pytest_mock import MockerFixture
from aws_lambda_context import LambdaContext
from service.dtos.kesher_dto import KesherDto
from service import handler

from tests.unit.test_utils import random_string


def test_get_kesher(mocker: MockerFixture):
    kesher_dto: KesherDto = KesherDto(name=random_string())

    response = handler.get_kesher({"pathParameters": {"name": kesher_dto.name}}, mocker.MagicMock())
    actual_kesher = json.loads(response["body"])

    assert actual_kesher['name'] == kesher_dto.name