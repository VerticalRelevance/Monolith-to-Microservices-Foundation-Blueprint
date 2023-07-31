import aws_cdk
import os

from monolith_database import EC2DatabaseInstanceStack
from webapp_microservice import WebAppMicroServiceStack

env = aws_cdk.Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION"),
)

app = aws_cdk.App()

monolith = EC2DatabaseInstanceStack(app, "zipcode-monolith-db", env=env)

microservice_enabled = bool(app.node.try_get_context("microservice_enabled"))

if microservice_enabled:
    microservice = WebAppMicroServiceStack(
        app,
        "zipcode-microservice",
        env=env,
        vpc=monolith.vpc,
        instance=monolith.instance,
        instance_security_group=monolith.security_group
    )

app.synth()
