import os
import json
import requests


def login():
    username = os.environ['USER_NAME']
    password = os.environ['DEFAULT_USER_PASSWORD']
    client_id = os.getenv('AUTH_CLIENT_ID', None)
    cognito_url = os.getenv('COGNITO_URL', None)

    """Login to Cognito and return the ID token to be used as the bearer in subsequent REST calls"""
    response = requests.api.post(
        cognito_url, json={
            "AuthFlow": "USER_PASSWORD_AUTH",
            "ClientId": client_id,
            "AuthParameters": {
                "USERNAME": username,
                "PASSWORD": password
            }
        }, headers={
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth'
        })
    assert response.status_code == 200
    resp_content = json.loads(response.content.decode('utf-8'))
    return resp_content["AuthenticationResult"]["IdToken"]


def add_auth_header(headers=None):
    if headers is None:
        headers = {}
    id_token = login()
    headers["Authorization"] = f"Bearer {id_token}"
    return headers
