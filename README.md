# Monolith-to-Microservices-Foundation-Blueprint
The Monolith-to-Microservices Foundation Blueprint is an AWS CDK application written in Python. The goal of the blueprint is to demonstrate setting up a legacy monolith on an EC2 instance and then migrate to a modern microservice using AWS API Gateway, Lambda, and DynamoDB. Included is an an implementation of the [strangler fig pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/modernization-aspnet-web-services/fig-pattern.html), which is a way to reduce risk when modernizing monolithic applications.

The `Makefile` includes commands for installing local dependencies, deploying the CDK application, and cleaning up. The application contains three stacks and the `--exclusively` flag is used to deploy the stacks individually within the same CDK application. This provides a phased approach to deploying the blueprint. This document will serve as a guide to set up and verify the monolith, microservice, and writeback function.

## Application
What this application aims to do is take any given USA zip code and provide it's county and state in JSON return format.  
The pattern to input your zipcode is in the URL as a PATH parameter.

Monolith example:

GET `http://<alb-url>.<region>.elb.amazonaws.com/zipcode/20001`

Microservice example:

GET `https://<YOUR_API_GATEWAY>.execute-api.<AWS-REGION>.amazonaws.com/prod/zipcode/20001`

The response should look like this:

```json
{  
    "city": "Washington",  
    "county": "District Of Columbia",  
    "latitude": "38.911936",  
    "longitude": "-77.016719",  
    "state": "DC",  
    "zip_code": "20001"  
}  
```


# Prerequisites
## Local
* Linux/MacOS
* [Homebrew](https://brew.sh) installed
* make
* python3


The following dependencies will be installed via Homebrew:

* nvm - used to install and run the node version specified in `.nvmrc` and then installs the CDK cli globally via npm
    * Note that if this is your first time installing nvm, please update your [bash or zsh profile](https://formulae.brew.sh/formula/nvm#default):
    ```bash
    export NVM_DIR="$HOME/.nvm"
    [ -s "$HOMEBREW_PREFIX/opt/nvm/nvm.sh" ] && \. "$HOMEBREW_PREFIX/opt/nvm/nvm.sh" # This loads nvm
    [ -s "$HOMEBREW_PREFIX/opt/nvm/etc/bash_completion.d/nvm" ] && \. "$HOMEBREW_PREFIX/opt/nvm/etc/bash_completion.d/nvm" # This loads nvm bash_completion
    ```
* awscli - needed for port-forwarding over SSM
* session-manager-plugin - needed for port-forwarding over SSM
* docker - used by the CDK to build the python lambda writeback function
* jq - used for parsing the CDK output json

## AWS Account
An AWS Account with administrator access is required


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
![Monolith Diagram](diagrams/monolith.png)

* `make deploy-monolith` - This will deploy the VPC, the RDS database, and AutoScaling group
* `make port-forward` - Port-forward to the database on localhost:5432 using SSM (leave this open)
    * `make hydrate-monolith` - Hydrate the monolith database with zipcode data (you can close `make port-forward` after this)

## Verify that the monolith is working
* `make verify-monolith` - This will curl the monolith application through the load balancer URL

It should return

```
Getting monolith root URL (should return Hello, World!)
curl http://<alb-url>.<region>.elb.amazonaws.com
<p>Hello, World!</p>

Getting monolith zipcode 20001 (should return a JSON document for Washington, DC)
curl http://<alb-url>.<region>.elb.amazonaws.com/zipcode/20001
{"city":"Washington","county":"District Of Columbia","latitude":"38.911936","longitude":"-77.016719","state":"DC","zip_code":"20001"}
```

To manually verify, the monolith API base URL can be retrieved with `jq`:

```bash
# Get the URL with JQ from the CDK output
export MONOLITH_API_URL=$(cat ./cdk/output.json | jq -r '."zipcode-monolith-db".ApiUrl')
# Curl the Monolith
curl ${MONOLITH_API_URL}/zipcode/20001
```

It should return:

```json
{"city":"Washington","county":"District Of Columbia","latitude":"38.911936","longitude":"-77.016719","state":"DC","zip_code":"20001"}
```

# Deploy the microservice
![Monolith with Microservice Diagram](diagrams/monolith_with_microservice.png)

* `make deploy-microservice` - This will deploy the API Gateway, Lambda Handler, DynamoDB Table
* `make hydrate-microservice` - Hydrate the DynamoDB table with zipcode data


## Verfiy that the microservice is working
* `make verify-microservice` - This will curl the microservice endpoint through API Gateway for zip code `20001`

```
Getting microservice zipcode 20001
curl https://<api-url>.execute-api.<region>.amazonaws.com/prod/zipcode/20001
{"Item": {"city": {"S": "Washington"}, "county": {"S": "District Of Columbia"}, "zip_code": {"S": "20001"}, "longitude": {"S": "-77.016719"}, "latitude": {"S": "38.911936"}, "state": {"S": "DC"}}, "ResponseMetadata": {"RequestId": "693J9OODRM4B2S4I5U65D0UNN3VV4KQNSO5AEMVJF66Q9ASUAAJG", "HTTPStatusCode": 200, "HTTPHeaders": {"server": "Server", "date": "Sun, 13 Aug 2023 15:36:08 GMT", "content-type": "application/x-amz-json-1.0", "content-length": "178", "connection": "keep-alive", "x-amzn-requestid": "693J9OODRM4B2S4I5U65D0UNN3VV4KQNSO5AEMVJF66Q9ASUAAJG", "x-amz-crc32": "1314546232"}, "RetryAttempts": 0}}
```

To manually verify, the microservice API base url can be retrieved with `jq`.

```bash
# Get the URL with JQ from the CDK output
export MICROSERVICE_API_URL=$(cat ./cdk/output.json | jq -r '."zipcode-microservice".ApiUrl')
# Curl the Monolith
curl ${MICROSERVICE_API_URL}zipcode/20001
```

It should return

```
"Item": {"city": {"S": "Washington"}, "county": {"S": "District Of Columbia"}, "zip_code": {"S": "20001"}, "longitude": {"S": "-77.016719"}, "latitude": {"S": "38.911936"}, "state": {"S": "DC"}}, "ResponseMetadata": {"RequestId": "QFBD0AL92FHUKBB1GMVMVMOF7RVV4KQNSO5AEMVJF66Q9ASUAAJG", "HTTPStatusCode": 200, "HTTPHeaders": {"server": "Server", "date": "Sun, 13 Aug 2023 15:55:15 GMT", "content-type": "application/x-amz-json-1.0", "content-length": "178", "connection": "keep-alive", "x-amzn-requestid": "QFBD0AL92FHUKBB1GMVMVMOF7RVV4KQNSO5AEMVJF66Q9ASUAAJG", "x-amz-crc32": "1314546232"}, "RetryAttempts": 0}}
```

# Deploy the Writeback Function
This implements the strangler fig pattern utilizing DynamoDB streams

![Monolith with Microservice and Writeback Diagram](diagrams/monolith_with_microservice_and_writeback.png)

* `make deploy-all` - This will deploy the writeback Lambda function that will automatically update the monolith database when the DynmaoDB Table is updated.

## Verify that the Writeback Function is working
* `make verify-writeback` - This will curl the microservice with test data, wait 30 seconds, and then will curl the monolith to show that the postgres database has been updated.

To manually verify:

```bash
# Get the URLs with JQ from the CDK output
export MICROSERVICE_API_URL=$(cat ./cdk/output.json | jq -r '."zipcode-microservice".ApiUrl')
export MONOLITH_API_URL=$(cat ./cdk/output.json | jq -r '."zipcode-monolith-db".ApiUrl')

# Update the Microservice
curl -X PUT -d '{"city":"TEST City","county":"TEST County","latitude":"38.911936","longitude":"-77.016719","state":"TEST","zip_code":"20001"}' -H 'content-type: application/json' ${MICROSERVICE_API_URL}zipcode/20001

# Wait for the writeback handler to run
sleep 30

curl ${MONOLITH_API_URL}/zipcode/20001
```

should return

```json
{"zip_code": {"S": "20001"}, "state": {"S": "TEST"}, "longitude": {"S": "-77.016719"}, "latitude": {"S": "38.911936"}, "county": {"S": "TEST County"}, "city": {"S": "TEST City"}}
```

(wait for 30 seconds)

```json
{"city":"TEST City","county":"TEST County","latitude":"38.911936","longitude":"-77.016719","state":"TEST","zip_code":"20001"}
```

This shows that the writeback function is correctly configured and handling updates from DynamoDB to the monolith databse.


# Cleanup
`make destroy` - This will attempt to clean up any ENIs in the writeback security group, and destroy the CDK stacks.
