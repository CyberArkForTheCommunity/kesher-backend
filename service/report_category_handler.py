import json
from http import HTTPStatus
from typing import List

from aws_lambda_context import LambdaContext
from aws_lambda_powertools import Logger
from pydantic import ValidationError, BaseModel

from service.response_utils import build_error_response, build_response

logger = Logger()


class SubCategory (BaseModel):
    subcategory_id: int
    subcategory_name: str


class Category(BaseModel):
    category_id: int
    category_name: str
    sub_categories: List = None



    # GET /kesher/ReportCategories
@logger.inject_lambda_context(log_event=True)
def get_report_categories_list(event: dict, context: LambdaContext) -> dict:
    print(" in get_report_categories_list, returning stab")
    print(f"event: {event}, context: {context}")

    try:
        # kesher_dto: KesherDto = KesherDto.parse_raw(event["body"])
        # now: Decimal = Decimal(datetime.now().timestamp())
        # kesher: Kesher = Kesher(name=kesher_dto.name, created_date=now, updated_date=now)

        logger.info(" in get_report_categories_list")

       # sub_categories = []
       # report_categories = []
       # sub_categories.append(SubCategory(subcategory_id=34, subcategory_name="mock_sub_category"))
       # report_categories.append(Category(category_id=123, category_name="mock_cat_name", sub_categories=sub_categories))

        mock_json = {
            "categories": {
                "category_id": 12,
                "category_name": "mock_cat_name",
                "sub_categories": {
                    "subcategory_id": 23,
                    "subcategory_name": "mock_sub_cat"
                }
            }
        }

        mock_json_str = json.dumps(mock_json)
        print(f"returning {mock_json_str}")

        return build_response(http_status=HTTPStatus.CREATED, body=mock_json_str)
    except (ValidationError, TypeError) as err:
        return build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return build_error_response(err)
