import os
import boto3
import json
import psycopg2

from flask import Flask, request, jsonify

app = Flask(__name__)


# Retrieve the credentials from secrets manager
def get_conn_parameters():

    client = boto3.client("secretsmanager")
    secret = client.get_secret_value(SecretId=os.environ.get("DB_SECRET_ARN"))
    secret_json = json.loads(secret["SecretString"])

    return {
        "user": secret_json["username"],
        "password": secret_json["password"],
        "host": os.environ.get("DATABASE_HOST"),
        "port": os.environ.get("DATABASE_PORT"),
    }

conn_params = get_conn_parameters()


@app.route("/")
def index():
    return "<p>Hello, World!</p>"


@app.route("/zipcode/<zip_code>", methods=["GET", "PUT"])
def zipcode(zip_code):
    if request.method == "GET":
        print("Looking up info for Zip Code: " + zip_code)
        zip_code_result = get_zip_code(zip_code)

        return jsonify(zip_code_result)

    elif request.method == "PUT":
        print(request.json["zip_code"])

        """ query data from the zipcode table """
        conn = None
        try:
            conn = psycopg2.connect(**conn_params)
            cur = conn.cursor()

            zip_code = request.json["zip_code"]
            latitude = request.json["latitude"]
            longitude = request.json["longitude"]
            city = request.json["city"]
            state = request.json["state"]
            county = request.json["county"]

            query = """INSERT INTO public.zipcodes (zip_code, latitude, longitude, city, state, county) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (zip_code) DO UPDATE SET (zip_code, latitude, longitude, city, state, county) = (EXCLUDED.zip_code, EXCLUDED.latitude, EXCLUDED.longitude, EXCLUDED.city, EXCLUDED.state, EXCLUDED.county) ;"""
            data = (zip_code, latitude, longitude, city, state, county)

            cur.execute(query, data)
            conn.commit()
            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
            print(query)
            return ("OK", 200)


def get_zip_code(zip_code):
    """query data from the zipcode table"""
    conn = None
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM public.zipcodes where zipcodes.zip_code = '"
            + zip_code
            + "' ORDER BY zip_code ASC LIMIT 100"
        )
        print("The number of zipcodes: ", cur.rowcount)
        row = cur.fetchone()

        json_doc = {
            "zip_code": row[0],
            "latitude": row[1],
            "longitude": row[2],
            "city": row[3],
            "state": row[4],
            "county": row[5],
        }
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
        print(json_doc)
        return json_doc