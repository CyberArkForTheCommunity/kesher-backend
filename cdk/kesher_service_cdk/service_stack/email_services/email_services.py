from aws_cdk import core
import aws_cdk.aws_ses as ses
import aws_cdk.aws_ses_actions as ses_actions
import aws_cdk.aws_lambda as aws_lambda
import aws_cdk.aws_iam as iam
import aws_cdk.aws_s3 as s3

from kesher_service_cdk.service_stack.stack_utils import get_stack_name
from kesher_service_cdk.service_stack.constants import KESHER_DOMAIN_NAME


EMAIL_BUCKET_ENV_VAR = 'EMAIL_BUCKET'


class EmailServices(core.Construct):


    _LAMBDA_ASSET_DIR = ".build/email_services"

    # pylint: disable=redefined-builtin,invalid-name
    def __init__(self, scope: core.Construct, id: str, lambda_role: iam.Role) -> None:
        super().__init__(scope, id)

        self.emails_bucket = s3.Bucket(
            self,
            f'{get_stack_name()}EmailsBucket',
            removal_policy=core.RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        self.emails_bucket.add_to_resource_policy(
            iam.PolicyStatement(actions=['s3:PutObject'], 
                                resources=[f'arn:aws:s3:::{self.emails_bucket.bucket_name}/*'],
                                principals=[iam.ServicePrincipal('ses.amazonaws.com')],
                                conditions={ "StringEquals": { "aws:Referer": core.Stack.of(self).account } }
            )
        )

        bucket_name_output = core.CfnOutput(self, id="EmailBucket", value=self.emails_bucket.bucket_name)
        bucket_name_output.override_logical_id("EmailBucket")

        admin_submit_lambda = aws_lambda.Function(
            self,
            'AdminDataSubmit',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.Code.from_asset(self._LAMBDA_ASSET_DIR),
            handler='functions.handler.admin_submit',
            role=lambda_role,
            environment={
                EMAIL_BUCKET_ENV_VAR: self.emails_bucket.bucket_name
            },
        )

        teacher_submit_lambda = aws_lambda.Function(
            self,
            'TeacherDataSubmit',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.Code.from_asset(self._LAMBDA_ASSET_DIR),
            handler='functions.handler.teacher_submit',
            role=lambda_role,
            environment={
                EMAIL_BUCKET_ENV_VAR: self.emails_bucket.bucket_name
            },
        )

        self.emails_bucket.grant_read_write(admin_submit_lambda)
        self.emails_bucket.grant_read_write(teacher_submit_lambda)


        ruleset_name = ses.ReceiptRuleSet(scope=self, id="DataSubmissionReceiptRuleSet",
            receipt_rule_set_name=f'{get_stack_name()}RecieptRules',
            rules=[
                ses.ReceiptRuleOptions(
                    receipt_rule_name=f'{get_stack_name()}AdminSubmitRule',
                    recipients=[f'adminsubmit@{KESHER_DOMAIN_NAME}'],
                    actions=[
                        ses_actions.S3(bucket=self.emails_bucket, object_key_prefix="AdminIncomingEmail"), 
                        ses_actions.Lambda(function=admin_submit_lambda)
                    ],
                ),
                ses.ReceiptRuleOptions(
                    receipt_rule_name=f'{get_stack_name()}TeacherSubmitRule',
                    recipients=[f'teachersubmit@{KESHER_DOMAIN_NAME}'],
                    actions=[
                        ses_actions.S3(bucket=self.emails_bucket, object_key_prefix="TeacherIncomingEmail"), 
                        ses_actions.Lambda(function=teacher_submit_lambda),
                    ]
                )
            ]
        )

        ruleset_name_output = core.CfnOutput(self, id="RuleSetName", value=ruleset_name.receipt_rule_set_name)
        ruleset_name_output.override_logical_id("RuleSetName")
