import os
import sys
from git import Repo
import getpass

from kesher_service_cdk.service_stack.constants import BASE_NAME
from aws_cdk.aws_apigateway import Resource
from aws_cdk import (core, aws_iam as iam, aws_apigateway as apigw, aws_lambda as _lambda, aws_ec2, aws_rds)
from kesher_service_cdk.service_stack.kesher_construct import get_stack_name


# @cached(TTLCache(maxsize=1, ttl=600))
# def get_my_public_ip() -> Optional[str]:
#     for i in range(10):
#         try:
#             response = get("https://api.ipify.org")
#             if response.status_code == HTTPStatus.OK:
#                 return response.text
#         except Exception as exc:
#             print(red(f'get_my_public_ip exception. {str(exc)}'))
#
#         print(yellow(f'get_my_public_ip failed. Trying: {i}, Error code: {response.status_code}'))
#         sleep(4)
#     return None

class DatabaseConstruct(core.Construct):
    _API_HANDLER_LAMBDA_MEMORY_SIZE = 128
    _API_HANDLER_LAMBDA_TIMEOUT = 10
    _LAMBDA_ASSET_DIR = ".build/service"

    # pylint: disable=redefined-builtin,invalid-name
    def __init__(self, scope: core.Construct, id: str, user_pool_arn: str) -> None:
        super().__init__(scope, id)

        # core.CfnOutput(self, id="StackName", value=get_stack_name())

        private_sn = aws_ec2.SubnetConfiguration(name=f"{get_stack_name()}private_sn", subnet_type=aws_ec2.SubnetType.PRIVATE, cidr_mask=24)
        public_sn = aws_ec2.SubnetConfiguration(name=f"{get_stack_name()}public_sn", subnet_type=aws_ec2.SubnetType.PUBLIC, cidr_mask=24)
        # cidr_block = CIDR_BLOCK_PREFIX[session.Session().region_name]
        self.vpc: IVpc = aws_ec2.Vpc(self, id='vpc', cidr='10.1.0.0/16', subnet_configuration=[private_sn, public_sn], max_azs=2)

        db_access_sg: aws_ec2.ISecurityGroup = aws_ec2.SecurityGroup(self, id=f"{get_stack_name()}fromOffice", vpc=self.vpc,
                                                               security_group_name='accessFromOffice', allow_all_outbound=True)
        database_port: int = 3306
        db_access_sg.connections.allow_from(aws_ec2.Peer.ipv4('194.90.225.101/32'), aws_ec2.Port.tcp(database_port), 'access from office only');

        my_sql = aws_rds.DatabaseClusterEngine.aurora_mysql(version=aws_rds.AuroraMysqlEngineVersion.VER_5_7_12)

        cluster = aws_rds.DatabaseCluster(self, id=f"{get_stack_name()}db_cluster",
                                          engine=my_sql,
                                          credentials=aws_rds.Credentials.from_username('clusteradmin'),
                                          instances=1,
                                          port=database_port,
                                          # credentials=aws_rds.Credentials.from_password(username="clusteradmin", password=SecretValue.plain_text("fffs")), # Optional - will default to 'admin' username and generated password
                                          instance_props={
                                              "instance_type": aws_ec2.InstanceType.of(aws_ec2.InstanceClass.BURSTABLE2, aws_ec2.InstanceSize.SMALL),
                                              "vpc_subnets": {
                                                  "subnet_type": aws_ec2.SubnetType.PRIVATE
                                              },
                                              "vpc": self.vpc,
                                              "publicly_accessible": True,
                                              "security_groups": [db_access_sg],

                                          })

        # build_cfn_output(construct=self, output_id=f"VpcId", value=self.vpc.vpc_id, export_name=f"{get_stack_name()}Vpc")
        # return self.vpc

        # self.service_role = iam.Role(
        #     self, "KesherServiceRole", assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"), inline_policies={
        #         "KesherServicePolicy":
        #             iam.PolicyDocument(statements=[
        #                 iam.PolicyStatement(actions=["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
        #                                     resources=["arn:aws:logs:*:*:*"], effect=iam.Effect.ALLOW)
        #             ])
        #     })
        #
        # role_output = core.CfnOutput(self, id="KesherServiceRoleArn", value=self.service_role.role_arn)
        # role_output.override_logical_id("KesherServiceRoleArn")
        #
        # self.table = aws_dynamodb.Table(
        #     self,
        #     'kesher-employees',
        #     partition_key=aws_dynamodb.Attribute(name="id", type=aws_dynamodb.AttributeType.STRING),
        #     billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
        #     removal_policy=core.RemovalPolicy.RETAIN
        # )
        # self.table.grant_read_write_data(self.service_role)
        #
        # self.rest_api: apigw.LambdaRestApi = apigw.RestApi(self, "kesher-rest-api", rest_api_name="kesher Rest API",
        #                                                    description="This service handles kesher")
        # endpoint_output = core.CfnOutput(self, id="KesherApiGw", value=self.rest_api.url)
        # endpoint_output.override_logical_id("KesherApiGw")
        # self.api_authorizer: apigw.CfnAuthorizer = self.__create_api_authorizer(user_pool_arn=user_pool_arn, api=self.rest_api)
        # kesher_resource: apigw.Resource = self.rest_api.root.add_resource("kesher")
        # self.__add_create_lambda_integration(kesher_resource, user_pool_arn)
        # kesher_name_resource = kesher_resource.add_resource("{name}")
        # self.__add_update_lambda_integration(kesher_name_resource, user_pool_arn)
        # self.__add_get_lambda_integration(kesher_name_resource, user_pool_arn)

    # pylint: disable = no-value-for-parameter
    # def __add_create_lambda_integration(self, kesher: Resource, user_pool_arn: str):
    #     lambda_function = _lambda.Function(
    #         self,
    #         'CreateKesher',
    #         runtime=_lambda.Runtime.PYTHON_3_8,
    #         code=_lambda.Code.from_asset(self._LAMBDA_ASSET_DIR),
    #         handler='service.handler.create_kesher',
    #         role=self.service_role,
    #         environment={
    #             "KESHER_USER_POOL_ARN": user_pool_arn
    #         },
    #     )
    #     self.__add_resource_method(
    #         resource=kesher,
    #         http_method="POST",
    #         integration=apigw.LambdaIntegration(handler=lambda_function),  # POST /kesher
    #         authorizer=self.api_authorizer,
    #     )
    #
    # def __add_update_lambda_integration(self, kesher_name: Resource, user_pool_arn: str):
    #     lambda_function = _lambda.Function(
    #         self,
    #         'UpdateKesher',
    #         runtime=_lambda.Runtime.PYTHON_3_8,
    #         code=_lambda.Code.from_asset(self._LAMBDA_ASSET_DIR),
    #         handler='service.handler.update_kesher',
    #         role=self.service_role,
    #         environment={
    #             "KESHER_USER_POOL_ARN": user_pool_arn
    #         },
    #     )
    #     self.__add_resource_method(
    #         resource=kesher_name,
    #         http_method="PUT",
    #         integration=apigw.LambdaIntegration(handler=lambda_function),  # PUT /kesher/{name}
    #         authorizer=self.api_authorizer,
    #     )
    #
    # def __add_get_lambda_integration(self, kesher_name: Resource, user_pool_arn: str):
    #     lambda_function = _lambda.Function(
    #         self,
    #         'GetKesher',
    #         runtime=_lambda.Runtime.PYTHON_3_8,
    #         code=_lambda.Code.from_asset(self._LAMBDA_ASSET_DIR),
    #         handler='service.handler.get_kesher',
    #         role=self.service_role,
    #         environment={
    #             "KESHER_USER_POOL_ARN": user_pool_arn
    #         },
    #     )
    #     self.__add_resource_method(
    #         resource=kesher_name,
    #         http_method="GET",
    #         integration=apigw.LambdaIntegration(handler=lambda_function),  # GET /kesher/{name}
    #         authorizer=self.api_authorizer,
    #     )
    #
    # def __create_api_authorizer(self, user_pool_arn: str, api: apigw.RestApi) -> apigw.CfnAuthorizer:
    #     authorizer = apigw.CfnAuthorizer(scope=self, name="KesherApiAuth", id="KesherApiAuth", type="COGNITO_USER_POOLS",
    #                                      provider_arns=[user_pool_arn], rest_api_id=api.rest_api_id,
    #                                      identity_source="method.request.header.Authorization")
    #     return authorizer
    #
    # @staticmethod
    # def __add_resource_method(resource: apigw.Resource, http_method: str, integration: apigw.LambdaIntegration,
    #                           authorizer: apigw.CfnAuthorizer) -> None:
    #     method = resource.add_method(
    #         http_method=http_method,
    #         integration=integration,
    #         authorization_type=apigw.AuthorizationType.COGNITO,
    #     )
    #     method_resource: apigw.Resource = method.node.find_child("Resource")
    #     method_resource.add_property_override("AuthorizerId", {"Ref": authorizer.logical_id})
