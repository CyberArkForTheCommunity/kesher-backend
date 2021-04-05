from http import HTTPStatus

import json

from aws_lambda_powertools.logging import logger
from aws_lambda_context import LambdaContext
from pydantic import ValidationError
from aws_lambda_powertools import Logger

logger = Logger()

@logger.inject_lambda_context(log_event=True)
def admin_submit(event: dict, context: LambdaContext) -> dict:
    try:
        pass
        # kesher_dto: KesherDto = KesherDto.parse_raw(event["body"])
        # now: Decimal = Decimal(datetime.now().timestamp())
        # kesher: Kesher = Kesher(name=kesher_dto.name, created_date=now, updated_date=now)
        # return _build_response(http_status=HTTPStatus.CREATED, body=kesher.json())
    except (ValidationError, TypeError) as err:
        return _build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return _build_error_response(err)


@logger.inject_lambda_context(log_event=True)
def teacher_submit(event: dict, context: LambdaContext) -> dict:
    try:
        pass
        # kesher_dto: KesherDto = KesherDto.parse_raw(event["body"])
        # now: Decimal = Decimal(datetime.now().timestamp())
        # kesher: Kesher = Kesher(name=kesher_dto.name, created_date=now, updated_date=now)
        # return _build_response(http_status=HTTPStatus.CREATED, body=kesher.json())
    except (ValidationError, TypeError) as err:
        return _build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return _build_error_response(err)


def _build_response(http_status: HTTPStatus, body: str) -> dict:
    return {'statusCode': http_status, 'headers': {'Content-Type': 'application/json'}, 'body': body}


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
