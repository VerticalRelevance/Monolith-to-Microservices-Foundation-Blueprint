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


# CDK Deploy
* Navigate terminal to clone the project repo located here:
* `git clone https://github.com/VerticalRelevance/Monolith-to-Microservices-Foundation-Blueprint`
* `cd Monolith-to-Microservices-Foundation-Blueprint/webapp-monolith-database/cdk`
* `cdk deploy`
* `cd Monolith-to-Microservices-Foundation-Blueprint/webapp-microservice/cdk`
* `cdk deploy`
* `cd Monolith-to-Microservices-Foundation-Blueprint/hydration`
* Turn off database streaming in preparation for hydration
* AWS Console Screenshot here of turning off database
* `sudo vim Monolith-to-Microservices-Foundation-Blueprint/hydration/hydrate_postgres_remote.py`
* Edit line 2 and put the IP address of our EC2 instance
* `python3 hydrate_postgres_remote.py`
* This should be very fast, however the PSQL Database needs some time to digest the file
  * You may verify the contents of the PSQL Database by using a free tool like PGAdmin4 https://www.postgresql.org/download/
  * `SELECT COUNT(*) from public.zipcodes`
  * This should be 42741
* Make sure you have environment variables loaded for your AWS account and execute: 'python3 hydrate_dynamodb.py`
* This should take about 5-10 minutes depending on your computer and internet
  * After the script ends, Verify that 42741 items have been loaded into DynamoDB
  * Screenshot of validating get live table count in the DynamoDB AWS Console 
* Turn DynamoDB Stream back on
* Start the monolith by command:
  * `cd Monolith-to-Microservices-Foundation-Blueprint/webapp-monolith-database`
  * `python3 -m flask --app webapp run`
  * The Monolith should now be running on your local machine


# Validation of success (Monolith)
We are going to validate the Monolith via GET requests.

Open a browser and navigate to:

http://127.0.0.1:5000/zipcode/20001

This should return JSON for the given zipcode.

# Validation of success (Microservice)
We are going to validate the Microservice via GET requests.

Open a browser and navigate to:

https://<YOUR_API_GATEWAY>.execute-api.us-east-1.amazonaws.com/zipcode/20001

This should return JSON for the given zipcode.
