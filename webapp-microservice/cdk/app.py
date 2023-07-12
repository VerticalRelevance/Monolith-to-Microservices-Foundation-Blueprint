from constructs import Construct

import aws_cdk
from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigateway as apigw_,
    aws_ec2 as ec2,
    aws_iam as iam,
    App, Stack, Duration
)


TABLE_NAME = "zipcodes"

class CdkWebAppMicroServiceStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create DynamoDb Table
        demo_table = dynamodb.Table(
            self,
            id = TABLE_NAME,
            table_name = TABLE_NAME,
            partition_key=dynamodb.Attribute(
                name="zip_code", type=dynamodb.AttributeType.STRING
            ),
            removal_policy=aws_cdk.RemovalPolicy.RETAIN
        )


        # Create the Lambda function to receive the request
        api_hanlder = lambda_.Function(
            self,
            "ApiHandler",
            function_name="apigw_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("lambda/apigw-handler"),
            handler="lambda.lambda_handler",
            memory_size=1024,
            timeout=Duration.minutes(5),
        )

        # grant permission to lambda to write to demo table
        # demo_table.grant_write_data(api_hanlder)
        demo_table.grant_read_data(api_hanlder)

        api_hanlder.add_environment("TABLE_NAME", demo_table.table_name)

        # Create API Gateway
        api = apigw_.LambdaRestApi(
            self,
            "MicroServiceZipcodeEndpoint",
            handler=api_hanlder,
            proxy=False
        )

        items = api.root.add_resource("zipcode")
        item = items.add_resource("{zipcode}")
        item.add_method("GET")

env_USA = aws_cdk.Environment(account="899456967600", region="us-east-1")

app = App()
CdkWebAppMicroServiceStack(app, "zipcode-microservice", env=env_USA)

app.synth()