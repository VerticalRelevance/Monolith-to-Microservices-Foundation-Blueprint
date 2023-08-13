import os
import requests
import json
import psycopg2

secrets_extension_http_port = os.environ.get(
    'PARAMETERS_SECRETS_EXTENSION_HTTP_PORT', '2773')

secret_arn = requests.utils.quote(os.environ.get('DATABASE_SECRET_ARN'))

def get_connection_params():
    secrets_extension_endpoint = f"http://localhost:{secrets_extension_http_port}/secretsmanager/get?secretId={secret_arn}"

    headers = {
        "X-Aws-Parameters-Secrets-Token": os.environ.get('AWS_SESSION_TOKEN')
    }

    r = requests.get(secrets_extension_endpoint, headers=headers)

    secret = json.loads(r.json()["SecretString"])

    return {
        "host": secret["host"],
        "user": secret["username"],
        "password": secret["password"],
        "port": secret["port"],
    }


def handler(event, context):
    conn_params = get_connection_params()

    for record in event["Records"]:
        conn = None
        try:
            conn = psycopg2.connect(**conn_params)
            cur = conn.cursor()

            zip_code = record["dynamodb"]["Keys"]["zip_code"]["S"]
            latitude = record["dynamodb"]["NewImage"]["latitude"]["S"]
            longitude = record["dynamodb"]["NewImage"]["longitude"]["S"]
            city = record["dynamodb"]["NewImage"]["city"]["S"]
            state = record["dynamodb"]["NewImage"]["state"]["S"]
            county = record["dynamodb"]["NewImage"]["county"]["S"]
            print("ZIPCODE:" + zip_code)
            print("CITY:" + city)

            query = """INSERT INTO public.zipcodes (zip_code, latitude, longitude, city, state, county) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (zip_code) DO UPDATE SET (zip_code, latitude, longitude, city, state, county) = (EXCLUDED.zip_code, EXCLUDED.latitude, EXCLUDED.longitude, EXCLUDED.city, EXCLUDED.state, EXCLUDED.county) ;"""
            data = (zip_code, latitude, longitude, city, state, county)

            cur.execute(query, data)
            conn.commit()
            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            print("ERROR: ")
            print(error)
        finally:
            if conn is not None:
                conn.close()
            print(query)
            return ("OK", 200)
    return "Successfully processed {} records.".format(len(event["Records"]))
