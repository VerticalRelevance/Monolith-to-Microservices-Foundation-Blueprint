import json
import psycopg2
import requests
from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

with open("cdk/output.json") as f:
    outputs = json.load(f)

# Note the following URL/API Gateway needs to be public read
LAMBDA_EXECUTE_URL = outputs["zipcode-microservice"]["ApiUrl"] if outputs.get("zipcode-microservice") else None
conn_parameters = "host=localhost user=postgres password=postgres"


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/zipcode/microservice/<zip_code>", methods=["GET", "PUT"])
def microservice_zipcode(zip_code):
    if not LAMBDA_EXECUTE_URL:
        return jsonify({"message": "API URL not found. Has the microservice been deployed?"})

    url = f'{LAMBDA_EXECUTE_URL}zipcode/{zip_code}'

    if request.method == "GET":
        print("Looking up info for Zip Code: " + zip_code)
        r = requests.get(url)
        print(r.text)
        zip_code_result = r.text
        return zip_code_result
    elif request.method == "PUT":
        print("Forwarding the PUT to the writeback lambda: " + LAMBDA_EXECUTE_URL)
        r = requests.put(
            url=url, json=request.json
        )
        print(r.text)
        zip_code_result = r.text
        return zip_code_result


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
            conn = psycopg2.connect(conn_parameters)
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
        conn = psycopg2.connect(conn_parameters)
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
