from datetime import datetime
from decimal import Decimal
from http import HTTPStatus

from aws_lambda_context import LambdaContext
from aws_lambda_powertools import Logger
from pydantic import ValidationError

from service.dtos.kesher_dto import KesherDto
from service.models.kesher import Kesher
from service.response_utils import build_error_response, build_response

logger = Logger()


# POST /kesher
@logger.inject_lambda_context(log_event=True)
def create_kesher(event: dict, context: LambdaContext) -> dict:
    try:
        kesher_dto: KesherDto = KesherDto.parse_raw(event["body"])
        now: Decimal = Decimal(datetime.now().timestamp())
        kesher: Kesher = Kesher(name=kesher_dto.name, created_date=now, updated_date=now)
        return build_response(http_status=HTTPStatus.CREATED, body=kesher.json())
    except (ValidationError, TypeError) as err:
        return build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return build_error_response(err)


# PUT /kesher/{name}
@logger.inject_lambda_context(log_event=True)
def update_kesher(event: dict, context: LambdaContext) -> dict:
    if "pathParameters" not in event or "name" not in event["pathParameters"]:
        return build_response(HTTPStatus.BAD_REQUEST, "")

    try:
        # pylint: disable=unused-variable
        name: str = event["pathParameters"]["name"]
        kesher_dto: KesherDto = KesherDto.parse_raw(event["body"])
        now: Decimal = Decimal(datetime.now().timestamp())
        kesher: Kesher = Kesher(
            name=kesher_dto.name,
            created_date=now - 1000,  # Note 'created_date' should be read from the database
            updated_date=now)
        return build_response(HTTPStatus.OK, kesher.json())
    except (ValidationError, TypeError) as err:
        return build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return build_error_response(err)


# GET /kesher/{name}
@logger.inject_lambda_context(log_event=True)
def get_kesher(event: dict, context: LambdaContext) -> dict:
    if "pathParameters" not in event or "name" not in event["pathParameters"]:
        return build_response(HTTPStatus.BAD_REQUEST, "")

    try:
        name: str = event["pathParameters"]["name"]
        #  Note: dates should be read from the database
        now: Decimal = Decimal(datetime.now().timestamp())
        item: Kesher = Kesher(name=name, created_date=now, updated_date=now)
        if item is None:
            return build_response(HTTPStatus.NOT_FOUND, body="{ 'message': 'item was not found' }")
        body = item.json()
        return build_response(HTTPStatus.OK, body)
    except (ValidationError, TypeError) as err:
        return build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return build_error_response(err)


