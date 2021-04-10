import os
import sys
from git import Repo
import getpass
from http import HTTPStatus
from typing import List, Optional

from kesher_service_cdk.service_stack.constants import BASE_NAME
from aws_cdk.aws_apigateway import Resource
from aws_cdk import (core, aws_iam as iam, aws_apigateway as apigw, aws_lambda as _lambda, aws_ec2, aws_rds)
from kesher_service_cdk.service_stack.stack_utils import get_stack_name,  read_git_branch
from requests import get


def get_my_public_ip() -> Optional[str]:
    for i in range(10):
        try:
            response = get("https://api.ipify.org")
            if response.status_code == HTTPStatus.OK:
                return response.text
        except Exception as exc:
            print(f'get_my_public_ip exception. {str(exc)}')

        print(f'get_my_public_ip failed. Trying: {i}, Error code: {response.status_code}')
        sleep(4)
    return None


class DatabaseConstruct(core.Construct):
    _API_HANDLER_LAMBDA_MEMORY_SIZE = 128
    _API_HANDLER_LAMBDA_TIMEOUT = 10
    _LAMBDA_ASSET_DIR = ".build/service"

    # pylint: disable=redefined-builtin,invalid-name
    def __init__(self, scope: core.Construct, id: str, user_pool_arn: str) -> None:
        super().__init__(scope, id)


        private_sn = aws_ec2.SubnetConfiguration(name=f"{get_stack_name()}private_sn", subnet_type=aws_ec2.SubnetType.PRIVATE, cidr_mask=24)
        public_sn = aws_ec2.SubnetConfiguration(name=f"{get_stack_name()}public_sn", subnet_type=aws_ec2.SubnetType.PUBLIC, cidr_mask=24)
        self.vpc: IVpc = aws_ec2.Vpc(self, id='vpc', cidr='10.1.0.0/16', subnet_configuration=[private_sn, public_sn], max_azs=2)

        db_access_sg: aws_ec2.ISecurityGroup = aws_ec2.SecurityGroup(self, id=f"{get_stack_name()}fromOffice", vpc=self.vpc,
                                                                     security_group_name='accessFromOffice', allow_all_outbound=True)
        database_port: int = 3306
        db_access_sg.connections.allow_from(aws_ec2.Peer.ipv4(f'{get_my_public_ip()}/32'), aws_ec2.Port.tcp(database_port),
                                            'access from office only');

        my_sql = aws_rds.DatabaseClusterEngine.aurora_mysql(version=aws_rds.AuroraMysqlEngineVersion.VER_5_7_12)

        cluster = aws_rds.DatabaseCluster(self, id=f"{get_stack_name()}db_cluster",
                                          engine=my_sql,
                                          credentials=aws_rds.Credentials.from_username('admin', secret_name=read_git_branch()),
                                          instances=1,
                                          port=database_port,
                                          instance_props={
                                              "instance_type": aws_ec2.InstanceType.of(aws_ec2.InstanceClass.BURSTABLE2,
                                                                                       aws_ec2.InstanceSize.SMALL),
                                              "vpc_subnets": {
                                                  "subnet_type": aws_ec2.SubnetType.PUBLIC
                                              },
                                              "vpc": self.vpc,
                                              "publicly_accessible": True,
                                              "security_groups": [db_access_sg],

                                          })

