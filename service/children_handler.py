from datetime import datetime
from decimal import Decimal
import json
from http import HTTPStatus
from service.models.daily_report import DailyReport, DailyReportAddDto, DailyReportGetDto
from service.response_utils import build_error_response, build_response
from aws_lambda_powertools.logging import logger
from aws_lambda_context import LambdaContext
from pydantic import ValidationError
from aws_lambda_powertools import Logger
from service.models.child import Child, Attendance
from service.access_layer.utils.db_query_utils import execute_query

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
        daily_report = DailyReportAddDto.parse_raw(event["body"])
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
        daily_reports_dtos = []
        
        query_results = execute_query(f"CALL get_daily_reports_per_child_id ('{child_id}');")
        for report in query_results:
            daily_report = DailyReport(*report)
            daily_report_dto = DailyReportGetDto(child_id=child_id, value = daily_report.report_value, 
                    category_id=daily_report.category_id, subcategory_id = daily_report.subcategory_id, 
                    sender_id=daily_report.sender_id, timestamp = daily_report.report_date.strftime("%m/%d/%Y, %H:%M:%S"))
            daily_reports_dtos.append(daily_report_dto.dict())

        if daily_reports_dtos is None:
            return build_response(HTTPStatus.NOT_FOUND, body="")
        body = json.dumps({'daily_reports': daily_reports_dtos})
        return build_response(HTTPStatus.OK, body)
    except (ValidationError, TypeError) as err:
        return build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return build_error_response(err)


# PUT /api/children/{child_id}/attendance
@logger.inject_lambda_context(log_event=True)
def update_child_attendance(event: dict, context: LambdaContext) -> dict:
    logger.info(f"in update_child_attendance, event: {event}")

    if "pathParameters" not in event or "child_id" not in event["pathParameters"]:
        return build_response(HTTPStatus.BAD_REQUEST, event)

    try:
        child_id: str = event["pathParameters"]["child_id"]
        now: Decimal = Decimal(datetime.now().timestamp())
        body = event["body"]
        logger.debug(f"input body: {body}")

        attendance = Attendance.parse_raw(event["body"])

        if attendance.attended and attendance.attended.upper() == "TRUE":
            logger.info(f"Setting attendance for chile_id: {child_id} at time: {now}")
            return build_response(HTTPStatus.OK, json.dumps("attendance updated"))

        # if for a reason the attended is false, there is notning to update. just return 200 OK
        return build_response(HTTPStatus.OK, json.dumps("attendance not updated, FALSE is not currently supported"))
    except (ValidationError, TypeError) as err:
        logger.exception("Failed to update child attendance, retuning bad request", err)
        return build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        logger.exception("Failed to update child attendance, returning error", err)
        return build_error_response(err)
