from constructs import Construct

import aws_cdk
from aws_cdk import (
    Stack,
    aws_ec2,
    aws_lambda,
    aws_lambda_python_alpha,
    aws_lambda_event_sources,
    Duration,
)


class WritebackFunctionStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc, instance,
                 instance_security_group, table, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._writeback_security_group = aws_ec2.SecurityGroup(
            self,
            "zipcodesWritebackSecurityGroup",
            vpc=vpc,
            allow_all_outbound=False,
        )

        self._writeback_security_group.connections.allow_to(
            instance_security_group,
            aws_cdk.aws_ec2.Port.tcp(5432),
            "Allow Lambda access to PostgreSQL",
        )

        aws_cdk.CfnOutput(self, "WritebackSecurityGroupId",
                          value=self._writeback_security_group.security_group_id)

        writeback_handler = aws_lambda_python_alpha.PythonFunction(
            self,
            "zipcodesWritebackLambda",
            entry="lambda/writeback-handler",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            memory_size=2048,
            timeout=Duration.minutes(1),
            insights_version=aws_lambda.LambdaInsightsVersion.VERSION_1_0_135_0,
            vpc=vpc,
            security_groups=[self._writeback_security_group],
        )

        writeback_handler.add_environment(
            "DATABASE_HOST", instance.instance_private_ip)

        writeback_handler.add_event_source(
            aws_lambda_event_sources.DynamoEventSource(
                table,
                starting_position=aws_lambda.StartingPosition.LATEST,
                batch_size=100,
                parallelization_factor=10,
            )
        )

    @property
    def writeback_security_group(self):
        return self._writeback_security_group
