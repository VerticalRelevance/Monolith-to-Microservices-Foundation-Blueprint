import aws_cdk
import os

from stacks.monolith_database import EC2DatabaseInstanceStack
from stacks.webapp_microservice import WebAppMicroServiceStack
from stacks.writeback_function import WritebackFunctionStack

env = aws_cdk.Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION"),
)

app = aws_cdk.App()

monolith = EC2DatabaseInstanceStack(app, "zipcode-monolith-db", env=env)

microservice = WebAppMicroServiceStack(
    app,
    "zipcode-microservice",
    env=env,
)

writeback_function = WritebackFunctionStack(
    app,
    "zipcode-writeback-function",
    env=env,
    vpc=monolith.vpc,
    secrets_manager_vpc_endpoint=monolith.secrets_manager_vpc_endpoint,
    database=monolith.database,
    table=microservice.table,
)

app.synth()
