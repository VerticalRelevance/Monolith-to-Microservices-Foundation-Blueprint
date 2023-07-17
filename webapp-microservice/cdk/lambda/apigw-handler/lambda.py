import boto3
import json
from botocore.vendored import requests

print('Loading function')
dynamo = boto3.client('dynamodb')

def lambda_handler(event, context):
    http_verb =  event['requestContext']['httpMethod']
    print("HTTP METHOD: " + str(http_verb))

    if(http_verb == "GET"):
        client = boto3.client('dynamodb')

        print("!!! EVENT PATH:" + event['path'])
        path = event['path']

        zipcode = path.split('/')[2]
        print("!!! ZIPCODE:" + zipcode)

        response = client.get_item(TableName='zipcodes', Key={'zip_code':{'S':str(zipcode)}})
        print(response)

        print("Received event: " + json.dumps(event, indent=2))
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    elif(http_verb == "PUT"):
        print("UPSERTING DYNAMODB...")
        json_doc = json.loads(event['body'])
        print(json_doc)

        item = {
            'zip_code':{'S':json_doc['zip_code']},
            'state':{'S':json_doc['state']},
            'longitude':{'S':json_doc['longitude']},
            'latitude':{'S':json_doc['latitude']},
            'county':{'S':json_doc['county']},
            'city':{'S':json_doc['city']}
        }
        print(item)
        response = dynamo.put_item(
            TableName='zipcodes',
            Item=item
        )

        return {
            'statusCode': 200,
            'body': json.dumps(item)
        }

