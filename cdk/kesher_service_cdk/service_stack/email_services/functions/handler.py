from http import HTTPStatus
import os
from typing import Dict, Tuple
import requests


from aws_lambda_context import LambdaContext
from aws_lambda_powertools.logging import logger
from aws_lambda_powertools import Logger
import boto3
from botocore.exceptions import ClientError
from pydantic import ValidationError

from kesher_service_cdk.service_stack.email_services.email_services import EMAIL_BUCKET_ENV_VAR

from email.parser import BytesParser
from email import policy
from email.message import Message, EmailMessage
from pandas import read_csv, DataFrame, Series
from io import BytesIO


logger = Logger()

@logger.inject_lambda_context(log_event=True)
def admin_submit(event: dict, context: LambdaContext) -> dict:
    try:
        pass
        # TODO read email content
        # TODO upload_s3_object_presigned - this is how we verify the sender
        # TODO read csv content, verify data
        # TODO Populate database
        # TODO Email teachers - if not verified, send verify email, otherwise normal email
        # TODO - must handle all errors - presigned url errors (expiration, bad url), other errirs
        # TODO - email the user with the result - success, error (with details and instructions)
    except (ValidationError, TypeError) as err:
        return _build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return _build_error_response(err)


@logger.inject_lambda_context(log_event=True)
def teacher_submit(event: dict, context: LambdaContext) -> dict:
    try:
        bucket_name = get_env_var(EMAIL_BUCKET_ENV_VAR)
        sender, presigned_url, attachment_bytes = read_email_content(event=event, bucket_name=bucket_name)
        
        local_file_name = f'{sender}.kindergarten_ids.csv'
        with open(local_file_name, "wb") as file:
            file.write(attachment_bytes)

        upload_s3_object_presigned(source_file=local_file_name, object_name=local_file_name, bucket_name=bucket_name)
        # by upload using the presigned url, we are in practive validating the expiration and the 
        # tenant identity (we emailed this teached with the link to this specific object in our bucket)
        # If this succeeds using a signed URL, this means that we provided a signed url for this bucket and this file name with the email 
        # Address prefix. this is the user authorization for this (temporary) flow

        # TODO - handle errors - expiration, invalid link etc. 

        # TODO - input validation on data - on error email back with the message id (this can be used for troubleshooting)

        # TODO - read records from file, push to DB
        # make sure that data is inserted into the DB in a secure way to avoid SQL injection

        # Respond to sender with result (do we respond to sender on any error? don't divulge informative errors to rogue senders)


    except (ValidationError, TypeError) as err:
        return _build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return _build_error_response(err)


def read_email_content(event: dict, bucket_name: str) -> Tuple[str, Dict, bytes]:
    # TODO - implement this
    # TODO - read email conteמt
    #   - extract presigned URL, maybe retry once with a short wait - merge code from Alex
    #   - extract attachment bytes

    # Hard code presigned url until url read is implemented 
    # You can generate a presigned URL for upload by calling create_presigned_post below

    # For example:

    #response = create_presigned_post(bucket_name="keshercsvupload-serviceemailkeshercsvuploademails-jbl8wdljx0tt", 
    #                                 object_name="/TeacherSubmissions/email@gmail.com-submission.csv")

    # sender = "email@gmail.com" # TODO: Extract sender from event
    #
    # # TODO: Buid this from the email context
    presgined_url_dict = {
        'url': 'https://keshercsvupload-serviceemailkeshercsvuploademails-jbl8wdljx0tt.s3.amazonaws.com/',
        'fields': {
            'AWSAccessKeyId': '<Populate>',
            'key': '/TeacherSubmissions/email@gmail.com-submission.csv',
            'policy': '<populate>',
            'signature': '<populate>',
            'x-amz-security-token': '<populate>'
        }
    }
    #
    # attachment_bytes = b'\xef\xbb\xbf\xd7\x9e\xd7\x96\xd7\x94\xd7\x94 \xd7\x92\xd7\x9f,\xd7\x9e\xd7\xa1\xd7\xa4\xd7\xa8 \xd7\x96\xd7\x94\xd7\x95\xd7\xaa \xd7\x99\xd7\x9c\xd7\x93/\xd7\x94,\xd7\xa9\xd7\x9d \xd7\xa4\xd7\xa8\xd7\x98\xd7\x99 \xd7\x99\xd7\x9c\xd7\x93/\xd7\x94,\xd7\xa9\xd7\x9d \xd7\x9e\xd7\xa9\xd7\xa4\xd7\x97\xd7\x94 \xd7\x99\xd7\x9c\xd7\x93/\xd7\x94,\xd7\xaa\xd7\x90\xd7\xa8\xd7\x99\xd7\x9a \xd7\x9c\xd7\x99\xd7\x93\xd7\x94 \xd7\x99\xd7\x9c\xd7\x93/\xd7\x94,\xd7\x94\xd7\x95\xd7\xa8\xd7\x94 1 \xd7\x9e\xd7\xa1\xd7\xa4\xd7\xa8 \xd7\x96\xd7\x94\xd7\x95\xd7\xaa,\xd7\x94\xd7\x95\xd7\xa8\xd7\x94 1 \xd7\xa9\xd7\x9d \xd7\xa4\xd7\xa8\xd7\x98\xd7\x99,\xd7\x94\xd7\x95\xd7\xa8\xd7\x94 1 \xd7\xa9\xd7\x9d \xd7\x9e\xd7\xa9\xd7\xa4\xd7\x97\xd7\x94,\xd7\x94\xd7\x95\xd7\xa8\xd7\x94 1 \xd7\x90\xd7\x99\xd7\x9e\xd7\x99\xd7\x99\xd7\x9c,\xd7\x94\xd7\x95\xd7\xa8\xd7\x94 2 \xd7\x9e\xd7\xa1\xd7\xa4\xd7\xa8 \xd7\x96\xd7\x94\xd7\x95\xd7\xaa,\xd7\x94\xd7\x95\xd7\xa8\xd7\x94 2 \xd7\xa9\xd7\x9d \xd7\xa4\xd7\xa8\xd7\x98\xd7\x99,\xd7\x94\xd7\x95\xd7\xa8\xd7\x94 2 \xd7\xa9\xd7\x9d \xd7\x9e\xd7\xa9\xd7\xa4\xd7\x97\xd7\x94,\xd7\x94\xd7\x95\xd7\xa8\xd7\x94 2 \xd7\x90\xd7\x99\xd7\x9e\xd7\x99\xd7\x99\xd7\x9c,\xd7\x94\xd7\x90\xd7\x9d \xd7\x9c\xd7\x9e\xd7\x97\xd7\x95\xd7\xa7? (\xd7\x9c\xd7\x9e\xd7\x97\xd7\x99\xd7\xa7\xd7\xaa \xd7\xa8\xd7\xa9\xd7\x95\xd7\x9e\xd7\x94 \xd7\x96\xd7\x95 \xd7\xa1\xd7\x9e\xd7\x9f V)\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,'
    # return sender, presgined_url_dict, attachment_bytes
    ses_mail = event['Records'][0]['ses']['mail']
    message_id = ses_mail['messageId']
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    raw_email = bucket.Object('TeacherIncomingEmail/' + message_id).get()['Body'].read()
    msg: EmailMessage = BytesParser(policy=policy.SMTP).parsebytes(raw_email)
    sender = None
    attachment_bytes = None
    presgined_url_dict = None
    for header in msg._headers:
        if header[0] == 'Return-Path':
            sender = header[1][1:-1]
    for attachment in msg.iter_attachments():
        filename: str = attachment.get_filename()
        if filename.endswith('.csv'):
            attachment_bytes = attachment.get_payload(decode=True)

    return sender, presigned_url, attachment_bytes


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
