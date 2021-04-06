# pylint: disable = print-used
import requests
import os
from http import HTTPStatus
import pytest
from dotenv import load_dotenv

from tests.helpers.environment_handler import load_env_vars
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


def test_get_categories_list__success(endpoint_url, auth_headers):
    headers = {"Content-Type": "application/json"}
    headers.update(auth_headers)
    response = requests.api.get(url=f"{endpoint_url}/api/categories", headers=headers)
    print(f"response: {response}")
    print(f"response: {response.content}")
    assert response.status_code == HTTPStatus.OK
    assert response.content is not None
