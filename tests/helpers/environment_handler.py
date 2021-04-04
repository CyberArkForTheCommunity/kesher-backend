import os

import boto3
from botocore import xform_name

_ENV = None


def load_env_vars(stack_name) -> dict:
    global _ENV
    if _ENV is None:
        _ENV = get_env_vars(stack_name)

    # load environment variable
    for key, value in _ENV.items():
        os.environ[key] = value
    return _ENV


def get_env_vars(stack_name) -> dict:
    cloudformation = boto3.client('cloudformation')
    response = cloudformation.describe_stacks(StackName=stack_name)
    outputs = response['Stacks'][0]['Outputs']
    env = {}
    for output in outputs:
        if not str(output['OutputKey']).endswith('ServiceRoleArn'):
            env[_to_env_var_name(output['OutputKey'])] = output['OutputValue']
    return env


def _to_env_var_name(name):
    return xform_name(name).upper()
