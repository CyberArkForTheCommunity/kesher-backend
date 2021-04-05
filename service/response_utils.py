
from http import HTTPStatus
from logging import Logger



def build_response(http_status: HTTPStatus, body: str) -> dict:
    return {'statusCode': http_status, 'headers': {'Content-Type': 'application/json'}, 'body': body}


def build_error_response(err, status: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR) -> dict:
    return {
        'statusCode': status,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': str(err),
    }
