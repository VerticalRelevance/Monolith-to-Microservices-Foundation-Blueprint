from constructs import Construct

import aws_cdk
import aws_cdk.aws_lambda_event_sources as eventsources
from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigateway as apigw_,
    aws_ec2 as ec2,
    aws_iam as iam,
    App,
    Stack,
    Duration,
)


TABLE_NAME = "zipcodes"


class CdkWebAppMicroServiceStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create DynamoDb Table
        demo_table = dynamodb.Table(
            self,
            id=TABLE_NAME,
            table_name=TABLE_NAME,
            partition_key=dynamodb.Attribute(
                name="zip_code", type=dynamodb.AttributeType.STRING
            ),
            removal_policy=aws_cdk.RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            stream=dynamodb.StreamViewType.NEW_IMAGE,
        )

        # TODO: Implement this CDK feature https://github.com/aws/aws-cdk/issues/21825

        # Create the Lambda function to receive the request
        api_hanlder = lambda_.Function(
            self,
            "ApiHandler",
            function_name="apigw_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("lambda/apigw-handler"),
            handler="lambda.lambda_handler",
            memory_size=2048,
            timeout=Duration.minutes(15),
            insights_version=lambda_.LambdaInsightsVersion.VERSION_1_0_135_0,
        )

        PSQL_layer = lambda_.LayerVersion(
            self,
            "PSQLLayer",
            code=lambda_.Code.from_asset("lambda/writeback-handler/psycopg2"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
        )

        writeback_handler = lambda_.Function(
            self,
            "zipcodesWritebackLambda",
            function_name="zipcodesWritebackLambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("lambda/writeback-handler"),
            handler="lambda.lambda_handler",
            memory_size=2048,
            timeout=Duration.minutes(15),
            layers=[PSQL_layer],
            insights_version=lambda_.LambdaInsightsVersion.VERSION_1_0_135_0,
        )

        writeback_handler.add_event_source(
            eventsources.DynamoEventSource(
                demo_table,
                starting_position=lambda_.StartingPosition.LATEST,
                batch_size=100,
                parallelization_factor=10,
            )
        )

        # grant permission to lambda to write to demo table
        demo_table.grant_read_write_data(api_hanlder)

        api_hanlder.add_environment("TABLE_NAME", demo_table.table_name)

        # Create API Gateway
        api = apigw_.LambdaRestApi(
            self, "MicroServiceZipcodeEndpoint", handler=api_hanlder, proxy=False
        )

        items = api.root.add_resource("zipcode")
        item = items.add_resource("{zipcode}")
        item.add_method("GET")
        item.add_method("PUT")


env_USA = aws_cdk.Environment(account="899456967600", region="us-east-1")

app = App()
CdkWebAppMicroServiceStack(app, "zipcode-microservice", env=env_USA)

app.synth()
