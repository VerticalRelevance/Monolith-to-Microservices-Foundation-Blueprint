# Monolith-to-Microservices-Foundation-Blueprint
What this application aims to do is take any given USA zip code and provide it's county and state in JSON return format.  
The pattern to input your zipcode is in the URL bar as a PATH parameter.

Monolith example:

GET http://127.0.0.1:5000/zipcode/20001

Microservice example:

GET https://<YOUR_API_GATEWAY>.execute-api.us-east-1.amazonaws.com/zipcode/20001

The response should look like this:

`{  
    "city": "Washington",  
    "county": "District Of Columbia",  
    "latitude": "38.911936",  
    "longitude": "-77.016719",  
    "state": "DC",  
    "zip_code": "20001"  
}  
`


# Prerequisites
* Linux/MacOS
* CLI (terminal)
* AWS CLI
* AWS Account/Console/Credentials
* Postman https://www.postman.com/downloads/
* python3
* pip3
* cdk
* git
* docker


# Clone the repository
* Navigate terminal to clone the project repo located here:
* `git clone https://github.com/VerticalRelevance/Monolith-to-Microservices-Foundation-Blueprint`
* `cd Monolith-to-Microservices-Foundation-Blueprint/`

# Configure your AWS Credentials
* `export AWS_PROFILE=<profile>`
* `aws configure set region <region>`

# Install dependencies, bootstrap the AWS environment, and ensure that the CDK stacks are able to synthesize
* `make`

# Deploy the monolith
* `make deploy-monolith` - This will deploy the VPC and monolith-db instance into a private subnet
* `make port-forward` - Port-forward to the database on localhost:5432
    * `make hydrate-monolith` - Hydrate the monolith database with zipcode data


## Verify that the monolith is working
* `make webapp` - leave this running while `make port-forward` is also running

```bash
curl http://127.0.0.1:5000/zipcode/20001
```

should return

```json
{"city":"Washington","county":"District Of Columbia","latitude":"38.911936","longitude":"-77.016719","state":"DC","zip_code":"20001"}
```

# Deploy the microservice
* `make deploy-microservice` - This will deploy the API Gateway, Lambda Handler, DynamoDB Table
* `make hydrate-microservice` - Hydrate the DynamoDB table with zipcode data


## Verfiy that the microservice is working
* `make webapp`


```bash
curl http://127.0.0.1:5000/zipcode/microservice/20001
```

should return

```json
{"city":"Washington","county":"District Of Columbia","latitude":"38.911936","longitude":"-77.016719","state":"DC","zip_code":"20001"}
```

# Deploy the Writeback Function
* `make deploy-all` - This will deploy the writeback Lambda function that will automatically update the monolith database when the DynmaoDB Table is updated.


## 


## Put
We are going to validate the Monolith via PUT requests.

Open Postman and create the following PUT request:
PUT http://127.0.0.1:5000/zipcode/microservice/20001

`{  
"city": "TEST City",  
"county": "TEST County",  
"latitude": "38.911936",  
"longitude": "-77.016719",  
"state": "TEST",  
"zip_code": "20001"  
}  
`

```bash
curl -X PUT -d '{"city":"TEST City","county":"TEST County","latitude":"38.911936","longitude":"-77.016719","state":"TEST","zip_code":"20001"}' -H 'content-type: application/json' http://127.0.0.1:5000/zipcode/microservice/20001
```

Wait about 1 minute to let the DynamoDB stream back to PostgresDB and then execute:

GET http://127.0.0.1:5000/zipcode/20001

You should now observe that on premise has been updated.

# Validation of success (Microservice)
## GET

We are going to validate the Microservice via GET requests.

Open a browser and navigate to:

https://<YOUR_API_GATEWAY>.execute-api.us-east-1.amazonaws.com/zipcode/20001

This should return JSON for the given zipcode.

## PUT
We are going to validate the Microservice via PUT requests.

Open Postman and create the following PUT request:
PUT https://<YOUR_API_GATEWAY>.execute-api.us-east-1.amazonaws.com/zipcode/20001

`{  
"city": "TEST City2",  
"county": "TEST County2",  
"latitude": "38.911936",  
"longitude": "-77.016719",  
"state": "TEST2",  
"zip_code": "20001"  
}  
`

Wait about 1 minute to let the DynamoDB stream back to PostgresDB and then execute:

GET http://127.0.0.1:5000/zipcode/20001

You should now observe that on premise has been updated via streaming.
