from http import HTTPStatus
from aws_lambda_context import LambdaContext
from pydantic import ValidationError
from logging import Logger
from service.response_utils import build_error_response, build_response


# GET /kesher/{name}
@Logger.inject_lambda_context(log_event=True)
def get_children(event: dict, context: LambdaContext) -> dict:
    # if "pathParameters" not in event or "name" not in event["pathParameters"]:
    #     return build_response(HTTPStatus.BAD_REQUEST, "")

    try:
        # name: str = event["pathParameters"]["name"]
        # #  Note: dates should be read from the database
        # now: Decimal = Decimal(datetime.now().timestamp())
        # item: Kesher = Kesher(name=name, created_date=now, updated_date=now)
        # if item is None:
        #     return _build_response(HTTPStatus.NOT_FOUND, body="{ 'message': 'item was not found' }")
        # body = item.json()
        return build_response(HTTPStatus.OK, "")
    except (ValidationError, TypeError) as err:
        return build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return build_error_response(err)
