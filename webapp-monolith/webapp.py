import copy
import json
import psycopg2
from flask import Flask
from flask import jsonify
app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/zipcode/<zip_code>")
def hello_world_zipcode(zip_code):
    # zip_code =
    print("Looking up infor for Zip Code: " + zip_code)

    # return_string = {
    #     "zip_code": 501,
    #     "latitude": 40.922326,
    #     "longitude": -72.637078,
    #     "city": "Holtsville",
    #     "state": "NY",
    #     "county": "Suffolk"
    # }
    # return jsonify(return_string)
    zip_code_result = get_zip_code(zip_code)
    return jsonify(zip_code_result)

def get_zip_code(zip_code):
    """ query data from the zipcode table """
    conn = None
    try:
        conn = psycopg2.connect("host=localhost dbname=zipcodes user=postgres")
        cur = conn.cursor()
        cur.execute("SELECT * FROM public.zipcodes where zipcodes.zip_code = '" + zip_code + "' ORDER BY zip_code ASC LIMIT 100")
        print("The number of zipcodes: ", cur.rowcount)
        row = cur.fetchone()

        json_doc = {
            "zip_code": row[0],
            "latitude": row[1],
            "longitude": row[2],
            "city": row[3],
            "state": row[4],
            "county": row[5]
        }
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
        print(json_doc)
        return json_doc