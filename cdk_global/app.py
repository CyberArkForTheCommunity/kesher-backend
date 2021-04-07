#!/usr/bin/env python3

# pylint: disable=invalid-name,ungrouped-imports

import os
import sys

from aws_cdk import core
from boto3 import client, session

sys.path.append(os.getcwd())

from cdk_global.kesher_global_stack import KesherGlobalStack


account = client('sts').get_caller_identity()['Account']
region = session.Session().region_name
app = core.App()
kesher_stack = KesherGlobalStack(
    app, 'KesherGlobalStack',
    env=core.Environment(account=os.environ.get("AWS_DEFAULT_ACCOUNT", account), region=os.environ.get("AWS_DEFAULT_REGION", region)))

app.synth()
