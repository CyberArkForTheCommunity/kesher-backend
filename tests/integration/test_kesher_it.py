# pylint: disable = print-used
import json
import requests
import os
from datetime import datetime
from http import HTTPStatus
import pytest
from dotenv import load_dotenv

from service.report_category_handler import SubCategory, Category
from tests.helpers.environment_handler import load_env_vars
from tests.helpers.random_utils import random_string
from tests.helpers.cognito_auth_util import add_auth_header

# from cdk.kesher_service_cdk.service_stack.kesher_construct import get_stack_name
# from kesher_service_cdk.service_stack.constants import BASE_NAME
from service.dtos.kesher_dto import KesherDto


@pytest.fixture(scope="module")
def endpoint_url():
    load_dotenv()
    load_env_vars()
    endpoint_url = os.environ['KESHER_API_GW']
    return endpoint_url[:-1]


@pytest.fixture(scope="module")
def auth_headers():
    return add_auth_header()


def test_get_categories_list__success(endpoint_url, auth_headers):
    headers = {"Content-Type": "application/json"}
    headers.update(auth_headers)
    response = requests.api.get(url=f"{endpoint_url}/categories", headers=headers)
    print(f"response: {response}")
    print(f"response: {response.content}")
    assert response.status_code == HTTPStatus.OK
    assert response.content is not None


#TODO: remove
# def test_create_kesher(endpoint_url, auth_headers):
#     # when create entity
#     kesher_dto: KesherDto = KesherDto(name=random_string())
#     headers = {"Content-Type": "application/json"}
#     headers.update(auth_headers)
#     response = requests.api.post(url=f"{endpoint_url}/kesher", headers=headers, json=kesher_dto.dict())
#
#     # then assert created
#     assert response.status_code == HTTPStatus.CREATED
#     # assert created_date & updated_date was initialize
#     resource = json.loads(response.content)
#     assert resource['name'] == kesher_dto.name
#     day_seconds = 24 * 60 * 60
#     now = datetime.now().timestamp()
#     assert now - day_seconds < resource['created_date'] < now + day_seconds
#     assert resource['created_date'] == resource['updated_date']
#
#     # when get the created entity
#     response = requests.api.get(url=f"{endpoint_url}/kesher/{kesher_dto.name}", headers=auth_headers)
#
#     # then assert all fields saved successfully
#     assert response.status_code == HTTPStatus.OK
#     resource = json.loads(response.content)
#     assert resource['name'] == kesher_dto.name
#     assert now - day_seconds < resource['created_date'] < now + day_seconds
#     assert resource['created_date'] == resource['updated_date']
#
#
# def test_get_kesher(endpoint_url, auth_headers):
#     # read by name
#     response = requests.api.get(url=f"{endpoint_url}/kesher/Alex", headers=auth_headers)
#     assert response.status_code == HTTPStatus.OK
#     resource = json.loads(response.content)
#     assert resource['name'] == "Alex"
#     day_seconds = 24 * 60 * 60
#     now = datetime.now().timestamp()
#     assert now - day_seconds < resource['created_date'] < now + day_seconds
#     assert resource['created_date'] == resource['updated_date']
#
#
# def test_update_kesher(endpoint_url, auth_headers):
#     # when create entity
#     kesher_dto: KesherDto = KesherDto(name=random_string())
#     headers = {"Content-Type": "application/json"}
#     headers.update(auth_headers)
#     requests.api.post(url=f"{endpoint_url}/kesher", headers=headers, json=kesher_dto.dict())
#
#     # then update the entity
#     response = requests.api.put(url=f"{endpoint_url}/kesher/{kesher_dto.name}", headers=headers,
#                                 json=kesher_dto.dict())
#
#     # then assert
#     assert response.status_code == HTTPStatus.OK
#     resource = json.loads(response.content)
#     day_seconds = 24 * 60 * 60
#     now = datetime.now().timestamp()
#     assert now - day_seconds < resource['created_date'] < now + day_seconds
#     assert now - day_seconds < resource['updated_date'] < now + day_seconds
#     assert resource['created_date'] < resource['updated_date']
