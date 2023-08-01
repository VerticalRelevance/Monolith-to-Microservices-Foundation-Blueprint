from constructs import Construct

import aws_cdk
from aws_cdk import (
    Stack,
    aws_dynamodb,
    aws_lambda,
    aws_lambda_event_sources,
    aws_apigateway,
    Stack,
    Duration,
)


class WebAppMicroServiceStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc, instance, instance_security_group, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create DynamoDb Table
        table = aws_dynamodb.Table(
            self,
            id="zipcodes",
            partition_key=aws_dynamodb.Attribute(
                name="zip_code", type=aws_dynamodb.AttributeType.STRING
            ),
            removal_policy=aws_cdk.RemovalPolicy.DESTROY,
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
            stream=aws_dynamodb.StreamViewType.NEW_IMAGE,
        )

        aws_cdk.CfnOutput(self, "TableName", value=table.table_name)

        # TODO: Implement this CDK feature https://github.com/aws/aws-cdk/issues/21825

        # Create the Lambda function to receive the request
        api_hanlder = aws_lambda.Function(
            self,
            "ApiHandler",
            function_name="apigw_handler",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            code=aws_lambda.Code.from_asset("lambda/apigw-handler"),
            handler="lambda.lambda_handler",
            memory_size=2048,
            timeout=Duration.minutes(1),
            insights_version=aws_lambda.LambdaInsightsVersion.VERSION_1_0_135_0,
        )

        PSQL_layer = aws_lambda.LayerVersion(
            self,
            "PSQLLayer",
            code=aws_lambda.Code.from_asset("lambda/writeback-handler/psycopg2"),
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_9],
        )

        self._writeback_security_group = aws_cdk.aws_ec2.SecurityGroup(
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

        writeback_handler = aws_lambda.Function(
            self,
            "zipcodesWritebackLambda",
            function_name="zipcodesWritebackLambda",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            code=aws_lambda.Code.from_asset("lambda/writeback-handler"),
            handler="lambda.lambda_handler",
            memory_size=2048,
            timeout=Duration.minutes(1),
            layers=[PSQL_layer],
            insights_version=aws_lambda.LambdaInsightsVersion.VERSION_1_0_135_0,
            vpc=vpc,
            security_groups=[self._writeback_security_group],
        )

        writeback_handler.add_environment("DATABASE_HOST", instance.instance_private_ip)

        writeback_handler.add_event_source(
            aws_lambda_event_sources.DynamoEventSource(
                table,
                starting_position=aws_lambda.StartingPosition.LATEST,
                batch_size=100,
                parallelization_factor=10,
            )
        )

        # Grant permission to lambda to write to table
        table.grant_read_write_data(api_hanlder)

        api_hanlder.add_environment("TABLE_NAME", table.table_name)

        # Create API Gateway
        api = aws_apigateway.LambdaRestApi(
            self, "MicroServiceZipcodeEndpoint", handler=api_hanlder, proxy=False
        )

        # Output the API URL
        aws_cdk.CfnOutput(self, "ApiUrl", value=api.url)

        items = api.root.add_resource("zipcode")
        item = items.add_resource("{zipcode}")
        item.add_method("GET")
        item.add_method("PUT")

    @property
    def writeback_security_group(self):
        return self._writeback_security_group
