from aws_cdk import core
import aws_cdk.aws_ses as ses
import aws_cdk.aws_ses_actions as ses_actions
import aws_cdk.aws_lambda as aws_lambda
import aws_cdk.aws_iam as iam

from cdk.kesher_service_cdk.service_stack.constants import KESHER_DOMAIN_NAME

class EmailServices(core.Construct):


    # pylint: disable=redefined-builtin,invalid-name
    def __init__(self, scope: core.Construct, id: str, lambda_role: iam.Role) -> None:
        super().__init__(scope, id)

        admin_submit_lambda = aws_lambda.Function(
            self,
            'AdminDataSubmission',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.Code.from_asset(self._LAMBDA_ASSET_DIR),
            handler='admin_submit.handler.handler',
            role=lambda_role,
        )

        teacher_submit_lambda = aws_lambda.Function(
            self,
            'TeacherDataSubmission',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.Code.from_asset(self._LAMBDA_ASSET_DIR),
            handler='teacher_submit.handler.handler',
            role=lambda_role,
        )

        ses.ReceiptRuleSet(scope=self, id="DataSubmissionReceiptRuleSet",
            rules=[
                ses.ReceiptRuleOptions(
                    recipients=[f'adminsubmit@{KESHER_DOMAIN_NAME}'],
                    actions=[ses_actions.Lambda(admin_submit_lambda)]
                ),
                ses.ReceiptRuleOptions(
                    recipients=[f'teachersubmit@{KESHER_DOMAIN_NAME}'],
                    actions=[ses_actions.Lambda(teacher_submit_lambda)]
                )
            ]
        )

