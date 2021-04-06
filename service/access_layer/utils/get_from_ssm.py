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

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region
    )

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
