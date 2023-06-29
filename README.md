# Monolith-to-Microservices-Foundation-Blueprint

## Zip Code Source
### https://github.com/millbj92/US-Zip-Codes-JSON (MIT)


## (Monolith) - Hydration
### EC2(Local)
### python3 -m flask --app app run
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