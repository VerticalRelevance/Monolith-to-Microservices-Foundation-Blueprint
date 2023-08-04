import aws_cdk
from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    Stack,
)
from constructs import Construct


class EC2DatabaseInstanceStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # VPC
        self._vpc = ec2.Vpc(
            self,
            "VPC",
            max_azs=1,
        )

        self._security_group = ec2.SecurityGroup(
            self, "InstanceSecurityGroup", vpc=self._vpc, allow_all_outbound=True)

        # AMI
        ubuntu_server_20_04_linux = ec2.LookupMachineImage(
            name="ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20221212",
            windows=False,
        )

        # Instance
        self._instance = ec2.Instance(
            self,
            "Instance",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.LARGE),
            machine_image=ubuntu_server_20_04_linux,
            vpc=self._vpc,
            security_group=self._security_group,
        )

        self._instance.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSSMManagedInstanceCore"),
        )

        # User data for Ubunutu Server 20.04
        self._instance.add_user_data("sudo apt update")
        self._instance.add_user_data(
            "sudo apt install -y python3-pip unzip awscli")
        self._instance.add_user_data(
            "sudo apt install -y postgresql postgresql-contrib")
        self._instance.add_user_data("pip3 install flask")
        self._instance.add_user_data("pip3 install psycopg2-binary")
        # instance.add_user_data('sudo -u postgres psql')
        self._instance.add_user_data(
            "sudo -u postgres psql -c \"ALTER USER postgres PASSWORD 'postgres';\""
        )
        self._instance.add_user_data(
            'sudo -u postgres psql -c "CREATE TABLE IF NOT EXISTS public.zipcodes (zip_code text NOT NULL, latitude text, longitude text, city text, state text, county text, CONSTRAINT zipcodes_pkey PRIMARY KEY (zip_code));"'
        )
        # sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"

        # To Enable external connections such as PGAdmin for a GUI
        # sudo vi /etc/postgresql/12/main/pg_hba.conf
        # immediately below this line:
        # host    all             all             127.0.0.1/32            md5
        # added this line:
        # host    all             all             0.0.0.0/0               md5
        self._instance.add_user_data(
            'sudo echo "host    all             all             0.0.0.0/0               md5" >> /etc/postgresql/12/main/pg_hba.conf'
        )

        # sudo vi /etc/postgresql/12/main/postgresql.conf
        self._instance.add_user_data(
            "sudo echo \"listen_addresses = '*'\" >> /etc/postgresql/12/main/postgresql.conf"
        )
        # listen_addresses = '*'                  # what IP address(es) to
        # listen on;.

        # Restart Postgres
        # sudo systemctl restart postgresql.service
        self._instance.add_user_data(
            "sudo systemctl restart postgresql.service")

        aws_cdk.CfnOutput(self, 'InstanceID', value=self._instance.instance_id)
        aws_cdk.CfnOutput(self, 'InstanceSecurityGroupID',
                          value=self._security_group.security_group_id)

    @property
    def instance(self):
        return self._instance

    @property
    def vpc(self):
        return self._vpc

    @property
    def security_group(self):
        return self._security_group
