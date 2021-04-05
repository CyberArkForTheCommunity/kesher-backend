import json
from http import HTTPStatus

from service.response_utils import build_error_response, build_response

from aws_lambda_powertools.logging import logger
from aws_lambda_context import LambdaContext
from pydantic import ValidationError
from aws_lambda_powertools import Logger
from service.models.child import Child

logger = Logger()

# GET /api/children
@logger.inject_lambda_context(log_event=True)
def get_children(event: dict, context: LambdaContext) -> dict:
    try:
        children = [
            Child(id='12345', first_name='Yeled', last_name='One').dict(),
            Child(id='436346', first_name='Kid', last_name='Two').dict()
        ]
        body = json.dumps({'Children': children})
        return build_response(HTTPStatus.OK, body)
    except (ValidationError, TypeError) as err:
        return build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return build_error_response(err)

