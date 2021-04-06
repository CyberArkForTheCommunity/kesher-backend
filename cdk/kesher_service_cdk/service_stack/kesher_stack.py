import getpass

from aws_cdk import core

from kesher_service_cdk.service_stack.kesher_construct import KesherServiceEnvironment, get_stack_name

from .auth_construct import KesherAuth

class KesherStack(core.Stack):

    # pylint: disable=redefined-builtin
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.kesher_auth = KesherAuth(self, f"{get_stack_name()}Auth")
        self.kesher_service_env = KesherServiceEnvironment(self, "Service", self.kesher_auth.user_pool.user_pool_arn)
