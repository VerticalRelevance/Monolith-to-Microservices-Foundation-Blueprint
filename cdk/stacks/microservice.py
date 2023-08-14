from constructs import Construct

import aws_cdk
from aws_cdk import (
    Stack,
    aws_dynamodb,
    aws_lambda,
    aws_apigateway,
    Duration,
)


class MicroserviceStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create DynamoDb Table
        self._table = aws_dynamodb.Table(
            self,
            id="zipcodes",
            partition_key=aws_dynamodb.Attribute(
                name="zip_code", type=aws_dynamodb.AttributeType.STRING
            ),
            removal_policy=aws_cdk.RemovalPolicy.DESTROY,
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
            stream=aws_dynamodb.StreamViewType.NEW_IMAGE,
        )

        aws_cdk.CfnOutput(self, "TableName", value=self._table.table_name)

        # TODO: Implement this CDK feature
        # https://github.com/aws/aws-cdk/issues/21825

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

        # Grant permission to lambda to write to table
        self._table.grant_read_write_data(api_hanlder)

        api_hanlder.add_environment("TABLE_NAME", self._table.table_name)

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
    def table(self):
        return self._table
