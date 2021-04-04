from datetime import datetime
from decimal import Decimal
from http import HTTPStatus

import json

from aws_lambda_powertools.logging import logger
from aws_lambda_context import LambdaContext
from pydantic import ValidationError
from aws_lambda_powertools import Logger

from service.dtos.kesher_dto import KesherDto
from service.models.kesher import Kesher

logger = Logger()


# POST /kesher
@logger.inject_lambda_context(log_event=True)
def create_kesher(event: dict, context: LambdaContext) -> dict:
    try:
        kesher_dto: KesherDto = KesherDto.parse_raw(event["body"])
        now: Decimal = Decimal(datetime.now().timestamp())
        kesher: Kesher = Kesher(name=kesher_dto.name, created_date=now, updated_date=now)
        return _build_response(http_status=HTTPStatus.CREATED, body=kesher.json())
    except (ValidationError, TypeError) as err:
        return _build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return _build_error_response(err)


# PUT /kesher/{name}
@logger.inject_lambda_context(log_event=True)
def update_kesher(event: dict, context: LambdaContext) -> dict:
    if "pathParameters" not in event or "name" not in event["pathParameters"]:
        return _build_response(HTTPStatus.BAD_REQUEST, "")

    try:
        # pylint: disable=unused-variable
        name: str = event["pathParameters"]["name"]
        kesher_dto: KesherDto = KesherDto.parse_raw(event["body"])
        now: Decimal = Decimal(datetime.now().timestamp())
        kesher: Kesher = Kesher(
            name=kesher_dto.name,
            created_date=now - 1000,  # Note 'created_date' should be read from the database
            updated_date=now)
        return _build_response(HTTPStatus.OK, kesher.json())
    except (ValidationError, TypeError) as err:
        return _build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return _build_error_response(err)


# GET /kesher/{name}
@logger.inject_lambda_context(log_event=True)
def get_kesher(event: dict, context: LambdaContext) -> dict:
    if "pathParameters" not in event or "name" not in event["pathParameters"]:
        return _build_response(HTTPStatus.BAD_REQUEST, "")

    try:
        name: str = event["pathParameters"]["name"]
        #  Note: dates should be read from the database
        now: Decimal = Decimal(datetime.now().timestamp())
        item: Kesher = Kesher(name=name, created_date=now, updated_date=now)
        if item is None:
            return _build_response(HTTPStatus.NOT_FOUND, body="{ 'message': 'item was not found' }")
        body = item.json()
        return _build_response(HTTPStatus.OK, body)
    except (ValidationError, TypeError) as err:
        return _build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return _build_error_response(err)


def _build_response(http_status: HTTPStatus, body: str) -> dict:
    return {'statusCode': http_status, 'headers': {'Content-Type': 'application/json'}, 'body': body}


def _build_error_response(err, status: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR) -> dict:
    logger.error(str(err))
    return {
        'statusCode': status,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': str(err),
    }
