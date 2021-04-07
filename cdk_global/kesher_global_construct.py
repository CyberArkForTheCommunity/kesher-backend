from aws_cdk import core
from aws_cdk.aws_route53 import MxRecord, MxRecordValue, HostedZone

from kesher_service_cdk.service_stack.constants import KESHER_DOMAIN_NAME

class KesherGlobal(core.Construct):

    # pylint: disable=redefined-builtin,invalid-name
    def __init__(self, scope: core.Construct, id: str) -> None:
        super().__init__(scope, id)

        hosted_zone = HostedZone.from_lookup(scope=self, id="DomainHostedZone", domain_name=KESHER_DOMAIN_NAME, private_zone=False)

        region = core.Stack.of(self).region

        # host_name = f'inbound-smtp.{region}InboundUrl.amazonaws.com'
        host_name = f'inbound-smtp.{region}.amazonaws.com'

        # https://docs.aws.amazon.com/ses/latest/DeveloperGuide/receiving-email-mx-record.html
        MxRecord(scope=self, id='DomainMXRecord', 
                 values=[MxRecordValue(host_name=host_name, priority=10)],
                 zone=hosted_zone)
