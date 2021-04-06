import pytest
import json
import os
from http import HTTPStatus
import requests
from tests.helpers.environment_handler import load_env_vars
from dotenv.main import load_dotenv
from tests.helpers.cognito_auth_util import add_auth_header
from service.models.daily_report import DailyReportAdd


@pytest.fixture(scope="module")
def endpoint_url():
    load_dotenv()
    load_env_vars()
    endpoint_url = os.environ['KESHER_API_GW']
    return endpoint_url[:-1]


@pytest.fixture(scope="module")
def auth_headers():
    return add_auth_header()

def test_get_children(endpoint_url, auth_headers):
    # read by name
    response = requests.api.get(url=f"{endpoint_url}/api/children", headers=auth_headers)
    assert response.status_code == HTTPStatus.OK
    resource = json.loads(response.content)
    assert resource is not None

def test_add_daily_report(endpoint_url, auth_headers):
    # when create entity
    headers = {"Content-Type": "application/json"}
    headers.update(auth_headers)
    daily_report = DailyReportAdd(child_id='23432', value="Itamar ate lunch", category_id=1234, subcategory_id=4635)

    response = requests.api.post(url=f"{endpoint_url}/api/children/12345/daily-reports", headers=headers, json=daily_report.dict())

    # then assert created
    assert response.status_code == HTTPStatus.CREATED
    # assert created_date & updated_date was initialize
    resource = json.loads(response.content)
    assert resource['value'] == daily_report.value

def test_get_child_daily_reports(endpoint_url, auth_headers):
    response = requests.api.get(url=f"{endpoint_url}/api/children/12345/daily-reports", headers=auth_headers)
    assert response.status_code == HTTPStatus.OK
    resource = json.loads(response.content)
    assert len(resource['daily_reports']) > 0
