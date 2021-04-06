import json
from http import HTTPStatus
from service.models.user_profile import UserProfile
from aws_lambda_powertools.logging import logger
from aws_lambda_context import LambdaContext
from pydantic import ValidationError
from aws_lambda_powertools import Logger
from service.response_utils import build_error_response, build_response

logger = Logger()

# GET /api/user-profile
@logger.inject_lambda_context(log_event=True)
def get_user_profile(event: dict, context: LambdaContext) -> dict:
    try:
        user_profile = UserProfile(role_type=3)
        body = json.dumps(user_profile.json())
        return build_response(HTTPStatus.OK, body)
    except (ValidationError, TypeError) as err:
        return build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return build_error_response(err)
