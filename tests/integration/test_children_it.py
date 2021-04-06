import pytest
import json
import os
from http import HTTPStatus
import requests

from service.models.child import Attendance
from tests.helpers.environment_handler import load_env_vars
from dotenv.main import load_dotenv
from tests.helpers.cognito_auth_util import add_auth_header
from service.models.daily_report import DailyReportAddDto


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
    response = requests.api.get(url=f"{endpoint_url}/api/children", headers=auth_headers)
    assert response.status_code == HTTPStatus.OK
    resource = json.loads(response.content)
    assert resource is not None


def test_add_daily_report(endpoint_url, auth_headers):
    # when create entity
    headers = {"Content-Type": "application/json"}
    headers.update(auth_headers)
    daily_report = DailyReportAddDto(child_id='23432', value="Itamar ate lunch", category_id=1234, subcategory_id=4635)

    response = requests.api.post(url=f"{endpoint_url}/api/children/12345/daily-reports", headers=headers,
                                 json=daily_report.dict())

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


def test_update_child_attendance_with_true_success(endpoint_url, auth_headers):
    attendance = Attendance(attended="true")
    child_id = 123132
    response = requests.api.put(url=f"{endpoint_url}/api/children/{child_id}/attendance",
                                headers=auth_headers,
                                json=attendance.dict())

    assert response.status_code == HTTPStatus.OK
    content = json.loads(response.content)
    assert content == "attendance updated"


def test_update_child_attendance_with_false_success(endpoint_url, auth_headers):
    attendance = Attendance(attended="false")
    child_id = 123132
    response = requests.api.put(url=f"{endpoint_url}/api/children/{child_id}/attendance",
                                headers=auth_headers,
                                json=attendance.dict())

    assert response.status_code == HTTPStatus.OK
    content = json.loads(response.content)
    assert content == "attendance not updated, FALSE is not currently supported"


def test_update_child_attendance_with_missing_params__failed(endpoint_url, auth_headers):
    child_id = 123132
    response = requests.api.put(url=f"{endpoint_url}/api/children/{child_id}/attendance",
                                headers=auth_headers,
                                json={})

    assert response.status_code == HTTPStatus.BAD_REQUEST
    content = str(response.content)
    assert "error for Attendance" in content
    assert "type=value_error.missing" in content
