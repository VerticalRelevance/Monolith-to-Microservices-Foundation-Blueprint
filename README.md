# Monolith-to-Microservices-Foundation-Blueprint
What this application aims to do is take any given USA zip code and provide it's county and state in JSON return format.
The pattern to input your zipcode is in the URL bar.

Monolith example:
http://<YOURE_EC2_IP_ADDRESS>:5000/zipcode/20001

Microservice example:
https://f3n2cvjfyf.execute-api.us-east-1.amazonaws.com/zipcode/20001

As you can see, the zipcode is the last parameter on the URL bar.

The response looks like this:

`{
    "city": "Washington",
    "county": "District Of Columbia",
    "latitude": "38.911936",
    "longitude": "-77.016719",
    "state": "DC",
    "zip_code": "20001"
}
`


# Prerequisites (Monolith)
* Linux/MacOS
* CLI (terminal)
* AWS CLI
* AWS Account/Console/Credentials
# CDK Deploy
* Navigate terminal to clone the project repo located here:
* `git clone https://github.com/VerticalRelevance/Monolith-to-Microservices-Foundation-Blueprint`
* `cd Monolith-to-Microservices-Foundation-Blueprint/webapp-monolith/cdk`
* `cdk deploy`

# Validation of success (Monolith)
Login to your AWS Account. Navigate to EC2 and find public IP address.

http://<YOURE_EC2_IP_ADDRESS>:5000/zipcode/19067


App running as a monolith acting like on-prem which is on EC2
<Screenshot>

Zip code url works: go <link> here


## Zip Code Source
### https://github.com/millbj92/US-Zip-Codes-JSON (MIT)


## (Monolith) - Hydration
### EC2(Local)
### python3 -m flask --app webapp run
### Postgres Database
#### Installing Postgres
pip install psycopg2-binary
postgress.app
pgAdmin4
#### Executing Hydration
##### JSON -> CSV -> Postgres
python3 data/json2csv.py
python3 postgres/hydrate.py







## (Microservice) - Hydration
### EC2
### DynamoDB



