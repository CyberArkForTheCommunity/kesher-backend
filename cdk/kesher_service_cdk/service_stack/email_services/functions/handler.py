from http import HTTPStatus
import os
import requests

from aws_lambda_context import LambdaContext
from aws_lambda_powertools.logging import logger
from aws_lambda_powertools import Logger
import boto3
from botocore.exceptions import ClientError
from pydantic import ValidationError

from kesher_service_cdk.service_stack.email_services.email_services import EMAIL_BUCKET_ENV_VAR


logger = Logger()

@logger.inject_lambda_context(log_event=True)
def admin_submit(event: dict, context: LambdaContext) -> dict:
    try:
        pass
        # kesher_dto: KesherDto = KesherDto.parse_raw(event["body"])
        # now: Decimal = Decimal(datetime.now().timestamp())
        # kesher: Kesher = Kesher(name=kesher_dto.name, created_date=now, updated_date=now)
        # return _build_response(http_status=HTTPStatus.CREATED, body=kesher.json())
    except (ValidationError, TypeError) as err:
        return _build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return _build_error_response(err)


@logger.inject_lambda_context(log_event=True)
def teacher_submit(event: dict, context: LambdaContext) -> dict:
    try:
        bucket_name = get_env_var(EMAIL_BUCKET_ENV_VAR)
        # TODO - read email conteמt, extract presigned URL, maybe retry once with a short wait - merge code from Alex

        # Hard code presigned url until url read is implemented 
        # You can generate a presigned URL for upload by calling create_presigned_post below

        # For example:

        #response = create_presigned_post(bucket_name="keshercsvupload-serviceemailkeshercsvuploademails-jbl8wdljx0tt", 
        #                                 object_name="/TeacherSubmissions/email@gmail.com-submission.csv")

        presigned_url = "https://s3.us-east-1.amazonaws.com/keshercsvupload-serviceemailkeshercsvuploademails-jbl8wdljx0tt%0A/TeacherSubmissions/email%40gmail.com-submission.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAR37OWCTPEKLJW67W%2F20210406%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20210406T102402Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Security-Token=FwoGZXIvYXdzENT%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaDPMiRKtTT75jAS1X0CLnATw3oM0E%2BQhUhiaNdtGd1cDrHWqQQaTgJnbMrcWoUIpKx0e9E%2FJw2BQyUHPNlTt8EUUkg9RWsmqI5UpdcRuUROaVnFvIxbNnYRJL%2F8wtEb3slj1RoXQvyWn3mkJ6yOyIcYZjzXHjy%2BoptTZDp%2BypKuD%2FcirkrkDZqf%2BNhiGm%2FBnkwAiDj8VEdvqf7tfyoSnteSZ%2BNECNQ9AVZuK2784tFxGVynLYt5D6aLZXRG6JBve4EycSkU0znDtNDx%2B7NhURAFE1qMu4rKPBbjjCdyLWCJJ1%2BINrizP4KSl1rHYtYM4ckIy7R2XG0Si0qK2DBjIrMFKsXc7ll3a24x6tKC9SoOQ%2FW5yrxrQhSNcs00uhfhVA895I6GI8wr4ydw%3D%3D&X-Amz-Signature=116dd8c692c953eff7e254e45705d3fcf702e09ad59111d1e90f56d3a98a732e"
                
        # TODO - upload to S3 - bucket name, build obj name from sender 
        #      - this validates expiration and the tenant identity (we emailed this teached with the link to this specific object in our bucket)

        # TODO - handle errors - expiration, invalid link etc. 

        # TODO - input validation on data - on error email back with the message id (this can be used for troubleshooting)

        # TODO - read records from file, push to DB
        # make sure that data is inserted into the DB in a secure way to avoid SQL injection

        # Respond to sender with result (do we respond to sender on any error? don't divulge informative errors to rogue senders)


    except (ValidationError, TypeError) as err:
        return _build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return _build_error_response(err)


def _build_response(http_status: HTTPStatus, body: str) -> dict:
    return {'statusCode': http_status, 'headers': {'Content-Type': 'application/json'}, 'body': body}


def _build_error_response(err, status: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR) -> dict:
    logger.error(str(err))
    return {
        'statusCode': status,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': str(err),
    }

def get_env_var(name: str) -> str:
    env_var = os.getenv(name)
    if env_var is None:
        error_message = f'{name} Enviroment Variable is missing for this lambda'
        logger.error(error_message)
        raise Exception(error_message)
    return env_var


def create_presigned_post(bucket_name, object_name, fields=None, conditions=None, expiration=3600):
    """Generate a presigned URL S3 POST request to upload a file

    :param bucket_name: string
    :param object_name: string
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_post(bucket_name,
                                                     object_name,
                                                     Fields=fields,
                                                     Conditions=conditions,
                                                     ExpiresIn=expiration)
    except ClientError as e:
        logger.error(e)
        return None

    # The response contains the presigned URL and required fields
    return response


def upload_s3_object_presigned(source_file: str, object_name: str, bucket_name: str) -> str:
    response = create_presigned_post(bucket_name, object_name)
    if response is None:
        raise Exception("Error generating presigned url for {object_name=}, {bucket_name=}")

    with open(source_file, 'rb') as f:
        files = {'file': (object_name, f)}
        http_response = requests.post(response['url'], data=response['fields'], files=files)
    
    # If successful, returns HTTP status code 204
    logger.info(f'File upload HTTP status code: {http_response.status_code}')
    if http_response.status_code > 300:
        logger.error(f"Error uploading object with presigned url {http_response.content=}")
        raise Exception(f"Error uploading {object_name=} to {bucket_name=}")
