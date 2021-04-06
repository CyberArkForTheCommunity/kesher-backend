import os
import boto3
import base64
from botocore.exceptions import ClientError

from mysql.connector import MySQLConnection
import mysql.connector

# from db_handler.utils.get_from_ssm import get_creds, get_secret_value, RdsConnectionParams

SECRET_PATH = "lambda-rds"
REGION = "us-east-1"
#rds settings
DBNAME = 'Kesher'
USER_PASSWORD_SSM_PATH = 'rds-db-credentials/cluster-G4GWF3TT2AEBXDLZQWEQ3GHKMY'

CONENCTION: MySQLConnection = None



##### DELETE ####
import boto3
import base64
from botocore.exceptions import ClientError
from pydantic import BaseModel, SecretStr, ValidationError


class RdsConnectionParams(BaseModel):
    port: int
    username: str  
    password: SecretStr
    host: str

def get_secret(secret_name: str, region: str):

    print('In get_secret')
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region
    )
    print('after creating client of secretsmanager')

    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        print(get_secret_value_response)
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            print("Secrets Manager can't decrypt the protected secret text using the provided KMS key.")
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            print("An error occurred on the server side.")
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("You provided an invalid value for a parameter.")
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("You provided a parameter value that is not valid for the current state of the resource.")
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("We can't find the resource that you asked for.")
            raise e
        else:
            print(f"unknown error. {e}")
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(get_secret_value_response['SecretBinary'])
        
        return secret


def get_creds(secret_name: str, region: str) -> RdsConnectionParams:

    retrieved_creds = get_secret(secret_name, region)
    if retrieved_creds is None:
        error_message = 'Could not retrieve secret from ssm'
        print(error_message)
        raise ValueError(error_message)

    try:
        return RdsConnectionParams.parse_raw(retrieved_creds)
    except (ValidationError, TypeError) as e:
        error_message = 'Could not parse retrieved data from ssm'
        print(error_message)
        raise e

##### DELETE ####


def create_connection_to_rds() -> MySQLConnection:
    print('started create_connection_to_rds')
    secret_params: RdsConnectionParams = get_creds(os.getenv('RDS_SECRET_PATH', SECRET_PATH), os.getenv('REGION', REGION))

    # we want to raise the origin exception
    try:
        #host = 'kesherrdscdk-dbkesherrdscdkdbcluster26435142-1q80effq67c8n.cluster-cqjsrrc4cikc.us-east-1.rds.amazonaws.com'
        #user = 'admin'
        #passwd = '^jQUmCI.rE,gUr,ta=D.CoxLPETb0k'
        #port = 3306
        return mysql.connector.connect(host=secret_params.host, user=secret_params.username,
         passwd=secret_params.password.get_secret_value(), port=secret_params.port, database=DBNAME)
        #return mysql.connector.connect(host=host, user=user, passwd=passwd, port=port, database=DBNAME)
    except Exception as exc:
        print("Database connection failed due to {}".format(exc))
        raise exc

def get_connection_to_rds() -> MySQLConnection:
    global CONENCTION
    if CONENCTION is None or not CONENCTION.is_connected():
        CONENCTION = create_connection_to_rds()
    return CONENCTION

def lambda_handler(event, context):
    print('starting lambda')
    connection = get_connection_to_rds()
    try:
        cur = connection.cursor()
        cur.execute("""SELECT now()""")
        query_results = cur.fetchall()
        print(query_results)
    except Exception as exc:
        print("Database connection failed due to {}".format(exc))     