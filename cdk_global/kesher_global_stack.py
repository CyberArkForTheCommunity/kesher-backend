
from cdk_global.kesher_global_construct import KesherGlobal
from aws_cdk import core


class KesherGlobalStack(core.Stack):

    # pylint: disable=redefined-builtin
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        KesherGlobal(scope=self, id='KesherGlobal')
