from aws_cdk import core, aws_cognito
from aws_cdk.aws_cognito import AuthFlow

## A place holder for your cdk assets demonstrated by the cognito cdk stack


class KesherAuth(core.Construct):

    # pylint: disable=redefined-builtin,invalid-name
    def __init__(self, scope: core.Construct, id: str) -> None:
        super().__init__(scope, id)

        self.user_pool = aws_cognito.UserPool(self, "UsersPool", sign_in_aliases=aws_cognito.SignInAliases(username=True))
        cfn_user_pool: aws_cognito.CfnUserPool = self.user_pool.node.default_child
        cfn_user_pool.policies = aws_cognito.CfnUserPool.PoliciesProperty(
            password_policy=aws_cognito.CfnUserPool.PasswordPolicyProperty(minimum_length=8, require_lowercase=False, require_numbers=False,
                                                                           require_symbols=False, require_uppercase=False))
        user_pool_output = core.CfnOutput(self, id="KesherUserPoolID", value=self.user_pool.user_pool_id)
        user_pool_output.override_logical_id("KesherUserPoolID")
        user_pool_arn_output = core.CfnOutput(self, id="KesherUserPoolArn", value=self.user_pool.user_pool_arn)
        user_pool_arn_output.override_logical_id("KesherUserPoolArn")

        self.user_pool_client = aws_cognito.UserPoolClient(
            self,
            "PoolClient",
            user_pool=self.user_pool,
            auth_flows=AuthFlow(admin_user_password=False, user_password=True),
        )
        auth_client_output = core.CfnOutput(self, id="AuthClientID", value=self.user_pool_client.user_pool_client_id)
        auth_client_output.override_logical_id("AuthClientID")
