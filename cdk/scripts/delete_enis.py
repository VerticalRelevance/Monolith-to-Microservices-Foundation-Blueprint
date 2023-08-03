import boto3
import json


try:
    with open('../output.json', 'r') as f:
        output = json.load(f)
        security_group_id = output["zipcode-writeback-function"]["WritebackSecurityGroupId"]
except Exception as e:
    print(e)
    print("Error reading security group id. Has the microservice been deployed? Check ../output.json")
    exit(0)

ec2 = boto3.resource('ec2')

# Get all network interfaces with the security group id
filters = [{'Name': 'group-id', 'Values': [security_group_id]}]
interfaces = ec2.network_interfaces.filter(Filters=filters)

# Iterate through the interfaces and delete them
for interface in interfaces:
    try:
        print("Deleting interface " + interface.id)
        interface.delete()
    except Exception as e:
        print(e)
        print("Error deleting interface " + interface.id)
