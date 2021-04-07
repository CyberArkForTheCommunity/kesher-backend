#!/usr/bin/env python
import argparse
import getpass
import os
import random
import string
from kesher_service_cdk.service_stack import constants
import boto3
from boto3 import session
from pathlib import Path
from dotenv import load_dotenv
from kesher_service_cdk.service_stack.stack_utils import get_stack_name
from build import do_build
from deploy import users


PROJECT_DIR_KEY = 'PROJECT_DIR'


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--clean-bucket', '-c', nargs='?', const=True, help="Delete bucket items before destruction")
    parser.add_argument('--disable-active-ses-rule-set', '-d', nargs='?', const=True, help="Disalbe SES Active rule set - this will prevent SES from processing receiving any emails!")
    args = parser.parse_args()

    ruleset_name = get_stack_output("RuleSetName")
    ses = boto3.client('ses')
    response = ses.describe_active_receipt_rule_set()
    if response.get('Metadata', {}).get('Name', "") == ruleset_name:
        ses.set_active_receipt_rule_set() # Disable the active rule set 
        

    if args.clean_bucket:
        bucket = get_stack_output("EmailBucket")
        if bucket:
            print('Deleting bucket content...')
            os.system(f'aws s3 rb s3://{bucket} --force')
            

    print("cdk destroy...")
    rc = os.system(f"cdk destroy")
    if rc:
        print(f"cdk destroy failed with return code: {rc}")
        exit(1)


def get_stack_output(output_key: str) -> str:
    cloudformation = boto3.client('cloudformation')
    response = cloudformation.describe_stacks(StackName=get_stack_name())
    outputs = response['Stacks'][0]['Outputs']
    output_value = [output['OutputValue'] for output in outputs if output['OutputKey'] == output_key]
    return output_value[0] if output_value else None

if __name__ == '__main__':
    main()
