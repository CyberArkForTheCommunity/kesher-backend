
import os
import sys
from git import Repo

from aws_cdk.aws_apigateway import Resource
from aws_cdk import (core, aws_iam as iam, aws_apigateway as apigw, aws_lambda as _lambda, aws_dynamodb)
from aws_cdk.core import Duration
from aws_cdk.aws_lambda import Function

from kesher_service_cdk.service_stack.stack_utils import get_stack_name
from kesher_service_cdk.service_stack.email_services.email_services import EmailServices

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
                        iam.PolicyStatement(
                            actions=["secretsmanager:GetSecretValue"],
                            resources=["*"], effect=iam.Effect.ALLOW),
                        iam.PolicyStatement(
                            actions=["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
                            resources=["arn:aws:logs:*:*:*"], effect=iam.Effect.ALLOW)
                    ])
            })

        EmailServices(scope=self, id="Email", lambda_role=self.service_role)

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
                                                           description="This service handles kesher's APIs..")
        endpoint_output = core.CfnOutput(self, id="KesherApiGw", value=self.rest_api.url)
        endpoint_output.override_logical_id("KesherApiGw")

        self.api_authorizer: apigw.CfnAuthorizer = self.__create_api_authorizer(user_pool_arn=user_pool_arn,
                                                                                api=self.rest_api)

        self.api_resource: apigw.Resource = self.rest_api.root.add_resource("api")

        self._environment = {
            "KESHER_USER_POOL_ARN": user_pool_arn
        }
        self._add_children_api()
        self._add_report_categories_api()
        self._add_user_profile_api()

    def _add_report_categories_api(self):
        categories_resource: apigw.Resource = self.api_resource.add_resource("categories")
        self.__add_lambda_api(lambda_name='GetReportCategories',
                              handler_method='service.report_category_handler.get_report_categories_list',
                              resource=categories_resource, http_method="GET",
                              member_name="get_categories_api_lambda")

    def _add_children_api(self):
        children_resource: apigw.Resource = self.api_resource.add_resource("children")
        self.__add_lambda_api(lambda_name='GetChildren', handler_method='service.children_handler.get_children',
                              resource=children_resource, http_method="GET",
                              member_name="get_children_api_lambda")

        child_resource: apigw.Resource = children_resource.add_resource("{child_id}")
        daily_reports_resource = child_resource.add_resource('daily-reports')
        attendance_resource = child_resource.add_resource('attendance')

        self.__add_lambda_api(lambda_name='AddChildReport',
                              handler_method='service.children_handler.add_child_report',
                              resource=daily_reports_resource, http_method="POST",
                              member_name="add_child_report_api_lambda")

        self.__add_lambda_api(lambda_name='GetChildReports',
                              handler_method='service.children_handler.get_child_reports',
                              resource=daily_reports_resource, http_method="GET",
                              member_name="get_child_reports_api_lambda")

        self.__add_lambda_api(lambda_name='UpdateChildAttendance',
                              handler_method='service.children_handler.update_child_attendance',
                              resource=attendance_resource, http_method="PUT",
                              member_name="update_child_attendance")

    def _add_user_profile_api(self):
        categories_resource: apigw.Resource = self.api_resource.add_resource("user-profile")
        self.__add_lambda_api(lambda_name='GetUserProfile',
                              handler_method='service.user_profile_handler.get_user_profile',
                              resource=categories_resource, http_method="GET",
                              member_name="get_user_profile_api_lambda")

    def __add_lambda_api(self, lambda_name: str, handler_method: str, resource: Resource, http_method: str,
                         member_name: str,
                         description: str = ''):
        new_api_lambda = \
            self.__create_lambda_function(lambda_name=f'{lambda_name}Api',
                                          handler=handler_method,
                                          role=self.service_role,
                                          environment=self._environment,
                                          description=description)

        self.__add_resource_method(resource=resource, http_method=http_method,
                                   integration=apigw.LambdaIntegration(handler=new_api_lambda),
                                   authorizer=self.api_authorizer)

        cfn_res: core.CfnResource = new_api_lambda.node.default_child
        cfn_res.override_logical_id(lambda_name)

        setattr(self, member_name, new_api_lambda)

    # pylint: disable = no-value-for-parameter
    def __create_lambda_function(self, lambda_name: str, handler: str, role: iam.Role, environment: dict,
                                 description: str = '',
                                 timeout: Duration = Duration.seconds(_API_HANDLER_LAMBDA_TIMEOUT)) -> Function:
        return _lambda.Function(self, lambda_name, runtime=_lambda.Runtime.PYTHON_3_8,
                                code=_lambda.Code.from_asset(self._LAMBDA_ASSET_DIR),
                                handler=handler, role=role, retry_attempts=0, environment=environment, timeout=timeout,
                                memory_size=self._API_HANDLER_LAMBDA_MEMORY_SIZE, description=description)

    def __create_api_authorizer(self, user_pool_arn: str, api: apigw.RestApi) -> apigw.CfnAuthorizer:
        authorizer = apigw.CfnAuthorizer(scope=self, name="KesherApiAuth", id="KesherApiAuth",
                                         type="COGNITO_USER_POOLS",
                                         provider_arns=[user_pool_arn], rest_api_id=api.rest_api_id,
                                         identity_source="method.request.header.Authorization")
        return authorizer

    @staticmethod
    def __add_resource_method(resource: apigw.Resource, http_method: str, integration: apigw.LambdaIntegration,
                              authorizer: apigw.CfnAuthorizer) -> None:
        method = resource.add_method(
            http_method=http_method,
            integration=integration,
            authorization_type=apigw.AuthorizationType.COGNITO)

        method_resource: apigw.Resource = method.node.find_child("Resource")

        method_resource.add_property_override("AuthorizerId", {"Ref": authorizer.logical_id})
