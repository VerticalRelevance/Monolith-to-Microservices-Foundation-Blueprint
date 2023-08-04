import os
import boto3
import json

print("Loading function")
dynamo = boto3.client("dynamodb")

TABLE_NAME = os.environ.get('TABLE_NAME', 'zipcodes')


def lambda_handler(event, context):
    http_verb = event["requestContext"]["httpMethod"]
    print("HTTP METHOD: " + str(http_verb))

    if http_verb == "GET":
        print("!!! EVENT PATH:" + event["path"])
        path = event["path"]

        zipcode = path.split("/")[2]
        print("!!! ZIPCODE:" + zipcode)

        response = dynamo.get_item(
            TableName=TABLE_NAME, Key={"zip_code": {"S": str(zipcode)}}
        )
        print(response)

        print("Received event: " + json.dumps(event, indent=2))
        return {"statusCode": 200, "body": json.dumps(response)}
    elif http_verb == "PUT":
        print("UPSERTING DYNAMODB...")
        json_doc = json.loads(event["body"])
        print(json_doc)

        item = {
            "zip_code": {"S": json_doc["zip_code"]},
            "state": {"S": json_doc["state"]},
            "longitude": {"S": json_doc["longitude"]},
            "latitude": {"S": json_doc["latitude"]},
            "county": {"S": json_doc["county"]},
            "city": {"S": json_doc["city"]},
        }
        print(item)
        response = dynamo.put_item(TableName=TABLE_NAME, Item=item)

        return {"statusCode": 200, "body": json.dumps(item)}
