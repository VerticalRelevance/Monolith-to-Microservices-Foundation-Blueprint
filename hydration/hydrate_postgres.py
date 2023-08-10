import os
import boto3
import json
import psycopg2

with open("../cdk/output.json", "r") as f:
    output = json.load(f)

def get_conn_parameters():

    client = boto3.client("secretsmanager")
    secret = client.get_secret_value(SecretId=output["zipcode-monolith-db"]["DatabaseSecretArn"])
    secret_json = json.loads(secret["SecretString"])

    return {
        "user": secret_json["username"],
        "password": secret_json["password"],
        "host": os.environ.get("DATABASE_HOST", "localhost"),
        "port": os.environ.get("DATABASE_PORT", "5432"),
    }

conn_params = get_conn_parameters()

conn = psycopg2.connect(**conn_params)
cur = conn.cursor()

# cur.execute("""
# set AUTOCOMMIT on""")

cur.execute(
    """

-- DROP TABLE IF EXISTS public.zipcodes;

CREATE TABLE IF NOT EXISTS zipcodes
(
    zip_code text COLLATE pg_catalog."default" NOT NULL,
    latitude text COLLATE pg_catalog."default",
    longitude text COLLATE pg_catalog."default",
    city text COLLATE pg_catalog."default",
    state text COLLATE pg_catalog."default",
    county text COLLATE pg_catalog."default",
    CONSTRAINT zipcodes_pkey PRIMARY KEY (zip_code)
)

TABLESPACE pg_default;

"""
)


with open("../data/USCities.csv", "r") as f:
    next(f)  # Skip the header row.
    cur.copy_from(f, "zipcodes", sep=",")
conn.commit()
