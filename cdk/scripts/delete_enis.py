import boto3
import json


try:
    with open('../output.json', 'r') as f:
        output = json.load(f)
        security_group_id = output["zipcode-microservice"]["WritebackSecurityGroupId"]
except Exception as e:
    print(e)
    print("Error reading security group id. Has the microservice been deployed? Check ../output.json")
    exit(0)

ec2 = boto3.client('ec2')

interfaces = ec2.network_interfaces.filter(Filters=[{'Name': 'group-id', 'Values': [security_group_id]}])
for interface in interfaces:
    try:
        print("Deleting interface " + interface["NetworkInterfaceId"])
        interface.delete()
    except Exception as e:
        print(e)
        print("Error deleting interface " + interface["NetworkInterfaceId"])
