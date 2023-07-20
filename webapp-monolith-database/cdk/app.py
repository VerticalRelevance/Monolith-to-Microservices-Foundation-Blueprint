import os.path

import aws_cdk
from aws_cdk.aws_s3_assets import Asset
from aws_cdk.aws_s3_deployment import *
from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    App, Stack
)

from constructs import Construct

dirname = os.path.dirname(__file__)


class EC2DatabaseInstanceStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # VPC
        vpc = ec2.Vpc(self, "VPC",
                      nat_gateways=0,
                      subnet_configuration=[ec2.SubnetConfiguration(name="public", subnet_type=ec2.SubnetType.PUBLIC)]
                      )

        # AMI
        ubuntu_server_20_04_linux = ec2.MachineImage.generic_linux(
            {'us-east-1': 'ami-0b93ce03dcbcb10f6'}
        )


        # Instance Role and SSM Managed Policy
        role = iam.Role(self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AWSXrayFullAccess"))

        # Instance
        instance = ec2.Instance(self, "ZipCodeMonolithDatabaseInstanceTarget",
                                instance_type=ec2.InstanceType("t3.xlarge"),
                                machine_image=ubuntu_server_20_04_linux,
                                vpc = vpc,
                                role = role,
                                detailed_monitoring = True
                                )

        #Flask Port
        instance.connections.allow_from_any_ipv4(ec2.Port.tcp(5000))

        #Postgres Port
        instance.connections.allow_from_any_ipv4(ec2.Port.tcp(5432))

        #User data for Ubunutu Server 20.04
        instance.add_user_data('sudo apt update')
        instance.add_user_data('sudo apt install -y python3-pip unzip awscli')
        instance.add_user_data('sudo apt install -y postgresql postgresql-contrib')
        instance.add_user_data('pip3 install flask')
        instance.add_user_data('pip3 install psycopg2-binary')
        # instance.add_user_data('sudo -u postgres psql')
        instance.add_user_data('sudo -u postgres psql -c "ALTER USER postgres PASSWORD \'postgres\';"')
        instance.add_user_data('sudo -u postgres psql -c "CREATE TABLE IF NOT EXISTS public.zipcodes (zip_code text NOT NULL, latitude text, longitude text, city text, state text, county text, CONSTRAINT zipcodes_pkey PRIMARY KEY (zip_code));"')
        # sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"

        # To Enable external connections such as PGAdmin for a GUI
        # sudo vi /etc/postgresql/12/main/pg_hba.conf
        #immediately below this line:
        #host    all             all             127.0.0.1/32            md5
        #added this line:
        #host    all             all             0.0.0.0/0               md5
        instance.add_user_data('sudo echo "host    all             all             0.0.0.0/0               md5" >> /etc/postgresql/12/main/pg_hba.conf')

        # sudo vi /etc/postgresql/12/main/postgresql.conf
        instance.add_user_data('sudo echo "listen_addresses = \'*\'" >> /etc/postgresql/12/main/postgresql.conf')
        # listen_addresses = '*'                  # what IP address(es) to listen on;.

        # Restart Postgres
        # sudo systemctl restart postgresql.service
        instance.add_user_data('sudo systemctl restart postgresql.service')

        # sudo cat /var/log/cloud-init-output.log

        # TODO Remove the following or implement it
        # instance.add_user_data('cd')
        # instance.add_user_data('git clone git@github.com:VerticalRelevance/ApplicationObservability-Blueprint.git');
        # instance.add_user_data('cd ~/ApplicationObservability-Blueprint/Django-Poll-App');
        # instance.add_user_data('python3 manage.py runserver 0.0.0.0:8000 --noreload &')


env_USA = aws_cdk.Environment(account="899456967600", region="us-east-1")

app = App()
EC2DatabaseInstanceStack(app, "zipcode-monolith-database", env=env_USA)

app.synth()