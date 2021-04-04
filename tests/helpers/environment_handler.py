import os
import boto3
from git import Repo
from botocore import xform_name

_ENV = None
BASE_NAME = "Kesher"

def read_git_branch() -> str:
    project_path = os.environ['PROJECT_DIR']
    # load git branch name in development environment
    repo = Repo(project_path)
    return repo.active_branch.name


def get_stack_name() -> str:
    branch_name = read_git_branch()
    # remove special characters from branch name
    branch_name = ''.join(e for e in branch_name if e.isalnum()).capitalize()
    stack_name: str = f"{BASE_NAME}{branch_name}"
    # stack_name: str = f"{getpass.getuser().capitalize().replace('.','')}{BASE_NAME}{branch_name}"
    return stack_name

def load_env_vars() -> dict:
    global _ENV
    if _ENV is None:
        _ENV = get_env_vars(get_stack_name())

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
