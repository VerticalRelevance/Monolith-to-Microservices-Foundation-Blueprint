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
    instance=monolith.instance,
    instance_security_group=monolith.security_group,
    table=microservice.table,
)

app.synth()
