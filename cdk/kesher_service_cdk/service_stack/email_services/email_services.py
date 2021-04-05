from aws_cdk import core
import aws_cdk.aws_ses as ses
import aws_cdk.aws_ses_actions as ses_actions
import aws_cdk.aws_lambda as aws_lambda
import aws_cdk.aws_iam as iam

from kesher_service_cdk.service_stack.stack_utils import get_stack_name
from kesher_service_cdk.service_stack.constants import KESHER_DOMAIN_NAME

class EmailServices(core.Construct):


    _LAMBDA_ASSET_DIR = ".build/email_services"

    # pylint: disable=redefined-builtin,invalid-name
    def __init__(self, scope: core.Construct, id: str, lambda_role: iam.Role) -> None:
        super().__init__(scope, id)

        admin_submit_lambda = aws_lambda.Function(
            self,
            'AdminDataSubmission',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.Code.from_asset(self._LAMBDA_ASSET_DIR),
            handler='functions.handler.admin_submit',
            role=lambda_role,
        )

        teacher_submit_lambda = aws_lambda.Function(
            self,
            'TeacherDataSubmission',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.Code.from_asset(self._LAMBDA_ASSET_DIR),
            handler='functions.handler.teacher_submit',
            role=lambda_role,
        )

        ruleset_name = ses.ReceiptRuleSet(scope=self, id="DataSubmissionReceiptRuleSet",
            receipt_rule_set_name=f'{get_stack_name()}RecieptRules',
            rules=[
                ses.ReceiptRuleOptions(
                    receipt_rule_name=f'{get_stack_name()}AdminSubmitRule',
                    recipients=[f'adminsubmit@{KESHER_DOMAIN_NAME}'],
                    actions=[ses_actions.Lambda(function=admin_submit_lambda)]
                ),
                ses.ReceiptRuleOptions(
                    receipt_rule_name=f'{get_stack_name()}TeacherSubmitRule',
                    recipients=[f'teachersubmit@{KESHER_DOMAIN_NAME}'],
                    actions=[ses_actions.Lambda(function=teacher_submit_lambda)]
                )
            ]
        )

        ruleset_name_output = core.CfnOutput(self, id="RuleSetName", value=ruleset_name.receipt_rule_set_name)
        ruleset_name_output.override_logical_id("RuleSetName")
