import boto3
from aws_cdk import (aws_iam, aws_lambda)
from aws_cdk import core

class ConnectionToRDS(core.Construct):
    __DB_HANDLER_CONNECTION = f'.build/db_handler'
    __API_HANDLER_LAMBDA_MEMORY_SIZE = 192
    _STEP_FUNCTION_TIMEOUT_SEC = 10

    def __init__(self, scope: core.Construct, id_: str) -> None:
        super().__init__(scope, id_)

        rds_connection_lambda = self._create_rds_connection_lambda(id_)

    def _get_region(self) -> str:
        sts_client = boto3.client('sts')
        account_id = sts_client.get_caller_identity()['Account']
        return sts_client.meta.region_name

    def _create_rds_connection_lambda(self, id_: str) -> aws_lambda.Function:
            self.lambda_handler_role = self._create_lambda_role('connect_to_rds_role')
            func = aws_lambda.Function(
                self,
                f'{id_}ConnectionToRds',
                function_name=f'{id_}ConnectionToRds',
                runtime=aws_lambda.Runtime.PYTHON_3_8,
                code=aws_lambda.Code.from_asset(self.__DB_HANDLER_CONNECTION),
                handler='db_handler.handler.lambda_handler',
                role=self.lambda_handler_role,
                environment={'REGION': self._get_region()}, # TODO: add secret path 
                timeout=core.Duration.seconds(self._STEP_FUNCTION_TIMEOUT_SEC),
                memory_size=self.__API_HANDLER_LAMBDA_MEMORY_SIZE,
                retry_attempts=0,
            )
            idaptive_output = core.CfnOutput(self, id="ConnectionToRds", value=func.function_name)
            idaptive_output.override_logical_id("ConnectionToRds")

            return func


    def _create_lambda_role(self, role_name: str) -> aws_iam.Role:
            role = aws_iam.Role(
                self,
                f'{role_name}',
                assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com"),
                inline_policies={
                    "SsmPolicy":
                        aws_iam.PolicyDocument(statements=[
                            aws_iam.PolicyStatement(
                                actions=["ssm:GetParameter", "secretsmanager:GetSecretValue"],
                                resources=["*"], # TODO: change to secret arn
                                effect=aws_iam.Effect.ALLOW,
                            ),
                        ]),
                },
                # add CloudWatch logging policy
                managed_policies=[aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonRDSDataFullAccess"), ],
            )
            return role
