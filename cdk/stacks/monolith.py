import os.path

import aws_cdk
from aws_cdk import (
    aws_autoscaling,
    aws_ec2,
    aws_iam,
    aws_elasticloadbalancingv2,
    aws_s3_assets,
    aws_rds,
    Stack,
)

from constructs import Construct

dirname = os.path.dirname(__file__)
db_name = "zipcodes"


class MonolithStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # VPC
        self._vpc = aws_ec2.Vpc(
            self,
            "VPC",
            max_azs=2,
        )

        # Secrets Manager VPC endpoint
        self._secrets_manager_vpc_endpoint = aws_ec2.InterfaceVpcEndpoint(
            self,
            "SecretsManagerVPCEndpoint",
            service=aws_ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
            vpc=self._vpc,
            private_dns_enabled=True,
        )

        # RDS Postgresql Database
        self._database = aws_rds.DatabaseInstance(
            self,
            "Database",
            engine=aws_rds.DatabaseInstanceEngine.POSTGRES,
            vpc=self._vpc,
            credentials=aws_rds.Credentials.from_generated_secret('postgres'),
            database_name=db_name,
            port=5432,
        )

        # Create a CfnOutput for the database endpoint
        aws_cdk.CfnOutput(
            self,
            "DatabaseEndpoint",
            value=self._database.db_instance_endpoint_address)
        aws_cdk.CfnOutput(
            self,
            "DatabasePort",
            value=self._database.db_instance_endpoint_port)
        aws_cdk.CfnOutput(self, "DatabaseName", value=db_name)
        aws_cdk.CfnOutput(
            self,
            "DatabaseSecretArn",
            value=self._database.secret.secret_arn)

        # Create a security group for the instance
        self._security_group = aws_ec2.SecurityGroup(
            self, "InstanceSecurityGroup", vpc=self._vpc, allow_all_outbound=True)

        # Allow the instance to access the database
        self._database.connections.allow_default_port_from(
            self._security_group)

        # Allow the instance to access the Secrets Manager VPC endpoint
        self._secrets_manager_vpc_endpoint.connections.allow_default_port_from(
            self._security_group)

        # AMI
        ubuntu_server_20_04_linux = aws_ec2.LookupMachineImage(
            name="ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20221212",
            windows=False,
        )

        # Archived and uploaded to Amazon S3 as a .zip file
        directory_asset = aws_s3_assets.Asset(self, "InstanceDirectoryAsset",
                                              path=os.path.join(
                                                  dirname, "../ec2_instance"),
                                              exclude=[".venv"],
                                              )

        # Create an AutoScaling Group
        asg = aws_autoscaling.AutoScalingGroup(
            self,
            "MonolithApplication",
            instance_type=aws_ec2.InstanceType.of(
                aws_ec2.InstanceClass.BURSTABLE3, aws_ec2.InstanceSize.MEDIUM),
            machine_image=ubuntu_server_20_04_linux,
            vpc=self._vpc,
            security_group=self._security_group,
            min_capacity=0,
            max_capacity=1,
            desired_capacity=1,
        )

        # Allow the ASG to access the S3 bucket
        directory_asset.grant_read(asg.role)

        # Allow the ASG to access the RDS database secret
        self._database.secret.grant_read(asg.role)

        # Allow SSM access to the instances
        asg.role.add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSSMManagedInstanceCore"),
        )

        # Add environemnt variables to the instance
        asg.add_user_data(
            f"export AWS_DEFAULT_REGION={self.region}")
        asg.add_user_data(
            f"export DATABASE_HOST={self._database.db_instance_endpoint_address}")
        asg.add_user_data(
            f"export DATABASE_PORT={self._database.db_instance_endpoint_port}")
        asg.add_user_data(
            f"export DATABASE_NAME={db_name}")
        asg.add_user_data(
            f"export DB_SECRET_ARN={self._database.secret.secret_arn}")

        # User data for Ubunutu Server 20.04
        asg.add_user_data("sudo apt update")
        asg.add_user_data("sudo apt install -y unzip awscli")

        # Download the zip file from Amazon S3
        asg.add_user_data(
            f"aws s3 cp {directory_asset.s3_object_url} /tmp/install.zip")

        # # Unzip the file
        asg.add_user_data("sudo unzip /tmp/install.zip -d /tmp/install")
        # # Run the install script
        asg.add_user_data("sudo chmod +x /tmp/install/install.sh")
        asg.add_user_data("cd /tmp/install && sudo -E ./install.sh")

        # Create an Application Load Balancer
        self._alb = aws_elasticloadbalancingv2.ApplicationLoadBalancer(
            self,
            "ALB",
            vpc=self._vpc,
            internet_facing=True,
        )

        # Output the ALB DNS name
        aws_cdk.CfnOutput(self, 'ApiUrl', value="http://" +
                          self._alb.load_balancer_dns_name)

        # Add a listener to the ALB
        listener = self._alb.add_listener(
            "Listener",
            port=80,
            open=True,
        )

        # Add a target group to the listener and use the instance as the target
        listener.add_targets(
            "Targets",
            port=5000,
            protocol=aws_elasticloadbalancingv2.ApplicationProtocol.HTTP,
            targets=[
                asg,
            ],
        )

        # Allow the ALB to connect to the instances through the security groups
        self._security_group.connections.allow_from(
            self._alb, aws_ec2.Port.tcp(5000), "ALB to Instances"
        )

    @property
    def vpc(self):
        return self._vpc

    @property
    def secrets_manager_vpc_endpoint(self):
        return self._secrets_manager_vpc_endpoint

    @property
    def security_group(self):
        return self._security_group

    @property
    def database(self):
        return self._database
