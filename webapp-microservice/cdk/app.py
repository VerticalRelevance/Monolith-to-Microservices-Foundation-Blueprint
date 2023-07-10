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
            TABLE_NAME,
            partition_key=dynamodb.Attribute(
                name="zip_code", type=dynamodb.AttributeType.STRING
            ),
        )

        # VPC
        vpc = ec2.Vpc(
            self,
            "Ingress",
            cidr="10.1.0.0/16",
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Private-Subnet", subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ],
        )

        # Create the Lambda function to receive the request
        api_hanlder = lambda_.Function(
            self,
            "ApiHandler",
            function_name="apigw_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("lambda/apigw-handler"),
            handler="index.handler",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            memory_size=1024,
            timeout=Duration.minutes(5),
        )

        # grant permission to lambda to write to demo table
        demo_table.grant_write_data(api_hanlder)
        api_hanlder.add_environment("TABLE_NAME", demo_table.table_name)

        # Create API Gateway
        apigw_.LambdaRestApi(
            self,
            "Endpoint",
            handler=api_hanlder,
        )

env_USA = aws_cdk.Environment(account="899456967600", region="us-east-1")

app = App()
CdkWebAppMicroServiceStack(app, "zipcode-microservice", env=env_USA)

app.synth()