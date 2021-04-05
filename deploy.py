#!/usr/bin/env python
import argparse
import getpass
import os
import random
import string
from kesher_service_cdk.service_stack import constants
from boto3 import session
from pathlib import Path
from dotenv import load_dotenv
from kesher_service_cdk.service_stack.stack_utils import get_stack_name
from build import do_build
from deploy import users

PROJECT_DIR_KEY = 'PROJECT_DIR'

def init_local_dotenv():
    region = session.Session().region_name
    project_path = os.path.abspath(os.path.dirname(__file__))
    vars = {
        'DEFAULT_USER_PASSWORD': random_password(16),
        'USER_NAME': getpass.getuser(),
        'PYLINTRC': '.venv/src/tools-configuration/pylint_linter/configuration/.pylintrc',
        'COGNITO_URL': f'https://cognito-idp.{region}.amazonaws.com/',
        'USE_REMOTE_API': 'true'
    }
    env_init_local_dotenv(project_path, vars)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--deploy-env', default='dev')
    parser.add_argument("--region", default="eu-west-1")
    parser.add_argument('--stack-name')
    parser.add_argument('--require-approval', default='broadening')
    parser.add_argument('--clean', nargs='?', const=True, help="Remove existing environment before deploying")
    parser.add_argument('--synth', nargs='?', const=True, help="Synthesize cloudformation.yml before deploying")
    parser.add_argument('--no-build', nargs='?', const=True, default=False, help="Skip lambda build")
    parser.add_argument('--skip-deps', nargs="?", const=True, default=False, help="Skip lambda dependencies")
    args = parser.parse_args()

    # environment update with the .env file
    init_local_dotenv()

    if not args.no_build:
        print("Building the lambda package...")
        do_build(consume_dependencies=not args.skip_deps)

    if args.clean:
        print("cdk destroy...")
        rc = os.system(f"cdk destroy")
        if rc != 0:
            print(f"cdk destroy failed with return code: {rc}")
            exit(1)

    if args.synth:
        print("cdk synth...")
        Path("cdk.out").mkdir(parents=True, exist_ok=True)
        rc = os.system(f"cdk synth --no-staging > .build{os.path.sep}template.yml")
        if rc:
            print(f"cdk synth failed with return code: {rc}")
            exit(1)

    print("cdk deploy...")
    rc = os.system(f"cdk deploy --require-approval {args.require_approval}")
    if rc:
        print(f"cdk deploy failed with return code: {rc}")
        exit(1)

    user_pool_id = users.get_user_pool_id(get_stack_name())

    password = os.environ.get('DEFAULT_USER_PASSWORD', default='Password123')
    email = os.environ.get('USER_EMAIL')
    users.create_user(getpass.getuser(), password, user_pool_id, email=email)

def env_init_local_dotenv(project_path: str, env_vars: dict, override_env_vars: bool = False):
    """
    Init a new .env file if it does not exist and load it into os.environ
    :param project_path: path to look for the relevant .env file or to create a new one
    :param env_vars: environment variables to be written to the .env file if it does not exist.
    :param override_env_vars: where to override the system environment variables with the variables in `.env` file 
    Note that 'project_path' parameter will be implicitly added as an additional environment variable,
    there is no need to duplicate it in 'env_vars' parameter
    """
    dot_env_file = f'{project_path}/.env'
    region = session.Session().region_name
    # noinspection PyTypeChecker
    lines = [f'{key}={value}{os.linesep}' for key, value in env_vars.items()]
    proj_path_line = f'{PROJECT_DIR_KEY}={project_path}{os.linesep}'
    lines.append(proj_path_line)
    if not os.path.exists(dot_env_file):
        print(f'.env file not found, creating with a random password, user {getpass.getuser()} and region {region}')
        with open(dot_env_file, 'w') as file:
            file.writelines(lines)
    else:
        with open(dot_env_file, 'a+') as file:  # append to the end of file
            file.seek(0)
            if PROJECT_DIR_KEY not in file.read():
                file.write(os.linesep + proj_path_line)
        print('using existing .env file')

    load_dotenv(dotenv_path=dot_env_file, override=override_env_vars)

def random_password(n=10):
    return ''.join(random.choices(string.digits, k=1)+random.choices(string.ascii_lowercase, k=1) +
                   random.choices(string.ascii_uppercase, k=1)+random.choices(string.ascii_letters + string.digits, k=n-3))

if __name__ == '__main__':
    main()
