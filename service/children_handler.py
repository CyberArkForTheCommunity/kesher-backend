from datetime import datetime
from decimal import Decimal
import json
from http import HTTPStatus
from service.models.daily_report import DailyReportAdd, DailyReportGet

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
        body = json.dumps({'children': children})
        return build_response(HTTPStatus.OK, body)
    except (ValidationError, TypeError) as err:
        return build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return build_error_response(err)


# POST /api/children/{child_id}/daily-reports
@logger.inject_lambda_context(log_event=True)
def add_child_report(event: dict, context: LambdaContext) -> dict:
    if "pathParameters" not in event or "child_id" not in event["pathParameters"]:
        return build_response(HTTPStatus.BAD_REQUEST, "")

    try:
        child_id: str = event["pathParameters"]["child_id"]
        daily_report = DailyReportAdd.parse_raw(event["body"])
        # TODO get from DB
        return build_response(http_status=HTTPStatus.CREATED, body=daily_report.json())
    except (ValidationError, TypeError) as err:
        return build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return build_error_response(err)
   
# GET /api/children/{child_id}/daily-reports
@logger.inject_lambda_context(log_event=True)
def get_child_reports(event: dict, context: LambdaContext) -> dict:
    if "pathParameters" not in event or "child_id" not in event["pathParameters"]:
        return build_response(HTTPStatus.BAD_REQUEST, event)

    try:
        child_id: str = event["pathParameters"]["child_id"]
        now: Decimal = Decimal(datetime.now().timestamp())
        daily_reports = [
            DailyReportGet(child_id=child_id, value="Itamar ate lunch", category_id=1234, subcategory_id=4635, sender_id=23432, timestamp=now).dict(),
            DailyReportGet(child_id=child_id, value="Itamar ate dinner", category_id=1234, subcategory_id=235235, sender_id=23432, timestamp=now).dict()
        ]
        if daily_reports is None:
            return build_response(HTTPStatus.NOT_FOUND, body="")
        body = json.dumps({'daily_reports': daily_reports})
        return build_response(HTTPStatus.OK, body)
    except (ValidationError, TypeError) as err:
        return build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return build_error_response(err)

