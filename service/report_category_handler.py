import json
from http import HTTPStatus
from typing import Dict, List
from service.models.report_categories import CategoryDto, SubCategory, SubCategoryDto
from service.access_layer.utils.db_query_utils import execute_query
from aws_lambda_context import LambdaContext
from aws_lambda_powertools import Logger
from pydantic import ValidationError
from service.response_utils import build_error_response, build_response

logger = Logger()


# GET /api/categories
@logger.inject_lambda_context(log_event=True)
def get_report_categories_list(event: dict, context: LambdaContext) -> dict:
    print(" in get_report_categories_list, returning stab")
    print(f"event: {event}, context: {context}")

    try:
        logger.debug("in get_report_categories_list")
        query_results = execute_query(f"CALL get_categories_and_subcategories();")
        sub_categories = []
        for record in query_results:
            sub_categories.append(SubCategory(*record))
        
        category_dtos = _sub_categories_models_to_dtos(sub_categories)
        body = json.dumps({'categories': category_dtos})
        return build_response(http_status=HTTPStatus.OK, body=body)
    except (ValidationError, TypeError) as err:
        return build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return build_error_response(err)

def _sub_categories_models_to_dtos(models: List[SubCategory]):
    categories_dict: Dict = dict()
    for model in models:
        if model.category_id not in categories_dict:
            category_dto = CategoryDto(category_id=model.category_id, category_name=model.category_name)
            categories_dict[model.category_id] = category_dto
        sub_category_dto = SubCategoryDto(subcategory_id=model.sub_category_id, subcategory_name=model.subcategory_name)
        category_dto.sub_categories.append(sub_category_dto.dict())

    return list(map(lambda x: x.dict(), categories_dict.values()))
