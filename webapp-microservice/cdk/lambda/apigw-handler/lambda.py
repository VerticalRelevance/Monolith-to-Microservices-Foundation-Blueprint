import boto3
import json

print('Loading function')
dynamo = boto3.client('dynamodb')

def lambda_handler(event, context):

    client = boto3.client('dynamodb')

    print("!!! EVENT PATH:" + event['path'])
    path = event['path']

    zipcode = path.split('/')[2]
    print("!!! ZIPCODE:" + zipcode)

    # response = client.get_item(TableName='zipcodes', Key={'zip_code':{'S':str(zipcode)}})
    # print(response)

    print("Received event: " + json.dumps(event, indent=2))
    return {
        'statusCode': 200,
        'body': "json.dumps(response)"
    }

# TODO PUT request.