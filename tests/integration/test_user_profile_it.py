import pytest
import json
import os
from http import HTTPStatus
import requests
from tests.helpers.environment_handler import load_env_vars
from dotenv.main import load_dotenv
from tests.helpers.cognito_auth_util import add_auth_header


@pytest.fixture(scope="module")
def endpoint_url():
    load_dotenv()
    load_env_vars()
    endpoint_url = os.environ['KESHER_API_GW']
    return endpoint_url[:-1]


@pytest.fixture(scope="module")
def auth_headers():
    return add_auth_header()

def test_get_user_profile(endpoint_url, auth_headers):
    response = requests.api.get(url=f"{endpoint_url}/api/user-profile", headers=auth_headers)
    assert response.status_code == HTTPStatus.OK
    body = json.loads(response.content)
    assert body is not None
    user_profile = json.loads(body)
    assert user_profile['role_type']
