import argparse
import getpass
import boto3
from kesher_service_cdk.service_stack.constants import BASE_NAME
from kesher_service_cdk.service_stack.stack_utils import get_stack_name

from mypy_boto3_cognito_idp import Client


def create_user(name: str, password: str, user_pool_id: str, group_name: str = "admins", email: str = None):
    client: Client = boto3.client('cognito-idp')
    if email is None:
        email = f"{name}@kesher.com"
    existing_users = client.list_users(UserPoolId=user_pool_id, Limit=1, Filter=f"username = \"{name}\"")
    if len(existing_users['Users']) > 0:
        client.admin_delete_user(UserPoolId=user_pool_id, Username=name)
    client.admin_create_user(UserPoolId=user_pool_id, Username=name, UserAttributes=[{
        'Name': "email",
        'Value': email
    }], MessageAction='SUPPRESS')
    client.admin_set_user_password(UserPoolId=user_pool_id, Username=name, Password=password, Permanent=True)

    groups = client.list_groups(UserPoolId=user_pool_id)
    if not any(x['GroupName'] == group_name for x in groups['Groups']):
        client.create_group(GroupName=group_name, UserPoolId=user_pool_id)
    client.admin_add_user_to_group(UserPoolId=user_pool_id, Username=name, GroupName=group_name)


def get_user_pool_id(stack_name) -> str:
    cloudformation = boto3.client('cloudformation')
    response = cloudformation.describe_stacks(StackName=stack_name)
    outputs = response['Stacks'][0]['Outputs']
    for output in outputs:
        if str(output['OutputKey']) == "KesherUserPoolID":
            return output['OutputValue']
    return ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', default=getpass.getuser())
    parser.add_argument('-p', '--password', required=True)
    parser.add_argument('-u', '--user-pool-id')
    parser.add_argument('-e', '--email', required=False)
    args = parser.parse_args()
    if args.user_pool_id is None:
        args.user_pool_id = get_user_pool_id(get_stack_name(BASE_NAME))
    create_user(args.name, args.password, args.user_pool_id, email=args.email)


if __name__ == '__main__':
    main()
