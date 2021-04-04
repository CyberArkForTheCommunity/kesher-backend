import os
import sys
from git import Repo
import getpass

from kesher_service_cdk.service_stack.constants import BASE_NAME
from aws_cdk.aws_apigateway import Resource
from aws_cdk import (core, aws_iam as iam, aws_apigateway as apigw, aws_lambda as _lambda, aws_dynamodb)

sys.path.append(os.getcwd())


def read_git_branch() -> str:

    project_path = os.environ['PROJECT_DIR']
    # load git branch name in development environment
    repo = Repo(project_path)
    return repo.active_branch.name


def get_stack_name() -> str:
    return BASE_NAME
    """
    branch_name = read_git_branch()
    # remove special characters from branch name
    branch_name = ''.join(e for e in branch_name if e.isalnum()).capitalize()
    stack_name: str = f"{getpass.getuser().capitalize().replace('.','')}{BASE_NAME}{branch_name}"
    return stack_name
    """


class KesherServiceEnvironment(core.Construct):
    _API_HANDLER_LAMBDA_MEMORY_SIZE = 128
    _API_HANDLER_LAMBDA_TIMEOUT = 10
    _LAMBDA_ASSET_DIR = ".build/service"

    # pylint: disable=redefined-builtin,invalid-name
    def __init__(self, scope: core.Construct, id: str, user_pool_arn: str) -> None:
        super().__init__(scope, id)

        core.CfnOutput(self, id="StackName", value=get_stack_name())

        self.service_role = iam.Role(
            self, "KesherServiceRole", assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"), inline_policies={
                "KesherServicePolicy":
                    iam.PolicyDocument(statements=[
                        iam.PolicyStatement(actions=["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
                                            resources=["arn:aws:logs:*:*:*"], effect=iam.Effect.ALLOW)
                    ])
            })

        role_output = core.CfnOutput(self, id="KesherServiceRoleArn", value=self.service_role.role_arn)
        role_output.override_logical_id("KesherServiceRoleArn")

        self.table = aws_dynamodb.Table(
            self,
            'kesher-employees',
            partition_key=aws_dynamodb.Attribute(name="id", type=aws_dynamodb.AttributeType.STRING),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=core.RemovalPolicy.RETAIN
        )
        self.table.grant_read_write_data(self.service_role)

        self.rest_api: apigw.LambdaRestApi = apigw.RestApi(self, "kesher-rest-api", rest_api_name="kesher Rest API",
                                                           description="This service handles kesher")
        endpoint_output = core.CfnOutput(self, id="KesherApiGw", value=self.rest_api.url)
        endpoint_output.override_logical_id("KesherApiGw")
        self.api_authorizer: apigw.CfnAuthorizer = self.__create_api_authorizer(user_pool_arn=user_pool_arn, api=self.rest_api)
        kesher_resource: apigw.Resource = self.rest_api.root.add_resource("kesher")
        self.__add_create_lambda_integration(kesher_resource, user_pool_arn)
        kesher_name_resource = kesher_resource.add_resource("{name}")
        self.__add_update_lambda_integration(kesher_name_resource, user_pool_arn)
        self.__add_get_lambda_integration(kesher_name_resource, user_pool_arn)

    # pylint: disable = no-value-for-parameter
    def __add_create_lambda_integration(self, kesher: Resource, user_pool_arn: str):
        lambda_function = _lambda.Function(
            self,
            'CreateKesher',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset(self._LAMBDA_ASSET_DIR),
            handler='service.handler.create_kesher',
            role=self.service_role,
            environment={
                "KESHER_USER_POOL_ARN": user_pool_arn
            },
        )
        self.__add_resource_method(
            resource=kesher,
            http_method="POST",
            integration=apigw.LambdaIntegration(handler=lambda_function),  # POST /kesher
            authorizer=self.api_authorizer,
        )

    def __add_update_lambda_integration(self, kesher_name: Resource, user_pool_arn: str):
        lambda_function = _lambda.Function(
            self,
            'UpdateKesher',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset(self._LAMBDA_ASSET_DIR),
            handler='service.handler.update_kesher',
            role=self.service_role,
            environment={
                "KESHER_USER_POOL_ARN": user_pool_arn
            },
        )
        self.__add_resource_method(
            resource=kesher_name,
            http_method="PUT",
            integration=apigw.LambdaIntegration(handler=lambda_function),  # PUT /kesher/{name}
            authorizer=self.api_authorizer,
        )

    def __add_get_lambda_integration(self, kesher_name: Resource, user_pool_arn: str):
        lambda_function = _lambda.Function(
            self,
            'GetKesher',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset(self._LAMBDA_ASSET_DIR),
            handler='service.handler.get_kesher',
            role=self.service_role,
            environment={
                "KESHER_USER_POOL_ARN": user_pool_arn
            },
        )
        self.__add_resource_method(
            resource=kesher_name,
            http_method="GET",
            integration=apigw.LambdaIntegration(handler=lambda_function),  # GET /kesher/{name}
            authorizer=self.api_authorizer,
        )

    def __create_api_authorizer(self, user_pool_arn: str, api: apigw.RestApi) -> apigw.CfnAuthorizer:
        authorizer = apigw.CfnAuthorizer(scope=self, name="KesherApiAuth", id="KesherApiAuth", type="COGNITO_USER_POOLS",
                                         provider_arns=[user_pool_arn], rest_api_id=api.rest_api_id,
                                         identity_source="method.request.header.Authorization")
        return authorizer

    @staticmethod
    def __add_resource_method(resource: apigw.Resource, http_method: str, integration: apigw.LambdaIntegration,
                              authorizer: apigw.CfnAuthorizer) -> None:
        method = resource.add_method(
            http_method=http_method,
            integration=integration,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )
        method_resource: apigw.Resource = method.node.find_child("Resource")
        method_resource.add_property_override("AuthorizerId", {"Ref": authorizer.logical_id})
