from http import HTTPStatus

import os

from aws_lambda_powertools.logging import logger
from aws_lambda_context import LambdaContext
from pydantic import ValidationError
from aws_lambda_powertools import Logger

from kesher_service_cdk.service_stack.email_services.email_services import EMAIL_BUCKET_ENV_VAR


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
        bucket_name = get_env_var(EMAIL_BUCKET_ENV_VAR)
        # TODO - read email context, extract presigned URL - merge code from Alex
        # presigned_url = 
        
        # TODO - input validation on data
        
        # TODO - make sure that data is inserted into the DB in a secure way to avoid SQL injection


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

def get_env_var(name: str) -> str:
    env_var = os.getenv(name)
    if env_var is None:
        error_message = f'{name} Enviroment Variable is missing for this lambda'
        logger.error(error_message)
        raise Exception(error_message)
    return env_var